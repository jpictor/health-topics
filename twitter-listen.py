import os
import json
import tweepy
import pydash
import requests
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

class ApiConfig(object):
    def __init__(self):
        self.consumer_key = os.environ['TWITTER_CONSUMER_KEY']
        self.consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
        self.access_token = os.environ['TWITTER_ACCESS_TOKEN']
        self.access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
        print('{} {} {} {}'.format(self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret))

api_config = ApiConfig()
auth = tweepy.OAuthHandler(api_config.consumer_key, api_config.consumer_secret)
auth.set_access_token(api_config.access_token, api_config.access_token_secret)
api = tweepy.API(auth)

def content_hub_crawl(url):
    print('CRAWL-URL: {}'.format(url))
    resp = requests.post('{}/api/content-hub/crawl'.format(url), data={'url': url})
    doc = resp.json()
    return doc

class MyStreamListener(tweepy.StreamListener):
    def on_data(self, data):
        tweet = json.loads(data)
        tweet_id = tweet.get('id_str')
        text = tweet.get('text')
        hashtags = [x.get('text') for x in pydash.deep_get(tweet, 'entities.hashtags', [])]
        urls = list(filter(lambda x: bool(x), [x.get('expanded_url') for x in pydash.deep_get(tweet, 'entities.urls', [])]))
        print('{}: {}'.format(tweet_id, text))
        print(hashtags)
        print(urls)

        if urls:
            for url in urls:
                print('URL: {}'.format(url))
                content_hub_crawl(url)

    def on_status(self, status):
        print(status.text)

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
myStream.filter(track=['#wellness', '#health', '#diet'])
