from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from telethon import TelegramClient
from transformers import pipeline
import os
import asyncio

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files configuration
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

# Environment variables for Telegram API
api_id = os.getenv('TELEGRAM_API_ID', '29135303')
api_hash = os.getenv('TELEGRAM_API_HASH', 'bf00cfc08a2e8006d542bf178c6170b1')
channel_usernames = os.getenv('CHANNEL_USERNAMES', 'Best_AI_tools,gpt_anthropic').split(',')
download_folder = 'downloads'

# Initialize Telegram client
client = TelegramClient('session_name', api_id, api_hash)

# Initialize zero-shot classifier with updated labels
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
labels = [
    "AI text-to-speech tools",
    "AI image editing tools",
    "AI image generator tools",
    "AI animation tools",
    "AI chatbot tools",
    "AI NSFW chatbot tools",
    "others"  # Fallback category
]

async def fetch_and_download_media(channel_usernames, limit=5):
    await client.start()

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    all_messages_info = []

    for channel_username in channel_usernames:
        channel_folder = os.path.join(download_folder, channel_username)
        if not os.path.exists(channel_folder):
            os.makedirs(channel_folder)

        channel = await client.get_entity(channel_username)
        messages_info = []
        download_tasks = []

        async for message in client.iter_messages(channel, limit=limit):
            message_data = {
                "channel": channel_username,
                "id": message.id,
                "text": message.text,
                "photo_path": None,
                "video_path": None,
                "label": None  # Added label field
            }

            # Classify text
            if message.text:
                result = classifier(message.text, candidate_labels=labels)
                category = result['labels'][result['scores'].index(max(result['scores']))]
                message_data["label"] = category  # Add the label to the message_data

            if message.photo:
                download_task = asyncio.create_task(message.download_media(file=channel_folder))
                download_tasks.append((download_task, message_data, 'photo'))
            elif message.video:
                download_task = asyncio.create_task(message.download_media(file=channel_folder))
                download_tasks.append((download_task, message_data, 'video'))
            else:
                messages_info.append(message_data)

        for download_task, message_data, media_type in download_tasks:
            media_path = await download_task
            if media_path:
                media_filename = os.path.basename(media_path)
                if media_type == 'photo':
                    message_data["photo_path"] = media_filename
                elif media_type == 'video':
                    message_data["video_path"] = media_filename
            messages_info.append(message_data)

        all_messages_info.extend(messages_info)

    return all_messages_info

@app.get('/api')
async def readfunc():
    try:
        messages_info = await fetch_and_download_media(channel_usernames)
        return {"message": "Photos and videos fetched from multiple channels", "data": messages_info}
    except Exception as e:
        return {"error": str(e)}

@app.on_event("shutdown")
async def shutdown_event():
    await client.disconnect()
