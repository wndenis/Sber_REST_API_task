import os

"""
retrieve environment vars from docker-compose
so configuration made only once at deployment
"""

pg_host = os.environ["POSTGRES_HOST"]
pg_port = os.environ["POSTGRES_PORT"]

pg_user = os.environ["POSTGRES_USER"]
pg_password = os.environ["POSTGRES_PASSWORD"]

pg_db = os.environ["POSTGRES_DB"]

DB_URI = f"postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"

fake_db = bool(os.environ["FAKE_DB"])
