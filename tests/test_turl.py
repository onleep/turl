from datetime import datetime, timedelta
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest
from api.main import app
from Dotenv import env
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

tempdb = SqliteDatabase(":memory:")

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

class DB:
    links = Links

@pytest.fixture(scope="function")
def db_session():
    tempdb.connect()
    tempdb.create_tables([Links])

    yield DB

    tempdb.drop_tables([Links])
    tempdb.close()

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

def test_create_link(client, db_session):
    expired = datetime.now() + timedelta(days=7)
    link = DB.links.create(
        turl='nmuiP',
        url='https://google.com',
        token='4c4f7476d203dd4151eefd5ffcf6b59f',
        stats=2,
        onetime=0,
        expired_at=expired,
    )

    assert link.id is not None
    assert link.turl == 'nmuiP'
    assert link.url == 'https://google.com'
    assert link.token == '4c4f7476d203dd4151eefd5ffcf6b59f'
    assert link.onetime == 0
    assert link.expired_at == expired

    mock_db = MagicMock()
    mock_links = MagicMock()

    mock_db.links = mock_links
    mock_links.get_or_none.return_value = MagicMock(turl="nmuiP", url="https://google.com")

    with patch('api.main.DB', mock_db):
        response = client.get('/links/search', params={"url": "https://google.com"})

    assert response.status_code == 200
    assert response.json() == {"turl": f"{env.get('URL_IP')}/nmuiP"}
