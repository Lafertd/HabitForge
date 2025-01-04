from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from uuid import uuid4  # Correct import for uuid
import uuid
from datetime import datetime, timedelta
import os

mongo_uri = os.getenv('MONGODB_URI')  # Must be set in production environment
if not mongo_uri:
    raise ValueError("MONGODB_URI must be set in production environment")

class User:
    def __init__(self, username, password):
        self.user_id = uuid4()  # Corrected UUID generation
        self.username = username
        self.password = password
        self.client = MongoClient(mongo_uri)
        self.db = self.client['habitforge']
        self.users = self.db['users']

    def save(self):
        """ Save a new user with hashed password to the database. """
        hashed_password = generate_password_hash(self.password, method='pbkdf2:sha256', salt_length=8)
        user_data = {
            "user_id": str(self.user_id),  # Ensure UUID is saved as a string
            "username": self.username,
            "password": hashed_password
        }
        # Insert the user into the MongoDB collection
        self.users.insert_one(user_data)

    @staticmethod
    def find_user_by_username(username):
        """ Find a user by username. """
        client = MongoClient(mongo_uri)
        db = client['habitforge']
        users = db['users']
        user = users.find_one({"username": username})
        return user  # Will return None if not found, no need for try-except for this

    def update_password(self, new_password):
        """ Update the password for the user. """
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)
        self.users.update_one({"username": self.username}, {"$set": {"password": hashed_password}})
