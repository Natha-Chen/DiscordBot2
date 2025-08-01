import discord
from discord.ext import commands

client = commands.Bot(command_prefix = '!', intents=discord.Intents.default())

@client.event
async def on_ready():
    print("Bot Is Ready! Logged in as: {client.user}")

@client.event
async def hello(ctx):
    await ctx.send("Hello, I am a bot.")

client.run('MTQwMDYzMzQxNjQ0MTAwNDA5Mw.GAwTux.1RXAkPFAj-77Mp454DHJe7x_J3lnuPw0Di5J4A')