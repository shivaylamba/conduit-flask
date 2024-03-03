from flask import Blueprint, request, jsonify, g
from models.profiles import Profiles
from utils.auth import authenticate
from extensions import couchbase_db
import uuid
from datetime import datetime
from validation.profiles import FollowUnfollowRequest, FollowUnfollowResponse
from validation.common import ErrorResponse
from utils.handle_errors import with_error_handling

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
@with_error_handling()
def follow_unfollow():
    data = FollowUnfollowRequest(**request.json)
    # TODO : Request Validation
    current_user = g.current_user
    profile_id = str(uuid.uuid4())
    action = data.action

    if action != "FOLLOW" and action != "UNFOLLOW":
        return jsonify(ErrorResponse(**{"error": "action doesn't exist"}).model_dump()), 400

    followed_username = data.followed_username

    query = f"SELECT * FROM users WHERE username = '{followed_username}'"

    user_data = couchbase_db.query(query)

    user = None
    for row in user_data.rows():
        usr = row["users"]
        user = usr
        break

    if user == None:
        return jsonify(ErrorResponse(**{"error": "followed user doesn't exist"}).model_dump()), 400   
    elif current_user.username == user['username']:
        return jsonify(ErrorResponse(**{"error": "following and followed user cannot be same"}).model_dump()), 400
    

    if action == "FOLLOW":
        # check if the entry already exists in the database if yes throw the error
        query = f"SELECT * FROM profiles where following_username = '{current_user.username}' and followed_username = '{followed_username}'"
        profile_data = couchbase_db.query(query)
        profile = None

        for row in profile_data.rows():
            profile = row["profiles"]
            break
        profile_data_to_insert = Profiles (
            id = profile_id,
            following_username= current_user.username,
            followed_username= followed_username,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        if profile is None:
            couchbase_db.insert_document("profiles",profile_id, profile_data_to_insert.to_dict())
            return jsonify(FollowUnfollowResponse(**{"message": "profile followed succesfully!"}).model_dump()), 200
        else:
            return jsonify(ErrorResponse(**{"error": "already following the user"}).model_dump()), 400
    else:
        query = f"SELECT * FROM profiles where following_username = '{current_user.username}' and followed_username = '{followed_username}'"

        profile_data = couchbase_db.query(query)
        profile = None

        for row in profile_data.rows():
            profile = row["profiles"]
            break
        
        if profile:
            couchbase_db.delete_document("profiles", profile['id'])
            return jsonify(FollowUnfollowResponse(**{"message": "profile unfollowed succesfully!"}).model_dump()), 200

        else:
            return jsonify(ErrorResponse(**{"error": "already not following the profile"}).model_dump()), 400