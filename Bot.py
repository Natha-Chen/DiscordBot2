import discord
from discord.ext import commands
import asyncio
from PyCharacterAI import get_client
from PyCharacterAI.exceptions import SessionClosedError
from pyngrok import ngrok
from dotenv import load_dotenv
from tokens import bot_token
from tokens import token
from tokens import channel_id


load_dotenv()



http_tunnel = ngrok.connect(addr='8080')

character_id = "k4CMesWIyypydwS_nNQfnBH7FbM4khINVFxICGtw0r8"

intents = discord.Intents.default() 
intents.message_content = True 
intents.guilds = True

client = commands.Bot(command_prefix= '!', intents=intents)
#command_prefix = '!',
# Config values
client.config = {
	'target_channel': 'https://www.youtube.com/@MomosuzuNene',
	'callback_url': http_tunnel.public_url,
	'announcement_channel': channel_id
}


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


@client.event
async def on_new_video(video_data):
    print("update")
	# Grab the channel from bot
    channel = client.get_channel(client.config['announcement_channel'])
	# Build embed message
    embed = discord.Embed(
        title=video_data['title'],
        color=discord.Colour.blurple()
    )

    embed.set_author(name=video_data['channel_name'])
	# https://img.youtube.com/vi/<Video ID here>/1.jpg
    embed.set_image(url=f'https://img.youtube.com/vi/{video_data["video_id"]}/1.jpg')
    embed.add_field(name='URL', value=video_data['video_url'])
    embed.set_thumbnail(url='https://i.imgur.com/zwHqAkd.png')

	# Send message
    await channel.send(f"{video_data['channel_name']} uploaded a new video.", embed=embed)

async def main():
    async with client:
        await client.load_extension('webserver')
        await client.start(bot_token)


asyncio.run(main())