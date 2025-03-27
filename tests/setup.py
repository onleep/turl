from datetime import datetime, timedelta

import fakeredis
import pytest
from api.main import app
from fastapi.testclient import TestClient
from peewee import (
    SQL,
    AutoField,
    CharField,
    DateTimeField,
    IntegerField,
    Model,
    SqliteDatabase,
)

tempdb = SqliteDatabase('file::memory:?cache=shared')


class BaseModel(Model):

    class Meta:
        database = tempdb


class Links(BaseModel):
    id = AutoField()
    turl = CharField(index=True, null=True, unique=True, default=None)
    url = CharField()
    token = CharField()
    stats = IntegerField(constraints=[SQL("DEFAULT 0")])
    onetime = IntegerField(constraints=[SQL("DEFAULT 0")])
    expired_at = DateTimeField(index=True, null=True, default=None)
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    updated_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])


class Database:
    links = Links


expired_at = datetime.now() + timedelta(days=7)


@pytest.fixture()
def DB():
    tempdb.connect()
    tempdb.create_tables([Links])

    Database.links.create(
        turl='nmuiP',
        url='https://google.com',
        token='4c4f7476d203dd4151eefd5ffcf6b59f',
        stats=2,
        onetime=0,
        expired_at=expired_at,
    )

    yield Database

    tempdb.drop_tables([Links])
    tempdb.close()


@pytest.fixture()
def redis():
    redis = fakeredis.FakeRedis()

    mapping = {'url': 'https://google.com', 'onetime': 0}
    redis.hset(f'turl:nmuiP', mapping=mapping)
    expire = int(expired_at.timestamp())
    redis.expire(f"turl:nmuiP", expire)

    yield redis

    redis.flushdb()
    redis.close()


client = TestClient(app)
