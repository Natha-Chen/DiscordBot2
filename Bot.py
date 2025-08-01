import discord
from discord.ext import commands

client = commands.Bot(command_prefix = '!', intents=discord.Intents.default())

@client.event
async def on_ready():
    print("Bot Is Ready! Logged in as: {client.user}")

@client.command()
async def hello(ctx):
    await ctx.send("Hello, I am a bot.")

client.run('MTQwMDYzMzQxNjQ0MTAwNDA5Mw.G1rKtN.oAHjw6mQr0JCr58pJobwavGxKTUw2MyQ68Ef_Q')