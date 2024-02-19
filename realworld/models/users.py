import bcrypt
import os
from extensions import couchbase_db

class User:
    def __init__(self, user_id, username, email, password):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password

    def to_json(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "password": self.password
        }

    def save(self):
        hashed_password = bcrypt.hashpw(self.password.encode('utf-8'), bcrypt.gensalt())
        self.password = hashed_password.decode('utf-8')  # Ensure it's stored as a string
        couchbase_db.upsert_document("users", str(self.user_id), self.to_json())
        print("couchbase client: ", couchbase_db)


    @staticmethod
    def get(user_id):
        result = couchbase_db.get_document("users", str(user_id))
        if result:
            user_data = result.content_as[str]()
            return User(
                user_id=user_data["user_id"],
                username=user_data["username"],
                email=user_data["email"],
                password=user_data["password"]
            )
        return None

    def delete(self):
        couchbase_db.delete_document("users", str(self.user_id))
