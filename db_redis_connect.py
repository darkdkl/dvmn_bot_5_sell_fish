import redis,os

_database = None


def get_database_connection():
    global _database
    if _database is None:
        database_password = os.environ["DATABASE_PASSWORD"]
        database_host = os.environ["DATABASE_HOST"]
        database_port = os.environ["DATABASE_PORT"]
        _database = redis.Redis(
            host=database_host, port=database_port, password=database_password)

   return _database
