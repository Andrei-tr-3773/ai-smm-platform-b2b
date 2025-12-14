import logging
from types import SimpleNamespace
from typing import TypedDict

import markdown as md
import streamlit as st

from common.config import pull_model_config
from common.llm import (
    LLM_CACHE_CONNECTED,
    ModelConfig,
    create_model_config,
)
from common.llm import (
    dedent as prompt_dedent,
)
from common.redis import get_hash_key, get_redis_client, redis_safe_ping

_logger = logging.getLogger(__name__)

## TODO: We should allow to specify the 'level' for the heading
def chapter(title: str):
    return st.markdown(f"""---
# {title}
---""")

class Point(TypedDict):
    title: str
    content: str
    icon: str


def render_point(point: Point) -> str:
    html = md.markdown(point["content"])
    return f"""
<div class="grid-item icon icon_{point['icon']}">
  <span class="title">{point['title']}</span><br/>
  <span class="content">{html}</span>
</div>
    """


def render_emphasis(point: Point) -> str:
    html = md.markdown(point["content"])
    return f"""
<div class="center-container">
  <div class="emphasized-square icon icon_{point['icon']}">
    <span class="title">{point['title']}</span><br/>
    <span class="content">{html}</span></span>
  </div>
</div>
    """

# TODO: Catalog URL should be a ENV variable
def get_breadcrumbs_html(name, catalog_url) -> str:
    return f"""
<div class="breadcrumbs">
    <a href="{catalog_url}">Catalog</a>
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M5.33301 13L10.6663 8L5.33301 3" stroke="#FBFAFA" stroke-width="0.666667" stroke-linecap="square"></path></svg>
    <span>{name}</span>
</div>
"""

def render_breadcrums(
    name: str = "Demo",
    catalog_url: str = "http://localhost:8501",
):
    html_string = get_breadcrumbs_html(name, catalog_url)
    st.markdown(html_string, unsafe_allow_html=True)
    return html_string


def render_preface(
    title: str,
    text: str,
    points=None,
    emphasis: Point = None,
    include_follow_up: bool = True,
    follow_up_title: str = "Demo",
    follow_up_text: str = "",
    short_title: str = "",
) -> str:
    if points is None:
        points = []
    points_html = "".join([render_point(point) for point in points])
    emphasis_html = ""
    follow_up_title_html = f'<span class="case-id">{follow_up_title}</span>'
    if emphasis:
        emphasis_html = render_emphasis(emphasis)
    # God knows why, but the following code does work ONLY
    # with this kind of indentation.
    # So don't touch it!
    html_string = f"""
<section class="preface">
  <h1>{title}</h1>
  <p>{text}</p>
  <div class="grid-container">
    {points_html}
  </div>
  {emphasis_html}
</section>
    """
    st.markdown(html_string, unsafe_allow_html=True)
    if include_follow_up:
        follow_up_text = follow_up_text if follow_up_text != "" else text
        follow_up_html = f"""
<h2>{follow_up_title_html}</h2>
<p>{follow_up_text}</p>
        """
        st.markdown(
            follow_up_html,
            unsafe_allow_html=True,
        )
    return html_string


class Page:
    def __init__(self):
        self.model_config = None
        self.ignore_llm_cache = None

    @staticmethod
    def set_state_defaults(
        state_namespace: str | None, state_defaults: list[tuple[str, any]]
    ):
        state = st.session_state
        if state_namespace is not None:
            if state_namespace not in state:
                state[state_namespace] = SimpleNamespace()
            state = state[state_namespace]

        for key, value in state_defaults:
            if not hasattr(state, key):
                setattr(state, key, value)

    def render(
        self,
        short_title: str = None,
        state_namespace: str | None = None,
        state_defaults=None,
        *args,
        **kwargs,
    ) -> tuple[ModelConfig, bool]:
        if state_defaults is None:
            state_defaults = []
        self.set_state_defaults(state_namespace, state_defaults)
        word_wrap()
        render_breadcrums(short_title)
        render_preface(*args, **kwargs)

        initial_config = pull_model_config()
        model_config, ignore_llm_cache = ConfigWidget(
            initial_config.default_model.value,
            [x.value for x in initial_config.available_models],
            initial_config.temperature,
            2000,
            initial_config.ignore_llm_cache,
        ).render()

        self.model_config = model_config
        self.ignore_llm_cache = ignore_llm_cache
        return model_config, ignore_llm_cache


