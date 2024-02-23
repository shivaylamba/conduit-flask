from flask import Flask
from dotenv import load_dotenv
from routes.v1.users import users_blueprint
from routes.v1.articles import articles_blueprint
import os
from extensions import couchbase_db

# Couchbase client object shared by all routes
load_dotenv()

def connectDB():
    conn_str = os.getenv('DB_CONNECTION_STRING')
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    couchbase_db.init_app(conn_str, username, password)
    # couchbase_db.upsert_document("users", "1", {"as" : "45"})


def _register_blueprints(app: Flask):
    app.register_blueprint(users_blueprint, url_prefix = users_blueprint.url_prefix)
    app.register_blueprint(articles_blueprint, url_prefix = articles_blueprint.url_prefix)

def create_app() -> Flask:
    app = Flask(__name__)
    _register_blueprints(app)
    connectDB()
    if __name__ == '__main__':
        app.run(debug=True, host="0.0.0.0", port=8080)
    return app

app = create_app()