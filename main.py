import asyncio
import base64
import mimetypes
import os
import pickle
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ContentType

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

BOT_TOKEN = os.getenv("BOT_TOKEN")
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")
OWNER_ID = os.getenv("OWNER_ID")

if not BOT_TOKEN or not DRIVE_FOLDER_ID or not OWNER_ID:
    raise ValueError("Please set BOT_TOKEN, DRIVE_FOLDER_ID and OWNER_ID in environment variables!")

OWNER_ID = int(OWNER_ID)

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_PATH = "token.pickle"

token_b64 = os.getenv("GOOGLE_TOKEN_B64")
if token_b64 and not os.path.exists(TOKEN_PATH):
    with open(TOKEN_PATH, "wb") as f:
        f.write(base64.b64decode(token_b64))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

creds = None
drive_service = None

def get_drive_service():
    global creds, drive_service

    if drive_service is not None and creds and creds.valid:
        return drive_service

    if creds is None and os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET_FILE):
                raise FileNotFoundError(f"{CLIENT_SECRET_FILE} not found, place it next to main.py")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)

    drive_service = build('drive', 'v3', credentials=creds)
    return drive_service

def get_file_info(message: types.Message):
    if message.photo:
        return message.photo[-1].file_id, "photo", "jpg"
    elif message.video:
        return message.video.file_id, "video", "mp4"
    elif message.document:
        ext = message.document.file_name.split(".")[-1] if message.document.file_name else "bin"
        return message.document.file_id, "document", ext
    elif message.voice:
        return message.voice.file_id, "voice", "ogg"
    elif message.video_note:
        return message.video_note.file_id, "circle", "mp4"
    elif message.audio:
        return message.audio.file_id, "audio", "mp3"
    elif message.sticker:
        if message.sticker.is_video:
            return message.sticker.file_id, "sticker", "webm"
        elif message.sticker.is_animated:
            return message.sticker.file_id, "sticker", "tgs"
        return message.sticker.file_id, "sticker", "webp"
    return None, None, None

def upload_sync(file_path: str, file_type: str, original_name: str = None):
    service = get_drive_service()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"{file_type}_{timestamp}"
    if original_name:
        name += f"_{original_name}"

    file_metadata = {'name': name, 'parents': [DRIVE_FOLDER_ID]}
    mime_type, _ = mimetypes.guess_type(file_path)
    mime_type = mime_type or 'application/octet-stream'

    with open(file_path, 'rb') as fh:
        media = MediaIoBaseUpload(fh, mimetype=mime_type, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    print(f"Uploaded {file_type}: {file.get('id')}")
    return file.get('id')

async def upload_to_drive(file_path: str, file_type: str, original_name: str = None):
    return await asyncio.to_thread(upload_sync, file_path, file_type, original_name)

@dp.message(lambda m: m.content_type != ContentType.TEXT)
async def handle_media(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return

    file_id, file_type, ext = get_file_info(message)
    if not file_id:
        return

    file = await bot.get_file(file_id)
    file_path = f"./downloads/{file_type}_{file_id[:12]}.{ext}"
    os.makedirs("./downloads", exist_ok=True)
    await bot.download_file(file.file_path, file_path)

    status = await message.reply(f"Saving {file_type} to Google Drive...")
    try:
        await upload_to_drive(file_path, file_type,
                               message.document.file_name if message.document else None)
        await message.delete()
        await status.delete()
        confirm = await message.answer(f"{file_type.capitalize()} saved to Google Drive.")
        await asyncio.sleep(3)
        await confirm.delete()
    except Exception as e:
        print(f"Error: {e}")
        await status.edit_text("Failed to save.")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@dp.message(Command("start"))
async def start(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("This bot is private.")
        return

    await message.answer(
        "<b>Universal Media Saver Bot</b>\n\n"
        "Send me any media (photos, videos, voice messages, circles, documents, stickers, etc.)\n"
        "I'll quietly save them to your Google Drive.",
        parse_mode="HTML"
    )

async def main():
    print("Universal Media Saver Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())