import psycopg
from psycopg.rows import class_row
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, timedelta


class Work_session(BaseModel):
    id: UUID
    started_at: datetime
    ended_at: datetime | None


def get_active_session(conn: psycopg.Connection) -> Work_session | None:
    quary = "SELECT * from work_sessions WHERE ended_at IS NULL"

    with conn.cursor(row_factory=class_row(Work_session)) as cur:

        cur.execute(quary)
        return cur.fetchone()


def update_active_session(conn: psycopg.Connection, session_id: UUID):

    quary = "UPDATE work_sessions SET ended_at = NOW() WHERE id = %(id)s"

    with conn.cursor() as cur:
        cur.execute(quary, {"id": session_id})


def create_session(conn: psycopg.Connection):
    quary = "INSERT INTO work_sessions DEFAULT VALUES"

    with conn.cursor() as cur:
        cur.execute(quary)


def get_todays_total(conn: psycopg.Connection) -> timedelta:
    quary = """
        SELECT COALESCE(SUM(COALESCE(ended_at, NOW()) - started_at),
        INTERVAL '0'
        )
        FROM work_sessions
        WHERE started_at >= CURRENT_DATE
        and started_at < CURRENT_DATE + INTERVAL '1 day'
    """

    with conn.cursor() as cur:
        cur.execute(quary)
        delta = cur.fetchone()
        assert delta is not None
        return delta[0]
