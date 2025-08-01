import discord
from discord.ext import commands

client = commands.Bot(command_prefix = '!', intents=discord.Intents.default())

@client.event
async def on_ready():
    print("Bot Is Ready! Logged in as: {client.user}")

@client.command()
async def hello(ctx):
    await ctx.send("Hello, I am a bot.")

client.run('MTQwMDYzMzQxNjQ0MTAwNDA5Mw.GZ0AuI.WyjLsFsJUIH0w1WB7cZinQ4jjYEM3P_iNOKiq4')