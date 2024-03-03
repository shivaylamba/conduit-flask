from flask import Blueprint, request, jsonify, g
from extensions import couchbase_db
from models.users import User
from utils.jwt import generate_token
from utils.auth import authenticate
from validation.auth import RegisterRequest, RegisterResponse, LoginRequest, ErrorResponse, CurrentResponse
from utils.handle_errors import with_error_handling
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

    # Check if the current request endpoint is in the list of routes that require authentication
    if request.endpoint in auth_required_routes:
        response = authenticate()
        if response:
            return response  # Return error response if authentication fails



@users_blueprint.route("/", methods=["POST"])
@with_error_handling()
def create_user() :
    data = RegisterRequest(**request.json)
    existing_user = User.get_by_username(data.username)
    existing_user_email = User.get_by_email(data.email)

    if existing_user:
        return jsonify(ErrorResponse(**{"error": "Username already exists"}).model_dump()), 400
    elif existing_user_email:
        return jsonify(ErrorResponse(**{"error": "Email already exists"}).model_dump()), 400


    user_id = str(uuid.uuid4())
    user = User(user_id, data.username, data.email, data.password)
    user.save()

    token = generate_token(user_id)
    register_response = RegisterResponse( **{
        "user": {
            "username": user.username, 
            "email": user.email, 
            "token": token
            }
        }
    )
    # Return the JSON response using jsonify
    return jsonify(register_response.model_dump()), 201

@users_blueprint.route("/login", methods=["POST"], )
@with_error_handling()
def login_user() :
    data = LoginRequest(**request.json)
    user = User.get_by_email(data.email)
    if not user:
        return jsonify(ErrorResponse(**{"error": "email or password is incorrect"}).model_dump()), 400

    if bcrypt.checkpw(data.password.encode('utf-8'), user.password.encode('utf-8')):
        # Passwords match, generate JWT token and return it
        token = generate_token(user.user_id)
        login_response = RegisterResponse( **{
            "user": {
                "username": user.username, 
                "email": user.email, 
                "token": token
            }
        }
    )
        return jsonify(login_response.model_dump()), 200
    else:
        # Passwords don't match
        return jsonify(ErrorResponse(**{"error": "Invalid password"}).model_dump()), 401


@users_blueprint.route("/get-current-user", methods=["GET"])
@with_error_handling()
def get_current_user():
    user = g.current_user
    if user:
        return jsonify(
            CurrentResponse( **{
                "user": {
                    "user_id" : user.user_id, 
                    "username": user.username, 
                    "email": user.email
                }
            }).model_dump()
        ), 200
    else:
        return jsonify(ErrorResponse(**{"error": "Not logged in"}).model_dump()), 401

def get_all_users() :
    return {
        "users": []
    }