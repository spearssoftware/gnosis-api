from __future__ import annotations

import hashlib
import time

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from gnosis_api.config import settings
from gnosis_api.db import get_keys_db

_api_key_header = APIKeyHeader(name="X-API-Key")


def _hash_key(key: str) -> str:
    return hashlib.sha256(f"{settings.api_key_salt}:{key}".encode()).hexdigest()


async def require_api_key(
    api_key: str = Security(_api_key_header),
) -> dict:
    db = get_keys_db()
    key_hash = _hash_key(api_key)

    row = await db.execute_fetchall(
        "SELECT key_hash, email, tier, enabled FROM api_key WHERE key_hash = ?",
        (key_hash,),
    )
    if not row:
        raise HTTPException(status_code=401, detail="Invalid API key")

    record = row[0]
    if not record["enabled"]:
        raise HTTPException(status_code=401, detail="API key disabled")

    daily_limit = (
        settings.rate_limit_daily_paid
        if record["tier"] == "paid"
        else settings.rate_limit_daily
    )
    cutoff = time.time() - 86400
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
        (key_hash, time.time()),
    )
    await db.commit()

    return {
        "key_hash": key_hash,
        "email": record["email"],
        "tier": record["tier"],
        "daily_limit": daily_limit,
        "daily_used": count + 1,
    }
