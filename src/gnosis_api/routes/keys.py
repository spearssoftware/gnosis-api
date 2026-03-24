import secrets
from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

from gnosis_api.db import get_keys_db
from gnosis_api.keys import hash_key

router = APIRouter(prefix="/v1", tags=["keys"])


class CreateKeyRequest(BaseModel):
    email: EmailStr


@router.post("/keys")
async def create_key(body: CreateKeyRequest):
    db = get_keys_db()

    cursor = await db.execute(
        "SELECT id FROM api_key WHERE email = ? AND enabled = 1",
        (body.email,),
    )
    existing = await cursor.fetchall()
    replaced = len(existing) > 0

    if replaced:
        await db.execute(
            "UPDATE api_key SET enabled = 0 WHERE email = ? AND enabled = 1",
            (body.email,),
        )

    raw_key = f"gn_{secrets.token_urlsafe(32)}"
    key_hash = hash_key(raw_key)
    await db.execute(
        "INSERT INTO api_key (key_hash, email, tier, created_at) VALUES (?, ?, ?, ?)",
        (key_hash, body.email, "free", datetime.now(UTC).isoformat()),
    )
    await db.commit()

    return {
        "data": {
            "api_key": raw_key,
            "email": body.email,
            "tier": "free",
            "replaced": replaced,
        }
    }
