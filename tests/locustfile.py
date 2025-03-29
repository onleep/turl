import asyncio
import threading
import time
from datetime import datetime, timedelta
from unittest.mock import patch

import fakeredis
import uvicorn
from api.main import app
from locust import HttpUser, between, events, task
from setup import Database, Links, tempdb


class PostUrlUser(HttpUser):
    host = "http://localhost:8001"
    wait_time = between(1, 2)

    def on_start(self):
        expired_at = datetime.now() + timedelta(days=14)
        self.format_date = expired_at.strftime(f'%Y-%m-%d %H:%M:%S')

    @task
    def post_url(self):
        params = {
            'url': 'https://google.com',
            'onetime': True,
        }
        self.client.post("/links/shorten", json=params)

        with self.client.post("/links/shorten", json=params) as response:
            if response.status_code == 200: print(f"✅ {response.text}")
            else: print(f"❌ {response.status_code}, Ответ: {response.text}")


@events.test_start.add_listener
def start_fastapi_server(environment, **kwargs):
    threading.Thread(target=run_fastapi).start()
    time.sleep(5)


def run_fastapi():
    tempdb.connect()
    tempdb.create_tables([Links])
    DB = Database()
    redis = fakeredis.FakeRedis()

    with patch.multiple('api.main', DB=DB, redis=redis):
        config = uvicorn.Config(app, port=8001, log_level='critical')
        asyncio.run(uvicorn.Server(config).serve())
