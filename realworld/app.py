from flask import Flask, jsonify
from dotenv import load_dotenv
import os
from db import CouchbaseClient

# Couchbase client object shared by all routes
load_dotenv()
app = Flask(__name__)
couchbase_db = CouchbaseClient()

conn_str = os.getenv('DB_CONNECTION_STRING')
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')

couchbase_db.init_app(conn_str, username, password, app)

@app.route('/')
def hello_world():
    return jsonify({'message': 'Hello, World!'})

if __name__ == '__main__':
    app.run(debug=True)
