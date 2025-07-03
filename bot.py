from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
import sqlite3
import random

# ✅ সরাসরি ভেরিয়েবল
API_ID = 18088290
API_HASH = "1b06cbb45d19188307f10bcf275341c5"
BOT_TOKEN = "7628770960:AAHKgUwOAtrolkpN4hU58ISbsZDWyIP6324"
PRIVATE_CHANNEL_ID = -1002899840201

bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

conn = sqlite3.connect("links.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS links (token TEXT, msg_id INTEGER)")
conn.commit()

@bot.on_message(filters.command("start"))
async def handle_start(client, message: Message):
    args = message.text.split()
    if len(args) == 2:
        token = args[1]
        cursor.execute("SELECT msg_id FROM links WHERE token=?", (token,))
        data = cursor.fetchone()
        if data:
            msg_id = data[0]
            sent = await client.copy_message(chat_id=message.chat.id, from_chat_id=PRIVATE_CHANNEL_ID, message_id=msg_id)
            await asyncio.sleep(1800)
            try:
                await sent.delete()
            except:
                pass
        else:
            await message.reply("⛔ Invalid or expired link.")
    else:
        await message.reply("👋 Welcome! Use /genlink <video_link>")

@bot.on_message(filters.command("genlink"))
async def gen_link(client, message: Message):
    try:
        args = message.text.split()
        if len(args) != 2:
            await message.reply("⚠️ Usage: /genlink <telegram message link>")
            return

        msg_link = args[1]
        if not msg_link.startswith("https://t.me/c/"):
            await message.reply("⛔ Invalid link format.")
            return

        parts = msg_link.strip().split("/")
        if len(parts) < 5:
            await message.reply("⛔ Invalid link structure.")
            return

        chat_part = parts[4]
        msg_id = int(parts[5])
        channel_id = int("-100" + chat_part)

        try:
            await client.get_messages(chat_id=channel_id, message_ids=msg_id)
        except Exception as e:
            await message.reply(f"❌ Cannot access message.\nError: `{e}`")
            return

        token = str(random.randint(100000, 999999))
        cursor.execute("INSERT INTO links VALUES (?, ?)", (token, msg_id))
        conn.commit()

        link = f"https://t.me/{client.me.username}?start={token}"
        await message.reply(f"✅ Link Generated:\n{link}")

    except Exception as e:
        await message.reply(f"❌ Error:\n`{e}`")

bot.run()
