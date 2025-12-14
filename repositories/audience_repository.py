from pymongo import MongoClient, errors
from audience import Audience
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudienceRepository:
    def __init__(self, mongo_collection_name):
        try:
            connection_string = os.getenv("CONNECTION_STRING_MONGO")
            if not connection_string:
                raise ValueError("MongoDB connection string is not set in environment variables.")
            
            self.mongo_client = MongoClient(connection_string)
            self.mongo_db = self.mongo_client.get_database()
            self.mongo_collection = self.mongo_db[mongo_collection_name]
            logger.info(f"Connected to MongoDB collection: {mongo_collection_name}")
        except errors.ConnectionError as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred during MongoDB connection setup: {e}")
            raise

    def save_audience(self, audience: Audience):
        try:
            self.mongo_collection.insert_one(audience.to_dict())
            logger.info(f"Audience '{audience.name}' saved successfully.")
        except errors.PyMongoError as e:
            logger.error(f"Failed to save audience '{audience.name}': {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while saving audience '{audience.name}': {e}")
            raise

    def get_audiences(self):
        try:
            audiences = self.mongo_collection.find()
            audience_list = [Audience.from_dict(audience) for audience in audiences]
            logger.info(f"Retrieved {len(audience_list)} audiences from the database.")
            return audience_list
        except errors.PyMongoError as e:
            logger.error(f"Failed to retrieve audiences: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while retrieving audiences: {e}")
            raise