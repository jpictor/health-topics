import json
import tweepy
import pydash
import requests


consumer_key = 'EXXJ3ygv659jwUoZuoBvuPZ7H'
consumer_secret = 'ZsryqsdCIowimKA1Jv46a3OXcJ8QUohInNZoCgHAzfn6UKjqJo'
access_token = '2195427973-6AkH2lhVbuBKst3v4xh9MH0nvSBs9htO7xs55Kj'
access_token_secret = 'S1jqpQLCJZFwQn5D2O7GcEtc8k640adbxqaLyPqZAU3v4'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


def content_hub_crawl(url):
    print('CRAWL-URL: {}'.format(url))
    resp = requests.post('http://localhost:8192/api/content-hub/crawl', data={'url': url})
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
