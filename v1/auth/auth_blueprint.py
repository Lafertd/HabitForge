# src/auth/auth_blueprint.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token
from werkzeug.security import check_password_hash
import redis
from models.database import User, Habit
from typing import Optional

# Create the blueprint for authentication
auth = Blueprint('auth', __name__)

@auth.route("/register", methods=["POST"])
def signup() -> jsonify:
    """
    Handles user registration, creates a new user, and returns a success message.

    This function performs the following:
    1. Retrieves the username and password from the request.
    2. Checks if the username is already taken.
    3. If the username is available, creates a new user and saves it to the database.

    Returns:
        jsonify: A JSON response indicating whether the account was created successfully.
    """
    username: Optional[str] = request.json.get("username", None)
    password: Optional[str] = request.json.get("password", None)

    if not username:
        return jsonify({"msg": "username is required"}), 400
    if not password:
        return jsonify({"msg": "password is required"}), 400

    # Check if the username is already taken
    if User.find_user_by_username(username):
        return jsonify({"msg": "username already used, try another one"}), 409

    # Create and save new user
    new_user = User(username, password)
    new_user.save()

    return jsonify({"msg": "account created successfully"}), 201


@auth.route("/login", methods=["POST"])
def login() -> jsonify:
    """
    Authenticates a user and returns a JWT token if the username and password are correct.

    This function:
    1. Retrieves the username and password from the request.
    2. Verifies the user's credentials.
    3. If successful, creates and returns a JWT access token.

    Returns:
        jsonify: A JSON response with either an error message or the access token.
    """
    username: Optional[str] = request.json.get("username", None)
    password: Optional[str] = request.json.get("password", None)

    # Retrieve user from the database
    user = User.find_user_by_username(username)

    # Check if user exists
    if not user:
        return jsonify({"msg": "user not found"}), 404

    # Check if the password is correct
    hashed_pwd = user["password"]
    if not check_password_hash(hashed_pwd, password):
        return jsonify({"msg": "Bad username or password"}), 401

    # Create JWT access token
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


@auth.route("/protected", methods=["GET"])
@jwt_required()
def protected() -> jsonify:
    """
    A protected route that requires a valid JWT to access.

    This function retrieves the identity of the currently logged-in user
    and returns it in the response.

    Returns:
        jsonify: A JSON response containing the logged-in user’s identity.
    """
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@auth.route("/logout", methods=["POST"])
@jwt_required()
def logout() -> jsonify:
    """
    Logs the user out by blacklisting the JWT token.

    This function:
    1. Retrieves the 'jti' (JWT ID) from the current token's payload.
    2. Stores the 'jti' in Redis to invalidate the token.
    3. Responds with a success message.

    Returns:
        jsonify: A JSON response indicating successful logout.
    """
    jti = get_jwt()["jti"]
    
    # Initialize Redis connection
    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    # Blacklist the JWT by storing its 'jti' in Redis with an expiration time of 1 hour (3600 seconds)
    r.setex(jti, 3600, "invalid")

    return jsonify(msg="Successfully logged out"), 200
