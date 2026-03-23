from __future__ import annotations

import sqlite3
from contextlib import asynccontextmanager
from typing import AsyncIterator

import aiosqlite

from gnosis_api.config import settings

_gnosis_db: aiosqlite.Connection | None = None
_keys_db: aiosqlite.Connection | None = None

_KEYS_SCHEMA = """
CREATE TABLE IF NOT EXISTS api_key (
    id INTEGER PRIMARY KEY,
    key_hash TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    tier TEXT NOT NULL DEFAULT 'free',
    created_at TEXT NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS request_log (
    id INTEGER PRIMARY KEY,
    key_hash TEXT NOT NULL,
    timestamp REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_request_log_key_ts ON request_log(key_hash, timestamp);
"""


async def init_db() -> None:
    global _gnosis_db, _keys_db

    _gnosis_db = await aiosqlite.connect(
        f"file:{settings.gnosis_db_path}?mode=ro",
        uri=True,
    )
    _gnosis_db.row_factory = aiosqlite.Row

    _keys_db = await aiosqlite.connect(str(settings.keys_db_path))
    _keys_db.row_factory = aiosqlite.Row
    await _keys_db.executescript(_KEYS_SCHEMA)
    await _keys_db.commit()


async def close_db() -> None:
    global _gnosis_db, _keys_db
    if _gnosis_db:
        await _gnosis_db.close()
        _gnosis_db = None
    if _keys_db:
        await _keys_db.close()
        _keys_db = None


def get_gnosis_db() -> aiosqlite.Connection:
    if _gnosis_db is None:
        raise RuntimeError("Database not initialized")
    return _gnosis_db


def get_keys_db() -> aiosqlite.Connection:
    if _keys_db is None:
        raise RuntimeError("Keys database not initialized")
    return _keys_db
