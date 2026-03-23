from fastapi import APIRouter, Depends, HTTPException, Query

from gnosis_api.auth import require_api_key
from gnosis_api.db import get_gnosis_db
from gnosis_api.models import ListMeta, ListResponse, PlaceOut, SingleResponse

router = APIRouter(prefix="/v1/places", tags=["places"])


def _row_to_place(row: dict) -> PlaceOut:
    return PlaceOut(
        slug=row["slug"],
        uuid=row["uuid"],
        name=row["name"],
        kjv_name=row["kjv_name"],
        esv_name=row["esv_name"],
        latitude=row["latitude"],
        longitude=row["longitude"],
        coordinate_source=row["coordinate_source"],
        feature_type=row["feature_type"],
        feature_sub_type=row["feature_sub_type"],
        modern_name=row["modern_name"],
    )


@router.get("", response_model=ListResponse[PlaceOut])
async def list_places(
    q: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    has_coordinates: bool | None = None,
    feature_type: str | None = None,
    _auth: dict = Depends(require_api_key),
):
    db = get_gnosis_db()
    conditions = []
    params: list = []

    if q:
        conditions.append("name LIKE ?")
        params.append(f"%{q}%")
    if has_coordinates is True:
        conditions.append("latitude IS NOT NULL")
    elif has_coordinates is False:
        conditions.append("latitude IS NULL")
    if feature_type:
        conditions.append("feature_type = ?")
        params.append(feature_type)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    count_row = await db.execute(f"SELECT COUNT(*) as cnt FROM place {where}", params)
    total = (await count_row.fetchone())["cnt"]

    rows = await db.execute(
        f"SELECT * FROM place {where} ORDER BY name LIMIT ? OFFSET ?",
        [*params, limit, offset],
    )
    places = [_row_to_place(dict(r)) for r in await rows.fetchall()]

    return ListResponse(data=places, meta=ListMeta(total=total, limit=limit, offset=offset))


@router.get("/{slug}", response_model=SingleResponse[PlaceOut])
async def get_place(slug: str, _auth: dict = Depends(require_api_key)):
    db = get_gnosis_db()
    row = await db.execute("SELECT * FROM place WHERE slug = ?", (slug,))
    place = await row.fetchone()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")

    return SingleResponse(data=_row_to_place(dict(place)))
