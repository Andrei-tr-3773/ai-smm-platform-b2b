import streamlit as st

from utils.ui_components import init_page_settings, load_css
from common.ui import render_preface, chapter

from PIL import Image

## Load the favico, you can set different favico (and all other settings) per page.
favico = Image.open("./static/images/favicon.ico")
## It is important that you call this function for EACH page.
## Also this function MUST be the first streamlit function you call in your script.
## Otherwise the app will crash.
init_page_settings()

## Loading your local copy of the styleguide, you can change that as you see fit
## It is important that you call this function in *EACH* streamlit page you have for it to work
## Generally any built-in component should work fine, in case if not you can contact @Maksim_Shastsel
## See https://docs.streamlit.io/develop/api-reference/ for more components
## You can also find some examples below
## This file is available for you locally in the repo, you can edit it if you need to
load_css("./static/ui/css/styles.css")

## Points are the key-value pairs that will be rendered below the title
## They are used in the 'render preface' below
## * You can specify the icon, title and content for each point
## * You can have as mamy points as you see fit, howewer we not do not recommend more than 4-5
## * Supported icons are: magnifier, globe, laptop, chain, eye
## * You can use markdown in the content of each point
points = [
    {
      "icon": "magnifier",
      "content": 
        """Points are the key-value pairs that will be rendered below the title
            * You can specify the icon, title and content for each point
            * You can have as mamy points as you see fit, howewer we not do not recommend more than 4
            * Supported icons are: magnifier, globe, laptop, chain, eye
            * You can use markdown in the content of each point""",
      "title": "What can it unlock?"
    },
    {
      "icon": "globe",
      "content": 
        """Points are the key-value pairs that will be rendered below the title
            * You can specify the icon, title and content for each point
            * You can have as mamy points as you see fit, howewer we not do not recommend more than 4
            * Supported icons are: magnifier, globe, laptop, chain, eye
            * You can use markdown in the content of each point""",
      "title": "Benefits"
    },
    {
      "icon": "laptop",
      "content": 
        """Points are the key-value pairs that will be rendered below the title
            * You can specify the icon, title and content for each point
            * You can have as mamy points as you see fit, howewer we not do not recommend more than 4
            * Supported icons are: magnifier, globe, laptop, chain, eye
            * You can use markdown in the content of each point""",
      "title": "Data sources"
    },
    {
      "icon": "chain",
      "content": 
        """Points are the key-value pairs that will be rendered below the title
            * You can specify the icon, title and content for each point
            * You can have as mamy points as you see fit, howewer we not do not recommend more than 4
            * Supported icons are: magnifier, globe, laptop, chain, eye
            * You can use markdown in the content of each point""",
      "title": "Related ideas"
    },
    {
      "icon": "eye",
      "content": 
        """Points are the key-value pairs that will be rendered below the title
            * You can specify the icon, title and content for each point
            * You can have as mamy points as you see fit, howewer we not do not recommend more than 4
            * Supported icons are: magnifier, globe, laptop, chain, eye
            * You can use markdown in the content of each point""",
      "title": "Way forward"
    }
]

render_preface(
        ## Title of your demo
        title="Styleguide (Demo)",
        ## Description of your demo
        text="Short description of the demo. This is the plain text, try to keep it short and concise.",
        points=points,
        ## Secondaty title, usually you can use that to provide 'preparation' for the demo
        follow_up_title="Secondary title, leave it empty if you don't need it",
        ## Secondaty text, usually you will use that, to provide some guidance before the demo
        follow_up_text="Secondary text, leave it empty if you don't need it",
)

## You can use `chapter` to split your demo into chapters
## Alternativelly you can use markdown heading or st.title
chapter("Chapter 1 - Split your demo into chapters")

## Even if linter says that the statement below has no effect, it does.
"To achive the result above markdown heading is used. We recommend that you split your demo into consumable chunks."

## See https://docs.streamlit.io/develop/api-reference/text/st.text for more information
## Note that that is a preformatted text
st.text("You can use `st.text` to create a monospaced ('code') text.")


chapter("Chapter 2 - Inputs")
## Please see streamlit documentation for more information on the inputs
## https://docs.streamlit.io/develop/api-reference/widgets

