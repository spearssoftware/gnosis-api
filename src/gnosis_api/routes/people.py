from fastapi import APIRouter, Depends, HTTPException, Query

from gnosis_api.auth import require_api_key
from gnosis_api.db import get_gnosis_db
from gnosis_api.models import ListMeta, ListResponse, PersonOut, SingleResponse

router = APIRouter(prefix="/v1/people", tags=["people"])


async def _build_person(row: dict) -> PersonOut:
    db = get_gnosis_db()
    pid = row["id"]

    birth_place = None
    if row["birth_place_id"]:
        r = await db.execute("SELECT slug FROM place WHERE id = ?", (row["birth_place_id"],))
        bp = await r.fetchone()
        if bp:
            birth_place = bp["slug"]

    death_place = None
    if row["death_place_id"]:
        r = await db.execute("SELECT slug FROM place WHERE id = ?", (row["death_place_id"],))
        dp = await r.fetchone()
        if dp:
            death_place = dp["slug"]

    father = None
    if row["father_id"]:
        r = await db.execute("SELECT slug FROM person WHERE id = ?", (row["father_id"],))
        f = await r.fetchone()
        if f:
            father = f["slug"]

    mother = None
    if row["mother_id"]:
        r = await db.execute("SELECT slug FROM person WHERE id = ?", (row["mother_id"],))
        m = await r.fetchone()
        if m:
            mother = m["slug"]

    siblings = [
        r["slug"]
        async for r in await db.execute(
            "SELECT p.slug FROM person p JOIN person_sibling ps ON p.id = ps.sibling_id WHERE ps.person_id = ?",
            (pid,),
        )
    ]
    children = [
        r["slug"]
        async for r in await db.execute(
            "SELECT p.slug FROM person p JOIN person_child pc ON p.id = pc.child_id WHERE pc.parent_id = ?",
            (pid,),
        )
    ]
    partners = [
        r["slug"]
        async for r in await db.execute(
            "SELECT p.slug FROM person p JOIN person_partner pp ON p.id = pp.partner_id WHERE pp.person_id = ?",
            (pid,),
        )
    ]
    verses = [
        r["osis_ref"]
        async for r in await db.execute(
            "SELECT v.osis_ref FROM verse v JOIN person_verse pv ON v.id = pv.verse_id WHERE pv.person_id = ?",
            (pid,),
        )
    ]
    groups = [
        r["slug"]
        async for r in await db.execute(
            "SELECT g.slug FROM people_group g JOIN person_group pg ON g.id = pg.group_id WHERE pg.person_id = ?",
            (pid,),
        )
    ]

    return PersonOut(
        slug=row["slug"],
        uuid=row["uuid"],
        name=row["name"],
        gender=row["gender"],
        birth_year=row["birth_year"],
        death_year=row["death_year"],
        birth_year_display=row["birth_year_display"],
        death_year_display=row["death_year_display"],
        earliest_year_mentioned=row["earliest_year_mentioned"],
        latest_year_mentioned=row["latest_year_mentioned"],
        earliest_year_mentioned_display=row["earliest_year_mentioned_display"],
        latest_year_mentioned_display=row["latest_year_mentioned_display"],
        birth_place=birth_place,
        death_place=death_place,
        father=father,
        mother=mother,
        siblings=siblings,
        children=children,
        partners=partners,
        verse_count=row["verse_count"],
        verses=verses,
        first_mention=row["first_mention"],
        name_meaning=row["name_meaning"],
        people_groups=groups,
    )


@router.get("", response_model=ListResponse[PersonOut])
async def list_people(
    q: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    gender: str | None = None,
    _auth: dict = Depends(require_api_key),
):
    db = get_gnosis_db()
    conditions = []
    params: list = []

    if q:
        conditions.append("name LIKE ?")
        params.append(f"%{q}%")
    if gender:
        conditions.append("gender = ?")
        params.append(gender)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    count_row = await db.execute(f"SELECT COUNT(*) as cnt FROM person {where}", params)
    total = (await count_row.fetchone())["cnt"]

    rows = await db.execute(
        f"SELECT * FROM person {where} ORDER BY name LIMIT ? OFFSET ?",
        [*params, limit, offset],
    )
    people = [await _build_person(dict(r)) for r in await rows.fetchall()]

    return ListResponse(data=people, meta=ListMeta(total=total, limit=limit, offset=offset))


@router.get("/{slug}", response_model=SingleResponse[PersonOut])
async def get_person(slug: str, _auth: dict = Depends(require_api_key)):
    db = get_gnosis_db()
    row = await db.execute("SELECT * FROM person WHERE slug = ?", (slug,))
    person = await row.fetchone()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    return SingleResponse(data=await _build_person(dict(person)))
