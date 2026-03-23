from fastapi import APIRouter, Depends, HTTPException, Query

from gnosis_api.auth import require_api_key
from gnosis_api.db import get_gnosis_db
from gnosis_api.models import ListMeta, ListResponse, PeopleGroupOut, SingleResponse

router = APIRouter(prefix="/v1/groups", tags=["groups"])


async def _build_group(row: dict) -> PeopleGroupOut:
    db = get_gnosis_db()
    members = [
        r["slug"]
        async for r in await db.execute(
            "SELECT p.slug FROM person p JOIN person_group pg ON p.id = pg.person_id WHERE pg.group_id = ?",
            (row["id"],),
        )
    ]
    return PeopleGroupOut(
        slug=row["slug"],
        uuid=row["uuid"],
        name=row["name"],
        members=members,
    )


@router.get("", response_model=ListResponse[PeopleGroupOut])
async def list_groups(
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

    count_row = await db.execute(f"SELECT COUNT(*) as cnt FROM people_group {where}", params)
    total = (await count_row.fetchone())["cnt"]

    rows = await db.execute(
        f"SELECT * FROM people_group {where} ORDER BY name LIMIT ? OFFSET ?",
        [*params, limit, offset],
    )
    groups = [await _build_group(dict(r)) for r in await rows.fetchall()]

    return ListResponse(data=groups, meta=ListMeta(total=total, limit=limit, offset=offset))


@router.get("/{slug}", response_model=SingleResponse[PeopleGroupOut])
async def get_group(slug: str, _auth: dict = Depends(require_api_key)):
    db = get_gnosis_db()
    row = await db.execute("SELECT * FROM people_group WHERE slug = ?", (slug,))
    group = await row.fetchone()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    return SingleResponse(data=await _build_group(dict(group)))
