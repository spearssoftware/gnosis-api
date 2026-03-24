from __future__ import annotations

import time
from typing import TypedDict

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from gnosis_api.config import settings
from gnosis_api.db import get_keys_db
from gnosis_api.keys import hash_key
from gnosis_api.rate_limit import get_burst_limiter

_api_key_header = APIKeyHeader(name="X-API-Key")


class ApiKeyContext(TypedDict):
    key_hash: str
    email: str
    tier: str
    daily_limit: int
    daily_used: int


async def require_api_key(
    api_key: str = Security(_api_key_header),
) -> ApiKeyContext:
    key_hash = hash_key(api_key)

    if not get_burst_limiter().is_allowed(key_hash):
        raise HTTPException(
            status_code=429,
            detail="Too many requests — slow down",
            headers={"Retry-After": "1"},
        )

    db = get_keys_db()
    row = await db.execute_fetchall(
        "SELECT key_hash, email, tier, enabled FROM api_key WHERE key_hash = ?",
        (key_hash,),
    )
    if not row:
        raise HTTPException(status_code=401, detail="Invalid API key")

    record = row[0]
    if not record["enabled"]:
        raise HTTPException(status_code=401, detail="API key disabled")

    now = time.time()
    daily_limit = (
        settings.rate_limit_daily_paid
        if record["tier"] == "paid"
        else settings.rate_limit_daily
    )
    cutoff = now - 86400
    count_row = await db.execute_fetchall(
        "SELECT COUNT(*) as cnt FROM request_log WHERE key_hash = ? AND timestamp > ?",
        (key_hash, cutoff),
    )
    count = count_row[0]["cnt"]

    if count >= daily_limit:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": "3600"},
        )

    await db.execute(
        "INSERT INTO request_log (key_hash, timestamp) VALUES (?, ?)",
        (key_hash, now),
    )
    await db.commit()

    return ApiKeyContext(
        key_hash=key_hash,
        email=record["email"],
        tier=record["tier"],
        daily_limit=daily_limit,
        daily_used=count + 1,
    )
