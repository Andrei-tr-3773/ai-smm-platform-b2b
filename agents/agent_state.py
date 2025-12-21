from typing import TypedDict, Annotated, Optional
from langchain_core.messages import AnyMessage
import operator

class ContentTemplate:
    def __init__(self, name: str, liquid_template: str, items: list[dict], example_query: str):
        self.name = name
        self.liquid_template = liquid_template
        self.items = items
        self.example_query = example_query


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    content_template: ContentTemplate
    translations: dict
    criticisms: str
    initial_english_content: str
    selected_languages: list[str]
    evaluation: dict
    selected_audience_name: str
    selected_audience_description: str

    # Week 4: Platform optimization fields
    selected_platform: Optional[str]  # instagram, facebook, telegram, linkedin
    optimized_content: Optional[str]  # Platform-optimized content
    posting_guide: Optional[str]  # Full posting guide with timing recommendations
