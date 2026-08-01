# Kaanu Advanced Music Bot 🎵

An advanced Telegram Voice Chat Music Bot built with Pyrogram and PyTgCalls. It uses yt-dlp for high-quality audio streaming and integrates the Last.fm API for intelligent track recommendations and continuous Autoplay.

## Features
- 🎧 **VC Playback**: Seamless voice chat streaming.
- 🔁 **Smart Autoplay**: Fetches similar tracks using Last.fm when the current song ends.
- 🎛 **Inline Controls**: Play, pause, skip, stop, and Autoplay toggle buttons.
- 📥 **Music Download**: `/music` command to download high-quality audio directly.
- 💡 **Recommendations**: `/recommend` command to find similar tracks.

## Deployment on Railway
1. Fork this repository.
2. Go to [Railway.app](https://railway.app/) and create a new project from your GitHub repo.
3. Add the following Environment Variables in Railway:
   - `API_ID`: Your Telegram API ID.
   - `API_HASH`: Your Telegram API Hash.
   - `BOT_TOKEN`: Your Bot Token from BotFather.
   - `SESSION_STRING`: Pyrogram String Session for the Assistant Account.
   - `LASTFM_API_KEY`: Last.fm API Key.
   - `LASTFM_API_SECRET`: Last.fm API Secret.
4. Deploy!
