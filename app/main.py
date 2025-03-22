import asyncio

from api.main import fastapi
from db.mysql import initdb
from sheduler.crontab import cron


async def main():
    await asyncio.gather(
        asyncio.to_thread(initdb),
        asyncio.to_thread(lambda: asyncio.run(cron())),
        asyncio.to_thread(lambda: asyncio.run(fastapi())),
    )


if __name__ == "__main__":
    asyncio.run(main())
