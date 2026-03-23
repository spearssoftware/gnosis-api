from fastapi import APIRouter, Depends, HTTPException, Query

from gnosis_api.auth import require_api_key
from gnosis_api.db import get_gnosis_db
from gnosis_api.models import EventOut, ListMeta, ListResponse, SingleResponse

router = APIRouter(prefix="/v1/events", tags=["events"])


async def _build_event(row: dict) -> EventOut:
    db = get_gnosis_db()
    eid = row["id"]

    parent_event = None
    if row["parent_event_id"]:
        r = await db.execute("SELECT slug FROM event WHERE id = ?", (row["parent_event_id"],))
        pe = await r.fetchone()
        if pe:
            parent_event = pe["slug"]

    predecessor = None
    if row["predecessor_id"]:
        r = await db.execute("SELECT slug FROM event WHERE id = ?", (row["predecessor_id"],))
        pr = await r.fetchone()
        if pr:
            predecessor = pr["slug"]

    participants = [
        r["slug"]
        async for r in await db.execute(
            "SELECT p.slug FROM person p JOIN event_participant ep ON p.id = ep.person_id WHERE ep.event_id = ?",
            (eid,),
        )
    ]
    locations = [
        r["slug"]
        async for r in await db.execute(
            "SELECT pl.slug FROM place pl JOIN event_verse ev ON pl.id = ev.event_id WHERE ev.event_id = ?",
            (eid,),
        )
    ]
    verses = [
        r["osis_ref"]
        async for r in await db.execute(
            "SELECT v.osis_ref FROM verse v JOIN event_verse ev ON v.id = ev.verse_id WHERE ev.event_id = ?",
            (eid,),
        )
    ]

    return EventOut(
        slug=row["slug"],
        uuid=row["uuid"],
        title=row["title"],
        start_year=row["start_year"],
        start_year_display=row["start_year_display"],
        duration=row["duration"],
        sort_key=row["sort_key"],
        participants=participants,
        locations=locations,
        verses=verses,
        parent_event=parent_event,
        predecessor=predecessor,
    )


@router.get("", response_model=ListResponse[EventOut])
async def list_events(
    q: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    _auth: dict = Depends(require_api_key),
):
    db = get_gnosis_db()
    conditions = []
    params: list = []

    if q:
        conditions.append("title LIKE ?")
        params.append(f"%{q}%")

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    count_row = await db.execute(f"SELECT COUNT(*) as cnt FROM event {where}", params)
    total = (await count_row.fetchone())["cnt"]

    rows = await db.execute(
        f"SELECT * FROM event {where} ORDER BY sort_key LIMIT ? OFFSET ?",
        [*params, limit, offset],
    )
    events = [await _build_event(dict(r)) for r in await rows.fetchall()]

    return ListResponse(data=events, meta=ListMeta(total=total, limit=limit, offset=offset))


@router.get("/{slug}", response_model=SingleResponse[EventOut])
async def get_event(slug: str, _auth: dict = Depends(require_api_key)):
    db = get_gnosis_db()
    row = await db.execute("SELECT * FROM event WHERE slug = ?", (slug,))
    event = await row.fetchone()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return SingleResponse(data=await _build_event(dict(event)))
