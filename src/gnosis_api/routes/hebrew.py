from fastapi import APIRouter, Depends, HTTPException

from gnosis_api.auth import require_api_key
from gnosis_api.db import get_gnosis_db
from gnosis_api.models import HebrewWordOut, ListMeta, ListResponse

router = APIRouter(prefix="/v1/hebrew", tags=["hebrew"])


@router.get("/{osis_ref}", response_model=ListResponse[HebrewWordOut])
async def get_hebrew_words(osis_ref: str, _auth: dict = Depends(require_api_key)):
    db = get_gnosis_db()
    verse_row = await db.execute("SELECT id FROM verse WHERE osis_ref = ?", (osis_ref,))
    verse = await verse_row.fetchone()
    if not verse:
        raise HTTPException(status_code=404, detail="Verse not found")

    rows = await db.execute(
        "SELECT word_id, position, text, lemma_raw, strongs_number, morph FROM hebrew_word WHERE verse_id = ? ORDER BY position",
        (verse["id"],),
    )
    words = [
        HebrewWordOut(
            word_id=r["word_id"],
            position=r["position"],
            text=r["text"],
            lemma_raw=r["lemma_raw"],
            strongs_number=r["strongs_number"],
            morph=r["morph"],
        )
        for r in await rows.fetchall()
    ]

    return ListResponse(data=words, meta=ListMeta(total=len(words), limit=len(words), offset=0))
