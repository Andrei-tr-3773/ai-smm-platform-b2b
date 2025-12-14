import json
import logging
from langchain_core.messages import HumanMessage
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph
from langchain_core.prompts import ChatPromptTemplate
from agents.agent_state import AgentState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranslationAgent:
    def __init__(self, model, translate_prompt="", criticize_prompt="", reflection_prompt=""):
        self.model = model
        self.translate_prompt = translate_prompt
        self.criticize_prompt = criticize_prompt
        self.reflection_prompt = reflection_prompt
        self.graph = self._initialize_graph()
        logger.info("TranslationAgent initialized.")

    def _initialize_graph(self):
        try:
            graph = StateGraph(AgentState)
            graph.add_node("translate_content", self.translate_content)
            graph.add_node("criticize_translation", self.criticize_translation)
            graph.add_node("reflect_on_translation", self.reflect_on_translation)
            graph.add_edge("translate_content", "criticize_translation")
            graph.add_edge("criticize_translation", "reflect_on_translation")
            graph.set_entry_point("translate_content")
            logger.info("StateGraph initialized and compiled.")
            return graph.compile()
        except Exception as e:
            logger.error(f"Error initializing StateGraph: {e}")
            raise

    def translate_content(self, state: AgentState):
        try:
            messages = state['messages']
            selected_languages = state['selected_languages']
            language_keys = ', '.join(selected_languages)
            translation_prompt = self.translate_prompt.format(language_keys=language_keys, json_content=messages[-1].content)
        
            translation_prompt_template = ChatPromptTemplate.from_template(
                f"{translation_prompt}"
                f"Format the result in the following JSON object with keys {language_keys}: {{json_content}}."
            )
            formatted_translation_prompt = translation_prompt_template.format(json_content=messages[-1].content)
        
            translation_message = HumanMessage(content=formatted_translation_prompt)
            translated_message = self.model.invoke([translation_message])
            translations = json.loads(translated_message.content.replace("```json", "").replace("```", ""))
            logger.info("Content translated successfully.")

            return {'translations': translations}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON during translation: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during content translation: {e}")
            raise

    def criticize_translation(self, state: AgentState):
        try:
            translations = state['translations']
            criticism_prompt = self.criticize_prompt
            for lang, translation in translations.items():
                criticism_prompt += f"<{lang}>\n{translation}\n</{lang}>\n"
            
            criticism_message = HumanMessage(content=criticism_prompt)
            criticism_response = self.model.invoke([criticism_message])
            logger.info("Translation criticized successfully.")

            return {'translations': translations, 'criticisms': criticism_response.content}
        except Exception as e:
            logger.error(f"Error during translation criticism: {e}")
            raise

    def reflect_on_translation(self, state: AgentState):
        try:
            translations = state['translations']
            criticisms = state['criticisms']
            selected_languages = state['selected_languages']
            language_keys = ', '.join(selected_languages)
            reflection_prompt = self.reflection_prompt
            
            for lang, translation in translations.items():
                reflection_prompt += f"<{lang}>\nTranslation: {translation}\nCriticism: {criticisms}\n</{lang}>\n"

            reflection_prompt += f"\nFormat the result in the following JSON object with keys: {language_keys}"
            
            reflection_message = HumanMessage(content=reflection_prompt)
            reflection_response = self.model.invoke([reflection_message])
            improved_translations = json.loads(reflection_response.content.replace("```json", "").replace("```", ""))
            logger.info("Reflection on translation completed successfully.")

            return {'messages': [reflection_response], 'translations': improved_translations}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON during reflection: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during reflection on translation: {e}")
            raise