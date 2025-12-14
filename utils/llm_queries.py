import json
from langchain_core.prompts import ChatPromptTemplate
from agents.agent_state import ContentTemplate

example_content_template = ContentTemplate(
    name="Simple Campaign",
    liquid_template="""
    <div style="font-family: 'Arial', sans-serif; max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ccc; border-radius: 10px; background-color: #f9f9f9;">
        <h1 style="color: #333; text-align: center;">{{HeaderText}}</h1>
        <h2 style="color: #555; text-align: center;">{{SubheaderText}}</h2>
        <p style="color: #666; font-size: 14px; line-height: 1.6;">{{BodyText}}</p>
    </div>
    """,
    items=[
        {"Type": "Text", "Name": "Header Text", "MaxLength": 50, "Id": "HeaderText", "IsRequired": True},
        {"Type": "Text", "Name": "Subheader Text", "MaxLength": 50, "Id": "SubheaderText", "IsRequired": False},
        {"Type": "TextArea", "Name": "Body Text", "MaxLength": 2000, "Id": "BodyText", "IsRequired": True}
    ],
    example_query="Announcing a scheduled maintenance on August 12, 2022. Please ensure all work is saved and log out by 10:00 AM UTC to avoid data loss."
)

predefined_query = """
Launch a marketing campaign for a new medical drugs. Highlight its unique specification, good quality, and amazing medical result. The campaign should appeal to people from 30-60 y.o. Include a catchy slogan and a call to action to buy the drugs and feel yourself better.
"""
# predefined_query = """
# Launch a marketing campaign for a new multiplayer online battle arena (MOBA) game. Highlight its unique characters, strategic gameplay, and competitive ranking system. The campaign should appeal to both casual and hardcore gamers. Include a catchy slogan and a call to action to download the game and join the battle.
# """

example_output = {
    "HeaderText": "Buy your new Medical Drug!",
    "SubheaderText": "Unleash Your Profit",
    "BodyText": "Check our new Medical Drugs, good quality, amazing medical results, and fitting for different ages. Come to our shop!"
}

system_prompt_template = ChatPromptTemplate.from_template(
    """
    You are a marketing campaign generator and translator. You generate the campaign content in the JSON format.
    You will be provided with a liquid template, that could be any: HTML, JSON, XML, etc. and the JSON with requirements to the generated content.
    As output you should provide a JSON with the content based on the template items. Keys: should be ids from the template items.

    Example:
    Query: "{example_query}"

    Example Template:
    ```{example_template}```

    Template items for the template:
    ```
    {example_template_items}
    ```

    Example output:
    ```
    {example_output}
    ```

    Provide in output just json, do not add any formatting(e.g ```).
    """
)

system_prompt = system_prompt_template.format(
    example_query=predefined_query,
    example_template=example_content_template.liquid_template,
    example_template_items=json.dumps(example_content_template.items),
    example_output=json.dumps(example_output)
)

translate_prompt = "Translate the following JSON values into {language_keys} while preserving the main context, style, tone, and idea. If idioms are used, try to find an idiom with the same idea in the native language."

criticize_prompt = """Provide constructive criticism and helpful suggestions to improve the translation for the following translations:\n    
When writing suggestions, pay attention to whether there are ways to improve the translation's \n\
(i) accuracy (by correcting errors of addition, mistranslation, omission, or untranslated text),\n\
(ii) fluency (by applying the langauge grammar, spelling and punctuation rules, and ensuring there are no unnecessary repetitions),\n\
(iii) style (by ensuring the translations reflect the style of the source text and take into account any cultural context),\n\
(iv) terminology (by ensuring terminology use is consistent and reflects the source text domain; and by only ensuring you use equivalent idioms {target_lang}).\n\

Write a list of specific, helpful and constructive suggestions for improving the translation.
Each suggestion should address one specific part of the translation.
Output only the suggestions and nothing else.
        """

reflection_prompt = """Improve the following translations based on these suggestions:\n
        Please take into account the expert suggestions when editing the translation. Edit the translation by ensuring:

(i) accuracy (by correcting errors of addition, mistranslation, omission, or untranslated text),
(ii) fluency (by applying the language grammar, spelling and punctuation rules and ensuring there are no unnecessary repetitions), \
(iii) style (by ensuring the translations reflect the style of the source text)
(iv) terminology (inappropriate for context, inconsistent use), or
(v) other errors.
"""

class DefaultPrompts:
    system_prompt = system_prompt
    translate_prompt = translate_prompt
    criticize_prompt = criticize_prompt
    reflection_prompt = reflection_prompt