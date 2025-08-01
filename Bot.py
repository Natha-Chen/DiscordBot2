import discord
from discord.ext import commands

intents = discord.Intents.default() 
intents.message_content = True 
intents.guilds = True

client = commands.Bot(command_prefix = '!', intents=intents)

@client.event
async def on_ready():
    print("Bot Is Ready! Logged in as: " + client.user )

@client.event
async def on_message(message):
    await client.process_commands(message)
    if message.author == client.user:
        return
    
    if message.content.startswith('will you marry me'):
        await message.channel.send('⚡KYS⚡')

@client.command()
async def hello(ctx):
    print("hello")
    await ctx.channel.send("Hello, I am a bot.")

@client.event
async def on_member_join(member):
    channel = client.get_channel('')
    await channel.send("Hello")

client.run('MTQwMDYzMzQxNjQ0MTAwNDA5Mw.Goyh5l.OeFKz44zcFPKati3-DCU0ceK7c6SVuEjZD6BGA')