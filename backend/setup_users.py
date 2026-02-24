from database.connection import db

users = [
    {"_id": "user_fixed_1", "name": "Alice", "rating": 4.8},
    {"_id": "user_fixed_2", "name": "Bob", "rating": 4.9},
    {"_id": "user_fixed_3", "name": "Charlie", "rating": 4.7}
]

for user in users:
    db.users.update_one({"_id": user["_id"]}, {"$set": user}, upsert=True)

print("3 Fixed Users initialized in MongoDB.")