import streamlit as st

def init_page_settings():
    st.set_page_config(
        layout="wide",
        page_title="AI SMM Platform for B2B",
        page_icon="./static/images/favicon.svg",
        initial_sidebar_state="collapsed"
    )

def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)