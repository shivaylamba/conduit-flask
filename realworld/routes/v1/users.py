from flask import Blueprint, request, jsonify, g
from extensions import couchbase_db
from models.users import User
from utils.jwt import generate_token
from utils.auth import authenticate
import bcrypt
import uuid

users_blueprint = Blueprint(
    "users_endpoints",
    __name__,
    url_prefix="/users",
)

@users_blueprint.before_request
def apply_authentication_middleware():
    # List of routes that require authentication
    auth_required_routes = ["users_endpoints.get_current_user"]
    print("-----Request Endpoint-------", request.endpoint)

    # Check if the current request endpoint is in the list of routes that require authentication
    if request.endpoint in auth_required_routes:
        response = authenticate()
        if response:
            return response  # Return error response if authentication fails



@users_blueprint.route("/", methods=["POST"])
def create_user() :
    print("------Creating user------")
    data = request.json
    # TODO: Request Validation

    # Check if the username already exists
    existing_user = User.get_by_username(data["username"])
    existing_user_email = User.get_by_email(data["email"])

    if existing_user:
        return jsonify({"error": "Username already exists"}), 400
    elif existing_user_email:
        return jsonify({"error": "Email already exists"}), 400


    user_id = str(uuid.uuid4())
    user = User(user_id, data["username"], data["email"], data["password"])
    user.save()

    token = generate_token(user_id)
    return jsonify({"user": {"username": user.username, "email": user.email, "token": token}}), 201

@users_blueprint.route("/login", methods=["POST"])
def login_user() :
    data = request.json
    # TODO: Request Validation

    user = User.get_by_email(data["email"])
    if not user:
        return jsonify({"error": "email or password is incorrect"}), 400

    if bcrypt.checkpw(data["password"].encode('utf-8'), user.password.encode('utf-8')):
        # Passwords match, generate JWT token and return it
        token = generate_token(user.user_id)
        return jsonify({"user": {"username": user.username, "email": user.email, "token": token}}), 200
    else:
        # Passwords don't match
        return jsonify({"error": "Invalid password"}), 401


@users_blueprint.route("/get-current-user", methods=["GET"])
def get_current_user():
    user = g.current_user
    if user:
        return jsonify({"user": {"user_id" : user.user_id, "username": user.username, "email": user.email}}), 200
    else:
        return jsonify({"error": "Not logged in"}), 401

def get_all_users() :
    return {
        "users": []
    }