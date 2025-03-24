import time

from Dotenv import env
from logger import logging
from peewee import (
    SQL,
    AutoField,
    CharField,
    DateTimeField,
    IntegerField,
    Model,
    MySQLDatabase,
)

DBNAME = env.get('DB_NAME')
LOGIN = env.get('DB_LOGIN')
PASS = env.get('DB_PASS')
IP = env.get('DB_IP')
PORT = 3306

db = MySQLDatabase(DBNAME, user=LOGIN, password=PASS, host=IP, port=PORT)


class BaseModel(Model):

    class Meta:
        database = db


class Links(BaseModel):
    id = AutoField()
    turl = CharField(index=True, null=True, unique=True, default=None)
    url = CharField()
    token = CharField()
    stats = IntegerField(constraints=[SQL("DEFAULT 0")])
    onetime = IntegerField(constraints=[SQL("DEFAULT 0")])
    expired_at = DateTimeField(index=True, null=True, default=None)
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    updated_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')])


class DB:
    links = Links


def initdb():
    for _ in range(5):
        try: 
            db.create_tables([Links])
            break
        except: 
            logging.error('initdb failed')
            time.sleep(5)
