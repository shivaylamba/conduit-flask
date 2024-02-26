from flask import Blueprint, request, jsonify, g
from models.comments import Author, Comment
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

comments_blueprint = Blueprint(
    "comments_endpoints",
    __name__,
    url_prefix="/comments",
)


@comments_blueprint.before_request
def apply_authentication_middleware():
    # List of routes that require authentication
    auth_required_routes = ["comments_endpoints.create_comment", "comments_endpoints.get_comments", "comments_endpoints.delete_comment"]
    print("-----Request Endpoint-------", request.endpoint)

    # Check if the current request endpoint is in the list of routes that require authentication
    if request.endpoint in auth_required_routes:
        response = authenticate()
        if response:
            return response  # Return error response if authentication fails
        

@comments_blueprint.route("/", methods=["POST"])
def create_comment():
    data = request.json
    # TODO : Request Validation
    user = g.current_user
    comment_id = str(uuid.uuid4())
    author = Author (
        following=False,
        bio="",
        image="",
        username=user.username
    )
    try:
            article = couchbase_db.get_document("articles", data["article_id"])

            comment = Comment(
                comment_id=comment_id,
                article_id=data["article_id"],
                body=data["body"],
                created_at=datetime.utcnow(),
                author=author  # Set author here based on authentication
            )

            couchbase_db.insert_document("comments", comment_id, comment.to_dict())

            return jsonify({"comment": comment.to_dict()}), 201
    
    except DocumentNotFoundException:
            return jsonify({"message": "Article not found"}), 404
    
    except CouchbaseException as e:
            return jsonify({"message": "internal server error"}), 500


@comments_blueprint.route("/<article_id>", methods=["GET"])
def get_comments(article_id):
    # Get optional query parameters
    skip = request.args.get("skip", default=0, type=int)
    limit = request.args.get("limit", default=10, type=int)

    try:
        comments = couchbase_db.query(f"""SELECT *
            FROM comments
            WHERE article_id = "{article_id}"
            LIMIT {limit} OFFSET {skip}
        """)
        print(comments)
        comments_data = []

        for row in comments.rows():
            comment = row['comments']
            comments_data.append(comment)

        # Convert comments to JSON format
        # Return comments as JSON response
        return jsonify({"comments": comments_data}), 200

    except Exception as e:
        # Handle exceptions
        return jsonify({"error": "Internal Server Error"}), 500


@comments_blueprint.route("/<comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    try:
        print("comment id", comment_id)
        comment_document = couchbase_db.get_document("comments", comment_id)
        print ('comment_document', comment_document)
        print("comment info", comment.value)
        comment = comment.value
        print("before user info", comment)

        user = g.current_user
        print("user info", user)

        print("user author", user.username)
        print("comment author", comment.author)


        if comment.author.username != user.username:
             return jsonify({"error": "You don't have permission to delete this comment"}), 403
        
        print("comment info", comment.value)


        couchbase_db.delete_document("comments", comment_id)

        return jsonify({"message": "Comment deleted successfully"}), 200
    
    except DocumentNotFoundException:
            return jsonify({"message": "Comment not found"}), 404
    
    except Exception as e:
        # Handle exceptions
        return jsonify({"error": "Internal Server Error"}), 500
