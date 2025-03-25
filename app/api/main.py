import re
from datetime import datetime, timedelta

import uvicorn
from db.mysql import DB
from db.redis import redis
from Dotenv import env
from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse

from .models import GenTurl, GetStats, PostTurl, TurlFull, VerifyUser
from .tools import gentoken, genturl

app = FastAPI()
router = APIRouter()
domain = env.get('URL_IP')


@router.post('/shorten', response_model=PostTurl)
async def posturl(req: GenTurl):
    info = {}
    datenow = datetime.now()
    expired = datenow + timedelta(days=7)
    if cstm := req.expired_at:
        texpiried = datetime.strptime(cstm, f'%Y-%m-%d %H:%M')
        if texpiried > datenow: expired = texpiried
        else: info['expired_at'] = 'Mintime is 1 day'
    if cstm and expired > (maxtime := datenow + timedelta(days=30)):
        info['expired_at'] = 'Maxtime is 30 days'
        expired = maxtime
    turl = req.custom_alias
    if not turl or DB.links.get_or_none(DB.links.turl == turl):
        if turl: info['custom_alias'] = f'Turl {turl} already exist'
        turl = genturl()
    token = req.token if req.token else gentoken()
    DB.links.create(
        turl=turl,
        url=req.url,
        token=token,
        expired_at=expired,
        onetime=req.onetime,
    )
    mapping = {'url': req.url, 'onetime': int(req.onetime)}
    redis.hset(f"turl:{turl}", mapping=mapping)
    expire = int((expired - datenow).total_seconds())
    redis.expire(f"turl:{turl}", expire)
    turl = f'{domain}/{turl}'
    expired_at = expired.strftime(f'%Y-%m-%d %H:%M:%S')
    response = {
        'turl': turl,
        'token': token,
        'expired_at': expired_at,
        'onetime': req.onetime,
    }
    return {'data': response, 'info': info}


@router.delete('/shorten', response_model=dict)
async def deleteurl(req: VerifyUser):
    turl = req.turl.split('/')[-1]
    data = DB.links.get_or_none(DB.links.turl == turl)
    if not data or data.token != req.token:
        raise HTTPException(status_code=404, detail='Turl does not exist')
    redis.delete(f"turl:{turl}")
    DB.links.update(turl=None).where(DB.links.id == data.id).execute()
    return {'data': f'turl {turl} has been deleted'}


@router.put('/shorten', response_model=dict)
async def puturl(req: VerifyUser):
    turl = req.turl.split('/')[-1]
    data = DB.links.get_or_none(DB.links.turl == turl)
    if not data or data.token != req.token:
        message = f'Turl {turl} does not exist'
        raise HTTPException(status_code=404, detail=message)
    newturl = genturl()
    redis.renamenx(f'turl:{turl}', f'turl:{newturl}')
    DB.links.update(turl=newturl).where(DB.links.id == data.id).execute()
    turl = f'{domain}/{newturl}'
    return {'turl': turl}


@router.get('/search', response_model=TurlFull)
async def searchurl(url: str = Query(regex=r'\b\w+://[^\s]+\b')):
    data = DB.links.get_or_none(DB.links.url == url, DB.links.turl != None)
    if not data:
        raise HTTPException(status_code=404, detail='Turl does not exist')
    turl = f'{domain}/{data.turl}'
    return {'turl': turl}


@router.get('/info', response_model=dict)
async def getinfo(token: str = Query(regex=r'^[a-f0-9]{32}$')):
    rows = DB.links.select().where(DB.links.token == token)
    if not rows:
        raise HTTPException(status_code=404, detail='Token does not exist')
    data = {}
    for row in rows:
        turl = f'{domain}/{row.turl}'
        data[turl] = {}
        data[turl]['url'] = row.url
        data[turl]['stats'] = row.stats
        data[turl]['onetime'] = row.onetime
        data[turl]['expired_at'] = row.expired_at
        data[turl]['created_at'] = row.created_at
    return {'data': data}


@app.get('/{turl}')
async def geturl(turl: str, hide: bool | None = None):
    pattern = r'^[a-zA-Z0-9]{5,10}$'
    match = re.match(pattern, turl)
    if not match or not (url := redis.hget(f'turl:{turl}', 'url')):
        raise HTTPException(status_code=404, detail=f'Turl {turl} does not exist')
    if hide: return RedirectResponse(str(url))
    onetime = redis.hget(f'turl:{turl}', 'onetime')
    stats = DB.links.stats + 1
    updturl = None if onetime == '1' else turl
    if not updturl: redis.delete(f"turl:{turl}")
    DB.links.update(turl=updturl, stats=stats).where(DB.links.turl == turl).execute()
    return RedirectResponse(str(url))


@app.get('/{turl}/stats', response_model=GetStats)
async def getstats(turl: str):
    pattern = r'^[a-zA-Z0-9]{5,10}$'
    match = re.match(pattern, turl)
    if not match or not (data := DB.links.get_or_none(DB.links.turl == turl)):
        raise HTTPException(status_code=404, detail=f'Turl {turl} does not exist')
    stats = {
        'url': data.url,
        'stats': data.stats,
        'expired_at': str(data.expired_at),
        'created_at': str(data.created_at),
        'updated_at': str(data.updated_at),
    }
    return {'data': stats}


app.include_router(router, prefix='/links')


async def fastapi():
    config = uvicorn.Config(app, host='0.0.0.0', log_config=None)
    await uvicorn.Server(config).serve()
