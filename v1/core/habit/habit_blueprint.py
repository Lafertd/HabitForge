from flask import Blueprint, jsonify, request
from database.data import User, Habit, Habit_Log
from .habit_service import HabitEngine
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Optional
import uuid
import json
import datetime

habit = Blueprint('habit', __name__)

@habit.route("/create", methods=['POST'], strict_slashes=False)
@jwt_required()
def create_habit():
    """ Create a specific habit. """
    username = get_jwt_identity()
    habit_name = request.json.get("habit_name")
    frequency = request.json.get("frequency")
    status = request.json.get("status")
    habit_obj = Habit(username, habit_name, frequency, status)
    habit = Habit.habits.find_one({"username": username, "habit_name": habit_name})
    if not habit:
        habit_obj.create()
        return jsonify({"message": f"{frequency} '{habit_name}' habit created successfully"}), 201
    return jsonify({"message": f"{habit_name} habit already exists"}), 409


@habit.route("/rename", methods=["PUT"], strict_slashes=False)
@jwt_required()
def rename_habit():
    """ Rename a habit. """
    username = get_jwt_identity()
    habit_name = request.json.get("habit_name")
    new_habit_name = request.json.get("new_habit_name")
    if Habit.habits.find_one({"username": username, "habit_name": new_habit_name}):
        return jsonify({"message": f"New Habit name already exists, try another one"}), 409
    else:
        habit = Habit.habits.find_one({"username": username, "habit_name": habit_name})
        if habit:
            habit_obj = Habit(username=username, habit_name=habit_name)
            habit_obj.rename_habit(habit_name, new_habit_name)
            return jsonify({"message": f"Habit renamed to {new_habit_name}"}), 200
        return jsonify({"message": f"Habit not found"}), 404


@habit.route("/delete", methods=['DELETE'], strict_slashes=False)
@jwt_required()
def del_habit():
    """ Delete a specific habit. """
    username = get_jwt_identity()
    habit_name = request.json.get("habit_name")
    habit = Habit.habits.find_one({"username": username, "habit_name": habit_name})
    if not habit:
        return jsonify({"message": "Habit not found"}), 404
    else:
        habit_obj = Habit(username=username, habit_name=habit_name)
        if habit_obj is None:
            return jsonify({"message": "Habit not found"}), 404
        del_habit = habit_obj.delete_habit(habit_name)
        return jsonify({"message": f"{del_habit}"}), 200


@habit.route("/reset", methods=['DELETE'], strict_slashes=False)
@jwt_required()
def reset_habits():
    """Reset all habits to 0 for the authenticated user."""
    username = get_jwt_identity()
    result = Habit.habits.delete_many({"username": username})
    
    if result.deleted_count > 0:
        return jsonify({"message": f"All habits for user '{username}' have been reset successfully."}), 200
    return jsonify({"message": f"No habits found for user '{username}'. No habits were reset."}), 404


@habit.route("/all", methods=['GET'], strict_slashes=False)
@jwt_required()
def list_habits():
    """ List all habits associated with the authenticated user. """
    username = get_jwt_identity()
    all_habits = []
    for habit in Habit.find({"username": username}):
        if isinstance(habit, dict):  # Ensure habit is a dictionary
            # Exclude fields (_id, habit_id, start_date)
            filter_habit = {}
            for key, value in habit.items():
                if key not in ['_id', 'habit_id', 'start_date']:
                    filter_habit[key] = value
            all_habits.append(str(filter_habit))  # Add the filtered habit to the list

    if all_habits == []:
            return jsonify({"message": "you have no habits yet"}), 404
    return jsonify({"message": all_habits}), 200


@habit.route("/details", methods=["GET"], strict_slashes=False)
@jwt_required()
def habit_details():
    """ Get detailed information about a specific habit. """
    username = get_jwt_identity()
    habit_name = request.json.get("habit_name")
    details = Habit.habits.find_one({"username": username, "habit_name": habit_name})
    filtered_habit = []
    filtered_attr = {}
    if details:
        for key, value in details.items():
            if key not in ['_id', 'habit_id', 'start_date']:
                filtered_attr[key] = value
        filtered_habit.append(filtered_attr)
        return jsonify({"message": filtered_habit}), 200
    else:
        return jsonify({"message": "Habit not found"}), 404


@habit.route("/status", methods=["GET", "PUT"], strict_slashes=False)
@jwt_required()
def habit_status():
    """ Log progress or completion for a specific habit. """

    username = get_jwt_identity()
    habit_name = request.json.get("habit_name")
    habit = Habit.habits.find_one({"username": username, "habit_name": habit_name})

    if not habit:
        return jsonify({"message": "Habit not found"}), 404
    elif request.method == "GET":
        habit_obj = Habit(username=username, habit_name=habit_name)
        status = habit_obj.get_status(habit_name)
        return jsonify({"message": status}), 200
    elif request.method == "PUT":
        status = request.json.get("status")
        habit_obj = Habit(username=username, habit_name=habit_name)
        result = habit_obj.put_status(habit_name, status)
        return jsonify({"message": result}), 200


