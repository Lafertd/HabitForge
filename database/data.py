from pymongo import MongoClient, ASCENDING
from werkzeug.security import generate_password_hash
from uuid import uuid4  # Correct import for uuid
import uuid
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv('MONGODB_URI')  # Must be set in production environment
if not mongo_uri:
    raise ValueError("MONGODB_URI must be set Configured")

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


class Habit:
    # Initialize the MongoDB client and collection at the class level
    client = MongoClient(mongo_uri)
    db = client['habitforge']
    habits = db['habits']
    habits.create_index([("username", ASCENDING), ("habit_name", ASCENDING)], unique=True)
    def __init__(self, username, habit_name=None, frequency=None, status=None):
        self.habit_id = uuid4()  # Corrected UUID generation
        self.username = username  # Use the username from JWT
        self.habit_name = habit_name
        self.frequency = frequency # Default to None if not provided
        self.status = status  # Default to None if not provided
        self.start_date = datetime.utcnow() # created_at that time

    # Ensure the Habit class has a find method defined to query the database
    @classmethod
    def find(cls, query):
        return cls.habits.find(query)  # Add this method to your Habit class

    
    @staticmethod
    def find_habit_by_id(habit_id):
        """ Find a user by username. """
        client = MongoClient(mongo_uri)
        db = client['habitforge']
        habits = db['habits']
        habit = habits.find_one({"habit_id": habit_id})
        return habit # return habit details

    def create(self):
        habit_data = {
            "username": self.username,
            "habit_id": str(self.habit_id),  # Ensure UUID is saved as a string
            "habit_name": self.habit_name,
            "frequency": self.frequency,
            "status": self.status,
            "start_date": self.start_date
        }
        self.habits.insert_one(habit_data)

    def rename_habit(self, habit_name, new_habit_name):
        habit = self.habits.find_one({"username": self.username, "habit_name": habit_name})
        if habit:
            self.habits.update_one(
                {"habit_id": habit["habit_id"]},
                {"$set": {"habit_name": new_habit_name}}
            )
            print("Habit renamed successfully.")
        else:
            print("Habit not found.")

    def delete_habit(self, habit_name):
        result = self.habits.delete_one({"username": self.username, "habit_name": habit_name})
        if result.deleted_count > 0:
            return f"Habit '{habit_name}' deleted successfully"
        else:
            return "Habit not found."


    def get_status(self, habit_name):
        habit = self.habits.find_one({"username": self.username, "habit_name": habit_name})
        if habit:
            return habit.get("status", "No status logged yet")
        return "Habit not found."

    def put_status(self, habit_name, status):
        self.habits.update_one(
            {"username": self.username, "habit_name": habit_name},
            {"$set": {"status": status}}
        )
        return f"Status for {habit_name} is '{status}'"

    def habit_frequency(self, habit_name):
        habit = self.habits.find_one({"username": self.username, "habit_name": habit_name})
        if habit:
            return habit.get("frequency")
        return f"Frequency not found"

class Habit_Log:
    # Initialize the MongoDB client and habit_logs collection at the class level
    client = MongoClient(mongo_uri)
    db = client['habitforge']
    habit_logs = db['habit_logs']
    habit_logs.create_index([('username', ASCENDING), ('habit_name', ASCENDING), ('log', ASCENDING), ('timestamp', ASCENDING)], unique=True)
    #habit_logs.drop_indexes()
    def __init__(self, username, habit_name, habit_id, log):
        self.username = username
        self.habit_name = habit_name
        self.habit_id = habit_id
        self.log = log
        self.timestamp = datetime.utcnow()

    def insert_log(self):
        
        log_data = {
                "username": self.username,
                "habit_name": self.habit_name,
                "habit_id": self.habit_id,
                "timestamp": self.timestamp,
                "log": self.log
                }
        try:
            self.habit_logs.insert_one(log_data)
            return {"message": "Log added successfully"}, 201
        except Exception as e:
            return {"message": f"Error adding log: {str(e)}"}
