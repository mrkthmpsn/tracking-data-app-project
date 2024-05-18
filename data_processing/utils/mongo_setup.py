"""
File for database-related utils
"""
import certifi
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pymongo.server_api import ServerApi

load_dotenv()


def get_mongo_client() -> MongoClient:
    """Instantiate a MongoClient"""

    # Fetch MongoDB connection details from environment variables
    mongo_uri = os.getenv("MONGO_URI", "")
    # return MongoClient(mongo_uri)
    return MongoClient(mongo_uri, server_api=ServerApi("1"), tlsCAFile=certifi.where())


def get_database(db_name):
    """Use MongoClient to get a named database"""

    client = get_mongo_client()
    return client[db_name]


def get_collection(collection_name, db_name="metrica_tracking"):
    """Use MongoClient to get a named collection from a database"""

    db = get_database(db_name)
    collection = db[collection_name]

    return collection
