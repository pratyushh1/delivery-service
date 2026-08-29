import os
from pymongo import MongoClient

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "deliverydb")
MONGO_USER = os.getenv("MONGO_USER", "")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "")

if MONGO_USER and MONGO_PASSWORD:
    MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"
else:
    MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

deliveries_collection = db["deliveries"]
