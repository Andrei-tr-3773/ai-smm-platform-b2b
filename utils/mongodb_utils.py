# mongodb_utils.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from campaign import Campaign

# Load environment variables from .env file
load_dotenv(override=True)

class MongoDBClient:
    def __init__(self, collection_name):
        self.client = MongoClient(os.getenv("CONNECTION_STRING_MONGO"))
        self.db = self.client.get_database()
        self.collection = self.db[collection_name]

    def get_templates(self):
        templates = self.collection.find()
        return list(templates)

    def get_template_by_name(self, name):
        template = self.collection.find_one({"name": name})
        return template

    def save_campaign(self, campaign: Campaign):
        self.collection.insert_one(campaign.to_dict())

    def get_campaigns(self):
        campaigns = self.collection.find()
        return [Campaign.from_dict(campaign) for campaign in campaigns]