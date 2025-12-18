from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

connection_string = os.getenv("CONNECTION_STRING_MONGO")
print(f"Connection string: {connection_string}")

client = MongoClient(connection_string)
db = client.get_database()
print(f"Database name: {db.name}")
print(f"Collections: {db.list_collection_names()}")
print(f"Templates count: {db.content_templates.count_documents({})}")
print(f"Audiences count: {db.audiences.count_documents({})}")
