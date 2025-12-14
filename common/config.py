import json
import logging
from os import getenv
from pathlib import Path
from typing import Optional

import streamlit as st
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from common.strapi_client import client


class ModelConfigItem(BaseModel):
    name: str
    value: str


class ModelConfig(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    available_models: list[ModelConfigItem]
    default_model: ModelConfigItem
    temperature: float
    ignore_llm_cache: bool = Field(alias="ignoreLLMCache")


def getenv_bool(key: str, default: bool = False) -> bool:
    value = getenv(key)
    if value is None:
        return default
    return value.lower() == "true"


def _fetch_remote_app_config(presets_resource: str) -> list | None:
    try:
        response = client.list_entities(presets_resource)
    except Exception:
        logging.exception("Error fetching app presets")
        return None

    # atm all presets that we're using are **collection** types
    # so we're expecting a list of items
    if not isinstance(response, list):
        raise ValueError("Unexpected payload format from CMS. Check preset schema")

    if len(response) == 0:
        return None

    return response


def _get_local_app_config() -> list:
    default_config_file = Path("./resources/default_config.json")
    config = json.loads(default_config_file.read_text(encoding="utf-8"))

    if not isinstance(config, list):
        raise ValueError("Unexpected payload format. Check default_config.json")

    return config


@st.cache_data(
    ttl=int(getenv("CONFIG_CACHE_TTL_SECONDS", "60")),  # seconds
    show_spinner=False,
)
def pull_app_config(presets_resource):
    if getenv_bool("STRAPI_INTEGRATION"):
        logging.info("STRAPI integration enabled. Pulling app config...")
        config = _fetch_remote_app_config(presets_resource)
        if config:
            return config
        logging.warning("Failed to pull app config")

    logging.info("Using app config from the source code...")
    return _get_local_app_config()


def _fetch_remote_model_config(config_id: str) -> dict | None:
    try:
        return client.get_entity("demo-configurations", config_id, {"populate": "*"})
    except Exception:
        logging.exception("Error fetching remote model config")
        return None


def _get_local_model_config() -> ModelConfig:
    default_config_file = Path("./resources/default_model_config.json")
    return ModelConfig.model_validate_json(default_config_file.read_text(encoding="utf-8"))


@st.cache_data(
    ttl=int(getenv("CONFIG_CACHE_TTL_SECONDS", "60")),  # seconds
    show_spinner=False,
)
def pull_model_config(external_config_id: Optional[str] = None) -> ModelConfig:
    if getenv_bool("STRAPI_INTEGRATION"):
        logging.info("STRAPI integration enabled. Pulling model config...")
        config_id = external_config_id or getenv("MODEL_CONFIG_ID")
        if config_id:
            config = _fetch_remote_model_config(config_id)
            if config:
                return ModelConfig.model_validate(config)
            logging.warning("Failed to pull model config")
        else:
            logging.warning("MODEL_CONFIG_ID not set")

    logging.info("Using model config from the source code...")
    return _get_local_model_config()
