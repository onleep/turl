import time
from datetime import datetime, timedelta
from unittest.mock import patch

from Dotenv import env
from setup import DB, client, redis

domain = env.get('URL_IP')


def test_posturl(DB, redis):
    expired_at = datetime.now() + timedelta(days=14)
    format_date = expired_at.strftime(f'%Y-%m-%d %H:%M:%S')
    params = {
        'url': 'https://google.com',
        'token': '819684eb601ea10c29ee74f09d99b216',
        'expired_at': format_date,
        'custom_alias': 'hellow',
        'onetime': True,
    }
    fparams = {
        'url': 'https://google.com',
        'token': '819684eb601ea10c29ee74f09d99b216',
        'expired_at': '2025-04-32 18:58:00',
        'custom_alias': 'hellow',
        'onetime': True,
    }
    with patch.multiple('api.main', DB=DB, redis=redis):
        response = client.post('/links/shorten', json=params)
        error = client.post('/links/shorten', json=fparams)

    # response
    data = response.json()
    assert response.status_code == 200
    assert data['data']['token'] == params['token']
    assert data['data']['onetime'] == params['onetime']
    assert data['data']['expired_at'] == params['expired_at']
    assert error.json()['detail'] == 'Invalid date'

    # db
    assert DB.links.select().count() == 2
    row = DB.links.select().order_by(DB.links.id.desc()).first()
    assert row != None
    assert row.stats == 0
    assert row.url == params['url']
    assert row.token == params['token']
    assert row.onetime == params['onetime']
    assert row.expired_at.strftime(f'%Y-%m-%d %H:%M:%S') == params['expired_at']

    # redis
    assert sum(1 for _ in redis.scan_iter("turl:*")) == 2
    redrow = redis.hgetall(f'turl:{row.turl}')
    assert redrow != None
    assert redrow[b'url'].decode() == params['url']
    newttl = expired_at.timestamp() - time.time()
    assert abs(redis.ttl(f'turl:{row.turl}') - newttl) < 5
    assert redrow[b'onetime'].decode() == f"{int(params['onetime'])}"
