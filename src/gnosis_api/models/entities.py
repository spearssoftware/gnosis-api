from pydantic import BaseModel


class PersonOut(BaseModel):
    slug: str
    uuid: str
    name: str
    gender: str | None = None
    birth_year: int | None = None
    death_year: int | None = None
    birth_year_display: str | None = None
    death_year_display: str | None = None
    earliest_year_mentioned: int | None = None
    latest_year_mentioned: int | None = None
    earliest_year_mentioned_display: str | None = None
    latest_year_mentioned_display: str | None = None
    birth_place: str | None = None
    death_place: str | None = None
    father: str | None = None
    mother: str | None = None
    siblings: list[str] = []
    children: list[str] = []
    partners: list[str] = []
    verse_count: int = 0
    verses: list[str] = []
    first_mention: str | None = None
    name_meaning: str | None = None
    people_groups: list[str] = []


class PlaceOut(BaseModel):
    slug: str
    uuid: str
    name: str
    kjv_name: str | None = None
    esv_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    coordinate_source: str | None = None
    feature_type: str | None = None
    feature_sub_type: str | None = None
    modern_name: str | None = None


class EventOut(BaseModel):
    slug: str
    uuid: str
    title: str
    start_year: int | None = None
    start_year_display: str | None = None
    duration: str | None = None
    sort_key: float | None = None
    participants: list[str] = []
    locations: list[str] = []
    verses: list[str] = []
    parent_event: str | None = None
    predecessor: str | None = None


class PeopleGroupOut(BaseModel):
    slug: str
    uuid: str
    name: str
    members: list[str] = []


class VerseEntitiesOut(BaseModel):
    osis_ref: str
    people: list[str] = []
    places: list[str] = []
    events: list[str] = []
    topics: list[str] = []


class CrossReferenceOut(BaseModel):
    from_verse: str
    to_verse_start: str
    to_verse_end: str | None = None
    votes: int = 0


class StrongsEntryOut(BaseModel):
    number: str
    uuid: str
    language: str
    lemma: str | None = None
    transliteration: str | None = None
    pronunciation: str | None = None
    definition: str | None = None
    kjv_usage: str | None = None


class DictionaryDefinitionOut(BaseModel):
    source: str
    text: str


class DictionaryEntryOut(BaseModel):
    slug: str
    uuid: str
    name: str
    definitions: list[DictionaryDefinitionOut] = []
    scripture_refs: list[str] = []


class TopicAspectOut(BaseModel):
    label: str | None = None
    source: str | None = None
    verses: list[str] = []


class TopicOut(BaseModel):
    slug: str
    uuid: str
    name: str
    aspects: list[TopicAspectOut] = []
    see_also: list[str] = []


class HebrewWordOut(BaseModel):
    word_id: str
    position: int
    text: str
    lemma_raw: str
    strongs_number: str | None = None
    morph: str


class GreekWordOut(BaseModel):
    word_id: str
    position: int
    text: str
    lemma: str
    strongs_number: str | None = None
    morph: str


class LexiconEntryOut(BaseModel):
    lexical_id: str
    uuid: str
    hebrew: str
    transliteration: str | None = None
    part_of_speech: str | None = None
    gloss: str | None = None
    strongs_number: str | None = None
    twot_number: str | None = None


class GreekLexiconEntryOut(BaseModel):
    strongs_number: str
    uuid: str
    greek: str
    transliteration: str | None = None
    part_of_speech: str | None = None
    short_gloss: str | None = None
    long_gloss: str | None = None
    gk_number: str | None = None


class SearchResultOut(BaseModel):
    slug: str
    name: str
    entity_type: str
    uuid: str


class SemanticSearchResultOut(BaseModel):
    slug: str
    type: str
    text: str
    score: float
