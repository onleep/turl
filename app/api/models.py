from pydantic import BaseModel, Field


class GenTurl(BaseModel):
    url: str = Field(pattern=r'\b\w+://[^\s]+\b')
    custom_alias: str | None = Field(default=None, pattern=r'^[a-zA-Z0-9]{6,10}$')
    expired_at: str | None = Field(default=None, pattern=r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$')
    onetime: bool = False


class ReqTurl(BaseModel):
    turl: str
    token: str
    expired_at: str
    

class PostTurl(BaseModel):
    data: ReqTurl
    info: dict


# class Turl(BaseModel):
#     turl: str = Field(pattern=r'^[a-zA-Z0-9]{5,10}$')


class Url(BaseModel):
    url: str = Field(pattern=r'\b\w+://[^\s]+\b')


class Stats(BaseModel):
    url: str
    stats: int
    expired_at: str
    created_at: str
    updated_at: str


class GetStats(BaseModel):
    stats: Stats


class TurlFull(BaseModel):
    turl: str = Field(pattern=r'^(https?://)?[\w.-]+(?::\d+)?/[\w]{5,10}$')


class VerifyUser(BaseModel):
    turl: str = Field(pattern=r'^(https?://)?[\w.-]+(?::\d+)?/[\w]{5,10}$')
    token: str
