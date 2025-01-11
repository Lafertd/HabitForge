from pymongo import MongoClient
from flask import Flask
from flask_jwt_extended import JWTManager
import redis
from urllib.parse import urlparse
from flask_sse import sse
import os
from dotenv import load_dotenv


def create_app():
    app = Flask(__name__)

    load_dotenv()

    # JWT Configuration
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")


    # Redis Configuration (using environment variable, no fallback)
    redis_url = os.getenv('REDIS_URL')  # Must be set in production environment
    if not redis_url:
        raise ValueError("REDIS_URL must be Configured")
    parsed_redis = urlparse(redis_url)

    # Configure Redis connection
    redis_client = redis.Redis(
            host=parsed_redis.hostname,
            port=parsed_redis.port,
            username=parsed_redis.username,
            password=parsed_redis.password,
            decode_responses=True
            )
    # Initialize JWT
    jwt = JWTManager(app)

    # Register SSE extension
    app.register_blueprint(sse, url_prefix='/stream')

    # MongoDB Configuration (using environment variable for production)
    mongo_uri = os.getenv('MONGODB_URI')  # Must be set in production environment
    if not mongo_uri:
        raise ValueError("MONGODB_URI must be Configured")
    client = MongoClient(mongo_uri)
    db_name = 'habitforge'  # Use your production database name
    db = client[db_name]
    app.config['MONGO_DB'] = db

    # Register blueprints
    from v1.auth import register_auth_blueprint
    register_auth_blueprint(app)
    from v1.core.habit import register_habit_blueprint
    register_habit_blueprint(app)
    
    # Token blacklisting check
    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload):
        return redis_client.get(jwt_payload["jti"]) is not None

    return app

app = create_app()

