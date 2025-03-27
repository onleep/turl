from unittest.mock import patch

from Dotenv import env
from setup import DB, client, redis

domain = env.get('URL_IP')


def test_getstats(DB, redis):
    outrow = DB.links.select().first()
    redttl = redis.ttl(f'turl:{outrow.turl}')
    stats = {
        'url': outrow.url,
        'stats': outrow.stats,
        'expired_at': str(outrow.expired_at.replace(microsecond=0)),
        'created_at': str(outrow.created_at.replace(microsecond=0)),
        'updated_at': str(outrow.updated_at.replace(microsecond=0)),
    }
    with patch.multiple('api.main', DB=DB, redis=redis):
        response = client.get(f'/{outrow.turl}/stats')
        error = client.get('/fakeurl/stats')

    # response
    assert response.status_code == 200
    assert response.json() == {'data': stats}
    assert error.status_code == 404
    assert error.json()['detail'] == 'Turl fakeurl does not exist'

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
