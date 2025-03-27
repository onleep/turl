from unittest.mock import patch

from Dotenv import env
from setup import DB, client, redis

domain = env.get('URL_IP')


def test_delete(DB, redis):
    outrow = DB.links.select().first()

    turl = f'{domain}/{outrow.turl}'
    fakeurl = f'{domain}/tfake'
    params = {'turl': turl, 'token': outrow.token}
    fparams = {'turl': fakeurl, 'token': '2ee0227bcfd7ac0d68716a3a966f4ca2'}
    with patch.multiple('api.main', DB=DB, redis=redis):
        response = client.request('DELETE', '/links/shorten', json=params)
        error = client.request('DELETE', '/links/shorten', json=fparams)

    # response
    assert response.status_code == 200
    assert response.json()['data'] == f'turl {outrow.turl} has been deleted'
    assert error.status_code == 404
    assert error.json()['detail'] == f'Turl does not exist'

    # db
    assert DB.links.select().count() == 1
    row = DB.links.select().first()
    assert row != None
    assert row.turl == None
    assert row.url == outrow.url
    assert row.token == outrow.token
    assert row.stats == outrow.stats
    assert row.onetime == outrow.onetime
    assert row.expired_at == outrow.expired_at

    # redis
    assert sum(1 for _ in redis.scan_iter("turl:*")) == 0
