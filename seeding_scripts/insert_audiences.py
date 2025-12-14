# insert_audiences.py - B2B Audiences
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables from .env file
load_dotenv(override=True)

connection_string = os.getenv("CONNECTION_STRING_MONGO")

# Parse database name correctly (handle query parameters)
parsed_url = urlparse(connection_string)
db_name = parsed_url.path.lstrip('/')  # Remove leading slash
if '?' in db_name:
    db_name = db_name.split('?')[0]  # Remove query parameters

client = MongoClient(connection_string)
db = client[db_name]
collection = db["audiences"]

audiences = [
    {
        "name": "Business Owners",
        "description": "Entrepreneurs and business owners with 10-100+ employees. They are looking for cost-effective solutions to improve productivity, streamline operations, and grow their business. Budget-conscious but willing to invest in quality tools that deliver ROI."
    },
    {
        "name": "Marketing Managers",
        "description": "Marketing professionals in mid-to-large companies responsible for campaign management, social media strategy, and content creation. They need efficient tools for multi-channel marketing, analytics, and team collaboration. Tech-savvy, data-driven, and focused on engagement metrics."
    },
    {
        "name": "Agency Partners",
        "description": "Marketing and creative agencies serving multiple clients across various industries. They require scalable solutions, white-label options, and bulk management capabilities. High volume users who value automation, customization, and client reporting features."
    },
]

# Clear existing audiences and insert new ones
collection.delete_many({})
collection.insert_many(audiences)

print(f"Successfully inserted {len(audiences)} B2B audiences into {db_name}.audiences")
print("Audience names:")
for audience in audiences:
    print(f"  - {audience['name']}: {audience['description'][:60]}...")
