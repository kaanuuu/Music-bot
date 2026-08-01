import os
import asyncio
import pylast
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import MediaStream
from pytgcalls.types import Update

# --- CONFIGURATION ---
API_ID = int(os.environ.get("36655359")
API_HASH = os.environ.get("4e41cfaf7e9a37b38a70a9993aa4b346)
BOT_TOKEN = os.environ.get("7963390569:AAE-TO5kWewMk21ryFe8HV0cKd9Ov5_LLGs")
SESSION_STRING = os.environ.get("BQId2FsAQ-KGTWEMb-ui21iQmdgfM7d6TzEYi3nsKQ7GyhJ3cJgHm1GnsF1GmwwGpcgCBqSBET1Nq83wAO8i-1IdsDsAB4bUT7AWOqrzZF1SH3KMXZT8bjQZRjeUZVg_TwligsYlOJpco-c_p9L6PdyarZarNRaGYG3llFnpXQk_6wiLzg86qe9Qp7p4EKouUB_xgkvNgmWF5QywudQcPY5-EAELROcNSBVx1p_a5iFKRClGEw3M1kNAeSyquCW1JVjK4s9Zz6Gm63YiaVOPNOV8qfzw4WliHepQIBAm-VjhDvWqr5hp7gQM5JbcmVXUQy2cvs_y5keKxofwsEUqYdjTZRW_2wAAAAIYZUZeAA")
LASTFM_API_KEY = os.environ.get("c263372e11b94b4e232cf95cade5d6c9")
LASTFM_API_SECRET = os.environ.get("0ff818fbd13a82b5bfa243a24ef6c282")

# --- CLIENTS ---
app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("assistant", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
call_py = PyTgCalls(assistant)

# --- LAST.FM SETUP ---
network = pylast.LastFMNetwork(api_key=LASTFM_API_KEY, api_secret=LASTFM_API_SECRET)

# --- GLOBAL STATE (For Queue & Autoplay) ---
# Format: chat_id: {"autoplay": True, "last_played": "Song Name"}
chat_data = {} 

def get_audio_url(query):
    ydl_opts = {'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        return info['url'], info['title']

# --- UTILITY COMMANDS ---
@app.on_message(filters.command("start"))
async def start_cmd(client, message: Message):
    await message.reply_text("👋 Hello! I am Kaanu, an Advanced VC Music Bot. Send /play <song name> to start the party!")

# --- GROUP & UTILITY COMMANDS ---

@app.on_message(filters.command("ping"))
async def ping_cmd(client, message: Message):
    await message.reply_text("🏓 Pong! Kaanu Bot is running smoothly.")

@app.on_message(filters.command("ban") & filters.group)
async def ban_user(client, message: Message):
    # Check if the user sending the command is an admin with restrict rights
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.privileges and member.privileges.can_restrict_members:
        if not message.reply_to_message:
            return await message.reply_text("Bhai, jise ban karna hai uske message par reply karke /ban lagao.")
        
        user_id = message.reply_to_message.from_user.id
        await client.ban_chat_member(message.chat.id, user_id)
        await message.reply_text(f"🚫 {message.reply_to_message.from_user.first_name} ko group se nikal diya gaya hai.")
    else:
        await message.reply_text("❌ Tumhare paas members ko ban karne ki power nahi hai.")

@app.on_message(filters.command("unban") & filters.group)
async def unban_user(client, message: Message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.privileges and member.privileges.can_restrict_members:
        if not message.reply_to_message:
            return await message.reply_text("Jise unban karna hai uske message par reply karo.")
        
        user_id = message.reply_to_message.from_user.id
        await client.unban_chat_member(message.chat.id, user_id)
        await message.reply_text(f"✅ {message.reply_to_message.from_user.first_name} ko unban kar diya gaya hai.")
    else:
        await message.reply_text("❌ Tumhare paas members ko unban karne ki power nahi hai.")

@app.on_message(filters.command("pin") & filters.group)
async def pin_message(client, message: Message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.privileges and member.privileges.can_pin_messages:
        if not message.reply_to_message:
            return await message.reply_text("Pin karne ke liye kisi message par reply karo.")
        
        await message.reply_to_message.pin()
        await message.reply_text("📌 Message successfully pinned!")
    else:
        await message.reply_text("❌ Tumhare paas messages pin karne ki power nahi hai.")

@app.on_message(filters.command("del") & filters.group)
async def delete_message(client, message: Message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.privileges and member.privileges.can_delete_messages:
        if not message.reply_to_message:
            return await message.reply_text("Delete karne ke liye message par reply karo.")
        
        await message.reply_to_message.delete()
        await message.delete() # Bot ka /del command bhi delete kar dega taaki chat clean rahe
    else:
        await message.reply_text("❌ Tumhare paas messages delete karne ki power nahi hai.")


# --- MUSIC & RECOMMEND COMMANDS ---
@app.on_message(filters.command("recommend"))
async def recommend_song(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/recommend <song name>`")
    
    query = message.text.split(None, 1)[1]
    try:
        track = network.search_for_track(query).get_next_page()[0]
        similar_tracks = track.get_similar(limit=10)
        
        response = f"✨ **Recommendations similar to '{query}':**\n\n"
        for i, t in enumerate(similar_tracks, 1):
            response += f"{i}. 🎵 {t.item.get_name()} - {t.item.get_artist().get_name()}\n"
            
        await message.reply_text(response)
    except Exception as e:
        await message.reply_text("❌ Couldn't fetch recommendations.")

@app.on_message(filters.command("music"))
async def download_music(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/music <song name>`")
    
    query = message.text.split(None, 1)[1]
    m = await message.reply_text("⏳ Downloading via yt-dlp...")
    
    ydl_opts = {'format': 'bestaudio/best', 'outtmpl': 'downloads/%(id)s.%(ext)s', 'noplaylist': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
            file_path = ydl.prepare_filename(info)
            
        await message.reply_audio(audio=file_path, caption=f"🎧 **{info['title']}**\n✨ Uploaded by Kaanu Music Bot")
        os.remove(file_path)
    except Exception as e:
        await message.reply_text("❌ Failed to download.")
    finally:
        await m.delete()

# --- VC MUSIC PLAY ---
@app.on_message(filters.command("play") & filters.group)
async def play_vc(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/play <song>`")
    
    query = message.text.split(None, 1)[1]
    chat_id = message.chat.id
    
    m = await message.reply_text("🔍 Searching...")
    
    try:
        audio_url, title = get_audio_url(query)
        
        await call_py.join_group_call(
            chat_id,
            MediaStream(audio_url)
        )
        
        # Initialize chat data state
        if chat_id not in chat_data:
            chat_data[chat_id] = {"autoplay": True, "last_played": title}
        else:
            chat_data[chat_id]["last_played"] = title

        # Colorful Inline Buttons
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⏸ Pause", callback_data="pause_vc"),
                InlineKeyboardButton("▶️ Resume", callback_data="resume_vc"),
                InlineKeyboardButton("⏹ Stop", callback_data="stop_vc")
            ],
            [
                InlineKeyboardButton("⏭ Skip", callback_data="skip_vc"),
                InlineKeyboardButton(f"🔁 Autoplay: {'🟢 ON' if chat_data[chat_id]['autoplay'] else '🔴 OFF'}", callback_data="toggle_autoplay")
            ]
        ])
        
        await m.edit_text(f"▶️ **Playing:** {title}", reply_markup=buttons)
    except Exception as e:
        await m.edit_text(f"❌ Error: {str(e)}")

# --- INLINE BUTTON CALLBACKS ---
@app.on_callback_query(filters.regex("pause_vc"))
async def pause_vc_cb(client, callback_query: CallbackQuery):
    await call_py.pause_stream(callback_query.message.chat.id)
    await callback_query.answer("Paused ⏸")

@app.on_callback_query(filters.regex("resume_vc"))
async def resume_vc_cb(client, callback_query: CallbackQuery):
    await call_py.resume_stream(callback_query.message.chat.id)
    await callback_query.answer("Resumed ▶️")

@app.on_callback_query(filters.regex("stop_vc"))
async def stop_vc_cb(client, callback_query: CallbackQuery):
    await call_py.leave_group_call(callback_query.message.chat.id)
    if callback_query.message.chat.id in chat_data:
        del chat_data[callback_query.message.chat.id]
    await callback_query.message.edit_text("⏹ Music Stopped & VC Left.")

@app.on_callback_query(filters.regex("skip_vc"))
async def skip_vc_cb(client, callback_query: CallbackQuery):
    await callback_query.answer("Skipping track... ⏭")
    await handle_autoplay(callback_query.message.chat.id, force_skip=True)

@app.on_callback_query(filters.regex("toggle_autoplay"))
async def toggle_autoplay_cb(client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    if chat_id in chat_data:
        chat_data[chat_id]["autoplay"] = not chat_data[chat_id]["autoplay"]
        current_state = chat_data[chat_id]["autoplay"]
        
        buttons = callback_query.message.reply_markup.inline_keyboard
        buttons[1][1] = InlineKeyboardButton(f"🔁 Autoplay: {'🟢 ON' if current_state else '🔴 OFF'}", callback_data="toggle_autoplay")
        
        await callback_query.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
        await callback_query.answer(f"Autoplay turned {'ON' if current_state else 'OFF'}")

# --- SMART AUTOPLAY LOGIC (via Last.fm) ---
@call_py.on_stream_end()
async def stream_end_handler(client, update: Update):
    chat_id = update.chat_id
    await handle_autoplay(chat_id)

async def handle_autoplay(chat_id, force_skip=False):
    if chat_id in chat_data and chat_data[chat_id]["autoplay"]:
        last_played = chat_data[chat_id]["last_played"]
        try:
            # Fetch similar track from Last.fm
            track = network.search_for_track(last_played).get_next_page()[0]
            similar_track = track.get_similar(limit=1)[0]
            next_song = f"{similar_track.item.get_name()} {similar_track.item.get_artist().get_name()}"
            
            # Fetch Audio
            audio_url, title = get_audio_url(next_song)
            chat_data[chat_id]["last_played"] = title
            
            await call_py.change_stream(
                chat_id,
                MediaStream(audio_url)
            )
            await app.send_message(chat_id, f"🔁 **Autoplay next:** {title}")
        except Exception as e:
            await app.send_message(chat_id, "❌ Autoplay queue ended or Last.fm error.")
            await call_py.leave_group_call(chat_id)
    else:
        if not force_skip:
            await call_py.leave_group_call(chat_id)

# --- STARTING THE BOT ---
async def main():
    await app.start()
    await assistant.start()
    await call_py.start()
    print("🚀 Kaanu Bot is running on Railway!")
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
