from pydantic import BaseModel, Field


class GenTurl(BaseModel):
    url: str = Field(pattern=r'\b\w+://[^\s]+\b')
    custom_alias: str | None = Field(default=None, pattern=r'^[a-zA-Z0-9]{6,10}$')
    expired_at: str | None = Field(default=None, pattern=r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$')
    token: str | None = Field(default=None, pattern=r'^[a-f0-9]{32}$')
    onetime: bool = False


class ReqTurl(BaseModel):
    turl: str
    token: str
    expired_at: str
    

class PostTurl(BaseModel):
    data: ReqTurl
    info: dict

class Stats(BaseModel):
    stats: int
    url: str
    expired_at: str
    created_at: str
    updated_at: str


class GetStats(BaseModel):
    data: Stats


class TurlFull(BaseModel):
    turl: str = Field(pattern=r'^(https?://)?[\w.-]+(?::\d+)?/[\w]{5,10}$')


class VerifyUser(BaseModel):
    turl: str = Field(pattern=r'^(https?://)?[\w.-]+(?::\d+)?/[\w]{5,10}$')
    token: str
