from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

T = TypeVar("T")


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class ListMeta(CamelModel):
    total: int
    limit: int
    offset: int


class ListResponse(CamelModel, Generic[T]):
    data: list[T]
    meta: ListMeta


class SingleResponse(CamelModel, Generic[T]):
    data: T
