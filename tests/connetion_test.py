from os import getenv
from telethon.sync import TelegramClient
from unittest.mock import patch, AsyncMock
from dotenv import load_dotenv, find_dotenv
import pytest

# environment variable setup
load_dotenv(find_dotenv())
phone = getenv("PHONE", None)
api_id = getenv("TEST_API_ID", None)
api_hash = getenv("API_HASH", None)

@pytest.mark.asyncio
async def test_successful_connection():
    with patch("telethon.sync.TelegramClient.connect", new_callable=AsyncMock) as mock_connect:
        with patch("telethon.sync.TelegramClient.is_user_authorized", new_callable=AsyncMock) as mock_is_authorized:
            mock_is_authorized.return_value = True #Set a scenario where Client is connected

            client = TelegramClient(phone, api_id, api_hash)
            await client.connect()


            mock_connect.assert_called_once()
