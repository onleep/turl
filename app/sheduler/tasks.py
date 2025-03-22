from db.mysql import DB
from logger import logging
from peewee import SQL


def clear_expired():
    count = DB.links.update(turl=None).where(SQL('expired_at < NOW()')).execute()
    logging.info(f"Expired turl cleaned: {count or 0}")
