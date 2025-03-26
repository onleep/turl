from pydantic import BaseModel, Field


class GenTurl(BaseModel):
    url: str = Field(pattern=r'\b\w+://[^\s]+\b')
    custom_alias: str | None = Field(default=None, pattern=r'^[a-zA-Z0-9]{6,10}$')
    expired_at: str | None = Field(default=None, pattern=r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$')
    token: str | None = Field(default=None, pattern=r'^[a-f0-9]{32}$')
    onetime: bool = False


class ReqTurl(BaseModel):
    turl: str = Field(pattern=r'^(https?://)?[\w.-]+(?::\d+)?/[\w]{5,10}$')
    token: str = Field(pattern=r'^[a-f0-9]{32}$')
    expired_at: str = Field( pattern=r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$')


class PostTurl(BaseModel):
    data: ReqTurl
    info: dict

class Stats(BaseModel):
    stats: int
    url: str = Field(pattern=r'\b\w+://[^\s]+\b')
    expired_at: str = Field( pattern=r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$')
    created_at: str = Field( pattern=r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$')
    updated_at: str = Field( pattern=r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$')


class GetStats(BaseModel):
    data: Stats


class TurlFull(BaseModel):
    turl: str = Field(pattern=r'^(https?://)?[\w.-]+(?::\d+)?/[\w]{5,10}$')


class VerifyUser(BaseModel):
    turl: str = Field(pattern=r'^(https?://)?[\w.-]+(?::\d+)?/[\w]{5,10}$')
    token: str = Field(pattern=r'^[a-f0-9]{32}$')
