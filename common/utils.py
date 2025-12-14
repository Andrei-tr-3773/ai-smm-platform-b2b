import json
import re
import os
from json import JSONDecodeError
from typing import Any
import logging
import shutil

import streamlit as st

from common.llm import dedent

from json_repair import repair_json

logger = logging.getLogger(__name__)

_EXTRA_COMMA_ARRAY_REGEX = re.compile(r"},\s*]")
_EXTRA_COMMA_ARRAY_SUBSTITUTION = "}]"
_MISSING_COMMA_ARRAY_REGEX = re.compile(r"}\s*{")
_MISSING_COMMA_ARRAY_SUBSTITUTION = "},{"


__pattern = r"```json\s*([\{\[].*?[\}\]])\s*```"


def safe_json(json_str: str) -> Any:
    try:
        return json.loads(json_str)
    except (ValueError, JSONDecodeError):
        # Use re.DOTALL to make the dot match newlines as well
        match = re.search(__pattern, json_str, re.DOTALL)

        if match:
            unwrapped_json_str = match.group(1)
            try:
                return json.loads(unwrapped_json_str)
            except json.JSONDecodeError:
                __error_debug(json_str)
                raise ValueError("Invalid JSON string")
        else:
            __error_debug(json_str)
            raise ValueError("No JSON found in the Markdown string")


def load_and_repair_json(json_string: str):
    try:
        result = json.loads(json_string)
    except json.JSONDecodeError as e:
        logger.warning(
            f"Error parsing JSON: {e}\n\nInput:{json_string}\n\nAttempting repair..."
        )
        json_string = re.sub(
            _EXTRA_COMMA_ARRAY_REGEX,
            _EXTRA_COMMA_ARRAY_SUBSTITUTION,
            json_string,
        )
        json_string = re.sub(
            _MISSING_COMMA_ARRAY_REGEX,
            _MISSING_COMMA_ARRAY_SUBSTITUTION,
            json_string,
        )
        result = repair_json(
            json_string,
            # return_objects=True,
        )

        logger.debug(f"Repair result: {result}")
        logger.warning("Repair successful!")

    return result


def __error_debug(json_str):
    with st.expander(label="JSON Parsing Error", expanded=False):
        st.error("Unable to parse JSON. Original LLM reply goes below")
        st.code(json_str, language="javascript")


def get_prompt(config_preset: dict, attribute: str) -> str:
    prompts = {
        p["promptTitle"]: p["prompt"] for p in config_preset[attribute]
    }
    return dedent(list(prompts.values())[0])
    # selected = st.selectbox(
    #     "Predefined Prompts",
    #     options=prompts.keys(),
    #     key=f"selectbox:{attribute}",
    # )
    # if selected is None:
    #     return ""
    # return dedent(prompts.get(selected, ""))


def load_css(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        st.markdown(
            f"<style data-id=\"{file_name}\">{f.read()}</style>", unsafe_allow_html=True)


def merge_folders(source, destination, override=False):
    """
    Merge the contents of the source folder into the destination folder.

    Args:
        source: Path to the source folder (relative or absolute).
        destination: Path to the destination folder (relative or absolute).
        override: Whether to override existing files in the destination folder. Defaults to False.
    """
    abs_source = os.path.abspath(source)
    abs_destination = os.path.abspath(destination)

    if not os.path.exists(abs_source):
        raise FileNotFoundError(
            f"Source folder '{abs_source}' does not exist.")

    if not os.path.exists(abs_destination):
        os.makedirs(abs_destination)

    for item in os.listdir(abs_source):
        source_item_path = os.path.join(abs_source, item)
        destination_item_path = os.path.join(abs_destination, item)

        # If item is a file, copy or move it to destination folder
        if os.path.isfile(source_item_path):
            if os.path.exists(destination_item_path) and not override:
                logging.info(
                    f"Skipping '{item}' because it already exists in the destination folder")
            else:
                action = "Copying"
                level = logging.INFO
                if override:
                    action = "Overriding"
                    level = logging.WARNING
                logging.log(level, f"{action} '{item}' to '{abs_destination}'")

                shutil.copy2(source_item_path, abs_destination)

        # If item is a folder, recursively merge its contents
        elif os.path.isdir(source_item_path):
            merge_folders(source_item_path, destination_item_path, override)
