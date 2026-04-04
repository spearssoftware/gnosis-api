from .common import CamelModel


class PersonOut(CamelModel):
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


class PlaceOut(CamelModel):
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


class EventOut(CamelModel):
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


class PeopleGroupOut(CamelModel):
    slug: str
    uuid: str
    name: str
    members: list[str] = []


class VerseEntitiesOut(CamelModel):
    osis_ref: str
    people: list[str] = []
    places: list[str] = []
    events: list[str] = []
    topics: list[str] = []


class CrossReferenceOut(CamelModel):
    from_verse: str
    to_verse_start: str
    to_verse_end: str | None = None
    votes: int = 0


class StrongsEntryOut(CamelModel):
    number: str
    uuid: str
    language: str
    lemma: str | None = None
    transliteration: str | None = None
    pronunciation: str | None = None
    definition: str | None = None
    kjv_usage: str | None = None


class DictionaryDefinitionOut(CamelModel):
    source: str
    text: str


class DictionaryEntryOut(CamelModel):
    slug: str
    uuid: str
    name: str
    definitions: list[DictionaryDefinitionOut] = []
    scripture_refs: list[str] = []


class TopicAspectOut(CamelModel):
    label: str | None = None
    source: str | None = None
    verses: list[str] = []


class TopicOut(CamelModel):
    slug: str
    uuid: str
    name: str
    aspects: list[TopicAspectOut] = []
    see_also: list[str] = []


class HebrewWordOut(CamelModel):
    word_id: str
    position: int
    text: str
    lemma_raw: str
    strongs_number: str | None = None
    morph: str


class GreekWordOut(CamelModel):
    word_id: str
    position: int
    text: str
    lemma: str
    strongs_number: str | None = None
    morph: str


class LexiconEntryOut(CamelModel):
    lexical_id: str
    uuid: str
    hebrew: str
    transliteration: str | None = None
    part_of_speech: str | None = None
    gloss: str | None = None
    strongs_number: str | None = None
    twot_number: str | None = None


class GreekLexiconEntryOut(CamelModel):
    strongs_number: str
    uuid: str
    greek: str
    transliteration: str | None = None
    part_of_speech: str | None = None
    short_gloss: str | None = None
    long_gloss: str | None = None
    gk_number: str | None = None


class SearchResultOut(CamelModel):
    slug: str
    name: str
    entity_type: str
    uuid: str


class SemanticSearchResultOut(CamelModel):
    slug: str
    type: str
    text: str
    score: float


class ChapterEntitiesOut(CamelModel):
    book: str
    chapter: int
    people: list[str] = []
    places: list[str] = []
    events: list[str] = []
    topics: list[str] = []
