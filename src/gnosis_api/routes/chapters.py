from fastapi import APIRouter, Depends, HTTPException

from gnosis_api.auth import require_api_key
from gnosis_api.db import get_gnosis_db
from gnosis_api.models import ChapterEntitiesOut, SingleResponse

router = APIRouter(prefix="/v1/chapters", tags=["chapters"])


@router.get("/{book}/{chapter}", response_model=SingleResponse[ChapterEntitiesOut])
async def get_chapter_entities(book: str, chapter: int, _auth: dict = Depends(require_api_key)):
    db = get_gnosis_db()

    rows = await db.execute("SELECT id FROM verse WHERE osis_ref LIKE ?", (f"{book}.{chapter}.%",))
    verse_ids = [r["id"] for r in await rows.fetchall()]

    if not verse_ids:
        raise HTTPException(status_code=404, detail="Chapter not found")

    placeholders = ",".join("?" * len(verse_ids))

    rows = await db.execute(
        f"""
        SELECT 'person' as kind, p.slug FROM person p JOIN person_verse pv ON p.id = pv.person_id WHERE pv.verse_id IN ({placeholders})
        UNION
        SELECT 'place', pl.slug FROM place pl JOIN place_verse plv ON pl.id = plv.place_id WHERE plv.verse_id IN ({placeholders})
        UNION
        SELECT 'event', e.slug FROM event e JOIN event_verse ev ON e.id = ev.event_id WHERE ev.verse_id IN ({placeholders})
        UNION
        SELECT 'topic', t.slug FROM topic t JOIN topic_aspect ta ON t.id = ta.topic_id JOIN topic_aspect_verse tav ON ta.id = tav.aspect_id WHERE tav.verse_id IN ({placeholders})
        """,
        verse_ids * 4,
    )

    people: list[str] = []
    places: list[str] = []
    events: list[str] = []
    topics: list[str] = []
    buckets = {"person": people, "place": places, "event": events, "topic": topics}
    for r in await rows.fetchall():
        buckets[r["kind"]].append(r["slug"])

    return SingleResponse(
        data=ChapterEntitiesOut(book=book, chapter=chapter, people=people, places=places, events=events, topics=topics)
    )
