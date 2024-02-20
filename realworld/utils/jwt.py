import jwt
from datetime import datetime, timedelta
import os

# Define a secret key for signing the JWT token
SECRET_KEY = os.getenv("SECRET_KEY")

# Generate JWT token
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=15)  # Token expiration time
    }
    print("Generating token inside JWT token")
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    print("Token generated successfully", token)
    return token