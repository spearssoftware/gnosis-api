from fastapi import APIRouter, Depends, HTTPException

from gnosis_api.auth import require_api_key
from gnosis_api.db import get_gnosis_db
from gnosis_api.models import LexiconEntryOut, SingleResponse

router = APIRouter(prefix="/v1/lexicon", tags=["lexicon"])


@router.get("/{lexical_id}", response_model=SingleResponse[LexiconEntryOut])
async def get_lexicon_entry(lexical_id: str, _auth: dict = Depends(require_api_key)):
    db = get_gnosis_db()
    row = await db.execute("SELECT * FROM lexicon_entry WHERE lexical_id = ?", (lexical_id,))
    entry = await row.fetchone()
    if not entry:
        raise HTTPException(status_code=404, detail="Lexicon entry not found")

    return SingleResponse(
        data=LexiconEntryOut(
            lexical_id=entry["lexical_id"],
            uuid=entry["uuid"],
            hebrew=entry["hebrew"],
            transliteration=entry["transliteration"],
            part_of_speech=entry["part_of_speech"],
            gloss=entry["gloss"],
            strongs_number=entry["strongs_number"],
            twot_number=entry["twot_number"],
        )
    )
