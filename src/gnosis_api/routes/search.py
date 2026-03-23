from fastapi import APIRouter, Depends, Query

from gnosis_api.auth import require_api_key
from gnosis_api.db import get_gnosis_db
from gnosis_api.models import ListMeta, ListResponse, SearchResultOut

router = APIRouter(prefix="/v1/search", tags=["search"])


@router.get("", response_model=ListResponse[SearchResultOut])
async def search(
    q: str = Query(..., min_length=1),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    _auth: dict = Depends(require_api_key),
):
    db = get_gnosis_db()
    pattern = f"%{q}%"
    results: list[SearchResultOut] = []

    for table, name_col, type_label in [
        ("person", "name", "person"),
        ("place", "name", "place"),
        ("event", "title", "event"),
        ("people_group", "name", "group"),
        ("dictionary_entry", "name", "dictionary"),
        ("topic", "name", "topic"),
    ]:
        rows = await db.execute(
            f"SELECT slug, {name_col} as name, uuid FROM {table} WHERE {name_col} LIKE ?",
            (pattern,),
        )
        for r in await rows.fetchall():
            results.append(
                SearchResultOut(
                    slug=r["slug"],
                    name=r["name"],
                    entity_type=type_label,
                    uuid=r["uuid"],
                )
            )

    results.sort(key=lambda r: r.name.lower())
    total = len(results)
    page = results[offset : offset + limit]

    return ListResponse(data=page, meta=ListMeta(total=total, limit=limit, offset=offset))
