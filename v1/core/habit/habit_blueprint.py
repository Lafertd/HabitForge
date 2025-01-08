from flask import Blueprint, jsonify, request
from database.data import User, Habit, Habit_Log
from .habit_service import HabitEngine
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Optional
import uuid
import json

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
