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

class Article:
    def __init__(self, slug: str, title: str, description: str, body: str, tag_list: list[str],
                 created_at: datetime, updated_at: datetime, favorited: bool, favorites_count: int,
                 author: Author):
        self.slug = slug
        self.title = title
        self.description = description
        self.body = body
        self.tag_list = tag_list
        self.created_at = created_at
        self.updated_at = updated_at
        self.favorited = favorited
        self.favorites_count = favorites_count
        self.author = author

    def to_dict(self):
        return {
            "slug": self.slug,
            "title": self.title,
            "description": self.description,
            "body": self.body,
            "tag_list": self.tag_list,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "favorited": self.favorited,
            "favorites_count": self.favorites_count,
            "author": self.author.to_dict()
        }
