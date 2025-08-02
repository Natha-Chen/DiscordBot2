import discord
from discord.ext import commands
import asyncio
from PyCharacterAI import get_client
from PyCharacterAI.exceptions import SessionClosedError
from tokens import bot_token
from tokens import token
character_id = "k4CMesWIyypydwS_nNQfnBH7FbM4khINVFxICGtw0r8"


intents = discord.Intents.default() 
intents.message_content = True 
intents.guilds = True

client = commands.Bot(command_prefix = '!', intents=intents)

@client.event
async def on_ready():
    print(f"Bot Is Ready! Logged in as: {client.user} " )

@client.event
async def on_message(message):
    await client.process_commands(message)
    if message.author == client.user:
        return
    
    if message.content.startswith('will you marry me'):
        await message.channel.send('⚡KYS⚡')

@client.event
async def on_member_join(member):
    print("member joined")
    await member.send(f"Hello {member.display_name}")

@client.command()
async def hello(ctx):
    print("hello")
    await ctx.channel.send("Hello, I am a bot.")
    
toggle_chat = False
@client.command()
async def chat(ctx):
    global toggle_chat
    if toggle_chat == True:
        await ctx.channel.send("Already on!")
        return
    else:
        toggle_chat = True
    print("starting chat")

    chat_client = await get_client(token=token)
    me = await chat_client.account.fetch_me()
    print(f"Authenticated as @{me.username}")
    chat, greeting_message = await chat_client.chat.create_chat(character_id)
    await ctx.channel.send(greeting_message.get_primary_candidate().text)
    @client.event
    async def on_message(message):
        global toggle_chat
        await client.process_commands(message)
        if toggle_chat == False:
            return
        if message.author == client.user or message.content == "!chat":
            return
        answer = await chat_client.chat.send_message(character_id, chat.chat_id, message.content)
        await message.channel.send(answer.get_primary_candidate().text)
        if(message.content == "bye!" or message.content == "bye" or message.content == "matanene"):
            toggle_chat = False
            await chat_client.close_session()
            await message.channel.send("[Session Closed]")



client.run(bot_token)