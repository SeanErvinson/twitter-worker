import os
import json

from celery.schedules import crontab
from celery import Celery
import redis
from fetch import query_tweets, retrieve_status_tweets

DEBUG = bool(int(os.getenv("DEBUG", 0)))
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", 6379)
DB_NUMBER = os.environ.get("DB_NUMBER", 1)
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

REDIS_URL = (
    f"redis://{DB_HOST}:{DB_PORT}/{DB_NUMBER}"
    if DEBUG
    else f"redis://:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NUMBER}"
)
BEARER_TOKEN = os.getenv("BEARER_TOKEN", None)
USERNAME = os.getenv("USERNAME", "ASean___")

redis_db = redis.from_url(REDIS_URL)
celery = Celery(__name__,broker=REDIS_URL)
celery.conf.broker_url = REDIS_URL
celery.conf.result_backend = REDIS_URL

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=10, day_of_week=0),
        fetch_tweets.s()
    )

@celery.task
def fetch_tweets():
    tweets = query_tweets(USERNAME, BEARER_TOKEN)
    status_tweets = retrieve_status_tweets(USERNAME, tweets)
    redis_db.set("status_tweets", json.dumps(status_tweets[:3]))
