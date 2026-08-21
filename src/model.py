import psycopg
from psycopg.rows import class_row
from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime, timedelta


class WorkSession(BaseModel):
    id: UUID
    started_at: datetime
    ended_at: datetime | None


class WorkDayDB(BaseModel):
    work_date: date
    total_worked: timedelta


def get_active_session(conn: psycopg.Connection) -> WorkSession | None:
    quary = "SELECT * from work_sessions WHERE ended_at IS NULL"

    with conn.cursor(row_factory=class_row(WorkSession)) as cur:

        cur.execute(quary)
        return cur.fetchone()


def update_active_session(
    conn: psycopg.Connection,
    session_id: UUID,
    end_time: datetime | None = None,
):

    if end_time is None:
        end_time = datetime.now().astimezone()

    quary = "UPDATE work_sessions SET ended_at = %(end_time)s WHERE id = %(id)s"

    with conn.cursor() as cur:
        cur.execute(quary, {"end_time": end_time, "id": session_id})


def create_session(conn: psycopg.Connection):
    quary = "INSERT INTO work_sessions DEFAULT VALUES"

    with conn.cursor() as cur:
        cur.execute(quary)


def get_sessions_for_period(
    start_date, end_date, conn: psycopg.Connection
) -> list[WorkSession]:
    quary = """SELECT * from work_sessions
        WHERE started_at >= %(start_date)s
        and started_at < %(end_date)s
    """

    with conn.cursor(row_factory=class_row(WorkSession)) as cur:
        cur.execute(quary, {"start_date": start_date, "end_date": end_date})
        return cur.fetchall()


def get_hourse_for_period(
    start_date, end_date, conn: psycopg.Connection
) -> list[WorkDayDB]:
    quary = """
        SELECT started_at::date AS work_date,
        COALESCE(SUM(COALESCE(ended_at, NOW()) - started_at),
        INTERVAL '0'
        ) AS total_worked
        FROM work_sessions
        WHERE started_at >= %(start_date)s
        and started_at < %(end_date)s
        GROUP BY started_at::date
        ORDER BY work_date
    """

    with conn.cursor(row_factory=class_row(WorkDayDB)) as cur:
        cur.execute(quary, {"start_date": start_date, "end_date": end_date})
        return cur.fetchall()


def get_total_for_period(start_date, end_date, conn: psycopg.Connection) -> timedelta:
    quary = """
        SELECT COALESCE(SUM(COALESCE(ended_at, NOW()) - started_at),
        INTERVAL '0'
        )
        FROM work_sessions
        WHERE started_at >= %(start_date)s
        and started_at < %(end_date)s
        """

    with conn.cursor() as cur:
        cur.execute(quary, {"start_date": start_date, "end_date": end_date})
        delta = cur.fetchone()
        assert delta is not None
        return delta[0]
