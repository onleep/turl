from unittest.mock import patch

from Dotenv import env
from setup import DB, client, redis

domain = env.get('URL_IP')


def test_getinfo(DB, redis):
    outrow = DB.links.select().first()
    redttl = redis.ttl(f'turl:{outrow.turl}')
    turl = f'{domain}/{outrow.turl}'
    params = {'token': outrow.token}
    fparams = {'token': '2ee0227bcfd7ac0d68716a3a966f4ca2'}
    data = {}
    turl = f'{domain}/{outrow.turl}'
    data[turl] = {}
    data[turl]['url'] = outrow.url
    data[turl]['stats'] = outrow.stats
    data[turl]['onetime'] = outrow.onetime
    data[turl]['expired_at'] = outrow.expired_at.isoformat()
    data[turl]['created_at'] = outrow.created_at.isoformat()
    with patch.multiple('api.main', DB=DB, redis=redis):
        response = client.get('/links/info', params=params)
        error = client.get('/links/info', params=fparams)

    # response
    assert response.status_code == 200
    assert response.json() == {'data': data}
    assert error.status_code == 404
    assert error.json()['detail'] == 'Token does not exist'

    # db
    assert DB.links.select().count() == 1
    row = DB.links.select().first()
    assert row != None
    assert row.turl != None
    assert row.url == outrow.url
    assert row.turl == outrow.turl
    assert row.token == outrow.token
    assert row.stats == outrow.stats
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