@habit.route("/frequency", methods=["GET", "PUT"], strict_slashes=False)
@jwt_required()
def habit_frequency():
    """ Get the frequency of a specific habit. """

    username = get_jwt_identity()
    new_frequency = request.json.get("new_frequency")
    habit_name = request.json.get("habit_name")
    habit = Habit.habits.find_one({"username": username, "habit_name": habit_name})
    if habit:
        habit_obj = Habit(username=username, habit_name=habit_name)
        frequency = habit_obj.habit_frequency(habit_name)
        
        if request.method == "GET":
            return jsonify({"frequency": frequency}), 200
        elif request.method == "PUT":
            if frequency in ['daily', 'weekly', 'monthly']:
                return jsonify({"message": "Frequency updates are not allowed. Logs must maintain consistency for 'daily', 'weekly', or 'monthly' tracking."}), 403
            else:
                Habit.habits.update_one(
                        {"habit_id": habit["habit_id"]},
                        {"$set": {"frequency": new_frequency}}
                        )
                return jsonify({"message": f"{new_frequency} frequency submitted successfully"}), 201
    else:
        return jsonify({"message": "Habit not found"}), 404



@habit.route("/log", methods=['POST', 'GET'], strict_slashes=False)
@jwt_required()
def habit_log():
    habit_name = request.json.get("habit_name") # This should be included in the request body
    username = get_jwt_identity()

    # Fetch the habit from the MongoDB database
    habit = Habit.habits.find_one({"username": username, "habit_name": habit_name})

    if not habit:
        return jsonify({"message": "Habit not found"}), 404  # Return 404 if habit doesn't exist

    habit_id = habit.get("habit_id")

    if request.method == 'POST':
        log = request.json.get("log")  # This should be included in the request body
        if not log:
            return jsonify({"message": "Log content cannot be empty"}), 400  # Validate log content

        # Using HabitEngine to post the log
        engine = HabitEngine()
        try:
            post_result = engine.post_log(username=username, habit_name=habit_name, habit_id=habit_id, log=log)  # Pass [username, habit_name, habit_id, log]
            return post_result
        except Exception as e:
            return {"message": f"Error posting log: {str(e)}"}, 500

    elif request.method == 'GET':
        # Fetch log history for the given habit_id
        logs = HabitEngine().log_history(habit_id=str(habit_id))
        # Process each log item
        
        list_logs = []
        for log in logs:
            formatted_log = {}
            for k, v in log.items():
                if k == "_id":
                    formatted_log[k] = str(v)  # Convert _id to string
                elif k == "timestamp":
                    formatted_log[k] = v.isoformat()  # Convert timestamp to ISO format
                else:
                    formatted_log[k] = v  # Add other values as they are
            list_logs.append(formatted_log) # Append formatted log to the list isinstance(list_logs, list):  # Ensure logs are returned in the correct format (list of dicts)
        if isinstance(list_logs, list):
            if list_logs == []:
                return {"message": "No logs found"}, 404
            return jsonify(list_logs), 200
        else:
            return jsonify({"message": f"{logs} is not in the correct format"}), 500


@habit.route("/streak", methods=['GET'], strict_slashes=False)
@jwt_required()
def get_streak():

    habit_name = request.json.get("habit_name") # This should be included in the request body
    username = get_jwt_identity()

    # Fetch the habit from the MongoDB database
    habit = Habit.habits.find_one({"username": username, "habit_name": habit_name})
    if habit:
        habit_id = habit.get('habit_id')
        engine = HabitEngine()
        get_streak = engine.streak(habit_id=habit_id)
        return get_streak
    else:
        return jsonify({"message": "habit not found"}), 404


@habit.route("/statistics", methods=['GET'], endpoint="statistics", strict_slashes=False)
@habit.route("/stats", methods=['GET'], endpoint="stats", strict_slashes=False)
@jwt_required()
def get_statistics():


    habit_name = request.json.get("habit_name") # This should be included in the request body
    username = get_jwt_identity()
    # Fetch the habit from the MongoDB database
    if not Habit.habits.find_one({"username": username, "habit_name": habit_name}):
        return jsonify({"message": "habit not found"}), 404
    else:
        habit = Habit.habits.find_one({"username": username, "habit_name": habit_name})
        habit_id = habit.get('habit_id')
        engine = HabitEngine()
        stats = engine.statistics(habit_id=habit_id)
        return stats
