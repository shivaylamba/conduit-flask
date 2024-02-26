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
        author=author  # Set author here based on authentication
    )
    couchbase_db.insert_document("articles", article_id, article.to_dict())

    return jsonify({"article": article.to_dict()}), 201


@articles_blueprint.route("/", methods=["GET"])
def get_articles():
    # Get query parameters for pagination
    skip = int(request.args.get("skip", 0))
    limit = int(request.args.get("limit", 10))  # Default limit to 10 if not provided
    author_query = request.args.get("author")
    print("Query parameters author", author_query)

    favorited_query = request.args.get("favorited")
    print("Query parameters favroite", favorited_query)
    tag_query = request.args.get("tag")

    print("Query parameters", tag_query)

    article = []

    # Fetch articles based on skip and limit
    if author_query:
        articles = couchbase_db.query(f"""SELECT *
            FROM articles
            WHERE author.username = "{author_query}"
            LIMIT {limit} OFFSET {skip}
        """)
    elif favorited_query:
        articles = couchbase_db.query(f"""SELECT *
            FROM articles
            WHERE ARRAY_CONTAINS(favorited, "{favorited_query}");
            LIMIT {limit} OFFSET {skip}
        """)
    elif tag_query:
        articles = couchbase_db.query(f"""SELECT *
            FROM articles
            WHERE ARRAY_CONTAINS(tag_list, "{tag_query}");
            LIMIT {limit} OFFSET {skip}
        """)
    else:
        articles = couchbase_db.query(f'SELECT * FROM `articles` LIMIT {limit} OFFSET {skip}')

    articles_data = []

    for row in articles.rows():
        article = row['articles']
        articles_data.append(article)

    # Return articles as JSON response
    return jsonify({"articles": articles_data}), 200

@articles_blueprint.route("/articles", methods=["PUT"])
def update_article():
    # Get request data of 
    data = request.json
    # TODO : Request Validation
    user = g.current_user
    article_id = data['article_id']
    fields = data["fields"]

    try:
        update_values = []

        for field, value in fields.items():
            # Escape single quotes in the value to prevent SQL injection
            value = str(value).replace("'", "''")
            update_values.append(f"{field} = '{value}'")

        update_query = f"UPDATE articles SET {', '.join(update_values)} WHERE article_id = '{article_id}' AND author.username = '{user.id}';"

        couchbase_db.query(update_query)
        
    except Exception as e:
        return jsonify({"message": "Unable to update article"}), 500


@articles_blueprint.route("/favorite", methods=["POST"])
def favorite_article():
    # Get request data of 
    data = request.json
    # TODO : Request Validation
    user = g.current_user
    article_id = data['article_id']

    try:
        couchbase_db.query(f"""
            UPDATE articles
            SET favorite = ARRAY_APPEND(IFNULL(favorited, []), {user.user_id})
            WHERE article_id = {article_id};
        """)
    except Exception as e:
        return jsonify({"message": "Unable to favorite article"}), 500

    # Return articles as JSON response
    return jsonify({"message": "article favorited"}), 200

@articles_blueprint.route("/", methods=["POST"])
def delete_articles():
    # Get request data of 
    data = request.json
    # TODO : Request Validation
    user = g.current_user
    article_id = data['article_id']

    # validating that

    try:
        couchbase_db.query(f"""
            DELETE FROM articles
            WHERE article_id = {article_id}
            AND author.username = {user.username};
        """)

    except Exception as e:
        return jsonify({"message": "article with id has been deleted sucessfully"}), 500

    # Return articles as JSON response
    return jsonify({"message": "article with id has been deleted sucessfully"}), 200


@articles_blueprint.route("/<slug>", methods=["GET"])
def get_article_by_slug(slug):
    # Query the database to fetch the article based on the slug
    print(slug)
    try:
        article = couchbase_db.query(f"""
            SELECT *
            FROM articles
            WHERE slug = '{slug}';
        """)
        print(article)

        for row in article.rows():
            article = row['articles']
            return jsonify({"article": article}), 200
        # article = article.rows()[0]['articles']
        
        # If article is found, return it as JSON response
        if article:
            return jsonify({"article": article}), 200
        else:
            return jsonify({"error": "Article not found"}), 404
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500
