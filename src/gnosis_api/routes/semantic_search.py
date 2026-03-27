from __future__ import annotations

import numpy as np
from fastapi import APIRouter, Depends, Query

from gnosis_api.auth import require_api_key
from gnosis_api.db import get_gnosis_db
from gnosis_api.embedding import get_index, get_model
from gnosis_api.models import SemanticSearchResultOut

router = APIRouter(prefix="/v1/search/semantic", tags=["search"])

_VALID_TYPES = frozenset(
    {
        "verse",
        "person",
        "place",
        "event",
        "topic",
        "dictionary",
        "strongs",
        "lexicon",
        "greek_lexicon",
    }
)


@router.get("", response_model=list[SemanticSearchResultOut])
async def semantic_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(default=10, ge=1, le=50),
    type: str | None = Query(default=None),
    _auth: dict = Depends(require_api_key),
):
    if type is not None and type not in _VALID_TYPES:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail=f"Invalid type filter. Must be one of: {', '.join(sorted(_VALID_TYPES))}",
        )

    model = get_model()
    index = get_index()

    vector = model.encode(q, normalize_embeddings=True)

    fetch_count = limit * 3 if type is not None else limit
    matches = index.search(np.array(vector, dtype=np.float32), fetch_count)

    keys = [int(k) for k in matches.keys]
    distances = list(matches.distances)

    if not keys:
        return []

    db = get_gnosis_db()
    placeholders = ",".join("?" * len(keys))
    rows = await db.execute(
        f"SELECT vector_id, entity_slug, entity_type, embed_text "
        f"FROM vector_meta WHERE vector_id IN ({placeholders})",
        keys,
    )
    meta_map = {row["vector_id"]: row for row in await rows.fetchall()}

    results: list[SemanticSearchResultOut] = []
    for key, dist in zip(keys, distances):
        meta = meta_map.get(key)
        if meta is None:
            continue
        if type is not None and meta["entity_type"] != type:
            continue
        results.append(
            SemanticSearchResultOut(
                slug=meta["entity_slug"],
                type=meta["entity_type"],
                text=meta["embed_text"],
                score=round(1.0 - float(dist), 4),
            )
        )
        if len(results) >= limit:
            break

    return results
