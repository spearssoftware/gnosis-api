from fastapi import APIRouter, Depends, HTTPException

from gnosis_api.auth import require_api_key
from gnosis_api.db import get_gnosis_db
from gnosis_api.models import SingleResponse, StrongsEntryOut

router = APIRouter(prefix="/v1/strongs", tags=["strongs"])


@router.get("/{number}", response_model=SingleResponse[StrongsEntryOut])
async def get_strongs(number: str, _auth: dict = Depends(require_api_key)):
    db = get_gnosis_db()
    row = await db.execute("SELECT * FROM strongs WHERE number = ?", (number,))
    entry = await row.fetchone()
    if not entry:
        raise HTTPException(status_code=404, detail="Strong's entry not found")

    return SingleResponse(
        data=StrongsEntryOut(
            number=entry["number"],
            uuid=entry["uuid"],
            language=entry["language"],
            lemma=entry["lemma"],
            transliteration=entry["transliteration"],
            pronunciation=entry["pronunciation"],
            definition=entry["definition"],
            kjv_usage=entry["kjv_usage"],
        )
    )
