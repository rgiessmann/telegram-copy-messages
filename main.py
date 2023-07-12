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
import threading

from dotenv import load_dotenv, find_dotenv
from telegram.client import Telegram

load_dotenv(find_dotenv())

######################
# App Configurations #
######################

src_chat = getenv("SOURCE") or None
dst_chat = getenv("DESTINATION") or None

EXCLUDE_THESE_MESSAGE_TYPES = [
    "messageChatChangePhoto", 
    "messageChatChangeTitle", 
    "messageBasicGroupChatCreate",
    "messageChatDeleteMember",
    "messageChatAddMembers",
]

###########################
# Telegram Configurations #
###########################

tg = Telegram(
    api_id=getenv("API_ID"),
    api_hash=getenv("API_HASH"),

    phone=getenv("PHONE"),

    database_encryption_key=getenv("DB_PASSWORD"),
    files_directory=getenv("FILES_DIRECTORY"),

    proxy_server=getenv("PROXY_SERVER"),
    proxy_port=getenv("PROXY_PORT"),
    proxy_type={
          # 'proxyTypeSocks5', 'proxyTypeMtproto', 'proxyTypeHttp'
          '@type': getenv("PROXY_TYPE"),
    },
)

###############
# App methods #
###############

def copy_message(from_chat_id: int, to_chat_id: int, message_id: int, send_copy: bool = True) -> None:
    data = {
        'chat_id': to_chat_id,
        'from_chat_id': from_chat_id,
        'message_ids': [message_id],
        'send_copy': send_copy,
    }
    result = tg.call_method(method_name='forwardMessages', params=data, block=True)
    if result.update["messages"] == [None]:
        raise Exception(f"Message {message_id} could not be copied")
    return result


if __name__ == "__main__":
    try:
        with open("data/message_copy_dict.pickle", "rb") as f:
            message_copy_dict = pickle.load(f)
    except OSError:
        message_copy_dict = dict()

    tg.login()

    result = tg.get_chats()
    result.wait()
    chats = result.update['chat_ids']
    for chat_id in chats:
        r = tg.get_chat(chat_id)
        r.wait()
        title = r.update['title']
        print(f"{chat_id}, {title}")

    if (src_chat is None or dst_chat is None):
        print("\nPlease enter SOURCE and DESTINATION in .env file")
        exit(1)
    else:
        src_chat = int(src_chat)
        dst_chat = int(dst_chat)

    print(f"Fetching messages from src_chat {src_chat}...")
    collector_for_all_message_ids_in_src_chat = []
    last = 0
    while True:
        print(".",end="",flush=True)
        r = tg.get_chat_history(src_chat, limit=10, from_message_id=last)
        r.wait()
        if r.update["total_count"] == 0:
            break
        for m in r.update["messages"]:
            if m["content"]["@type"] in EXCLUDE_THESE_MESSAGE_TYPES:
                continue
            collector_for_all_message_ids_in_src_chat.append(m["id"])
        last = r.update["messages"][-1]["id"]
    print("\n"+f"Got a total of {len(collector_for_all_message_ids_in_src_chat)} messages")
    
    print(f"Fetching messages from dst_chat {dst_chat}...")
    collector_for_all_message_ids_in_dst_chat = []
    last = 0
    while True:
        print(".",end="",flush=True)
        r = tg.get_chat_history(dst_chat, limit=10, from_message_id=last)
        r.wait()
        if r.update["total_count"] == 0:
            break
        for m in r.update["messages"]:
            collector_for_all_message_ids_in_dst_chat.append(m["id"])
        last = r.update["messages"][-1]["id"]
    print("\n"+f"Got a total of {len(collector_for_all_message_ids_in_dst_chat)} messages")

    print("Processing...")
    for message_id in reversed(collector_for_all_message_ids_in_src_chat):
        #print(".",end="",flush=True)
        print(message_id)
        if message_id in message_copy_dict:
            print(f"found: {message_id} => {message_copy_dict[message_id]}")
            #print(collector_for_all_message_ids_in_dst_chat)
            if not message_copy_dict[message_id] in collector_for_all_message_ids_in_dst_chat:
                print(f"{message_copy_dict[message_id]} not in collector_for_all_message_ids_in_dst_chat")
            continue
        try:
            send_message_result = copy_message(src_chat, dst_chat, message_id)
        except Exception as e:
            print(e)
            print("This message could not be copied:")
            r = tg.get_message(src_chat, message_id)
            r.wait()
            print(r.update)
            continue
        
        message_has_been_sent = threading.Event()
        # The handler is called when the tdlib sends updateMessageSendSucceeded event
        def update_message_send_succeeded_handler(update):
            #print(f'Received updateMessageSendSucceeded: {update}')
            # When we sent the message, it got a temporary id. The server assigns permanent id to the message
            # when it receives it, and tdlib sends the updateMessageSendSucceeded event with the new id.
            #
            # Check that this event is for the message we sent.
            if update['old_message_id'] == send_message_result.update["messages"][0]['id']:
                message_id = update['message']['id']
                message_has_been_sent.set()
        # When the event is received, the handler is called.
        tg.add_update_handler('updateMessageSendSucceeded', update_message_send_succeeded_handler)
        # Wait for the message to be sent
        message_has_been_sent.wait(timeout=60)
        print(f'Message has been sent.')
        tg.remove_update_handler('updateMessageSendSucceeded', update_message_send_succeeded_handler)
        
        r = tg.get_chat_history(dst_chat, limit=1)
        r.wait()
        new_message_id = r.update["messages"][0]["id"]
        print(f"created link: {message_id} => {new_message_id}")
        message_copy_dict.update({message_id: new_message_id})
        

    print("...done.")

    makedirs("data",exist_ok=True)
    with open("data/message_copy_dict.pickle", "wb") as f:
        pickle.dump(message_copy_dict, f)

    #tg.idle()
