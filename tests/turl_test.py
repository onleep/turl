from unittest.mock import patch

from Dotenv import env
from setup import DB, client, redis
from datetime import datetime, timedelta
import time

domain = env.get('URL_IP')


def test_links_search(DB):
    with patch('api.main.DB', DB):
        response = client.get('/links/search', params={"url": "https://google.com"})

    assert response.status_code == 200
    assert response.json() == {"turl": f"{env.get('URL_IP')}/nmuiP"}


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
    with patch.multiple('api.main', DB=DB, redis=redis):
        response = client.post('/links/shorten', json=params)

    data = response.json()

    # response
    assert response.status_code == 200
    assert data['data']['token'] == params['token']
    assert data['data']['onetime'] == params['onetime']
    assert data['data']['expired_at'] == params['expired_at']

    # db
    assert DB.links.select().count() == 2
    row = DB.links.select().order_by(DB.links.id.desc()).first()
    assert row != None
    assert row.url == params['url']
    assert row.token == params['token']
    assert row.onetime == params['onetime']
    assert row.expired_at.strftime(f'%Y-%m-%d %H:%M:%S') == params['expired_at']

    # redis
    assert sum(1 for _ in redis.scan_iter("turl:*")) == 2
    redrow = redis.hgetall(f'turl:{row.turl}')
    assert redrow != None
    assert redrow[b'url'].decode() == params['url']
    assert redrow[b'onetime'].decode() == f"{int(params['onetime'])}"


def test_delete(DB, redis):
    outrow = DB.links.select().first()

    turl = f'{domain}/{outrow.turl}'
    params = {'turl': turl, 'token': outrow.token}
    with patch.multiple('api.main', DB=DB, redis=redis):
        response = client.request('DELETE', '/links/shorten', json=params)
    assert response.status_code == 200

    # db
    assert DB.links.select().count() == 1
    row = DB.links.select().first()
    assert row != None
    assert row.turl == None
    assert row.url == outrow.url
    assert row.token == row.token
    assert row.onetime == row.onetime
    assert row.expired_at == row.expired_at

    # redis
    assert sum(1 for _ in redis.scan_iter("turl:*")) == 0


def test_puturl(DB, redis):
    outrow = DB.links.select().first()
    redttl = redis.ttl(f'turl:{outrow.turl}')
    turl = f'{domain}/{outrow.turl}'
    params = {'turl': turl, 'token': outrow.token}
    with patch.multiple('api.main', DB=DB, redis=redis):
        response = client.put('/links/shorten', json=params)
    assert response.status_code == 200

    # db
    assert DB.links.select().count() == 1
    row = DB.links.select().first()
    assert row != None
    assert row.turl != None
    assert row.turl != outrow.turl
    assert row.url == outrow.url
    assert row.token == outrow.token
    assert row.onetime == outrow.onetime
    assert row.expired_at == outrow.expired_at

    # redis
    assert sum(1 for _ in redis.scan_iter("turl:*")) == 1
    redrow = redis.hgetall(f'turl:{row.turl}')
    assert redrow != None
    assert abs(redis.ttl(f'turl:{row.turl}') - redttl) < 5
    assert redrow[b'url'].decode() == outrow.url
    assert redrow[b'url'].decode() == outrow.url
    assert redrow[b'onetime'].decode() == f"{int(outrow.onetime)}"


def test_extendurl(DB, redis):
    outrow = DB.links.select().first()
    timennow = time.time()
    delta = timedelta(days=7)
    redttl = redis.ttl(f'turl:{outrow.turl}') + delta.total_seconds()
    turl = f'{domain}/{outrow.turl}'
    expired_at = outrow.expired_at.replace(microsecond=0) + delta
    format_date = expired_at.strftime(f'%Y-%m-%d %H:%M:%S')
    params = {'turl': turl, 'token': outrow.token, 'expired_at': format_date}
    with patch.multiple('api.main', DB=DB, redis=redis):
        response = client.put('/links/extend', json=params)
    assert response.status_code == 200

    # db
    assert DB.links.select().count() == 1
    row = DB.links.select().first()
    assert row != None
    assert row.turl != None
    assert row.turl == outrow.turl
    assert row.url == outrow.url
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

