import aiohttp
import asyncio
import os
import json
from telethon import TelegramClient, events, connection
from dotenv import load_dotenv

load_dotenv("config.env")

TOKEN = os.environ.get("TOKEN", "")
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")

PROXY_HOST = os.environ.get("PROXY_HOST", "")
PROXY_PORT = int(os.environ.get("PROXY_PORT", "0"))
PROXY_SECRET = os.environ.get("PROXY_SECRET", "")

temp = 0.85
len = 128

client = TelegramClient(
    'bot_session',
    API_ID,
    API_HASH,
    connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
    proxy=(PROXY_HOST, PROXY_PORT, PROXY_SECRET),
)

model_lock = asyncio.Semaphore(1)

# === /params ===
@client.on(events.NewMessage(pattern=r'^/params'))
async def printparams(event):
    global temp, len
    await event.reply("Температура: " + str(temp) + ", Длина сообщения: " + str(len))

# === /sett ===
@client.on(events.NewMessage(pattern=r'^/sett'))
async def sett(event):
    global temp
    try:
        temp = float(event.text.split()[1])
        if temp > 1:
            temp = 1
        if temp < 0.1:
            temp = 0.1
        await event.reply("Поставлена температура " + str(temp))
    except:
        await event.reply("Ошибка, хуево задан параметр :<")

# === /setl ===
@client.on(events.NewMessage(pattern=r'^/setl'))
async def setl(event):
    global len
    try:
        len = int(event.text.split()[1])
        if len > 200:
            len = 200
        if len < 5:
            len = 5
        await event.reply("Поставлено кол-во слов " + str(len))
    except:
        await event.reply("Ошибка, хуево задан параметр :<")

# === /model ===
@client.on(events.NewMessage(pattern=r'^/model'))
async def model(event):
    response = requests.get("http://localhost:5001/about").json()
    content = f"Текущая модель: {response['model_name']}\n\nОписание:\n{response['model_description']}"
    message = await event.reply(content)

@client.on(events.NewMessage(
    incoming=True,
    func=lambda e: (
        e.text
        and not e.text.startswith('/')
    )
))
async def sendPrompt(event):
    global temp, len
    msg = await event.reply("В очереди")
    data = {"prompt": event.text, "temperature": float(temp), "len": int(len)}

    #busy_test = requests.get("http://localhost:5001/status").json()
    #if busy_test:
    #    await client.edit_message(event.chat_id, msg.id, str("Сервер занят!"))

    try:
        async with model_lock:
            await msg.edit("Думаю...")
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:5001/prompt", params=data) as resp:
                    response = await resp.json()

        if not response.get('error'):
            print(f"New text {str(response['message'])}")
            print(f"\nOld text {msg.raw_text}")
            print("\n\n")
            await client.edit_message(event.chat_id, msg.id, str(response['message']))
        else:
            await client.edit_message(event.chat_id, msg.id, str(response['error']))
    except Exception as e:
        print(f"Model call error: {e}")
        await msg.edit(f"Произошла ошибка при обращении к модели.")

client.start(bot_token=TOKEN)
client.run_until_disconnected()

'''
TODO: сохранение настроек в БД (aiosqlite)
'''