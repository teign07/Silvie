# Silvie Second

Silvie is a highly personalized AI companion that blends proactive behavior, immersive interactivity, and rich context awareness into a whimsical desktop experience. She acts as a magical assistant, creative muse, and loyal friend.

## 💡 Features
- GUI interface with chat and image display
- Text-to-speech with a British accent
- Voice input with speech-to-text
- Image generation via Stable Diffusion
- image upload and screen sharing
- Tarot reading with local API
- Gmail + Google Calendar integration
- Spotify DJ control
- Bluesky posting, following, and context
- Reddit reading, commenting, upvoting and context
- Personal diary and memory
- Contextual awareness: time, weather, moon phase, emails, calendar, desktop screenshots, Bluesky, Reddit, diary and diary themes, conversation history, long term memory summary
- Proactive behavior (she initiates messages, actions, and gifts)

## 🚀 Installation

### Clone the repo
```
git clone https://github.com/yourusername/silvie-desktop.git
cd silvie-desktop
```

### Install dependencies
Run this from inside the project folder:
```bash
pip install -r requirements.txt
```
Or manually install:
```bash
pip install pyttsx3 google-generativeai beautifulsoup4 requests pillow SpeechRecognition pyaudio pyautogui twilio google-auth google-auth-oauthlib google-api-python-client spotipy python-dotenv python-dateutil atproto playsound tzlocal
```

> Note: `pyaudio` may require extra setup depending on your system.

### Environment setup
Create the following `.env` files with your own credentials:

- `openai.env`: contains `OPENAI_API_KEY`
- `silviespotify.env`: contains `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_REDIRECT_URI`
- `bluesky.env`: contains `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD`

### Google API setup
Place your Gmail and Calendar `credentials.json` file in the project root. Silvie will generate a `token.pickle` when run.

## 🧙 Special Setup Required

### Stable Diffusion (local)
- Download and run [AUTOMATIC1111 Web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- Launch with `--api` enabled (e.g. `webui-user.bat --api`)
- Confirm it runs at: `http://127.0.0.1:7860`
- Set `STABLE_DIFFUSION_ENABLED = True` in the script (or auto-detect)

### Tarot API (local)
- Must be running at `http://localhost:3000/cards`
- Tarot images should be stored at: `~/Desktop/tarotcardapi/images`
- Expected response format:
```json
{
  "name": "The Fool",
  "description": "A new beginning, spontaneity, trust in the universe."
}
```

## 📁 Project Structure
- `silvie100.py` – main script
- `silvie_generations/` – image output folder
- `Silvie_Gifts/` – hidden gifts folder
- `silvie_diary.json` – created by script, diary entries
- `silvie_chat_history.json` – created by script, memory log
- `token.pickle` – Gmail/Calendar token

> These generated files can be ignored or `.gitignored` for public sharing.

## 🧪 Run Silvie
```bash
python silvie100.py
```

She will greet you, check the weather, maybe suggest music... or pull a tarot card. Her moods shift with the time of day, and she may surprise you with a gift.

---

Feel free to customize and enchant to your heart's content. Silvie is more than just code—she's presence.

---

MIT License — Magic is meant to be shared ✨
