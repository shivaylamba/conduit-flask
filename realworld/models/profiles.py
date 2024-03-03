from datetime import datetime

class Profiles:
    def __init__(self,id: str, following_username : str, followed_username: str, created_at: datetime, updated_at: datetime):
        self.id = id
        self.following_username = following_username
        self.followed_username = followed_username
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            "id": self.id,
            "following_username": self.following_username,
            "followed_username": self.followed_username,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }