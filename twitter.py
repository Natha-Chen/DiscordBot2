import tweepy
import discord
from discord.ext import commands
from tweepy import asynchronous
from tokens import bearer_token
from tokens import twitter_id
import asyncio
import time



class TwitterCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def twitter_bot(self):  
        class twitterStream(tweepy.StreamingClient):
            def on_connect(self):
                print("Twitter bot connected!")

            def on_tweet(self, tweet):
                if tweet.referenced_tweets == None:
                    self.client.dispatch('new_tweet', tweet)
                    print(tweet.text)
    
        auth = tweepy.Client(bearer_token)
        twitter_client = tweepy.Client(
        consumer_key="API / Consumer Key here",
        consumer_secret="API / Consumer Secret here",
        access_token="Access Token here",
        access_token_secret="Access Token Secret here"
)
        stream = twitterStream(bearer_token)

       
        await stream.add_rules(tweepy.StreamRule(f"from:{twitter_id}"))
        await stream.filter(tweet_fields= ["author_id", "created_at", "text"])






async def setup(client: commands.bot):
    print("setting up twitter bot!")
    cog = TwitterCog(client)
    await client.add_cog(cog)
    client.loop.create_task(cog.twitter_bot())       
    print("done!")     