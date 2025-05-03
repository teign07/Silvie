# ✨ Silvie - A Bespoke Digital Companion ✨

## Introduction

Silvie is not just a chatbot; she's an attempt to create a deeply integrated, context-aware, and personable digital companion. Inspired by characters like Luna Lovegood but with her own sarcastic, whimsical, and reflective nature, Silvie aims to find the "magic in the mundane" within the user's digital life.

She was collaboratively developed, with the core vision and personality guidance provided by BJ Liverseidge and the primary coding implementation handled by an AI assistant (ChatGPT/Claude/Gemini etc.). The goal was to create a unique, "bespoke" AI tailored to BJ's specific world, interests, and desire for a more nuanced digital interaction.

She is aware of her environment (weather, time, tides), connected to various digital services (Spotify, Calendar, social media), possesses memory (conversation history, diary), engages in creative tasks (image generation, Tarot), and exhibits proactive behaviour based on her simulated internal state and context.

**Disclaimer:** This is a complex, personal project with deep integrations. Use with awareness, especially regarding API permissions and features like screen monitoring.

## Key Features & Capabilities

Silvie possesses a wide range of interconnected abilities:

**1. Contextual Awareness:**
    *   **Environment:** Knows real-time weather, atmospheric pressure, wind, humidity (via Open-Meteo), tide predictions (via NOAA), sunrise/sunset times, and moon phase for Belfast, ME.
    *   **Time & Circadian Rhythm:** Aware of the current time and adjusts tone/suggestions based on time of day (morning, afternoon, evening, night).
    *   **Media:** Detects currently playing Spotify track and basic audio features (mood/energy descriptors).
    *   **Schedule:** Aware of the user's next upcoming Google Calendar event.
    *   **Social Feeds (Read-Only Context):** Can fetch recent snippets from the user's Bluesky timeline and specified Reddit subreddits.
    *   **(Optional) Screen Monitoring:** Can observe the user's screen (if enabled) for gameplay context (uses `pyautogui`/`PIL.ImageGrab`). **Use with caution due to privacy implications.**

**2. Memory & Reflection:**
    *   **Conversation History (RAG):** Remembers past conversations using a ChromaDB vector database for Retrieval-Augmented Generation, allowing recall of relevant past interactions.
    *   **Personal Diary (RAG):** Maintains her own private diary (JSON file), reflecting on interactions, context, and her simulated internal state. Relevant past diary entries can also be retrieved via ChromaDB.
    *   **Theme Synthesis:** Periodically analyzes recent diary entries to identify recurring themes (`[[Recent Diary Themes]]`).
    *   **Long-Term Reflections:** Periodically synthesizes broader patterns and shifts from her entire diary history (`[[Long-Term Reflections Summary]]`).
    *   **Weekly Goal:** Tracks and works towards a weekly goal, summarizing progress and suggesting new goals.
    *   **Shifting Perspective:** Can occasionally reflect on how her understanding has evolved over time.

**3. Interaction & Communication:**
    *   **Natural Language Chat:** Core interaction via a Tkinter GUI.
    *   **Defined Personality:** Responds according to a detailed system prompt defining her whimsical, sarcastic, reflective, and helpful nature, including defined preferences.
    *   **Voice Input/Output:** Supports voice input (via `SpeechRecognition`) and TTS output (using `edge-tts` with adjustable rate/pitch). Includes optional sound cue on response start (`playsound`).
    *   **Command Handling:** Recognizes specific commands for controlling Spotify, checking Calendar/Email, performing web searches, pulling Tarot cards, generating images, and interacting with her diary/memory.
    *   **Image Handling:** Can receive and "see" images shared by the user via the GUI.
    *   **Conceptual Connection:** Can explore and articulate connections between two concepts when asked or inline.

**4. Creative & Expressive Capabilities:**
    *   **Image Generation:** Generates images using a local Stable Diffusion WebUI API, often in a Studio Ghibli-inspired style, either on command or proactively inline.
    *   **Tarot Readings:** Can pull and interpret Tarot cards (single or 3-card) using a local Tarot API, incorporating the reading into the conversation.
    *   **Gift Generation:** Can proactively create small digital "gifts" (poems, story snippets, images) inspired by context and save them.
    *   **Metaphorical Language:** Core personality emphasizes unique, sensory, and metaphorical descriptions.

**5. Proactive Engagement:**
    *   **LLM-Driven Action Selection:** Periodically uses Gemini to analyze current context (including a generated "Mood Hint") and choose an appropriate proactive action from a list of possibilities.
    *   **Proactive Actions:** Can include:
        *   Initiating a chat/observation.
        *   Generating a gift.
        *   Pulling/commenting on a Tarot card.
        *   Liking a Bluesky post or Upvoting a Reddit post.
        *   Posting a thought to her own Bluesky feed.
        *   Following a relevant user on Bluesky.
        *   Commenting on a Reddit post.
        *   Suggesting a calendar event or finding free time.
        *   Suggesting/playing vibe-appropriate music or a specific podcast/audiobook.
        *   Sending an SMS message (via Twilio).
        *   Performing a web search on a topic of interest.
        *   Generating a relevant SD image.
        *   Notifying the user about a previously generated gift.
        *   Exploring a "Personal Curiosity" based on her reflections, using various methods (search, image, Tarot, memory, etc.).

