import psycopg
import os


def create_connection():
    return psycopg.connect(
        host=os.environ.get("POSTGRES_HOST", "postgres"),
        port=os.environ.get("POSTGRES_PORT", "5432"),
        dbname=os.environ["POSTGRES_NAME"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def get_connection():
    with create_connection() as conn:
        yield conn


def init_db():
    with open("schema.sql", "r") as f:
        schema = f.read()

    with create_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(schema)
