from fastapi import APIRouter, Depends, HTTPException, Query

from gnosis_api.auth import require_api_key
from gnosis_api.db import get_gnosis_db
from gnosis_api.models import (
    ListMeta,
    ListResponse,
    SingleResponse,
    TopicAspectOut,
    TopicOut,
)

router = APIRouter(prefix="/v1/topics", tags=["topics"])


async def _build_topic(row: dict) -> TopicOut:
    db = get_gnosis_db()
    tid = row["id"]

    aspect_rows = await db.execute(
        "SELECT id, label, source FROM topic_aspect WHERE topic_id = ?", (tid,)
    )
    aspects = []
    for ar in await aspect_rows.fetchall():
        verses = [
            r["osis_ref"]
            async for r in await db.execute(
                "SELECT v.osis_ref FROM verse v JOIN topic_aspect_verse tav ON v.id = tav.verse_id WHERE tav.aspect_id = ?",
                (ar["id"],),
            )
        ]
        aspects.append(TopicAspectOut(label=ar["label"], source=ar["source"], verses=verses))

    see_also = [
        r["slug"]
        async for r in await db.execute(
            "SELECT t.slug FROM topic t JOIN topic_see_also tsa ON t.id = tsa.related_topic_id WHERE tsa.topic_id = ?",
            (tid,),
        )
    ]

    return TopicOut(
        slug=row["slug"],
        uuid=row["uuid"],
        name=row["name"],
        aspects=aspects,
        see_also=see_also,
    )


@router.get("", response_model=ListResponse[TopicOut])
async def list_topics(
    q: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    _auth: dict = Depends(require_api_key),
):
    db = get_gnosis_db()
    conditions = []
    params: list = []

    if q:
        conditions.append("name LIKE ?")
        params.append(f"%{q}%")

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    count_row = await db.execute(f"SELECT COUNT(*) as cnt FROM topic {where}", params)
    total = (await count_row.fetchone())["cnt"]

    rows = await db.execute(
        f"SELECT * FROM topic {where} ORDER BY name LIMIT ? OFFSET ?",
        [*params, limit, offset],
    )
    topics = [await _build_topic(dict(r)) for r in await rows.fetchall()]

    return ListResponse(data=topics, meta=ListMeta(total=total, limit=limit, offset=offset))


@router.get("/{slug}", response_model=SingleResponse[TopicOut])
async def get_topic(slug: str, _auth: dict = Depends(require_api_key)):
    db = get_gnosis_db()
    row = await db.execute("SELECT * FROM topic WHERE slug = ?", (slug,))
    topic = await row.fetchone()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    return SingleResponse(data=await _build_topic(dict(topic)))
