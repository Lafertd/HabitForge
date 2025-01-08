# src/auth/auth_blueprint.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token
from werkzeug.security import check_password_hash
import redis
from database.data import User, Habit
from typing import Optional, Dict, Tuple, Union

# Create the blueprint for authentication
auth = Blueprint('auth', __name__)

@auth.route("/register", methods=["POST"])
def signup() -> Tuple[Dict[str, str], int]:
    """
    Handles user registration, creates a new user, and returns a success message.
    """
    username: Optional[str] = request.json.get("username", None)
    password: Optional[str] = request.json.get("password", None)

    if not username:
        return jsonify({"msg": "username is required"}), 400
    if not password:
        return jsonify({"msg": "password is required"}), 400

    if User.find_user_by_username(username):
        return jsonify({"msg": "username already used, try another one"}), 409

    new_user = User(username, password)
    new_user.save()

    return jsonify({"msg": "account created successfully"}), 201


@auth.route("/login", methods=["POST"])
def login() -> Tuple[Dict[str, Union[str, str]], int]:
    """
    Authenticates a user and returns a JWT token if the username and password are correct.
    """
    username: Optional[str] = request.json.get("username", None)
    password: Optional[str] = request.json.get("password", None)

    user = User.find_user_by_username(username)

    if not user:
        return jsonify({"msg": "user not found"}), 404

    hashed_pwd = user["password"]
    if not check_password_hash(hashed_pwd, password):
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


@auth.route("/protected", methods=["GET"])
@jwt_required()
def protected() -> Tuple[Dict[str, str], int]:
    """
    A protected route that requires a valid JWT to access.
    """
    current_user: str = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@auth.route("/logout", methods=["POST"])
@jwt_required()
def logout() -> Dict[str, str]:
    """
    Logs the user out by blacklisting the JWT token.
    """
    jti = get_jwt()["jti"]

    r = redis.StrictRedis(host="redis-12255.c10.us-east-1-4.ec2.cloud.redislabs.com", port=12255, password = "1rPEIkNriUNIT8PyUpy6C4rQCId3evGb", db =0)
    r.setex(jti, 3600, "invalid")

    return jsonify(msg="Successfully logged out"), 200
