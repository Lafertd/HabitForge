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
