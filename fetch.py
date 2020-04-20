import re
from urllib.parse import urlencode

import requests

def query_tweets(username, bearer, tweet_count=10):
    query = "https://api.twitter.com/1.1/statuses/user_timeline.json?count=20"
    headers = {"Authorization": f"Bearer {bearer}"}
    data = {"screen_name": username, "count": tweet_count, "include_rts": "false"}
    response = requests.get(query, params=urlencode(data), headers=headers)
    return response.json()

def retrieve_status_tweets(username, tweets):
    status_tweets = []
    for tweet in tweets:
        text = tweet.get('text')
        user_mentions = retrieve_user_mentions(tweet)
        hashtags = retrieve_hashtags(tweet)
        if contains_user_mentions(username, user_mentions) and validate_hashtags(text):
            status_tweets.append(clean_text(text))
    return status_tweets

def clean_text(text):
    cleaned_text = re.sub(r'^\S*', "", text)
    return re.sub(r"[\D\s]#status", "", cleaned_text).strip()

def contains_user_mentions(username, user_mentions):
    return user_mentions and len(user_mentions) == 1 and username in user_mentions

def validate_hashtags(text):
    return len(re.findall(r"#\S+$", text)) == 1

def retrieve_user_mentions(tweet):
    user_mentions = tweet.get("entities").get("user_mentions")
    if user_mentions:
        return [user_mention.get("screen_name") for user_mention in user_mentions]
    return None

def retrieve_hashtags(tweet):
    hashtags = tweet.get("entities").get("hashtags")
    if hashtags:
        return [hashtag.get("text") for hashtag in hashtags]
    return None
