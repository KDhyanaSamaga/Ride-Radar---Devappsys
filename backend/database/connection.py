from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

client = MongoClient(
    "mongodb://localhost:27017/",
    serverSelectionTimeoutMS=5000
)

try:
    client.admin.command('ping')
    print("Connection Successfully")
    
except ConnectionFailure:
    print("Connection Failed")
    raise

db = client["NewTry"]


