import logging
import os
from typing import (
    Any,
    Callable,
    Optional,
    TypedDict,
)
from uuid import UUID

from langchain.cache import RedisCache
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import ConversationChain, LLMChain
from langchain.globals import set_llm_cache
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
)
from langchain.schema import AIMessage, HumanMessage, LLMResult, SystemMessage
from langchain_openai.chat_models import AzureChatOpenAI
from redis import ConnectionError, Redis, TimeoutError

LLM_CACHE_ENABLED = os.getenv("LLM_CACHE_ENABLED", "false").lower() == "true"
LLM_CACHE_CONNECTED = False
if LLM_CACHE_ENABLED:
    try:
        DEFAULT_REDIS_HOST = "localhost"
        DEFAULT_SOCKET_TIMEOUT_SECONDS = 10
        redis_host = os.getenv("REDIS_HOST", DEFAULT_REDIS_HOST)
        redis_port = int(os.getenv("REDIS_PORT_OVERRIDE", "6379"))
        logging.info(f"Trying to connect to Redis at {redis_host}:{redis_port}")
        redis_client = Redis(
            host=redis_host,
            port=redis_port,
            db=0,
            socket_timeout=DEFAULT_SOCKET_TIMEOUT_SECONDS,
        )
        redis_client.ping()
        DEFAULT_CACHE_TTL = 3600 * 24 * 30  # 30 days
        LLM_CACHE_TTL = int(os.getenv("LLM_CACHE_TTL", f"{DEFAULT_CACHE_TTL}"))
        logging.info("Connected to Redis. Setting up LLM cache...")
        set_llm_cache(RedisCache(redis_client, ttl=DEFAULT_CACHE_TTL))
        LLM_CACHE_CONNECTED = True
    except (ConnectionError, TimeoutError) as e:
        logging.error(f"Cannot connect to Redis: {e}. Skipping LLM cache setup...")


REQUEST_TIMEOUT = 120  # seconds


def dedent(s: str) -> str:
    """
    Custom dedent function for multi-line prompt texts
    """
    s = s.strip()
    return "\n".join(line.lstrip() for line in s.splitlines())


class ModelConfig(TypedDict):
    azure_deployment: str
    tiktoken_model_name: str
    temperature: float


def _resolve_tiktoken_model_name(model_name: str) -> str:
    if model_name.startswith("gpt-35"):
        return "gpt-35-turbo"
    if model_name.startswith("gpt-4o"):
        return "gpt-4o"
    if model_name.startswith("gpt-4"):
        return "gpt-4"
    if "-ada" in model_name:
        return "text-embedding-ada-002"
    return model_name


def create_model_config(
    deployment: str,
    temperature: float = 0.0,
):
    return ModelConfig(
        azure_deployment=deployment,
        tiktoken_model_name=_resolve_tiktoken_model_name(deployment),
        temperature=temperature,
    )


# token, buffer, output elem
OnLlmNewTokenLambda = Callable[[str, str, Any], None]
# result, buffer, output elem
OnLlmEndLambda = Callable[[LLMResult, str, Any], None]


class NoopElement:
    def write(self, text: str, *args, **kwargs) -> None:
        pass

    def text(self, text: str, *args, **kwargs) -> None:
        pass


# noinspection DuplicatedCode
class StreamingHtmlCallbackHandler(BaseCallbackHandler):
    def __init__(
        self,
        output_elem: Optional[NoopElement | Any],
        *,
        on_llm_new_token: Optional[OnLlmNewTokenLambda] = None,
        on_llm_end: Optional[OnLlmEndLambda] = None,
    ):
        self.target = output_elem if output_elem else NoopElement()
        self.buffer = ""
        self.on_llm_new_token_lambda = on_llm_new_token
        self.on_llm_end_lambda = on_llm_end

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        if self.on_llm_new_token_lambda:
            return self.on_llm_new_token_lambda(token, self.buffer, self.target)
        else:
            self.buffer += token
            self.target.text(self.buffer)

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        if self.on_llm_end_lambda:
            self.on_llm_end_lambda(response, self.buffer, self.target)


