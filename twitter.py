import tweepy
import discord
from discord.ext import commands
from tweepy import asynchronous
from tokens import bearer_token
from tokens import twitter_id
import asyncio
import time



class twitterStream(tweepy.StreamingClient):
    def on_connect(self):
        print("Twitter bot connected!")

    def on_tweet(self, tweet):
        if tweet.referenced_tweets == None:
            self.client.dispatch('new_tweet', tweet)
            print(tweet.text)



class TwitterCog(commands.cog):
    def __init__(self, client):
        self.client = client

    async def twitter_bot(self):    
        auth = tweepy.Client(bearer_token)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        stream = await twitterStream(bearer_token)
        await stream.add_rules(tweepy.StreamRule(f"from:{twitter_id}"))
        await stream.filter(tweet_fields= ["author_id"])






async def setup(client: commands.bot):
    await client.add_cog(TwitterCog(client))            