from os import getenv
import streamlit as st
from openai import OpenAI
from PIL import Image
from utils.ui_components import init_page_settings, load_css

## Load the favico, you can set different favico (and all other settings) per page.
favico = Image.open("./static/images/favicon.ico")
## It is important that you call this function for EACH page.
## Also this function MUST be the first streamlit function you call in your script.
## Otherwise the app will crash.
init_page_settings()

## Loading your local copy of the styleguide, you can change that as you see fit
## It is important that you call this function in *EACH* streamlit page you have for it to work
## Generally any built-in component should work fine, in case if not you can contact @Maksim_Shastsel
load_css("./static/ui/css/styles.css")

st.title("OpenAI Check")

api_key = getenv("AZURE_OPENAI_API_KEY")
if not api_key:
    st.error("AZURE_OPENAI_API_KEY is missing")
    st.stop()

"- ✅ AZURE_OPENAI_API_KEY is set"

model_name = getenv("AZURE_OPENAI_MODEL", "gpt-4o-mini")
"- ✅ Model: " + model_name

_client = OpenAI(api_key=api_key)

if st.button("List models", type="primary"):
    try:
        response = _client.models.list()
        models_mapped = [x.id for x in response.data]
        st.write(models_mapped)
    except Exception as e:
        st.error(f"Error listing models: {e}")

if st.button("Tell me a joke", type="primary"):
    try:
        response = _client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": "Tell me a joke",
                }
            ],
            temperature=1.0,
        )

        st.code(
            response.choices[0].message.content,
            language="markdown",
        )
    except Exception as e:
        st.error(f"Error: {e}")
