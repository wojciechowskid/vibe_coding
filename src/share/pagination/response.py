from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar('T')


class Pagination(BaseModel):
    count: int | None
    page: int
    limit: int


class Meta(BaseModel):
    pagination: Pagination


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: Meta

    @classmethod
    def factory(cls, items: list[T], page: int, limit: int, count: int | None = None) -> 'PaginatedResponse[T]':
        return cls(data=items, meta=Meta(pagination=Pagination(count=count, page=page, limit=limit)))
