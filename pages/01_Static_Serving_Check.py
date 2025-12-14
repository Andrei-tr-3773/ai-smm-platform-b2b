import streamlit as st

from PIL import Image

from utils.ui_components import load_css

## Load the favico, you can set different favico (and all other settings) per page.
favico = Image.open("./static/images/favicon.ico")
## It is important that you call this function for EACH page.
## Also this function MUST be the first streamlit function you call in your script.
## Otherwise the app will crash.
st.set_page_config(
    layout="wide",
    page_title="Simple App - Home",
    page_icon=favico,
    initial_sidebar_state="collapsed"
)

## Loading your local copy of the styleguide, you can change that as you see fit
## It is important that you call this function in *EACH* streamlit page you have for it to work
## Generally any built-in component should work fine, in case if not you can contact @Maksim_Shastsel
load_css("./static/ui/css/styles.css")

st.title("Static Serving Check")

"Demo on how to reference static files in Streamlit."

with st.echo():
    st.markdown("![Sunflowers, sun, rain](app/static/sunflowers.webp)")
