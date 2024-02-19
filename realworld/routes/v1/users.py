from flask import Blueprint, request, jsonify
from extensions import couchbase_db
from models.users import User
import uuid

users_blueprint = Blueprint(
    "users_endpoints",
    __name__,
    url_prefix="/users",
)

@users_blueprint.route("/", methods=["POST"])
def create_user() :
    data = request.json
    # TODO : Request Validation
    user_id = str(uuid.uuid4())
    user = User(user_id, data["username"], data["email"], data["password"])
    user.save()
    return jsonify({"user": user.to_json()}), 201

@users_blueprint.route("/", methods=["GET"])
def get_all_users() :
    return {
        "users": []
    }