from pydantic import BaseModel, Field


class URL(BaseModel):
    url: str = Field(pattern=r'^(?:https?://)?[a-zA-Z0-9\-]{4,}\.[a-zA-Z0-9]{2,}$')
    expired_at: str | None = Field(default=None, pattern=r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$')
    custom_alias: str | None = None

class Turl(BaseModel):
    turl: str
    token: str
    expired_at: str

class PostTurl(BaseModel):
    data: Turl

class VerifyUser(BaseModel):
    turl: str
    token: str

class Stats(BaseModel):
    url: str
    stats: int
    created_at: str
    expired_at: str
    created_at: str
    updated_at: str

class GetStats(BaseModel):
    stats: Stats

