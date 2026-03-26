from fastapi import APIRouter, Depends, HTTPException

from gnosis_api.auth import require_api_key
from gnosis_api.db import get_gnosis_db
from gnosis_api.models import GreekLexiconEntryOut, SingleResponse

router = APIRouter(prefix="/v1/greek-lexicon", tags=["greek-lexicon"])


@router.get("/{strongs_number}", response_model=SingleResponse[GreekLexiconEntryOut])
async def get_greek_lexicon_entry(strongs_number: str, _auth: dict = Depends(require_api_key)):
    db = get_gnosis_db()
    row = await db.execute("SELECT * FROM greek_lexicon_entry WHERE strongs_number = ?", (strongs_number,))
    entry = await row.fetchone()
    if not entry:
        raise HTTPException(status_code=404, detail="Greek lexicon entry not found")

    return SingleResponse(
        data=GreekLexiconEntryOut(
            strongs_number=entry["strongs_number"],
            uuid=entry["uuid"],
            greek=entry["greek"],
            transliteration=entry["transliteration"],
            part_of_speech=entry["part_of_speech"],
            short_gloss=entry["short_gloss"],
            long_gloss=entry["long_gloss"],
            gk_number=entry["gk_number"],
        )
    )
