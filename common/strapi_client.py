from os import getenv
from typing import Any, Optional

import requests


def _unpack_api_wrapped_obj(data: dict) -> dict | list | None:
    if "data" not in data:
        return None

    nested_data = data.get("data")

    def has_attributes(x):
        return isinstance(x, dict) and "attributes" in x

    if isinstance(nested_data, dict) and has_attributes(nested_data):
        return nested_data["attributes"]

    if isinstance(nested_data, list) and all(has_attributes(x) for x in nested_data):
        return [x["attributes"] for x in nested_data]

    return None


def _unwrap_api_response(
    data: Any,
    ignoredKeys: Optional[list[str]] = None,
) -> Any:
    # Funny things we can do the same on STRAPI side
    # using middlewares. But I learned it too late.

    if isinstance(data, dict):
        ignoredKeys = ignoredKeys or []

        result = _unpack_api_wrapped_obj(data)
        if result is not None:
            return _unwrap_api_response(result, ignoredKeys)

        result = {}
        for key, value in data.items():
            if key in ignoredKeys:
                continue
            result[key] = _unwrap_api_response(value, ignoredKeys)

        return result

    if isinstance(data, list):
        return [_unwrap_api_response(item, ignoredKeys) for item in data]

    return data


class StrapiClient:
    def __init__(
        self,
        api_base_url: str | None,
        api_token: str | None,
        verify_ssl: Optional[bool] = False,
        ignored_response_keys: Optional[list[str]] = [
            "createdAt",
            "updatedAt",
            "publishedAt",
            "meta",
        ],
    ):
        # if api_base_url is None or api_token is None:
        #     raise ValueError("apiBaseUrl, apiToken are required")

        self.__api_base_url = api_base_url
        self.__api_token = api_token
        self.__verify_ssl = verify_ssl
        self.__ignored_response_keys = ignored_response_keys

    def __build_auth_headers(self):
        return {"Authorization": f"Bearer {self.__api_token}"}

    def __make_request(self, url: str, query: dict, raw: bool):
        response = requests.get(
            url,
            params=query,
            headers=self.__build_auth_headers(),
            verify=self.__verify_ssl,
        )
        response.raise_for_status()

        data = response.json()
        if raw:
            return data

        return _unwrap_api_response(
            data,
            self.__ignored_response_keys,
        )

    def list_entities(
        self,
        entity: str,
        query: dict = {},
        raw: bool = False,
    ):
        url = f"{self.__api_base_url}/api/{entity}"
        return self.__make_request(url, query, raw)

    def get_entity(
        self,
        entity: str,
        id: str,
        query: dict = {},
        raw: bool = False,
    ):
        url = f"{self.__api_base_url}/api/{entity}/{id}"
        return self.__make_request(url, query, raw)


client = StrapiClient(
    api_base_url=getenv("STRAPI_URL"),
    api_token=getenv("STRAPI_TOKEN"),
    verify_ssl=False,
)
