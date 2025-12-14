import json
import logging
import os
import streamlit as st

from common.utils import merge_folders

SOURCE_ASSETS_FOLDER = "../../../libs/assets"
DESTINATION_ASSETS_FOLDER = "./static/common"


def get_app_default_assets():
    merge_folders(SOURCE_ASSETS_FOLDER,
                  DESTINATION_ASSETS_FOLDER, override=False)


@st.cache_data(
    ttl=int(os.environ.get("CONFIG_CACHE_TTL_SECONDS", "60")),  # seconds
    show_spinner=False,
)
def pull_app_assets():
    logging.info(
        "Merging local and common assets...")
    return get_app_default_assets()
