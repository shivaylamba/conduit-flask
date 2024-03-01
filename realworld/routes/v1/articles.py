from flask import Blueprint, request, jsonify, g
from models.articles import Article, Author
from utils.auth import authenticate
from extensions import couchbase_db
import uuid
from utils.slug import create_slug
from datetime import datetime
from validation.articles import CreateArticleRequest, CreateArticleResponse, GetArticleResponse, UpdateArticleRequest, UpdateArticleResponse, DeleteArticleResponse, FavoriteArticleRequest, FavoriteArticleResponse, DeleteArticleRequest, GetTagsResponse, GetArticlesResponse
from validation.common import ErrorResponse


articles_blueprint = Blueprint(
    "articles_endpoints",
    __name__,
    url_prefix="/articles",
)

@articles_blueprint.before_request
def apply_authentication_middleware():
    # List of routes that require authentication
    auth_required_routes = ["articles_endpoints.create_article","articles_endpoints.get_followed_articles"]
    print("-----Request Endpoint-------", request.endpoint)

    # Check if the current request endpoint is in the list of routes that require authentication
    if request.endpoint in auth_required_routes:
        response = authenticate()
        if response:
            return response  # Return error response if authentication fails

@articles_blueprint.route("/", methods=["POST"])
def create_article():
    data = CreateArticleRequest(**request.json)
    user = g.current_user
    article_id = str(uuid.uuid4())
    author = Author (
        following=False,
        bio="",
        image="",
        username=user.username
    )
    article = Article(
        slug=create_slug(data.title),
        title=data.title,
        description=data.description,
        body=data.body,
        tag_list=data.tagList,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        favorited=False,
        author=author  # Set author here based on authentication
    )
    couchbase_db.insert_document("articles", article_id, article.to_dict())

    return jsonify(CreateArticleResponse(**{"article": article.to_dict()})), 201


@articles_blueprint.route("/", methods=["GET"])
def get_articles():
    # Get query parameters for pagination
    skip = int(request.args.get("skip", 0))
    limit = int(request.args.get("limit", 10))  # Default limit to 10 if not provided
    author_query = request.args.get("author")

    favorited_query = request.args.get("favorited")
    tag_query = request.args.get("tag")

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
    return jsonify(GetArticlesResponse(**{"articles": articles_data})), 200

@articles_blueprint.route("/articles", methods=["PUT"])
def update_article():
    # Get request data of 
    data = UpdateArticleRequest(**request.json)
    user = g.current_user
    article_id = data.article_id
    fields = data.fields

    try:
        update_values = []

        for field, value in fields.items():
            # Escape single quotes in the value to prevent SQL injection
            value = str(value).replace("'", "''")
            update_values.append(f"{field} = '{value}'")

        update_query = f"UPDATE articles SET {', '.join(update_values)} WHERE article_id = '{article_id}' AND author.username = '{user.id}';"

        couchbase_db.query(update_query)

        return jsonify(UpdateArticleResponse(**{"message": "Article update"})), 200
        
    except Exception as e:
        return jsonify(ErrorResponse(**{"message": "Unable to update article"})), 500


@articles_blueprint.route("/favorite", methods=["POST"])
def favorite_article():
    # Get request data of 
    data = FavoriteArticleRequest(**request.json)
    user = g.current_user
    article_id = data.article_id

    try:
        couchbase_db.query(f"""
            UPDATE articles
            SET favorite = ARRAY_APPEND(IFNULL(favorited, []), {user.user_id})
            WHERE article_id = "{article_id}";
        """)
    except Exception as e:
        return jsonify(ErrorResponse(**{"message": "Unable to favorite article"})), 500

    # Return articles as JSON response
    return jsonify(FavoriteArticleResponse(**{"message": "article favorited"})), 200

@articles_blueprint.route("/", methods=["POST"])
def delete_articles():
    # Get request data of 
    data = DeleteArticleRequest(**request.json)
    # TODO : Request Validation
    user = g.current_user
    article_id = data.article_id

    # validating that

    try:
        couchbase_db.query(f"""
            DELETE FROM articles
            WHERE article_id = "{article_id}"
            AND author.username = "{user.username}";
        """)

    except Exception as e:
        return jsonify(ErrorResponse(**{"message": "article with id has been deleted sucessfully"})), 500

    # Return articles as JSON response
    return jsonify(DeleteArticleResponse(**{"message": "article with id has been deleted sucessfully"})), 200


@articles_blueprint.route("/<slug>", methods=["GET"])
def get_article_by_slug(slug):
    # Query the database to fetch the article based on the slug
    try:
        article = couchbase_db.query(f"""
            SELECT *
            FROM articles
            WHERE slug = '{slug}';
        """)

        for row in article.rows():
            article = row['articles']
            return jsonify({"article": article}), 200
        # article = article.rows()[0]['articles']
        
        # If article is found, return it as JSON response
        if article:
            return jsonify(GetArticleResponse(**{"article": article})), 200
        else:
            return jsonify(ErrorResponse(**{"error": "Article not found"})), 404
    except Exception as e:
        return jsonify(ErrorResponse(**{"error": "Internal Server Error"})), 500

@articles_blueprint.route("/tags", methods=["GET"])
def get_all_tags():
    try:
        articles = couchbase_db.query(f"""
            SELECT *
            FROM article
            WHERE ARRAY_LENGTH(tag_list, 1) > 0;;
        """)
        tags = []
        for row in articles.rows:
            article = row['articles']
            tags.extend(article.tag_list)
        return jsonify(GetTagsResponse(**{"tags": tags})), 200
    except Exception as e:
        return jsonify(ErrorResponse(**{"error": "Internal Server Error"})), 500
    
@articles_blueprint.blueprint.route("/get_followed_articles", methods=["GET"])
def get_followed_articles():
    try:
        current_user = g.current_user

        followed_profiles_data = couchbase_db.query("""SELECT followed_username from users where following_username = "{current_user.username}"; """)
        followed_profiles = []

        for row in followed_profiles_data.rows():
            followed_profiles.append(row['followed_username'])

        articles = couchbase_db.query(f"""
            SELECT *
            FROM articles
            WHERE username IN {followed_profiles};
        """)
        articles_data = []
        for row in articles.rows:
            article = row['articles']
            articles_data.append(article)
        return jsonify(GetArticlesResponse(**{"articles": articles_data})), 200
    except Exception as e:
        return jsonify(ErrorResponse(**{"error": "Internal Server Error"})), 500