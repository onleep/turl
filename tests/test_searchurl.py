from unittest.mock import patch

from Dotenv import env
from setup import DB, client, redis

domain = env.get('URL_IP')


def test_searchurl(DB, redis):
    outrow = DB.links.select().first()
    redttl = redis.ttl(f'turl:{outrow.turl}')
    turl = f'{domain}/{outrow.turl}'
    params = {'url': outrow.url}
    fparams = {'url': 'https://fake.url'}
    with patch.multiple('api.main', DB=DB, redis=redis):
        response = client.get('/links/search', params=params)
        error = client.get('/links/search', params=fparams)

    # response
    assert response.status_code == 200
    assert response.json() == {'turl': turl}
    assert error.status_code == 404
    assert error.json()['detail'] == 'Turl does not exist'

    # db
    assert DB.links.select().count() == 1
    row = DB.links.select().first()
    assert row != None
    assert row.turl != None
    assert row.turl == outrow.turl
    assert row.url == outrow.url
    assert row.token == outrow.token
    assert row.onetime == outrow.onetime
    assert row.expired_at == outrow.expired_at

    # redis
    assert sum(1 for _ in redis.scan_iter("turl:*")) == 1
    redrow = redis.hgetall(f'turl:{row.turl}')
    assert redrow != None
    newttl = redis.ttl(f'turl:{row.turl}')
    assert abs(int(newttl) - int(redttl)) < 5
    assert redrow[b'url'].decode() == outrow.url
    assert redrow[b'onetime'].decode() == f"{int(outrow.onetime)}"
