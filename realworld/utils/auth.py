from flask import g, request, jsonify
from models.users import User
import jwt
import os


# Middleware to handle authentication
def authenticate():
    # Extract the JWT token from the request headers
    SECRET_KEY = os.getenv("SECRET_KEY")
    token = request.headers.get('Authorization')
    print("####2 Authentication", token)
    if token:
        try:
            # Decode the JWT token
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            # Extract the user_id from the payload
            user_id = payload.get('user_id')
            # You can fetch the user object from the database using user_id and store it in g
            g.current_user = User.get_user_by_id(user_id)  # Assuming User.get() fetches user from DB
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
    else:
        # No token provided in the request headers
        return jsonify({"error": "Authorization token required"}), 401
