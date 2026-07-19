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


@app.get("/hours/today")
def get_todays_total(conn: Conn):
    return service.get_todays_total(conn)
