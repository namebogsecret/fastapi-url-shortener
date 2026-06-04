"""A minimal URL shortener: FastAPI + SQLite, base62 short codes, redirects + stats.

Run: uvicorn app:app --reload
"""
from __future__ import annotations

import sqlite3
import string
from contextlib import closing
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

DB = Path(__file__).with_name("urls.db")
ALPHABET = string.digits + string.ascii_letters  # base62


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(_conn()) as c, c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS urls (
                   id     INTEGER PRIMARY KEY AUTOINCREMENT,
                   target TEXT NOT NULL,
                   hits   INTEGER NOT NULL DEFAULT 0
               )"""
        )


def encode(n: int) -> str:
    s = ""
    while n:
        n, r = divmod(n, 62)
        s = ALPHABET[r] + s
    return s or "0"


def decode(code: str) -> int:
    n = 0
    for ch in code:
        n = n * 62 + ALPHABET.index(ch)
    return n


app = FastAPI(title="URL Shortener", version="1.0")
init_db()


class ShortenIn(BaseModel):
    url: HttpUrl


class ShortenOut(BaseModel):
    code: str
    short_url: str
    target: str


@app.post("/shorten", response_model=ShortenOut)
def shorten(body: ShortenIn) -> ShortenOut:
    with closing(_conn()) as c, c:
        cur = c.execute("INSERT INTO urls (target) VALUES (?)", (str(body.url),))
        code = encode(cur.lastrowid)
    return ShortenOut(code=code, short_url=f"/{code}", target=str(body.url))


@app.get("/{code}")
def follow(code: str) -> RedirectResponse:
    try:
        rid = decode(code)
    except ValueError:
        raise HTTPException(404, "bad code")
    with closing(_conn()) as c, c:
        row = c.execute("SELECT target FROM urls WHERE id = ?", (rid,)).fetchone()
        if not row:
            raise HTTPException(404, "not found")
        c.execute("UPDATE urls SET hits = hits + 1 WHERE id = ?", (rid,))
    return RedirectResponse(row["target"])


@app.get("/stats/{code}")
def stats(code: str) -> dict:
    with closing(_conn()) as c:
        row = c.execute("SELECT target, hits FROM urls WHERE id = ?", (decode(code),)).fetchone()
    if not row:
        raise HTTPException(404, "not found")
    return {"code": code, "target": row["target"], "hits": row["hits"]}
