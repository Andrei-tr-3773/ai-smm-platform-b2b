import json
import logging
import os

import requests

import streamlit as st

def get_strapi_catalog_content(app_name) -> dict:
    STRAPI_URL = os.environ.get("STRAPI_URL")
    STRAPI_TOKEN = os.environ.get("STRAPI_TOKEN")

    url = f"{STRAPI_URL}/api/catalogs?filters[app_name]={app_name}&populate=*"

    payload = {}
    headers = {"Authorization": f"Bearer {STRAPI_TOKEN}"}

    try:
        response = requests.request("GET", url, headers=headers, data=payload, verify=False)
    except Exception:
        logging.exception("Error occurred while making request")
        return None

    if response.status_code != 200:
        return None

    if len(response.json()["data"]) == 0:
        return None

    return response.json()["data"][0]


def get_default_catalog_content() -> dict:
    with open("./resources/default_catalog_content.json", "r", encoding="utf-8") as f:
        return json.loads(f.read())


@st.cache_data(
    ttl=int(os.environ.get("CONFIG_CACHE_TTL_SECONDS", "60")),  # seconds
    show_spinner=False,
)
def pull_catalog_content(app_name):
    if os.environ.get("STRAPI_INTEGRATION", "false") == "true":
        logging.info("Strapi integration enabled. Pulling catalog content...")
        config = get_strapi_catalog_content(app_name)
        if config is None:
            logging.warn(f"Failed to retrive catalog content, fallback to catalog content from the source code...")
            return get_default_catalog_content()
        return config
    else:
        logging.info("Strapi integration disabled. Using catalog content from the source code...")
        return get_default_catalog_content()
