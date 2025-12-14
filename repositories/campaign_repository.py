from pymongo import MongoClient, errors as mongo_errors
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility, exceptions as milvus_errors
from utils.azure_openai_utils import generate_embeddings  # Import from utils
from campaign import Campaign
import os
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Parse Milvus connection string (optional - only if RAG is needed)
milvus_conn_str = os.getenv("CONNECTION_STRING_MILVUS")
milvus_available = False

if milvus_conn_str:
    try:
        parsed_url = urlparse(milvus_conn_str)
        milvus_host = parsed_url.hostname
        milvus_port = parsed_url.port
        milvus_user = parsed_url.username
        milvus_password = parsed_url.password
        milvus_database = parsed_url.path.lstrip('/')  # Extract the database from the path

        connections.connect(
            alias="default",
            host=milvus_host,
            port=str(milvus_port),
            user=milvus_user,
            password=milvus_password,
            db_name=milvus_database
        )
        logger.info("Connected to Milvus successfully.")
        milvus_available = True
    except Exception as e:
        logger.warning(f"Failed to connect to Milvus: {e}. RAG functionality will be disabled.")
        milvus_available = False
else:
    logger.info("Milvus connection string not provided. RAG functionality will be disabled.")

class CampaignRepository:
    def __init__(self, mongo_collection_name, milvus_collection_name, similarity_threshold=0.5):
        try:
            connection_string = os.getenv("CONNECTION_STRING_MONGO")
            if not connection_string:
                raise ValueError("MongoDB connection string is not set in environment variables.")
            
            self.mongo_client = MongoClient(connection_string)
            self.mongo_db = self.mongo_client.get_database()
            self.mongo_collection = self.mongo_db[mongo_collection_name]
            logger.info(f"Connected to MongoDB collection: {mongo_collection_name}")
        except mongo_errors.ConnectionError as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred during MongoDB connection setup: {e}")
            raise

        self.milvus_collection_name = milvus_collection_name
        self.similarity_threshold = similarity_threshold
        self._setup_milvus()
        
    def _setup_milvus(self):
        global milvus_available

        if not milvus_available:
            logger.info("Milvus is not available. Skipping Milvus setup.")
            self.milvus_collection = None
            return

        try:
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=5000),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536)
            ]
            schema = CollectionSchema(fields, "Campaign content embeddings")

            if not utility.has_collection(self.milvus_collection_name):
                self.milvus_collection = Collection(name=self.milvus_collection_name, schema=schema)
                logger.info(f"Created Milvus collection: {self.milvus_collection_name}")
            else:
                self.milvus_collection = Collection(name=self.milvus_collection_name)
                logger.info(f"Using existing Milvus collection: {self.milvus_collection_name}")

            index_params = {
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128},
                "metric_type": "L2"
            }
            if not self.milvus_collection.has_index():
                self.milvus_collection.create_index(field_name="embedding", index_params=index_params)
                logger.info(f"Created index on Milvus collection: {self.milvus_collection_name}")

            self.milvus_collection.load()
            logger.info(f"Loaded Milvus collection: {self.milvus_collection_name}")
        except Exception as e:
            logger.warning(f"Failed to set up Milvus collection: {e}. RAG functionality will be disabled.")
            self.milvus_collection = None
            milvus_available = False

    def save_campaign(self, campaign: Campaign):
        try:
            self.mongo_collection.insert_one(campaign.to_dict())
            logger.info(f"Campaign '{campaign.name}' saved to MongoDB.")

            # Save to Milvus only if available
            if self.milvus_collection is not None:
                english_content_dict = campaign.localized_content.get('en-US', {})
                english_content = '\n'.join(english_content_dict.values())

                embedding = generate_embeddings(english_content)

                data = [
                    [english_content],
                    [embedding]
                ]

                self.milvus_collection.insert(data)
                logger.info(f"Campaign '{campaign.name}' saved to Milvus.")
            else:
                logger.debug(f"Milvus not available. Campaign '{campaign.name}' saved to MongoDB only.")
        except mongo_errors.PyMongoError as e:
            logger.error(f"Failed to save campaign '{campaign.name}': {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while saving campaign '{campaign.name}': {e}")
            raise

    def search_similar_campaigns(self, text):
        if self.milvus_collection is None:
            logger.debug("Milvus not available. Returning empty list for similar campaigns.")
            return []

        try:
            query_embedding = generate_embeddings(text)

            search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
            results = self.milvus_collection.search([query_embedding], "embedding", search_params, limit=5, output_fields=["text"])

            similar_contents = []
            for result in results[0]:  # Assuming 1 query, hence results[0]
                if result.distance < self.similarity_threshold:
                    similar_contents.append(result.entity.get("text"))

            logger.info(f"Found {len(similar_contents)} similar campaigns.")
            return similar_contents
        except Exception as e:
            logger.warning(f"Failed to search similar campaigns: {e}. Returning empty list.")
            return []

    def get_campaigns(self):
        try:
            campaigns = self.mongo_collection.find()
            campaign_list = [Campaign.from_dict(campaign) for campaign in campaigns]
            logger.info(f"Retrieved {len(campaign_list)} campaigns from MongoDB.")
            return campaign_list
        except mongo_errors.PyMongoError as e:
            logger.error(f"Failed to retrieve campaigns: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while retrieving campaigns: {e}")
            raise