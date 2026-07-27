from datetime import date, datetime

from fastapi import Depends, FastAPI
import psycopg
from typing import Annotated
import service
from db import get_connection, init_db
from contextlib import asynccontextmanager

Conn = Annotated[psycopg.Connection, Depends(get_connection)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/session/toggle")
def toggle_session(conn: Conn):
    service.toggle_session(conn)


@app.get("/session/{date}")
def get_sessions(date: date, conn: Conn):
    return service.get_sessions_for_day(date, conn)


@app.get("/hours/today")
def get_todays_total(conn: Conn):
    return service.get_todays_total(conn)


@app.get("/state")
def get_current_state(conn: Conn):
    return service.get_state(conn)


@app.post("/period")
def get_period(start_date: date, end_date: date, conn: Conn):
    print(start_date)
    print(end_date)
    return service.get_period(start_date, end_date, conn)
