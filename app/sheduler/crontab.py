import asyncio

from aiocron import crontab

from .tasks import clear_expired


async def cron():
    crontab('*/10 * * * *', func=clear_expired)  # 10 mins

    await asyncio.Event().wait()
