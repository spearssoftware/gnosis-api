from fastapi import APIRouter, Depends, HTTPException, Query

from gnosis_api.auth import require_api_key
from gnosis_api.db import get_gnosis_db
from gnosis_api.models import (
    DictionaryDefinitionOut,
    DictionaryEntryOut,
    ListMeta,
    ListResponse,
    SingleResponse,
)

router = APIRouter(prefix="/v1/dictionary", tags=["dictionary"])


async def _build_entry(row: dict) -> DictionaryEntryOut:
    db = get_gnosis_db()
    eid = row["id"]

    defs = [
        DictionaryDefinitionOut(source=r["source"], text=r["text"])
        async for r in await db.execute(
            "SELECT source, text FROM dictionary_definition WHERE entry_id = ?", (eid,)
        )
    ]
    refs = [
        r["osis_ref"]
        async for r in await db.execute(
            "SELECT v.osis_ref FROM verse v JOIN dictionary_verse dv ON v.id = dv.verse_id WHERE dv.entry_id = ?",
            (eid,),
        )
    ]

    return DictionaryEntryOut(
        slug=row["slug"],
        uuid=row["uuid"],
        name=row["name"],
        definitions=defs,
        scripture_refs=refs,
    )


@router.get("", response_model=ListResponse[DictionaryEntryOut])
async def list_dictionary(
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

    count_row = await db.execute(f"SELECT COUNT(*) as cnt FROM dictionary_entry {where}", params)
    total = (await count_row.fetchone())["cnt"]

    rows = await db.execute(
        f"SELECT * FROM dictionary_entry {where} ORDER BY name LIMIT ? OFFSET ?",
        [*params, limit, offset],
    )
    entries = [await _build_entry(dict(r)) for r in await rows.fetchall()]

    return ListResponse(data=entries, meta=ListMeta(total=total, limit=limit, offset=offset))


@router.get("/{slug}", response_model=SingleResponse[DictionaryEntryOut])
async def get_dictionary_entry(slug: str, _auth: dict = Depends(require_api_key)):
    db = get_gnosis_db()
    row = await db.execute("SELECT * FROM dictionary_entry WHERE slug = ?", (slug,))
    entry = await row.fetchone()
    if not entry:
        raise HTTPException(status_code=404, detail="Dictionary entry not found")

    return SingleResponse(data=await _build_entry(dict(entry)))