class ChainWrapper:
    def __init__(
        self,
        chain: LLMChain,
        *args,
        ignore_llm_cache: Optional[bool] = False,
        **kwargs,
    ):
        self.chain = chain
        self.ignore_llm_cache = ignore_llm_cache
        self.args = args
        self.kwargs = kwargs

    def __call__(
        self, prompt: str, wrapper_output_elem: NoopElement | Any | None = None
    ):
        # TODO: wait fix https://github.com/hwchase17/langchain/issues/2359
        # with get_openai_callback() as cb:
        #     res = self.chain.predict(input=prompt)
        #     logging.info(cb)
        #     return res

        # noinspection PyUnusedLocal,PyShadowingNames
        def cached_predict(
            prompt: str,
            wrapper_output_elem: NoopElement | Any | None = None,
            *args,
            **kwargs,
        ):
            callbacks = []
            if wrapper_output_elem:
                callbacks = [StreamingHtmlCallbackHandler(wrapper_output_elem)]
            return self.chain.predict(input=prompt, callbacks=callbacks)

        return cached_predict(
            prompt,
            wrapper_output_elem,
            *self.args,
            **self.kwargs,
        )


def llm_stateful_chat(
    model_config: ModelConfig,
    history: Optional[list[tuple[str, str]]] = None,
    *,
    output_elem: Optional[NoopElement | Any] = None,
    callbacks: Optional[list[BaseCallbackHandler]] = None,
    system: str = "",
    ignore_llm_cache: Optional[bool] = False,
) -> ChainWrapper:
    """
    Create a stateful chatbot that remembers the conversation history
    :param system: The system message to display at the start of the conversation
    :param history: A list of tuples of (human message, AI message)
    to seed the conversation
    :param output_elem: The output element to use. If not specified,
    then a noop output element will be used.
    :param model_config: The model configuration to use
    :param callbacks: A list of callbacks to use.
    For example to print out streaming output to the terminal,
    use [StreamingTerminalCallbackHandler()]
    :param ignore_llm_cache: Whether to ignore the LLM cache
    """
    llm = AzureChatOpenAI(
        **model_config,
        timeout=REQUEST_TIMEOUT,  # seconds
        max_retries=5,
        streaming=True,
        callbacks=[
            StreamingHtmlCallbackHandler(
                output_elem,
            )
        ]
        if not callbacks
        else callbacks,
        cache=not ignore_llm_cache,
    )
    default_template = f"""
The following is a friendly conversation between a human and an AI.
The AI is talkative and provides lots of specific details from its context.
If the AI does not know the answer to a question, it truthfully says it does not know.

{system}

Current conversation:
{{history}}
Human: {{input}}
AI:"""
    prompt = PromptTemplate(
        input_variables=["history", "input"], template=default_template
    )
    memory = ConversationBufferMemory()
    if history:
        for pair in history:
            # noinspection PyUnresolvedReferences
            memory.add_message(HumanMessage(content=pair[0]))
            # noinspection PyUnresolvedReferences
            memory.add_message(AIMessage(content=pair[1]))
    conversation = ConversationChain(
        llm=llm, prompt=prompt, memory=memory, verbose=True
    )
    return ChainWrapper(
        conversation,
        history,
        model_config,
        ignore_llm_cache=ignore_llm_cache,
    )


def llm_simple_reply(
    model_config: ModelConfig,
    prompt: str,
    *,
    system: Optional[str] = None,
    callbacks: Optional[list[BaseCallbackHandler]] = None,
    output_elem: Optional[NoopElement | Any] = None,
    ignore_llm_cache: Optional[bool] = False,
) -> str:
    """
    Simple chatbot that replies to a prompt

    :param prompt: The prompt to reply to
    :param system: The system message to display at the start of the conversation
    :param output_elem: The output element to use. If not specified,
    then a noop output element will be used.
    :param model_config: The model configuration to use
    :param callbacks: A list of callbacks to use.
    :param ignore_llm_cache: Whether to ignore the LLM cache
    """
    chat = AzureChatOpenAI(
        **model_config,
        timeout=REQUEST_TIMEOUT,  # seconds
        max_retries=5,
        streaming=True,
        callbacks=[
            StreamingHtmlCallbackHandler(
                output_elem,
            )
        ]
        if not callbacks
        else callbacks,
        cache=not ignore_llm_cache,
    )

    messages = []
    if system:
        messages.append(SystemMessage(content=system))
    messages.append(HumanMessage(content=prompt))

    message = chat.invoke(messages)
    return str(message.content)


