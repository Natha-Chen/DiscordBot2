import discord
from discord.ext import commands

intents = discord.Intents.default() 
intents.message_content = True 
intents.guilds = True

client = commands.Bot(command_prefix = '!', intents=intents)

@client.event
async def on_ready():
    print("Bot Is Ready! Logged in as: {client.user}")

@client.command()
async def hello(ctx):
    print("hello")
    await ctx.send("Hello, I am a bot.")



client.run('MTQwMDYzMzQxNjQ0MTAwNDA5Mw.Goyh5l.OeFKz44zcFPKati3-DCU0ceK7c6SVuEjZD6BGA')