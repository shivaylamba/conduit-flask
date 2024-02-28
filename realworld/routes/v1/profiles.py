from flask import Blueprint, request, jsonify, g
from models.profiles import Profiles
from utils.auth import authenticate
from extensions import couchbase_db
import uuid
from utils.slug import create_slug
from datetime import datetime
from couchbase.exceptions import (
    CouchbaseException,
    DocumentExistsException,
    DocumentNotFoundException,
)

profiles_blueprint = Blueprint(
    "profiles_endpoints",
    __name__,
    url_prefix="/profiles",
)

@profiles_blueprint.before_request
def apply_authentication_middleware():
        response = authenticate()
        if response:
            return response  # Return error response if authentication fails

@profiles_blueprint.route("/", methods=["POST"])
def follow_unfollow():
    data = request.json
    # TODO : Request Validation
    current_user = g.current_user
    profile_id = str(uuid.uuid4())
    action = data["action"]

    if action != "FOLLOW" and action != "UNFOLLOW":
        return jsonify({"error": "action doesn't exist"}), 400

    followed_username = data["followed_username"]

    user_data = couchbase_db.query("""SELECT * FROM users WHERE username = {followed_username}""")
    user = None
    for row in user_data.rows():
        usr = row["users"]
        user = usr
        break
        
    if user == None:
        return jsonify({"error": "followed user doesn't exist"}), 400   
    elif current_user.username == user.username:
        return jsonify({"error": "following and followed user cannot be same"}), 400
    

    if action == "FOLLOW":
        # check if the entry already exists in the database if yes throw the error
        profile_data = couchbase_db.query("""SELECT * FROM profiles where following_username = {current_user.username} and followed_username = {following_username}""")
        profile = None

        for row in profile_data.rows():
            profile = row["profiles"]
            break
        profile_data_to_insert = Profiles (
            id = profile_id,
            following_username= current_user.username,
            followed_username= followed_username,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        if profile == None:
            couchbase_db.insert("profiles",profile_id, profile_data_to_insert.to_dict())
            return jsonify({"message": "profile followed succesfully!"}), 200
        else:
            return jsonify({"error": "following and followed user cannot be same"}), 400
    else:
        profile_data = couchbase_db.query("""SELECT * FROM profiles where following_username = {current_user.username} and followed_username = {following_username}""")
        profile = None

        for row in profile_data.rows():
            profile = row["profiles"]
            break
        
        if profile!= None:
            couchbase_db.delete("profiles",profile_id)
            return jsonify({"message": "profile unfollowed succesfully!"}), 200
        else:
            return jsonify({"error": "already following the profile"}), 400