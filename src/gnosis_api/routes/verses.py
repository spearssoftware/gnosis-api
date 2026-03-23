from fastapi import APIRouter, Depends, HTTPException

from gnosis_api.auth import require_api_key
from gnosis_api.db import get_gnosis_db
from gnosis_api.models import CrossReferenceOut, ListResponse, ListMeta, SingleResponse, VerseEntitiesOut

router = APIRouter(prefix="/v1/verses", tags=["verses"])


@router.get("/{osis_ref}", response_model=SingleResponse[VerseEntitiesOut])
async def get_verse_entities(osis_ref: str, _auth: dict = Depends(require_api_key)):
    db = get_gnosis_db()
    row = await db.execute("SELECT id FROM verse WHERE osis_ref = ?", (osis_ref,))
    verse = await row.fetchone()
    if not verse:
        raise HTTPException(status_code=404, detail="Verse not found")

    vid = verse["id"]

    people = [
        r["slug"]
        async for r in await db.execute(
            "SELECT p.slug FROM person p JOIN person_verse pv ON p.id = pv.person_id WHERE pv.verse_id = ?",
            (vid,),
        )
    ]
    places = [
        r["slug"]
        async for r in await db.execute(
            "SELECT pl.slug FROM place pl JOIN place_verse plv ON pl.id = plv.place_id WHERE plv.verse_id = ?",
            (vid,),
        )
    ]
    events = [
        r["slug"]
        async for r in await db.execute(
            "SELECT e.slug FROM event e JOIN event_verse ev ON e.id = ev.event_id WHERE ev.verse_id = ?",
            (vid,),
        )
    ]

    return SingleResponse(
        data=VerseEntitiesOut(osis_ref=osis_ref, people=people, places=places, events=events)
    )


@router.get("/{osis_ref}/cross-references", response_model=ListResponse[CrossReferenceOut])
async def get_cross_references(osis_ref: str, _auth: dict = Depends(require_api_key)):
    db = get_gnosis_db()
    row = await db.execute("SELECT id FROM verse WHERE osis_ref = ?", (osis_ref,))
    verse = await row.fetchone()
    if not verse:
        raise HTTPException(status_code=404, detail="Verse not found")

    vid = verse["id"]
    rows = await db.execute(
        """
        SELECT vs.osis_ref as to_start, ve.osis_ref as to_end, cr.votes
        FROM cross_reference cr
        JOIN verse vs ON cr.to_verse_start_id = vs.id
        LEFT JOIN verse ve ON cr.to_verse_end_id = ve.id
        WHERE cr.from_verse_id = ?
        ORDER BY cr.votes DESC
        """,
        (vid,),
    )
    refs = [
        CrossReferenceOut(
            from_verse=osis_ref,
            to_verse_start=r["to_start"],
            to_verse_end=r["to_end"],
            votes=r["votes"],
        )
        for r in await rows.fetchall()
    ]

    return ListResponse(data=refs, meta=ListMeta(total=len(refs), limit=len(refs), offset=0))