def llm_few_shots_chain(
    model_config: ModelConfig,
    system: str,
    history: list[tuple[str, str]],
    stateful: bool = False,
    *,
    output_elem: Optional[NoopElement | Any] = None,
    callbacks: Optional[list[BaseCallbackHandler]] = None,
    ignore_llm_cache: Optional[bool] = False,
) -> ChainWrapper:
    """
    Create a chatbot that can be seeded with a few examples

    :param system: The system message to display at the start of the conversation
    :param history: A list of tuples of (human message, AI message) to seed
    the conversation
    :param output_elem: The output element to use. If not specified,
    then a noop output element will be used.
    :param model_config: The model configuration to use
    :param stateful: Whether to use a stateful conversation. If set to True,
    then the chatbot will remember the conversation history between invocations.
    :param callbacks: A list of callbacks to use.
    For example to print out streaming output to the terminal,
    use [StreamingTerminalCallbackHandler()]
    :param ignore_llm_cache: Whether to ignore the LLM cache
    """
    system_message = SystemMessage(content=system)
    convo = []
    for example_pair in history:
        convo.append(HumanMessage(content=example_pair[0]))
        convo.append(AIMessage(content=example_pair[1]))

    human_template = "{input}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat = AzureChatOpenAI(
        **model_config,
        timeout=REQUEST_TIMEOUT,  # seconds
        max_retries=5,
        streaming=True,
        callbacks=[
            StreamingHtmlCallbackHandler(
                output_elem,
            )
        ]
        if not callbacks
        else callbacks,
        cache=not ignore_llm_cache,
    )
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            system_message,
            *convo,
            human_message_prompt,
        ]
    )
    memory = None
    if stateful:
        memory = ConversationBufferMemory()
    chain = LLMChain(llm=chat, prompt=chat_prompt, memory=memory)
    return ChainWrapper(
        chain,
        history,
        model_config,
        ignore_llm_cache=ignore_llm_cache,
    )


def llm_map(
    model_config: ModelConfig,
    promptTemplate: Callable[[list[Any]], str],
    data: list[Any],
    chunk_size: int = 20000,
    *,
    system: str = "",
    callbacks: Optional[list[BaseCallbackHandler]] = None,
    output_elem: Optional[NoopElement | Any] = None,
    ignore_llm_cache: Optional[bool] = False,
) -> str:
    """
    This is a wrapper arount stuff chain with token limit

    :param prompt: The prompt to reply to, it takes two parameters - next chunk of the content and shared context
    :param system: The system message to display at the start of the conversation
    :param output_elem: The output element to use. If not specified,
    then a noop output element will be used.
    :param model_config: The model configuration to use
    :param callbacks: A list of callbacks to use.
    :param ignore_llm_cache: Whether to ignore the LLM cache
    """
    chat = AzureChatOpenAI(
        **model_config,
        timeout=REQUEST_TIMEOUT,  # seconds
        max_retries=5,
        streaming=True,
        callbacks=[
            StreamingHtmlCallbackHandler(
                output_elem,
            )
        ]
        if not callbacks
        else callbacks,
        cache=not ignore_llm_cache,
    )

    final_result = []
    current_chunk = []
    current_size = 0

    # Split data into chunks
    for item in data:
        item_size = calculate_token_size(promptTemplate(current_chunk + [item]))
        if current_size + item_size > chunk_size and current_chunk:
            final_result.append(
                process_chunk(current_chunk, promptTemplate, system, chat)
            )
            current_chunk = [item]
            current_size = item_size
        else:
            current_chunk.append(item)
            current_size += item_size

    # Process the remaining chunk if any
    if current_chunk:
        final_result.append(process_chunk(current_chunk, promptTemplate, system, chat))

    return final_result


def process_chunk(chunk, promptTemplate, system, chat):
    prompt = promptTemplate(chunk)
    logging.info(f"running chunk of size {len(chunk)}")
    data = chat([SystemMessage(content=system), HumanMessage(content=prompt)]).content
    logging.info(data)
    return data


def get_azure_chat(
        model_name: str,
        *,
        output_elem: Optional[NoopElement | Any] = None,
        callbacks: Optional[list[BaseCallbackHandler]] = None,
        ignore_llm_cache: Optional[bool] = False):
    return AzureChatOpenAI(
        azure_deployment=model_name,
        request_timeout=5,  # seconds
        max_retries=5,
        streaming=True,
        callbacks=[
            StreamingHtmlCallbackHandler(
                output_elem,
            )
        ]
        if not callbacks
        else callbacks,
        cache=not ignore_llm_cache
    )


def calculate_token_size(data: str) -> int:
    return len(data) / 4