class ConfigWidget:
    def __init__(
        self,
        default_model_name: str,
        default_model_options: list[str],
        default_temperature: float,
        default_max_tokens: int,
        ignore_llm_cache=False,
    ):
        self.default_model_name = default_model_name
        self.default_model_options = default_model_options
        self.default_temperature = default_temperature
        self.default_max_tokens = default_max_tokens
        self.ignore_llm_cache = ignore_llm_cache

    def render(self) -> tuple[ModelConfig, bool, bool]:
        elem_key_prefix = ("model_config",)
        expander_settings = st.expander("Model Config")
        with expander_settings:
            if st.button("Refresh Page"):
                st.experimental_rerun()
            ignore_llm_cache = st.checkbox(
                "Ignore Global LLM cache",
                value=self.ignore_llm_cache,
            )

            if LLM_CACHE_CONNECTED:
                st.info("Connected to the remote LLM cache.", icon="ℹ️")
            else:
                st.warning("Cannot connect to the remote LLM cache.", icon="⚠️")
            model_name = st.selectbox(
                label="Choose model",
                key=f"{elem_key_prefix}_select",
                options=self.default_model_options,
                index=self.default_model_options.index(self.default_model_name),
            )
            # why?
            if model_name in self.default_model_options:
                model_config: ModelConfig = create_model_config(
                    deployment=model_name,
                    temperature=expander_settings.slider(
                        label="Temperature - Modify the randomness of the LLM response.",
                        key=f"{elem_key_prefix}_tmp",
                        min_value=0.0,
                        max_value=1.0,
                        value=float(self.default_temperature),
                        step=0.1,
                    ),
                )
            else:
                raise ValueError(f"Unknown model name: {model_name}")
            return model_config, ignore_llm_cache


class PromptWidget:
    __no_select_label = "Default"

    def __init__(
        self,
        ns: str,
        default_text: str = "",
        default_select: str = "Default",
        key: str = "Prompt",
        title: str = None,
        collapsed: bool = True,
        height: int = 500,
        dedent: bool = True,
        help_text: str = None,
    ):
        self.state = st.session_state
        self.state_prefix = f"{ns}:{key}"
        if self.state_prefix not in self.state:
            self.state[self.state_prefix] = None
        self.ns = ns
        self.key = key
        self.default_text = prompt_dedent(default_text) if dedent else default_text
        self.default_select = default_select
        self.help_text = help_text
        if not title:
            self.title = self.key
        else:
            self.title = title
        self.collapsed = collapsed
        self.height = height
        self.elem_key = get_hash_key(f"{self.ns}", key)
        if LLM_CACHE_CONNECTED and redis_safe_ping(redis_client := get_redis_client()):
            self.redis_options = [
                s.decode("utf-8") for s in redis_client.keys(f"{ns}:{key}:*")
            ]
            self.redis_options = {
                key: redis_client.get(key).decode("utf-8") for key in self.redis_options
            }
        else:
            _logger.info(
                "Cannot connect to Redis therefore cannot pull list of prompts"
            )
            self.redis_options = {}
        self.options = {
            PromptWidget.__no_select_label: "",
            **{k.split(":")[2]: v for k, v in self.redis_options.items()},
        }
        self.selected = self.state[self.state_prefix]

    def _render_prompt(self, title: str, text: str) -> str:
        prompt_text = st.text_area(
            label=title,
            value=f"{text}",
            height=self.height,
            help=self.help_text,
            key=f"prompt:{self.elem_key}",
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            save_as = st.text_input(
                label="Save As",
                value=self.selected if self.selected else self.default_select,
                key=f"label:{self.elem_key}",
            )
        redis_key = get_hash_key(f"{self.ns}:{self.key}:{save_as}", save_as)
        with col2:
            st.write("")
            st.write("")
            if st.button("Save", key=f"button:{self.elem_key}"):
                if LLM_CACHE_CONNECTED and redis_safe_ping(
                    redis_client := get_redis_client()
                ):
                    redis_client.set(redis_key, prompt_text)
                    st.info(f"Saved at [`{redis_key}`]")
                    st.experimental_rerun()
                else:
                    st.warning("Cannot save prompt: no connection to Redis")
        with col3:
            st.write("")
            st.write("")
            if st.button("Delete", key=f"button_del:{self.elem_key}"):
                if LLM_CACHE_CONNECTED and redis_safe_ping(
                    redis_client := get_redis_client()
                ):
                    redis_client.delete(redis_key)
                    st.info(f"Deleted [`{redis_key}`]")
                    st.experimental_rerun()
                else:
                    st.warning("Cannot delete prompt: no connection to Redis")
        return prompt_text

    def render(self) -> str:
        with st.expander(self.title, False) if self.collapsed else st.container():
            if self.options and len(self.options) > 1:
                index = 0
                try:
                    if self.default_select:
                        index = list(self.options.keys()).index(self.default_select)
                except ValueError:
                    pass
                selected = st.selectbox(
                    "Predefined Prompts",
                    options=self.options,
                    index=index,
                    key=f"selectbox:{self.elem_key}",
                )
                if (
                    selected != self.selected
                    and selected != PromptWidget.__no_select_label
                ):
                    text = self.options[selected]
                    self.state[self.state_prefix] = selected
                    self.selected = selected
                elif selected == self.selected:
                    text = self.options[selected]
                elif selected == PromptWidget.__no_select_label:
                    text = self.default_text
                else:
                    text = self.default_text
            else:
                text = self.default_text
            return self._render_prompt("Text" if self.collapsed else self.title, text)


def word_wrap():
    st.markdown(
        """
<style>
pre code, .stTextLabelWrapper div {
white-space: pre-wrap !important;
word-wrap: break-word !important;
}
.stTextLabelWrapper {
background-color: rgb(22, 23, 27);
padding: 16px;
}
</style>
            """,
        unsafe_allow_html=True,
    )
