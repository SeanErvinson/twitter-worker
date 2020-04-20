import os
import json

from celery.schedules import crontab
from celery import Celery
import redis
from twitter_worker.fetch import query_tweets, retrieve_status_tweets

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1")
BEARER_TOKEN = os.getenv("BEARER_TOKEN", None)
USERNAME = os.getenv("USERNAME", "ASean___")

redis_db = redis.from_url(REDIS_URL)
celery = Celery(__name__,broker=REDIS_URL)

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
