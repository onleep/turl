from datetime import datetime, timedelta

import uvicorn
from api.model import URL, PostTurl, VerifyUser, GetStats
from api.tools import gentoken, genturl
from db.main import DB
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from Dotenv import env

app = FastAPI()
router = APIRouter()
domain = env.get('URL_IP') or 'local'


@router.post('/shorten', response_model=PostTurl)
async def posturl(req: URL):
    turl = genturl()
    token = gentoken()
    expired = datetime.now() + timedelta(days=7, hours=3)
    DB.links.create(turl=turl, url=req.url, token=token, expired_at=expired)

    turl = f'{domain}/shorten/{turl}'
    expired_at = expired.strftime(f'%Y-%m-%d %H:%M:%S')
    response = {'turl': turl, 'token': token, 'expired_at': expired_at}
    return {'data': response}


@router.get('/shorten/{short_code}')
async def geturl(short_code: str):
    data = DB.links.get_or_none(DB.links.turl == short_code)
    if not data:
        raise HTTPException(status_code=404, detail="turl does not exist")
    DB.links.update(stats=DB.links.stats + 1).where(DB.links.id == data.id).execute()
    return RedirectResponse(url=data.url)


@router.delete('/shorten', response_model=dict)
async def deleteurl(req: VerifyUser):
    data = DB.links.get_or_none(DB.links.turl == req.turl)
    if not data or data.token != req.token:
        raise HTTPException(status_code=404, detail='turl does not exist')
    DB.links.update(turl=None).where(DB.links.id == data.id).execute()
    return {'data': 'turl has been deleted'}


@router.put('/shorten', response_model=dict)
async def puturl(req: VerifyUser):
    data = DB.links.get_or_none(DB.links.turl == req.turl)
    if not data or data.token != req.token:
        raise HTTPException(status_code=404, detail='turl does not exist')
    turl = genturl()
    DB.links.update(turl=turl).where(DB.links.id == data.id).execute()
    turl = f'{domain}/shorten/{turl}'
    return {'turl': turl}


@router.get('/shorten/{short_code}/stats', response_model=GetStats)
async def getstats(short_code: str):
    data = DB.links.get_or_none(DB.links.turl == short_code)
    if not data:
        raise HTTPException(status_code=404, detail="turl does not exist")
    stats = {
        'url': data.url,
        'stats': data.stats,
        'expired_at': str(data.expired_at),
        'created_at': str(data.created_at),
        'updated_at': str(data.updated_at),
    }
    return {'stats': stats}


app.include_router(router, prefix='/links')


async def fastapi():
    config = uvicorn.Config(app, host='0.0.0.0', log_config=None)
    await uvicorn.Server(config).serve()
