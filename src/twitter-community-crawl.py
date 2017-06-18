import os
import json
import tweepy
import pydash
import requests
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

class ApiConfig(object):
    @classmethod
    def get_api(cls):
        api_config = cls()
        auth = tweepy.OAuthHandler(api_config.consumer_key, api_config.consumer_secret)
        auth.set_access_token(api_config.access_token, api_config.access_token_secret)
        api = tweepy.API(auth)
        return api

    def __init__(self):
        self.consumer_key = os.environ['TWITTER_CONSUMER_KEY']
        self.consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
        self.access_token = os.environ['TWITTER_ACCESS_TOKEN']
        self.access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

twitter_api = ApiConfig.get_api()

class User(object):
    def __init__(self, user_lookup_id):
        self.user = twitter_api.get_user(user_lookup_id)
        print(dir(self.user))
        print(self.user)
        self.followers = []
        self.following = []

    def get_followers(self):
        self.followers = [u for u in tweepy.Cursor(twitter_api.followers, self.user.id).items(1)]

    def get_following(self):
        self.followers = [u for u in tweepy.Cursor(twitter_api.following, self.user.id).items(1)]

    def save(self):
        user_dir = os.path.join(os.environ['DATA_ROOT'], 'users', str(self.user.id))
        os.makedirs(user_dir)

def main():
    twitter_users_string = os.environ['TWITTER_COMMUNITY_CRAWL_USERS']
    users = [User(twitter_user) for twitter_user in twitter_users_string.split(' ')]
    for user in users:
        user.get_followers()
        user.get_following()
        user.save()

if __name__ == '__main__':
    main()
