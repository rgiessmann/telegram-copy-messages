# MIT License
#
# Copyright (c) 2023 Robert Giessmann
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from os import getenv, makedirs
import pickle
from sys import exit
from telethon.sessions.sqlite import PeerChannel, PeerChat
from telethon.tl.types import Message, MessageReplyHeader
from utils.telegram.messages import collect_messages, handle_source_messages
from utils.telegram.chat import get_title, get_chat_ids, check_for_src_dst_id


import threading
import asyncio

from dotenv import load_dotenv, find_dotenv
from telethon.sync import TelegramClient, events



# Environment Variables Configuration #
#---------------------------------------------------------------------------------
load_dotenv(find_dotenv())
phone = getenv("PHONE", None)
api_id = getenv("API_ID", None)
api_hash = getenv("API_HASH", None)
#Source and destination config check
SOURCE_ID , DESTINATION_ID=check_for_src_dst_id()






# Functions #
#--------------------------------------------------------------------------

#Main function
async def main():

    src_chat_id = SOURCE_ID
    dst_chat_id = DESTINATION_ID

    ## Keeping track of previous or already sent messages
    # try:
    #     with open("data/message_copy_dict.pickle", "rb") as f:
    #         message_copy_dict = pickle.load(f)
    # except OSError:
    #     message_copy_dict = dict()

    async with TelegramClient(phone, api_id, api_hash) as tg :

        #Start Client
        await tg.start(phone)
        #Get chats
        chat_ids = await get_chat_ids(tg)



        try:
            #Get Source and Destination Chat entity
            src_entity =await tg.get_entity(src_chat_id)
            dst_entity =await tg.get_entity(dst_chat_id)
        except Exception as e:
            print()
            print("An Error occcured getting source or destination entity!")
            print("-----------------------------")
            print(f"Error: {e}")
            exit(0)
        src_title = get_title(src_entity)
        dst_title = get_title(dst_entity)
        print(f'Retrieved Entities: \nSource-->{src_title} \n Destination --> {dst_title}')
        print()

        #Fetch ids from source and Destination
        print(f"Fetching messages from src_chat {src_title}...")
        collector_for_all_message_ids_in_src_chat :list[int] = await collect_messages(tg, src_chat_id)
        print(f"Got: {len(collector_for_all_message_ids_in_src_chat)} messages from source chat")

        print()

        print(f"Fetching messages from dst_chat_id {dst_title}...")
        collector_for_all_message_ids_in_dst_chat_id =await collect_messages(tg, dst_chat_id)
        print(f"Got: {len(collector_for_all_message_ids_in_src_chat)} messages from destination chat")

        print("Processing...")
        links = await handle_source_messages(tg, messages_list=collector_for_all_message_ids_in_src_chat)

        print("...done.")
        print(f"Source to Destination Message ID Links ----> {links}")
        # makedirs("data",exist_ok=True)
        # with open("data/message_copy_dict.pickle", "wb") as f:
        #     pickle.dump(message_copy_dict, f)




if __name__ == "__main__":
    asyncio.run(main())
