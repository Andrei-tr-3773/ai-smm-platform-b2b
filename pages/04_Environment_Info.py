import json
from os import environ
import streamlit as st

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

st.title("Environment Info")

st.code(
    json.dumps(dict(environ), indent=2),
    language="json",
)
