from os import getenv
from urllib.parse import urlparse

# from azure.storage.blob import BlobServiceClient
import psycopg2
import pymilvus
import pymongo
import pymongo.errors as pymongo_errors
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

st.title("Resources Check")

"### MongoDB"

connection_string_mongo = getenv("CONNECTION_STRING_MONGO")
if connection_string_mongo:
    "- ✅ CONNECTION_STRING_MONGO is set"
    client = pymongo.MongoClient(
        connection_string_mongo,
        connectTimeoutMS=5000,
    )
    try:
        client.admin.command("ping")
        "- ✅ Connection established"
    except pymongo_errors.ConnectionFailure as e:
        st.error("Server not available")
        st.exception(e)
else:
    st.error("CONNECTION_STRING_MONGO is missing")


"### PostgreSQL"

connection_string_postgres = getenv("CONNECTION_STRING_POSTGRES")
if connection_string_postgres:
    "- ✅ CONNECTION_STRING_POSTGRES is set"
    try:
        connection_params = urlparse(connection_string_postgres)
        with psycopg2.connect(
            host=connection_params.hostname,
            user=connection_params.username,
            password=connection_params.password,
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database();")
                (db_name,) = cur.fetchone()  # type: ignore
                f"- ✅ Connection established, DB: {db_name}"
    except Exception as e:
        st.error(f"Connection failed: {e}")
else:
    st.error("CONNECTION_STRING_POSTGRES is missing")


"### Milvus"

connection_string_postgres = getenv("CONNECTION_STRING_MILVUS")
if connection_string_postgres:
    "- ✅ CONNECTION_STRING_MILVUS is set"
    try:
        pymilvus.connections.connect(uri=connection_string_postgres)
        collections = pymilvus.utility.list_collections()
        f"- ✅ Connection established, Collections: {collections}"
    except Exception as e:
        st.error(f"Connection failed: {e}")
else:
    st.error("CONNECTION_STRING_MILVUS is missing")

"### Azure Blob Storage"

"Please check it yourself, we couldn't make it in time"

"### Persistent Volume check"

"Please check it yourself, we couldn't make it in time"
