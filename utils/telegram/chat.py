from os import getenv
from telethon.sync import TelegramClient
from telethon.tl.types import User, Channel
from dotenv import load_dotenv, find_dotenv


def get_title(entity):
    '''
    Get title name of the chat user or channel.
    '''
    if type(entity) == User:
        return entity.first_name
    elif type(entity) == Channel:
        return entity.title


async def get_chat_ids(tg: TelegramClient):
    '''
    Get Dialogs: Chats, Groups and Channels from Telegram Client.
    '''
    #get chats, groups and channels
    dialogs = await tg.get_dialogs()
    # Print information about each chat
    for dialog in dialogs:
        print(f'Chat ID: {dialog.id}, Chat Name: {dialog.name}')
    # Gather chat IDs
    chat_ids = [dialog.id for dialog in dialogs]
    return chat_ids

def check_for_src_dst_id()-> str:
    '''
    Confirm Source annd Destination IDs are inputed in environment variables
    '''
    load_dotenv(find_dotenv())
    source_id = getenv("SOURCE", None)
    destination_id = getenv("DESTINATION", None)
    if (not source_id or not destination_id):
        print()
        print("Please enter SOURCE and DESTINATION in .env file")
        exit(1)
        return None, None

    return int(source_id), int(destination_id)