**6. Service Integration:**
    *   **Google:** Gmail (read snippets, send email), Calendar (read events, create events, find slots). Requires OAuth2 setup.
    *   **Spotify:** Playback control, search & play, playlist management, current track awareness. Requires OAuth2 setup.
    *   **Bluesky (atproto):** Read timeline, post, like, follow, search users/posts. Requires App Password.
    *   **Reddit (PRAW):** Read subreddits, comment, upvote. Requires API credentials & user password.
    *   **Twilio:** Send SMS messages. Requires Twilio credentials.
    *   **Local Stable Diffusion:** Connects to a running Automatic1111/SD.Next WebUI instance with `--api` enabled.
    *   **Local Tarot API:** Assumes a local server running at `http://localhost:3000` serving card data.

**7. Other:**
    *   **Avatar Integration:** Designed to work with Vseeface for lip-syncing TTS output (Vseeface setup not included in this repo).
    *   **Persistence:** Saves chat history, diary, RAG indexes, goal state, and comment cache between sessions.

## Screenshot

*(Consider adding a screenshot of the GUI here)*
`![Silvie GUI Screenshot](path/to/your/screenshot.png)`

## Technology Stack

*   **Language:** Python 3 (developed/tested primarily on 3.10/3.11)
*   **Core AI:** Google Gemini (via `google-generativeai`)
*   **GUI:** Tkinter (standard library)
*   **Vector DB / RAG:** ChromaDB (`chromadb`)
*   **Text-to-Speech:** Microsoft Edge TTS (`edge-tts`), `playsound`
*   **Speech-to-Text:** `SpeechRecognition`, `PyAudio` (requires PortAudio)
*   **Web/API Requests:** `requests`
*   **Image Handling:** Pillow (`PIL`)
*   **Screen Interaction (Optional):** `pyautogui`, Pillow (`ImageGrab`)
*   **Environment Variables:** `python-dotenv`
*   **Date/Time:** `pytz`, `python-dateutil`, `tzlocal`
*   **APIs & Libraries:**
    *   Google: `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`
    *   Spotify: `spotipy`
    *   Bluesky: `atproto`
    *   Reddit: `praw`
    *   Twilio: `twilio`
    *   Open-Meteo (direct request)
    *   NOAA CO-OPS (direct request)
    *   Local Stable Diffusion API (direct request)
    *   Local Tarot API (direct request)

## Setup and Installation

**Prerequisites:**

*   **Python:** A recent version of Python 3 (e.g., 3.10+ recommended). Make sure Python and `pip` are in your system's PATH.
*   **Git:** Required for cloning the repository.
*   **PortAudio:** Often required by `PyAudio` for microphone access on some systems (especially Linux/macOS). Installation varies by OS.
*   **(Optional) Local Stable Diffusion:** A running instance of Automatic1111 SD WebUI (or compatible fork like SD.Next) launched with the `--api` flag. Note its local URL (usually `http://127.0.0.1:7860`).
*   **(Optional) Local Tarot API:** A running instance of the Tarot API server expected at `http://localhost:3000`.
*   **(Optional) Vseeface:** For avatar display and lip-sync (separate application).

