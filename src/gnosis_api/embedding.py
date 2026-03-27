from __future__ import annotations

from typing import TYPE_CHECKING

from gnosis_api.config import settings

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer
    from usearch.index import Index

_model: SentenceTransformer | None = None
_index: Index | None = None


def load_model_and_index() -> None:
    get_model()
    get_index()


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def get_index() -> Index:
    global _index
    if _index is None:
        from usearch.index import Index

        _index = Index.restore(str(settings.usearch_index_path))
    return _index
