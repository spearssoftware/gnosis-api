from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ListMeta(BaseModel):
    total: int
    limit: int
    offset: int


class ListResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: ListMeta


class SingleResponse(BaseModel, Generic[T]):
    data: T
