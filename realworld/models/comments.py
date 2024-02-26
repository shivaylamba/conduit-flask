from datetime import datetime

class Author:
    def __init__(self, username: str, bio: str, image: str, following: bool):
        self.username = username
        self.bio = bio
        self.image = image
        self.following = following

    def to_dict(self):
        return {
            "username": self.username,
            "bio": self.bio,
            "image": self.image,
            "following": self.following
        }

class Comment:
    def __init__(self, comment_id: int, article_id: int, body: str, created_at: datetime, author: Author):
        self.comment_id = comment_id
        self.article_id = article_id
        self.body = body
        self.created_at = created_at
        self.author = author

    def to_dict(self):
        return {
            "comment_id": self.comment_id,
            "article_id": self.article_id,
            "body": self.body,
            "created_at": self.created_at.isoformat(),
            "author": self.author.to_dict()
        }