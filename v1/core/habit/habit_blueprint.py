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
        return jsonify({"message": f"{frequency} '{habit_name}' habit created successfully"})
    return jsonify({"message": f"{habit_name} habit already exists"})


@habit.route("/rename", methods=["PUT"], strict_slashes=False)
@jwt_required()
def rename_habit():
    """ Rename a habit. """
    username = get_jwt_identity()
    habit_name = request.json.get("habit_name")
    new_habit_name = request.json.get("new_habit_name")
    habit = Habit.habits.find_one({"username": username, "habit_name": habit_name})
    if habit:
        habit_obj = Habit(username=username, habit_name=habit_name)
        habit_obj.rename_habit(habit_name, new_habit_name)
        return jsonify({"message": f"Habit renamed to {new_habit_name}"})
    return jsonify({"message": f"Habit not found"})


@habit.route("/delete", methods=['DELETE'], strict_slashes=False)
@jwt_required()
def del_habit():
    """ Delete a specific habit. """
    username = get_jwt_identity()
    habit_name = request.json.get("habit_name")
    habit = Habit.habits.find_one({"username": username, "habit_name": habit_name})
    if habit is None:
        return jsonify({"message": "Habit not found"}), 404
    else:
        habit_obj = Habit(username=username, habit_name=habit_name)
        if habit_obj is None:
            return jsonify({"message": "Habit not found"}), 404
        del_habit = habit_obj.delete_habit(habit_name)
        return jsonify({"message": f"{del_habit}"})


@habit.route("/reset", methods=['DELETE'], strict_slashes=False)
@jwt_required()
def reset_habits():
    """ Reset all habits to 0. """
    username = get_jwt_identity()
    habit = Habit.habits.find({"username": username})
    if habit:
        habit_obj = Habit(username=username)
        reset_habits = habit_obj.reset()
        return jsonify({"message": reset_habits})
    return jsonify({"message": "Habit not found"}), 404


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
    return jsonify({"message": all_habits}), 201


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
        return jsonify({"message": filtered_habit}), 201
    else:
        return jsonify({"message": "Habit not found"}), 404


@habit.route("/status", methods=["GET", "PUT"], strict_slashes=False)
@jwt_required()
def habit_status():
    """ Log progress or completion for a specific habit. """

    username = get_jwt_identity()
    habit_name = request.json.get("habit_name")
    habit = Habit.habits.find_one({"username": username, "habit_name": habit_name})

    if request.method == "GET":
        habit_obj = Habit(username=username, habit_name=habit_name)
        status = habit_obj.get_status(habit_name)
        return jsonify({"message": status})

    elif request.method == "PUT":
        status = request.json.get("status")
        habit_obj = Habit(username=username, habit_name=habit_name)
        result = habit_obj.put_status(habit_name, status)
        return jsonify({"message": result})


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
        if request.method == "GET":
            frequency = habit_obj.habit_frequency(habit_name)
            return jsonify({"frequency": frequency})
        elif request.method == "PUT":
            Habit.habits.update_one(
                    {"habit_id": habit["habit_id"]},
                    {"$set": {"frequency": new_frequency}}
                )
            return jsonify({"message": f"{new_frequency} frequency submitted successfully"}), 201
    else:
        return jsonify({"message": "Habit not found"}), 404
