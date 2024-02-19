from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException
from datetime import timedelta


class CouchbaseClient(object):
    """Class to handle interactions with Couchbase cluster"""

    def __init__(self) -> None:
        self.cluster = None
        self.bucket = None
        self.scope = None

    def init_app(self, conn_str: str, username: str, password: str):
        """Initialize connection to the Couchbase cluster"""
        print("Initializing connection")
        self.conn_str = conn_str
        self.bucket_name = "travel-sample"
        self.scope_name = "inventory"
        self.username = username
        self.password = password
        self.connect()

    def connect(self) -> None:
        """Connect to the Couchbase cluster"""
        print("Connecting to Couchbase")
        # If the connection is not established, establish it now
        if not self.cluster:
            try:
                # authentication for Couchbase cluster
                auth = PasswordAuthenticator(self.username, self.password)

                cluster_opts = ClusterOptions(auth)
                cluster_opts.kv_timeout = timedelta(milliseconds=10000)  # Set KV timeout
                cluster_opts.query_timeout = timedelta(milliseconds=10000)  # Set query timeout
                # wan_development is used to avoid latency issues while connecting to Couchbase over the internet
                cluster_opts.apply_profile("wan_development")
   
                self.cluster = Cluster(self.conn_str, cluster_opts)
                self.cluster.wait_until_ready(timedelta(seconds=5))
                # get a reference to our bucket
                self.bucket = self.cluster.bucket(self.bucket_name)
                
            except CouchbaseException as error:
                print(f"Could not connect to cluster. \nError: {error}")
                print(
                    "Ensure that you have the travel-sample bucket loaded in the cluster."
                )
                exit()

            if not self.check_scope_exists():
                print(
                    "Inventory scope does not exist in the bucket. \nEnsure that you have the inventory scope in your travel-sample bucket."
                )
                exit()

            # get a reference to our scope
            self.scope = self.bucket.scope(self.scope_name)
            print("Connected to Couchbase")

    def check_scope_exists(self) -> bool:
        """Check if the scope exists in the bucket"""
        try:
            scopes_in_bucket = [
                scope.name for scope in self.bucket.collections().get_all_scopes()
            ]
            return self.scope_name in scopes_in_bucket
        except Exception as e:
            print(
                "Error fetching scopes in cluster. \nEnsure that travel-sample bucket exists."
            )
            print(e)
            exit()

    def get_document(self, collection_name: str, key: str):
        """Get document by key using KV operation"""
        return self.scope.collection(collection_name).get(key)

    def insert_document(self, collection_name: str, key: str, doc: dict):
        """Insert document using KV operation"""
        return self.scope.collection(collection_name).insert(key, doc)

    def delete_document(self, collection_name: str, key: str):
        """Delete document using KV operation"""
        return self.scope.collection(collection_name).remove(key)

    def upsert_document(self, collection_name: str, key: str, doc: dict):
        """Upsert document using KV operation"""
        print("Upsert document using KV operation : " , doc)
        return self.scope.collection(collection_name).upsert(key, doc)

    def query(self, sql_query, *options, **kwargs):
        """Query Couchbase using SQL++"""
        # options are used for positional parameters
        # kwargs are used for named parameters
        return self.scope.query(sql_query, *options, **kwargs)