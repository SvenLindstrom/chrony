import model

import psycopg
from datetime import timedelta


def toggle_session(conn: psycopg.Connection):
    session = model.get_active_session(conn)
    if session is None:
        model.create_session(conn)
    else:
        model.update_active_session(conn, session.id)


def get_todays_total(conn: psycopg.Connection):
    duration = model.get_todays_total(conn)

    total_seconds = int(duration.total_seconds())

    return {
        "total_seconds": total_seconds,
        "hours": total_seconds // 3600,
        "minutes": (total_seconds % 3600) // 60,
    }
