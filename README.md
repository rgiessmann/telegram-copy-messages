# Telegram Copy Messages Script

## What's the problem
You use Telegram to store stuff, e.g. notes to yourself, files, etc. Possibly you even use it together with another person to share notes, e.g. your grocery store list.

But: you created a group in the past, which now blocks you from editing the messages of yourself or the other person. You want to get rid of the group and use a much-cooler channel, but you refrain from copying all the content of the group by yourself.

This script is for you.

## What it does
This script copies messages from a source chat to a destination chat.

It will display the list of available chats/groups/channels first, and you can select source and destination.

It keeps a list of already-copied messages on file, so you can run it multiple times without copying everything again.

## How to use
0. Clone this repository and cd into the corresponding directory:
    ```
    git clone git@github.com:rgiessmann/telegram-copy-messages.git
    cd telegram-copy-messages
    ```
1. Copy `.env.example` to `.env`.
    ```
    cp .env.example .env
    ```
2. Fill in your phone number in the `.env` file. Obtain `api_id` and `api_hash` from [this link](https://my.telegram.org/apps) and fill it inside `Telegram Configuration` section of the `.env` file.
3. Run the script via python:
    ```
    pip install -r requirements.txt
    python main.py
    ```
4. After logging in, you will see your chat names and their chat id. Copy chat ids of source and destination chats and put them inside `App Configuration` section of the `.env` file.
5. Run the script or container again (with the commands from above) and it will do the job. The links between messages are saved persistently in either your local directory (under "data") or in the Docker volume telegramcopymessages-data.

## Inspired by
Kudos to https://github.com/radinshayanfar/TGCopyBot/ and https://github.com/alexander-akhmetov/python-telegram/blob/master/examples/ !
