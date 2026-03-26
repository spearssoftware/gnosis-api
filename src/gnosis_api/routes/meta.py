import sqlite3

from fastapi import APIRouter, Depends

from gnosis_api.auth import require_api_key
from gnosis_api.db import get_gnosis_db

router = APIRouter(prefix="/v1", tags=["meta"])


@router.get("/meta")
async def get_meta(_auth: dict = Depends(require_api_key)):
    db = get_gnosis_db()

    meta_rows = await db.execute("SELECT key, value FROM gnosis_meta")
    meta = {r["key"]: r["value"] for r in await meta_rows.fetchall()}

    tables = ["person", "place", "event", "people_group", "strongs", "dictionary_entry", "topic", "lexicon_entry", "cross_reference", "hebrew_word", "greek_word", "greek_lexicon_entry"]
    subqueries = ", ".join(f"(SELECT COUNT(*) FROM {t}) as {t}" for t in tables)
    try:
        row = await db.execute(f"SELECT {subqueries}")
        r = await row.fetchone()
        counts = {t: r[t] for t in tables}
    except sqlite3.OperationalError:
        counts = {}
        for t in tables:
            try:
                row = await db.execute(f"SELECT COUNT(*) as cnt FROM {t}")
                counts[t] = (await row.fetchone())["cnt"]
            except sqlite3.OperationalError:
                pass

    return {
        "data": {
            "version": meta.get("version"),
            "build_date": meta.get("build_date"),
            "counts": counts,
        }
    }


@router.get("/usage")
async def get_usage(auth: dict = Depends(require_api_key)):
    return {
        "data": {
            "email": auth["email"],
            "tier": auth["tier"],
            "daily_limit": auth["daily_limit"],
            "daily_used": auth["daily_used"],
        }
    }