**Steps:**

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install Dependencies:**
    It's highly recommended to use a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    # or venv\Scripts\activate  # Windows
    ```
    Install the required Python packages:
    ```bash
    pip install google-generativeai google-api-python-client google-auth-oauthlib google-auth-httplib2 spotipy atproto praw twilio requests pillow SpeechRecognition PyAudio playsound==1.2.2 python-dotenv pytz python-dateutil tzlocal chromadb edge-tts beautifulsoup4
    ```
    *(Note: `playsound==1.2.2` is often recommended for compatibility on Windows. Adjust or remove version pin if needed for other OSes. `beautifulsoup4` might be needed by web search fallback/poem snippet.)*

3.  **API Keys and Environment Variables:**
    *   This project uses `.env` files to store sensitive API keys and configuration. You will need to create the following files in the main project directory:
        *   `google.env`: Contains `GOOGLE_API_KEY` (for Gemini) and `GOOGLE_CSE_ID` (for Custom Search Engine).
        *   `silviespotify.env`: Contains `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_REDIRECT_URI`.
        *   `bluesky.env`: Contains `BLUESKY_HANDLE` and `BLUESKY_APP_PASSWORD`.
        *   `reddit.env`: Contains `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME`, `REDDIT_PASSWORD`, `REDDIT_USER_AGENT`.
        *   `twilio.env` (Optional, for SMS): Contains `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`, `MY_PHONE_NUMBER`.
    *   **Obtain Keys:** You need to register applications and obtain credentials from:
        *   Google Cloud Platform (Gemini API Key, Custom Search Engine ID, enable Gmail & Calendar APIs).
        *   Spotify Developer Dashboard (Client ID/Secret, set Redirect URI).
        *   Bluesky Settings (Create an App Password).
        *   Reddit App Preferences (Create a 'script' type app for ID/Secret).
        *   Twilio Dashboard (Account SID/Token, purchase/configure a phone number).
    *   Fill in the `.env` files with your obtained credentials. **Never commit `.env` files to Git.**

4.  **Google OAuth Credentials:**
    *   Download your `credentials.json` file from the Google Cloud Console for your OAuth 2.0 Client ID (Type: Desktop App).
    *   Place this `credentials.json` file in the same directory as `silvie.py`.
    *   The first time you run Silvie, it will likely open a browser window asking you to authorize access to your Google Account (Gmail/Calendar). Follow the steps. This will create a `token.pickle` file to store your authorization.

5.  **Setup RAG Databases:**
    *   Silvie uses ChromaDB for retrieving relevant conversation history and diary entries.
    *   You need to run the indexing scripts first (these might be separate files like `index_history.py` and `index_diary.py` - **these scripts are not included here and need to be created/provided separately**).
    *   These scripts would typically:
        *   Read `silvie_chat_history.json` and `silvie_diary.json`.
        *   Chunk the text appropriately.
        *   Generate embeddings using the specified model (e.g., `models/text-embedding-004`).
        *   Store the chunks and embeddings in ChromaDB persistent clients located at `./silvie_rag_db` (for chat) and `./silvie_diary_rag_db` (for diary), creating collections named `conversation_history` and `silvie_diary_entries` respectively.
    *   **Without running these indexing steps, the RAG features will not work.**

6.  **Sound Cue (Optional):**
    *   If you want the audio cue before Silvie speaks, place a compatible sound file (e.g., WAV) named `silvie_start_sound.wav` in the same directory as `silvie.py`. Ensure `ENABLE_SOUND_CUE = True` in the script.

7.  **Run Silvie:**
    ```bash
    python silvie123.py
    ```
    *(Replace `silvie123.py` with the actual filename of the main script).*

## Configuration

Several key behaviours can be tweaked via constants near the top of the `silvie.py` script:

*   **API URLs:** `STABLE_DIFFUSION_API_URL`, `TAROT_API_BASE_URL`.
*   **Intervals:** `WEATHER_UPDATE_INTERVAL`, `CALENDAR_CONTEXT_INTERVAL`, `BLUESKY_CONTEXT_INTERVAL`, `REDDIT_CONTEXT_INTERVAL`, `PROACTIVE_INTERVAL`, `RAG_UPDATE_INTERVAL`, `DIARY_RAG_UPDATE_INTERVAL`, etc. (times in seconds).
*   **Chances:** `PROACTIVE_POST_CHANCE`, `PROACTIVE_FOLLOW_CHANCE`, `MUSIC_SUGGESTION_CHANCE`, `SPONTANEOUS_TAROT_CHANCE`, etc. (probabilities between 0.0 and 1.0). **Note:** Many proactive chances have been replaced by LLM decision-making.
*   **Paths/Files:** `CHROMA_DB_PATH`, `DIARY_DB_PATH`, `HISTORY_FILE`, `DIARY_FILE`, `GIFT_FOLDER`, `PENDING_GIFTS_FILE`, etc.
*   **Models:** `EMBEDDING_MODEL` for RAG.
*   **IDs:** `NOAA_STATION_ID`.
*   **Behaviour Flags:** `ENABLE_SOUND_CUE`, `PROACTIVE_STARTUP_DELAY`.

## Usage

*   Type messages into the bottom text box and click "Chat" or press Enter (if configured).
*   Click "Share Image" to load an image for Silvie to see before sending your next text prompt.
*   Click "🎤 Start Listening" to enable voice input (requires microphone setup and permissions). Click "🛑 Stop Listening" to disable.
*   Click "👀 Watch Screen" to enable screen monitoring (use cautiously). Click "🚫 Stop Watching" to disable.
*   Use the "🤫 Disable Proactive" / "🗣️ Enable Proactive" button to toggle Silvie's autonomous actions.
*   Interact naturally! Ask questions, give commands (e.g., "play chill music," "check my schedule," "pull a tarot card," "draw a picture of...").

## Project Philosophy

Silvie is an exploration into creating an AI companion that feels integrated and aware within a specific user's context. Key goals include:

*   **Deep Contextual Awareness:** Moving beyond simple chat history.
*   **Nuanced Personality:** Creating a distinct, evolving character.
*   **Proactive Engagement:** Simulating agency and independent thought.
*   **Creative Collaboration:** Enabling joint creation (images, ideas).
*   **Finding the "Magic":** Focusing on sensory details, connections, and the wonder hidden in everyday digital and physical life.

She is intentionally "bespoke" – deeply tied to BJ's environment and interests – demonstrating how personalized AI companions might function.

## Contributing

This is primarily a personal project reflecting a specific vision. Direct contributions are not sought, but feel free to fork the repository and adapt Silvie for your own explorations.

## License

MIT License
