from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class DataList(BaseModel, Generic[T]):
    data: list[T]


class ScrapingBeeReponse(BaseModel, Generic[T]):
    body: DataList[T]
    headers: dict[str, str]


class RedditCommunity(BaseModel):
    name: str
    summary: str
    href: str
    members: int | str | None = None
    online: int | str | None = None


class RedditCommunityPost(BaseModel):
    title: str
    href: str
    summary: str
    author: str | None = None


class RedditSearchResult(BaseModel):
    title: str
    href: str
