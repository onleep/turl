import time
from datetime import timedelta
from unittest.mock import patch

from Dotenv import env
from setup import DB, client, redis

domain = env.get('URL_IP')


def test_extendurl(DB, redis):
    outrow = DB.links.select().first()
    delta = timedelta(days=7)
    expired_at = outrow.expired_at.replace(microsecond=0) + delta
    format_date = expired_at.strftime(f'%Y-%m-%d %H:%M:%S')
    token = outrow.token
    timennow = time.time()
    exp = outrow.expired_at
    fturl = f'{domain}/fturl'
    turl = f'{domain}/{outrow.turl}'
    redttl = redis.ttl(f'turl:{outrow.turl}') + delta.total_seconds()

    params = {'turl': turl, 'token': token, 'expired_at': format_date}
    fparams0 = {'turl': fturl, 'token': token, 'expired_at': format_date}
    fparams1 = {'turl': turl, 'token': token, 'expired_at': '2025-04-32 18:58:00'}
    fparams2 = {'turl': turl, 'token': token, 'expired_at': '2024-04-20 18:58:00'}
    data = {
        'turl': params['turl'],
        'expired_at': params['expired_at'],
        'token': params['token'],
        'onetime': outrow.onetime,
    }
    with patch.multiple('api.main', DB=DB, redis=redis):
        error0 = client.put('/links/extend', json=fparams0)
        error1 = client.put('/links/extend', json=fparams1)
        error2 = client.put('/links/extend', json=fparams2)
        response = client.put('/links/extend', json=params)

    # response
    assert response.status_code == 200
    assert response.json()['data'] == data
    assert error0.status_code == 404
    assert error0.json()['detail'] == 'Turl fturl does not exist'
    assert error1.status_code == 404
    assert error1.json()['detail'] == 'Invalid date'
    assert error2.status_code == 404
    assert error2.json()['detail'] == f'Mintime is 1+ days. Current expired: {exp}'

    # db
    assert DB.links.select().count() == 1
    row = DB.links.select().first()
    assert row != None
    assert row.turl != None
    assert row.url == outrow.url
    assert row.turl == outrow.turl
    assert row.stats == outrow.stats
    assert row.token == outrow.token
    assert row.onetime == outrow.onetime
    assert row.expired_at == expired_at

    # redis
    assert sum(1 for _ in redis.scan_iter("turl:*")) == 1
    redrow = redis.hgetall(f'turl:{row.turl}')
    assert redrow != None
    newttl = redis.ttl(f'turl:{row.turl}') + timennow
    assert abs(int(newttl) - int(redttl)) < 5
    assert redrow[b'url'].decode() == outrow.url
    assert redrow[b'onetime'].decode() == f"{int(outrow.onetime)}"