## See https://docs.streamlit.io/develop/api-reference/widgets/st.radio
st.radio("I am example of a radio button:", ["option 1", "option 2", "option 3"])

## See https://docs.streamlit.io/develop/api-reference/widgets/st.selectbox
st.selectbox("I am example of a dropdown:", ["option 1", "option 2", "option 3"])

## See https://docs.streamlit.io/develop/api-reference/widgets/st.text_input
st.text_input(
            "Single line input", "Default value",
)

## See https://docs.streamlit.io/develop/api-reference/widgets/st.text_area
st.text_area(
    label="Text area with label",
    value="Default value, you can change it. You can also deifne the height of the text area in lines. Please see st documentation for more",
    help="This is a help text, you can use it to provide additional information to the user.",
    max_chars=1000,
    height=6,
)

## See https://docs.streamlit.io/develop/api-reference/widgets/st.text_area
st.text_area(
    label="Disabled text area",
    disabled=True,
    value="Disabled text area can be used as a plain text output for the LLM.",
    help="This is a help text, you can use it to provide additional information to the user.",
    max_chars=1000,
    height=6,
)

## See https://docs.streamlit.io/develop/api-reference/widgets/st.button
st.button("I am a button")

## See https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader
st.file_uploader(label="I am a multiple file input", accept_multiple_files=False)

chapter("Chapter 3 - Layout")

st.subheader("Table")
## See https://docs.streamlit.io/develop/api-reference/layout/st.table
st.table(
    {
        "First column": [1, 2, 3, 4],
        "Second column": [10, 20, 30, 40],
    }
)

st.subheader("Columns")
## If you have a lot of content to be displayed, we recommend that you conder following layout tricks:
## See https://docs.streamlit.io/develop/api-reference/layout/st.columns
col1, col2 = st.columns([1, 1])
with col1:
    ## Even if pylint says that the statement below has no effect, it does.
    "You can use columns to layout your content."
with col2:
    st.code(
        """You can put any built-in component in the columns. Usually it will layout itself just fine""",
    language="markdown",
)

st.subheader("Tabs")
## See https://docs.streamlit.io/develop/api-reference/layout/st.tabs
with st.container():
    video_tab, other = st.tabs(["Video", "Other tab"])
    with video_tab:
        video_url = st.text_input(
            "Video URL", "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        )
        if video_url:
            ## See https://docs.streamlit.io/develop/api-reference/media/st.video
            st.video(video_url)
            ## It is good to know that there are a lot of build-in/3rd party components that can be used for media
            ## See https://docs.streamlit.io/develop/api-reference/media for more information
        with other:
            "You can use tabs to split your content into tabs. It is a good way to split your content into sections."

chapter("Chapter 4 - Rest")

## See https://docs.streamlit.io/develop/api-reference/text/st.markdown for more information
## !It is important to know, that `st.markdown` can be used to insert custom JS/CSS into the page
st.markdown(
    """You can use `st.markdown` to render markdown text. It is a good way to provide additional information to the user.""",
)

## !It is important to know, that `st.markdown` can be used to insert custom JS/CSS into the page
## See https://docs.streamlit.io/develop/api-reference/text/st.markdown for more information
st.markdown(
    """You can use [Plotly Chart](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart) if you need charts""",
)

## See https://docs.streamlit.io/develop/api-reference/media/st.image for more information
st.image(
    "https://www.streamlit.io/images/brand/streamlit-mark-color.png",
)

st.subheader("Below is a markdowncode block")
## Advantage of presenting it as a code block is that it will be easier to copy-paste from it
st.code(
        """I am a markdown code block. We recomend to use such to display prompts.""",
        language="markdown",
)

## See https://docs.streamlit.io/develop/api-reference/text/st.subheader for more information
## Please note, that if you to use 'divider' not all of the color options are aligned with the stuileguide.
st.subheader("JSON Code block")
"You can use that to display JSON outputs from LLM"
## See https://docs.streamlit.io/develop/api-reference/text/st.code for more information
## We recommend to use this code block, to display JSON outputs as it supports
## a) syntax highlighting
## b) copy-paste
st.code(
"""
{
  "key": "value"
}
""",
    language="json",
)

## You can use st.spinner for loading indication
st.spinner("Loading indication...")
