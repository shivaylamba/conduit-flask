from flask import Blueprint, request, jsonify
from extensions import couchbase_db
from models.users import User
from utils.jwt import generate_token
import bcrypt
import uuid

users_blueprint = Blueprint(
    "users_endpoints",
    __name__,
    url_prefix="/users",
)

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


@users_blueprint.route("/", methods=["GET"])
def get_all_users() :
    return {
        "users": []
    }