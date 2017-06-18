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

class ContentSource(object):
    def __init__(self, search=None):
        self.search = search
        self.twitter_min_likes = 0
        self.twitter_min_retweets = 0

class PostItem(object):
    def __init__(self, url=None, created_at=None, score=None):
        self.url = url
        self.created_at = created_at
        self.score = score

def single_space(string):
    while '  ' in string:
        string = string.replace('  ', ' ')
    return string

def clean_text(text):
    text = text.replace('\n', ' ')
    text = single_space(text)
    return text

def html_extract(url):
    print('HTML-EXTRACT-URL: {}'.format(url))
    resp = requests.get('{URL_EXTRACT_URL}/api/url-extract/html_extract'.format(**os.environ), params={'url': url})
    doc = resp.json()
    doc['text'] = clean_text(doc.get('text', ''))
    print(doc.keys())
    print('HTML-EXTRACT-URL-TITLE: {title}'.format(**doc))
    print('HTML-EXTRACT-URL-TEXT: {text}'.format(**doc))
    return doc

def content_hub_crawl(url):
    print('CRAWL-URL: {}'.format(url))
    resp = requests.post('{CONTENT_HUB_URL}/api/content-hub/crawl'.format(**os.environ), data={'url': url})
    doc = resp.json()
    return doc

def get_twitter_post_items(content_source, max_age_days=5):
    def log_info(x):
        print('get_twitter_post_items: search={} {}'.format(content_source.search, x))

    def log_error(x):
        print('get_twitter_post_items: search={} {}'.format(content_source.search, x))

    is_hashtag = not content_source.search.startswith('@')

    def get_post_items_from_tweet_links(tweets):
        results = []
        for tweet in tweets:
            print('tweet: {}'.format(tweet.text))
            favorite_count = tweet.favorite_count
            retweet_count = tweet.retweet_count

            if favorite_count < content_source.twitter_min_likes:
                continue
            if retweet_count < content_source.twitter_min_retweets:
                continue

            score = favorite_count + retweet_count
            links = tweet.entities['urls']
            for link in links:
                post_item = PostItem(url=link['url'], created_at=tweet.created_at, score=score)
                results.append(post_item)
        return results

    api_config = ApiConfig()
    auth = tweepy.OAuthHandler(api_config.consumer_key, api_config.consumer_secret)
    auth.set_access_token(api_config.access_token, api_config.access_token_secret)
    api = tweepy.API(auth)

    def get_tweets():
        if is_hashtag:
            _tweets = api.search(
                q='{} filter:links'.format(content_source.search),
                lang='en',
                result_type='popular',  # options: mixed, popular, recent
                wait_on_rate_limit=True,
                rpp=99)
        else:
            print('SCREEN-NAME: {}'.format(content_source.search))
            _tweets = api.user_timeline(
                screen_name=content_source.search[1:],  # trim the @prefix of user names
                count=99,
                exclude_replies=True,
                include_rts=True,
                wait_on_rate_limit=True)

        return _tweets

    try:
        tweets = list(get_tweets())
    except tweepy.error.TweepError as e:
        log_error(e)
        return

    log_info('search query returned {} tweets'.format(len(tweets)))
    post_items = get_post_items_from_tweet_links(tweets)
    log_info('search query returned {} post-items'.format(len(post_items)))
    return post_items


def crawl_post_items(post_items):
    if post_items:
        for post_item in post_items:
            check = content_hub_crawl(post_item.url)
            print(post_item.url)

def main():
    twitter_users_string = os.environ['TWITTER_SEARCH_USERS']
    users = twitter_users_string.split(' ')

    for user in users:
        source = ContentSource()
        source.search = user
        post_items = get_twitter_post_items(source)
        crawl_post_items(post_items)

if __name__ == '__main__':
    main()
