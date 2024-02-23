from flask import Blueprint, request, jsonify, g
from models.articles import Article, Author
from utils.auth import authenticate
from extensions import couchbase_db
import uuid
from utils.slug import create_slug
from datetime import datetime


articles_blueprint = Blueprint(
    "articles_endpoints",
    __name__,
    url_prefix="/articles",
)

@articles_blueprint.before_request
def apply_authentication_middleware():
    # List of routes that require authentication
    auth_required_routes = ["articles_endpoints.create_article"]
    print("-----Request Endpoint-------", request.endpoint)

    # Check if the current request endpoint is in the list of routes that require authentication
    if request.endpoint in auth_required_routes:
        response = authenticate()
        if response:
            return response  # Return error response if authentication fails

@articles_blueprint.route("/", methods=["POST"])
def create_article():
    data = request.json
    # TODO : Request Validation
    user = g.current_user
    article_id = str(uuid.uuid4())
    author = Author (
        following=False,
        bio="",
        image="",
        username=user.username
    )
    article = Article(
        slug=create_slug(data["title"]),
        title=data["title"],
        description=data["description"],
        body=data["body"],
        tag_list=data["tagList"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        favorited=False,
        favorites_count=0,
        author=author  # Set author here based on authentication
    )
    couchbase_db.insert_document("articles", article_id, article.to_dict())

    return jsonify({"article": article.to_dict()}), 201


@articles_blueprint.route("/", methods=["GET"])
def get_articles():
    # Get query parameters for pagination
    skip = int(request.args.get("skip", 0))
    limit = int(request.args.get("limit", 10))  # Default limit to 10 if not provided

    # Fetch articles based on skip and limit
    print("---Hiting Query for articles---")
    articles = couchbase_db.query(f'SELECT * FROM `articles` LIMIT {limit} OFFSET {skip}')
    print ('---all articles--', articles)

    articles_data = []

    for row in articles.rows():
        article = row['articles']
        articles_data.append(article)

    # Return articles as JSON response
    return jsonify({"articles": articles_data}), 200