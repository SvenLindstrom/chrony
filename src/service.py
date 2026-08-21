from datetime import date, datetime, time, timedelta
import os

import model

import psycopg
from pydantic import BaseModel


def get_fallback_time():
    time_str = os.environ.get("FALLBACK_TIME", "17:00").split(":")
    if len(time_str) != 2:
        raise Exception("Failed to parse fallback time")
    hours, minutes = [int(i) for i in time_str]
    return hours, minutes


class Duration(BaseModel):
    total_seconds: int
    hours: int
    minutes: int

    @classmethod
    def from_delta(cls, delta: timedelta):
        seconds = int(delta.total_seconds())
        return cls(
            total_seconds=seconds,
            hours=seconds // 3600,
            minutes=(seconds % 3600) // 60,
        )


class WorkDayResponse(BaseModel):
    date: date
    time_worked: Duration

    @classmethod
    def from_db(cls, work_day: model.WorkDayDB):

        return cls(
            date=work_day.work_date,
            time_worked=Duration.from_delta(work_day.total_worked),
        )


class WorkSessionResponse(BaseModel):
    start: time
    end: time | None
    duration: Duration | None

    @classmethod
    def from_db(cls, work_session: model.WorkSession):
        ended_at = work_session.ended_at
        duration = None
        if ended_at:
            duration = Duration.from_delta(ended_at - work_session.started_at)
            ended_at = ended_at.time()

        return cls(
            start=work_session.started_at.time(),
            end=ended_at,
            duration=duration,
        )


def toggle_session(conn: psycopg.Connection):
    session = model.get_active_session(conn)
    if session is None:
        model.create_session(conn)
    else:
        if session.started_at.date() != date.today():
            hours, minutes = get_fallback_time()
            fallback_end = datetime.combine(
                session.started_at.date(),
                time(hours, minutes),
                tzinfo=session.started_at.tzinfo,
            )
            model.update_active_session(
                conn,
                session.id,
                fallback_end,
            )
            return
        model.update_active_session(conn, session.id)


def get_sessions_for_day(date: date, conn: psycopg.Connection):
    end_at = date + timedelta(days=1)
    sessions = model.get_sessions_for_period(date, end_at, conn)
    sessions_response = [WorkSessionResponse.from_db(k) for k in sessions]
    return {"date": date, "sessions": sessions_response}


def get_hourse_for_period(start_at, end_at, conn: psycopg.Connection):
    return model.get_total_for_period(start_at, end_at, conn)


def get_todays_total(conn: psycopg.Connection):
    start_at = datetime.date(datetime.now())
    end_at = start_at + timedelta(days=1)
    duration = get_hourse_for_period(start_at, end_at, conn)
    return Duration.from_delta(duration)


def get_state(conn: psycopg.Connection):
    working = model.get_active_session(conn) != None
    duration = get_todays_total(conn)
    return {"working": working, "time": duration}


def get_period(start_date, end_date, conn: psycopg.Connection):
    days = model.get_hourse_for_period(start_date, end_date, conn)
    days_response = [WorkDayResponse.from_db(k) for k in days]
    duration = get_hourse_for_period(start_date, end_date, conn)
    return {
        "start": start_date,
        "end": end_date,
        "total_time": Duration.from_delta(duration),
        "days": days_response,
    }
