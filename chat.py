import asyncio
from PyCharacterAI import get_client
from PyCharacterAI.exceptions import SessionClosedError

token = "d82b8abebf44d99bb9ff03cc0625fac42c8cd1a7"
character_id = "k4CMesWIyypydwS_nNQfnBH7FbM4khINVFxICGtw0r8"


async def main():
    client = await get_client(token=token)

    me = await client.account.fetch_me()
    print(f"Authenticated as @{me.username}")

    chat, greeting_message = await client.chat.create_chat(character_id)

    print(f"{greeting_message.author_name}: {greeting_message.get_primary_candidate().text}")

    try:
        while True:
            # NOTE: input() is blocking function!
            message = input(f"[{me.name}]: ")


            answer = await client.chat.send_message(character_id, chat.chat_id, message)
            print(f"[{answer.author_name}]: {answer.get_primary_candidate().text}")
            if message == "bye!":
                break

    except SessionClosedError:
        print("session closed. Bye!")

    finally:
        # Don't forget to explicitly close the session
        await client.close_session()

asyncio.run(main())