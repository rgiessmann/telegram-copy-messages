from telethon.sync import TelegramClient
from telethon.tl.types import Message, MessageReplyHeader, MessageMediaDocument, MessageMediaWebPage
from .chat import check_for_src_dst_id


SOURCE_ID , DESTINATION_ID=check_for_src_dst_id()
SRC_DST_LINKS = {}
ALLOWED_MESSAGE_TYPES= [
    MessageReplyHeader,
    Message
]





async def handle_source_messages(tg: TelegramClient, messages_list: list[int]) -> None:
    src_dst_link = {}

    # Holds previous message after a new iteration starts
    # and the iteration does not fit in a group of media or is and new group of media.
    previous_message: Message = None #holds info about previous iteration to
    grouped_media_caption: str=None
    grouped_media: list=[]
    group_id: int = None  #Identifies the group id of a media message (2 messages with identical group ids are in the same group)

    # Iterates through collected messages in source chat
    for message_id in reversed(messages_list): #the last message or first message when reversed prints out channel name!
        message = await tg.get_messages(SOURCE_ID, ids=message_id)

        # Check if the message is of type Message and not MessageService
        if type(message) not in ALLOWED_MESSAGE_TYPES:
            print()
            print(f"Error: Fetched message is a {type(message)} instead of one of these: \n{ALLOWED_MESSAGE_TYPES}")
            print()
            print(f"message raising error: --> \n{message}")
            print()
            continue


        # Store to previous message and add caption if message is a MEDIA with a CAPTION
        if message.message != "" and message.media is not None:
            grouped_media_caption=message.message
            previous_message = message

        # If new iteration(media message) is not part of a group of media (initiated previously),
        # after a grouped media has be initiated or created,
        # Send media(previously set as previous message) before sending current iteration(media)
        if message.grouped_id is None: # If message is not a grouped message(media)
            if grouped_media: # If a group of media messages is initiated but not sent/handled
                sent_file = await tg.send_file(DESTINATION_ID, grouped_media, caption=grouped_media_caption)
                src_dst_link[f"{previous_message.id}"] = sent_file[-1].id
                grouped_media=[]
            # Send a copy of the message
            await send_copy_message(tg, DESTINATION_ID, message)

        #assign a new group id if group id is empty
        elif group_id is None:
            grouped_media.append(message.media)
            group_id = message.grouped_id
            previous_message = message

        #if message is part of the existing group
        elif message.grouped_id == group_id:
            grouped_media.append(message.media)
            previous_message = message

        # if message media is not a part of an existing group of media,
        # Send the existing group of media
        # create a new group of media.
        elif message.grouped_id != group_id:
            print("new group for current message found! ")
            sent_file=await tg.send_file(DESTINATION_ID, grouped_media, caption=grouped_media_caption) #send existing group media
            src_dst_link[f"{previous_message.id}"] = sent_file[-1].id
            # refresh lists for a new group of media and new group id
            grouped_media = []
            group_id=[]
            # new group configuration
            grouped_media.append(message.media)
            group_id = message.grouped_id
        continue
    return SRC_DST_LINKS


async def collect_messages(tg:TelegramClient, chat_id: int):
    '''
    Get all messages in target chat.
    '''
    try:
        message_ids=[]
        # while True:
        print(".",end="",flush=True)
        messages = await tg.get_messages(chat_id, limit=1_000_000)
        if not messages.total:
            print("Chat is Empty!")
            return message_ids
        for m in messages:
            message_ids.append(m.id)

        print(f'list of retrieved message IDs: {message_ids}')
    except Exception as e:
        print(f"Error Occured in collect_messages function --> {e} ")
        return None
    return message_ids


#Copy function for all message types
# ----------------------------------------------
async def send_copy_message(tg: TelegramClient, chat_recipient: int, message_obj: Message, ):
    '''
    Sends a message object to chat recipient.
    '''
    reply_message: Message = None #Holds message being replied to!
    link_preview: bool = False

    # if message is a reply to another message
    if message_obj.reply_to:
        try:
            reply_id_source = message_obj.reply_to.reply_to_msg_id
            reply_id_dest = SRC_DST_LINKS[f"{reply_id_source}"]
            reply_message = await tg.get_messages(chat_recipient, ids=reply_id_dest)
        except Exception as e:
            print()
            print(f"Error in send_copy_message function----> {e}")
            print(message_obj)

    if isinstance(message_obj.media, MessageMediaWebPage):
        message_obj.media = None
        link_preview = True

    try:
        sent_message_obj = await tg.send_message(
            chat_recipient,
            message = message_obj.message,
            reply_to=reply_message,
            silent=message_obj.silent,
            file=message_obj.media,  # Assuming 'media' is the media file to send
            link_preview = link_preview
            # parse_mode=message_obj.parse_mode,
            # reply_markup=message_obj.reply_markup,
            # clear_draft=message_obj.clear_draft,
        )
    except Exception as e:
        print()
        print(message_obj)
        print(f"Error found while Sending message ----> {e}")

    # append message ID link from old message to new
    SRC_DST_LINKS[f"{message_obj.id}"] = sent_message_obj.id
    print(f"Message of ID ->{message_obj.id} sent successfully!")
    return sent_message_obj
