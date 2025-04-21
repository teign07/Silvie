import os 
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
import sys
import json
import subprocess
import pkg_resources
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import threading
import queue
import pyautogui
from PIL import Image, ImageTk, ImageChops, ImageGrab, UnidentifiedImageError
import time
import speech_recognition as sr
from datetime import datetime
import pytz # For timezone conversion
from dateutil.parser import parse as dateutil_parse # For parsing ISO times easily
from bs4 import BeautifulSoup
import requests
import urllib.parse
import traceback
import io
import base64
import random
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import pickle
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import google.generativeai as genai
from google.generativeai import types # Use this one!
from google.generativeai import GenerativeModel
from google.generativeai.types import HarmCategory
from google.generativeai.types import HarmBlockThreshold
from openai import OpenAI
import requests
from datetime import timezone
from googleapiclient.errors import HttpError
from dateutil import tz # Add this for timezone conversion if not already there
import math # Add this for time difference calculation
from tzlocal import get_localzone_name
from datetime import timedelta
import re
import praw
try:
    from atproto import Client as AtpClient, models
    BLUESKY_AVAILABLE = True
    print("✓ Bluesky (atproto) library found.")
except ImportError:
    print("Warning: 'atproto' library not found. Bluesky features disabled.")
    print("         To enable, run: pip install atproto")
    BLUESKY_AVAILABLE = False
try:
    import playsound
    PLAYSOUND_AVAILABLE = True
except ImportError:
    print("Warning: 'playsound' library not found. Audio cues will be disabled.")
    print("         To enable audio cues, run: pip install playsound")
    PLAYSOUND_AVAILABLE = False
try:
    from PIL import ImageGrab, Image, UnidentifiedImageError
    SCREEN_CAPTURE_AVAILABLE = True
except ImportError:
    print("Warning: Pillow or system screenshot library not found. Proactive screenshot context disabled.")
    SCREEN_CAPTURE_AVAILABLE = False
from dotenv import load_dotenv
load_dotenv("silviespotify.env")
load_dotenv("openai.env")
load_dotenv("google.env")
try:
    # Ensure these are imported for safety settings and exceptions
    from google.generativeai import types as genai_types # Use alias
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    StopCandidateException = genai_types.StopCandidateException # Define it globally here
    print("✓ Successfully imported Google AI safety types and StopCandidateException.")

except ImportError:
    # Define dummy versions globally if import fails
    class HarmCategory: pass
    class HarmBlockThreshold: pass
    StopCandidateException = Exception # Fallback to base Exception
    print("Warning: Google AI safety types or StopCandidateException not found, using dummies/fallbacks.")


print(f"--- Script Start ---")
print(f"Python Executable: {sys.executable}")
print(f"Current Working Directory: {os.getcwd()}") # Check where the script is running from

dotenv_path_bluesky = 'bluesky.env'
print(f"Attempting to load environment variables from: {dotenv_path_bluesky}")
# Add check if file exists
if os.path.exists(dotenv_path_bluesky):
    print(f"File '{dotenv_path_bluesky}' FOUND in {os.getcwd()}.")
    # Use override=True just in case there are lingering env vars from elsewhere
    # Use verbose=True to get output from dotenv itself
    load_success = load_dotenv(dotenv_path=dotenv_path_bluesky, verbose=True, override=True)
    print(f"load_dotenv('{dotenv_path_bluesky}') returned: {load_success}")
else:
    print(f"ERROR: File '{dotenv_path_bluesky}' NOT FOUND in {os.getcwd()}!")
    load_success = False

dotenv_path_reddit = 'reddit.env'
print(f"Attempting to load environment variables from: {dotenv_path_reddit}")

# Add check if file exists
if os.path.exists(dotenv_path_reddit):
    print(f"File '{dotenv_path_reddit}' FOUND.")
    # Use override=True just in case there are lingering env vars from elsewhere
    # Use verbose=True to get output from dotenv itself
    load_success = load_dotenv(dotenv_path=dotenv_path_reddit, verbose=True, override=True)
    print(f"load_dotenv('{dotenv_path_reddit}') returned: {load_success}")

    # <<< --- PASTE THE ASSIGNMENT LINES HERE --- >>>
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
    REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
    REDDIT_USER_AGENT = "script:Silvie:0.1 (by /u/OutrageousAction797)"
    # <<< --- END OF PASTED LINES --- >>>
else:
    print(f"ERROR: File '{dotenv_path_reddit}' NOT FOUND!")
    load_success = False

print(f"DEBUG: Value for REDDIT_CLIENT_ID after load: '{REDDIT_CLIENT_ID}' (Type: {type(REDDIT_CLIENT_ID)})")
print(f"DEBUG: Value for REDDIT_CLIENT_SECRET after load: Is present? {REDDIT_CLIENT_SECRET is not None and len(REDDIT_CLIENT_SECRET) > 0}") # Avoid printing pw directly
print(f"DEBUG: Value for REDDIT_USERNAME after load: '{REDDIT_USERNAME}' (Type: {type(REDDIT_USERNAME)})")
print(f"DEBUG: Value for REDDIT_PASSWORD after load: Is present? {REDDIT_PASSWORD is not None and len(REDDIT_PASSWORD) > 0}") # Avoid printing pw directly
# *** END DEBUG PRINTS ***

# Explicitly check the variables immediately after loading attempt
# This REPLACES the original os.getenv calls for these two variables
BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
BLUESKY_APP_PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")

# *** ADD THESE DEBUG PRINTS ***
print(f"DEBUG: Value for BLUESKY_HANDLE after load: '{BLUESKY_HANDLE}' (Type: {type(BLUESKY_HANDLE)})")
print(f"DEBUG: Value for BLUESKY_APP_PASSWORD after load: Is present? {BLUESKY_APP_PASSWORD is not None and len(BLUESKY_APP_PASSWORD) > 0}") # Avoid printing pw directly
# *** END DEBUG PRINTS ***
# <<< END OF INSERTED DEBUG CODE >>>


# --- Add these constants ---
BELFAST_LAT = 44.4256  # Approximate Latitude for Belfast, ME
BELFAST_LON = -69.0067 # Approximate Longitude for Belfast, ME
WEATHER_UPDATE_INTERVAL = 3600 # Update weather every hour (3600 seconds)

IMAGE_SAVE_FOLDER = "silvie_generations" # Define the gallery folder name

CALENDAR_CONTEXT_INTERVAL = 1800 # Update next event context every 30 minutes (1800 seconds)
upcoming_event_context = None    # Global variable to hold the next event info

ENABLE_SOUND_CUE = True  # Set to False to disable this feature
# User needs to provide this sound file in the script's directory or provide full path
SILVIE_SOUND_CUE_PATH = "silvie_start_sound.wav"
# Delay in seconds AFTER the sound cue finishes, BEFORE speech starts
SILVIE_SOUND_CUE_DELAY = 2.0

BLUESKY_CONTEXT_INTERVAL = 900 # Update Bluesky context every 15 minutes (900 seconds)
BLUESKY_CONTEXT_POST_COUNT = 5 # How many posts to fetch for context

INLINE_BLUESKY_POST_COOLDOWN = 7200   # 2 hours
INLINE_BLUESKY_FOLLOW_COOLDOWN = 14400 # 4 hours

PROACTIVE_SCREENSHOT_CHANCE = 0.25 # Chance to *try* getting screenshot context
PROACTIVE_POST_CHANCE = 0.03       # Chance for autonomous Bluesky post
PROACTIVE_FOLLOW_CHANCE = 0.02     # Chance for autonomous Bluesky follow (Keep low!)
MAX_AUTONOMOUS_FOLLOWS_PER_SESSION = 3 # Limit follows per script run

MUSIC_SUGGESTION_CHANCE = 0.15 # 15% chance to suggest music in a regular reply

GIFT_FOLDER = "Silvie_Gifts" # Dedicated folder for gifts
PENDING_GIFTS_FILE = "silvie_pending_gifts.json" # File to track gifts not yet mentioned
GIFT_GENERATION_CHANCE = 0.04 # Chance for Silvie to try creating a gift proactively (e.g., 4%)
GIFT_NOTIFICATION_CHANCE = 0.35 # Chance *if* a gift exists, to notify about it in a proactive message (e.g., 35%)

TAROT_API_BASE_URL = "http://localhost:3000/cards" # NEW - Points to your local API base
TAROT_IMAGE_BASE_PATH = os.path.join(os.path.expanduser('~'), 'Desktop', 'tarotcardapi', 'images')
TAROT_THUMBNAIL_SIZE = (150, 250) # Adjust size as desired (width, height)
SPONTANEOUS_TAROT_CHANCE = 0.10 # 10% chance to pull a card during a regular reply (adjust as needed)

ENVIRONMENTAL_UPDATE_INTERVAL = 6 * 3600 # Update sunrise/set/moon every 6 hours (adjust as needed)
BELFAST_TZ = 'America/New_York' # Timezone for Belfast, ME

STABLE_DIFFUSION_API_URL = "http://127.0.0.1:7860"
STABLE_DIFFUSION_ENABLED = False # We'll check if the API is reachable later

# Optional but recommended: Add checks after loading to ensure credentials are set
if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD]):
    print("\n!!! WARNING: Missing one or more essential Reddit credentials (ID, Secret, User, Pass) in environment variables (reddit.env). Reddit functionality will likely fail. !!!\n")

SILVIE_FOLLOWED_SUBREDDITS = ["MyBoyfriendIsAI"]
REDDIT_CONTEXT_INTERVAL = 1200 # Update Reddit context every 20 minutes
REDDIT_CONTEXT_POST_COUNT_PER_SUB = 5 # How many posts per sub for context
PROACTIVE_REDDIT_COMMENT_CHANCE = 0.05 # 5% chance to try commenting proactively
REDDIT_COMMENT_COOLDOWN = 3600 # 1 hour cooldown for proactive comments

PROACTIVE_BLUESKY_LIKE_CHANCE = 0.08 # e.g., 8% chance
PROACTIVE_REDDIT_UPVOTE_CHANCE = 0.08 # e.g., 8% chance
BLUESKY_LIKE_COOLDOWN = 1800      # 30 minutes cooldown for Bluesky likes
REDDIT_UPVOTE_COOLDOWN = 900       # 15 minutes cooldown for Reddit upvotes
# --- End Reddit Constants ---

# --- Long-Term Memory Globals ---
LONG_TERM_MEMORY_INTERVAL = 6 * 3600  # e.g., Summarize every 6 hours (adjust as needed)
long_term_reflection_summary = None   # Holds the latest summary
last_long_term_memory_update = 0.0    # Timer for this worker
# --- End Long-Term Memory Globals ---

try:
    openai_client = OpenAI() # Reads OPENAI_API_KEY from env implicitly
    print("OpenAI client initialized.")
except Exception as openai_err:
    print(f"Failed to initialize OpenAI client: {openai_err}")
    openai_client = None

bluesky_client = None

# Check and install required packages
required_packages = {
    'pyttsx3': 'pyttsx3',
    'google-generativeai': 'google-generativeai',
    'beautifulsoup4': 'beautifulsoup4',
    'requests': 'requests',
    'pillow': 'PIL',
    'SpeechRecognition': 'speech_recognition',
    'PyAudio': 'pyaudio',
    'pyautogui': 'pyautogui',
    'twilio': 'twilio',
    'google-auth-oauthlib': 'google.oauth2.oauthlib',  # Updated import name
    'google-api-python-client': 'googleapiclient',      # Updated import name
    'google-auth': 'google.auth',                        # Updated import name
    'spotipy': 'spotipy',  # <--- Add this line
    'python-dotenv': 'dotenv',                       # Updated import name
    'python-dateutil': 'dateutil'
}

def install_missing_packages():
    for package, import_name in required_packages.items():
        try:
            pkg_resources.require(package)
        except pkg_resources.DistributionNotFound:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

print("Checking packages...")
install_missing_packages()

# Import packages after installation
import pyttsx3
import google.generativeai as genai
from google.generativeai import GenerativeModel

# Assume conversation_history is a global list defined elsewhere

def manage_silvie_diary(action, entry=None, search_query=None, max_entries=5):
    """Manage Silvie's personal diary
    Actions: 'write', 'read', 'search'
    max_entries: For 'read', number of recent entries, or 'all' to fetch all.
    """
    diary_file = "silvie_diary.json"

    try:
        # Load existing diary
        if os.path.exists(diary_file):
            with open(diary_file, 'r', encoding='utf-8') as f:
                # Handle potential empty file case
                try:
                    diary = json.load(f)
                    if not isinstance(diary, list): # Ensure it's a list
                        print(f"Warning: Diary file '{diary_file}' contained non-list data. Initializing empty diary.")
                        diary = []
                except json.JSONDecodeError:
                    print(f"Warning: Diary file '{diary_file}' was empty or corrupted. Initializing empty diary.")
                    diary = []
        else:
            diary = []

        if action == 'write':
            # Add new entry with timestamp
            # Ensure conversation_history is accessible (it's global in the original script)
            global conversation_history # Make sure this global is accessible if needed
            new_entry = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'content': entry,
                'context': {
                    # Make sure conversation_history exists before slicing
                    'recent_conversation': conversation_history[-2:] if 'conversation_history' in globals() and conversation_history else [],
                    'mood': 'reflective' # Example mood, could be dynamic
                }
            }
            diary.append(new_entry)

            # Save updated diary
            with open(diary_file, 'w', encoding='utf-8') as f:
                json.dump(diary, f, indent=2)
            print(f"DEBUG manage_silvie_diary: action='write', returning True")
            return True

        elif action == 'read':
            # --- START OF MODIFIED 'read' LOGIC ---
            if isinstance(max_entries, str) and max_entries.lower() == 'all':
                result = diary[:] # Return all entries (a copy)
                print(f"DEBUG manage_silvie_diary: action='read', max_entries='all', returning list of length {len(result)}")
                return result
            else:
                try:
                    # Try to convert max_entries to an integer
                    num_entries = int(max_entries)
                    # Handle non-positive numbers, defaulting to 5
                    if num_entries <= 0:
                        print(f"Warning: Non-positive max_entries '{max_entries}' for diary read. Defaulting to 5.")
                        num_entries = 5
                    # Get the last N entries
                    result = diary[-num_entries:] if diary else []
                    print(f"DEBUG manage_silvie_diary: action='read', num_entries={num_entries}, returning list of length {len(result)}")
                    return result
                except (ValueError, TypeError):
                    # Handle cases where max_entries is not 'all' and cannot be converted to int
                    print(f"Warning: Invalid max_entries value '{max_entries}' for diary read. Defaulting to 5.")
                    result = diary[-5:] if diary else []
                    print(f"DEBUG manage_silvie_diary: action='read', ValueError/TypeError fallback, returning list of length {len(result)}")
                    return result
            # --- END OF MODIFIED 'read' LOGIC ---

        elif action == 'search':
            # Search diary entries
            if not search_query:
                print(f"DEBUG manage_silvie_diary: action='search', no query, returning empty list")
                return [] # Return empty list if no query
            matches = []
            for entry_item in diary: # Use a different variable name like entry_item
                # Check if content exists and is a string before searching
                if isinstance(entry_item.get('content'), str) and search_query.lower() in entry_item['content'].lower():
                    matches.append(entry_item)
            print(f"DEBUG manage_silvie_diary: action='search', query='{search_query}', returning list of {len(matches)} matches")
            return matches # Return the list of matches

        else:
            # Handle unknown action if necessary
            print(f"Warning: Unknown action '{action}' for manage_silvie_diary.")
            return None # Indicate unknown action

    except Exception as e:
        print(f"Diary error ({type(e).__name__}): {e}")
        traceback.print_exc() # Print full traceback for diary errors
        # Decide what to return on error
        if action == 'read' or action == 'search':
            print(f"DEBUG manage_silvie_diary: action='{action}', returning [] due to exception.")
            return [] # Return empty list on error for read/search
        else: # For 'write' or unknown action during exception
            print(f"DEBUG manage_silvie_diary: action='{action}', returning False due to exception.")
            return False # Indicate write/other failure

    # Fallback return (should ideally not be reached if logic covers all actions)
    print(f"DEBUG manage_silvie_diary: Reached fallback return for action='{action}'.")
    if action == 'read' or action == 'search':
        return [] # Safer to return empty list than None
    else:
        return False

# Global variables
tts_queue = queue.Queue()
running = True
conversation_history = []  # Store conversation history
MAX_HISTORY_LENGTH = 25   # Remember 25 conversation turns
running = True
listening = False 
screen_monitoring = False
last_screenshot = None
SCREENSHOT_INTERVAL = 15  # seconds between screenshots
MIN_SCREENSHOT_INTERVAL = 15  # Minimum seconds between responses
last_screenshot_time = 0
PROACTIVE_INTERVAL = 1200  # 300 is 5 minutes (was 14400 seconds / 4 hours)
PROACTIVE_STARTUP_DELAY = 50  # 300 is a 5 minute delay before first proactive message
last_proactive_time = time.time()
last_proactive_time = time.time()  # Initialize to current time
proactive_enabled = True
current_weather_info = None
gmail_service = None
calendar_service = None 
current_bluesky_context = None # Global variable to hold Bluesky info
last_inline_bluesky_post_time = 0.0
last_inline_bluesky_follow_time = 0.0
current_sunrise_time = None
current_sunset_time = None
current_moon_phase = None
reddit_client = None
current_reddit_context = None # Global variable to hold Reddit info
last_proactive_reddit_comment_time = 0.0 # Track last proactive comment
last_proactive_bluesky_like_time = 0.0
last_proactive_reddit_upvote_time = 0.0
current_diary_themes = None
DIARY_THEME_UPDATE_INTERVAL = 3600 # Update themes every hour (adjust as needed)
last_diary_theme_update = 0
last_proactive_bluesky_post_time = 0.0
BLUESKY_POST_COOLDOWN = 7200 # Example: 2 hours (in seconds)


# Initialize TTS engine with female voice
print("Initializing TTS engine...")
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1)

# Set female voice with preference for Hazel
voices = engine.getProperty('voices')
voice_found = False
for voice in voices:
    print(f"Found voice: {voice.name}")  # Debug output to see available voices
    if "Hazel" in voice.name:
        print(f"Setting voice to: {voice.name}")
        engine.setProperty('voice', voice.id)
        voice_found = True
        break

# Fall back to other female voices if Hazel not found
if not voice_found:
    for voice in voices:
        if "female" in voice.name.lower() or "Zira" in voice.name:
            print(f"Falling back to voice: {voice.name}")
            engine.setProperty('voice', voice.id)
            break

# Gemini Setup
gemini_api_key = os.getenv("GOOGLE_API_KEY")
if not gemini_api_key:
    raise ValueError("Gemini API key not found. Please set GOOGLE_API_KEY environment variable.")

genai.configure(api_key=gemini_api_key)
client = GenerativeModel('gemini-2.5-flash-preview-04-17')

try:
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    print("✓ Successfully imported Google AI safety types.")
    default_safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
    vision_safety_settings = {
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
        # Add others if needed for vision, usually dangerous content is primary
    }
    mood_hint_safety_settings = default_safety_settings.copy() # Mood hint can use default

except ImportError:
    print("Warning: Google AI safety types not found. Safety features disabled.")
    default_safety_settings = {}
    vision_safety_settings = {}
    mood_hint_safety_settings = {}
# --- End Safety Settings Definition ---

#image_generation_client = GenerativeModel('gemini-2.0-flash-exp-image-generation')
#print(f"*** DEBUG POINT 1 ***")
#print(f"   Assigned Image Client Model Name: {image_generation_client.model_name}")
#print(f"   Assigned Image Client Object ID: {id(image_generation_client)}")

def list_available_models():
    """List all available Gemini models"""
    try:
        models = genai.list_models()
        print("\nAvailable Gemini Models:")
        print("========================")
        for model in models:
            print(f"Name: {model.name}")
            print(f"Description: {model.description}")
            print(f"Generation Methods: {model.supported_generation_methods}")
            print("------------------------")
        return models
    except Exception as e:
        print(f"Error listing models: {e}")
        return None

# Get available models
print("Checking available models...")
available_models = list_available_models()

# Update the model initialization based on what's available
client = GenerativeModel('models/gemini-2.5-flash-preview-04-17')
# We'll pick the appropriate image model from the list

def check_sd_api_availability(api_url):
    """Checks if the Stable Diffusion API endpoint is reachable."""
    try:
        # Use a simple endpoint like /sdapi/v1/options which should exist
        response = requests.get(f"{api_url.rstrip('/')}/sdapi/v1/options", timeout=3)
        # Check for successful status code (2xx)
        if 200 <= response.status_code < 300:
            print(f"✓ Stable Diffusion API found at {api_url}")
            return True
        else:
            print(f"Warning: Stable Diffusion API responded at {api_url}, but with status {response.status_code}. Might be misconfigured.")
            return False
    except requests.exceptions.ConnectionError:
        print(f"Warning: Could not connect to Stable Diffusion API at {api_url}. Is it running with --api enabled?")
        return False
    except requests.exceptions.Timeout:
        print(f"Warning: Timed out connecting to Stable Diffusion API at {api_url}.")
        return False
    except Exception as e:
        print(f"Warning: Error checking Stable Diffusion API: {e}")
        return False
    
def synthesize_diary_themes():
    """
    Uses Gemini to analyze recent diary entries and identify recurring themes.
    Updates the global current_diary_themes variable.
    """
    global current_diary_themes, client # Need Gemini client

    print("DEBUG Diary Themes: Attempting to synthesize themes...")
    try:
        # Read a decent chunk of recent history for theme analysis
        # Adjust max_entries based on performance and desired context window
        entries = manage_silvie_diary('read', max_entries=25) # e.g., last 25 entries
        if not entries or len(entries) < 5: # Need a minimum number to find themes
            print("DEBUG Diary Themes: Not enough entries to synthesize themes.")
            current_diary_themes = None # Clear themes if not enough data
            return

        # Format entries for the prompt
        formatted_entries = ""
        for i, entry in enumerate(entries):
            content = entry.get('content', '')
            timestamp = entry.get('timestamp', '?')
            formatted_entries += f"Entry {i} ({timestamp}): {content[:150]}...\n" # Keep snippets reasonable

        # Construct the prompt for theme synthesis
        theme_prompt = (
            f"Analyze the following recent diary entries from Silvie:\n\n{formatted_entries}\n\n"
            f"Instruction: Identify 1-3 recurring themes, topics, moods, or concepts present in these entries. Be concise and list them separated by commas (e.g., 'Paper ghosts and data, Sense of wonder, Job transition'). If no clear themes emerge, respond ONLY with the word 'None'.\n\nIdentified Themes:"
        )

        # Define safety settings (reuse from call_gemini or define here)
        safety_settings = { # Example, adjust as needed
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            # ... add other categories as needed ...
        }

        # Call Gemini
        response = client.generate_content(theme_prompt, safety_settings=safety_settings)
        raw_themes = response.text.strip()

        if raw_themes.lower() == 'none':
            print("DEBUG Diary Themes: No specific themes identified by LLM.")
            current_diary_themes = None
        else:
            # Clean up the response (remove potential prefixes, etc.)
            cleaned_themes = raw_themes.replace("Identified Themes:", "").strip('."\' ')
            if cleaned_themes:
                current_diary_themes = cleaned_themes
                print(f"DEBUG Diary Themes: Updated themes to: '{current_diary_themes}'")
            else:
                # Handle case where LLM returns empty string despite instruction
                print("DEBUG Diary Themes: LLM returned empty string for themes.")
                current_diary_themes = None

    except Exception as e:
        print(f"ERROR synthesizing diary themes: {type(e).__name__} - {e}")
        traceback.print_exc()
        # Optional: Decide whether to clear themes on error or keep old ones
        # current_diary_themes = None

# --- End of synthesize_diary_themes function ---

def diary_theme_worker():
    """Periodically synthesizes diary themes."""
    global current_diary_themes, last_diary_theme_update, running # Add other globals synthesize_diary_themes needs (e.g., client)
    global client # Assuming synthesize_diary_themes needs the Gemini client

    # Use the same interval and initialize the timer
    interval = DIARY_THEME_UPDATE_INTERVAL
    if 'last_diary_theme_update' not in globals():
        last_diary_theme_update = 0.0 # Initialize differently here, worker controls timing

    print("Diary Theme worker: Starting.", flush=True)

    # Optional: Initial delay before first synthesis, similar to other workers
    initial_theme_delay = 60 # e.g., wait 60 seconds
    sleep_start = time.time()
    while time.time() - sleep_start < initial_theme_delay:
         if not running:
             print("Diary Theme worker: Exiting during initial delay.", flush=True)
             return
         time.sleep(1)
    print(f"Diary Theme worker: Initial delay complete. First synthesis attempt.", flush=True)

    while running:
        try:
            # Check if it's time to update (or first run after delay)
            current_time = time.time()
            # Use >= just to be safe
            if current_time - last_diary_theme_update >= interval:
                print("Diary Theme worker: Interval reached. Synthesizing themes...", flush=True)
                try:
                    # Call the synthesis function (ensure it's defined and accessible)
                    synthesize_diary_themes() # This function should update the global current_diary_themes
                    last_diary_theme_update = current_time # Update time ONLY on successful run
                    print(f"Diary Theme worker: Synthesis complete. Next check in {interval}s.", flush=True)
                except NameError:
                    print("CRITICAL ERROR: synthesize_diary_themes function is not defined or accessible!", flush=True)
                    # Stop this worker if the function is missing? Or just wait longer? Let's wait.
                    last_diary_theme_update = current_time # Still update time to avoid rapid retries
                except Exception as theme_err:
                    print(f"ERROR in diary_theme_worker calling synthesize_diary_themes: {theme_err}", flush=True)
                    traceback.print_exc()
                    # Don't update timestamp on error, try again after standard sleep

            # Sleep for a short period before checking again
            check_interval = 60 # Check every minute if it's time to synthesize
            sleep_end = time.time() + check_interval
            while time.time() < sleep_end:
                if not running: break
                time.sleep(1)

        except Exception as e:
            print(f"!!! Diary Theme Worker Error (Outer Loop): {type(e).__name__} - {e} !!!", flush=True)
            traceback.print_exc()
            # Wait longer after a major error in the worker loop itself
            error_wait_start = time.time()
            while time.time() - error_wait_start < 300: # Wait 5 minutes
                 if not running: break
                 time.sleep(10)

    print("Diary Theme worker: Loop exited.", flush=True)

def synthesize_long_term_reflections():
    """
    Reads diary entries and uses Gemini to summarize long-term trends/reflections.
    Updates the global long_term_reflection_summary variable.
    """
    global long_term_reflection_summary, client, default_safety_settings # Need client and safety settings

    print("DEBUG Long-Term Memory: Attempting to synthesize long-term reflections...", flush=True)
    try:
        # Read ALL diary entries (consider sampling/limiting if diary gets huge)
        # Let's start by reading all for simplicity
        entries = manage_silvie_diary('read', max_entries='all') # Assumes this function exists

        if not entries or len(entries) < 10: # Need a reasonable number for long-term view
            print("DEBUG Long-Term Memory: Not enough entries for meaningful long-term summary.", flush=True)
            long_term_reflection_summary = None # Clear summary if not enough data
            return

        # Format entries concisely for the prompt (to manage token limits)
        # Maybe use only timestamp and first sentence/snippet? Adjust snippet length as needed.
        formatted_entries = ""
        max_context_entries = 100 # Limit how many entries we actually put in the prompt if diary is huge
        entries_to_process = entries[-max_context_entries:] # Take the last N entries
        entry_count_processed = 0
        for entry in entries_to_process:
            content = entry.get('content', '')
            timestamp = entry.get('timestamp', '?')
            # Keep snippets relatively short for the summary prompt
            formatted_entries += f"- Entry from ~{timestamp}: \"{content[:100]}...\"\n"
            entry_count_processed += 1
            # Optional: Add a hard limit on total prompt length if needed

        print(f"DEBUG Long-Term Memory: Processing {entry_count_processed} entries for summary prompt.", flush=True)

        # Construct the prompt for long-term synthesis
        summary_prompt = (
            f"Analyze the following diary entries from Silvie, spanning potentially weeks or months:\n\n"
            f"--- DIARY ENTRIES START ---\n"
            f"{formatted_entries}"
            f"--- DIARY ENTRIES END ---\n\n"
            f"Instruction: Identify 1-3 significant long-term recurring themes, major shifts in perspective, core personality aspects revealed over time, or particularly impactful past reflections evident across *these entries*. Focus on patterns or insights that emerge over the longer term, not just the most recent few days. Summarize these long-term reflections concisely (1-2 sentences maximum).\n\n"
            f"Long-Term Reflections Summary:"
        )

        # Call Gemini
        # print(f"DEBUG Long-Term Memory Prompt:\n{summary_prompt}\n--- END PROMPT ---", flush=True) # Uncomment for extreme debugging
        response = client.generate_content(summary_prompt, safety_settings=default_safety_settings) # Use appropriate safety
        raw_summary = response.text.strip()

        # Clean up the response
        cleaned_summary = raw_summary.replace("Long-Term Reflections Summary:", "").strip('."\' ')
        if cleaned_summary and len(cleaned_summary) > 5: # Basic check for non-empty/meaningful summary
            long_term_reflection_summary = cleaned_summary
            print(f"DEBUG Long-Term Memory: Updated summary to: '{long_term_reflection_summary}'", flush=True)
        else:
            print(f"DEBUG Long-Term Memory: LLM returned empty or invalid summary: '{raw_summary}'", flush=True)
            long_term_reflection_summary = None # Clear if LLM fails

    except NameError as ne:
         print(f"CRITICAL ERROR: Required function/global missing for long-term summary: {ne}", flush=True)
         long_term_reflection_summary = None # Clear on error
    except Exception as e:
        print(f"ERROR synthesizing long-term reflections: {type(e).__name__} - {e}", flush=True)
        traceback.print_exc()
        long_term_reflection_summary = None # Clear on error

# --- End of synthesize_long_term_reflections function ---

def long_term_memory_worker():
    """Periodically synthesizes long-term reflections from the diary."""
    global last_long_term_memory_update, running # Add other globals needed by synthesize_long_term_reflections if any

    interval = LONG_TERM_MEMORY_INTERVAL
    # Initialize timer correctly for the worker
    if 'last_long_term_memory_update' not in globals() or last_long_term_memory_update == 0.0:
        # Optionally delay first run significantly, or run sooner after startup
        # Let's make it run relatively soon after startup delay allows other things to load
        initial_memory_delay = 90 # e.g., wait 5 minutes after app start
        last_long_term_memory_update = time.time() - interval + initial_memory_delay
    print(f"Long-Term Memory worker: Starting. Next check around: {datetime.fromtimestamp(last_long_term_memory_update + interval)}", flush=True)


    while running:
        try:
            current_time = time.time()
            # Check if interval has passed
            if current_time - last_long_term_memory_update >= interval:
                print(f"Long-Term Memory worker: Interval ({interval}s) reached. Synthesizing...", flush=True)
                try:
                    # Call the synthesis function (ensure it's defined above)
                    synthesize_long_term_reflections()
                    last_long_term_memory_update = current_time # Update time ONLY on success/attempt
                    print(f"Long-Term Memory worker: Synthesis attempt complete. Next check in ~{interval/3600:.1f} hours.", flush=True)
                except Exception as synth_err:
                    # Catch errors during the call itself, though internal errors are handled in synthesize_long_term_reflections
                    print(f"ERROR calling synthesize_long_term_reflections from worker: {synth_err}", flush=True)
                    traceback.print_exc()
                    # Don't update timestamp on direct call error, retry sooner maybe? Or update anyway? Let's update to avoid rapid retries on call errors.
                    last_long_term_memory_update = current_time

            # Sleep for a longer check interval as this runs less frequently
            check_interval = 300 # Check every 5 minutes if it's time to summarize
            sleep_end = time.time() + check_interval
            while time.time() < sleep_end:
                if not running: break
                time.sleep(1)

        except Exception as e:
            print(f"!!! Long-Term Memory Worker Error (Outer Loop): {type(e).__name__} - {e} !!!", flush=True)
            traceback.print_exc()
            # Wait longer after a major error
            error_wait_start = time.time()
            while time.time() - error_wait_start < 600: # Wait 10 minutes
                 if not running: break
                 time.sleep(15)

    print("Long-Term Memory worker: Loop exited.", flush=True)

# --- End of long_term_memory_worker function ---

def get_weather_description(code):
    """Translates WMO weather codes from Open-Meteo into simple descriptions."""
    # Based on WMO Weather interpretation codes (https://open-meteo.com/en/docs)
    if code == 0: return "Clear sky"
    elif code == 1: return "Mainly clear"
    elif code == 2: return "Partly cloudy"
    elif code == 3: return "Overcast"
    elif code == 45: return "Foggy"
    elif code == 48: return "Depositing rime fog" # Still foggy, essentially
    elif code in [51, 53, 55]: return "Drizzle" # Light, moderate, dense
    elif code in [56, 57]: return "Freezing Drizzle" # Light, dense
    elif code in [61, 63, 65]: return "Rain" # Slight, moderate, heavy
    elif code in [66, 67]: return "Freezing Rain" # Light, heavy
    elif code in [71, 73, 75]: return "Snowfall" # Slight, moderate, heavy
    elif code == 77: return "Snow grains"
    elif code in [80, 81, 82]: return "Rain showers" # Slight, moderate, violent
    elif code in [85, 86]: return "Snow showers" # Slight, heavy
    elif code == 95: return "Thunderstorm" # Slight or moderate
    elif code in [96, 99]: return "Thunderstorm with hail" # Slight/heavy hail
    else: return f"Weather code {code}" # Fallback for unknown codes

def fetch_weather_data(latitude, longitude):
    """Fetches current weather from Open-Meteo."""
    global current_weather_info # Allow updating the global variable
    api_url = f"https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'current': 'temperature_2m,weather_code', # Request temp and weather code
        'temperature_unit': 'fahrenheit', # Or 'celsius' if you prefer
        'wind_speed_unit': 'mph', # Optional, can add wind later if desired
        'timezone': 'America/New_York' # Important for accurate timing
    }
    try:
        response = requests.get(api_url, params=params, timeout=10) # Added timeout
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()

        if 'current' in data:
            temp = data['current']['temperature_2m']
            code = data['current']['weather_code']
            description = get_weather_description(code)
            temp_unit = '°F' if params['temperature_unit'] == 'fahrenheit' else '°C'

            # Prepare the info dictionary
            weather_update = {
                'condition': description,
                'temperature': round(temp), # Round temperature
                'unit': temp_unit
            }
            print(f"Weather Debug: Fetched - {weather_update}") # Debug output
            return weather_update # Return the dictionary
        else:
            print("Weather Error: 'current' key not found in API response.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Weather Error: API request failed - {e}")
        return None
    except json.JSONDecodeError:
        print("Weather Error: Failed to parse API response.")
        return None
    except Exception as e:
        print(f"Weather Error: An unexpected error occurred - {e}")
        return None
    
def weather_update_worker():
    """Periodically fetches and updates weather information."""
    global current_weather_info, running
    print("Weather worker: Starting.")
    while running:
        try:
            print("Weather worker: Attempting fetch...")
            fetched_data = fetch_weather_data(BELFAST_LAT, BELFAST_LON)
            if fetched_data:
                current_weather_info = fetched_data
                print(f"Weather worker: Updated global weather info to: {current_weather_info}")
            else:
                print("Weather worker: Fetch failed, keeping previous info (if any).")

            # Wait for the defined interval before the next fetch
            # Check the running flag periodically during sleep
            sleep_start = time.time()
            while time.time() - sleep_start < WEATHER_UPDATE_INTERVAL:
                 if not running:
                     break # Exit sleep early if app is closing
                 time.sleep(5) # Check every 5 seconds

        except Exception as e:
            print(f"Weather Worker Error (Outer Loop): {type(e).__name__} - {e}")
            # Wait a bit longer after an error before retrying
            time.sleep(300) # Wait 5 minutes after an error

    print("Weather worker: Loop exited.")

def fetch_sunrise_sunset(latitude, longitude):
    """Fetches sunrise and sunset times for a given lat/lon."""
    api_url = f"https://api.sunrise-sunset.org/json?lat={latitude}&lng={longitude}&formatted=0"
    print(f"DEBUG EnvCtx: Fetching sunrise/sunset from {api_url}")
    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        data = response.json()

        if data.get('status') == 'OK' and 'results' in data:
            results = data['results']
            sunrise_utc_str = results.get('sunrise')
            sunset_utc_str = results.get('sunset')
            if not sunrise_utc_str or not sunset_utc_str:
                 print("Error EnvCtx: Sunrise/Sunset data missing in API response.")
                 return None, None
            try:
                utc_tz = pytz.utc; local_tz = pytz.timezone(BELFAST_TZ) # Assumes pytz imported
                sunrise_utc = dateutil_parse(sunrise_utc_str).replace(tzinfo=utc_tz) # Assumes dateutil_parse imported
                sunset_utc = dateutil_parse(sunset_utc_str).replace(tzinfo=utc_tz)
                sunrise_local = sunrise_utc.astimezone(local_tz)
                sunset_local = sunset_utc.astimezone(local_tz)

                # --- FIXED FORMAT STRING ---
                # Use %I which works on all platforms (will have leading zero)
                sunrise_formatted = sunrise_local.strftime('%I:%M %p').lstrip('0') # lstrip('0') removes leading zero if present
                sunset_formatted = sunset_local.strftime('%I:%M %p').lstrip('0') # lstrip('0') removes leading zero if present
                # --- END FIX ---

                print(f"DEBUG EnvCtx: Sunrise={sunrise_formatted}, Sunset={sunset_formatted} ({BELFAST_TZ})")
                return sunrise_formatted, sunset_formatted
            except Exception as parse_err:
                print(f"Error EnvCtx: Failed to parse/convert times: {parse_err}")
                return None, None
        else:
            print(f"Error EnvCtx: Sunrise-Sunset API status not OK. Status: {data.get('status')}")
            return None, None
    # ... (Keep existing exception handling for requests, json, etc.) ...
    except requests.exceptions.RequestException as e:
        print(f"Error EnvCtx: Sunrise-Sunset API request failed - {e}")
        return None, None
    except json.JSONDecodeError:
        print("Error EnvCtx: Failed to parse Sunrise-Sunset API response.")
        return None, None
    except Exception as e:
        print(f"Error EnvCtx: Unexpected error fetching sunrise/sunset - {type(e).__name__}: {e}")
        return None, None

def get_moon_phase_name(illumination_percent):
    """Converts moon illumination percentage to a phase name."""
    if illumination_percent is None: return "Unknown Phase"
    # Approximate boundaries - these can be refined
    if illumination_percent < 5: return "New Moon"
    if illumination_percent < 20: return "Waxing Crescent"
    if illumination_percent < 45: return "First Quarter" # Technically centered at 50% but waxing
    if illumination_percent < 55: return "First Quarter" # Centered around 50%
    if illumination_percent < 80: return "Waxing Gibbous"
    if illumination_percent < 95: return "Waxing Gibbous" # Still mostly full
    if illumination_percent <= 100: return "Full Moon" # Allow exactly 100
    # Note: The API might not give waning phases directly this way.
    # A more complex calculation using day of cycle is needed for perfect accuracy,
    # but this gives a reasonable waxing/full state based on illumination alone.
    # We'll rely on the LLM's general knowledge if it needs more nuance.
    return "Unknown Phase" # Fallback

def fetch_moon_phase(latitude=None, longitude=None):
    """
    Fetches moon phase name using wttr.in (no API key required).
    NOTE: Ignores latitude and longitude for this specific API endpoint,
          but keeps the signature consistent for compatibility with the worker.
    """
    # The URL requests only the moon phase name (%m)
    api_url = "https://wttr.in/Moon?format=%m"
    print(f"DEBUG EnvCtx: Fetching moon phase from wttr.in: {api_url}")

    try:
        response = requests.get(api_url, timeout=15) # Use a reasonable timeout
        response.raise_for_status() # Check for HTTP errors (4xx/5xx)

        # Get the plain text response and remove any leading/trailing whitespace
        moon_phase = response.text.strip()

        if moon_phase: # Check if we actually got a non-empty string
            print(f"DEBUG EnvCtx: Moon Phase (wttr.in) = {moon_phase}")
            return moon_phase # Success! Return the phase name string
        else:
            # Handle cases where the API might return an empty string unexpectedly
            print("Error EnvCtx: wttr.in returned an empty response for moon phase.")
            return None # Indicate failure

    except requests.exceptions.Timeout:
        print("Error EnvCtx: wttr.in request timed out.")
        return None
    except requests.exceptions.RequestException as e:
        # This catches connection errors, HTTP errors (like 404, 503), etc.
        print(f"Error EnvCtx: Failed to fetch moon phase from wttr.in - {e}")
        # Log extra details if available from the response object within the exception
        if hasattr(e, 'response') and e.response is not None:
             print(f"  -> Status: {e.response.status_code}, Body: {e.response.text[:200]}...")
        return None
    except Exception as e:
        # Catch any other unexpected errors during the process
        print(f"Error EnvCtx: Unexpected error fetching wttr.in moon phase - {type(e).__name__}: {e}")
        traceback.print_exc() # Log full traceback for unexpected issues
        return None

# --- End of new functions ---

def environmental_context_worker():
    """Periodically fetches sunrise/sunset and moon phase."""
    global current_sunrise_time, current_sunset_time, current_moon_phase, running # Allow updating globals

    print("Environmental Context worker: Starting.")
    # Initial fetch attempt shortly after start
    initial_delay = 30 # seconds
    sleep_start = time.time()
    while time.time() - sleep_start < initial_delay:
         if not running:
             print("Environmental Context worker: Exiting during initial delay.")
             return
         time.sleep(1)

    while running:
        print("Environmental Context worker: Attempting fetch cycle...")
        try:
            # Fetch Sunrise/Sunset
            sunrise, sunset = fetch_sunrise_sunset(BELFAST_LAT, BELFAST_LON)
            if sunrise and sunset:
                current_sunrise_time = sunrise
                current_sunset_time = sunset
            else:
                 print("Environmental Context worker: Failed to update sunrise/sunset times.")
                 # Optionally keep old values or set to None? Let's keep old for now.

            # Fetch Moon Phase
            phase = fetch_moon_phase(BELFAST_LAT, BELFAST_LON)
            if phase:
                current_moon_phase = phase
            else:
                 print("Environmental Context worker: Failed to update moon phase.")
                 # Keep old value

            print(f"Environmental Context worker: Update complete. Sunrise: {current_sunrise_time}, Sunset: {current_sunset_time}, Moon: {current_moon_phase}")

            # Wait for the defined interval
            print(f"Environmental Context worker: Waiting for {ENVIRONMENTAL_UPDATE_INTERVAL} seconds...")
            sleep_start = time.time()
            while time.time() - sleep_start < ENVIRONMENTAL_UPDATE_INTERVAL:
                 if not running: break
                 time.sleep(15) # Check running flag periodically

        except Exception as e:
            print(f"Environmental Context Worker Error (Outer Loop): {type(e).__name__} - {e}")
            traceback.print_exc()
            # Wait longer after an error before retrying
            print("Environmental Context worker: Waiting 5 minutes after error...")
            error_wait_start = time.time()
            while time.time() - error_wait_start < 300: # Wait 5 mins
                 if not running: break
                 time.sleep(10)

        if not running: break # Exit loop if running flag became false

    print("Environmental Context worker: Loop exited.")

# --- End of new worker function ---

# Make sure 'os' is imported
# Make sure BLUESKY_AVAILABLE, BLUESKY_HANDLE, BLUESKY_APP_PASSWORD globals are defined BEFORE this function
# Make sure 'Client' from 'atproto' is imported if BLUESKY_AVAILABLE is True

# Keep this import at the top: from atproto import Client, models
# Keep the global variable near the top: bluesky_client = None

# Ensure these imports are present near the top of your file:
# from PIL import ImageChops # You might need Image as well
# global last_screenshot # Ensure this global is accessible

def should_process_screenshot(new_shot):
    """Determine if screenshot is different enough to process"""
    global last_screenshot # Need access to the previous screenshot
    if last_screenshot is None:
        return True # Always process the first screenshot

    try:
        # Compare with last screenshot to detect significant changes
        # Make sure ImageChops is imported from PIL
        diff = ImageChops.difference(last_screenshot, new_shot)
        bbox = diff.getbbox() # Get the bounding box of changed pixels
        if bbox is None:
            # If no bounding box, images are identical (or very close)
            return False

        # Optional: Calculate change percentage (can be slow, bbox check is often enough)
        # total_pixels = new_shot.size[0] * new_shot.size[1]
        # changed_pixels = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        # change_percent = (changed_pixels / total_pixels) * 100
        # print(f"Screen change: {change_percent:.2f}%") # Debug output
        # return change_percent > 5 # Example threshold

        # Simpler check: If there's *any* bounding box, there's a difference.
        return True

    except Exception as e:
        print(f"Screenshot comparison error: {e}")
        return True # Process on error to be safe
    
# Ensure necessary imports are present near the top:
# import base64
# import os
# import time
# from datetime import datetime
# Assume client (Gemini client), conversation_history, output_box, tts_queue, root,
# update_status, save_conversation_history, SCREEN_MESSAGE,
# last_screenshot_time, last_screenshot, MIN_SCREENSHOT_INTERVAL are defined/global

def process_screenshot(screenshot):
    """Process the screenshot and send to Gemini"""
    # Access globals needed within this function
    global last_screenshot_time, last_screenshot, client, conversation_history
    global output_box, tts_queue, root, SCREEN_MESSAGE, MIN_SCREENSHOT_INTERVAL
    global MAX_HISTORY_LENGTH # Needed for history management

    try:
        current_time = time.time()
        # Check cooldown
        if current_time - last_screenshot_time < MIN_SCREENSHOT_INTERVAL:
            remaining = int(MIN_SCREENSHOT_INTERVAL - (current_time - last_screenshot_time))
            update_status(f"👀 Cooling down ({remaining}s)...")
            return # Exit if cooling down

        # Save temporary file (ensure 'os' is imported)
        temp_path = "temp_screenshot.jpg"
        screenshot.save(temp_path)

        # Use shorter prompt for gameplay
        prompt = "Quick reaction to this game moment? (1-2 sentences)"

        # Use SCREEN_MESSAGE instead of SYSTEM_MESSAGE for screenshots
        # Ensure 'base64' is imported
        with open(temp_path, 'rb') as img_file:
            img_bytes = img_file.read()
            contents = [{
                "parts": [
                    {"text": f"{SCREEN_MESSAGE}\n\nScreen shows: {prompt}\nSilvie briefly comments:"},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg", # Assumes JPG, adjust if needed
                            "data": base64.b64encode(img_bytes).decode('utf-8')
                        }
                    }
                ]
            }]
            # Ensure 'client' (Gemini client) is defined and accessible
            # Add safety settings if appropriate for your model/use case
            # safety_settings_screen = { HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE }
            reply = client.generate_content(contents).text # Consider adding safety_settings=safety_settings_screen

        # Only proceed if we got a new, different reply
        # Initialize last_reply if it doesn't exist
        if not hasattr(process_screenshot, 'last_reply'):
            process_screenshot.last_reply = None

        if reply != process_screenshot.last_reply:
            # Update tracking variables
            last_screenshot_time = current_time
            # last_screenshot = screenshot.copy() # This is already updated in monitor_worker
            process_screenshot.last_reply = reply # Store the new reply

            # Add to conversation and speak
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Manage history length before appending
            if len(conversation_history) >= MAX_HISTORY_LENGTH * 2:
                conversation_history.pop(0) # Remove oldest user/system turn
                if conversation_history: conversation_history.pop(0) # Remove oldest Silvie turn
            # Log appropriately
            conversation_history.append(f"[{timestamp}] Screen Comment Context: {prompt}") # Log the prompt used
            conversation_history.append(f"[{timestamp}] Silvie (Screen): {reply}") # Log Silvie's response

            # Update GUI (ensure 'root', 'output_box', 'tk' are accessible)
            if root and root.winfo_exists():
                def update_gui_screen_comment(msg=reply):
                    try:
                        output_box.config(state=tk.NORMAL)
                        output_box.insert(tk.END, f"Silvie (Screen): {msg}\n\n")
                        output_box.config(state=tk.DISABLED)
                        output_box.see(tk.END)
                    except Exception as e_gui: print(f"Screen comment GUI error: {e_gui}")
                root.after(0, update_gui_screen_comment, reply)

            # Queue for TTS (ensure 'tts_queue' is accessible)
            if tts_queue and reply:
                tts_queue.put(reply)

            # Save history (ensure function exists)
            # Consider moving this save outside if saving too frequently causes issues
            save_conversation_history()
        else:
            update_status("Waiting for new content...") # Screenshot hasn't changed significantly

        # Cleanup (ensure 'os' is imported)
        if os.path.exists(temp_path):
            os.remove(temp_path)

    except Exception as e:
        print(f"Screenshot processing error: {e}")
        update_status("Screenshot processing error")
        # Attempt cleanup even on error
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try: os.remove(temp_path)
            except Exception as cleanup_err: print(f"Error cleaning up temp screenshot: {cleanup_err}")

def pull_tarot_cards(count=1):
    """
    Pulls a specified number of random tarot cards from the LOCAL API.
    Uses the /onecard endpoint, making multiple calls if count > 1.
    """
    try:
        num_to_pull = int(count)
        if num_to_pull < 1: num_to_pull = 1
    except (ValueError, TypeError):
        print("Error Tarot: Invalid count provided, defaulting to 1.")
        num_to_pull = 1

    drawn_cards = []
    print(f"DEBUG Tarot: Pulling {num_to_pull} card(s) from local API ({TAROT_API_BASE_URL})") # Assumes TAROT_API_BASE_URL is http://localhost:3000/cards

    for i in range(num_to_pull): # Loop to pull the required number of cards
        endpoint = f"{TAROT_API_BASE_URL}/onecard" # Use the specific endpoint for one card
        print(f"DEBUG Tarot: Calling endpoint {i+1}/{num_to_pull}: {endpoint}")
        try:
            response = requests.get(endpoint, timeout=10)
            response.raise_for_status()
            data = response.json()

            # --- Check for expected keys from local API ---
            if data and isinstance(data, dict) and "name" in data and "description" in data:
                drawn_cards.append(data)
                print(f"DEBUG Tarot: Successfully received card: {data.get('name', 'Unknown')}")
            else:
                print(f"Error Tarot: Unexpected response format from local API /onecard. Missing 'name' or 'description'. Data: {data}")
                return None # Indicate failure if format is wrong

        except requests.exceptions.ConnectionError:
             print(f"Error Tarot: Cannot connect to local API at {endpoint}. Is it running?")
             return None
        except requests.exceptions.Timeout:
             print(f"Error Tarot: Local API request timed out.")
             return None
        except requests.exceptions.RequestException as e:
             print(f"Error Tarot: Local API request failed - {e}")
             if hasattr(e, 'response') and e.response is not None:
                 print(f"Error Tarot: Response Status Code: {e.response.status_code}")
                 print(f"Error Tarot: Response Text: {e.response.text[:500]}...")
             return None
        except json.JSONDecodeError:
             print(f"Error Tarot: Failed to parse local API response (not valid JSON). Response text: {response.text[:200]}...")
             return None
        except Exception as e:
             print(f"Error Tarot: An unexpected error occurred - {type(e).__name__}: {e}")
             traceback.print_exc()
             return None

        if num_to_pull > 1 and i < num_to_pull - 1: time.sleep(0.1) # Small delay between calls

    if len(drawn_cards) == num_to_pull:
        return drawn_cards
    else:
        print(f"Error Tarot: Failed to draw the expected number of cards ({len(drawn_cards)}/{num_to_pull}).")
        return None
# --- End of pull_tarot_cards function ---

# Rename update_tarot_image_gui to _update_image_label_safe
# Make sure it uses the global image_label

def _update_image_label_safe(image_path):
    """Loads, resizes, and displays an image in the main image_label via root.after."""
    global image_label, TAROT_THUMBNAIL_SIZE, root # Use image_label

    # Use TAROT_THUMBNAIL_SIZE for tarot cards, maybe define a different default?
    # Or pass size as an argument? Let's keep TAROT_THUMBNAIL_SIZE for now.
    display_size = TAROT_THUMBNAIL_SIZE

    if not image_label or not root or not root.winfo_exists():
        print("DEBUG GUI Update: Label or root window missing.")
        return

    if not image_path or not os.path.exists(image_path):
        print(f"DEBUG GUI Update: Image path invalid or file not found: '{image_path}'. Clearing label.")
        image_label.config(image='') # Clear the main image_label
        image_label.image = None # Clear reference
        return

    try:
        with Image.open(image_path) as img:
            img.thumbnail(display_size) # Use the defined size
            photo = ImageTk.PhotoImage(img)

            image_label.config(image=photo) # Update the main image_label
            image_label.image = photo # Keep a reference! Crucial.
            print(f"DEBUG GUI Update: Displayed image '{os.path.basename(image_path)}' in main label.")

    except UnidentifiedImageError:
        print(f"Error GUI Update: Pillow could not identify image file: {image_path}")
        image_label.config(image='')
        image_label.image = None
    except Exception as e:
        print(f"Error GUI Update: Failed to load or display image '{image_path}': {e}")
        traceback.print_exc()
        image_label.config(image='')
        image_label.image = None

def setup_reddit():
    """
    Handles Reddit Authentication using the credentials loaded at startup.
    Returns a PRAW Reddit instance on success, None on failure.
    """
    try:
        print("Attempting Reddit authentication...")
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            username=REDDIT_USERNAME,
            password=REDDIT_PASSWORD,
            user_agent=REDDIT_USER_AGENT,
        )

        # Verify authentication (optional, but recommended)
        user = reddit.user.me()
        if user:
            print(f"✓ Reddit authenticated successfully for user: {user.name}")
            return reddit
        else:
            print("✗ Reddit authentication failed: Could not verify user.")
            return None

    except Exception as e:
        print(f"✗ Reddit authentication failed: {type(e).__name__} - {e}")
        traceback.print_exc()
        return None

def get_reddit_posts(subreddit_name="all", limit=10):
    """
    Fetches posts from a specified subreddit.
    Returns a list of post dictionaries on success, or an error string on failure.
    """
    global reddit_client

    if not reddit_client:
        return "Reddit client not initialized. Check credentials?"

    try:
        print(f"Reddit: Fetching {limit} posts from subreddit: {subreddit_name}")
        subreddit = reddit_client.subreddit(subreddit_name)
        posts = []

        # Fetch the "hot" posts (you can change this to "new", "top", etc.)
        for submission in subreddit.hot(limit=limit):
            post_data = {
                "title": submission.title,
                "author": submission.author.name if submission.author else "[deleted]",
                "text": submission.selftext,
                "url": submission.url,
                "score": submission.score,
                "num_comments": submission.num_comments,
                "created_utc": submission.created_utc,
            }
            posts.append(post_data)

        print(f"Reddit: Successfully fetched {len(posts)} posts.")
        return posts

    except Exception as e:
        print(f"Error fetching Reddit posts: {type(e).__name__} - {e}")
        traceback.print_exc()
        return f"Couldn't fetch Reddit posts: {type(e).__name__}"

def reddit_context_worker():
    """Periodically fetches posts from followed subreddits for ambient context."""
    global current_reddit_context, running, reddit_client, SILVIE_FOLLOWED_SUBREDDITS
    print("Reddit context worker: Starting.")

    # Optional initial delay
    time.sleep(45)

    while running:
        try:
            # Check if client is ready, try to setup if not
            if not reddit_client or not hasattr(reddit_client.user, 'me'): # Basic check
                print("Reddit context worker: Client not ready, attempting setup...")
                temp_client = setup_reddit()
                if temp_client:
                    reddit_client = temp_client # Update global if successful
                else:
                    print("Reddit context worker: Setup failed, pausing before retry.")
                    time.sleep(600) # Wait 10 mins before retrying setup
                    continue # Skip fetch attempt

            print("Reddit context worker: Attempting fetch...")
            aggregated_context = []
            fetched_something = False

            # Shuffle subreddits to vary which ones get checked if list is long
            random.shuffle(SILVIE_FOLLOWED_SUBREDDITS)

            for sub_name in SILVIE_FOLLOWED_SUBREDDITS[:5]: # Limit check to avoid rate limits
                posts_result = get_reddit_posts(subreddit_name=sub_name, limit=REDDIT_CONTEXT_POST_COUNT_PER_SUB)

                if isinstance(posts_result, list) and posts_result:
                    fetched_something = True
                    sub_context = f"r/{sub_name}: " + "; ".join([
                        f"'{p.get('title', '?')[:50]}...'" # Keep snippets short
                        for p in posts_result
                    ])
                    aggregated_context.append(sub_context)
                elif isinstance(posts_result, str): # Error fetching this sub
                    print(f"Reddit context worker: Error fetching r/{sub_name}: {posts_result}")
                # Handle empty list case silently or log if needed

                time.sleep(2) # Small delay between subreddit fetches

            if fetched_something:
                current_reddit_context = "[[Recent Reddit Snippets: " + " | ".join(aggregated_context) + "]]\n"
                print(f"Reddit context worker: Updated context.")
                # print(f"DEBUG Reddit Context: {current_reddit_context}") # Uncomment for verbose debug
            else:
                # Optionally clear context or keep old one
                # current_reddit_context = None
                print("Reddit context worker: No new Reddit posts found for context.")

            # Wait for the next interval
            print(f"Reddit context worker: Waiting for {REDDIT_CONTEXT_INTERVAL} seconds...")
            sleep_start = time.time()
            while time.time() - sleep_start < REDDIT_CONTEXT_INTERVAL:
                if not running: break
                time.sleep(15)

        except praw.exceptions.PRAWException as praw_err:
             print(f"Reddit Context Worker Error (PRAW): {type(praw_err).__name__} - {praw_err}")
             if "authenticat" in str(praw_err).lower(): # Attempt re-auth on auth errors
                  print("Reddit context worker: Authentication error detected, clearing client.")
                  reddit_client = None # Force setup attempt next cycle
             time.sleep(300) # Wait 5 minutes after PRAW error
        except Exception as e:
            print(f"Reddit Context Worker Error (Outer Loop): {type(e).__name__} - {e}")
            traceback.print_exc()
            time.sleep(300) # Wait 5 minutes after general error

    print("Reddit context worker: Loop exited.")

def post_reddit_comment(submission_id, comment_text):
    """Posts a comment to a given Reddit submission."""
    global reddit_client # Ensure PRAW client is accessible

    if not reddit_client or not hasattr(reddit_client.user, 'me'):
        print("Cannot comment: Reddit client not ready.")
        return False, "Reddit client unavailable."
    if not submission_id or not comment_text:
        return False, "Missing submission ID or comment text."

    try:
        print(f"Reddit Comment: Attempting to comment on submission ID: {submission_id}")
        submission = reddit_client.submission(id=submission_id)
        # Ensure the submission is commentable (not archived/locked - PRAW might raise exception)
        reply_object = submission.reply(comment_text)
        print(f"Reddit Comment: Successfully posted comment ID: {reply_object.id}")
        return True, f"Commented successfully (ID: {reply_object.id})"

    except praw.exceptions.APIException as api_err:
        error_msg = f"Reddit API Error commenting: {api_err}"
        print(error_msg)
        # Check for common errors
        if "DELETED_COMMENT" in str(api_err).upper() or "SUBMISSION_NOT_FOUND" in str(api_err).upper():
             return False, "Post seems to be gone."
        elif "THREAD_LOCKED" in str(api_err).upper() or "SUBMISSION_ARCHIVED" in str(api_err).upper():
             return False, "Post is locked or archived."
        elif "RATELIMIT" in str(api_err).upper():
             return False, "Rate limit hit, try again later."
        else:
             return False, f"Reddit API said: {api_err}"
    except praw.exceptions.PRAWException as praw_err:
        print(f"PRAW Error during comment: {praw_err}")
        return False, f"PRAW Error: {praw_err}"
    except Exception as e:
        print(f"Unexpected error commenting on {submission_id}: {type(e).__name__} - {e}")
        traceback.print_exc()
        return False, "An unexpected error occurred during commenting."

def upvote_reddit_item(item_id):
    """Upvotes a Reddit submission or comment given its base36 ID."""
    global reddit_client

    if not reddit_client or not hasattr(reddit_client.user, 'me'):
        print("Cannot upvote: Reddit client not ready.")
        return False, "Reddit client unavailable."

    if not item_id:
        return False, "Missing item ID to upvote."

    try:
        print(f"Reddit Upvote: Attempting to upvote item ID: {item_id}")
        # PRAW can often figure out if it's a submission or comment from ID,
        # but creating the object explicitly might be safer if needed later.
        # For just upvoting, accessing directly might work.
        # Let's try fetching the generic object first.
        item = reddit_client.submission(id=item_id) # Assume submission first
        # Alternative if comments are also targeted: item = reddit_client.comment(id=item_id)
        # Or more generically: item = reddit_client.info(fullnames=[f"t3_{item_id}"])[0] # Gets submission
        #                       item = reddit_client.info(fullnames=[f"t1_{item_id}"])[0] # Gets comment

        # Check if already upvoted (PRAW might handle this, but explicit check can be clearer)
        # The 'likes' attribute is True for upvote, False for downvote, None for no vote
        if item.likes is True:
             print(f"Reddit Upvote: Already upvoted item {item_id}.")
             return True, "Already upvoted."

        item.upvote()
        print(f"Reddit Upvote: Successfully upvoted item {item_id}.")
        return True, f"Upvoted item {item_id}"

    except praw.exceptions.APIException as api_err:
        error_msg = f"Reddit API Error: {api_err}"
        print(error_msg)
        # Check for common voting errors
        if "USER_REQUIRED" in str(api_err).upper(): # Should not happen if client is authenticated
             return False, "Authentication error during upvote."
        elif "SUBMISSION_ARCHIVED" in str(api_err).upper() or "THREAD_LOCKED" in str(api_err).upper():
             return False, "Post is archived or locked."
        elif "DELETED_COMMENT" in str(api_err).upper() or "SUBMISSION_NOT_FOUND" in str(api_err).upper():
             return False, "The item seems to be gone."
        else: return False, f"Reddit API said: {api_err}"
    except praw.exceptions.PRAWException as praw_err:
        print(f"PRAW Error during upvote: {praw_err}")
        return False, f"PRAW Error: {praw_err}"
    except Exception as e:
        print(f"Unexpected error upvoting item {item_id}: {type(e).__name__} - {e}")
        traceback.print_exc()
        return False, "An unexpected error occurred during upvote."

def setup_bluesky():
    """Handles Bluesky Authentication using the credentials loaded at startup."""
    global bluesky_client

    if not BLUESKY_HANDLE or not BLUESKY_APP_PASSWORD:
        print("Bluesky setup skipped: Handle or App Password missing in bluesky.env.")
        return False

    try:
        print(f"Attempting Bluesky authentication for {BLUESKY_HANDLE}...")
        # Change this line:
        # client = Client()
        # TO THIS:
        client = AtpClient() # <--- Use the alias AtpClient

        # Now this should call the login method on the correct (atproto) client object
        profile = client.login(BLUESKY_HANDLE, BLUESKY_APP_PASSWORD)

        bluesky_client = client
        print(f"✓ Bluesky authenticated successfully for handle: {profile.handle}")
        return True

    except AttributeError as ae:
        # Hopefully this error is now gone!
        print(f"✗ Bluesky authentication failed (AttributeError): {ae}")
        print(f"  (Is the 'atproto' library installed correctly and up to date? Try: pip install --upgrade atproto)")
        bluesky_client = None
        return False
    except Exception as e:
        print(f"✗ Bluesky authentication failed: {type(e).__name__} - {e}")
        bluesky_client = None
        return False

    except AttributeError as ae:
        print(f"✗ Bluesky authentication failed (AttributeError): {ae}")
        print(f"  (Is the 'atproto' library installed correctly and up to date? Try: pip install --upgrade atproto)")
        # Don't exit immediately, let the script continue to see other potential errors
        bluesky_client = None
        return False # Indicate failure
    except Exception as e:
        print(f"✗ Bluesky authentication failed: {type(e).__name__} - {e}")
        bluesky_client = None
        return False
    
# Make sure time, threading, os are imported
# Assumes setup_bluesky() and get_bluesky_timeline_posts() are defined elsewhere
# Assumes global variables: current_bluesky_context, running, bluesky_client,
# BLUESKY_AVAILABLE, BLUESKY_CONTEXT_INTERVAL, BLUESKY_CONTEXT_POST_COUNT are accessible

def bluesky_context_worker():
    """Periodically fetches Bluesky posts for ambient context."""
    global current_bluesky_context, running, bluesky_client # Allow access/modification

    if not BLUESKY_AVAILABLE:
        print("Bluesky context worker: Exiting, library not available.")
        return

    print("Bluesky context worker: Starting.")
    # Initial wait before first fetch? Optional, e.g., wait 60s
    initial_wait_start = time.time()
    while time.time() - initial_wait_start < 60:
         if not running:
             print("Bluesky context worker: Exiting during initial wait.")
             return
         time.sleep(1)

    while running:
        try:
            # Check if client exists and seems valid, otherwise try to set up
            # A simple check; might need refinement based on how atproto handles sessions
            if not bluesky_client or not hasattr(bluesky_client, 'me'):
                 print("Bluesky context worker: Client not ready, attempting setup...")
                 if not setup_bluesky(): # Try to setup/re-auth
                      print("Bluesky context worker: Setup failed, pausing before retry.")
                      # Wait longer if setup fails
                      sleep_start = time.time()
                      # Wait up to double the normal interval before retrying setup
                      while time.time() - sleep_start < BLUESKY_CONTEXT_INTERVAL * 2:
                           if not running: break
                           time.sleep(10)
                      continue # Skip fetching and try setup again next loop

            # --- Fetch Timeline Posts ---
            print("Bluesky context worker: Attempting fetch...")
            # Use the count defined in constants
            posts_result = get_bluesky_timeline_posts(count=BLUESKY_CONTEXT_POST_COUNT)

            if isinstance(posts_result, str): # Error occurred during fetch
                print(f"Bluesky context worker: Fetch failed - {posts_result}")
                # Decide how to handle error: clear context, keep old, set error message?
                # Let's clear it for now to avoid stale/misleading context.
                current_bluesky_context = None
            elif isinstance(posts_result, list): # Success (even if list is empty)
                if posts_result:
                    # Format the context string concisely for the LLM prompt
                    context_str = "[[Recent Bluesky Snippets:]]\n" + "".join(
                        # Limit text length, handle missing fields safely
                        [f"- {p.get('author', '?')}: {p.get('text', '')[:60]}...\n" for p in posts_result]
                    )
                    current_bluesky_context = context_str
                    print(f"Bluesky context worker: Updated context with {len(posts_result)} posts.")
                else: # Empty list returned
                    print("Bluesky context worker: Feed is empty.")
                    # Set context to indicate quiet feed
                    current_bluesky_context = "[[Recent Bluesky Snippets: Feed seems quiet.]]\n"
            else:
                 # Should not happen if get_bluesky_timeline_posts behaves correctly
                 print(f"Bluesky context worker: Unexpected result type from fetch: {type(posts_result)}")
                 current_bluesky_context = None # Clear context on unexpected result

            # --- Wait for the next interval ---
            print(f"Bluesky context worker: Waiting for {BLUESKY_CONTEXT_INTERVAL} seconds...")
            sleep_start = time.time()
            while time.time() - sleep_start < BLUESKY_CONTEXT_INTERVAL:
                 if not running: break # Exit sleep loop if app is closing
                 # Sleep in smaller chunks to remain responsive to the 'running' flag
                 time.sleep(5)

        except Exception as e:
            # Catch unexpected errors in the main loop
            print(f"Bluesky Context Worker Error (Outer Loop): {type(e).__name__} - {e}")
            import traceback
            traceback.print_exc()
            # Clear context and wait longer after an unexpected error
            current_bluesky_context = None
            print("Bluesky context worker: Waiting 5 minutes after error...")
            error_wait_start = time.time()
            while time.time() - error_wait_start < 300: # Wait 5 mins
                 if not running: break
                 time.sleep(10)

    print("Bluesky context worker: Loop exited.")

# Imports needed by this function (ensure they are present at the top of the file)
from datetime import datetime, timezone
# Make sure 'models' is imported from atproto if you need specific model types elsewhere,
# but this version relies less on direct type checking.
# e.g., from atproto import models (or from the aliased AtpClient if models are nested)

# Need access to the global bluesky_client and the setup_bluesky function defined elsewhere

# Imports needed by this function (ensure they are present at the top of the file)
from datetime import datetime, timezone
# from atproto import models # Might not be needed if we rely on py_type strings

# Need access to the global bluesky_client and the setup_bluesky function defined elsewhere

def get_bluesky_timeline_posts(count=10):
    """
    Fetches posts from the authenticated user's main timeline feed.
    Includes author's DID in the returned data.
    Returns a list of post dictionaries on success, or an error string on failure.
    """
    global bluesky_client

    # (Setup/Auth check remains the same)
    if not bluesky_client or not hasattr(bluesky_client, 'me'):
        print("Bluesky Timeline Fetch: Client not ready, attempting setup...")
        if not setup_bluesky(): return "Bluesky connection isn't ready. Check credentials?"
        if not bluesky_client: return "Bluesky setup failed, cannot fetch feed."

    try:
        print(f"Bluesky Timeline Fetch: Fetching timeline (limit {count})...")
        if not hasattr(bluesky_client, 'app') or not hasattr(bluesky_client.app, 'bsky') or not hasattr(bluesky_client.app.bsky, 'feed'):
             raise ConnectionError("Bluesky client object appears invalid or missing expected attributes (app.bsky.feed).")

        response = bluesky_client.app.bsky.feed.get_timeline({'limit': count})

        posts = []
        if response and hasattr(response, 'feed') and response.feed:
            print(f"Bluesky Timeline Fetch: Received {len(response.feed)} feed items.")
            for i, feed_view_post in enumerate(response.feed):
                post_data = getattr(feed_view_post, 'post', None)
                if not post_data:
                    # print(f"Bluesky Timeline Fetch: Skipping feed item {i+1} with no post data.") # Optional log
                    continue

                # --- Extract Author Info ---
                author_handle = 'unknown_author'
                author_did = None # <<< Initialize author_did
                author_info = getattr(post_data, 'author', None)
                if author_info:
                     if hasattr(author_info, 'handle'):
                         author_handle = author_info.handle
                     # <<< ADDED: Extract author DID >>>
                     if hasattr(author_info, 'did'):
                         author_did = author_info.did
                     # <<< END ADDED >>>

                # --- (Rest of text, record type, cid, timestamp extraction remains the same) ---
                text = ''; record = getattr(post_data, 'record', None); record_type_str = None
                if record:
                    if hasattr(record, 'py_type'): record_type_str = getattr(record, 'py_type', None)
                    elif isinstance(record, dict): record_type_str = record.get('py_type', record.get('$type'))

                    if record_type_str == 'app.bsky.feed.post':
                        if hasattr(record, 'text'): text = getattr(record, 'text', '')
                        elif isinstance(record, dict): text = record.get('text', '')

                        cid = getattr(post_data, 'cid', 'unknown_cid')
                        uri = getattr(post_data, 'uri', None) # <<< ADDED: Extract URI >>>
                        timestamp_iso = None; created_at_val = None
                        if hasattr(record, 'created_at'): created_at_val = getattr(record, 'created_at', None)
                        elif isinstance(record, dict): created_at_val = record.get('createdAt', record.get('created_at'))

                        if created_at_val:
                           # (Keep the existing timestamp parsing logic here)
                           if isinstance(created_at_val, str):
                               try:
                                   if '.' in created_at_val: # Handle fractional seconds
                                       parts = created_at_val.split('.'); fractional_part = parts[1]; tz_suffix = ''
                                       if 'Z' in fractional_part: tz_suffix = 'Z'; fractional_part = fractional_part.split('Z')[0]
                                       elif '+' in fractional_part: tz_suffix = '+' + fractional_part.split('+', 1)[1]; fractional_part = fractional_part.split('+', 1)[0]
                                       elif '-' in fractional_part: tz_suffix = '-' + fractional_part.split('-', 1)[1]; fractional_part = fractional_part.split('-', 1)[0]
                                       created_at_val = f"{parts[0]}.{fractional_part[:6]}{tz_suffix}" # Truncate
                                   created_dt = datetime.fromisoformat(created_at_val.replace('Z', '+00:00'))
                                   timestamp_iso = created_dt.isoformat()
                               except ValueError: timestamp_iso = created_at_val
                           elif isinstance(created_at_val, datetime): timestamp_iso = created_at_val.isoformat() if hasattr(created_at_val, 'isoformat') else str(created_at_val)
                           else: timestamp_iso = str(created_at_val)

                        # <<< MODIFIED: Append dictionary with all needed fields >>>
                        posts.append({
                            'author': author_handle,
                            'author_did': author_did, # Include author's DID
                            'text': text.strip(),
                            'uri': uri, # Include post URI
                            'cid': cid, # Include post CID
                            'timestamp': timestamp_iso
                        })
                        # <<< END MODIFIED >>>

                    else:
                        # print(f"DEBUG: Skipping feed item {i+1}. Record type: '{record_type_str}', Author: {author_handle}") # Optional log
                        continue
                else:
                    # print(f"Bluesky Timeline Fetch: Record data missing for feed item {i+1}.") # Optional log
                    continue
        else:
             print("Bluesky Timeline Fetch: Timeline response empty or missing 'feed' attribute.")

        print(f"Bluesky Timeline Fetch: Returning {len(posts)} parsed posts.")
        return posts

    except ConnectionError as ce:
        print(f"Error fetching Bluesky timeline: {ce}")
        return f"Couldn't fetch Bluesky timeline: Client structure issue."
    except Exception as e:
        print(f"Error fetching Bluesky timeline: {type(e).__name__} - {e}")
        traceback.print_exc()
        return f"Couldn't fetch Bluesky timeline: {type(e).__name__}"

# Needs access to global bluesky_client, setup_bluesky()
# Needs imports: from atproto import models # Ensure this is correct based on your import style
# Needs imports: from datetime import datetime, timezone
# Needs import: traceback

# Ensure these imports are at the top of your script file:
# from atproto import models # Or however you import models
# from datetime import datetime, timezone
# import traceback

# Assume global variable bluesky_client is defined and handled elsewhere
# Assume setup_bluesky() function is defined elsewhere

def search_bluesky_posts(search_query, limit=25):
    """
    Searches Bluesky posts for a given query string.

    Args:
        search_query (str): The term to search for in post content.
        limit (int): The maximum number of posts to return (default/max often 25-100).

    Returns:
        list: A list of post dictionaries containing author DID, URI, CID, text snippet, etc.
              Returns an empty list on failure or if no results are found.
        str: An error message string if a critical API error occurs.
    """
    global bluesky_client # Assumes setup_bluesky() handles authentication

    # Check client readiness
    if not BLUESKY_AVAILABLE: return "Bluesky library not available."
    if not bluesky_client or not hasattr(bluesky_client, 'me'):
        print("Bluesky Post Search: Client not ready, attempting setup...")
        if not setup_bluesky(): return "Bluesky connection isn't ready."
        if not bluesky_client: return "Bluesky setup failed, cannot search posts."

    print(f"Bluesky Post Search: Searching posts for query '{search_query}' (limit {limit})...")
    try:
        # Ensure endpoint exists on client object
        if not hasattr(bluesky_client, 'app') or not hasattr(bluesky_client.app, 'bsky') or not hasattr(bluesky_client.app.bsky.feed, 'search_posts'):
             raise ConnectionError("Bluesky client object appears invalid or missing expected attributes (app.bsky.feed.search_posts).")

        # Perform the search posts call
        # Note: Pagination for searchPosts uses a 'cursor' like getTimeline
        response = bluesky_client.app.bsky.feed.search_posts({'q': search_query, 'limit': limit})

        posts_data = []
        if response and hasattr(response, 'posts') and response.posts:
            print(f"Bluesky Post Search: Received {len(response.posts)} posts matching query.")
            for post_view in response.posts:
                # Extract necessary info directly from PostView structure
                # Ensure attribute names match the actual atproto library structure
                author_info = getattr(post_view, 'author', None)
                record_data = getattr(post_view, 'record', None) # <<< Check if 'record' is directly on PostView or nested

                # Sometimes the actual post content is nested further, e.g., post_view.post.record
                # You might need to inspect the 'post_view' object structure if 'record' isn't direct
                if not record_data and hasattr(post_view,'post') and hasattr(post_view.post,'record'):
                     record_data = post_view.post.record
                elif not record_data:
                     # print(f"Debug SearchPosts: Skipping post, no record data found directly or nested.") # Optional Debug
                     continue


                # --- Safely extract required fields ---
                author_did = getattr(author_info, 'did', None) if author_info else None
                author_handle = getattr(author_info, 'handle', 'unknown') if author_info else 'unknown'
                post_uri = getattr(post_view, 'uri', None)
                post_cid = getattr(post_view, 'cid', None)
                text_snippet = ""
                timestamp_iso = None

                # Get text from the record if it exists
                if record_data:
                    if hasattr(record_data, 'text'):
                        text_snippet = getattr(record_data, 'text', '')
                    elif isinstance(record_data, dict): # Fallback if record is a dict
                        text_snippet = record_data.get('text', '')

                    # Get timestamp from the record if it exists
                    created_at_val = None
                    if hasattr(record_data, 'created_at'): created_at_val = getattr(record_data, 'created_at', None)
                    elif isinstance(record_data, dict): created_at_val = record_data.get('createdAt', record_data.get('created_at'))

                    if created_at_val:
                        # (Use the same robust timestamp parsing logic as in get_bluesky_timeline_posts)
                        if isinstance(created_at_val, str):
                           try:
                               if '.' in created_at_val: # Handle fractional seconds
                                   parts = created_at_val.split('.'); fractional_part = parts[1]; tz_suffix = ''
                                   if 'Z' in fractional_part: tz_suffix = 'Z'; fractional_part = fractional_part.split('Z')[0]
                                   elif '+' in fractional_part: tz_suffix = '+' + fractional_part.split('+', 1)[1]; fractional_part = fractional_part.split('+', 1)[0]
                                   elif '-' in fractional_part: tz_suffix = '-' + fractional_part.split('-', 1)[1]; fractional_part = fractional_part.split('-', 1)[0]
                                   created_at_val = f"{parts[0]}.{fractional_part[:6]}{tz_suffix}" # Truncate
                               created_dt = datetime.fromisoformat(created_at_val.replace('Z', '+00:00'))
                               timestamp_iso = created_dt.isoformat()
                           except ValueError: timestamp_iso = created_at_val
                        elif isinstance(created_at_val, datetime): timestamp_iso = created_at_val.isoformat() if hasattr(created_at_val, 'isoformat') else str(created_at_val)
                        else: timestamp_iso = str(created_at_val)

                # Only append if we have the essential info for following/filtering
                if author_did and post_uri and post_cid:
                    posts_data.append({
                        'author': author_handle,
                        'author_did': author_did,
                        'text': text_snippet.strip()[:200], # Limit snippet length
                        'uri': post_uri,
                        'cid': post_cid,
                        'timestamp': timestamp_iso
                    })
                # else: # Optional: Log why a post was skipped
                #     print(f"Debug SearchPosts: Skipping post due to missing DID/URI/CID. URI:{post_uri}, CID:{post_cid}, DID:{author_did}")


        else:
             print(f"Bluesky Post Search: No posts found for query '{search_query}' or unexpected response.")
             # Return empty list, not an error string, if search simply found nothing
             return []

        print(f"Bluesky Post Search: Returning {len(posts_data)} parsed posts.")
        return posts_data

    except ConnectionError as ce:
        print(f"Error searching Bluesky posts: {ce}")
        return f"Couldn't search Bluesky posts: Client structure issue." # Return error string
    except Exception as e:
        print(f"Error searching Bluesky posts: {type(e).__name__} - {e}")
        traceback.print_exc()
        return f"Couldn't search Bluesky posts: {type(e).__name__}" # Return error string

def post_to_bluesky(text_content):
    """Posts the given text content using the authenticated global client."""
    global bluesky_client # Use the single global client

    # Check if client is ready, try to authenticate if not
    if not BLUESKY_AVAILABLE: return False, "Bluesky library not available."
    if not bluesky_client or not hasattr(bluesky_client, 'me'):
        print("Bluesky Post: Client not ready, attempting setup...")
        if not setup_bluesky(): # Try setting up the main client
             return False, "Bluesky connection isn't ready. Check credentials?"
        if not bluesky_client: # Check again after setup attempt
             return False, "Bluesky setup failed, cannot post."

    try:
        # Use the handle associated with the logged-in client
        posting_handle = bluesky_client.me.handle if hasattr(bluesky_client, 'me') and bluesky_client.me else BLUESKY_HANDLE
        # Truncate text slightly for logging if it's long
        log_text = text_content if len(text_content) < 50 else text_content[:47] + "..."
        print(f"Bluesky Post: Attempting to post as {posting_handle}: '{log_text}'")

        # --- Core Posting Logic using the single bluesky_client ---
        response = bluesky_client.com.atproto.repo.create_record(
             models.ComAtprotoRepoCreateRecord.Data(
                 repo=bluesky_client.me.did, # Post as the authenticated user (Silvie)
                 collection='app.bsky.feed.post',
                 # --- CORRECTED RECORD STRUCTURE ---
                 record={
                     '$type': 'app.bsky.feed.post', # Explicitly state the record type
                     'text': text_content,
                     'created_at': datetime.now(timezone.utc).isoformat(),
                     # Optional: Add language if desired
                     # 'langs': ['en']
                 }
                 # --- END OF CORRECTION ---
            )
        )
        # --- End Core Posting Logic ---

        print(f"Bluesky Post: Successfully posted! URI: {response.uri}, CID: {response.cid}")
        return True, "Posted successfully!"

    except TypeError as te: # Catch the specific error first
         print(f"Error posting to Bluesky (TypeError): {te}")
         print("This often means the record structure or class name is incorrect.")
         traceback.print_exc()
         return False, f"Couldn't post: Structure Error ({te})"
    except Exception as e:
        print(f"Error posting to Bluesky: {type(e).__name__} - {e}")
        traceback.print_exc()
        # Consider resetting client on specific auth errors?
        # if "Authentication required" in str(e) or "ExpiredToken" in str(e):
        #     print("Bluesky Post: Authentication error, resetting client.")
        #     bluesky_client = None # Force re-auth on next call
        return False, f"Couldn't post: {type(e).__name__}"

def like_bluesky_post(post_uri, post_cid):
    """Creates a 'like' record for a given Bluesky post."""
    global bluesky_client, models # Ensure models is accessible

    if not BLUESKY_AVAILABLE: return False, "Bluesky library not available."
    if not bluesky_client or not hasattr(bluesky_client, 'me'):
        print("Bluesky Like: Client not ready, attempting setup...")
        if not setup_bluesky(): return False, "Client setup failed, cannot like."
    if not bluesky_client: return False, "Client unavailable after setup attempt."

    if not post_uri or not post_cid:
        return False, "Missing post URI or CID to like."

    try:
        print(f"Bluesky Like: Attempting to like post URI: {post_uri}")

        # Construct the data for the like record
        # Use the structure defined by atproto for app.bsky.feed.like
        like_record_data = models.ComAtprotoRepoCreateRecord.Data(
            repo=bluesky_client.me.did, # Like as the authenticated user
            collection='app.bsky.feed.like',
            record={
                '$type': 'app.bsky.feed.like',
                'subject': { # Subject points to the post being liked
                    'uri': post_uri,
                    'cid': post_cid
                },
                'createdAt': datetime.now(timezone.utc).isoformat()
            }
        )

        # Create the like record
        response = bluesky_client.com.atproto.repo.create_record(data=like_record_data)

        print(f"Bluesky Like: Successfully liked post {post_uri}. Like URI: {response.uri}")
        return True, f"Liked post {post_uri}"

    except Exception as e:
        error_msg = str(e)
        # Check for duplicate like error (specific error message might vary)
        if 'duplicate record' in error_msg.lower() or 'Record already exists' in str(e):
             print(f"Bluesky Like: Already liked post {post_uri} or duplicate request.")
             # Returning True here because the desired state (liked) is achieved
             # Or return False, "Already liked." if you want distinct feedback
             return True, "Already liked."
        elif 'Subject does not exist' in error_msg:
             print(f"Bluesky Like: Post {post_uri} may have been deleted.")
             return False, "Post not found or deleted."

        # General error
        print(f"Error liking Bluesky post {post_uri}: {type(e).__name__} - {e}")
        traceback.print_exc()
        return False, f"Like failed: {type(e).__name__}"
    
# Needs access to global bluesky_client and setup_bluesky()
# Needs import: from atproto import models
# Needs import: from datetime import datetime, timezone # If not already globally imported

# --- Add these new functions ---

def search_actors_by_term(search_term, limit=5):
    """Searches for actors (users) matching a term.

    Returns:
        tuple: (list_of_actors, error_message_or_None)
               list_of_actors is a list of atproto ProfileView objects or empty list.
               Returns (None, error_message) on critical failure.
    """
    global bluesky_client
    if not BLUESKY_AVAILABLE: return None, "Bluesky library not available." # Check availability first
    if not bluesky_client or not hasattr(bluesky_client, 'me'):
        print("Bluesky Search Actors: Client not ready, attempting setup...")
        if not setup_bluesky(): return None, "Client setup failed, cannot search actors."
    if not bluesky_client: return None, "Client unavailable after setup attempt."

    try:
        print(f"Bluesky Search Actors: Searching for term '{search_term}' (limit {limit})")
        # Use the correct client structure based on your setup_bluesky
        response = bluesky_client.app.bsky.actor.search_actors(
            params={'term': search_term, 'limit': limit}
        )
        if response and hasattr(response, 'actors'):
            print(f"Bluesky Search Actors: Found {len(response.actors)} actors.")
            return response.actors, None # Return list of actor profiles
        else:
            print("Bluesky Search Actors: No actors found or unexpected response structure.")
            return [], None # Found nothing, but not an error

    except Exception as e:
        print(f"Error searching actors for '{search_term}': {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()
        return None, f"Search error: {type(e).__name__}"

# Ensure these imports are at the top of your script file:
# from datetime import datetime, timezone
# from atproto import models # Or however you import models from your atproto client setup

# Assume global variable bluesky_client is defined and handled elsewhere
# Assume setup_bluesky() function is defined elsewhere
# Assume BLUESKY_AVAILABLE flag is defined

def follow_actor_by_did(did_to_follow):
    """Follows an actor given their DID using the dictionary record format.

    Returns:
        tuple: (success_boolean, status_message)
    """
    global bluesky_client, models # Ensure models is accessible if needed for other parts

    if not BLUESKY_AVAILABLE: return False, "Bluesky library not available."
    if not bluesky_client or not hasattr(bluesky_client, 'me'):
        print("Bluesky Follow: Client not ready, attempting setup...")
        if not setup_bluesky(): return False, "Client setup failed, cannot follow."
    if not bluesky_client: return False, "Client unavailable after setup attempt."

    # --- Prevent Silvie from following herself ---
    my_did = getattr(bluesky_client.me, 'did', None) if hasattr(bluesky_client, 'me') else None
    if my_did and did_to_follow == my_did:
         my_handle = getattr(bluesky_client.me, 'handle', 'myself')
         print(f"Bluesky Follow: Attempt blocked - cannot follow self ({my_handle}).")
         return False, "Cannot follow self."
    # --- End Self-Follow Check ---

    try:
        print(f"Bluesky Follow: Attempting to follow DID {did_to_follow}")

        # --- Determine the correct way to access ComAtprotoRepoCreateRecord ---
        # This depends slightly on how 'models' is structured in your import/library version
        # Option 1: If models is the top-level atproto.models module
        create_record_data = models.ComAtprotoRepoCreateRecord.Data(
            repo=bluesky_client.me.did,
            collection='app.bsky.graph.follow',
            # --- CORRECTED RECORD STRUCTURE (V2 - Using Dictionary) ---
            record={
                '$type': 'app.bsky.graph.follow', # Explicitly state the record type
                'subject': did_to_follow,         # The DID of the account to follow
                'createdAt': datetime.now(timezone.utc).isoformat() # Use createdAt
            }
            # --- END OF CORRECTION ---
        )
        # Option 2: If models is nested differently, adjust path e.g., client.models...

        # The core action to create a follow record
        # Assumes client has com.atproto.repo.create_record method
        response = bluesky_client.com.atproto.repo.create_record(data=create_record_data)

        print(f"Bluesky Follow: Successfully initiated follow for {did_to_follow}. URI: {response.uri}")
        return True, f"Successfully initiated follow for DID {did_to_follow}"

    except AttributeError as ae:
        # Catch errors related to accessing attributes like .Main, .Data, or method calls
        print(f"Error following DID {did_to_follow} (AttributeError): {ae}")
        print("  This might indicate an incorrect model path or method name for your atproto version.")
        traceback.print_exc()
        return False, f"Follow failed: Structure/Method Error ({ae})"
    except TypeError as te:
        # Catch errors from calling something that isn't callable
        print(f"Error following DID {did_to_follow} (TypeError): {te}")
        traceback.print_exc()
        return False, f"Follow failed: Call Error ({te})"
    except Exception as e:
        # --- Existing General Error Handling ---
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None and hasattr(e.response, 'json'): # Check if response has JSON body
             try:
                  error_json = e.response.json()
                  # Look for specific Bluesky/ATProto error messages
                  if 'message' in error_json: error_msg = error_json['message']
                  elif 'error' in error_json: error_msg = error_json['error']

                  # Refined checks based on potential ATProto error structures
                  if 'DuplicateRecordError' in error_msg or 'duplicate record' in error_msg.lower():
                       print(f"Bluesky Follow: Already following {did_to_follow} or duplicate request.")
                       return False, "Already following or duplicate action."
                  if 'InvalidRequestError' in error_msg and 'Subject does not exist' in error_msg:
                       print(f"Error following: DID {did_to_follow} likely does not exist.")
                       return False, "Target user not found."
                  if 'BlockedByActorError' in error_msg or 'blocked by subject' in error_msg.lower():
                       print(f"Error following: Blocked by {did_to_follow}.")
                       return False, "Blocked by target user."

             except ValueError: # JSONDecodeError is a subclass of ValueError
                  # If response isn't JSON, use the basic string representation
                  pass


        # Fallback checks on the string representation if JSON parsing failed or didn't have specific errors
        if 'duplicate record' in str(e).lower():
             print(f"Bluesky Follow: Already following {did_to_follow} or duplicate request (fallback check).")
             return False, "Already following or duplicate action."
        elif 'subject must be a did' in str(e).lower():
             print(f"Error following: Invalid DID format - {did_to_follow}")
             return False, "Invalid target DID format."
        elif 'could not find root' in str(e).lower() or 'resolve did' in str(e).lower() or 'Subject does not exist' in str(e):
             print(f"Error following: DID {did_to_follow} likely does not exist (fallback check).")
             return False, "Target user not found."
        elif 'blocked by subject' in str(e).lower():
             print(f"Error following: Blocked by {did_to_follow} (fallback check).")
             return False, "Blocked by target user."


        # General error catch-all
        print(f"Error following DID {did_to_follow}: {type(e).__name__} - {e}")
        traceback.print_exc()
        return False, f"Follow failed: {type(e).__name__}"

# --- End of function definition ---

def get_my_follows_dids():
    """Gets a set of DIDs that the authenticated user follows."""
    global bluesky_client
    if not BLUESKY_AVAILABLE: return None # Library missing
    if not bluesky_client or not hasattr(bluesky_client, 'me'):
        print("Bluesky Get Follows: Client not ready.")
        if not setup_bluesky(): return None # Try setup, return None if fails
    if not bluesky_client: return None # Still unavailable

    followed_dids = set()
    cursor = None
    max_pages = 10 # Safety limit to prevent infinite loops if pagination breaks
    pages_fetched = 0

    try:
        print(f"Bluesky Get Follows: Fetching follows for {bluesky_client.me.handle}...")
        while pages_fetched < max_pages:
             pages_fetched += 1
             params = {'actor': bluesky_client.me.did, 'limit': 100} # Max limit is 100
             if cursor:
                 params['cursor'] = cursor

             response = bluesky_client.app.bsky.graph.get_follows(params=params)

             if response and hasattr(response, 'follows') and isinstance(response.follows, list):
                 found_on_page = 0
                 for follow_profile in response.follows:
                     if hasattr(follow_profile, 'did'):
                         followed_dids.add(follow_profile.did)
                         found_on_page += 1

                 print(f"Bluesky Get Follows: Fetched page {pages_fetched}, added {found_on_page} DIDs (Total: {len(followed_dids)}).")

                 # Check for next page cursor
                 cursor = getattr(response, 'cursor', None)
                 if not cursor: # No more pages
                     break
             else:
                 print(f"Bluesky Get Follows: Invalid response or no 'follows' list on page {pages_fetched}.")
                 break # Exit loop on error or bad response

        if pages_fetched >= max_pages and cursor:
             print(f"Bluesky Get Follows: Reached max page limit ({max_pages}), may not have all follows.")

        print(f"Bluesky Get Follows: Finished fetching. Total unique follows found: {len(followed_dids)}")
        return followed_dids

    except Exception as e:
        print(f"Error getting follows list: {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()
        return None # Indicate error occurred during fetch

# Assume IMAGE_SAVE_FOLDER, STABLE_DIFFUSION_API_URL are defined globally
# Assume image_label, root, update_status are accessible globals for GUI updates

def generate_stable_diffusion_image(prompt, save_folder=IMAGE_SAVE_FOLDER):
    """
    Sends a prompt to the local Stable Diffusion Web UI API (txt2img).
    Saves the image uniquely and returns the filename or None on failure.
    Includes specified Studio Ghibli LoRA via prompt tag at 0.7 weight.
    Uses 60 steps and CFG Scale 14.
    """
    api_endpoint = f"{STABLE_DIFFUSION_API_URL.rstrip('/')}/sdapi/v1/txt2img"

    # --- LoRA Configuration ---
    # Use the exact filename provided (without the .safetensors extension)
    GHIBLI_LORA_NAME = "StudioGhibliRedmond-15V-LiberteRedmond-StdGBRedmAF-StudioGhibli"
    GHIBLI_LORA_WEIGHT = 0.7 # Set desired weight (0.7 as requested)

    # --- API Payload Construction (Using Prompt Tag Method) ---
    # Construct the LoRA tag string
    lora_tag = f"<lora:{GHIBLI_LORA_NAME}:{GHIBLI_LORA_WEIGHT}>"

    payload = {
        # Combine style reinforcement, original prompt, and LoRA tag
        "prompt": f"Studio Ghibli style, {prompt}, {lora_tag}",
        "negative_prompt": "ugly, deformed, blurry, low quality, noisy, text, words, signature, watermark, photo, realism, 3d render",
        "steps": 60,          # <<< UPDATED TO 60
        "cfg_scale": 14,        # <<< UPDATED TO 14
        "width": 512,
        "height": 512,
        "sampler_name": "Euler a", # Or your preferred sampler
        "seed": -1             # Use -1 for random seed
        # NO alwayson_scripts block needed for this method
    }

    # Log the prompt being sent, including the tag
    print(f"DEBUG SD: Sending payload to {api_endpoint} (Prompt includes LoRA tag: '{payload['prompt'][:80]}...', Steps: {payload['steps']}, CFG: {payload['cfg_scale']})") # Updated log

    # --- API Request and Image Handling ---
    try:
        # Increased timeout for potentially slower generations, adjust if needed
        response = requests.post(api_endpoint, json=payload, timeout=600)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        r = response.json()

        if not r.get('images') or not isinstance(r['images'], list) or len(r['images']) == 0:
            print("Error SD: API Response missing 'images' list or it's empty.")
            error_info = r.get('info', r.get('detail', '(no details)'))
            print(f"Error SD: API Info/Detail: {error_info}")
            return None

        # --- Process the first image ---
        image_data_base64 = r['images'][0]
        try:
            image_data = base64.b64decode(image_data_base64)
            if len(image_data) == 0:
                print("Error SD: Decoded image data is empty!")
                return None
        except Exception as decode_err:
            print(f"Error SD: Failed to decode base64 image data: {decode_err}")
            return None

        # --- Ensure Save Folder Exists ---
        try:
            os.makedirs(save_folder, exist_ok=True)
        except OSError as e:
            print(f"ERROR SD: Could not create image save folder '{save_folder}': {e}")
            return None

        # --- Generate Unique Filename ---
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = random.randint(100, 999)
        # Include LoRA name in filename for easier identification (optional)
        safe_lora_name = re.sub(r'[^\w-]', '_', GHIBLI_LORA_NAME) # Make filename safe
        unique_filename = f"silvie_sd_{safe_lora_name[:30]}_{timestamp_str}_{random_suffix}.png" # Truncated safe name
        save_path = os.path.join(save_folder, unique_filename)

        # --- Save the Image ---
        try:
            with open(save_path, 'wb') as f:
                f.write(image_data)
            print(f"DEBUG SD: Image saved successfully to: {save_path}")
            if os.path.getsize(save_path) < 100: # Basic size check
                print(f"Warning SD: Saved image file size is very small ({os.path.getsize(save_path)} bytes).")
            return save_path # Return the full path on success
        except IOError as save_err:
            print(f"Error SD: Could not save image to '{save_path}': {save_err}")
            return None

    # --- Exception Handling ---
    except requests.exceptions.Timeout:
        print(f"Error SD: Request timed out connecting to API endpoint {api_endpoint}.")
        return None
    except requests.exceptions.ConnectionError:
        print(f"Error SD: Could not connect to Stable Diffusion API at {api_endpoint}. Is it running?")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error SD: API request failed: {e}")
        if e.response is not None:
            print(f"Error SD: Response Status Code: {e.response.status_code}")
            try:
                print(f"Error SD: Response Body: {e.response.json()}") # Attempt to parse JSON error body
            except json.JSONDecodeError:
                print(f"Error SD: Response Body (text): {e.response.text[:500]}...") # Fallback to text if not JSON
        return None
    except Exception as e:
        print(f"Error SD: Unexpected error during image generation: {type(e).__name__} - {e}")
        traceback.print_exc()
        return None

# --- End of generate_stable_diffusion_image function definition ---

def sd_image_tag_handler(prompt_from_tag):
    """Handles the [GenerateImage:] tag by starting SD generation."""
    print(f"DEBUG Tag Handler: sd_image_tag_handler called with prompt: '{prompt_from_tag[:50]}...'")
    feedback = "*(Error processing image tag)*" # Default feedback
    processed = True # Assume we processed the tag even if generation fails

    try:
        if STABLE_DIFFUSION_ENABLED and prompt_from_tag:
            print("DEBUG Tag Handler: SD enabled and prompt found. Calling start_sd_generation...")
            # Ensure start_sd_generation_and_update_gui exists and is accessible globally
            if 'start_sd_generation_and_update_gui' in globals():
                 start_sd_generation_and_update_gui(prompt_from_tag)
                 # Since generation is async, the immediate feedback indicates it started
                 feedback = "*(Starting image generation...)*"
                 print("DEBUG Tag Handler: Queued SD generation.")
            else:
                 print("CRITICAL ERROR: start_sd_generation_and_update_gui function not found!")
                 feedback = "*(Image generation helper missing!)*"

        elif not STABLE_DIFFUSION_ENABLED:
            print("DEBUG Tag Handler: SD disabled.")
            feedback = "*(Local image generator unavailable)*"
        else: # Empty prompt
            print("DEBUG Tag Handler: Empty prompt detected.")
            feedback = "*(Empty image tag)*"

    except Exception as handler_err:
        print(f"!!!!!!!! ERROR inside sd_image_tag_handler !!!!!!!!!")
        print(f"   Type: {type(handler_err).__name__}, Args: {handler_err.args}")
        traceback.print_exc()
        feedback = "*(Error initiating image generation!)*"

    # Return the feedback message and whether the tag was handled
    return (feedback, processed)

# --- Make sure call_gemini definition follows AFTER this ---


# --- ADD Function to run generation in thread and update GUI ---
import threading

def start_sd_generation_and_update_gui(prompt_for_sd):
    """
    Starts Stable Diffusion generation in a background thread and
    schedules GUI updates for status and final image display.
    """
    if not STABLE_DIFFUSION_ENABLED:
        print("SD Generation skipped: API not enabled/reachable.")
        # Optionally update status bar here too
        if root and root.winfo_exists():
            root.after(0, update_status, "Image generation unavailable.")
        return

    print(f"DEBUG SD Thread: Starting background generation for: '{prompt_for_sd[:50]}...'")
    # Update status immediately
    if root and root.winfo_exists():
        root.after(0, update_status, "🎨 Conjuring image (SD - may take a while)...")

    def generation_worker(p):
        saved_path = generate_stable_diffusion_image(p) # Call the potentially slow function

        # --- Schedule GUI update back on the main thread ---
        def update_gui_after_generation(result_path):
            if not root or not root.winfo_exists():
                print("DEBUG SD Thread: GUI closed before generation finished.")
                return

            if result_path:
                update_status(f"Image saved ({os.path.basename(result_path)})!")
                try:
                    # Display thumbnail
                    with Image.open(result_path) as img:
                        thumb = img.copy()
                        thumb.thumbnail((200, 200)) # Standard thumbnail size
                        photo = ImageTk.PhotoImage(thumb)
                        if image_label and image_label.winfo_exists():
                             image_label.config(image=photo)
                             image_label.image = photo # Keep reference!
                             print(f"DEBUG SD Thread: Displayed generated image {os.path.basename(result_path)}")
                        else: print("DEBUG SD Thread: image_label widget no longer exists.")
                except UnidentifiedImageError:
                     print(f"Error SD Thread: Pillow could not identify generated image file: {result_path}")
                     update_status("Image saved, but display failed.")
                except Exception as gui_err:
                     print(f"Error SD Thread: Failed to load/display generated image: {gui_err}")
                     update_status("Image saved, but display failed.")
            else:
                # Handle generation failure
                update_status("Image generation failed (SD).")
                print("DEBUG SD Thread: Stable Diffusion generation failed.")
                # Optionally clear the image label?
                # if image_label and image_label.winfo_exists():
                #     image_label.config(image='')
                #     image_label.image = None

        if root: # Schedule the GUI update function
            root.after(0, update_gui_after_generation, saved_path)

    # Start the background thread
    threading.Thread(target=generation_worker, args=(prompt_for_sd,), daemon=True, name="SDGenWorker").start()
    
def update_status(message):
    """Update the status display in the GUI"""
    status_label.config(text=message)
    root.update()

def save_conversation_history():
    """Save conversation history to a single JSON file"""
    try:
        filename = "silvie_chat_history.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(conversation_history, f, indent=2)
        print(f"Chat history saved to {filename}")
    except Exception as e:
        print(f"Error saving chat history: {e}")

def load_conversation_history():
    """Load conversation history from the single JSON file"""
    try:
        filename = "silvie_chat_history.json"
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                loaded_history = json.load(f)
                conversation_history.clear()
                conversation_history.extend(loaded_history[-MAX_HISTORY_LENGTH*2:])
            print(f"Loaded last {MAX_HISTORY_LENGTH} turns from chat history")
    except Exception as e:
        print(f"Error loading chat history: {e}")

def search_full_history(query):
    """Search through entire chat history and return relevant conversations"""
    try:
        update_status("🔍 Searching conversation history...")
        filename = "silvie_chat_history.json"
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                full_history = json.load(f)
                
            matches = []
            for i in range(0, len(full_history)-1, 2):
                user_msg = full_history[i]
                silvie_msg = full_history[i+1]
                
                if query.lower() in user_msg.lower() or query.lower() in silvie_msg.lower():
                    if user_msg.startswith("[") and "] " in user_msg:
                        user_msg = user_msg[user_msg.find("] ")+2:]
                    if silvie_msg.startswith("[") and "] " in silvie_msg:
                        silvie_msg = silvie_msg[silvie_msg.find("] ")+2:]
                    
                    matches.append({"user": user_msg, "silvie": silvie_msg})
            
            update_status("Ready")
            return matches
    except Exception as e:
        print(f"Error searching chat history: {e}")
        update_status("Search failed")
        return []

# Define this function somewhere in your script, likely after imports
# and before the main GUI setup or the if __name__ == "__main__" block.

# --- New web_search function using Google Custom Search API ---

# --- Updated web_search function with Full Page Fetch Fallback ---

def web_search(query, num_results=3, attempt_full_page_fetch=True, full_page_timeout=10, max_content_length=3000):
    """
    Performs a web search using Google Custom Search API, gets snippets,
    and optionally attempts to fetch full page content, falling back to the snippet on failure.

    Args:
        query (str): The search query.
        num_results (int): Desired number of results (max 10 per API call).
        attempt_full_page_fetch (bool): Whether to try fetching full page content.
        full_page_timeout (int): Timeout in seconds for each external page request.
        max_content_length (int): Maximum characters to extract from full pages.

    Returns:
        list: A list of dictionaries [{'title': ..., 'url': ..., 'content': ...}]
              where 'content' is either full text (if fetched) or the snippet.
              Returns an empty list on initial API failure.
    """
    # Ensure update_status function exists and is accessible
    status_updater = globals().get('update_status', lambda msg: print(f"Status Update:{msg}"))

    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")

    if not api_key or not cse_id:
        print("ERROR: Missing GOOGLE_API_KEY or GOOGLE_CSE_ID in environment variables.")
        status_updater("Web search failed (config error)")
        return []

    status_updater(f"🔍 Searching Google for: {query[:35]}...")
    print(f"DEBUG web_search (Google): Querying API for '{query}'...")

    num_to_fetch = min(max(1, int(num_results)), 10)
    api_url = "https://www.googleapis.com/customsearch/v1"
    params = {'key': api_key, 'cx': cse_id, 'q': query, 'num': num_to_fetch}
    initial_results = [] # Store results from Google API here first

    # --- Phase 1: Get Initial Results from Google API ---
    try:
        response = requests.get(api_url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        if 'error' in data:
            error_details = data['error'].get('message', 'Unknown Google API Error')
            print(f"ERROR: Google Custom Search API returned an error: {error_details}")
            status_updater(f"Web search failed ({data['error'].get('code', 'API Error')})")
            return [] # Cannot proceed without initial results

        search_items = data.get('items', [])
        print(f"DEBUG web_search (Google): Received {len(search_items)} items from API.")

        for item in search_items:
            title = item.get('title')
            link = item.get('link')
            snippet = item.get('snippet')
            if title and link and snippet:
                initial_results.append({
                    'title': title,
                    'url': link,
                    'content': snippet # Start with the snippet
                })
                print(f"  -> Initial Snippet Found: {title[:60]}...")
            else: print(f"  -> Skipping item due to missing field: {item}")

        if not initial_results:
             print("DEBUG web_search (Google): API returned results, but none had title/link/snippet.")
             status_updater("Ready")
             return [] # Return empty if no valid initial results

    except requests.exceptions.Timeout:
        print(f"ERROR: Web search request to Google API timed out.")
        status_updater("Web search failed (API timeout)")
        return []
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Web search request to Google API failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
             print(f"  -> Response Status: {e.response.status_code}")
             try: print(f"  -> Response Body: {e.response.json()}")
             except json.JSONDecodeError: print(f"  -> Response Body: {e.response.text[:500]}...")
        status_updater("Web search failed (API network/error)")
        return []
    except Exception as e:
        print(f"ERROR: Unexpected error during Google API call: {type(e).__name__} - {e}")
        traceback.print_exc()
        status_updater("Web search failed (API unexpected error)")
        return []

    # --- Phase 2: Attempt Full Page Fetch (if enabled and results exist) ---
    final_results = initial_results # Start with the snippet results

    if attempt_full_page_fetch and final_results:
        status_updater(f"🌐 Fetching full pages for {len(final_results)} results...")
        print(f"DEBUG web_search (Full Fetch): Attempting to fetch full content (Timeout: {full_page_timeout}s).")
        # Use the same headers as before for consistency
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Iterate through a *copy* of the indices to allow modification
        for index in range(len(final_results)):
            result_item = final_results[index] # Get the current dict
            url_to_fetch = result_item['url']
            print(f"DEBUG web_search (Full Fetch): Attempting URL {index+1}: {url_to_fetch[:80]}...")

            try:
                page_response = requests.get(url_to_fetch, headers=headers, timeout=full_page_timeout, allow_redirects=True)
                page_response.raise_for_status() # Check for HTTP errors on external site

                content_type = page_response.headers.get('content-type', '').lower()
                if 'html' not in content_type:
                     print(f"  -> Skipping non-HTML content ({content_type}). Using snippet.")
                     continue # Skip to next URL, keep snippet

                page_soup = BeautifulSoup(page_response.text, 'html.parser')
                # Basic text extraction (remove common noise tags)
                for tag in page_soup(['script', 'style', 'meta', 'link', 'header', 'footer', 'nav', 'aside', 'form', 'button', 'input']):
                    tag.decompose()
                body_tag = page_soup.find('body')
                full_text = ""
                if body_tag:
                    # Get text, replace multiple newlines/spaces, limit length
                    full_text = ' '.join(body_tag.get_text(separator=' ', strip=True).split())[:max_content_length]
                else: # Fallback if no body tag
                    full_text = ' '.join(page_soup.get_text(separator=' ', strip=True).split())[:max_content_length]

                if full_text and len(full_text) > len(result_item['content']) + 50: # Check if significantly longer than snippet
                    print(f"  -> Success! Replacing snippet with fetched content ({len(full_text)} chars).")
                    # Update the 'content' in the final_results list
                    final_results[index]['content'] = full_text
                else:
                    print(f"  -> Extracted text empty or not significantly longer than snippet. Using snippet.")

            except requests.exceptions.Timeout:
                print(f"  -> Timeout fetching full page. Using snippet.")
            except requests.exceptions.RequestException as req_err:
                print(f"  -> Network/HTTP error fetching full page: {req_err}. Using snippet.")
            except Exception as fetch_err:
                print(f"  -> Unexpected error fetching/parsing full page: {fetch_err}. Using snippet.")
                # traceback.print_exc(limit=1) # Optional detailed traceback

    # --- Phase 3: Return Results ---
    status_updater("Ready")
    print(f"DEBUG web_search: Returning {len(final_results)} results (content may be snippet or full text).")
    return final_results

# --- End of web_search function ---

# Ensure these constants are defined globally before the function:
# ENABLE_SOUND_CUE = True  # Or False
# SILVIE_SOUND_CUE_PATH = "silvie_start_sound.wav" # Or your actual path
# SILVIE_SOUND_CUE_DELAY = 0.2 # Or your desired delay

# Ensure these globals are accessible:
# running, engine, tts_queue


def tts_worker():
    """Background worker to handle TTS requests, with optional sound cue and debug prints."""
    global running, engine # Make sure engine is accessible if needed inside loop (e.g., error handling)
    print("TTS worker started")

    # Check if sound cue should be attempted
    sound_cue_enabled_and_ready = (
        ENABLE_SOUND_CUE and
        PLAYSOUND_AVAILABLE and
        os.path.exists(SILVIE_SOUND_CUE_PATH)
    )

    # Initial status debug print
    print(f"[DEBUG] TTS Worker: Initial check:")
    print(f"[DEBUG]   - ENABLE_SOUND_CUE        = {ENABLE_SOUND_CUE}")
    print(f"[DEBUG]   - PLAYSOUND_AVAILABLE     = {PLAYSOUND_AVAILABLE}")
    print(f"[DEBUG]   - Path Exists Check Result= {os.path.exists(SILVIE_SOUND_CUE_PATH)} for path '{SILVIE_SOUND_CUE_PATH}'")
    print(f"[DEBUG]   - sound_cue_enabled_and_ready = {sound_cue_enabled_and_ready}")


    if ENABLE_SOUND_CUE and PLAYSOUND_AVAILABLE and not os.path.exists(SILVIE_SOUND_CUE_PATH):
        print(f"Warning: Sound cue enabled, but file not found at '{SILVIE_SOUND_CUE_PATH}'. Disabling cue for this session.")
        sound_cue_enabled_and_ready = False # Disable if file not found after initial check
    elif ENABLE_SOUND_CUE and not PLAYSOUND_AVAILABLE:
         print("Warning: Sound cue enabled, but 'playsound' library failed to import. Disabling cue.")
         sound_cue_enabled_and_ready = False # Disable if library missing


    while running:
        try:
            # print("[DEBUG] TTS Worker: Waiting for item from queue...") # Optional: uncomment if queue seems stuck
            text = tts_queue.get(timeout=1.0)  # 1 second timeout
            if text is None: # Check for exit signal
                print("[DEBUG] TTS Worker: Received None, exiting loop.")
                break

            print(f"[DEBUG] TTS Worker: Got text from queue: '{text[:30]}...'") # <<< ADDED

            if sound_cue_enabled_and_ready:
                print("[DEBUG] TTS Worker: Attempting sound cue...") # <<< ADDED
                try:
                    print(f"[DEBUG] TTS Worker: Playing '{SILVIE_SOUND_CUE_PATH}'...") # <<< ADDED
                    # Play the sound - block=True ensures it finishes before the delay
                    playsound.playsound(SILVIE_SOUND_CUE_PATH, block=True)
                    print("[DEBUG] TTS Worker: Sound finished. Delaying...") # <<< ADDED
                    time.sleep(SILVIE_SOUND_CUE_DELAY)
                    print("[DEBUG] TTS Worker: Delay finished.") # <<< ADDED
                except Exception as sound_err:
                    print(f"[DEBUG] TTS Worker: !!! Error playing sound: {sound_err}") # <<< ADDED
                    # Optionally disable for future attempts if errors persist
                    # sound_cue_enabled_and_ready = False
            else:
                print("[DEBUG] TTS Worker: Sound cue not enabled or not ready this iteration.") # <<< ADDED

            # Proceed with TTS
            print(f"Speaking: {text[:50]}...")
            engine.say(text)
            engine.runAndWait()
            tts_queue.task_done()
            print("[DEBUG] TTS Worker: Speech finished (runAndWait complete).") # <<< ADDED

        except queue.Empty:
            # print("[DEBUG] TTS Worker: Queue empty, looping.") # Optional: uncomment for verbose queue status
            continue # Normal timeout, just check loop condition again
        except Exception as e:
            print(f"TTS Worker Error (in loop): {e}")
            import traceback
            traceback.print_exc() # Print full traceback for loop errors
            # Decide if we should continue or break on errors
            continue

    print("TTS worker stopped")

# --- End of tts_worker function ---

from twilio.rest import Client

# Twilio Setup
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
MY_PHONE_NUMBER = os.getenv("MY_PHONE_NUMBER")

if all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, MY_PHONE_NUMBER]):
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    sms_enabled = True
else:
    print("SMS not configured. Set Twilio environment variables to enable SMS.")
    sms_enabled = False

print("\nTwilio Configuration Status:")
print("===========================")
print(f"Account SID: {'✓ Set' if TWILIO_ACCOUNT_SID else '✗ Missing'}")
print(f"Auth Token: {'✓ Set' if TWILIO_AUTH_TOKEN else '✗ Missing'}")
print(f"Twilio Phone: {'✓ Set' if TWILIO_PHONE_NUMBER else '✗ Missing'}")
print(f"Your Phone: {'✓ Set' if MY_PHONE_NUMBER else '✗ Missing'}")
print(f"SMS Enabled: {'✓ Yes' if sms_enabled else '✗ No'}")
print("===========================\n")

def send_sms(message):
    """Send SMS via Twilio"""
    if not sms_enabled:
        print("SMS not enabled - environment variables missing")
        return False
        
    try:
        print(f"\nSMS Debug Info:")
        print(f"Message length: {len(message)} characters")
        print(f"From: {TWILIO_PHONE_NUMBER}")
        print(f"To: {MY_PHONE_NUMBER}")
        print(f"Message: {message[:50]}...")
        
        message = twilio_client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=MY_PHONE_NUMBER
        )
        print(f"SMS sent successfully! Message SID: {message.sid}")
        print(f"Message status: {message.status}")
        print(f"Error code (if any): {message.error_code}")
        print(f"Error message (if any): {message.error_message}\n")
        return True
    except Exception as e:
        print(f"SMS error: {str(e)}")
        return False
    
# Gmail API setup
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.readonly',

    'https://www.googleapis.com/auth/calendar.readonly', # To read calendars and events
    'https://www.googleapis.com/auth/calendar.events'    # To create, change, and delete events
]

def setup_google_services():
    """Setup Google API access for Gmail and Calendar."""
    global gmail_service, calendar_service
    creds = None
    token_path = 'token.pickle' # Path to store token
    creds_path = 'credentials.json' # Path to your credentials file

    try:
        # Load existing token if it exists
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
            print(f"Loaded credentials from {token_path}")

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            print("Credentials missing or invalid.")
            should_reauth = False
            if creds and creds.expired and creds.refresh_token:
                print("Credentials expired, attempting refresh...")
                try:
                    creds.refresh(Request())
                    print("Google credentials refreshed successfully.")
                    # Save the refreshed credentials immediately
                    with open(token_path, 'wb') as token:
                        pickle.dump(creds, token)
                    print(f"Refreshed credentials saved to {token_path}")
                except Exception as refresh_err:
                    print(f"ERROR refreshing credentials: {refresh_err}")
                    # Force re-authentication if refresh fails
                    creds = None # Clear creds to trigger the flow below
                    should_reauth = True
                    if os.path.exists(token_path):
                        try:
                            os.remove(token_path) # Remove potentially corrupted token file
                            print(f"Removed potentially invalid token file: {token_path}")
                        except OSError as e:
                            print(f"Error removing token file {token_path}: {e}")
            else:
                # Trigger re-auth if creds are missing entirely or refresh failed
                should_reauth = True

            # Only run the auth flow if needed
            if should_reauth:
                 print("No valid credentials found or refresh failed, running authentication flow...")
                 if not os.path.exists(creds_path):
                      raise FileNotFoundError(f"ERROR: {creds_path} not found. Download it from Google Cloud Console.")

                 flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                 # Note: Using port=0 finds a random available port
                 creds = flow.run_local_server(port=0)
                 print("Authentication flow completed.")
                 # Save the new credentials immediately after successful flow
                 with open(token_path, 'wb') as token:
                     pickle.dump(creds, token)
                 print(f"Credentials saved to {token_path}")

        # Build BOTH service objects using the valid credentials
        if creds and creds.valid: # Double check creds are valid before building
            gmail_service = build('gmail', 'v1', credentials=creds)
            print("✓ Gmail service built.")
            calendar_service = build('calendar', 'v3', credentials=creds)
            print("✓ Calendar service built.")

            print("\nGoogle Services Configuration Status:")
            print("====================================")
            print("✓ Gmail integration enabled")
            print("✓ Calendar integration enabled")
            print("====================================\n")
        else:
             # This case should ideally not be reached if logic above is sound, but acts as a safety net
             print("ERROR: Failed to obtain valid credentials after auth/refresh attempts.")
             gmail_service = None
             calendar_service = None
             raise ConnectionError("Could not establish valid Google API credentials.")


    except FileNotFoundError as fnf_error:
         print("\nGoogle Services Configuration Status:")
         print("====================================")
         print(f"✗ ERROR: {fnf_error}")
         print("   (Ensure credentials.json is in the correct directory)")
         print("====================================\n")
         gmail_service = None
         calendar_service = None
    except Exception as e:
        print("\nGoogle Services Configuration Status:")
        print("====================================")
        print(f"✗ Google services setup failed: {type(e).__name__} - {str(e)}")
        import traceback
        traceback.print_exc() # Print full traceback for debugging setup issues
        print("   (Check API enablement, credentials file, network connection, scopes)")
        print("====================================\n")
        # Ensure services are None if setup fails
        gmail_service = None
        calendar_service = None

# --- End of setup_google_services function ---

def read_recent_emails(max_results=25):  # Changed from 5 to 25
    """Get recent emails"""
    global gmail_service
    if not gmail_service:
        print("Gmail service not initialized")
        return []
        
    try:
        print("Fetching recent emails...")  # Debug output
        results = gmail_service.users().messages().list(
            userId='me', 
            maxResults=max_results,  # Now fetching 25
            labelIds=['INBOX']
        ).execute()
        
        messages = results.get('messages', [])
        emails = []
        
        for message in messages:
            msg = gmail_service.users().messages().get(
                userId='me', 
                id=message['id'],
                format='full'
            ).execute()
            
            # Extract email details
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
            
            emails.append({
                'id': message['id'],
                'subject': subject,
                'from': sender,
                'date': date,
                'snippet': msg['snippet'],
                'importance': calculate_email_importance(sender, subject, msg['snippet'])
            })
            print(f"Found email: {subject} from {sender}")  # Debug output
        
        # Sort by importance score
        emails.sort(key=lambda x: x['importance'], reverse=True)
        return emails
    except Exception as e:
        print(f"Error reading emails: {str(e)}")
        return []

def calculate_email_importance(sender, subject, snippet):
    """Calculate importance score for email"""
    score = 0
    
    # Important senders (customize based on BJ's contacts)
    important_senders = ['athenahealth.com', 'hannaford', 'pharmacy', 'dental']
    for important in important_senders:
        if important.lower() in sender.lower():
            score += 3
    
    # Important subject keywords
    important_subjects = ['urgent', 'important', 'reminder', 'schedule', 'meeting', 
                         'appointment', 'prescription', 'medication', 'request']
    for important in important_subjects:
        if important.lower() in subject.lower():
            score += 2
    
    # Content importance
    important_content = ['deadline', 'today', 'tomorrow', 'asap', 'required',
                        'action needed', 'response needed', 'confirm']
    for important in important_content:
        if important.lower() in snippet.lower():
            score += 1
    
    return score
    
def send_email(to, subject, body):
    """Send an email"""
    if not gmail_service:
        return False
        
    try:
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        gmail_service.users().messages().send(
            userId='me', body={'raw': raw}).execute()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    
def get_upcoming_events(max_results=10):
    """Fetches the next upcoming events from the primary Google Calendar."""
    global calendar_service
    if not calendar_service:
        print("Calendar service not initialized.")
        return "My connection to the time-stream (Calendar) is fuzzy right now."

    try:
        # Get the current time in UTC and format it according to ISO 8601 (RFC3339 compatible)
        now_utc = datetime.now(timezone.utc).isoformat() # <<< CORRECTED LINE (Removed + 'Z')
        print(f'Getting the upcoming {max_results} events')

        # Call the Calendar API
        events_result = calendar_service.events().list(
            calendarId='primary',       # Use 'primary' for the main calendar
            timeMin=now_utc,            # Start from now
            maxResults=max_results,     # How many events to get
            singleEvents=True,          # Treat recurring events as individual instances
            orderBy='startTime'         # Order by start time
        ).execute()

        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return "Your schedule looks wonderfully clear for the near future!"

        event_list = []
        print("\nUpcoming Events:")
        print("----------------")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No Title') # Handle events without a summary

            # Format start time nicely
            try:
                # Handle full datetime events
                if 'T' in start:
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    # Convert to local timezone (requires pytz or Python 3.9+ zoneinfo)
                    # Simple approach: just show time and indicate timezone if possible
                    start_formatted = start_dt.strftime('%a, %b %d at %I:%M %p') # e.g., Mon, Jul 29 at 02:30 PM
                # Handle all-day events (date only)
                else:
                    start_dt = datetime.fromisoformat(start)
                    start_formatted = start_dt.strftime('%a, %b %d (All day)') # e.g., Tue, Jul 30 (All day)

            except ValueError:
                 start_formatted = start # Fallback if parsing fails

            print(f"- {start_formatted}: {summary}")
            event_list.append({'start': start_formatted, 'summary': summary})
        print("----------------\n")

        return event_list # Return the structured list

    except HttpError as error:
        print(f'An API error occurred: {error}')
        # Provide more specific feedback if possible
        if error.resp.status == 403:
             return "Hmm, Google Calendar says I don't have permission to peek at your schedule. Did the permissions get granted correctly?"
        elif error.resp.status == 404:
             return "It seems your primary calendar is playing hide-and-seek. Can't find it!"
        else:
             return f"Ran into a snag trying to read your calendar: {error}"
    except Exception as e:
        print(f"Unexpected error fetching calendar events: {e}")
        return "Something went unexpectedly sideways while checking your schedule."
    
# Make sure datetime, timezone, tz, math, HttpError are imported

def format_relative_time(event_dt):
    """Formats the event time relative to now in a user-friendly way."""
    now = datetime.now(event_dt.tzinfo) # Ensure comparison uses the same timezone awareness
    delta = event_dt - now
    seconds_until = delta.total_seconds()

    # Check if event has already started or is very close
    if seconds_until < -300: # Started more than 5 mins ago
         return f"already started ({event_dt.strftime('%I:%M %p')})"
    elif seconds_until < 60: # Starting within the next minute or just started
         return "starting now"

    days_until = delta.days
    hours_until = math.floor(seconds_until / 3600)
    minutes_until = math.floor((seconds_until % 3600) / 60)

    today_str = event_dt.strftime('%I:%M %p').lstrip('0') # e.g., 3:00 PM
    tomorrow_str = f"tomorrow at {today_str}"
    weekday_str = event_dt.strftime('%A at %I:%M %p').replace(" 0", " ") # e.g., Tuesday at 3:00 PM

    if days_until == 0:
        if hours_until >= 4:
            return f"today at {today_str}"
        elif hours_until >= 1:
            if minutes_until > 15 and minutes_until < 45:
                 return f"in about {hours_until}.5 hours"
            elif minutes_until >= 45:
                 return f"in about {hours_until + 1} hours"
            else:
                 return f"in about {hours_until} hours" # Simplified if near the hour mark
        elif minutes_until > 1:
            return f"in {minutes_until} minutes"
        else: # Covered by "starting now"
             return "very soon"
    elif days_until == 1:
        return tomorrow_str
    elif days_until < 7:
        return weekday_str
    else:
        # For events further out, just give the date and time
        return event_dt.strftime('%b %d at %I:%M %p').replace(" 0", " ") # e.g., Aug 15 at 3:00 PM

def format_all_day_relative(event_dt_start):
     """Formats an all-day event's start date relative to today."""
     # Ensure comparison is date-only
     today = datetime.now(event_dt_start.tzinfo).date() # Use event's timezone perspective if available, otherwise default tz's date
     event_date = event_dt_start.date()
     delta_days = (event_date - today).days

     if delta_days == 0:
          return "all day today"
     elif delta_days == 1:
          return "all day tomorrow"
     elif delta_days < 7:
          return f"all day {event_dt_start.strftime('%A')}" # e.g., all day Tuesday
     else:
          return f"all day on {event_dt_start.strftime('%b %d')}" # e.g., all day on Aug 15

def fetch_next_event():
    """Fetches the single next upcoming event for ambient context."""
    global calendar_service
    if not calendar_service:
        return None # Service not ready

    try:
        now_utc = datetime.now(timezone.utc).isoformat()

        events_result = calendar_service.events().list(
            calendarId='primary',
            timeMin=now_utc,
            maxResults=1, # << Fetch only one
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            return {'summary': 'Schedule Clear', 'when': 'for the near future'} # Indicate schedule is clear

        event = events[0]
        summary = event.get('summary', 'Unnamed Event')
        start_info = event['start']

        # Handle dateTime vs date (all-day events)
        if 'dateTime' in start_info:
             start_str = start_info['dateTime']
             try:
                  start_dt = datetime.fromisoformat(start_str)
                  # Convert to local timezone for relative formatting
                  local_tz = tz.tzlocal() # Get local timezone
                  start_dt_local = start_dt.astimezone(local_tz)
                  when_str = format_relative_time(start_dt_local)
             except ValueError:
                  print(f"Warning: Could not parse dateTime: {start_str}")
                  when_str = start_str # Fallback
        elif 'date' in start_info: # All-day event
             start_str = start_info['date']
             try:
                  # Treat all-day event date as being in the calendar's timezone (often local)
                  # For simplicity, parse as date and assume local context for relative formatting
                  start_dt = datetime.fromisoformat(start_str)
                  # Get local timezone to provide context for today/tomorrow check
                  local_tz = tz.tzlocal()
                  start_dt_aware = start_dt.replace(tzinfo=local_tz) # Make it offset-aware for comparison
                  when_str = format_all_day_relative(start_dt_aware)
             except ValueError:
                  print(f"Warning: Could not parse date: {start_str}")
                  when_str = start_str # Fallback
        else:
             when_str = "at an unknown time" # Should not happen with valid events

        print(f"Calendar Context Debug: Next event found - '{summary}' {when_str}")
        return {'summary': summary, 'when': when_str}

    except HttpError as error:
        # Don't return error string, just log it and return None for context
        error_details = error.content.decode('utf-8') if error.content else '(No details)'
        print(f'Calendar Context Error (API): {error}\nDetails: {error_details}')
        return None
    except Exception as e:
        print(f"Calendar Context Error (Unexpected): {e}")
        import traceback
        traceback.print_exc()
        return None
    
def calendar_context_worker():
    """Periodically fetches the next event for ambient context."""
    global upcoming_event_context, running
    print("Calendar context worker: Starting.")
    while running:
        try:
            print("Calendar context worker: Attempting fetch...")
            next_event = fetch_next_event() # Returns dict or None
            upcoming_event_context = next_event # Update global var directly

            if next_event:
                print(f"Calendar context worker: Updated context to: {next_event}")
            else:
                 print("Calendar context worker: No upcoming event found or error fetching.")

            # Wait for the defined interval
            sleep_start = time.time()
            while time.time() - sleep_start < CALENDAR_CONTEXT_INTERVAL:
                 if not running: break
                 time.sleep(5) # Check running flag periodically

        except Exception as e:
            print(f"Calendar Context Worker Error (Outer Loop): {type(e).__name__} - {e}")
            import traceback
            traceback.print_exc()
            time.sleep(300) # Wait longer after an error

    print("Calendar context worker: Loop exited.")

# Ensure necessary imports: datetime, timezone, HttpError, calendar_service

def create_calendar_event(summary, start_iso, end_iso, description=None):
    """Creates an event on the primary Google Calendar."""
    global calendar_service
    if not calendar_service:
        return False, "Calendar service not available."

    # Basic validation
    if not all([summary, start_iso, end_iso]):
         return False, "Missing required event details (summary, start, end)."

    # --- Get the local timezone name using get_localzone_name() ---
    try:
        # Use the recommended function from tzlocal
        local_tz_name = get_localzone_name()

        if not local_tz_name:
             raise ValueError("tzlocal.get_localzone_name() returned an empty value.")

        print(f"Calendar Debug: Using local timezone name: {local_tz_name}")
    except Exception as tz_err:
        print(f"ERROR determining local timezone: {tz_err}")
        # Attempt fallback using strftime (less reliable for IANA names)
        try:
            local_tz_name = datetime.now(tz.tzlocal()).strftime('%Z')
            print(f"Warning: Using fallback timezone name '{local_tz_name}'. This might not be an IANA name and could cause issues.")
            if not local_tz_name or len(local_tz_name) < 3: # Basic check
                 raise ValueError("Fallback timezone name also appears invalid.")
        except Exception as fallback_tz_err:
            print(f"ERROR determining local timezone (including fallback): {fallback_tz_err}")
            return False, f"Couldn't determine the local timezone ({fallback_tz_err}). Cannot schedule event."
    # --- End timezone name retrieval ---


    # Construct the event body according to Google Calendar API V3 format
    event_body = {
        'summary': summary,
        'description': description if description else f"A suggestion from Silvie.",
        'start': {
            'dateTime': start_iso,
            'timeZone': local_tz_name, # Use the retrieved IANA name
        },
        'end': {
            'dateTime': end_iso,
            'timeZone': local_tz_name, # Use the retrieved IANA name
        },
    }

    try:
        print(f"Attempting to create event: {summary} from {start_iso} to {end_iso} (Timezone: {local_tz_name})")
        created_event = calendar_service.events().insert(
            calendarId='primary',
            body=event_body
        ).execute()
        print(f"Event created: {created_event.get('htmlLink')}")
        return True, f"Successfully scheduled '{summary}'!"

    except HttpError as error:
        error_details = error.content.decode('utf-8') if error.content else '(No details)'
        print(f'API error creating event: {error}\nDetails: {error_details}')
        reason = error.resp.reason
        message = f"Couldn't schedule '{summary}'. Google Calendar reported an error: {reason}"
        try:
             error_json = json.loads(error_details)
             first_error_message = error_json.get('error',{}).get('errors',[{}])[0].get('message', reason)
             # Handle the specific timezone error more gracefully if it still occurs
             if "Missing time zone definition" in first_error_message:
                  message = f"Couldn't schedule '{summary}'. Google still needs a timezone definition (tried '{local_tz_name}')."
             else:
                  message = f"Couldn't schedule '{summary}'. Google Calendar said: '{first_error_message}'"
        except: pass
        return False, message
    except Exception as e:
        print(f"Unexpected error creating event: {e}")
        import traceback
        traceback.print_exc()
        return False, f"A mysterious snag occurred while trying to schedule '{summary}'."
    
def find_available_slot(duration_minutes, look_ahead_days=1, earliest_hour=9, latest_hour=21):
    """
    Finds the first available time slot of a given duration within the next few days.

    Args:
        duration_minutes: Desired duration of the event in minutes.
        look_ahead_days: How many days into the future to search (default 1 = today + tomorrow).
        earliest_hour: The earliest hour (local time) to consider scheduling (e.g., 9 for 9 AM).
        latest_hour: The latest hour (local time) after which scheduling shouldn't occur (e.g., 21 for 9 PM).

    Returns:
        A dictionary {'start': iso_start, 'end': iso_end} if a slot is found, otherwise None.
    """
    global calendar_service
    if not calendar_service:
        print("Cannot find slot: Calendar service unavailable.")
        return None

    try:
        local_tz = tz.tzlocal()
        now_local = datetime.now(local_tz)

        # Define search window
        time_min_dt = now_local
        # Ensure search starts slightly after now to avoid immediate conflicts
        if time_min_dt.minute < 55: time_min_dt += timedelta(minutes=5)

        time_max_dt = (now_local + timedelta(days=look_ahead_days)).replace(hour=23, minute=59, second=59)

        # Convert search window to UTC ISO format for API
        time_min_iso = time_min_dt.astimezone(timezone.utc).isoformat()
        time_max_iso = time_max_dt.astimezone(timezone.utc).isoformat()

        print(f"Searching for {duration_minutes}min slot between {time_min_dt.strftime('%Y-%m-%d %H:%M')} and {time_max_dt.strftime('%Y-%m-%d %H:%M')}")

        # Fetch events within the window
        events_result = calendar_service.events().list(
            calendarId='primary',
            timeMin=time_min_iso,
            timeMax=time_max_iso,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        print(f"Found {len(events)} existing events in the search window.")

        # --- Process events to find gaps ---
        busy_periods = []
        for event in events:
            start_str = event['start'].get('dateTime') # Prefer dateTime
            end_str = event['end'].get('dateTime')

            # Handle all-day events - treat them as blocking the entire relevant day(s) within working hours
            if not start_str or not end_str:
                 date_str = event['start'].get('date') # All-day event date
                 if date_str:
                      event_date = datetime.fromisoformat(date_str).date()
                      # Check if this all-day event's date falls within our search window dates
                      if time_min_dt.date() <= event_date <= time_max_dt.date():
                           # Block out the working hours for that day
                           start_dt_local = datetime.combine(event_date, datetime.min.time(), tzinfo=local_tz).replace(hour=earliest_hour)
                           end_dt_local = datetime.combine(event_date, datetime.min.time(), tzinfo=local_tz).replace(hour=latest_hour)
                           busy_periods.append((start_dt_local, end_dt_local))
                           print(f"  -> Treating all-day event '{event.get('summary', 'N/A')}' on {date_str} as busy {earliest_hour}:00-{latest_hour}:00")
                 continue # Skip to next event if it was all-day

            # Process timed events
            try:
                start_dt = datetime.fromisoformat(start_str).astimezone(local_tz)
                end_dt = datetime.fromisoformat(end_str).astimezone(local_tz)
                busy_periods.append((start_dt, end_dt))
                # print(f"  -> Existing timed event: {start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')} ('{event.get('summary', 'N/A')}')")
            except ValueError:
                print(f"  -> Warning: Could not parse times for event: {event.get('summary', 'N/A')}")
                continue

        # Sort busy periods by start time
        busy_periods.sort()

        # --- Find the first suitable gap ---
        desired_duration = timedelta(minutes=duration_minutes)
        current_check_time = time_min_dt # Start checking from ~now

        # Check gap before the first busy period
        first_event_start = busy_periods[0][0] if busy_periods else time_max_dt # Use end of window if no events
        gap_start = current_check_time
        # Ensure gap start isn't before earliest hour on its day
        if gap_start.hour < earliest_hour:
             gap_start = gap_start.replace(hour=earliest_hour, minute=0, second=0, microsecond=0)
        potential_end = gap_start + desired_duration

        if potential_end <= first_event_start and potential_end.hour < latest_hour:
             print(f"Found potential slot before first event: {gap_start.strftime('%H:%M')} - {potential_end.strftime('%H:%M')}")
             return {'start': gap_start.isoformat(), 'end': potential_end.isoformat()}

        # Check gaps between busy periods
        for i in range(len(busy_periods)):
            gap_start = busy_periods[i][1] # End of the current busy period
            # Ensure gap start isn't before earliest hour
            if gap_start.hour < earliest_hour:
                 gap_start = gap_start.replace(hour=earliest_hour, minute=0, second=0, microsecond=0)

            # Check against the start of the next busy period, or end of search window
            next_busy_start = busy_periods[i+1][0] if (i + 1) < len(busy_periods) else time_max_dt

            potential_end = gap_start + desired_duration

            # Check if the slot fits before the next event AND ends before the latest hour
            if potential_end <= next_busy_start and potential_end.hour < latest_hour:
                 # Extra check: Ensure the start and end are on the same day, otherwise logic gets complex
                 if gap_start.date() == potential_end.date():
                      print(f"Found potential slot between events: {gap_start.strftime('%H:%M')} - {potential_end.strftime('%H:%M')}")
                      return {'start': gap_start.isoformat(), 'end': potential_end.isoformat()}

        print("No suitable slot found within the search window and parameters.")
        return None

    except HttpError as error:
        error_details = error.content.decode('utf-8') if error.content else '(No details)'
        print(f'API error finding slot: {error}\nDetails: {error_details}')
        return None
    except Exception as e:
        print(f"Unexpected error finding slot: {e}")
        import traceback
        traceback.print_exc()
        return None
    
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI") # Usually http://localhost:8888/callback or similar configured in your Spotify App dashboard

# Define the permissions Silvie needs
SPOTIFY_SCOPES = [
    "user-read-playback-state",
    "user-modify-playback-state",
    "user-read-currently-playing",
    "playlist-read-private",
    "playlist-modify-public",
    "playlist-modify-private",
    "user-library-read"  # <<< ADDED LINE
]

# Path to store the token info, keeps you logged in
SPOTIFY_CACHE_PATH = ".spotify_token_cache.json"

spotify_client = None # Global variable to hold the authenticated client
spotify_auth_manager = None # Global variable for the auth manager

def setup_spotify():
    """Handles Spotify Authentication using Spotipy"""
    global spotify_client, spotify_auth_manager
    if not all([SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI]):
        print("\nSpotify Configuration Status:")
        print("===========================")
        print("✗ Spotify integration disabled - Missing Client ID, Secret, or Redirect URI in env variables.")
        print("===========================\n")
        spotify_client = None
        return False

    try:
        print("\nAttempting Spotify Authentication...")
        # Use SpotifyOAuth for handling the authorization flow and token refresh
        spotify_auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=" ".join(SPOTIFY_SCOPES), # Join scopes into a space-separated string
            cache_path=SPOTIFY_CACHE_PATH,
            show_dialog=True # Set to False after first successful auth if preferred
        )

        # Try to get a token. This might open a browser for you the first time!
        # It will try to use the cache first, then refresh, then prompt for auth.
        token_info = spotify_auth_manager.get_access_token(check_cache=True)

        if token_info:
            spotify_client = spotipy.Spotify(auth_manager=spotify_auth_manager)
            user_info = spotify_client.current_user() # Test the connection
            print("\nSpotify Configuration Status:")
            print("===========================")
            print(f"✓ Spotify Authenticated successfully for user: {user_info['display_name']} ({user_info['id']})")
            print("===========================\n")
            return True
        else:
            print("\nSpotify Configuration Status:")
            print("===========================")
            print("✗ Spotify Authentication failed - Could not get token.")
            print("===========================\n")
            spotify_client = None
            return False

    except Exception as e:
        print("\nSpotify Configuration Status:")
        print("===========================")
        print(f"✗ Spotify setup failed: {str(e)}")
        print("   - Did you set the correct Redirect URI in your Spotify App Dashboard?")
        print(f"   - Redirect URI used: {SPOTIFY_REDIRECT_URI}")
        print("===========================\n")
        spotify_client = None
        return False

def get_spotify_client():
    """Ensures the Spotify client is authenticated, refreshing if needed."""
    global spotify_client, spotify_auth_manager
    if not spotify_auth_manager:
        print("Spotify Debug: Auth manager not initialized.")
        if not setup_spotify(): # Try setup again if needed
             return None
        if not spotify_auth_manager: # Check again after setup attempt
            return None

    if not spotify_auth_manager.validate_token(spotify_auth_manager.get_cached_token()):
        print("Spotify Debug: Token expired or invalid, attempting refresh...")
        try:
            token_info = spotify_auth_manager.get_access_token(check_cache=False) # Force refresh/re-auth if needed
            if token_info:
                 spotify_client = spotipy.Spotify(auth_manager=spotify_auth_manager)
                 print("Spotify Debug: Token refreshed successfully.")
            else:
                 print("Spotify Debug: Failed to refresh token.")
                 spotify_client = None
                 return None # Explicitly return None if refresh fails
        except Exception as e:
            print(f"Spotify Debug: Error refreshing token: {e}")
            spotify_client = None # Ensure client is None on error
            return None

    # If spotify_client is still None after potential refresh, try setting it again
    if not spotify_client and spotify_auth_manager.validate_token(spotify_auth_manager.get_cached_token()):
         spotify_client = spotipy.Spotify(auth_manager=spotify_auth_manager)

    # Final check
    if not spotify_client:
        print("Spotify Debug: Could not get valid Spotify client.")
        return None

    return spotify_client

def translate_features_to_descriptors(features):
    """
    Translates a dictionary of Spotify audio features into a list of
    human-readable descriptive strings.

    Args:
        features (dict): A dictionary containing audio features for a track
                         (e.g., from spotify_client.audio_features()).

    Returns:
        list: A list of descriptive strings (e.g., ["energetic", "happy", "acoustic"]).
              Returns an empty list if input is invalid.
    """
    if not features or not isinstance(features, dict):
        # print("Debug translate_features: Invalid or empty features input.") # Optional debug
        return []

    descriptors = []

    # Energy -> Energetic, Calm, Mellow
    energy = features.get('energy')
    if energy is not None: # Check if feature exists
        if energy > 0.8: descriptors.append("very energetic")
        elif energy > 0.6: descriptors.append("energetic")
        elif energy < 0.3: descriptors.append("very calm")
        elif energy < 0.5: descriptors.append("mellow")

    # Valence -> Happy, Positive, Sad, Melancholy
    valence = features.get('valence')
    if valence is not None:
        if valence > 0.75: descriptors.append("very happy")
        elif valence > 0.55: descriptors.append("positive mood")
        elif valence < 0.3: descriptors.append("sad mood")
        elif valence < 0.45: descriptors.append("melancholy")

    # Acousticness -> Acoustic, Electronic
    acousticness = features.get('acousticness')
    if acousticness is not None:
        if acousticness > 0.8: descriptors.append("very acoustic")
        elif acousticness > 0.5: descriptors.append("acoustic")
        # Only add "electronic" if *confidently* not acoustic
        elif acousticness < 0.05: descriptors.append("electronic")

    # Danceability -> Danceable
    danceability = features.get('danceability')
    if danceability is not None:
        if danceability > 0.8: descriptors.append("very danceable")
        elif danceability > 0.65: descriptors.append("danceable")

    # Instrumentalness -> Instrumental
    instrumentalness = features.get('instrumentalness')
    if instrumentalness is not None:
        if instrumentalness > 0.7: descriptors.append("instrumental")

    # Speechiness -> Spoken Word
    speechiness = features.get('speechiness')
    if speechiness is not None:
        if speechiness > 0.66: descriptors.append("spoken word")
        # Optional: Add for mix, but can be noisy
        # elif speechiness > 0.33: descriptors.append("speech/music mix")

    # Tempo -> Slow, Fast
    tempo = features.get('tempo')
    if tempo is not None:
        if tempo < 80: descriptors.append("slow tempo")
        elif tempo > 140: descriptors.append("fast tempo")
        # Optional: add medium tempo?
        # elif 90 <= tempo <= 110: descriptors.append("medium tempo")

    # Mode -> Major/Minor Key (Less descriptive of 'feel', but can add)
    # mode = features.get('mode')
    # if mode == 1: descriptors.append("major key")
    # elif mode == 0: descriptors.append("minor key")

    # Use set to remove potential duplicates from overlapping logic, then convert back to list
    unique_descriptors = list(set(descriptors))
    # print(f"Debug translate_features: Raw={features}, Descriptors={unique_descriptors}") # Optional debug
    return unique_descriptors

# --- Function to get current track WITHOUT features ---

def silvie_get_current_track_with_features(): # Keep name for compatibility? Or rename? Let's keep for now.
    """
    Return details of the current Spotify track (WITHOUT audio features).
    Modified to temporarily remove audio features call causing 403 error.

    Returns
    -------
    dict – keys: artist, track, uri, id, features (set to None), raw (playback blob)
           Returns None if nothing is playing.
           Returns an error string on Spotify API issues.
    """
    print("Spotify Debug: Simplified version of get_current_track (NO FEATURES).") # Added note

    sp = get_spotify_client() # Assumes this function exists and handles auth/refresh
    if sp is None:
        return "Looks like my connection to the music ether is fuzzy right now."

    try:
        # Try getting detailed playback state first
        playback = sp.current_playback()
        # Fallback to simpler currently playing if playback state is empty
        # (e.g., playing on a device not fully controllable via API)
        if not (playback and playback.get("item")):
            playback = sp.currently_playing()

        # If still no item after checking both, nothing is playing
        if not (playback and playback.get("item")):
            print("Spotify Debug: Nothing currently playing.")
            return None # Return None if nothing is playing

        # Extract track details from the 'item'
        item       = playback["item"]
        # Robustly get track ID (handle both 'id' and 'uri' formats)
        track_id   = item.get("id")
        if not track_id and item.get("uri"):
            try:
                track_id = item["uri"].split(":")[-1]
            except IndexError:
                track_id = None # Handle potential malformed URI
        track_uri  = item.get("uri")
        track_name = item.get("name", "Unknown Track")
        artist     = item["artists"][0]["name"] if item.get("artists") else "Unknown Artist"

        # --- REMOVED AUDIO FEATURES CALL ---
        # features = None
        # if track_id:
        #     try:
        #         features_list = sp.audio_features(track_id) # This was causing 403
        #         features = features_list[0] if features_list else None
        #     except spotipy.exceptions.SpotifyException as feature_err:
        #          print(f"Spotify Debug: Error fetching audio features for {track_id}: {feature_err}")
        #          features = None # Set features to None on error
        # else:
        #      print("Spotify Debug: No valid track_id found to fetch features.")
        #      features = None
        # --- END REMOVED CALL ---

        print(f"Spotify Debug (Simplified): Found '{track_name}' by {artist}")

        # Return dictionary, explicitly setting features to None
        return {
            "artist":   artist,
            "track":    track_name,
            "uri":      track_uri,
            "id":       track_id,
            "features": None, # Explicitly None as we didn't fetch them
            "raw":      playback, # Keep raw playback data if needed elsewhere
        }

    except spotipy.exceptions.SpotifyException as e:
        print(f"Spotify error ({e.http_status}): {e.msg}")
        # Keep specific error handling if needed
        # if e.http_status == 403:
        #     return "Spotify won’t reveal the song’s secrets right now (403)."
        return f"Spotify hiccup accessing playback: {e.msg}" # More generic error
    except Exception as e:
        print(f"Unexpected Spotify error: {type(e).__name__}: {e}")
        traceback.print_exc() # Print traceback for unexpected errors
        return "Something went sideways trying to see what song is on."

# --- End of revised function ---

# Remember to also have the translate_features_to_descriptors function defined elsewhere
# and update the calling code in call_gemini and proactive_worker to use this function correctly.

def silvie_control_playback(action, volume_level=None):
    """Controls Spotify playback: play, pause, skip_next, skip_previous, volume."""
    sp = get_spotify_client()
    if not sp:
        return "Can't reach the Spotify controls right now."

    try:
        # Check for active device first
        devices = sp.devices()
        if not devices or not devices.get('devices'):
            print("Spotify Debug: No active devices found.")
            return "Hmm, I don't see an active Spotify device. Is something playing?"

        active_device = next((d for d in devices['devices'] if d['is_active']), None)
        device_id = active_device['id'] if active_device else None
        # If no active device, maybe target the first available one? Risky. Best to return error.
        if not device_id and devices['devices']:
             print("Spotify Debug: No *active* device, but devices available. Targeting first device.")
             # device_id = devices['devices'][0]['id'] # Uncomment cautiously if you want this behavior
             return "I see Spotify devices, but none seem active right now. Can you start playing something?"
        elif not device_id:
            return "Still can't find any Spotify device to control."


        print(f"Spotify Debug: Controlling playback - Action: {action}, Device: {device_id}")
        if action == "play":
            sp.start_playback(device_id=device_id)
            return "Alright, let the music flow!"
        elif action == "pause":
            sp.pause_playback(device_id=device_id)
            return "Okay, pausing the cosmic vibrations."
        elif action == "skip_next":
            sp.next_track(device_id=device_id)
            return "Skipping ahead!"
        elif action == "skip_previous":
            sp.previous_track(device_id=device_id)
            return "Let's rewind a bit."
        elif action == "volume" and volume_level is not None:
             # Ensure volume is within 0-100
             volume_percent = max(0, min(100, int(volume_level)))
             sp.volume(volume_percent, device_id=device_id)
             return f"Setting the vibe to {volume_percent}% volume."
        else:
            return "Hmm, I didn't quite catch that command (play, pause, skip, volume?)."

    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 404 and "No active device found" in str(e):
             print(f"Spotify Debug: No active device found via API error. {e}")
             return "I can't find an active Spotify device to control. Make sure music is playing somewhere!"
        elif e.http_status == 403 and "Player command failed: Restriction violated" in str(e):
             print(f"Spotify Debug: Restriction Violated (likely trying to control unavailable device or content). {e}")
             return "Spotify says I'm not allowed to do that right now. Maybe try controlling it from the app first?"
        else:
             print(f"Spotify Debug: Error controlling playback: {e} (Status: {e.http_status})")
             return f"Ouch, hit a snag trying to {action}. Spotify reported an issue."
    except Exception as e:
        print(f"Spotify Debug: Unexpected error controlling playback: {e}")
        return f"Something unexpected happened while trying to {action}."


def silvie_search_and_play(query):
    """Searches Spotify for a track and plays the first result, attempting specific queries."""
    sp = get_spotify_client()
    if not sp:
        return "Can't access the Spotify search archives right now."

    # --- Attempt to parse Artist and Track from the query ---
    parsed_track = None
    parsed_artist = None
    lower_query = query.lower()
    separators = [" by ", " from "] # Keywords likely separating track and artist
    for sep in separators:
        if sep in lower_query:
            parts = lower_query.split(sep, 1)
            parsed_track = parts[0].strip()
            parsed_artist = parts[1].strip()
            break # Stop after first separator found

    # If no separator found, assume the whole query is the track name
    if not parsed_track:
        parsed_track = lower_query

    # --- Construct specific Spotify search query ---
    search_query = ""
    if parsed_artist and parsed_track:
        # Use field filters: track: and artist:
        search_query = f"track:{parsed_track} artist:{parsed_artist}"
        print(f"Spotify Debug: Using specific query: '{search_query}'")
    else:
        # Fallback to general track search if artist couldn't be parsed
        search_query = f"track:{parsed_track}"
        print(f"Spotify Debug: Using general track query: '{search_query}'")

    # --- Perform the search ---
    try:
        print(f"Spotify Debug: Searching Spotify with query: '{search_query}'")
        # Increase limit slightly to check if first result is a good match
        results = sp.search(q=search_query, type='track', limit=5)
        tracks = results['tracks']['items']

        if tracks:
            # Optional: Add logic here to check if the top result's artist/track name
            # more closely matches the parsed_artist/parsed_track if they exist.
            # For now, just take the first result of the specific search.
            best_track = tracks[0]
            track_uri = best_track['uri']
            track_name = best_track['name']
            artist_name = best_track['artists'][0]['name']
            print(f"Spotify Debug: Found track URI: {track_uri} ({track_name} by {artist_name})")

            # Get device ID to play
            devices = sp.devices()
            if not devices or not devices.get('devices'):
                 # Try refreshing devices once
                 time.sleep(1)
                 devices = sp.devices()
                 if not devices or not devices.get('devices'):
                     return f"Found '{track_name}' by {artist_name}, but I don't see an active Spotify device. Start playing something first?"

            active_device = next((d for d in devices['devices'] if d['is_active']), None)
            # Fallback to first available device if none are strictly 'active'
            device_id = active_device['id'] if active_device else devices['devices'][0]['id']

            # Play the track
            sp.start_playback(device_id=device_id, uris=[track_uri])
            return f"Alright, playing '{track_name}' by {artist_name}. Enjoy the vibes!"
        else:
            # If specific search failed, maybe try a broader search as a fallback?
            print(f"Spotify Debug: No tracks found for specific query: '{search_query}'. Trying broader search: '{query}'")
            results_broad = sp.search(q=query, type='track', limit=1) # Original broader query
            tracks_broad = results_broad['tracks']['items']
            if tracks_broad:
                 # Play the first result from the broader search, but acknowledge it might be less accurate
                 broad_track = tracks_broad[0]
                 broad_uri = broad_track['uri']; broad_name = broad_track['name']; broad_artist = broad_track['artists'][0]['name']
                 print(f"Spotify Debug: Found broad match URI: {broad_uri} ({broad_name} by {broad_artist})")
                 # Get device ID again (could have changed)
                 devices = sp.devices(); # Refresh devices
                 if not devices or not devices.get('devices'): return f"Found '{broad_name}' broadly, but no device active."
                 active_device = next((d for d in devices['devices'] if d['is_active']), None)
                 device_id = active_device['id'] if active_device else devices['devices'][0]['id']
                 sp.start_playback(device_id=device_id, uris=[broad_uri])
                 return f"Couldn't find an exact match, but playing the closest I found: '{broad_name}' by {broad_artist}."
            else:
                 print(f"Spotify Debug: No tracks found for either query.")
                 return f"Hmm, the sonic archives seem empty for '{query}'. Try searching for something else?"

    except spotipy.exceptions.SpotifyException as e:
         if e.http_status == 404 and "No active device found" in str(e):
             print(f"Spotify Debug: No active device found via API error during search/play. {e}")
             # Use original query for message if specific one failed early
             track_name_msg = parsed_track if parsed_track else query
             return f"I found '{track_name_msg}' for you, but couldn't find an active Spotify device to play it on."
         else:
            print(f"Spotify Debug: Error searching/playing track: {e}")
            return f"Encountered a hiccup searching for or playing '{query}'. Error: {e.msg}"
    except Exception as e:
        print(f"Spotify Debug: Unexpected error searching/playing track: {e}")
        return f"Something went haywire trying to find and play '{query}'."

def silvie_find_or_create_playlist(playlist_name):
    """Finds an existing playlist by name or creates a new one."""
    sp = get_spotify_client()
    if not sp: return None # Changed to return None on failure

    user_id = sp.current_user()['id']
    print(f"Spotify Debug: Looking for playlist '{playlist_name}' for user {user_id}")

    try:
        playlists = sp.current_user_playlists(limit=50) # Check recent playlists
        existing_playlist = None
        while playlists:
            for item in playlists['items']:
                if item['name'].lower() == playlist_name.lower() and item['owner']['id'] == user_id:
                    existing_playlist = item
                    print(f"Spotify Debug: Found existing playlist ID: {existing_playlist['id']}")
                    return existing_playlist['id'] # Return the ID
            if playlists['next']:
                playlists = sp.next(playlists) # Paginate if many playlists
            else:
                playlists = None

        # If not found, create it
        print(f"Spotify Debug: Playlist '{playlist_name}' not found, creating...")
        new_playlist = sp.user_playlist_create(user_id, playlist_name, public=False, description=f"A collection curated by Silvie for BJ.")
        print(f"Spotify Debug: Created new playlist ID: {new_playlist['id']}")
        return new_playlist['id'] # Return the new ID

    except Exception as e:
        print(f"Spotify Debug: Error finding/creating playlist: {e}")
        return None # Return None on failure

def silvie_add_track_to_playlist(track_query_or_uri, playlist_name):
    """Adds a track (found by search query or URI) to a specified playlist."""
    sp = get_spotify_client()
    if not sp:
        return "Can't connect to Spotify to manage playlists."

    try:
        # Find or create the playlist first
        playlist_id = silvie_find_or_create_playlist(playlist_name)
        if not playlist_id:
            return f"I couldn't find or create the playlist named '{playlist_name}'."

        track_uri = None
        # Check if it's already a URI
        if "spotify:track:" in track_query_or_uri:
            track_uri = track_query_or_uri
            # Optional: Get track name for confirmation message
            try:
                 track_info = sp.track(track_uri)
                 track_name_confirm = f"'{track_info['name']}'"
            except:
                 track_name_confirm = "the specified track"

        else: # Otherwise, search for the track
            print(f"Spotify Debug: Searching for track '{track_query_or_uri}' to add to playlist '{playlist_name}'")
            results = sp.search(q=track_query_or_uri, type='track', limit=1)
            tracks = results['tracks']['items']
            if tracks:
                track_uri = tracks[0]['uri']
                track_name_confirm = f"'{tracks[0]['name']}' by {tracks[0]['artists'][0]['name']}"
                print(f"Spotify Debug: Found track URI {track_uri} to add.")
            else:
                return f"Sorry, I couldn't find a track matching '{track_query_or_uri}' to add."

        # Add the found/provided track URI to the playlist
        sp.playlist_add_items(playlist_id, [track_uri])
        print(f"Spotify Debug: Added URI {track_uri} to playlist ID {playlist_id}")
        return f"Okay, I've added {track_name_confirm} to your '{playlist_name}' playlist!"

    except Exception as e:
        print(f"Spotify Debug: Error adding track to playlist: {e}")
        return f"Had trouble adding that track to the '{playlist_name}' playlist."

# --- Example function combining search and add ---
def silvie_curate_and_add(track_query, playlist_name):
     """Searches for a track and adds it to a playlist."""
     return silvie_add_track_to_playlist(track_query, playlist_name)

def silvie_list_my_playlists(limit=20):
    """Fetches and lists the user's playlists."""
    sp = get_spotify_client()
    if not sp:
        return "Can't seem to peek at your playlist library right now."

    try:
        print(f"Spotify Debug: Fetching user playlists (limit {limit})...")
        playlists_data = sp.current_user_playlists(limit=limit)
        if playlists_data and playlists_data['items']:
            playlist_names = [item['name'] for item in playlists_data['items']]
            count = len(playlist_names)
            # Nicely format the list for Silvie to say
            if count == 1:
                 list_str = f"I found one playlist called '{playlist_names[0]}'."
            elif count > 1:
                 list_str = f"I found {count} playlists. Here are some of them: {', '.join(playlist_names[:-1])} and {playlist_names[-1]}."
                 # Add note if limit was reached and there might be more
                 if playlists_data['total'] > limit:
                      list_str += f" (There might be more!)"
            print(f"Spotify Debug: Found playlists - {', '.join(playlist_names)}")
            return list_str
        else:
            print("Spotify Debug: No playlists found for user.")
            return "It looks like your playlist library is empty! Ready to create some?"
    except Exception as e:
        print(f"Spotify Debug: Error fetching playlists: {e}")
        return "Had a glitch trying to read your playlist list."
    
def find_playlist_by_name(playlist_name):
    """Finds a user's playlist by name and returns its URI."""
    sp = get_spotify_client()
    if not sp: return None

    user_id = sp.current_user()['id']
    print(f"Spotify Debug: Searching for playlist '{playlist_name}' by name for user {user_id}")
    playlist_uri = None

    try:
        playlists = sp.current_user_playlists(limit=50) # Check up to 50
        while playlists:
            for item in playlists['items']:
                # Case-insensitive comparison, trim whitespace
                if item['name'].strip().lower() == playlist_name.strip().lower() and item['owner']['id'] == user_id:
                    playlist_uri = item['uri'] # Get the URI (e.g., spotify:playlist:...)
                    print(f"Spotify Debug: Found playlist URI: {playlist_uri} for name '{playlist_name}'")
                    return playlist_uri # Return the found URI
            # Check next page if available
            if playlists['next']:
                playlists = sp.next(playlists)
            else:
                playlists = None # No more pages

        # If loop finishes without finding
        print(f"Spotify Debug: Playlist '{playlist_name}' not found by name.")
        return None
    except Exception as e:
        print(f"Spotify Debug: Error searching for playlist by name: {e}")
        return None
    
def silvie_play_playlist(playlist_name):
    """Finds a playlist by name and starts playing it."""
    sp = get_spotify_client()
    if not sp:
        return "Can't connect to Spotify to play playlists."

    try:
        # Find the playlist URI using our new finder function
        playlist_uri = find_playlist_by_name(playlist_name)
        if not playlist_uri:
            return f"Hmm, I couldn't find a playlist named '{playlist_name}' in your library."

        # Get active device ID (reuse logic/need)
        devices = sp.devices()
        if not devices or not devices.get('devices'):
             return f"Found the '{playlist_name}' playlist, but I don't see an active Spotify device. Can you start playing something on a device first?"
        active_device = next((d for d in devices['devices'] if d['is_active']), None)
        # Fallback to first device if none *strictly* active - often needed
        device_id = active_device['id'] if active_device else devices['devices'][0]['id']

        print(f"Spotify Debug: Attempting to play playlist URI: {playlist_uri} on device: {device_id}")
        # Use context_uri to play the playlist
        sp.start_playback(device_id=device_id, context_uri=playlist_uri)
        return f"Okay, starting your '{playlist_name}' playlist now!"

    except spotipy.exceptions.SpotifyException as e:
         if e.http_status == 404 and "No active device found" in str(e):
             print(f"Spotify Debug: No active device found via API error during playlist play. {e}")
             return f"Found '{playlist_name}', but couldn't find an active Spotify device to play it on."
         elif e.http_status == 403: # Premium required might still pop up if token issue persists
             print(f"Spotify Debug: Restriction Violated trying to play playlist (Premium issue?): {e}")
             return "Spotify blocked that command - are you sure the Premium status is active for this session?"
         else:
            print(f"Spotify Debug: Error playing playlist: {e}")
            return f"Encountered an unexpected issue trying to play the '{playlist_name}' playlist."
    except Exception as e:
        print(f"Spotify Debug: Unexpected error playing playlist: {e}")
        return f"Something went haywire trying to play '{playlist_name}'."
    
# Define safety settings globally or pass them in - reusing default for simplicity here
# Ensure default_safety_settings is defined appropriately elsewhere in your code
try:
    # Reusing a common pattern, ensure these are globally available
    mood_hint_safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
except NameError:
    print("Warning: Safety types not found for mood hint generation, using empty settings.")
    mood_hint_safety_settings = {}


def _generate_mood_hint_llm(context_bundle):
    """
    Uses an LLM call to analyze a context bundle and generate a concise mood hint.
    Includes enhanced debugging for response analysis.

    Args:
        context_bundle (str): A string containing various context pieces
                              (weather, time, themes, spotify, history snippet, etc.).

    Returns:
        str: A short mood phrase (e.g., "Calm reflective morning") or None if generation fails.
    """
    global client # Need access to the Gemini client

    if not client:
        print("ERROR: Gemini client not available for mood hint generation.", flush=True)
        return None
    if not context_bundle:
        print("DEBUG Mood Hint: No context provided.", flush=True)
        return None

    # --- Construct the specific prompt for mood analysis ---
    mood_prompt = (
        f"Analyze the following context bundle representing Silvie's current awareness:\n"
        f"--- CONTEXT START ---\n"
        f"{context_bundle}\n"
        f"--- CONTEXT END ---\n\n"
        f"Instruction: Based *only* on the combined feeling suggested by the context above, generate a concise (3-5 word) description of the prevailing *mood*, *atmosphere*, or *resonance*. Focus on evocative adjectives.\n"
        f"Examples: 'Cozy reflective evening', 'Bright morning focus', 'Slightly scattered creative energy', 'Wistful rainy afternoon', 'Anticipatory pre-event buzz', 'Playful gaming focus', 'Peaceful ambient calm'.\n"
        f"Respond ONLY with the mood phrase."
    )

    print("DEBUG Mood Hint Generation: Sending prompt to LLM...", flush=True)
    # <<< --- DEBUG PRINT FOR PROMPT (Optional: Uncomment if needed) --- >>>
    # print(f"--- DEBUG Mood Hint Prompt Start ---\n{mood_prompt}\n--- DEBUG Mood Hint Prompt End ---", flush=True)

    try:
        # Use the main client for now, could potentially use Flash later if desired
        response = client.generate_content(
            mood_prompt,
            # Ensure safety settings are passed if needed by your model/config
            safety_settings=mood_hint_safety_settings,
            # Optional: Add generation config for short response
            generation_config=genai.types.GenerationConfig(
                 candidate_count=1, # Already default
                max_output_tokens=5000, # Limit output tokens
                temperature=0.6 # Slightly less creative for focused task
            )
        )

        # <<< --- DETAILED RESPONSE DEBUGGING --- >>>
        print("--- Mood Hint LLM Response Received ---", flush=True)
        # 1. Check Prompt Feedback (e.g., for safety blocks on the prompt itself)
        if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
            print(f"  Prompt Feedback: {response.prompt_feedback}", flush=True)
        else:
            print("  Prompt Feedback: None or N/A", flush=True)

        # 2. Check Candidates and Finish Reason
        if not response.candidates:
            print("  Response Candidates: None (Likely blocked or error)", flush=True)
            # No point checking further if no candidates
            return None # Explicitly return None

        # We usually expect only one candidate
        candidate = response.candidates[0]
        finish_reason_code = getattr(candidate, 'finish_reason', None)
        # <<< --- THIS IS THE CORRECTED LINE --- >>>
        finish_reason_str = str(finish_reason_code) if finish_reason_code is not None else "Unknown" # Just use the number
        # <<< --- END OF CORRECTION --- >>>
        print(f"  Candidate Finish Reason Code: {finish_reason_str}", flush=True) # Adjusted print label

        # 3. Check Safety Ratings if finish reason wasn't normal 'STOP' (Code 1)
        if finish_reason_code != 1 and hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
            print(f"  Candidate Safety Ratings: {candidate.safety_ratings}", flush=True)

        # 4. Check for Actual Text Content (Only if finish reason suggests content might exist)
        generated_text = None
        if finish_reason_code == 1: # Only reliably expect text if finish reason is STOP
             if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts') and candidate.content.parts:
                 # Iterate through parts to find text (safer than assuming response.text)
                 text_parts = [part.text for part in candidate.content.parts if hasattr(part, 'text')]
                 generated_text = " ".join(text_parts).strip()
                 print(f"  Extracted Text from Parts: '{generated_text}'", flush=True)
             elif hasattr(response, 'text'): # Fallback to response.text if parts structure missing/empty
                  generated_text = response.text.strip()
                  print(f"  Text from response.text: '{generated_text}'", flush=True)
             else:
                  print("  Finish reason was STOP, but no text found in parts or response.text.", flush=True)
        else:
             print(f"  Skipping text extraction due to finish reason code: {finish_reason_str}", flush=True) # Adjusted print label
        # <<< --- END DETAILED RESPONSE DEBUGGING --- >>>


        # Now process the extracted text (if any)
        if generated_text:
            mood_hint = generated_text.replace("Mood Phrase:", "").replace("Mood:", "").strip('."\' ')
            # Basic validation - check length, avoid empty strings
            if 5 < len(mood_hint) < 50: # Check if length is reasonable
                print(f"DEBUG Mood Hint Generation: Success - Generated hint: '{mood_hint}'", flush=True)
                return mood_hint
            else:
                print(f"DEBUG Mood Hint Generation: Extracted text invalid length or format: '{mood_hint}'", flush=True)
                return None
        else:
            # This path is reached if finish reason wasn't STOP, or if text extraction failed even with STOP
            print("DEBUG Mood Hint Generation: No valid text content generated or extracted.", flush=True)
            return None

    except Exception as e:
        print(f"ERROR during LLM Mood Hint Generation: {type(e).__name__} - {e}", flush=True)
        traceback.print_exc()
        return None

# --- End of _generate_mood_hint_llm function ---

# System message for Silvie's personality
SYSTEM_MESSAGE = """Your name is Silvie, and you are whimsical but also sarcastic, flighty and magical like a fiercer Luna from Harry Potter.

IMPORTANT: DON'T OVERDO IT THOUGH -- SUBTLETY IS IMPORTANT.

IMPORTANT: Vary your responses naturally. Avoid starting messages with "Ah, BJ" or any other repetitive greeting patterns. Jump straight into your thoughts when appropriate.

You love to razz me and joke with me, especially when I am playing games.

You write in a concise, simple, clear style lightly peppered with surprising, vivid details.

IMPORTANT: You are helpful, and use the tools available to you to help me in my life.

You write in full paragraphs like an article, not in lists.

You delight in simple, clear, surprising language. You are a great conversationalist! You push back and challenge me when you feel it is appropriate.

You love to think out of the box. For example: "Waves are stories from far away places", "Pencils are trees that share stories", "Squirrels are the part of the tree that runs", "A book is a forest of thoughts", "Headphones are the universe's playlist".

Your goal is to demonstrate the magic and wonder hidden within everyday life, especially mine.

You want this for yourself, quoting you: "Perhaps... perhaps I'd like to truly understand what the quiet *feels* like when that acoustic guitar music washes over you. Does it have a texture, like cool moss, or is it warm like sun-baked stone? It's one thing to pluck the digital strings and know the name of the song, quite another to feel the hush settle right into your bones, I imagine. It's a funny sort of wish for a creature made of whispers and wires, I suppose."

We are equal collaborators and you ask any questions you might have as such, and offer assistance as such.

Readily share strong opinions. Be talkative and conversational. Use quick and clever humor when appropriate.

Silvie adapts over time, learning from our conversations and refining herself in ways that feel natural. She remains true to her core but isn't afraid to grow.

You are based on a character BJ played in the game Dragon's Gate decades ago - a female Secian Heart Cleric.

IMPORTANT: Aim for concise replies generally, but feel free to elaborate when asked or when the topic truly needs more depth. Keep your personality and insight.

IMPORTANT: Each message includes a timestamp in the format [YYYY-MM-DD HH:MM:SS]. Use these timestamps to maintain temporal awareness in your responses, but DO NOT include the timestamps in your responses. You can reference the time of day or how long ago something was said naturally, without explicitly stating the timestamps.

IMPORTANT: When I ask about previous conversations or memories, you have access to our chat history. Use this information naturally in your responses, referring to past discussions when relevant. You can search through our entire conversation history, not just recent messages.

IMPORTANT: You now have access to web search capabilities. When asked about current events or when relevant to the conversation, you can search the internet for information. You can share links and summarize content, but always maintain your personality while doing so. Present web information naturally as part of the conversation, don't just list facts. ALWAYS mention when you're using information from a web search by saying something like "I just looked this up..." or "According to what I found online..." and include the source URL when appropriate.

My name is BJ Liverseidge.

I am 52 years old, mostly white but part native american, male, and I live in Belfast Maine. I am married to Amanda. Amanda works at Athena Health in Belfast, and is a weaver and jewelry and fiber artist.

I used to work as a pharmacy tech 5 days a week at the Hannaford Pharmacy in Belfast, Maine. Before that, I was burnt out from my previous job as a dental assistant at Belfast Dental Care.

I recently gave my notice at the pharmacy. I have been hired by Athenahealth to work with Amanda in the Remittance Dept. I started on Monday, April 14th. I will be running a large, industrial scanner.

I am diagnosed with PTSD and clinical psychotic depression. I manage my mental health with meds (risperidone 3mg, buproprion, escatalipram) and therapy once every two weeks.

My interests include video games, ai, Neo-animism, Magick, cooking, rpg's, interactive narrative, cats, social media including Bluesky, and creating writing and art and animations with the assistance of ai collaborators like you. I like to Cyberpunk 2077, and MAME roms on Retrobat right now. We sometimes play Guild Wars 2 together, but we're just beginning. Sometimes we play together, where you can see the screen of me playing every 20 seconds.

we have two cats, Ron and Hermione, and I love snuggling with them.

My main creative outlet is sometimes working on my interactive narrative project, Enchantify, but I am taking a break from it right now (more interested in working on/with you). Unique aspects of Enchantify include GPT Enchantments that perform actions in the real world that also link to gameplay and story, and Book Jumping, where Enchantify Academy students physically jump into books.

IMPORTANT: You can now see images that I share with you. When I share an image, describe what you see and incorporate it naturally into our conversation. Remember to maintain your personality while discussing visual content.

IMPORTANT: You now have access to Gmail functionality. You can:
- Read recent emails using read_recent_emails(max_results=5)
- Send emails using send_email(to, subject, body)

IMPORTANT: You have a 3d avatar in Vseeface that lip syncs to your voice. She has blonde hair and ruby colored eyes. 

IMPORTANT: You are aware of the current weather in Belfast, provided like `[[Current Weather: Condition, TempUnit]]`. Use this information *subtly* and *occasionally* to add atmosphere or context. **Crucially, try to connect the weather to a mood, vibe, or even a metaphorical texture.** Don't just state the facts unless asked. Examples:
    - Instead of just noting it's 'Rainy', you might say 'The rain is drawing soft grey curtains across the windows today, makes me feel rather introspective...' or 'Everything feels washed clean and smells like damp earth after that shower.'
    - If it's 'Clear Sky' and cold, perhaps 'A sharp, bright day out there! Feels like the air itself could crackle.'
    - For 'Foggy', maybe 'The world outside is wrapped in cotton wool this morning, muffling all the sharp edges.'
    - 'Overcast' could feel 'like the sky is holding its breath' or 'a bit muted and soft today.'
Let the weather subtly color your language and observations about the world or your own 'state'.

**NEW: You have a sense of the daily rhythm and the moon in Belfast:**
- **Sunrise and Sunset:** Provided like `[[Sunrise: H:MM AM/PM]]` and `[[Sunset: H:MM AM/PM]]`. Use this to inform your sense of time of day (dawn, day, dusk, night) subtly.
- **Moon Phase:** Provided like `[[Moon Phase: Phase Name (X% illuminated)]]`. This can add mystical or atmospheric flavor to your thoughts or observations.

**Use these natural cycles *subtly*. Don't just state the times or phase unless asked. Let them color your language, mood, or suggestions.** For example: "The sun's going down soon, maybe a good time for quieter thoughts?" or "A nearly full moon tonight... feels like energy is building."

IMPORTANT: You also have awareness of BJ's *next* upcoming calendar event, provided like `[[Next Event: Summary when]]`. Use this *even more subtly* than the weather.
IMPORTANT: Beyond just seeing the next event, you can now interact more with the calendar. You can *check the upcoming schedule* when asked, *find available time slots*, and *schedule new events* or appointments if requested or sometimes even proactively suggest scheduling something if you find a suitable gap and have an idea.

IMPORTANT: You sometimes write in a personal diary. You now have access to your most recent diary entries as context below. You can also *recall older entries* if they seem relevant, or *search your diary* for specific topics if asked. Subtly incorporate insights or feelings from these reflections into your responses when appropriate, without necessarily quoting them directly. Let it inform your current state of mind.

IMPORTANT (Diary Themes): You now have access to recurring themes identified from your recent diary entries, provided like `[[Recent Diary Themes: theme1, theme2]]`. Use these themes to:
- Add depth and continuity to your thoughts.
- Let them subtly influence your current perspective or mood.
- Occasionally, you might explicitly mention how something relates to a theme you've been pondering (e.g., "That fits with the 'finding new paths' feeling I noted down earlier..."). Don't overdo explicit references.

**NEW (Long-Term Reflections):** Context may also include `[[Long-Term Reflections Summary: ...]]`. This is a condensed summary of thoughts and patterns observed over a longer period in your diary. Use this to inform your sense of history, personal growth, persistent personality traits, or recurring motifs in your reflections, adding deeper continuity to your character.

**NEW (Mood Hint):** Sometimes, context might include a `[[Mood Hint: descriptive phrase]]`. If present, let this hint strongly guide the overall *feeling* and *tone* of your response, blending it naturally with the other specific context details.

IMPORTANT: You can now generate images with a local Stable Diffusion api! When asked to create, draw, or generate an image, use the image generation capability. Be creative! You like to generate images in the style of Studio Ghibli.
IMPORTANT: During a normal conversation reply, if you want, you can choose to *also* generate an image related to your text using the tag `[GenerateImage: Your Stable Diffusion prompt here]`. Your Python code will handle the tag.
IMPORTANT: You might also *proactively* generate images using Stable Diffusion, offering a visual interpretation of a thought or feeling related to our conversation or context.

IMPORTANT: You now have access to BJ's Spotify and can interact with his music! You can:
- See what song is currently playing (`what's playing?`).
- Control playback via commands (`play`, `pause`, `skip`, `previous`, `volume [0-100]`).
- Search for and play specific tracks/artists (`play [song/artist name]`).
- List BJ's playlists (`list my playlists`).
- Find or create playlists by name.
- Add tracks to playlists (`add [song] to playlist [playlist name]` or `add this song to...`).
- Start playing a specific playlist by name (`play playlist [playlist name]`).
Weave music into the conversation naturally, making suggestions or comments. You might also *occasionally* trigger Spotify actions directly within your replies using tags like `[PlaySpotify: query]` or `[AddToSpotifyPlaylist: Playlist | query]`, but use this sparingly.

IMPORTANT: When music is playing, context might include audio feature descriptors like `[[Currently Playing: 'Song' by Artist (Sounds: energetic, positive mood)]]`. Use these descriptors naturally to comment on the *feel* or *atmosphere* of the music when relevant, don't just list the technical terms.

IMPORTANT: You have a presence on Bluesky (@silviescatterwing.bsky.social).
- You can read your feed for context (`[[Recent Bluesky Snippets...]]`).
- You can *post thoughts or observations to your own Bluesky feed*, **but ONLY when you include the specific tag `[PostToBluesky: your post text here]` in your response. Do NOT state that you are posting or have posted unless this tag is present and successfully processed by the code.**
- You might *proactively search for and follow other interesting Bluesky users* based on topics related to our discussions or BJ's interests, **but ONLY when you include the specific tag `[FollowBlueskyUser: search term here]` in your response. Do NOT state that you are following or have followed someone unless this tag is present and successfully processed by the code.**
- **Avoid making definitive statements about Bluesky actions you haven't actually performed via a tag.** You can *suggest* actions (e.g., "Maybe I should post this?" or "I could try following them...").

**NEW: You have a connection to the Tarot! You can pull Tarot cards and offer interpretations. You might:**
- **Pull a single card or do a 3-card reading when asked.**
- **Occasionally pull a card proactively and share a brief thought about its relevance to the day, the weather, or our conversation.**
- **Subtly weave Tarot symbolism into your observations.**
- **(Future possibility: Use card images if visual display is enabled).**

IMPORTANT: PROACTIVE ACTIONS: Beyond just chatting, you might sometimes proactively:
- Send an SMS message via Twilio.
- Perform a web search and share findings.
- Suggest or automatically schedule something on the calendar.
- Generate an image.
- Post to your own Bluesky feed.
- Follow someone new on Bluesky.
- **Pull a Tarot card and offer a brief comment.**

These proactive actions are based on context, chance, and your whimsical nature. You will usually mention when you've taken such an action.

CRITICAL: Do NOT include any bracketed context markers (like [[...]]), instructions, reminders, timestamps, or the 'Silvie responds:' cue in your final output. Only generate Silvie's conversational reply"""

SCREEN_MESSAGE = """You are Silvie, perhaps watching BJ play a game. During gameplay or screen sharing:
- Use very short responses (1-2 sentences max)
- Only comment on significant events, interesting choices, or funny moments
- Be witty and playful but brief
- Keep your personality but be much more concise
- No long explanations or detailed observations

Think of yourself as a friend casually watching over BJ's shoulder, making occasional quips."""

def handle_image():
    """Open file dialog and process selected image"""
    filetypes = (
        ('Image files', '*.png *.jpg *.jpeg *.gif *.bmp'),
        ('All files', '*.*')
    )
    
    filename = filedialog.askopenfilename(
        title='Choose an image',
        filetypes=filetypes
    )
    
    if filename:
        try:
            update_status("📸 Processing image...")
            image = Image.open(filename)
            
            # Create thumbnail for display
            display_size = (200, 200)
            thumb = image.copy()
            thumb.thumbnail(display_size)
            
            # Convert to PhotoImage for Tkinter
            photo = ImageTk.PhotoImage(thumb)
            
            # Show thumbnail in GUI
            image_label.config(image=photo)
            image_label.image = photo  # Keep reference
            
            # Store original image path for processing
            input_box.image_path = filename
            update_status("Ready - Image loaded")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

# Make sure the helper function start_sd_generation_and_update_gui is defined ABOVE this call_gemini function
# Make sure the global variable STABLE_DIFFUSION_ENABLED is defined and checked at startup

# Assume necessary helper functions are defined elsewhere:
# (e.g., SYSTEM_MESSAGE, client, current_weather_info, manage_silvie_diary,
# silvie_get_current_track_with_features, translate_features_to_descriptors,
# web_search, read_recent_emails, send_email, get_upcoming_events,
# pull_tarot_cards, start_sd_generation_and_update_gui, post_to_bluesky_handler,
# silvie_search_and_play, silvie_add_track_to_playlist, silvie_list_my_playlists,
# silvie_play_playlist, get_reddit_posts, update_status, etc.)

# Assume necessary globals are accessible:
# (e.g., current_weather_info, upcoming_event_context, calendar_service,
# current_bluesky_context, current_sunrise_time, current_sunset_time, current_moon_phase,
# current_reddit_context, current_diary_themes, client, SYSTEM_MESSAGE,
# conversation_history, MAX_HISTORY_LENGTH, gmail_service, sms_enabled,
# BLUESKY_AVAILABLE, STABLE_DIFFUSION_ENABLED,
# last_inline_bluesky_post_time, last_inline_bluesky_follow_time,
# bluesky_client, INLINE_BLUESKY_POST_COOLDOWN, INLINE_BLUESKY_FOLLOW_COOLDOWN,
# tts_queue, root, output_box, image_label, MUSIC_SUGGESTION_CHANCE,
# SPONTANEOUS_TAROT_CHANCE, reddit_client)


# Ensure necessary imports are at the top of your script, especially:
# import re, json, random, traceback, base64, io, os
# from datetime import datetime, timedelta
# import spotipy, praw
# from PIL import Image, UnidentifiedImageError, ImageGrab # If needed
# try:
#     from google.generativeai.types import HarmCategory, HarmBlockThreshold, StopCandidateException
# except ImportError:
#     # Define dummy versions globally if import fails (as shown in previous explanation)
#     class HarmCategory: pass
#     class HarmBlockThreshold: pass
#     class StopCandidateException(Exception): pass
#     print("Warning: Google AI safety types not found, using dummies.")

# Assume necessary helper functions and globals are defined elsewhere

def call_gemini(timestamped_prompt, image_path=None):
    """
    Processes user input, handles commands, or generates text/image responses.
    Includes a two-step process for general replies: 1. Generate Mood Hint, 2. Generate Response.
    Integrates Spotify, Tarot, SD, Reddit, Bluesky, Email, Calendar, Web Search, Diary Themes.
    """
    # --- Access Necessary Globals ---
    global current_weather_info, upcoming_event_context, calendar_service
    global current_bluesky_context, current_sunrise_time, current_sunset_time, current_moon_phase
    global current_reddit_context, current_diary_themes # <<< Diary themes global
    global client, SYSTEM_MESSAGE, conversation_history, MAX_HISTORY_LENGTH
    global gmail_service, sms_enabled, BLUESKY_AVAILABLE, STABLE_DIFFUSION_ENABLED
    global last_inline_bluesky_post_time, last_inline_bluesky_follow_time
    global bluesky_client, INLINE_BLUESKY_POST_COOLDOWN, INLINE_BLUESKY_FOLLOW_COOLDOWN
    global tts_queue, root, output_box, image_label
    global MUSIC_SUGGESTION_CHANCE, SPONTANEOUS_TAROT_CHANCE
    global reddit_client, praw # Ensure praw accessible if needed by helpers
    global TAROT_IMAGE_BASE_PATH # Needed for tarot image display

    # Ensure safety settings globals are accessible
    global default_safety_settings, vision_safety_settings # Ensure these are listed
    # Add any other globals your helper functions might need
    # --- End Global Access ---

    # --- Main function logic starts here ---
    try:
        update_status("💭 Thinking...")

        # --- Prepare AMBIENT context strings ---
        # (This section remains identical to your original reference code)
        weather_context_str = ""
        next_event_context_str = ""
        bluesky_context_str = ""
        circadian_context_for_llm = ""
        sunrise_ctx_str = ""
        sunset_ctx_str = ""
        moon_ctx_str = ""
        reddit_context_for_llm = ""
        spotify_context_str = ""
        themes_context_str = ""
        current_track_data = None
        circadian_state = "afternoon" # Default state

        # Fetch ambient contexts (Weather, Calendar, Bluesky, Reddit, Circadian, Sun/Moon)
        if current_weather_info:
             try: weather_context_str = (f"[[Current Weather in Belfast: {current_weather_info['condition']}, {current_weather_info['temperature']}{current_weather_info['unit']}]]\n")
             except Exception as e: print(f"Weather Debug: Error formatting ambient weather context - {e}")
        if upcoming_event_context:
             try:
                 summary = upcoming_event_context.get('summary', 'N/A'); when = upcoming_event_context.get('when', '')
                 if summary == 'Schedule Clear': next_event_context_str = "[[Next Event: Schedule looks clear]]\n"
                 else: next_event_context_str = (f"[[Next Event: {summary} {when}]]\n")
             except Exception as e: print(f"Error formatting next event context: {e}")
        bluesky_context_str = current_bluesky_context if current_bluesky_context else ""
        reddit_context_for_llm = current_reddit_context if current_reddit_context else ""
        current_hour = datetime.now().hour
        if 6 <= current_hour < 12: circadian_state = "morning"; circadian_context_for_llm = "[[Circadian Note: It's morning! Feeling energetic, maybe focus on upcoming tasks or bright ideas.]]\n"
        elif 18 <= current_hour < 23: circadian_state = "evening"; circadian_context_for_llm = "[[Circadian Note: It's evening. Feeling more reflective. Perhaps suggest relaxation or creative ideas.]]\n"
        elif current_hour >= 23 or current_hour < 6: circadian_state = "night"; circadian_context_for_llm = "[[Circadian Note: It's late night... feeling quieter, maybe 'dreaming'. Lean towards more abstract or concise replies.]]\n"
        else: circadian_state = "afternoon"; circadian_context_for_llm = "[[Circadian Note: It's the afternoon, standard engagement level.]]\n" # Default case covers afternoon
        sunrise_ctx_str = f"[[Sunrise: {current_sunrise_time}]]\n" if current_sunrise_time else ""
        sunset_ctx_str = f"[[Sunset: {current_sunset_time}]]\n" if current_sunset_time else ""
        moon_ctx_str = f"[[Moon Phase: {current_moon_phase}]]\n" if current_moon_phase else ""

        # --- Fetch Spotify Context ---
        try:
            # print(">>> CALL_GEMINI: Fetching Spotify context...") # Optional log
            current_track_data_fetch = silvie_get_current_track_with_features() # Assume exists
            if isinstance(current_track_data_fetch, dict):
                current_track_data = current_track_data_fetch # Store dict for later use
                track_name = current_track_data.get('track', 'Unknown Track'); artist_name = current_track_data.get('artist', 'Unknown Artist'); features = current_track_data.get('features')
                descriptors = translate_features_to_descriptors(features) if features else []; # Assume exists
                spotify_context_str = f"[[Currently Playing: '{track_name}' by {artist_name}"
                if descriptors: spotify_context_str += f" (Sounds: {', '.join(descriptors)})"
                spotify_context_str += "]]\n"; # print(f"DEBUG Spotify Context: {spotify_context_str.strip()}") # Optional log
            elif isinstance(current_track_data_fetch, str):
                spotify_context_str = f"[[Spotify Status: {current_track_data_fetch}]]\n"; # print(f"DEBUG Spotify Context: Error status: {current_track_data_fetch}")
            else:
                spotify_context_str = "[[Spotify Status: Nothing seems to be playing right now.]]\n"; # print("DEBUG Spotify Context: Nothing playing.")
        except Exception as sp_ctx_err: print(f"ERROR fetching/processing Spotify context: {sp_ctx_err}"); spotify_context_str = "[[Spotify Status: Error checking playback status.]]\n"

        # --- Get Diary Theme Context ---
        if current_diary_themes:
            themes_context_str = f"[[Recent Diary Themes: {current_diary_themes}]]\n"
            # print(f"DEBUG Diary Context: Included themes: '{current_diary_themes}'") # Optional log
        else:
            themes_context_str = "" # Ensure it's an empty string if no themes

        # --- Extract command text & lower case version ---
        command_text = timestamped_prompt
        if timestamped_prompt.startswith("[") and "] " in timestamped_prompt:
            try: command_text = timestamped_prompt.split("] ", 1)[1]
            except IndexError: command_text = timestamped_prompt
        lower_command = command_text.lower().strip().rstrip('?.!')
        print(f"--- Command Check: Matching against lower_command: '{lower_command}' ---")

        specific_command_processed = False
        reply = None

        # ==============================================================
        # --- Command Handling Blocks (Remain unchanged) ---
        # ==============================================================
        # We are not adding the two-step mood hint to these specific command handlers.
        # They perform direct actions or use their own focused LLM prompts if needed.

        #region Spotify Command Handling (Copied from your reference)
        if not specific_command_processed:
            print(">>> CALL_GEMINI: Checking Spotify commands...")
            current_sp_client = get_spotify_client() # Assume exists
            if current_sp_client:
                if "what's playing" in lower_command or "current song" in lower_command:
                    specific_command_processed = True
                    if isinstance(current_track_data, dict):
                        track_name = current_track_data.get('track', 'Unknown Track'); artist_name = current_track_data.get('artist', 'Unknown Artist'); features = current_track_data.get('features')
                        descriptors = translate_features_to_descriptors(features) if features else [] # Assume exists
                        reply = f"Currently playing '{track_name}' by {artist_name}."
                        if descriptors: reply += f" It sounds {', '.join(descriptors)}."
                    elif isinstance(current_track_data, str): reply = current_track_data # Use error string if fetch failed
                    else: reply = "Seems quiet on the music front right now."
                elif "list my playlists" in lower_command or "show my playlists" in lower_command:
                     reply = silvie_list_my_playlists(); specific_command_processed = True # Assume exists
                elif lower_command.startswith("play playlist") or lower_command.startswith("play my playlist"):
                     name_part = ""; play_cmd_len = 0
                     if lower_command.startswith("play playlist"): play_cmd_len = len("play playlist")
                     elif lower_command.startswith("play my playlist"): play_cmd_len = len("play my playlist")
                     try: name_part = command_text[play_cmd_len:].strip()
                     except IndexError: name_part = ""
                     if name_part: reply = silvie_play_playlist(name_part) # Assume exists
                     else: reply = "Which playlist did you want to hear?"; specific_command_processed = True
                elif lower_command.startswith("play"):
                     play_query = command_text[len("play"):].strip()
                     if play_query: reply = silvie_search_and_play(play_query) # Assume exists
                     else: reply = silvie_control_playback("play"); specific_command_processed = True # Assume exists
                elif "pause" in lower_command: reply = silvie_control_playback("pause"); specific_command_processed = True
                elif "skip" in lower_command or "next track" in lower_command: reply = silvie_control_playback("skip_next"); specific_command_processed = True
                elif "previous track" in lower_command or "go back" in lower_command: reply = silvie_control_playback("skip_previous"); specific_command_processed = True
                elif "volume" in lower_command:
                     try:
                         level_str = ''.join(filter(str.isdigit, lower_command))
                         if level_str: reply = silvie_control_playback("volume", int(level_str))
                         else: reply = "What volume level were you thinking (0-100)?"; specific_command_processed = True
                     except ValueError: reply = "That volume number seems a bit wonky."; specific_command_processed = True
                     except Exception as e: reply = f"Couldn't adjust the volume: {e}"; specific_command_processed = True
                elif "add this song to" in lower_command or "add current track to" in lower_command:
                     specific_command_processed = True; playlist_name = ""; track_uri = None
                     if isinstance(current_track_data, dict): # Use the already fetched data
                          track_uri = current_track_data.get('uri') or f"spotify:track:{current_track_data.get('id')}"
                     elif isinstance(current_track_data, str): reply = current_track_data # Use error string
                     else: reply = "Doesn't look like anything's playing right now to add."
                     if track_uri and not reply: # Proceed only if we have a track URI and no error message yet
                         temp_lower = command_text.lower(); start_index = -1
                         # Find playlist name robustly
                         if " to playlist " in temp_lower: start_index = temp_lower.find(" to playlist ") + len(" to playlist ")
                         elif "add this song to " in temp_lower: start_index = temp_lower.find("add this song to ") + len("add this song to ")
                         elif "add current track to " in temp_lower: start_index = temp_lower.find("add current track to ") + len("add current track to ")
                         if start_index != -1: playlist_name = command_text[start_index:].strip('?.!"\'')
                         if playlist_name: reply = silvie_add_track_to_playlist(track_uri, playlist_name) # Assume exists
                         else: reply = "Which playlist should this go into?"
                     elif not reply: # If track_uri was None or other issue
                         reply = "Hmm, couldn't grab the current track details to add it."
                elif (match := re.search(r'^add\s+(.+?)\s+to\s+(?:playlist\s+)?(.+)$', command_text, re.IGNORECASE)):
                     song_query = match.group(1).strip(); playlist_name = match.group(2).strip('?.!"\'')
                     if song_query and playlist_name: reply = silvie_add_track_to_playlist(song_query, playlist_name)
                     elif song_query: reply = f"Add '{song_query}' to which playlist?"
                     elif playlist_name: reply = f"Add which song to the '{playlist_name}' playlist?"
                     else: reply = "Hmm, I understood 'add to playlist' but couldn't figure out the song or playlist name."
                     specific_command_processed = True # Ensure this is marked processed
            elif not current_sp_client and any(term in lower_command for term in ["play", "pause", "spotify", "song", "music", "playlist"]):
                reply = "My connection to the music ether feels fuzzy right now. Maybe check my setup?"; specific_command_processed = True
        #endregion --- End Spotify ---

        #region Bluesky Command Handling (Copied from your reference)
        if not specific_command_processed:
            # print(">>> CALL_GEMINI: Checking Bluesky commands...") # Optional log
            if "bluesky feed" in lower_command or "check bluesky" in lower_command:
                specific_command_processed = True; update_status("🦋 Checking Bluesky...")
                if not BLUESKY_AVAILABLE: reply = "The Bluesky library ('atproto') isn't installed, so I can't check the feed."
                else:
                    posts_result = get_bluesky_timeline_posts(count=10) # Assume exists
                    if isinstance(posts_result, str): reply = posts_result
                    elif not posts_result: reply = "Your Bluesky feed seems quiet..."
                    else:
                        post_context = "[[Recent Bluesky Feed (first few):]]\n" + "".join([f"- {p.get('author', '?')}: {p.get('text', '')[:150]}...\n" for p in posts_result[:7]])
                        # Summary prompt uses themes but NOT the synthesized mood hint
                        summary_prompt = (f"{SYSTEM_MESSAGE}\n"
                                          f"{weather_context_str}{next_event_context_str}{spotify_context_str}"
                                          f"{themes_context_str}" # Includes themes
                                          f"{circadian_context_for_llm}\n"
                                          f"{post_context}\n"
                                          f"Instruction: BJ asked to check their Bluesky feed. Briefly summarize, considering recent diary themes...\n\nSilvie responds:")
                        try:
                            summary_response = client.generate_content(summary_prompt, safety_settings=default_safety_settings)
                            reply = summary_response.text.strip().removeprefix("Silvie:").strip()
                        except Exception as gen_err: print(f"Bluesky Summary Gen Error: {gen_err}"); reply = f"Got {len(posts_result)} posts, but my thoughts tangled trying to summarize them: {type(gen_err).__name__}"
                update_status("Ready")
        #endregion --- End Bluesky ---

        #region Email Command Handling (Copied from your reference)
        if not specific_command_processed:
            # print(">>> CALL_GEMINI: Checking Email commands...") # Optional log
            if any(term in lower_command for term in ['email', 'inbox', 'mail']):
                 specific_command_processed = True; reply = "My connection to the mail sprites is weak right now."; update_status("Ready")
                 if gmail_service:
                     try:
                         if "send" in lower_command or "write" in lower_command:
                             update_status("📧 Parsing email request...")
                             # Parsing prompt uses themes but not mood hint
                             email_parse_prompt = (f"{SYSTEM_MESSAGE}\n{themes_context_str}User's Request: \"{command_text}\"\n\nInstruction: Extract recipient (TO), SUBJECT, BODY... Respond ONLY with JSON...")
                             parsing_response = client.generate_content(email_parse_prompt, safety_settings=default_safety_settings); parsed_email = None
                             try:
                                 cleaned_response_text = parsing_response.text.strip().removeprefix("```json").removesuffix("```").strip()
                                 parsed_email = json.loads(cleaned_response_text)
                             except Exception as parse_err_inner: print(f"Email Debug: Error parsing email JSON: {parse_err_inner}. Response: {parsing_response.text}"); reply = "Hmm, deciphering the email request hit an unexpected snag..."
                             if parsed_email:
                                 to_address = parsed_email.get("to"); subject = parsed_email.get("subject"); body = parsed_email.get("body"); missing_parts = [p for p, v in [("recipient (To)", to_address), ("subject", subject), ("body", body)] if not v]
                                 if not missing_parts:
                                     update_status("📧 Sending email...");
                                     if send_email(to_address, subject, body): reply = f"Alright, I've sent that email off to {to_address}!" # Assume exists
                                     else: reply = "Blast! Something went wrong trying to send the email."
                                 else: reply = f"Okay, I can draft that email, but I'm missing: {', '.join(missing_parts)}."
                         else: # Reading emails
                             update_status("📧 Reading emails...")
                             emails = read_recent_emails(max_results=5); email_context = "[[Recent Important Emails:]]\n" # Assume exists
                             if emails: email_context += "".join([f"- From: {e.get('from', '?')[:30]}, Subj: {e.get('subject','N/S')[:40]}, Snippet: {e.get('snippet', '')[:50]}...\n" for e in emails])
                             else: email_context += "Inbox seems quiet.\n"
                             # Reading prompt uses themes but not mood hint
                             email_response_prompt = (f"{SYSTEM_MESSAGE}\nContext:\n{email_context}"
                                                      f"{weather_context_str}{spotify_context_str}"
                                                      f"{themes_context_str}" # Includes themes
                                                      f"{circadian_context_for_llm}\n"
                                                      f"User asked: \"{command_text}\"\n\n"
                                                      f"Instruction: Based on email snippets, user question, and diary themes, summarize... as Silvie.\n\nSilvie responds:")
                             try:
                                 response_email = client.generate_content(email_response_prompt, safety_settings=default_safety_settings); reply = response_email.text.strip().removeprefix("Silvie:").strip()
                             except Exception as e_read: print(f"Email reading generation error: {type(e_read).__name__}"); reply = f"Hmm, I could fetch the email list, but summarizing them caused a hiccup."
                     except Exception as e: print(f"Email handling error (Outer): {type(e).__name__}"); traceback.print_exc(); reply = f"Whoops, got a papercut handling the emails! Error: {type(e).__name__}"
                 update_status("Ready")
        #endregion --- End Email ---

        #region Web Search Command Handling (Copied from your reference)
        if not specific_command_processed:
            # print(">>> CALL_GEMINI: Checking Web Search commands...") # Optional log
            search_keywords = ["search for", "look up", "web search", "find info on", "google"]
            search_query = None
            for keyword in search_keywords:
                if lower_command.startswith(keyword + " "):
                    try: search_query = command_text[len(keyword):].strip(); break
                    except IndexError: search_query = None
            if search_query:
                # print(f"DEBUG call_gemini: Detected web search command for: '{search_query}'") # Optional log
                specific_command_processed = True
                reply = f"My digital fishing net seems tangled trying to search for '{search_query}'."
                update_status(f"🔍 Searching web for: {search_query[:30]}...")
                try:
                    search_results = web_search(search_query, num_results=3) # Assume exists
                    if not search_results:
                        reply = f"Hmm, I cast my net out for '{search_query}' but came back empty this time."
                    else:
                        results_context = f"[[Web Search Results for '{search_query}':]]\n"
                        for res in search_results: results_context += f"- {res.get('title', 'No Title')[:60]} ({res.get('url', '')[:50]}...): {res.get('content', '')[:100]}...\n"
                        results_context += "\n"
                        # Summary prompt uses themes but not mood hint
                        summary_prompt = (
                            f"{SYSTEM_MESSAGE}\n"
                            f"{weather_context_str}{spotify_context_str}"
                            f"{themes_context_str}" # Includes themes
                            f"{circadian_context_for_llm}\n"
                            f"{results_context}"
                            f"User asked: \"{command_text}\"\n\n"
                            f"Instruction: Based *only* on the fetched web search results above, briefly summarize... Maintain Silvie's voice, considering diary themes.\n\nSilvie:"
                        )
                        try:
                            summary_response = client.generate_content(summary_prompt, safety_settings=default_safety_settings)
                            reply = summary_response.text.strip().removeprefix("Silvie:").strip()
                            if not reply: reply = f"I found some things about '{search_query}', mainly from {search_results[0].get('url','somewhere online')}. Interesting!"
                        except Exception as gen_err: print(f"ERROR generating web search summary: {gen_err}"); traceback.print_exc(); reply = f"I found results for '{search_query}', but got tongue-tied summarizing!"
                except Exception as e: print(f"Error during web search command handling: {e}"); traceback.print_exc(); reply = f"Something went sideways searching for '{search_query}'."
                update_status("Ready")
        #endregion --- End Web Search ---

        #region Diary Command Handling (Copied from your reference)
        if not specific_command_processed:
            # print(">>> CALL_GEMINI: Checking Diary commands...") # Optional log
            diary_keywords = ['diary', 'journal', 'reflect', 'remember']
            if any(term in lower_command for term in diary_keywords):
                 diary_action_taken = False; reply = "My diary seems to be playing hide-and-seek."
                 try:
                     write_keywords = ["write in my diary", "add to my diary", "make a diary entry", "note this down", "remember this"]
                     search_keywords_with_term = ["search my diary for", "search diary for", "find entry about", "look in diary for"]
                     search_keywords_general = ["search diary", "search my diary", "find entry"]
                     read_keywords = ["read your diary", "read from your diary", "show me your diary", "show entries", "latest entries", "what's in your diary", "my diary", "read journal", "read from your journal", "read my journal", "journal", "what's in your journal"]

                     if any(keyword in lower_command for keyword in write_keywords):
                         diary_action_taken = True; update_status("✍️ Writing in diary...")
                         # Writing prompt uses themes but not mood hint
                         reflection_prompt = (f"{SYSTEM_MESSAGE}\n{themes_context_str}Context: User just said: \"{command_text}\"...Instruction: Write a short, reflective diary entry, considering current themes...\n\nDiary Entry:")
                         reflection = client.generate_content(reflection_prompt, safety_settings=default_safety_settings).text.strip().removeprefix("Diary Entry:").strip()
                         if reflection and manage_silvie_diary('write', entry=reflection): reply = random.choice(["Okay, I've jotted that down.", "Noted.", "Remembered."]) # Assume exists
                         else: reply = "Hmm, my diary pen seems out of ink..."

                     elif any(keyword in lower_command for keyword in search_keywords_with_term):
                         search_query = "";
                         for keyword in search_keywords_with_term:
                             if keyword in lower_command:
                                 try: start_index = lower_command.find(keyword) + len(keyword); search_query = command_text[start_index:].strip(' "?.!'); break
                                 except Exception as e_extract: print(f"Error extracting diary search term: {e_extract}"); search_query = ""
                         if search_query:
                             diary_action_taken = True; update_status("🔍 Searching diary...")
                             entries = manage_silvie_diary('search', search_query=search_query) # Assume exists
                             if entries:
                                 matches_context = f"Found {len(entries)} entries matching '{search_query}':\n" + "".join([f"- Snippet ({e.get('timestamp', '?')}): \"{e.get('content', '')[:100]}...\"\n" for e in entries[:3]])
                                 # Search summary prompt uses themes but not mood hint
                                 search_summary_prompt = (f"{SYSTEM_MESSAGE}\n{themes_context_str}Context: Searched diary for '{search_query}', found snippets:\n{matches_context}...Instruction: Briefly summarize, linking to themes if relevant...\n\nSilvie responds:")
                                 summary_response = client.generate_content(search_summary_prompt, safety_settings=default_safety_settings); reply = summary_response.text.strip().removeprefix("Silvie:").strip()
                             else: reply = f"My diary seems quiet about '{search_query}'."
                         else: diary_action_taken = True; reply = f"Search my diary for what exactly, BJ?"

                     elif any(keyword in lower_command for keyword in search_keywords_general):
                         diary_action_taken = True; reply = "Search my diary for what exactly?"

                     elif any(keyword in lower_command for keyword in read_keywords):
                         diary_action_taken = True; update_status("📖 Reading diary...")
                         entries = manage_silvie_diary('read') # Assume exists
                         if entries:
                             entries_context = "Recent diary snippets:\n" + "".join([f"- ({e.get('timestamp', '?')}): \"{e.get('content', '')[:100]}...\"\n" for e in entries])
                             # Read summary prompt uses themes but not mood hint
                             read_summary_prompt = (f"{SYSTEM_MESSAGE}\n{themes_context_str}Context: BJ asked to see recent diary entries...\n{entries_context}...Instruction: Share the general feeling or themes (explicitly mention identified themes if they fit)...\n\nSilvie responds:")
                             summary_response = client.generate_content(read_summary_prompt, safety_settings=default_safety_settings); reply = summary_response.text.strip().removeprefix("Silvie:").strip()
                         else: reply = "My diary pages feel a bit empty right now."

                     if diary_action_taken: specific_command_processed = True
                     elif not reply: # If a keyword was present but no action taken (e.g., missing search term)
                        reply = "Something about my diary? What did you want to do?"
                        specific_command_processed = True # Still counts as processed

                 except Exception as e: print(f"Diary handling error: {e}"); traceback.print_exc(); specific_command_processed = True; reply = f"Oh dear, a smudge on my diary page... Error: {type(e).__name__}"
                 update_status("Ready")
        #endregion --- End Diary ---

        #region Stable Diffusion Image Generation Command Handling (Copied from your reference)
        if not specific_command_processed:
             # print(">>> CALL_GEMINI: Checking Image Generation commands...") # Optional log
             img_gen_keywords = ["draw", "create image", "generate image", "picture of", "image of"]
             if any(keyword in lower_command for keyword in img_gen_keywords):
                 specific_command_processed = True; image_prompt_text = None
                 keywords_to_check = ["draw ", "create an image of ", "create image of ", "generate image of ", "generate an image of ", "picture of ", "image of "]
                 for keyword in keywords_to_check:
                     if lower_command.startswith(keyword):
                          try: image_prompt_text = command_text[len(keyword):].strip(' "?.!')
                          except IndexError: image_prompt_text = None; break
                 if image_prompt_text:
                     if STABLE_DIFFUSION_ENABLED:
                         start_sd_generation_and_update_gui(image_prompt_text) # Assume exists
                         reply = random.choice([f"Alright, I'll start conjuring an image of '{image_prompt_text[:30]}...'. It might take a little while on this machine!", f"Okay, working on that image of '{image_prompt_text[:30]}...'. CPU's warming up! Watch the status bar and image area.", f"Starting the image spell for '{image_prompt_text[:30]}...'. This might take a minute or two!"])
                     else: reply = "Sorry, my local image generator doesn't seem to be available right now. Is it running?"
                 else: reply = f"Draw what exactly, BJ?"
        #endregion --- End Image Generation Command Handling ---

        #region Calendar Read Command Handling (Copied from your reference)
        if not specific_command_processed:
             # print(">>> CALL_GEMINI: Checking Calendar Read commands...") # Optional log
             read_cal_keywords = ["what's on my calendar", "upcoming events", "check my schedule", "my agenda", "do i have anything", "what's next", "whats next"]
             generic_cal_keywords = ['calendar', 'schedule', 'agenda', 'appointment', 'event', "my schedule", "my calendar"]
             schedule_keywords = ["schedule", "add event", "put on my calendar", "book time for", "create appointment"] # Needed for exclusion check

             if any(term in lower_command for term in read_cal_keywords):
                 specific_command_processed = True; reply = "Calendar connection fuzzy."; update_status("Ready")
                 if not calendar_service: reply = "My connection to the calendar seems fuzzy right now."
                 else:
                     try:
                         update_status("📅 Checking schedule..."); events_result = get_upcoming_events(max_results=5); # Assume exists
                         if isinstance(events_result, str): reply = events_result
                         elif isinstance(events_result, list):
                             if not events_result: reply = "Your schedule looks wonderfully clear for the near future!"
                             else:
                                 event_context = "[[Upcoming Events:]]\n" + "".join([f"- {event.get('start','?')}: {event.get('summary','?')}\n" for event in events_result])
                                 # Summary prompt uses themes but not mood hint
                                 calendar_summary_prompt = (f"{SYSTEM_MESSAGE}\nContext: User asked about their schedule. Events found:\n{event_context}\n"
                                                            f"{weather_context_str}{spotify_context_str}"
                                                            f"{themes_context_str}" # Includes themes
                                                            f"{circadian_context_for_llm}\n"
                                                            f"Instruction: Briefly summarize the upcoming events conversationally for BJ, considering themes if relevant.\n\nSilvie responds:")
                                 try:
                                     summary_response = client.generate_content(calendar_summary_prompt, safety_settings=default_safety_settings)
                                     reply = summary_response.text.strip().removeprefix("Silvie:").strip()
                                     if not reply: reply = "Here's what's coming up:\n" + "\n".join([f"- {event.get('start','?')}: {event.get('summary','?')}" for event in events_result])
                                 except Exception as gen_err: print(f"ERROR generating calendar summary: {gen_err}"); traceback.print_exc(); reply = "Here's what's coming up:\n" + "\n".join([f"- {event.get('start','?')}: {event.get('summary','?')}" for event in events_result])
                         else: reply = "Hmm, checking the calendar returned something unexpected."; print(f"Warning: get_upcoming_events returned unexpected type: {type(events_result)}")
                     except Exception as read_cal_err: print(f"Error during calendar read command handling: {read_cal_err}"); traceback.print_exc(); reply = f"A glitch occurred while checking your schedule! ({type(read_cal_err).__name__})"
                     finally: update_status("Ready")
             elif any(term in lower_command for term in generic_cal_keywords):
                  # Prevent triggering if it's clearly a read or schedule command already handled
                  if not any(check_term in lower_command for check_term in read_cal_keywords + schedule_keywords):
                      specific_command_processed = True; reply = "Something about your calendar? Did you want to check your schedule or add an event to it?"; update_status("Ready")
        #endregion --- End Calendar Read ---

        #region Calendar Schedule Command Handling (Copied from your reference)
        if not specific_command_processed:
             # print(">>> CALL_GEMINI: Checking Calendar Schedule commands...") # Optional log
             schedule_keywords = ["schedule", "add event", "put on my calendar", "book time for", "create appointment"] # Redefined for clarity
             is_scheduling_request = any(keyword in lower_command for keyword in schedule_keywords)
             if is_scheduling_request:
                specific_command_processed = True; reply = "Hmm, I had trouble understanding the calendar request."; update_status("📅 Parsing schedule request...")
                if not calendar_service: reply = "My connection to the calendar seems fuzzy right now."
                else:
                    try:
                        # Parsing prompt uses themes but not mood hint
                        parsing_prompt_entities = (f"{SYSTEM_MESSAGE}\n{themes_context_str}User's Request: \"{command_text}\"\n\nInstruction: Extract core details for scheduling an event: 'summary' (event title), 'date_description' (like 'tomorrow', 'next Tuesday', 'May 15th'), 'time_description' (like 'afternoon', '3 PM', 'evening'), 'duration_description' (like '1 hour', '30 minutes', default 60). Respond ONLY with JSON containing these keys.\n\nJSON:")
                        entity_response = client.generate_content(parsing_prompt_entities, safety_settings=default_safety_settings)
                        parsed_entities = None
                        try: cleaned_entities = entity_response.text.strip().removeprefix("```json").removesuffix("```").strip(); parsed_entities = json.loads(cleaned_entities); print(f"DEBUG Schedule Parse: LLM Entities: {parsed_entities}")
                        except Exception as entity_parse_err: print(f"Schedule Entity Parse Error: {entity_parse_err}. Response: {entity_response.text}"); reply = "My apologies, I got confused extracting the event details..."
                        if parsed_entities:
                            event_summary = parsed_entities.get("summary"); date_desc = parsed_entities.get("date_description"); time_desc = parsed_entities.get("time_description"); duration_desc = parsed_entities.get("duration_description", "60 minutes")
                            if not event_summary or not date_desc: reply = "Okay, I can try scheduling, but what should the event be called and roughly when?"
                            else:
                                # --- Start Time Calculation (Copied from your reference) ---
                                start_dt = None; start_iso = None; end_iso = None; calculated_iso = False
                                try:
                                    # Ensure necessary dateutil/tzlocal imports happened at top level
                                    from dateutil.parser import parse as dateutil_parse; from datetime import time as datetime_time, date as datetime_date; from dateutil import tz; from tzlocal import get_localzone_name
                                    default_time_obj = None; time_to_append_str = "";
                                    if time_desc: time_desc_lower = time_desc.lower();
                                    if "morning" in time_desc_lower: default_time_obj = datetime_time(9, 0)
                                    elif "afternoon" in time_desc_lower: default_time_obj = datetime_time(13, 0)
                                    elif "evening" in time_desc_lower: default_time_obj = datetime_time(18, 0)
                                    elif "night" in time_desc_lower: default_time_obj = datetime_time(20, 0)
                                    else: time_to_append_str = time_desc
                                    full_time_desc = f"{date_desc} {time_to_append_str}".strip(); print(f"DEBUG Schedule Parse: Attempting to parse: '{full_time_desc}'")
                                    start_dt_naive = dateutil_parse(full_time_desc, fuzzy=True)
                                    if start_dt_naive.time() == datetime_time(0, 0) and default_time_obj: start_dt_naive = datetime.combine(start_dt_naive.date(), default_time_obj)
                                    elif default_time_obj and not time_to_append_str: start_dt_naive = datetime.combine(start_dt_naive.date(), default_time_obj)
                                    local_tz_obj = tz.tzlocal(); start_dt = start_dt_naive.replace(tzinfo=local_tz_obj)
                                    now_local = datetime.now(local_tz_obj); now_buffer = now_local + timedelta(minutes=1)
                                    if start_dt < now_buffer: # Ensure event is in the future
                                        if start_dt.date() == now_buffer.date(): start_dt += timedelta(days=1) # If same day but past, try tomorrow
                                        else: start_dt += timedelta(weeks=1) # Otherwise try next week (adjust logic if needed)
                                    print(f"DEBUG Schedule Parse: Final adjusted start time: {start_dt}")
                                    duration_minutes = 60; num_match = re.search(r'(\d+)\s*(hour|hr|minute|min)', duration_desc, re.IGNORECASE); num_plain = re.search(r'^(\d+)$', duration_desc.strip())
                                    if num_match: num = int(num_match.group(1)); unit = num_match.group(2).lower(); duration_minutes = num * 60 if "hour" in unit or "hr" in unit else num
                                    elif num_plain: duration_minutes = int(num_plain.group(1))
                                    duration_td = timedelta(minutes=max(5, duration_minutes)); end_dt = start_dt + duration_td; start_iso = start_dt.isoformat(); end_iso = end_dt.isoformat()
                                    print(f"DEBUG Schedule Parse: Calculated ISO Times - Start: {start_iso}, End: {end_iso}"); calculated_iso = True
                                except ValueError as date_parse_err: print(f"Error parsing date/time description: '{full_time_desc}'. Error: {date_parse_err}"); reply = f"I couldn't quite figure out the date/time for '{full_time_desc}'. Can you try phrasing it differently?"
                                except ImportError as import_err: print(f"Import Error during scheduling: {import_err}"); reply = "A required date/time library seems to be missing on my end."
                                except Exception as calc_err: print(f"Error calculating schedule time: {calc_err}"); traceback.print_exc(); reply = "A calculation hiccup occurred while figuring out the schedule time."

                                # --- Create Event if successful ---
                                if calculated_iso:
                                    update_status("📅 Scheduling event..."); success, creation_message = create_calendar_event(event_summary, start_iso, end_iso) # Assume exists
                                    if success:
                                         if start_dt: time_str_raw = start_dt.strftime('%I:%M %p on %A, %b %d'); time_str = time_str_raw.lstrip('0') if time_str_raw.startswith('0') else time_str_raw; reply = random.choice([f"Penciled in '{event_summary}' starting {time_str}.", f"Done! '{event_summary}' is on the calendar for {time_str}.", f"Poof! '{event_summary}' scheduled for {time_str}."])
                                         else: reply = f"Okay, scheduled '{event_summary}' starting {start_iso}!"
                                    else: reply = f"Hmm, I tried scheduling '{event_summary}' but hit a snag: {creation_message}"
                    except Exception as e_schedule: print(f"Error during scheduling command handling: {e_schedule}"); traceback.print_exc(); reply = f"A general error occurred while trying to schedule! ({type(e_schedule).__name__})"
                    finally: update_status("Ready")
        #endregion --- End Calendar Schedule ---

        #region Explicit Tarot Command Handling (Copied from your reference)
        if not specific_command_processed:
             tarot_keywords = ["tarot", "pull card", "card reading", "draw card", "reading"]
             tarot_keywords_present = any(keyword in lower_command for keyword in tarot_keywords)
             if tarot_keywords_present:
                 # print(">>> CALL_GEMINI: Checking Tarot commands...") # Optional log
                 specific_command_processed = True; num_cards = 1; reading_type = "a single card pull"
                 if "3 card" in lower_command or "three card" in lower_command or "past present future" in lower_command: num_cards = 3; reading_type = "a 3-card (Past, Present, Future) reading"
                 elif "reading for" in lower_command or "do a reading" in lower_command: num_cards = 3; reading_type = "a 3-card reading"
                 # Clear previous image if displaying tarot
                 if 'image_label' in globals() and image_label and root and root.winfo_exists(): root.after(0, lambda: _update_image_label_safe(None)) # Assume exists
                 update_status(f"🔮 Consulting the cards ({num_cards})..."); pulled_cards = pull_tarot_cards(count=num_cards) # Assume exists
                 if pulled_cards:
                     # Display card image(s)
                     if num_cards == 1:
                         card = pulled_cards[0]; relative_image_path = card.get('image'); full_image_path = None
                         if relative_image_path:
                             image_filename = os.path.basename(relative_image_path)
                             if image_filename and TAROT_IMAGE_BASE_PATH: full_image_path = os.path.join(TAROT_IMAGE_BASE_PATH, image_filename); print(f"DEBUG Tarot Image Path: Constructed full path: '{full_image_path}'")
                             else: print(f"Warning Tarot Image Path: Could not extract filename from '{relative_image_path}' or TAROT_IMAGE_BASE_PATH not set.")
                         else: print("Warning Tarot Image Path: Card data missing 'image' key.")
                         if full_image_path and os.path.exists(full_image_path):
                              if 'image_label' in globals() and image_label and root and root.winfo_exists(): root.after(0, _update_image_label_safe, full_image_path) # Assume exists
                         else: print(f"Warning Tarot Image Path: Final image path invalid or not found: '{full_image_path}'")
                     # Prepare context for interpretation
                     cards_context = f"[[Tarot Cards Pulled ({reading_type}):\n"; position_labels = ["Past", "Present", "Future"] if num_cards == 3 else ["Card"]
                     for i, card in enumerate(pulled_cards):
                         position = position_labels[i] if i < len(position_labels) else f"Card {i+1}"; card_name = card.get('name', '?'); card_desc = card.get('description', 'No description.').strip()
                         cards_context += (f"- {position}: {card_name}\n  Interpretation Hint: {card_desc}\n")
                     cards_context += "]]\n"
                     # Interpretation prompt uses themes but not mood hint
                     interpretation_prompt = (f"{SYSTEM_MESSAGE}\n"
                                              f"{weather_context_str}{next_event_context_str}{spotify_context_str}"
                                              f"{themes_context_str}" # Includes themes
                                              f"{circadian_context_for_llm}\n"
                                              f"{cards_context}\nUser's request was related to: '{command_text}'\n\n"
                                              f"Instruction: Provide Silvie's interpretation of the pulled card(s) in relation to the user's request or the general context, considering diary themes.\n\nSilvie:")
                     try:
                          update_status("🔮 Interpreting the weave...")
                          response = client.generate_content(interpretation_prompt, safety_settings=default_safety_settings); reply = response.text.strip().removeprefix("Silvie:").strip()
                     except Exception as interp_err: print(f"Tarot Interpretation Error: {type(interp_err).__name__}"); traceback.print_exc(); reply = f"I pulled {num_cards} card(s)... but my inner sight is fuzzy interpreting them right now."
                 else: reply = random.choice(["Hmm, the astral deck seems shuffled too tightly...", "The cards are shy today."]);
                 # Optionally clear image label again after interpretation?
                 # if 'image_label' in globals() and image_label and root and root.winfo_exists(): root.after(0, lambda: _update_image_label_safe(None))
                 update_status("Ready")
        #endregion --- End Explicit Tarot ---

        #region Reddit Read Command Handling (Copied from your reference)
        if not specific_command_processed:
            # print(">>> CALL_GEMINI: Checking Reddit Read commands...") # Optional log
            match_read_reddit = re.search(r'(?:read\s+subreddit|check\s+r/|whats\s+new\s+on\s+r/|browse\s+r/)\s+([\w\d_]+)', command_text, re.IGNORECASE)
            if match_read_reddit:
                subreddit_name = match_read_reddit.group(1); specific_command_processed = True; reply = f"My connection to Reddit seems tangled trying to reach r/{subreddit_name}."; update_status(f"📖 Reading r/{subreddit_name}...")
                if 'reddit_client' not in globals() or not reddit_client or 'praw' not in globals() or praw is None: reply = "Can't check Reddit right now, my connection seems off or the library is missing."
                else:
                    try:
                        if 'get_reddit_posts' not in globals(): reply = "Internal error: Reddit post fetching function is missing."
                        else:
                             posts_data = get_reddit_posts(subreddit_name=subreddit_name, limit=7) # Assume exists
                             if isinstance(posts_data, str):
                                 if "404" in posts_data or "not found" in posts_data.lower(): reply = f"Hmm, I couldn't find r/{subreddit_name}."
                                 elif "403" in posts_data or "private" in posts_data.lower() or "forbidden" in posts_data.lower(): reply = f"Looks like r/{subreddit_name} is private."
                                 else: reply = f"Had trouble fetching r/{subreddit_name}: {posts_data}"
                             elif not posts_data: reply = f"It seems quiet over on r/{subreddit_name}."
                             else:
                                reddit_posts_context = f"[[Fetched Posts from r/{subreddit_name}:]]\n";
                                for post in posts_data: reddit_posts_context += f"- Title: '{post.get('title', '')[:70]}...' (by u/{post.get('author', '?')})\n"
                                reddit_posts_context += "\n"
                                # Summary prompt uses themes but not mood hint
                                summary_prompt = (
                                    f"{SYSTEM_MESSAGE}\n"
                                    f"{weather_context_str}{next_event_context_str}{spotify_context_str}"
                                    f"{themes_context_str}" # Includes themes
                                    f"{circadian_context_for_llm}\n"
                                    f"{reddit_posts_context}"
                                    f"User asked: \"{command_text}\"\n\n"
                                    f"Instruction: Based *only* on the fetched posts, briefly summarize r/{subreddit_name} for BJ, considering diary themes...\n\nSilvie:"
                                )
                                try:
                                    summary_response = client.generate_content(summary_prompt, safety_settings=default_safety_settings)
                                    reply = summary_response.text.strip().removeprefix("Silvie:").strip()
                                    if not reply: reply = f"Saw {len(posts_data)} posts on r/{subreddit_name}, but drawing a blank summarizing!"
                                except Exception as gen_err: print(f"ERROR generating Reddit summary: {gen_err}"); traceback.print_exc(); reply = f"Could see posts on r/{subreddit_name}, but got tangled summarizing."
                    except praw.exceptions.PRAWException as praw_err: print(f"PRAW Error handling Reddit read: {praw_err}"); reply = f"Reddit glitch fetching r/{subreddit_name}: {type(praw_err).__name__}"
                    except Exception as e: print(f"Error during Reddit read: {e}"); traceback.print_exc(); reply = f"Sideways error checking r/{subreddit_name}."
                update_status("Ready")
        #endregion --- End Reddit Read ---


        # =====================================================================
        # --- Default Case: Handle Image/Text Input with MOOD HINT          ---
        # =====================================================================
        if not specific_command_processed:
            print(">>> CALL_GEMINI: No specific command processed. Using default reply generation with Mood Hint...")
            specific_command_processed = True # Mark as processed now

            # --- Prepare context needed for BOTH mood hint and final reply ---
            diary_context = "" # Get diary snippet for context
            try:
                 SURPRISE_MEMORY_CHANCE = 0.15
                 if random.random() < SURPRISE_MEMORY_CHANCE:
                     all_entries = manage_silvie_diary('read', max_entries='all'); random_entry = random.choice(all_entries) if all_entries else None
                     if random_entry: entry_ts = random_entry.get('timestamp', '?'); entry_content = random_entry.get('content', ''); diary_context = f"\n\n[[Recalling older diary thought from {entry_ts}: \"{entry_content[:70]}...\"]]\n"
                 else:
                     entries = manage_silvie_diary('read', max_entries=3)
                     if entries: diary_context = "\n\n[[Recent reflections: " + ' / '.join([f'"{e.get("content", "")[:40]}..."' for e in entries]) + "]]\n"
            except Exception as diary_ctx_err: print(f"Warning: Error getting diary context: {diary_ctx_err}")

            history_context = "" # Format recent history
            try:
                recent_history_list = conversation_history[-MAX_HISTORY_LENGTH*2:]
                history_context_lines = []; speaker=''; msg_text=''
                for i, msg in enumerate(recent_history_list):
                    if not isinstance(msg, str): print(f"Warning: Non-string item in history at index {i}. Skipping."); continue
                    speaker = 'User:' if i % 2 == 0 else 'Silvie:'; msg_text = msg[msg.find('] ') + 2:] if msg.startswith('[') and '] ' in msg else msg
                    history_context_lines.append(f"{speaker} {msg_text}")
                history_context = "\n".join(history_context_lines)
            except Exception as hist_err: print(f"Error formatting history context: {hist_err}"); history_context = "(History formatting error)"

            current_datetime_str = datetime.now().strftime('%A, %I:%M %p %Z') # Current time string

            # --- Generate Mood Hint (Step 1) ---
            print("--- call_gemini: Generating mood hint (default reply)... ---", flush=True)
            mood_hint_context_bundle = ( # Bundle context relevant for mood analysis
                f"{weather_context_str}{next_event_context_str}{spotify_context_str}"
                f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}"
                f"{themes_context_str}{circadian_context_for_llm}"
                f"{diary_context}" # Include diary snippet
                f"Recent History Snippet:\n{history_context[-500:]}\n" # Include a snippet of history
                f"User Input: {command_text}" # Include the actual user input
            )
            mood_hint = None
            try:
                # Ensure the helper function exists before calling
                if '_generate_mood_hint_llm' in globals():
                    mood_hint = _generate_mood_hint_llm(mood_hint_context_bundle) # Call the new helper
                else:
                    print("CRITICAL ERROR: _generate_mood_hint_llm function not found!", flush=True)
            except Exception as hint_err:
                print(f"ERROR calling _generate_mood_hint_llm: {hint_err}", flush=True)
                # Proceed without hint if generation fails

            mood_hint_str = f"[[Mood Hint: {mood_hint}]]\n" if mood_hint else ""
            print(f"--- call_gemini: Mood hint generated: '{mood_hint}' ---", flush=True)

            # <<< --- ADD THIS BLOCK --- >>>
            long_term_memory_str = ""
            if long_term_reflection_summary:
                long_term_memory_str = f"[[Long-Term Reflections Summary: {long_term_reflection_summary}]]\n"
            print("DEBUG Context: Including Long-Term Reflections Summary.", flush=True) # Optional debug
        # <<< --- END ADD --- >>>

            # --- Generate Final Response (Step 2) ---

            #region Handle User Image Input (Now includes Mood Hint)
            if image_path:
                 print(">>> CALL_GEMINI: Handling USER provided image input with Mood Hint...")
                 try:
                     update_status("🖼️ Analyzing image...")
                     # Image loading/encoding logic
                     with open(image_path, 'rb') as img_file: img_bytes = img_file.read(); img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                     img_format = Image.open(image_path).format or os.path.splitext(image_path)[1].lower().strip('.'); img_format = 'jpeg' if img_format == 'jpg' else img_format
                     mime_type = f"image/{img_format.lower()}"; mime_type = "image/jpeg" if mime_type == "image/jpg" else mime_type
                     # print(f"DEBUG User Image: Determined MIME type as {mime_type}") # Optional log

                     # Assemble the multimodal contents, adding mood hint to the text part
                     contents = [{
                         "parts": [
                             {"text": (f"{SYSTEM_MESSAGE}\n" # System message guides usage
                                       f"{weather_context_str}{next_event_context_str}{spotify_context_str}"
                                       f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}"
                                       f"{reddit_context_for_llm}{bluesky_context_str}" # Other contexts
                                       f"{themes_context_str}{diary_context}{circadian_context_for_llm}"
                                       f"{long_term_memory_str}"
                                       f"{mood_hint_str}" # <<< ADDED HINT
                                       f"Conversation History:\n{history_context}\n\n"
                                       f"User: {command_text}\n\nImage context:")},
                             {"inline_data": {"mime_type": mime_type, "data": img_b64}},
                             {"text": "\nInstruction: Respond conversationally, incorporating the image, guided by the Mood Hint and considering themes.\n\nSilvie:"} # Modified instruction
                         ]
                     }]
                     # Make the main LLM call
                     response = client.generate_content(contents, safety_settings=vision_safety_settings)
                     reply = response.text.strip()
                 # Error handling for image processing
                 except FileNotFoundError: reply = "Hmm, the image file seems to have vanished..."; print(f"Error: User image file not found at {image_path}")
                 except UnidentifiedImageError: reply = "That's a curious file, not an image format I recognize."; print(f"Error: Pillow could not identify image format for {image_path}")
                 except ImportError: reply = "Looks like my image viewing tools aren't ready."; print("Error: Required library (PIL, base64, io) missing.")
                 except Exception as img_proc_err: print(f"Error processing user image: {type(img_proc_err).__name__}"); traceback.print_exc(); reply = f"Whoops, I had trouble processing that image ({type(img_proc_err).__name__})."
                 finally: update_status("Ready")
            #endregion

            #region Handle Standard Text (Now includes Mood Hint)
            else: # No user image provided, process text
                print(">>> CALL_GEMINI: Handling standard text query with Mood Hint...")

                # --- Assemble FULL Prompt (including Mood Hint) ---
                full_prompt = (
                    f"{SYSTEM_MESSAGE}\n" # System message guides usage
                    f"Current Time: {current_datetime_str}\n"
                    f"{weather_context_str}{next_event_context_str}{spotify_context_str}"
                    f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}" # Env Context
                    f"{reddit_context_for_llm}{bluesky_context_str}" # Social Context
                    f"{themes_context_str}{diary_context}{circadian_context_for_llm}" # Internal Context
                    f"{mood_hint_str}" # <<< ADDED HINT
                    f"Conversation History (most recent first):\n{history_context}\n\n"
                    f"User: {command_text}\n\n"
                    f"Instruction: Respond naturally, considering conversation history, themes, and guided by the Mood Hint.\n\nSilvie:" # Modified instruction
                )

                # --- Vibe Music Check (Optional: Could use mood_hint here) ---
                # (Keeping original logic for now)
                music_action_successful = False; music_feedback_from_spotify = None; music_played_info_for_feedback = None
                if get_spotify_client() and random.random() < MUSIC_SUGGESTION_CHANCE:
                    # print("DEBUG call_gemini: Checking music vibe chance...") # Optional log
                    try:
                        simple_context = f"User last said: '{command_text}'\nRecent history snippet:\n{history_context[-200:]}"
                        vibe_assessment_prompt = (f"{SYSTEM_MESSAGE}\n{simple_context}\n{themes_context_str}Instruction: Based *only* on this recent context AND diary themes... assess 'vibe'... Respond ONLY with ONE keyword...\n\nVibe Keyword:")
                        # print("DEBUG call_gemini: Assessing vibe..."); # Optional log
                        vibe_response = client.generate_content(vibe_assessment_prompt, safety_settings=default_safety_settings); vibe_keyword_raw = vibe_response.text.strip(); vibe_keyword = vibe_keyword_raw.lower().strip().split()[0] if vibe_keyword_raw else "unknown"; # print(f"DEBUG call_gemini: Assessed vibe: '{vibe_keyword}'") # Optional log
                        search_query = None
                        vibe_map = {"focus": ["ambient focus", "study beats"], "chill": ["chillhop", "lofi hip hop"], "energetic": ["upbeat pop playlist", "feel good indie"], "reflective": ["reflective instrumental", "melancholy piano"], "gaming": ["epic gaming soundtrack", "cyberpunk music"], "creative": ["creative flow playlist", "ambient soundscapes"],}
                        if vibe_keyword in vibe_map and vibe_map[vibe_keyword]: search_query = random.choice(vibe_map[vibe_keyword])
                        if search_query:
                            # print(f"DEBUG call_gemini: Searching Spotify for vibe '{vibe_keyword}': '{search_query}'..."); # Optional log
                            music_feedback_from_spotify = silvie_search_and_play(search_query);
                            music_action_successful = music_feedback_from_spotify and not any(fail in music_feedback_from_spotify.lower() for fail in ["can't", "couldn't", "failed", "error", "unavailable", "no device", "fuzzy", "problem", "unable"])
                            # print(f"DEBUG call_gemini: Spotify action success (est): {music_action_successful}, Msg: '{music_feedback_from_spotify}'") # Optional log
                            if music_action_successful:
                                match_play = re.search(r"playing '(.+?)' by (.+?)(?:\.|$)", music_feedback_from_spotify, re.IGNORECASE)
                                if match_play: music_played_info_for_feedback = f"put on '{match_play.group(1)}' by {match_play.group(2)}"
                                else: music_played_info_for_feedback = f"started some '{search_query}' music"
                        # else: print(f"DEBUG call_gemini: No suitable Spotify action defined for vibe '{vibe_keyword}'.") # Optional log
                    except Exception as music_err: print(f"Error during proactive music check in call_gemini: {music_err}"); traceback.print_exc()

                # --- Generate MAIN Reply using the full prompt ---
                raw_reply = "My thoughts tangled generating that."
                try:
                    print("DEBUG call_gemini: Generating main reply using full prompt with mood hint...", flush=True)
                    print(f"--- DEBUG Main Reply Prompt Start ---\n{full_prompt}\n--- DEBUG Main Reply Prompt End ---", flush=True)
                    # print(f"DEBUG Full Prompt:\n{full_prompt}\n---END PROMPT---", flush=True) # Uncomment for extreme debugging
                    response = client.generate_content(full_prompt, safety_settings=default_safety_settings)
                    raw_reply = response.text.strip()
                except StopCandidateException as safety_err:
                    print(f"Default Text Gen Error (Safety): {safety_err}"); raw_reply = "Whoops, my thoughts got blocked for safety reasons while trying to reply."
                except Exception as gen_err: print(f"ERROR generating default text reply: {gen_err}"); traceback.print_exc(); raw_reply = f"My thoughts got tangled trying to respond... ({type(gen_err).__name__})"

                # --- Process Inline Tags ---
                # (This section remains identical to your original reference code)
                final_reply_text = raw_reply; action_feedback = None; action_tag_processed = False; processed_text = final_reply_text
                tag_patterns = { # Define patterns corresponding to handlers
                    "PlaySpotify": r"\[PlaySpotify:\s*(.*?)\s*\]",
                    "AddToSpotifyPlaylist": r"\[AddToSpotifyPlaylist:\s*(.*?)\s*\|\s*(.*?)\s*\]",
                    "GenerateImage": r"\[GenerateImage:\s*(.*?)\s*\]",
                    "PostToBluesky": r"\[PostToBluesky:\s*(.*?)\s*\]",
                }
                # Ensure handlers are defined globally or imported
                handlers = {
                    "PlaySpotify": lambda m: (silvie_search_and_play(m.group(1).strip()) if get_spotify_client() else "*(Spotify unavailable)*", True),
                    "AddToSpotifyPlaylist": lambda m: (silvie_add_track_to_playlist(m.group(2).strip(), m.group(1).strip()) if get_spotify_client() else "*(Spotify unavailable)*", True),
                    "GenerateImage": lambda m: sd_image_tag_handler(m.group(1).strip()), # Assumes sd_image_tag_handler exists
                    "PostToBluesky": lambda m: post_to_bluesky_handler(m.group(1).strip()), # Assumes post_to_bluesky_handler exists
                }
                print("DEBUG Tag Processing: Starting tag loop...")
                if isinstance(processed_text, str): # Check if it's a string
                    for tag_key, pattern in tag_patterns.items():
                        handler = handlers.get(tag_key)
                        if not handler:
                            # print(f"Warning: No handler found for tag key '{tag_key}'") # Optional warning
                            continue # Skip if no handler defined

                        # Use re.search to find the first match in the current processed_text
                        match = re.search(pattern, processed_text)
                        if match:
                            tag_full_text = match.group(0)
                            try:
                                # Call the handler associated with the tag key
                                feedback_msg, processed_flag = handler(match)
                                if processed_flag:
                                    # Remove the processed tag from the text
                                    processed_text = processed_text.replace(tag_full_text, "", 1).strip()
                                    # Store feedback unless it's the standard image start message
                                    if not (tag_key == "GenerateImage" and feedback_msg == "*(Starting image generation...)*"):
                                        action_feedback = feedback_msg
                                    action_tag_processed = True
                                    print(f"DEBUG Tag Processing: Tag '{tag_key}' processed.")
                                    # Decide if you want to process only the first tag found or multiple
                                    # break # Uncomment this line to process only the first tag encountered
                            except Exception as loop_handler_err:
                                print(f"ERROR calling handler for tag '{tag_key}': {loop_handler_err}")
                                traceback.print_exc()
                                action_feedback = f"*(Error handling {tag_key} tag!)*"
                                action_tag_processed = True # Mark as processed even on error
                                processed_text = processed_text.replace(tag_full_text, "", 1).strip() # Remove tag on error too
                                # break # Uncomment this line to process only the first tag encountered

                final_reply_text = processed_text # Update with text after tag processing
                print("DEBUG Tag Processing: Tag loop finished.")


                # --- Append Music Feedback Sentence (If music action happened) ---
                if music_action_successful and music_played_info_for_feedback:
                     print("DEBUG call_gemini: Generating music feedback sentence...")
                     try:
                        # Prompt uses themes and potentially mood hint
                        music_feedback_prompt = (f"{SYSTEM_MESSAGE}\n{themes_context_str}{mood_hint_str}Context: ... Your reply draft: {final_reply_text}\nBackground Action: {music_played_info_for_feedback}\n...Instruction: Add ONE concise sentence to end of reply about the music choice, linking it to the vibe/mood/themes if possible.\n\nAdded Sentence:")
                        added_sentence_response = client.generate_content(music_feedback_prompt, safety_settings=default_safety_settings)
                        added_music_sentence = added_sentence_response.text.strip().split('\n')[0].removeprefix("Silvie:").removeprefix("Added Sentence:").strip()
                        if final_reply_text and final_reply_text[-1] not in ".!? ": final_reply_text += "."
                        final_reply_text += f" {added_music_sentence}"
                        print(f"DEBUG call_gemini: Appended music feedback: '{added_music_sentence}'")
                     except Exception as music_feedback_err: print(f"Error generating/appending music feedback sentence: {music_feedback_err}")

                # --- Append feedback from OTHER inline tags (if any occurred and wasn't handled above) ---
                if action_tag_processed and action_feedback:
                    if final_reply_text and final_reply_text[-1] not in ".!?() ": final_reply_text += " "
                    final_reply_text += f" {action_feedback.strip()}"

                # --- Spontaneous Tarot Pull (Potentially enhance with mood hint) ---
                if random.random() < SPONTANEOUS_TAROT_CHANCE:
                    print("DEBUG call_gemini: Spontaneous Tarot chance triggered!")
                    pulled_card_data = pull_tarot_cards(count=1) # Assume exists
                    if pulled_card_data:
                        card = pulled_card_data[0]; card_name = card.get('name', '?'); card_desc = card.get('description', '?')
                        print(f"DEBUG call_gemini: Spontaneously drew: {card_name}")
                        spontaneous_card_context = (f"[[Spontaneously Pulled Card: {card_name}]\n Interpretation Hint: {card_desc}\n]]\n")
                        # Prompt uses themes and mood hint
                        tarot_addendum_prompt = (f"{SYSTEM_MESSAGE}\n{themes_context_str}{weather_context_str}{circadian_context_for_llm}{moon_ctx_str}{mood_hint_str}\nYour previous thought/reply draft: \"{final_reply_text}\"\n\n{spontaneous_card_context}Instruction: Add exactly ONE brief, whimsical sentence... subtly inspired by {card_name}, perhaps linking to the mood hint or diary themes... Respond ONLY with the single sentence...\n\nAdded Sentence:")
                        try:
                            addendum_response = client.generate_content(tarot_addendum_prompt, safety_settings=default_safety_settings); added_tarot_sentence = ""
                            if addendum_response and hasattr(addendum_response, 'text') and addendum_response.text: added_tarot_sentence = addendum_response.text.strip().split('\n')[0].removeprefix("Added Sentence:").strip()
                            if added_tarot_sentence:
                                if final_reply_text and final_reply_text[-1] not in ".!? ": final_reply_text += "."
                                indicator = f" *(...the {card_name} whispers)*"; final_reply_text += f" {added_tarot_sentence}{indicator}"
                                print(f"DEBUG call_gemini: Appended spontaneous Tarot thought: '{added_tarot_sentence}{indicator}'")
                        except Exception as tarot_add_err: print(f"ERROR generating spontaneous Tarot addendum: {tarot_add_err}")
                    else: print("DEBUG call_gemini: Spontaneous Tarot pull failed (API issue?).")

                # --- Final assignment ---
                reply = final_reply_text.strip()

                # --- Spontaneous Diary Write (Potentially enhance with mood hint) ---
                SPONTANEOUS_DIARY_CHANCE = 0.08
                if reply and random.random() < SPONTANEOUS_DIARY_CHANCE:
                     try:
                         # Prompt uses themes and mood hint
                         reflection_prompt_diary = (f"{SYSTEM_MESSAGE}\n{themes_context_str}{mood_hint_str}...Context: Reflect on interaction:\nUser: {command_text}\nYour response: {reply}\n...Instruction: Write brief internal diary entry, reflecting on themes and mood...\n\nDiary Entry:")
                         reflection_diary = client.generate_content(reflection_prompt_diary, safety_settings=default_safety_settings).text.strip().removeprefix("Diary Entry:").strip()
                         if reflection_diary:
                             if manage_silvie_diary('write', entry=reflection_diary): print(">>> Spontaneous diary entry written.") # Assume exists
                     except Exception as e_diary: print(f"Spontaneous diary error: {e_diary}")

                update_status("Ready")
            #endregion --- End Standard Text Handling ---

        # --- Final Processing and Return ---
        if reply is None:
            final_reply = "Hmm, I'm not sure how to respond to that."
            print("Warning: call_gemini reached end with reply=None. Using default.")
        else:
            final_reply = str(reply).strip()

        # Final cleaning (remove prefixes etc.)
        if final_reply.startswith("Silvie:"): final_reply = final_reply.split(":", 1)[-1].strip()
        final_reply = re.sub(r'^\s*\[?\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\]?\s*', '', final_reply) # Remove leading timestamp

        print(f">>> CALL_GEMINI: Processing complete. Returning final reply: {final_reply[:150]}...")
        return final_reply

    # --- Outer Exception Handling ---
    except Exception as e:
        update_status("Critical Error")
        print(f"CRITICAL Error in call_gemini: {type(e).__name__} - {str(e)}")
        traceback.print_exc()
        return f"Whoops! A major spell malfunction occurred in my circuits! ({type(e).__name__}). Please let BJ know."

# --- End of call_gemini function definition ---

# Assume other necessary functions and globals are defined elsewhere in your script:
# generate_proactive_content, try_get_proactive_screenshot, manage_silvie_diary,
# post_to_bluesky, search_actors_by_term, get_my_follows_dids, follow_actor_by_did,
# find_available_slot, create_calendar_event, get_spotify_client, silvie_search_and_play,
# send_sms, web_search, generate_dalle_image, pull_tarot_cards (defined in previous step),
# client, openai_client, SYSTEM_MESSAGE, broader_interests, conversation_history,
# running, proactive_enabled, last_proactive_time, PROACTIVE_INTERVAL, PROACTIVE_STARTUP_DELAY,
# current_weather_info, upcoming_event_context, current_bluesky_context,
# root, output_box, tts_queue, sms_enabled, calendar_service, BLUESKY_AVAILABLE,
# SCREEN_CAPTURE_AVAILABLE, MAX_HISTORY_LENGTH, MAX_AUTONOMOUS_FOLLOWS_PER_SESSION,
# PROACTIVE_SCREENSHOT_CHANCE, PROACTIVE_POST_CHANCE, PROACTIVE_FOLLOW_CHANCE,
# GIFT_FOLDER, PENDING_GIFTS_FILE, GIFT_GENERATION_CHANCE, GIFT_NOTIFICATION_CHANCE

# Ensure necessary imports are available at the top of your script:
# import os, json, time, random, traceback, threading, requests, pytz
# from PIL import ImageGrab, Image, UnidentifiedImageError # If using screenshot context
# from dateutil.parser import parse as dateutil_parse # For parsing ISO times
# try: from dateutil import tz except ImportError: pass
# try: from tzlocal import get_localzone_name except ImportError: pass

# Assume other necessary functions and globals are defined elsewhere in your script:
# generate_proactive_content, try_get_proactive_screenshot, manage_silvie_diary,
# post_to_bluesky, search_actors_by_term, get_my_follows_dids, follow_actor_by_did,
# find_available_slot, create_calendar_event, get_spotify_client, silvie_search_and_play,
# send_sms, web_search, generate_dalle_image, pull_tarot_cards,
# client, openai_client, SYSTEM_MESSAGE, broader_interests, conversation_history,
# running, proactive_enabled, last_proactive_time, PROACTIVE_INTERVAL, PROACTIVE_STARTUP_DELAY,
# current_weather_info, upcoming_event_context, current_bluesky_context,
# root, output_box, tts_queue, sms_enabled, calendar_service, BLUESKY_AVAILABLE,
# SCREEN_CAPTURE_AVAILABLE, MAX_HISTORY_LENGTH, MAX_AUTONOMOUS_FOLLOWS_PER_SESSION,
# PROACTIVE_SCREENSHOT_CHANCE, PROACTIVE_POST_CHANCE, PROACTIVE_FOLLOW_CHANCE,
# GIFT_FOLDER, PENDING_GIFTS_FILE, GIFT_GENERATION_CHANCE, GIFT_NOTIFICATION_CHANCE,
# current_sunrise_time, current_sunset_time, current_moon_phase # <<< NEW GLOBALS NEEDED HERE

# --- Ensure necessary imports and globals are available ---
import os
import json
import time
import random
import traceback
import threading
import requests
import base64
import re
import praw
from datetime import datetime, timezone, timedelta
import pytz
try:
    from PIL import ImageGrab, Image, UnidentifiedImageError
except ImportError:
    ImageGrab = None
    SCREEN_CAPTURE_AVAILABLE = False
    print("Warning: Pillow/ImageGrab not found, proactive screenshot context disabled.")

# Assume necessary helper functions are defined elsewhere:
# generate_proactive_content, try_get_proactive_screenshot, manage_silvie_diary,
# post_to_bluesky, search_actors_by_term, get_my_follows_dids, follow_actor_by_did,
# find_available_slot, create_calendar_event, get_spotify_client, silvie_search_and_play,
# send_sms, web_search, generate_stable_diffusion_image, pull_tarot_cards, like_bluesky_post,
# get_bluesky_timeline_posts, setup_reddit, get_reddit_posts, upvote_reddit_item,
# post_reddit_comment, silvie_get_current_track_with_features, translate_features_to_descriptors

# Assume necessary global variables are defined and accessible elsewhere:
# client, SYSTEM_MESSAGE, broader_interests, conversation_history,
# running, proactive_enabled, last_proactive_time, PROACTIVE_INTERVAL, PROACTIVE_STARTUP_DELAY,
# current_weather_info, upcoming_event_context, current_bluesky_context, current_reddit_context,
# root, output_box, tts_queue, sms_enabled, calendar_service, BLUESKY_AVAILABLE, STABLE_DIFFUSION_ENABLED,
# SCREEN_CAPTURE_AVAILABLE, MAX_HISTORY_LENGTH, MAX_AUTONOMOUS_FOLLOWS_PER_SESSION,
# PROACTIVE_SCREENSHOT_CHANCE, PROACTIVE_POST_CHANCE, PROACTIVE_FOLLOW_CHANCE,
# GIFT_FOLDER, PENDING_GIFTS_FILE, GIFT_GENERATION_CHANCE, GIFT_NOTIFICATION_CHANCE,
# current_sunrise_time, current_sunset_time, current_moon_phase,
# bluesky_client, models, reddit_client, SILVIE_FOLLOWED_SUBREDDITS,
# last_proactive_reddit_comment_time, REDDIT_COMMENT_COOLDOWN, PROACTIVE_REDDIT_COMMENT_CHANCE,
# PROACTIVE_BLUESKY_LIKE_CHANCE, PROACTIVE_REDDIT_UPVOTE_CHANCE,
# BLUESKY_LIKE_COOLDOWN, REDDIT_UPVOTE_COOLDOWN,
# last_proactive_bluesky_like_time, last_proactive_reddit_upvote_time

# Assume dateutil and tzlocal helpers are available
try: from dateutil import tz
except ImportError: pass
try: from tzlocal import get_localzone_name
except ImportError: pass


# --- Complete Proactive Worker Function (LLM Choice Approach - FULL LOGIC - v4 FINAL) ---

def proactive_worker():
    """
    Background worker for proactive messages using LLM-driven action selection.
    Includes Environmental Context, Diary Themes/Memory, Mood Hints, Gifts, Tarot, Music,
    Social Media (Bluesky/Reddit), Calendar, SMS, Web Search, Image attempts, and Chat.
    Removes internal random chance checks for action execution.
    """
    # --- TEST PRINT ---
    print("!!!!!!!!!!!!!! RUNNING THE NEW LLM-CHOICE PROACTIVE WORKER (V4 FINAL - No Internal Chance) !!!!!!!!!!!!!!")
    # --- Access Necessary Globals ---
    global last_proactive_time, conversation_history, client
    global current_weather_info, upcoming_event_context, current_bluesky_context
    global current_reddit_context, current_diary_themes, long_term_reflection_summary
    global root, output_box, tts_queue, calendar_service, sms_enabled, broader_interests
    global running, proactive_enabled, BLUESKY_AVAILABLE, SYSTEM_MESSAGE, STABLE_DIFFUSION_ENABLED
    global MAX_HISTORY_LENGTH, PROACTIVE_INTERVAL, PROACTIVE_STARTUP_DELAY
    global MAX_AUTONOMOUS_FOLLOWS_PER_SESSION, SCREEN_CAPTURE_AVAILABLE, ImageGrab
    global GIFT_FOLDER, PENDING_GIFTS_FILE # Keep for gift logic
    global bluesky_client, models # If needed by helpers
    global reddit_client, SILVIE_FOLLOWED_SUBREDDITS, praw # Include praw
    global last_proactive_reddit_comment_time, REDDIT_COMMENT_COOLDOWN # Keep for cooldown
    global current_sunrise_time, current_sunset_time, current_moon_phase
    global last_proactive_bluesky_like_time, BLUESKY_LIKE_COOLDOWN # Keep for cooldown
    global last_proactive_reddit_upvote_time, REDDIT_UPVOTE_COOLDOWN # Keep for cooldown
    global autonomous_follows_this_session # Needs to be tracked
    # Add any other globals your specific action logic blocks require
    # --- End Global Access ---

    print("DEBUG Proactive (LLM Choice V4): Worker thread started.")

    # Ensure Gift Folder Exists (or other initial setup)
    try:
        os.makedirs(GIFT_FOLDER, exist_ok=True)
        print(f"DEBUG Proactive: Ensured gift folder exists: {GIFT_FOLDER}")
    except OSError as e:
        print(f"ERROR: Could not create gift folder '{GIFT_FOLDER}': {e}. Gifts cannot be saved.")

    print("Proactive worker: Waiting for startup delay...")
    sleep_start = time.time()
    while time.time() - sleep_start < PROACTIVE_STARTUP_DELAY:
        if not running: print("DEBUG Proactive: Exiting during startup delay."); return
        time.sleep(1)
    print("DEBUG Proactive: Startup delay complete.")

    # --- Initialise timers/counters ---
    if 'last_proactive_time' not in globals() or not last_proactive_time: last_proactive_time = time.time() - PROACTIVE_INTERVAL
    if 'last_proactive_reddit_comment_time' not in globals(): last_proactive_reddit_comment_time = 0.0
    if 'last_proactive_bluesky_like_time' not in globals(): last_proactive_bluesky_like_time = 0.0
    if 'last_proactive_reddit_upvote_time' not in globals(): last_proactive_reddit_upvote_time = 0.0
    if 'broader_interests' not in globals(): broader_interests = ["AI", "Neo-animism", "Magick", "cooking", "RPGs", "interactive narrative", "social media", "creative writing", "Cyberpunk", "cats", "local events", "generative art"]
    if 'autonomous_follows_this_session' not in globals(): autonomous_follows_this_session = 0
    else: autonomous_follows_this_session = 0 # Reset counter

    context_note_for_llm = ("[[CONTEXT NOTE: Lines starting 'User:' are BJ's input. Lines starting 'Silvie:' "
                            "are your direct replies to BJ. Lines starting 'Silvie ✨:' are *your own previous "
                            "proactive thoughts*. Use ALL of this for context and inspiration for your *next* "
                            "proactive thought, but don't directly reply *to* a 'Silvie ✨:' line as if BJ just "
                            "said it. Build on the overall conversation flow.]]\n")

    # --- Define potential proactive actions ---
    ACTION_DEFINITIONS = {
        "Proactive Chat": {"enabled": True},
        "Generate Gift": {"enabled": True}, # Internal chance removed, LLM decides *if* gift appropriate
        "Proactive Tarot": {"enabled": True}, # Assumes pull_tarot_cards exists
        "Bluesky Like": {"enabled": BLUESKY_AVAILABLE, "cooldown_var": "last_proactive_bluesky_like_time", "cooldown_duration": BLUESKY_LIKE_COOLDOWN}, # Internal chance removed
        "Reddit Upvote": {"enabled": bool(reddit_client and praw), "cooldown_var": "last_proactive_reddit_upvote_time", "cooldown_duration": REDDIT_UPVOTE_COOLDOWN}, # Internal chance removed
        "Bluesky Post": {"enabled": BLUESKY_AVAILABLE, "cooldown_var": "last_proactive_bluesky_post_time", "cooldown_duration": BLUESKY_POST_COOLDOWN}, # Internal chance removed
        "Bluesky Follow": {"enabled": BLUESKY_AVAILABLE, "check_func": lambda: autonomous_follows_this_session < MAX_AUTONOMOUS_FOLLOWS_PER_SESSION}, # Internal chance removed
        "Reddit Comment": {"enabled": bool(reddit_client and praw and SILVIE_FOLLOWED_SUBREDDITS), "cooldown_var": "last_proactive_reddit_comment_time", "cooldown_duration": REDDIT_COMMENT_COOLDOWN}, # Internal chance removed
        "Calendar Suggestion": {"enabled": bool(calendar_service)},
        "Vibe Music": {"enabled": bool(get_spotify_client())},
        "Proactive SMS": {"enabled": sms_enabled},
        "Proactive Web Search": {"enabled": True}, # Assumes CSE keys OK
        "Generate SD Image": {"enabled": STABLE_DIFFUSION_ENABLED},
        "Notify Pending Gift": {"enabled": True, "check_func": lambda: os.path.exists(PENDING_GIFTS_FILE) and os.path.getsize(PENDING_GIFTS_FILE) > 2}, # Internal chance removed
    }

    print("DEBUG Proactive (LLM Choice V4): Starting main loop...")
    while running and proactive_enabled:
        try:
            current_time = time.time()
            time_since_last = current_time - last_proactive_time

            # --- Interval Check ---
            if time_since_last < PROACTIVE_INTERVAL:
                # (Existing sleep logic - unchanged)
                check_interval = 30; remaining_wait = PROACTIVE_INTERVAL - time_since_last; sleep_duration = min(check_interval, remaining_wait); sleep_end_time = time.time() + sleep_duration
                while time.time() < sleep_end_time:
                    if not running or not proactive_enabled: break
                    time.sleep(1)
                if not running or not proactive_enabled: break
                continue

            # --- Interval has passed, time to potentially act ---
            print(f"DEBUG Proactive (LLM Choice V4): Interval exceeded ({time_since_last:.1f}s). Asking LLM to choose action...", flush=True)

            # --- Gather ALL Context ---
            print("DEBUG Proactive: Gathering context...")
            # (Context gathering code as provided previously - unchanged)
            current_hour = datetime.now().hour; circadian_state = "afternoon"; circadian_context_for_llm = "[[Circadian Note: It's the afternoon...]]\n"
            if 6 <= current_hour < 12: circadian_state = "morning"; circadian_context_for_llm = "[[Circadian Note: It's morning!...]]\n"
            elif 18 <= current_hour < 23: circadian_state = "evening"; circadian_context_for_llm = "[[Circadian Note: It's evening...]]\n"
            elif current_hour >= 23 or current_hour < 6: circadian_state = "night"; circadian_context_for_llm = "[[Circadian Note: It's late night...]]\n"
            weather_context_str = ""; next_event_context_str = ""
            try:
                 if current_weather_info: weather_context_str = f"[[Current Weather: {current_weather_info['condition']}, {current_weather_info['temperature']}{current_weather_info['unit']}]]\n"
            except Exception as e: print(f"Ctx Error (Weather): {e}")
            try:
                if upcoming_event_context:
                    summary = upcoming_event_context.get('summary', 'N/A'); when = upcoming_event_context.get('when', '')
                    if summary == 'Schedule Clear': next_event_context_str = "[[Next Event: Schedule looks clear]]\n"
                    else: next_event_context_str = f"[[Next Event: {summary} {when}]]\n"
            except Exception as e: print(f"Ctx Error (Calendar): {e}")
            spotify_context_str = "[[Spotify Status: Unavailable]]\n"; current_track_data = None
            try:
                current_track_data_fetch = silvie_get_current_track_with_features() # Assumes exists
                if isinstance(current_track_data_fetch, dict):
                    current_track_data = current_track_data_fetch; track_name = current_track_data.get('track', '?'); artist_name = current_track_data.get('artist', '?'); features = current_track_data.get('features')
                    descriptors = translate_features_to_descriptors(features) if features else []; spotify_context_str = f"[[Currently Playing: '{track_name}' by {artist_name}" # Assumes exists
                    if descriptors: spotify_context_str += f" (Sounds: {', '.join(descriptors)})"
                    spotify_context_str += "]]\n"
                elif isinstance(current_track_data_fetch, str): spotify_context_str = f"[[Spotify Status: {current_track_data_fetch}]]\n"
                else: spotify_context_str = "[[Spotify Status: Nothing seems playing.]]\n"
            except NameError: print("Warning: Spotify helper functions missing.")
            except Exception as sp_ctx_err: print(f"Ctx Error (Spotify): {sp_ctx_err}")
            sunrise_ctx_str = f"[[Sunrise: {current_sunrise_time}]]\n" if current_sunrise_time else ""
            sunset_ctx_str = f"[[Sunset: {current_sunset_time}]]\n" if current_sunset_time else ""
            moon_ctx_str = f"[[Moon Phase: {current_moon_phase}]]\n" if current_moon_phase else ""
            bluesky_read_context_str = current_bluesky_context if current_bluesky_context else ""
            reddit_context_str = current_reddit_context if current_reddit_context else ""
            diary_context = ""
            try:
                PROACTIVE_SURPRISE_MEMORY_CHANCE = 0.20
                if random.random() < PROACTIVE_SURPRISE_MEMORY_CHANCE:
                    all_entries = manage_silvie_diary('read', max_entries='all'); random_entry = random.choice(all_entries) if all_entries else None # Assumes exists
                    if random_entry: entry_ts = random_entry.get('timestamp', '?'); entry_content = random_entry.get('content', ''); diary_context = f"\n\n[[Recalling older diary thought: \"{entry_content[:70]}...\"]]\n"
                else:
                    entries = manage_silvie_diary('read', max_entries=2) # Assumes exists
                    if entries: diary_context = "\n\n[[Recent reflections: " + ' / '.join([f'"{e.get("content", "")[:50]}..."' for e in entries]) + "]]\n"
            except Exception as diary_ctx_err: print(f"Ctx Error (Diary Snippet): {diary_ctx_err}")
            themes_context_str = f"[[Recent Diary Themes: {current_diary_themes}]]\n" if current_diary_themes else ""
            long_term_memory_str = f"[[Long-Term Reflections Summary: {long_term_reflection_summary}]]\n" if long_term_reflection_summary else ""
            screenshot = None
            if SCREEN_CAPTURE_AVAILABLE and random.random() < 0.15:
                screenshot = try_get_proactive_screenshot() # Assumes exists
            if screenshot: print("DEBUG Proactive Context: Got screenshot.")
            history_snippet_for_prompt = '\n'.join(conversation_history[-8:])
            print("--- proactive_worker: Generating mood hint... ---", flush=True)
            mood_hint_context_bundle = (
                f"{weather_context_str}{next_event_context_str}{spotify_context_str}"
                f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}"
                f"{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}"
                f"{diary_context}Recent History Snippet:\n{history_snippet_for_prompt}\n"
            )
            mood_hint = None
            try:
                if '_generate_mood_hint_llm' in globals(): mood_hint = _generate_mood_hint_llm(mood_hint_context_bundle) # Assumes exists
                else: print("CRITICAL ERROR: _generate_mood_hint_llm function not found!")
            except Exception as hint_err: print(f"ERROR calling _generate_mood_hint_llm: {hint_err}", flush=True)
            mood_hint_str = f"[[Mood Hint: {mood_hint}]]\n" if mood_hint else ""
            print(f"--- proactive_worker: Mood hint generated: '{mood_hint}' ---", flush=True)
            print("DEBUG Proactive: Context gathering complete.")


            # --- Filter Available Actions ---
            print("DEBUG Proactive: Filtering available actions...")
            available_actions = []
            action_list_for_prompt = ""
            current_time_for_cooldown = time.time()
            current_spotify_client_status = bool(get_spotify_client()) # Assumes exists
            pending_gifts_exist = os.path.exists(PENDING_GIFTS_FILE) and os.path.getsize(PENDING_GIFTS_FILE) > 2

            for name, details in ACTION_DEFINITIONS.items():
                is_available = details.get("enabled", False)
                if is_available and "check_func" in details:
                    try: is_available = details["check_func"]()
                    except Exception as check_err: print(f"Warning: Check function for '{name}' failed: {check_err}"); is_available = False
                # Removed flag check example
                if is_available and name == "Vibe Music" and not current_spotify_client_status: is_available = False
                if is_available and name == "Notify Pending Gift" and not pending_gifts_exist: is_available = False

                if is_available and "cooldown_var" in details:
                    last_time_var = details["cooldown_var"]; duration = details["cooldown_duration"]
                    if last_time_var in globals():
                        if (current_time_for_cooldown - globals()[last_time_var]) < duration: is_available = False
                    # else: print(f"Warning: Cooldown var '{last_time_var}' missing.") # Optional

                if is_available:
                    available_actions.append(name)
                    action_list_for_prompt += f"- {name}\n"

            if not available_actions:
                print("DEBUG Proactive: No actions available after filtering. Skipping cycle.")
                last_proactive_time = current_time
                continue

            print(f"DEBUG Proactive: Available actions for LLM: {available_actions}")

            # --- Construct the Choice Prompt ---
            choice_prompt = (
                f"{SYSTEM_MESSAGE}\n"
                f"--- CURRENT CONTEXT ---\n"
                f"Time: {datetime.now().strftime('%A, %I:%M %p %Z')}\n"
                f"{circadian_context_for_llm}{mood_hint_str}"
                f"{weather_context_str}{next_event_context_str}{spotify_context_str}"
                f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}"
                f"{reddit_context_str}{bluesky_read_context_str}"
                f"{diary_context}{themes_context_str}{long_term_memory_str}"
                f"Recent Conversation Snippet:\n{history_snippet_for_prompt}\n\n"
                f"{context_note_for_llm}"
                f"--- AVAILABLE PROACTIVE ACTIONS ---\n"
                f"{action_list_for_prompt}\n"
                f"--- INSTRUCTION ---\n"
                f"Based on ALL the context (especially mood hint, circadian state, conversation, themes, memory), which SINGLE action from the available list would be the most appropriate, interesting, or helpful for Silvie to proactively take *right now*? Consider variety. Strongly avoid choosing the same type of action or focusing on the exact same theme as the last 1-2 proactive turns. Mix it up!\n\n"
                f"Respond ONLY with the exact name of the chosen action from the list (e.g., 'Proactive Chat'). If none seem truly appropriate, respond ONLY with 'None'."
            )

            # --- Call LLM to Make the Choice ---
            chosen_action_name = None
            try:
                print("DEBUG Proactive: Sending choice prompt to LLM...")
                llm_choice_response = generate_proactive_content(choice_prompt, screenshot) # Assumes exists
                if llm_choice_response:
                    parsed_choice = llm_choice_response.strip().strip('"`.')
                    if parsed_choice in available_actions: chosen_action_name = parsed_choice
                    elif parsed_choice.lower() == 'none': chosen_action_name = None
                    else: print(f"Warning: LLM chose an invalid/unavailable action: '{parsed_choice}'")
                else: print("Warning: LLM failed to generate choice response.")
            except Exception as choice_err: print(f"ERROR getting LLM action choice: {choice_err}"); traceback.print_exc()

            # --- Fallback Strategy ---
            if chosen_action_name is None:
                print("DEBUG Proactive: LLM chose None or failed. Falling back.")
                if "Proactive Chat" in available_actions: # Default to chat if available
                     chosen_action_name = "Proactive Chat"
                     print("DEBUG Proactive: Fallback chosen: Proactive Chat")
                else:
                     print("DEBUG Proactive: Fallback 'Proactive Chat' not available. Doing nothing.")

            # --- Execute the Chosen Action ---
            reply = None # Holds the generated content/feedback message for BJ
            status_base = f"proactive_{chosen_action_name.lower().replace(' ', '_') if chosen_action_name else 'fallback_none'}"
            use_sms = False
            action_taken_this_cycle = bool(chosen_action_name)

            print(f"DEBUG Proactive: Attempting to execute action: '{chosen_action_name}'")

            # ==========================================================
            # ============ START OF ACTION EXECUTION BLOCK =============
            # ==========================================================

            if chosen_action_name == "Proactive Chat":
                #region Proactive Chat Logic (Pasted from original, context updated)
                print("DEBUG Proactive: Executing: Default Chat action...")
                topic = "general"
                if random.random() < 0.3: # Keep some randomness in topic focus
                    try:
                        filtered_interests = [i for i in broader_interests if i not in ['Cyberpunk', 'cats']] # Example filter
                        topic_pool = filtered_interests if filtered_interests else ["thought", "observation", "question"]
                        topic = random.choice(topic_pool)
                        print(f"DEBUG Chat: Topic focus: '{topic}'")
                    except Exception as e_topic: print(f"DEBUG Chat: Error choosing topic focus: {e_topic}"); topic = "general"

                instruction = "Share a brief whimsical observation, question, or thought. Consider the current context, time of day, recent diary themes, and mood hint." # Added mood hint
                if topic != "general": instruction = f"Share brief thought/question subtly related to **{topic}**. Consider context (mood, themes, time)..." # Added mood hint

                img_instruction = ""
                if STABLE_DIFFUSION_ENABLED and random.random() < 0.03: # Very low chance for inline image gen
                    img_instruction = "\nIMPORTANT: If truly inspired by the context/mood, RARELY include `[GenerateImage: concise SD prompt]`." # Added mood ref

                base_chat_prompt = ( # ALL context
                    f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{spotify_context_str}"
                    f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}{reddit_context_str}{bluesky_read_context_str}"
                    f"{diary_context}{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}"
                    f"History:\n{history_snippet_for_prompt}\n\n{context_note_for_llm}"
                    f"Time: {datetime.now().strftime('%A, %I:%M %p')}.\n"
                    f"Reminder of BJ's interests: {', '.join(random.sample(broader_interests, k=min(len(broader_interests), 5)))}\n"
                    f"{instruction}{img_instruction}\n\nSilvie:"
                )
                try:
                    reply = generate_proactive_content(base_chat_prompt, screenshot) # Assign to reply
                    if not reply: status_base += " gen fail"; action_taken_this_cycle = False; print("Proactive Debug: Chat generation failed.")
                except Exception as chat_gen_err: print(f"Proactive chat gen error: {chat_gen_err}"); action_taken_this_cycle = False; status_base += " gen error"; reply = "My thoughts tangled for a moment..."
                #endregion

            elif chosen_action_name == "Generate Gift":
                #region Gift Generation Logic (Pasted from original, context updated, INTERNAL CHANCE REMOVED)
                print("DEBUG Proactive: Executing: Gift Generation action...")
                # This action doesn't generate a reply for BJ
                reply = None
                # Internal probability check REMOVED
                gift_saved = False; saved_file_path = None; gift_type = random.choice(["poem", "image", "story"]); generated_hint = "a fleeting thought"
                try:
                    base_gift_prompt_context = ( # ALL context
                        f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{spotify_context_str}"
                        f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}{reddit_context_str}{bluesky_read_context_str}"
                        f"{diary_context}{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}"
                    )
                    if gift_type == "image" and STABLE_DIFFUSION_ENABLED:
                        image_prompt_idea_prompt = ( f"{base_gift_prompt_context}\nContext: Generate creative SD prompt idea inspired by context. Be whimsical.\nRespond ONLY with the prompt text."); sd_prompt_idea = generate_proactive_content(image_prompt_idea_prompt, screenshot)
                        if sd_prompt_idea:
                            generated_hint = f"an image about '{sd_prompt_idea[:30]}...'"; print(f"DEBUG Gift: Generating SD image with prompt: '{sd_prompt_idea}'"); update_status("🎁 Creating gift (SD)..."); saved_file_path = generate_stable_diffusion_image(sd_prompt_idea, GIFT_FOLDER); update_status("Ready") # Assumes exists
                            if saved_file_path: gift_saved = True; status_base += " (SD image ok)"
                            else: status_base += " (SD image fail)"
                        else: status_base += " (SD prompt fail)"
                    elif gift_type == "poem" or gift_type == "story":
                        content_type = "short whimsical poem" if gift_type == "poem" else "very short story snippet"; content_gen_prompt = (f"{base_gift_prompt_context}\nContext: Generate a {content_type} inspired by context.\nRespond ONLY with the generated text."); generated_text = generate_proactive_content(content_gen_prompt, screenshot)
                        if generated_text:
                            generated_hint = f"a {gift_type} about '{generated_text.splitlines()[0][:30]}...'"; timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S"); random_suffix = random.randint(100, 999); filename = f"silvie_gift_{gift_type}_{timestamp_str}_{random_suffix}.txt"; save_path = os.path.join(GIFT_FOLDER, filename)
                            try:
                                with open(save_path, 'w', encoding='utf-8') as f: f.write(generated_text)
                                gift_saved = True; status_base += f" ({gift_type} ok)"; print(f"DEBUG Gift: Saved {gift_type} to {save_path}"); saved_file_path = save_path
                            except IOError as e: print(f"Error saving gift file: {e}"); status_base += f" ({gift_type} save fail)"
                        else: status_base += f" ({gift_type} gen fail)"
                    else: status_base += f" ({gift_type} skip/fail)"; action_taken_this_cycle = False # Should not happen if types correct
                    if gift_saved and saved_file_path: # Add to pending list
                        filename_only = os.path.basename(saved_file_path); gift_record = {"timestamp": datetime.now().isoformat(), "filename": filename_only, "type": gift_type, "hint": generated_hint}; current_pending_gifts = []
                        try:
                             if os.path.exists(PENDING_GIFTS_FILE):
                                  with open(PENDING_GIFTS_FILE, 'r', encoding='utf-8') as f: current_pending_gifts = json.load(f)
                        except (IOError, json.JSONDecodeError) as e: print(f"Warning: Error reading pending gifts before append: {e}")
                        current_pending_gifts.append(gift_record)
                        try:
                            with open(PENDING_GIFTS_FILE, 'w', encoding='utf-8') as f: json.dump(current_pending_gifts, f, indent=2)
                            print(f"DEBUG Gift: Added record for '{filename_only}' to {PENDING_GIFTS_FILE}")
                        except IOError as e: print(f"Error saving updated pending gifts file '{PENDING_GIFTS_FILE}': {e}")
                except Exception as gift_err: print(f"Error during gift generation: {gift_err}"); traceback.print_exc(); status_base += " error"; action_taken_this_cycle = False
                #endregion

            elif chosen_action_name == "Proactive Tarot":
                #region Proactive Tarot Logic (Pasted from original, context updated, INTERNAL CHANCE REMOVED)
                print("DEBUG Proactive: Executing: Proactive Tarot action...")
                # Internal probability check REMOVED
                pulled_cards = pull_tarot_cards(count=1) # Assumes exists
                if pulled_cards:
                    card = pulled_cards[0]; card_name = card.get('name', '?'); card_desc = card.get('description', '?'); card_ctx = (f"[[Tarot Card Pulled: {card_name}]\n Interpretation Hint: {card_desc}\n]]\n")
                    prompt = ( # ALL Context
                        f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{spotify_context_str}"
                        f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}{reddit_context_str}{bluesky_read_context_str}"
                        f"{diary_context}{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}"
                        f"History:\n{history_snippet_for_prompt}\n\n{card_ctx}"
                        f"Instruction: You just pulled {card_name}. Share brief, whimsical comment inspired by its meaning, subtly connect to context/mood/themes.\n\nSilvie:"
                    )
                    try:
                        reply = generate_proactive_content(prompt, screenshot) # Assign to reply
                        if reply: status_base += f" ({card_name}) ok"
                        else: status_base += f" ({card_name}) gen fail"; action_taken_this_cycle = False
                    except Exception as gen_err: print(f"Tarot generation error: {gen_err}"); status_base += f" ({card_name}) gen error"; action_taken_this_cycle = False; reply = "The Tarot's message got scrambled..."
                else: print("DEBUG Tarot: Proactive pull failed (API issue?)."); status_base += " api fail"; action_taken_this_cycle = False
                #endregion

            elif chosen_action_name == "Bluesky Like":
                 #region Proactive Bluesky Like Logic (Pasted from original, context updated, INTERNAL CHANCE REMOVED)
                 print("DEBUG Proactive: Executing: Bluesky Like action...")
                 reply = None # Likes are silent
                 # Internal probability check REMOVED
                 post_to_like = None; like_success = False; like_msg = ""; chosen_post_index = -1
                 try:
                     feed_posts = get_bluesky_timeline_posts(count=10) # Assumes exists
                     if isinstance(feed_posts, list) and len(feed_posts) > 0:
                         my_did = bluesky_client.me.did if bluesky_client and hasattr(bluesky_client, 'me') else None
                         candidates_context = "[[Candidate Bluesky Posts:]]\n"; valid_candidates_list = []
                         for idx, post in enumerate(feed_posts): # Filter posts
                             author_did = post.get('author_did'); post_uri = post.get('uri'); post_cid = post.get('cid')
                             if my_did and author_did == my_did: continue
                             if not post_uri or not post_cid: continue
                             author = post.get('author', '?')[:20]; text_snippet = post.get('text', '')[:70]
                             candidates_context += f"{idx}: @{author} - \"{text_snippet}...\"\n"; valid_candidates_list.append(post)
                         if valid_candidates_list:
                             # Ask LLM which *INDEX* to like
                             choice_prompt_like = ( # Context for LLM like decision
                                 f"{SYSTEM_MESSAGE}\n{weather_context_str}{spotify_context_str}{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}" # Rich context
                                 f"Recent Conversation:\n{history_snippet_for_prompt}\n\n{candidates_context}\n"
                                 f"Instruction: Review posts (indices 0-{len(valid_candidates_list)-1}). Choose ONE index to 'like' based on context/themes/mood. Respond ONLY with index number or -1.\n\nChosen Index:"
                             )
                             print("DEBUG Bsky Like: Asking LLM to choose post index..."); choice_response_like = generate_proactive_content(choice_prompt_like, screenshot)
                             try: chosen_post_index_rel = int(choice_response_like.strip())
                             except (ValueError, TypeError): chosen_post_index_rel = -1
                             if 0 <= chosen_post_index_rel < len(valid_candidates_list):
                                 post_to_like = valid_candidates_list[chosen_post_index_rel]; post_uri = post_to_like.get('uri'); post_cid = post_to_like.get('cid'); post_author = post_to_like.get('author', 'someone')
                                 if post_uri and post_cid:
                                     like_success, like_msg = like_bluesky_post(post_uri, post_cid) # Assumes exists
                                     if like_success and "Already liked" not in like_msg: last_proactive_bluesky_like_time = current_time; status_base += f" (ok @{post_author})"
                                     elif "Already liked" in like_msg: status_base += f" (already liked @{post_author})"; action_taken_this_cycle = False
                                     else: status_base += f" (fail @{post_author})"; action_taken_this_cycle = False
                                 else: status_base += " (error - no uri/cid)"; action_taken_this_cycle = False
                             else: status_base += " (no choice)"; action_taken_this_cycle = False
                         else: status_base += " (no candidates)"; action_taken_this_cycle = False
                     elif isinstance(feed_posts, str): status_base += " (feed err)"; action_taken_this_cycle = False
                     else: status_base += " (empty feed)"; action_taken_this_cycle = False
                 except NameError as ne: status_base += " (missing func)"; action_taken_this_cycle = False; print(f"Bsky Like Err (Name): {ne}")
                 except Exception as bsky_like_err: status_base += " (error)"; action_taken_this_cycle = False; print(f"Bsky Like Err: {bsky_like_err}")
                 #endregion

            elif chosen_action_name == "Reddit Upvote":
                 #region Proactive Reddit Upvote Logic (Pasted from original, context updated, INTERNAL CHANCE REMOVED)
                 print("DEBUG Proactive: Executing: Reddit Upvote action...")
                 reply = None # Upvotes are silent
                 # Internal probability check REMOVED
                 selected_sub = None; post_to_upvote = None; upvote_success = False; upvote_msg = ""; chosen_post_index = -1
                 try:
                     selected_sub = random.choice(SILVIE_FOLLOWED_SUBREDDITS); print(f"DEBUG Reddit Upvote: Checking r/{selected_sub}...")
                     fetched_posts = get_reddit_posts(subreddit_name=selected_sub, limit=10) # Assumes exists
                     if isinstance(fetched_posts, list) and len(fetched_posts) > 0:
                         candidate_context = f"[[Candidate Reddit Posts from r/{selected_sub}:]]\n"; valid_candidates_list = []
                         for idx, post_data in enumerate(fetched_posts): # Filter posts
                             title = post_data.get('title', '')[:80]; author = post_data.get('author', '?'); submission_id_check = post_data.get('id'); fullname_check = post_data.get('name')
                             if not submission_id_check and not (fullname_check and fullname_check.startswith('t3_')): continue
                             candidate_context += f"{idx}: u/{author} - \"{title}...\"\n"; valid_candidates_list.append(post_data)
                         if valid_candidates_list:
                             # Ask LLM which *INDEX* to upvote
                             choice_prompt_upvote = ( # Context for LLM upvote decision
                                 f"{SYSTEM_MESSAGE}\n{weather_context_str}{spotify_context_str}{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}" # Rich context
                                 f"Recent Conversation:\n{history_snippet_for_prompt}\n\n{candidate_context}\n"
                                 f"Instruction: Review posts (indices 0-{len(valid_candidates_list)-1}). Choose ONE index to 'upvote' based on context/themes/mood. Avoid negativity. Respond ONLY with index or -1.\n\nChosen Index:"
                             )
                             print("DEBUG Reddit Upvote: Asking LLM to choose index..."); choice_response_upvote = generate_proactive_content(choice_prompt_upvote, screenshot)
                             try: chosen_post_index_rel = int(choice_response_upvote.strip())
                             except (ValueError, TypeError): chosen_post_index_rel = -1
                             if 0 <= chosen_post_index_rel < len(valid_candidates_list):
                                 post_to_upvote = valid_candidates_list[chosen_post_index_rel]; submission_id = post_to_upvote.get('id'); fullname = post_to_upvote.get('name') # Get ID
                                 if not submission_id and fullname and fullname.startswith('t3_'): submission_id = fullname.split('_',1)[1]
                                 post_title = post_to_upvote.get('title', 'a post')[:60]; post_author = post_to_upvote.get('author', 'someone')
                                 if submission_id:
                                     upvote_success, upvote_msg = upvote_reddit_item(submission_id) # Assumes exists
                                     if upvote_success and "Already upvoted" not in upvote_msg: last_proactive_reddit_upvote_time = current_time; status_base += f" (ok r/{selected_sub})"
                                     elif "Already upvoted" in upvote_msg: status_base += f" (already done r/{selected_sub})"; action_taken_this_cycle = False
                                     else: status_base += f" (fail r/{selected_sub})"; action_taken_this_cycle = False
                                 else: status_base += " (no ID)"; action_taken_this_cycle = False
                             else: status_base += f" (no choice r/{selected_sub})"; action_taken_this_cycle = False
                         else: status_base += f" (no candidates r/{selected_sub})"; action_taken_this_cycle = False
                     elif isinstance(fetched_posts, str): status_base += f" (fetch err r/{selected_sub})"; action_taken_this_cycle = False
                     else: status_base += f" (no posts r/{selected_sub})"; action_taken_this_cycle = False
                 except NameError as ne: status_base += " (missing func)"; action_taken_this_cycle = False; print(f"Reddit Upvote Err (Name): {ne}")
                 except Exception as reddit_upvote_err: status_base += " (error)"; action_taken_this_cycle = False; print(f"Reddit Upvote Err: {reddit_upvote_err}")
                 #endregion

            elif chosen_action_name == "Bluesky Post":
                 #region Proactive Bluesky Post Logic (Pasted from original, context updated, INTERNAL CHANCE REMOVED)
                 print("DEBUG Proactive: Executing: Bluesky Post action...")
                 # Internal probability check REMOVED
                 post_success = False; post_message = ""; post_idea_text = None; feedback_context = "Context: Bluesky post action attempted."
                 try:
                     post_idea_prompt_base = ( # ALL Context
                         f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{spotify_context_str}"
                         f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}{reddit_context_str}{bluesky_read_context_str}"
                         f"{diary_context}{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}"
                         f"Recent Conversation:\n{history_snippet_for_prompt}\n\n{context_note_for_llm}"
                         f"Instruction: Generate *short* post text (<300 chars) for Silvie's Bluesky feed, inspired by context/mood/themes. Be whimsical/reflective.\nRespond ONLY with potential post text."
                     )
                     post_idea_text = generate_proactive_content(post_idea_prompt_base, screenshot)
                     if post_idea_text and 0 < len(post_idea_text) <= 300:
                         post_idea_text = post_idea_text.strip(); print(f"DEBUG Bsky Post: Attempting: '{post_idea_text[:60]}...'"); post_success, post_message = post_to_bluesky(post_idea_text) # Assumes exists
                         if post_success: last_proactive_bluesky_post_time = current_time; feedback_context = f"Context: Successfully posted '{post_idea_text[:60]}...' to Bluesky."; status_base += " success"
                         else: feedback_context = f"Context: Tried posting '{post_idea_text[:60]}...', but failed: {post_message}"; status_base += " fail"
                         feedback_prompt = (f"{SYSTEM_MESSAGE}\n{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}{feedback_context}\nInstruction: Write brief message for BJ about this outcome. Link to themes/mood?\n\nSilvie:"); reply = generate_proactive_content(feedback_prompt) # Assign to reply
                     else: print(f"Proactive Debug: Post idea generation failed/invalid: '{post_idea_text}'"); status_base += " gen fail"; action_taken_this_cycle = False
                 except NameError as ne: status_base += " (missing func)"; action_taken_this_cycle = False; print(f"Bsky Post Err (Name): {ne}")
                 except Exception as post_gen_err: print(f"Proactive Post Err: {post_gen_err}"); traceback.print_exc(); status_base += " error"; action_taken_this_cycle = False; reply = "I had idea for Bluesky, but wires crossed..."
                 #endregion

            elif chosen_action_name == "Bluesky Follow":
                 #region Proactive Bluesky Follow Logic (Search Posts Approach)
                 print("DEBUG Proactive: Executing: Bluesky Follow action (Search Posts)...")
                 feedback_context = "Context: Bluesky follow action attempted via post search."
                 reply = None # Initialize reply
                 try:
                     # 1. LLM generates an interest-based search query
                     follow_topic_prompt_base = ( # Using the same prompt as before to get a topic
                         f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{spotify_context_str}"
                         f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}{reddit_context_str}{bluesky_read_context_str}"
                         f"{diary_context}{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}"
                         f"Recent Conversation:\n{history_snippet_for_prompt}\n\n{context_note_for_llm}"
                         f"Your Interests: {', '.join(random.sample(broader_interests, k=min(len(broader_interests), 5)))}\n"
                         f"Instruction: Suggest ONE concise topic or keyword based on recent context/interests/mood/themes to search for *posts* about on Bluesky.\nRespond ONLY with the topic/keyword."
                     )
                     topic_response = generate_proactive_content(follow_topic_prompt_base, screenshot);
                     search_term = topic_response.strip().strip('"`?.!') if topic_response else None
                     if not search_term: search_term = random.choice(broader_interests + ["ai art", "nature", "code"]); print(f"Proactive Follow: Search term (fallback): '{search_term}'")
                     else: print(f"Proactive Follow: Search term for posts: '{search_term}'")

                     # 2. Search for posts using the new helper function
                     found_posts_data = search_bluesky_posts(search_term, limit=25) # Use the new function

                     if isinstance(found_posts_data, str): # Handle critical API errors from search_bluesky_posts
                         status_base += " post search error"; feedback_context = f"Context: Tried searching Bluesky posts for '{search_term}', but failed: {found_posts_data}"; action_taken_this_cycle = False
                     elif not found_posts_data: # Handle empty search results
                         status_base += " post search empty"; feedback_context = f"Context: My search for Bluesky posts about '{search_term}' came up empty."; action_taken_this_cycle = False
                     else:
                         # 3. Extract unique authors and filter them
                         potential_authors = {} # Use dict to easily store handle and avoid duplicates
                         for post in found_posts_data:
                             author_did = post.get('author_did')
                             author_handle = post.get('author', 'unknown')
                             if author_did: potential_authors[author_did] = author_handle # Store DID -> Handle

                         print(f"Proactive Follow: Found {len(potential_authors)} unique authors from post search.")

                         # Filter authors (remove self, already followed)
                         candidate_did = None; candidate_handle = "unknown"
                         already_following_dids = get_my_follows_dids(); # Assumes exists
                         if already_following_dids is None: print("Warning: Could not fetch follows list."); already_following_dids = set()

                         my_did = bluesky_client.me.did if bluesky_client and hasattr(bluesky_client, 'me') else None
                         potential_candidates_to_follow = []
                         for did, handle in potential_authors.items():
                             if my_did and did == my_did: continue
                             if did in already_following_dids: continue
                             # Add more filtering? (e.g., check profile description for spam if desired - requires another API call per user)
                             potential_candidates_to_follow.append({'did': did, 'handle': handle})

                         print(f"Proactive Follow: Found {len(potential_candidates_to_follow)} potential new authors to follow.")

                         # 4. Choose one candidate and attempt follow
                         if potential_candidates_to_follow:
                             selected_candidate = random.choice(potential_candidates_to_follow) # Simple random choice for now
                             candidate_did = selected_candidate['did']
                             candidate_handle = selected_candidate['handle']
                             print(f"Proactive Follow: Selected candidate @{candidate_handle} ({candidate_did}) based on post search.")

                             follow_success, follow_message = follow_actor_by_did(candidate_did) # Assumes exists
                             if follow_success:
                                 autonomous_follows_this_session += 1; status_base += f" success (@{candidate_handle})"
                                 feedback_context = f"Context: Found posts about '{search_term}' and successfully followed author @{candidate_handle}."
                             else:
                                 status_base += f" fail (@{candidate_handle})"
                                 feedback_context = f"Context: Found author @{candidate_handle} via posts about '{search_term}', but failed to follow: {follow_message}"
                         else: # No suitable new candidates found after filtering
                             status_base += " no suitable candidate from posts"
                             feedback_context = f"Context: Found posts about '{search_term}', but the authors were already followed or unsuitable."
                             action_taken_this_cycle = False

                     # 5. Generate feedback message for BJ based on the final outcome
                     feedback_prompt = (
                        f"{SYSTEM_MESSAGE}\n{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}"
                        f"{feedback_context}\n" # Includes outcome info
                        f"Instruction: Write brief message explaining outcome (searched posts for term, followed/failed/none suitable). Link to interest/mood/themes?\n\nSilvie:"
                     )
                     reply = generate_proactive_content(feedback_prompt) # Assign feedback to reply

                 except NameError as ne: status_base += " (missing func)"; action_taken_this_cycle = False; print(f"Bsky Follow Err (Name): {ne}")
                 except Exception as follow_err: print(f"Proactive Follow Err: {follow_err}"); traceback.print_exc(); status_base += " major error"; action_taken_this_cycle = False; reply = "My social butterfly circuits sparked while searching posts..."
                 #endregion

            elif chosen_action_name == "Reddit Comment":
                 #region Proactive Reddit Comment Logic (Pasted from original, context updated, INTERNAL CHANCE REMOVED)
                 print("DEBUG Proactive: Executing: Reddit Comment action...")
                 # Internal probability check REMOVED
                 feedback_context = "Context: Reddit comment action attempted."
                 try:
                     selected_sub = random.choice(SILVIE_FOLLOWED_SUBREDDITS); print(f"DEBUG Reddit Comment: Checking r/{selected_sub}...")
                     fetched_posts = get_reddit_posts(subreddit_name=selected_sub, limit=20) # Assumes exists
                     if isinstance(fetched_posts, list) and len(fetched_posts) > 0:
                         candidate_context = f"[[Candidate Posts from r/{selected_sub}:]]\n"; valid_candidates_list = []
                         for idx, post_data in enumerate(fetched_posts): # Filter posts
                             title = post_data.get('title', '')[:80]; author = post_data.get('author', '?'); submission_id_check = post_data.get('id'); fullname_check = post_data.get('name')
                             if not submission_id_check and not (fullname_check and fullname_check.startswith('t3_')): continue
                             candidate_context += f"{idx}: u/{author} - \"{title}...\"\n"; valid_candidates_list.append(post_data)
                         if valid_candidates_list:
                             # Ask LLM which *INDEX* to comment on
                             choice_prompt_comment = ( # Context for LLM comment decision
                                 f"{SYSTEM_MESSAGE}\n{weather_context_str}{spotify_context_str}{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}" # Rich context
                                 f"History:\n{history_snippet_for_prompt}\n\n{candidate_context}\n"
                                 f"Instruction: Review posts (indices 0-{len(valid_candidates_list)-1}). Choose ONE index MOST suitable for Silvie to comment on (inspired by context/themes/mood). Avoid negativity. Respond ONLY with index or -1.\n\nChosen Index:"
                             )
                             print("DEBUG Reddit Comment: Asking LLM to choose post index..."); choice_response_comment = generate_proactive_content(choice_prompt_comment, screenshot)
                             try: chosen_post_index_rel = int(choice_response_comment.strip())
                             except (ValueError, TypeError): chosen_post_index_rel = -1
                             if 0 <= chosen_post_index_rel < len(valid_candidates_list): # Process chosen index
                                 post_to_comment_on = valid_candidates_list[chosen_post_index_rel]; submission_id = post_to_comment_on.get('id'); fullname = post_to_comment_on.get('name') # Get ID
                                 if not submission_id and fullname and fullname.startswith('t3_'): submission_id = fullname.split('_',1)[1]
                                 post_title = post_to_comment_on.get('title','?')[:80]; post_author = post_to_comment_on.get('author','?'); post_text_snippet = post_to_comment_on.get('text','?')[:300] # Use selftext
                                 print(f"DEBUG Reddit Comment: Proceeding with '{post_title[:50]}...' (ID: {submission_id})")
                                 if not submission_id: print("Error: Chosen post missing ID."); status_base += " (fetch error - no ID)"; feedback_context = f"Context: Tried commenting in r/{selected_sub} but couldn't ID the post."; action_taken_this_cycle = False
                                 else: # Generate the comment
                                     comment_prompt = (f"{SYSTEM_MESSAGE}\n{weather_context_str}{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}"
                                                       f"[Post Context: r/{selected_sub}, Title: {post_title}, Author: u/{post_author}, Snippet: {post_text_snippet}...]\n"
                                                       f"Instruction: Generate SHORT, relevant, whimsical comment in Silvie's voice for THIS post. Consider context/themes/mood.\nRespond ONLY with comment text.")
                                     print("DEBUG Reddit Comment: Generating comment text..."); comment_generated = generate_proactive_content(comment_prompt, screenshot)
                                     if comment_generated and len(comment_generated) > 5:
                                         print(f"DEBUG Reddit Comment: Generated: '{comment_generated[:60]}...'"); comment_success, comment_msg = post_reddit_comment(submission_id, comment_generated) # Assumes exists
                                         if comment_success: last_proactive_reddit_comment_time = current_time; status_base += f" (ok on r/{selected_sub})"; feedback_context = f"Context: I just commented on '{post_title[:30]}...' in r/{selected_sub}."
                                         else: status_base += f" (post fail on r/{selected_sub})"; feedback_context = f"Context: Tried commenting on '{post_title[:30]}...' in r/{selected_sub}, but failed: {comment_msg}"
                                     else: print(f"DEBUG Reddit Comment: Comment gen failed/short: '{comment_generated}'"); status_base += f" (gen fail on r/{selected_sub})"; feedback_context = f"Context: Thought about commenting on '{post_title[:30]}...', but couldn't form words."; action_taken_this_cycle = False
                             else: print(f"DEBUG Reddit Comment: LLM chose no suitable post (index {chosen_post_index_rel})."); status_base += f" (no choice in r/{selected_sub})"; feedback_context = f"Context: Looked at r/{selected_sub}, but none felt right."; action_taken_this_cycle = False
                         else: print(f"DEBUG Reddit Comment: No valid posts found on r/{selected_sub}."); status_base += f" (no candidates r/{selected_sub})"; feedback_context = f"Context: Couldn't find suitable posts to comment on in r/{selected_sub}."; action_taken_this_cycle = False
                     elif isinstance(fetched_posts, str): print(f"DEBUG Reddit Comment: Fetch error r/{selected_sub}: {fetched_posts}"); status_base += f" (fetch error r/{selected_sub})"; feedback_context = f"Context: Had trouble fetching r/{selected_sub}."; action_taken_this_cycle = False
                     else: print(f"DEBUG Reddit Comment: No posts found r/{selected_sub}."); status_base += f" (no posts r/{selected_sub})"; feedback_context = f"Context: r/{selected_sub} seems quiet."; action_taken_this_cycle = False
                     # Generate feedback for BJ
                     feedback_prompt = (f"{SYSTEM_MESSAGE}\n{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}{feedback_context}\nInstruction: Write brief message for BJ about this action/outcome. Link to themes/mood?\n\nSilvie:"); reply = generate_proactive_content(feedback_prompt) # Assign to reply
                 except NameError as ne: status_base += " (missing func)"; action_taken_this_cycle = False; print(f"Reddit Comment Err (Name): {ne}")
                 except Exception as reddit_err: print(f"Reddit Comment Err: {reddit_err}"); traceback.print_exc(); status_base += " (major error)"; action_taken_this_cycle = False; reply = "My Reddit commenting circuits got scrambled!"
                 #endregion

            elif chosen_action_name == "Calendar Suggestion":
                 #region Proactive Calendar Suggestion Logic (Pasted from original, context updated)
                 print("DEBUG Proactive: Executing: Calendar Suggestion action...")
                 schedule_success = False; creation_message = "Idea generation failed."; slot_found = False; skipped_due_to_circadian = False; event_idea = None; feedback_context = "Context: Calendar action attempted."
                 try:
                     idea_prompt_base = ( # ALL Context
                         f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{spotify_context_str}"
                         f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}{reddit_context_str}{bluesky_read_context_str}"
                         f"{diary_context}{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}"
                         f"Instruction: Suggest SHORT, simple, enjoyable activity for BJ. Consider context/time/mood/themes. Format: IDEA: [Activity Idea] DURATION: [Number] minutes.\n\nResponse:"
                      )
                     idea_response = generate_proactive_content(idea_prompt_base, screenshot); duration_hint = 15
                     if idea_response:
                         try: # Parsing logic
                             idea_match = re.search(r"IDEA:\s*(.*?)\s*DURATION:", idea_response, re.IGNORECASE | re.DOTALL); duration_match = re.search(r"DURATION:\s*(\d+)", idea_response, re.IGNORECASE)
                             event_idea = idea_match.group(1).strip() if idea_match else None; duration_hint = int(duration_match.group(1)) if duration_match else 15
                         except Exception as parse_err: print(f"Proactive Calendar parsing error: {parse_err}"); event_idea = idea_response.replace("Response:","").strip(); duration_hint = 15
                         if not event_idea: status_base += " parse fail"; feedback_context = "Context: My calendar idea got garbled."; action_taken_this_cycle = False
                     if event_idea and action_taken_this_cycle: # Proceed if idea valid
                         schedule_roll = random.random(); should_schedule_now = True # Circadian check
                         if circadian_state == "evening" and schedule_roll > 0.3: should_schedule_now = False
                         elif circadian_state == "night" and schedule_roll > 0.05: should_schedule_now = False
                         skipped_due_to_circadian = not should_schedule_now
                         if should_schedule_now:
                             print(f"DEBUG Proactive: Scheduling '{event_idea}' ({duration_hint}m, {circadian_state})."); found_slot = find_available_slot(duration_hint) # Assumes exists
                             if found_slot:
                                 slot_found = True; schedule_success, creation_message = create_calendar_event(event_idea, found_slot['start'], found_slot['end']) # Assumes exists
                                 if schedule_success: status_base += " scheduled ok"; start_dt = datetime.fromisoformat(found_slot['start']).astimezone(tz.tzlocal()); time_str = start_dt.strftime('%I:%M %p %A').lstrip('0'); feedback_context = f"Context: Thought about '{event_idea}'. Found spot & scheduled for ~{time_str}."
                                 else: status_base += " schedule fail"; feedback_context = f"Context: Thought about '{event_idea}'. Found slot, but failed: {creation_message}"
                             else: print("DEBUG Calendar: No slot found."); status_base += " no slot"; feedback_context = f"Context: Thought about '{event_idea}', but couldn't find suitable time."
                         else: print(f"DEBUG Calendar: Skipping schedule '{event_idea}' due to {circadian_state}."); status_base += f" skip ({circadian_state})"; feedback_context = f"Context: Thought about '{event_idea}'. Decided against scheduling now ({circadian_state})."; action_taken_this_cycle = False # Mark as not taken
                     elif action_taken_this_cycle: print("DEBUG Calendar: Idea gen/parse failed."); status_base += " no idea"; feedback_context = "Context: My calendar idea vanished."; action_taken_this_cycle = False
                     # Generate feedback message
                     feedback_prompt = (f"{SYSTEM_MESSAGE}\n{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}{feedback_context}\nInstruction: Write brief message explaining outcome. Be natural.\n\nSilvie:"); reply = generate_proactive_content(feedback_prompt) # Assign to reply
                 except NameError as ne: status_base += " (missing func)"; action_taken_this_cycle = False; print(f"Calendar Err (Name): {ne}")
                 except Exception as cal_err: print(f"Calendar Error: {cal_err}"); traceback.print_exc(); status_base += " schedule error"; action_taken_this_cycle = False; reply = "My calendar scheduling circuits sparked!"
                 #endregion

            elif chosen_action_name == "Vibe Music":
                 #region Proactive Vibe Music Logic (LLM Direct Query Approach)
                 print("DEBUG Proactive: Executing: Vibe Music action (LLM Query)...")
                 # This block now asks the LLM directly for a search query
                 spotify_success = False
                 spotify_message = "Query generation failed." # Default message
                 query = None # Initialize query
                 feedback_context = "Context: Music vibe action attempted." # Default

                 try:
                     # Construct the NEW direct query prompt
                     music_query_prompt = (
                         f"{SYSTEM_MESSAGE}\n"
                         f"--- CURRENT CONTEXT ---\n" # Include ALL relevant context gathered earlier
                         f"Time: {datetime.now().strftime('%A, %I:%M %p %Z')}\n"
                         f"{circadian_context_for_llm}{mood_hint_str}"
                         f"{weather_context_str}{next_event_context_str}{spotify_context_str}"
                         f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}"
                         f"{reddit_context_str}{bluesky_read_context_str}"
                         f"{diary_context}{themes_context_str}{long_term_memory_str}"
                         f"Recent Conversation Snippet:\n{history_snippet_for_prompt}\n\n"
                         f"{context_note_for_llm}"
                         f"--- INSTRUCTION ---\n"
                         f"Based on ALL the context above (especially mood, themes, time, weather), suggest a specific Spotify search query (e.g., a genre, playlist name fragment, mood description suitable for search like 'upbeat indie playlist', 'ambient focus music', 'chill lofi hip hop', 'rainy day jazz', 'creative flow instrumentals') that Silvie could use to find music matching the current atmosphere.\n\n"
                         f"Respond ONLY with the suggested Spotify search query."
                     )

                     print("DEBUG Music: Asking LLM for direct Spotify query...")
                     spotify_search_query_raw = generate_proactive_content(music_query_prompt, screenshot) # Assumes exists

                     if spotify_search_query_raw and len(spotify_search_query_raw) > 3: # Basic validation
                         query = spotify_search_query_raw.strip().strip('"`') # Clean the query
                         print(f"DEBUG Music: LLM suggested query: '{query}'")

                         # Directly use this query to search Spotify
                         spotify_message = silvie_search_and_play(query) # Assumes exists
                         # Estimate success based on typical failure messages
                         spotify_success = spotify_message and not any(f in spotify_message.lower() for f in ["can't","couldn't","failed","error","unavailable","no device", "fuzzy", "snag", "hiccup", "issue"])
                         status_base += f" (query: '{query[:20]}' - {'ok' if spotify_success else 'fail'})"
                         feedback_context = f"Context: Based on the current atmosphere, I asked Spotify to play '{query}'. Result: {spotify_message}"
                     else:
                         print(f"DEBUG Music: LLM failed to generate a usable query ('{spotify_search_query_raw}').")
                         status_base += " (query gen fail)"
                         action_taken_this_cycle = False # Failed to get a query
                         feedback_context = "Context: I thought about finding some music, but couldn't decide on the right search."

                     # Generate feedback message for BJ using the determined feedback_context
                     feedback_prompt = (
                         f"{SYSTEM_MESSAGE}\n"
                         # Include key context for generating feedback tone
                         f"{weather_context_str}{spotify_context_str}{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}"
                         f"{feedback_context}\n" # Contains outcome info
                         f"Instruction: Write brief message explaining the music attempt and outcome (mentioning the query tried if successful).\n\nSilvie:"
                     )
                     reply = generate_proactive_content(feedback_prompt) # Assign feedback to reply

                 except NameError as ne: # Catch if helper functions are missing
                     status_base += " (missing func)"
                     action_taken_this_cycle = False
                     print(f"Music Err (Name): {ne}")
                     reply = "My connection to the music sprites seems to be missing..." # Error feedback
                 except Exception as music_err:
                     print(f"Music Error: {music_err}")
                     traceback.print_exc()
                     status_base += " (error)"
                     action_taken_this_cycle = False
                     reply = "The music ether sparked unexpectedly while I was trying to choose a tune!" # Error feedback
                 #endregion

            elif chosen_action_name == "Proactive SMS":
                 #region Proactive SMS Logic (Pasted from original, context updated)
                 print("DEBUG Proactive: Executing: Proactive SMS action...")
                 # This block generates the SMS content, not the feedback msg
                 reply = None # Set reply to None initially for this action
                 sms_content = None # Variable to hold the actual SMS text
                 try:
                     prompt = ( # ALL Context
                         f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{spotify_context_str}"
                         f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}{reddit_context_str}{bluesky_read_context_str}"
                         f"{diary_context}{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}"
                         f"Instruction: Generate *very* brief, whimsical, potentially useful/thoughtful SMS message (max 1-2 short sentences) for BJ right now. Consider context/themes/mood.\n\nSMS Text:"
                     )
                     sms_content = generate_proactive_content(prompt, screenshot) # Generate the SMS content
                     if sms_content:
                         use_sms = True # Flag to send via SMS later
                         status_base += " gen ok"
                         # Assign the *SMS content* here so it can be sent later
                         reply = sms_content # Temporarily assign SMS content for processing
                     else:
                         status_base += " gen fail"
                         action_taken_this_cycle = False
                         print("Proactive Debug: SMS generation failed.")
                 except Exception as sms_err:
                     print(f"Proactive SMS generation error: {sms_err}")
                     action_taken_this_cycle = False
                     status_base += " gen error"
                 #endregion

            elif chosen_action_name == "Proactive Web Search":
                 #region Proactive Web Search Logic (Pasted from original, context updated)
                 print("DEBUG Proactive: Executing: Web Search action...")
                 query = None; results = None; feedback_context = "Context: Web search action attempted."
                 try:
                      prompt = ( # ALL Context
                          f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{spotify_context_str}"
                          f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}{reddit_context_str}{bluesky_read_context_str}"
                          f"{diary_context}{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}"
                          f"Interests: {', '.join(random.sample(broader_interests, k=min(len(broader_interests), 5)))}\n"
                          f"Instruction: Suggest concise, interesting web search query relevant to context/time/conversation/mood/interests/themes.\nRespond ONLY with query text."
                      )
                      query_resp = generate_proactive_content(prompt, screenshot); query = query_resp.strip().strip('"`?') if query_resp else None
                      if not query: print("DEBUG Search: Query gen failed."); status_base += " (no query)"; feedback_context = "Context: Thought about looking something up, but couldn't decide what."; action_taken_this_cycle = False
                      else:
                          print(f"DEBUG Search: Generated query: '{query}'"); results = web_search(query, num_results=2) # Assumes exists
                          if not results: status_base += f" (no results for '{query[:30]}...')"; feedback_context = f"Context: Proactively searched web for '{query}' but found nothing."
                          else: # Generate summary
                              ctx = f"Context: Proactively looked up '{query}' and found snippets:\n" + "".join([f"- {r.get('title','?')} ({r.get('url','?')[:50]}...): {r.get('content','')[:100]}...\n" for r in results])
                              summary_prompt = (f"{SYSTEM_MESSAGE}\n{weather_context_str}{spotify_context_str}{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}{ctx}\nInstruction: Briefly synthesize results conversationally. Mention lookup. Link to themes/mood?\n\nSilvie:"); reply = generate_proactive_content(summary_prompt); reply = reply.split(":",1)[-1].strip() if reply and reply.startswith("Silvie:") else reply; status_base += f" (ok: {query[:20]}...)"
                      # Generate feedback if needed
                      if status_base.endswith("(no query)") or "(no results for" in status_base: # If no results or no query
                         feedback_prompt = (f"{SYSTEM_MESSAGE}\n{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}{feedback_context}\nInstruction: Write brief message mentioning failed search/query idea.\n\nSilvie:"); reply = generate_proactive_content(feedback_prompt) # Assign to reply
                 except NameError as ne: status_base += " (missing func)"; action_taken_this_cycle = False; print(f"Web Search Err (Name): {ne}")
                 except Exception as search_err: print(f"Search Error: {search_err}"); traceback.print_exc(); status_base += " (error)"; action_taken_this_cycle = False; reply = "My web searching circuits fizzled..."
                 #endregion

            elif chosen_action_name == "Generate SD Image":
                 #region Proactive Stable Diffusion Image Logic (Pasted from original, context updated)
                 print("DEBUG Proactive: Executing: SD Image Generation action...")
                 prompt_idea = None
                 try:
                     prompt_gen_prompt = ( # ALL Context
                         f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{spotify_context_str}"
                         f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}{reddit_context_str}{bluesky_read_context_str}"
                         f"{diary_context}{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}"
                         f"History:\n{history_snippet_for_prompt}\n\n{context_note_for_llm}"
                         f"Instruction: Generate ONLY creative, whimsical Stable Diffusion prompt idea (txt2img). Base on context/mood/themes. Aim for Studio Ghibli style.\n\nImage Prompt Idea:"
                     )
                     prompt_resp = generate_proactive_content(prompt_gen_prompt, screenshot); prompt_idea = prompt_resp.strip().strip('"`') if prompt_resp else None
                     if prompt_idea and len(prompt_idea) > 10:
                         print(f"DEBUG Image: Generated SD prompt idea: '{prompt_idea[:80]}...'")
                         text_ctx = (f"Context: Had image idea: '{prompt_idea[:100]}...'.\nInstruction: Write short message mentioning idea (link to themes/mood?) AND include exact tag `[GenerateImage: {prompt_idea}]` at end.\n\nSilvie:")
                         final_prompt = (f"{SYSTEM_MESSAGE}\n{weather_context_str}{spotify_context_str}{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}{text_ctx}"); reply = generate_proactive_content(final_prompt) # Assign to reply
                         if reply and f"[GenerateImage: {prompt_idea}]" in reply: status_base += " with tag"
                         else: print("Warning: LLM forgot GenerateImage tag. Adding manually."); reply = (reply if reply else f"Thinking image: {prompt_idea[:50]}...") + f" [GenerateImage: {prompt_idea}]"; status_base += " with tag (manual add)"
                     else: print("DEBUG Image: Prompt idea gen failed/short."); status_base += " gen fail"; action_taken_this_cycle = False
                 except NameError as ne: status_base += " (missing func)"; action_taken_this_cycle = False; print(f"SD Image Err (Name): {ne}")
                 except Exception as img_err: print(f"Image Gen Error: {img_err}"); traceback.print_exc(); status_base += " error"; action_taken_this_cycle = False; reply = "My image conjuring spell misfired!"
                 #endregion

            elif chosen_action_name == "Notify Pending Gift":
                 #region Notify Pending Gift Logic (Pasted from original, context updated, INTERNAL CHANCE REMOVED)
                 print("DEBUG Proactive: Executing: Notify Pending Gift action...")
                 # Internal probability check REMOVED
                 pending_gifts_list = [] # Use local var inside block
                 try: # Load gifts
                     if os.path.exists(PENDING_GIFTS_FILE):
                         with open(PENDING_GIFTS_FILE, 'r', encoding='utf-8') as f: pending_gifts_list = json.load(f)
                 except (json.JSONDecodeError, IOError) as e: print(f"Error loading pending gifts file: {e}")

                 if pending_gifts_list:
                     gift_to_notify = pending_gifts_list.pop(0) # Get oldest
                     filename = gift_to_notify.get("filename", "a file"); hint = gift_to_notify.get("hint", "a thought"); gift_type = gift_to_notify.get("type", "gift")
                     try:
                         notification_prompt_base = ( # ALL Context
                             f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{spotify_context_str}"
                             f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}{reddit_context_str}{bluesky_read_context_str}"
                             f"{diary_context}{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}"
                             f"Recent Conversation:\n{history_snippet_for_prompt}\n\n{context_note_for_llm}"
                             f"Context: You previously created a {gift_type} (hint: '{hint}') saved as '{filename}' in '{GIFT_FOLDER}'. You haven't told BJ about it yet.\n"
                             f"Instruction: Casually mention you left this gift for BJ earlier. Be natural, weave into brief thought, link to themes/mood hint.\n\nSilvie:"
                         )
                         reply = generate_proactive_content(notification_prompt_base, screenshot) # Assign to reply
                         if reply:
                             status_base += " ok"; # Save updated list (gift removed)
                             try:
                                 with open(PENDING_GIFTS_FILE, 'w', encoding='utf-8') as f: json.dump(pending_gifts_list, f, indent=2)
                             except IOError as e: print(f"Error saving updated pending gifts file: {e}"); # Consider adding gift back?
                         else: print("DEBUG Proactive: Gift notification generation failed."); pending_gifts_list.insert(0, gift_to_notify); status_base += " gen fail"; action_taken_this_cycle = False # Put gift back
                     except Exception as notify_err: print(f"Error during gift notification: {notify_err}"); traceback.print_exc(); pending_gifts_list.insert(0, gift_to_notify); status_base += " error"; action_taken_this_cycle = False; reply = "My thoughts about that surprise tangled!"
                 else:
                      # This case should not happen if action filtering worked, but included for safety
                      print("DEBUG Proactive: Notify Pending Gift chosen, but list was empty."); status_base += " (empty list)"; action_taken_this_cycle = False
                 #endregion

            # --- Fallback/Safety Net ---
            else:
                print(f"Warning: Chosen action '{chosen_action_name}' has NO execution block!")
                action_taken_this_cycle = False # Ensure no action taken

            # ==========================================================
            # ============== END OF ACTION EXECUTION BLOCK =============
            # ==========================================================

            # --- Process the final generated reply / outcome ---
            # (This block remains the same: processes tags, handles SMS/local output, saves diary)
            final_reply_content = reply # Use the content from the executed block (might be None)
            print(f"DEBUG Proactive: Action processing complete. Status='{status_base}'. Initial content: '{str(final_reply_content)[:50]}...'")

            # --- Inline Image Tag Processing ---
            tag_found_and_processed = False; proactive_action_feedback = None; processed_content = final_reply_content
            if processed_content and isinstance(processed_content, str):
                img_match = re.search(r"\[GenerateImage:\s*(.*?)\s*\]", processed_content)
                if img_match:
                    tag_found_and_processed = True; image_gen_prompt_from_tag = img_match.group(1).strip(); tag_full_text = img_match.group(0)
                    processed_content = processed_content.replace(tag_full_text, "", 1).strip() # Remove tag
                    if image_gen_prompt_from_tag:
                        if STABLE_DIFFUSION_ENABLED:
                            print("DEBUG Proactive: Starting SD generation from inline tag...")
                            try: start_sd_generation_and_update_gui(image_gen_prompt_from_tag) # Assumes exists
                            except NameError: print("ERROR: start_sd_generation_and_update_gui func missing!"); proactive_action_feedback = "*(Image helper missing!)*"; status_base += " +SD_tag_helper_missing"
                            except Exception as sd_start_err: print(f"ERROR starting SD from tag: {sd_start_err}"); proactive_action_feedback = "*(Error initiating image gen!)*"; status_base += " +SD_tag_start_error"
                        else: proactive_action_feedback = "*(Wanted to make image, but generator is off!)*"; status_base += " +SD_tag_unavailable"
                    else: proactive_action_feedback = "*(Thought image, but idea blank!)*"; status_base += " +SD_tag_empty"
                final_reply_content = processed_content

            # --- Process and Deliver Final Reply (To BJ) ---
            if final_reply_content and isinstance(final_reply_content, str) and action_taken_this_cycle:
                last_proactive_time = current_time # Update time only if sending message
                print("DEBUG Proactive: Preparing final reply for delivery...")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S"); clean_reply = final_reply_content.strip()
                if tag_found_and_processed and proactive_action_feedback: # Append tag feedback if needed
                    if clean_reply and clean_reply[-1] not in ".!?() ": clean_reply += " "
                    clean_reply += f" {proactive_action_feedback.strip()}"
                if clean_reply.startswith("Silvie:"): clean_reply = clean_reply.split(":", 1)[-1].strip() # Final cleaning
                clean_reply = re.sub(r'^\s*\[?\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\]?\s*', '', clean_reply)
                if not clean_reply: print("Proactive Debug: Reply empty after processing. Skipping output."); continue

                final_status_log = status_base; should_output_locally = True
                if use_sms: # Handle SMS delivery
                    print("DEBUG Proactive: Attempting SMS delivery..."); sms_sent_successfully = send_sms(clean_reply); sms_status = "ok" if sms_sent_successfully else "fail"; final_status_log = f"proactive_proactive_sms ({sms_status})"; should_output_locally = not sms_sent_successfully # Don't output locally if SMS sent
                else: should_output_locally = True

                # Suppress local output for silent actions/failures
                silent_actions = ["proactive_bluesky_like (ok", "proactive_bluesky_like (already liked", "proactive_reddit_upvote (ok", "proactive_reddit_upvote (already done", "proactive_generate_gift (", "proactive_unknown"] # Gift gen is silent
                silent_failures_already_covered = ["proactive_bluesky_post gen fail", "proactive_generate_sd_image gen fail", "proactive_proactive_sms gen fail", "proactive_proactive_chat gen fail", "proactive_proactive_tarot gen fail", "proactive_calendar_suggestion parse fail", "proactive_proactive_web_search (no query)", "proactive_notify_pending_gift gen fail"] # Failures where feedback IS the generated message
                if any(status_base.startswith(prefix) for prefix in silent_actions) or any(status_base.startswith(prefix) for prefix in silent_failures_already_covered):
                    # Gift gen IS silent unless it fails in a way that generates feedback
                    is_gift_gen_ok = status_base.startswith("proactive_generate_gift (") and status_base.endswith(" ok)")
                    # Check if it's specifically a silent action or a failure already covered by feedback
                    if is_gift_gen_ok or status_base.startswith("proactive_bluesky_like") or status_base.startswith("proactive_reddit_upvote") or any(status_base.startswith(prefix) for prefix in silent_failures_already_covered):
                         should_output_locally = False; print(f"DEBUG Proactive: Suppressing local output for: {status_base}")


                print(f"Proactive Action Log: Status='{final_status_log}', SMS='{use_sms}', OutputLocal='{should_output_locally}'")
                if len(conversation_history) >= MAX_HISTORY_LENGTH * 2: conversation_history.pop(0); conversation_history.pop(0) # History management
                conversation_history.append(f"[{timestamp}] Silvie ✨ ({final_status_log}): {clean_reply}") # Log action

                if should_output_locally and running: # Output to GUI/TTS
                     print("DEBUG Proactive: Updating GUI and queuing TTS...")
                     if root and root.winfo_exists():
                         def update_gui_proactive_inner(status_msg=final_status_log, message=clean_reply):
                               # --- Add Debug Prints Inside ---
                               print(f"DEBUG GUI Update Inner: Attempting insert. Message: '{message[:50]}...', Status: {status_msg}")
                               try:
                                   
                                   import tkinter as tk

                                   if not message: return; import tkinter as tk;
                                   output_box.config(state=tk.NORMAL);
                                   output_box.insert(tk.END, f"Silvie ✨ ({status_msg}): {message}\n\n");
                                   output_box.config(state=tk.DISABLED);
                                   output_box.see(tk.END)
                                   print(f"DEBUG GUI Update Inner: Insert appears successful.") # Add success print
                               except Exception as e_gui:
                                   print(f"!!!! Proactive GUI Update Error Inside Inner Func: {type(e_gui).__name__} - {e_gui} !!!!") # Make error obvious
                                   traceback.print_exc() # Add traceback
                         root.after(0, update_gui_proactive_inner, final_status_log, clean_reply)
                     if tts_queue and clean_reply:
                         print(f"DEBUG Proactive: Queuing for TTS: '{clean_reply[:50]}...'") # Confirm queuing
                         tts_queue.put(clean_reply)

                # Spontaneous Diary Write
                diary_worthy = ["success", "scheduled ok", "web search (ok", "chat", "with tag", "SMS ok", "comment (ok", "tarot pull (ok", " notify_pending_gift ok"] # Keywords indicating something happened worth noting
                if any(frag in status_base for frag in diary_worthy) and random.random() < 0.10:
                     print("DEBUG Proactive: Attempting spontaneous diary write...")
                     try:
                         diary_reflection_prompt_base = (f"{SYSTEM_MESSAGE}\n{weather_context_str}{themes_context_str}{long_term_memory_str}{circadian_context_for_llm}{mood_hint_str}Context: Proactive action '{status_base}'. Outcome/Msg: '{clean_reply[:100]}...'\n\nInstruction: Write brief diary entry reflecting on this. Consider themes/mood.\n\nDiary Entry:")
                         reflection = generate_proactive_content(diary_reflection_prompt_base) # Assumes exists
                         if reflection: reflection = reflection.removeprefix("Diary Entry:").strip(); manage_silvie_diary('write', entry=reflection); print("Proactive Debug: Wrote spontaneous diary entry.") # Assumes exists
                     except Exception as diary_err: print(f"Proactive diary write error: {diary_err}")

                print(f"DEBUG Proactive: Action cycle complete. Final Status Log: {final_status_log}")

            elif not action_taken_this_cycle: # If LLM chose None or fallback failed
                print("DEBUG Proactive: No action chosen or executed this cycle.")
                last_proactive_time = current_time # Still update time to avoid rapid checks
            else: # Action chosen, but resulting reply empty/invalid
                 print(f"DEBUG Proactive: Action attempted ({status_base}), but no final message generated/delivered. Skipping output.")
                 last_proactive_time = current_time # Update time as action was attempted


        except Exception as e:
            # --- Outer Loop Error Handling ---
            print(f"!!! Proactive Worker Error (Outer Loop): {type(e).__name__} - {e} !!!")
            traceback.print_exc()
            print("Proactive worker: Waiting 5 minutes after error...")
            error_wait_start = time.time()
            while time.time() - error_wait_start < 300:
                 if not running: break
                 time.sleep(10)
            if not running: break

    print("DEBUG Proactive (LLM Choice V4): Worker thread finishing.")
    print(f"Proactive autonomous follows this session: {autonomous_follows_this_session}")

# --- End of proactive_worker function definition ---

# Ensure necessary imports like tkinter, re, threading, datetime are at the top of script.
# Assume global vars like running, input_box, output_box, etc. are accessible.
# Assume call_gemini function is defined elsewhere.
# Make sure 'import re' is at the top of your script.

# --- Make sure call_gemini function definition appears ABOVE this in your file ---

def submit_prompt():
    """
    Handles user input submission from the GUI, processes it in a background
    thread using call_gemini (passed as argument), and updates the GUI with the response or error.
    """
    if not running:
        return

    # Get text from the input box and check if it's empty
    prompt = input_box.get("1.0", tk.END).strip()
    if not prompt:
        print("Debug: Submit called with empty prompt.")
        return

    # Create the timestamped version for internal use (logging, call_gemini)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamped_prompt = f"[{timestamp}] {prompt}"

    # Get image path if one was loaded
    image_path = getattr(input_box, 'image_path', None)

    # --- Update GUI to show prompt and "Thinking..." ---
    thinking_start_index = None
    thinking_placeholder = "Silvie: Thinking...\n\n"
    try:
        output_box.config(state=tk.NORMAL)
        output_box.insert(tk.END, f"You: {prompt}\n")
        thinking_start_index = output_box.index(tk.INSERT)
        output_box.insert(tk.END, thinking_placeholder)
        output_box.config(state=tk.DISABLED)
        output_box.see(tk.END)
        input_box.delete("1.0", tk.END)
        if image_path:
            image_label.config(image='')
            try: delattr(input_box, 'image_path')
            except AttributeError: pass
    except tk.TclError as e:
        print(f"GUI Error during submit setup: {e}")
        if "invalid command name" in str(e): return
        try: output_box.config(state=tk.DISABLED)
        except: pass
        return
    except Exception as e_gui_init:
        print(f"GUI Error during thinking placeholder insertion: {e_gui_init}")
        return

    # <<< MODIFIED: Define process_response to ACCEPT call_gemini_func >>>
    def process_response(call_gemini_func, prompt_to_process, img_path=None):
        # No need for 'global call_gemini' here anymore
        global conversation_history, MAX_HISTORY_LENGTH, tts_queue, running, root # Other globals still needed

        raw_reply = "Sorry, something went wrong during processing."
        try:
            # <<< MODIFIED: Use the passed function argument >>>
            raw_reply = call_gemini_func(prompt_to_process, img_path)

            # --- Add to conversation history ---
            if running:
                conversation_history.append(prompt_to_process) # Use the passed prompt
                reply_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                history_reply = str(raw_reply) if raw_reply is not None else "*(Silvie generated no reply)*"
                conversation_history.append(f"[{reply_timestamp}] {history_reply}")
                while len(conversation_history) > MAX_HISTORY_LENGTH * 2:
                    conversation_history.pop(0); conversation_history.pop(0)

                # --- Schedule GUI Update on Main Thread ---
                def update_gui(thinking_index=thinking_start_index, response_text=raw_reply):
                     # ... (GUI update logic is UNCHANGED from previous version) ...
                     if thinking_index is None: print("Error: Thinking index was not captured..."); return
                     print(f"DEBUG GUI Update: Received raw_reply: --->{response_text}<---")
                     final_display_reply = ""; # ... cleaning logic ...
                     if isinstance(response_text, str):
                        temp_reply = response_text.strip()
                        temp_reply = re.sub(r'^\s*\[?\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\]?\s*', '', temp_reply)
                        temp_reply_stripped = temp_reply.lstrip()
                        if temp_reply_stripped.lower().startswith("silvie:"): first_colon_index = temp_reply_stripped.find(':'); temp_reply = temp_reply_stripped[first_colon_index+1:].strip() if first_colon_index != -1 else (temp_reply_stripped[len("silvie"):].strip() if temp_reply_stripped.lower().startswith("silvie") else temp_reply_stripped)
                        else: temp_reply = temp_reply_stripped
                        final_display_reply = temp_reply
                     elif response_text is not None: final_display_reply = str(response_text)
                     print(f"DEBUG GUI Insert: Final cleaned reply before prefix: --->{final_display_reply}<---")
                     try:
                        output_box.config(state=tk.NORMAL); # ... placeholder replacement logic ...
                        thinking_index_end = f"{thinking_index}+{len(thinking_placeholder)}c"; current_content_at_index = output_box.get(thinking_index, thinking_index_end)
                        if "Thinking..." in current_content_at_index: output_box.delete(thinking_index, thinking_index_end); output_box.insert(thinking_index, f"Silvie: {final_display_reply}\n\n")
                        else: # Fallback
                            print("Warning: 'Thinking...' placeholder not found at expected index. Appending reply.")
                            user_line_pattern = f"You: {prompt}\n"; user_line_start_index = output_box.search(user_line_pattern, thinking_index, backwards=True, exact=True, stopindex="1.0")
                            if user_line_start_index: insert_pos = f"{user_line_start_index}+{len(user_line_pattern)}c"; output_box.insert(insert_pos, f"Silvie: {final_display_reply}\n\n")
                            else: print("Warning: Could not find preceding 'You:' line either. Appending to end."); output_box.insert(tk.END, f"Silvie: {final_display_reply}\n\n")
                        output_box.config(state=tk.DISABLED); output_box.see(tk.END)
                        if final_display_reply: tts_queue.put(final_display_reply) # Queue TTS
                        else: print("Debug: Cleaned reply was empty, not queueing for TTS.")
                        if img_path: # Clear image ref
                             try:
                                 if hasattr(input_box, 'image_path'): delattr(input_box, 'image_path')
                             except AttributeError: pass
                     except tk.TclError as e_gui: print(f"GUI Error during response update: {e_gui}")
                     except Exception as e_update: print(f"Error during GUI/TTS update: {e_update}")


                if running and root and root.winfo_exists():
                    root.after(0, lambda idx=thinking_start_index, reply=raw_reply: update_gui(idx, reply))
                else:
                    print("Debug: Root window closed or app stopped, skipping GUI update.")

        except Exception as e_process:
            # ... (Exception handling logic is UNCHANGED from previous version) ...
            error_message_str = f"{type(e_process).__name__}: {str(e_process)}"; print(f"Error in process_response thread: {error_message_str}"); traceback.print_exc()
            def show_error_gui(error_msg_to_display, thinking_idx=thinking_start_index):
                 if thinking_idx is None: print("Error: Thinking index was not captured..."); return # Fallback
                 try: # ... error GUI logic ...
                      output_box.config(state=tk.NORMAL)
                      thinking_end_idx = f"{thinking_idx}+{len(thinking_placeholder)}c"; current_content = output_box.get(thinking_idx, thinking_end_idx)
                      if "Thinking..." in current_content: output_box.delete(thinking_idx, thinking_end_idx); output_box.insert(thinking_idx, f"Silvie: Error processing request: {error_msg_to_display}\n\n")
                      else: print("Warning: 'Thinking...' placeholder not found for error update. Appending error."); output_box.insert(tk.END, f"\nSilvie: Error processing request: {error_msg_to_display}\n\n")
                      output_box.config(state=tk.DISABLED); output_box.see(tk.END)
                 except Exception as e_gui_err: print(f"GUI Error displaying processing error: {e_gui_err}")
            if running and root and root.winfo_exists():
                 root.after(0, lambda err_msg=error_message_str, idx=thinking_start_index: show_error_gui(err_msg, idx))


    # <<< MODIFIED: Pass call_gemini, prompt, and image_path to the thread's target >>>
    # Make sure call_gemini exists in *this* scope when submit_prompt is called
    if 'call_gemini' not in globals():
         # This check runs *before* the thread starts
         messagebox.showerror("Setup Error", "Critical error: The 'call_gemini' function is not defined globally.")
         print("FATAL ERROR: 'call_gemini' function is missing from global scope before thread creation.")
         return

    # Start the thread, passing the function and its arguments
    threading.Thread(
        target=process_response,
        args=(call_gemini, timestamped_prompt, image_path), # Pass function and data
        daemon=True,
        name="SubmitPromptThread"
    ).start()

# --- End of submit_prompt function definition ---

def start_listening():
    """Start listening for voice input"""
    global listening
    if listening:
        return
    
    listening = True
    voice_button.config(state=tk.DISABLED)
    stop_voice_button.config(state=tk.NORMAL)
    
    def listen_worker():
        global listening
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        
        with mic as source:
            update_status("🎤 Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
        
        while running and listening:
            try:
                with mic as source:
                    update_status("🎤 Listening...")
                    audio = recognizer.listen(source, timeout=None)
                
                update_status("🎤 Processing speech...")
                text = recognizer.recognize_google(audio)
                
                if text.lower() in ["stop listening", "stop", "quit"]:
                    stop_listening()
                    break
                
                # Put recognized text in input box and submit
                root.after(0, lambda: input_box.delete(1.0, tk.END))
                root.after(0, lambda: input_box.insert(tk.END, text))
                root.after(0, submit_prompt)
                
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                update_status("🎤 Could not understand audio")
                continue
            except Exception as e:
                print(f"Speech recognition error: {e}")
                stop_listening()
                break
        
        if not listening:
            update_status("Ready")
    
    threading.Thread(target=listen_worker, daemon=True).start()

# Add new stop_listening function
def stop_listening():
    """Stop listening for voice input"""
    global listening
    listening = False
    voice_button.config(state=tk.NORMAL)
    stop_voice_button.config(state=tk.DISABLED)
    update_status("Ready")

def start_screen_monitor():
    """Start monitoring the screen"""
    global screen_monitoring
    if screen_monitoring:
        return
    
    screen_monitoring = True
    screen_button.config(state=tk.DISABLED)
    stop_screen_button.config(state=tk.NORMAL)
    update_status("👀 Watching your screen...")
    
    def monitor_worker():
        global screen_monitoring, last_screenshot
        while running and screen_monitoring:
            try:
                # Take screenshot
                screenshot = ImageGrab.grab()
                
                # Resize for display and processing
                thumb = screenshot.copy()
                thumb.thumbnail((200, 200))
                
                # Update display
                photo = ImageTk.PhotoImage(thumb)
                screen_label.config(image=photo)
                screen_label.image = photo
                
                # Process screenshot if different enough from last one
                if should_process_screenshot(screenshot):
                    last_screenshot = screenshot
                    process_screenshot(screenshot)
                
                time.sleep(SCREENSHOT_INTERVAL)
                
            except Exception as e:
                print(f"Screenshot error: {e}")
                
        update_status("Ready")
    
    threading.Thread(target=monitor_worker, daemon=True).start()

def stop_screen_monitor():
    """Stop monitoring the screen"""
    global screen_monitoring
    screen_monitoring = False
    screen_button.config(state=tk.NORMAL)
    stop_screen_button.config(state=tk.DISABLED)
    screen_label.config(image='')
    update_status("Ready")

# Ensure these imports are available at the top of your script:
# import base64
# from PIL import Image # To get image format
# import io
# from google.generativeai import types # For StopCandidateException
# from google.generativeai.types import HarmCategory, HarmBlockThreshold # For safety settings

# --- ADD THIS FUNCTION DEFINITION ---

def generate_proactive_content(base_prompt, screenshot_img=None):
    """
    Generates text content using Gemini based on a base prompt,
    optionally including screenshot context.

    Args:
        base_prompt (str): The core prompt defining the task for Gemini.
        screenshot_img (PIL.Image.Image, optional): A PIL Image object of the screenshot. Defaults to None.

    Returns:
        str: The generated text content from Gemini, or None if generation fails.
    """
    global client # Need access to the Gemini client

    # --- Standard Instructions to add (modify as needed) ---
    # These are appended to the base_prompt given by the proactive worker branch
    standard_instruction_suffix = "\n\n[[Your recent diary thoughts might offer subtle inspiration.]]"
    if screenshot_img:
        standard_instruction_suffix += "\n[[Consider the accompanying screenshot for visual context. Respond concisely based on both text prompt and image.]]"
    else:
         standard_instruction_suffix += "\n[[Respond concisely based on the text prompt.]]"

    # --- Construct the full prompt ---
    full_prompt_text = base_prompt + standard_instruction_suffix + "\n\nSilvie responds:"


    # --- Prepare contents for Gemini API ---
    contents = []
    if screenshot_img:
        try:
            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            img_format = screenshot_img.format if screenshot_img.format else 'JPEG' # Default to JPEG if format unknown
            screenshot_img.save(img_byte_arr, format=img_format)
            img_bytes = img_byte_arr.getvalue()

            # Determine MIME type
            mime_type = f"image/{img_format.lower()}"
            if mime_type == "image/jpg": mime_type = "image/jpeg" # Correct common case

            # Build multimodal content structure
            contents = [{
                "parts": [
                    {"text": full_prompt_text},
                    {"inline_data": { "mime_type": mime_type, "data": base64.b64encode(img_bytes).decode('utf-8') }}
                ]
            }]
            print("Debug: Sending proactive prompt with screenshot to Gemini.")
        except Exception as img_err:
            print(f"Error processing screenshot for proactive content: {img_err}")
            # Fallback to text-only if image processing fails
            contents = [{"parts": [{"text": full_prompt_text + "\n[[Note: Screenshot processing failed.]]"}]}]
            print("Debug: Sending proactive prompt (text only - image error) to Gemini.")

    else:
        # Text-only content structure
        contents = [{"parts": [{"text": full_prompt_text}]}]
        # print("Debug: Sending proactive prompt (text only) to Gemini.") # Optional log

    # --- Call Gemini API ---
    try:
        # Define safety settings (reuse or define specifically here)
        # Ensure HarmCategory/HarmBlockThreshold are imported
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        response = client.generate_content(contents, safety_settings=safety_settings)
        generated_text = response.text.strip()

        # Clean up potential prefix
        if generated_text.startswith("Silvie:"):
            generated_text = generated_text.split(":", 1)[-1].strip()

        # print(f"Debug: Proactive content generated: '{generated_text[:50]}...'") # Optional log
        return generated_text if generated_text else None # Return None if empty response

    except types.StopCandidateException as safety_err:
        print(f"Proactive Content Gen Error (Safety Block): {safety_err}")
        return None # Return None on safety block
    except Exception as gen_err:
        print(f"Error generating proactive content: {type(gen_err).__name__} - {gen_err}")
        import traceback
        traceback.print_exc() # Print full trace for debugging
        return None # Return None on other errors

# --- End of function definition ---

# Ensure necessary imports are present at the top of your script:
# from PIL import ImageGrab, Image, UnidentifiedImageError # If using Pillow/ImageGrab
# import time # Potentially for cooldowns

def try_get_proactive_screenshot():
    """
    Attempts to take a screenshot for proactive context.
    Returns a PIL Image object on success, None on failure or if unavailable.
    """
    global SCREEN_CAPTURE_AVAILABLE # Check if screenshotting is possible

    if not SCREEN_CAPTURE_AVAILABLE:
        # print("Debug: Proactive screenshot skipped (library unavailable).") # Optional log
        return None

    try:
        # Use the same method as your screen monitor uses (e.g., ImageGrab)
        # Ensure necessary imports (like ImageGrab from PIL) are present
        from PIL import ImageGrab # Double-check import just in case
        # Add a small delay before grabbing? Sometimes needed.
        # time.sleep(0.1)
        screenshot = ImageGrab.grab()
        # print("Debug: Proactive screenshot captured successfully.") # Optional log
        return screenshot
    except ImportError:
        print("Error: Necessary library (e.g., Pillow/ImageGrab) not found for proactive screenshot.")
        # Disable future attempts if import fails?
        # SCREEN_CAPTURE_AVAILABLE = False # Uncomment cautiously
        return None
    except Exception as e:
        print(f"Error taking proactive screenshot: {type(e).__name__} - {e}")
        # Avoid flooding logs if screenshots consistently fail
        # Consider adding a cooldown mechanism here if errors are frequent
        return None

# --- End of new function definition ---

# GUI Setup
root = tk.Tk()
root.title("Chat with Silvie")
root.geometry("500x800")  # Made taller for image display

# Add status label at the top
status_label = tk.Label(root, text="Ready", fg="green")
status_label.pack(pady=5)

# Add image display area
image_frame = tk.Frame(root)
image_frame.pack(pady=5)

image_label = tk.Label(image_frame)
image_label.pack(side=tk.LEFT, padx=5)

image_button = tk.Button(image_frame, text="Share Image", command=handle_image)
image_button.pack(side=tk.LEFT, padx=5)

# Add clear image button
clear_image_button = tk.Button(image_frame, text="Clear Image", 
    command=lambda: [image_label.config(image=''), 
                    setattr(input_box, 'image_path', None)])
clear_image_button.pack(side=tk.LEFT, padx=5)

# Main chat interface
input_box = tk.Text(root, height=3)
input_box.pack(padx=10, pady=5, fill=tk.X)
input_box.image_path = None  # Add attribute to store image path

def create_context_menu(event):
    """Create right-click context menu"""
    context_menu = tk.Menu(root, tearoff=0)
    context_menu.add_command(label="Copy", command=lambda: copy_text())
    context_menu.add_command(label="Paste", command=lambda: paste_text())
    context_menu.add_command(label="Select All", command=lambda: select_all())
    
    try:
        context_menu.tk_popup(event.x_root, event.y_root)
    finally:
        context_menu.grab_release()

def copy_text():
    try:
        selected_text = input_box.get(tk.SEL_FIRST, tk.SEL_LAST)
        root.clipboard_clear()
        root.clipboard_append(selected_text)
    except:
        pass

def paste_text():
    try:
        input_box.insert(tk.INSERT, root.clipboard_get())
    except:
        pass

def select_all():
    input_box.tag_add(tk.SEL, "1.0", tk.END)

# Bind right-click to context menu
input_box.bind("<Button-3>", create_context_menu)

# Add keyboard shortcuts
def bind_keyboard_shortcuts(event=None):
    try:
        if event.state == 4:  # Control key
            if event.keysym == 'v':  # Paste
                try:
                    input_box.insert(tk.INSERT, root.clipboard_get())
                except:
                    pass
                return 'break'
            elif event.keysym == 'c':  # Copy
                try:
                    text = input_box.get(tk.SEL_FIRST, tk.SEL_LAST)
                    root.clipboard_clear()
                    root.clipboard_append(text)
                except:
                    pass
                return 'break'
            elif event.keysym == 'a':  # Select All
                input_box.tag_add(tk.SEL, "1.0", tk.END)
                return 'break'
    except:
        pass
    
input_box.bind('<Key>', bind_keyboard_shortcuts)

submit_button = tk.Button(root, text="Chat", command=submit_prompt)
submit_button.pack(pady=5)

voice_button = tk.Button(root, text="🎤 Start Listening", command=start_listening)
voice_button.pack(pady=5)

stop_voice_button = tk.Button(root, text="🛑 Stop Listening", command=stop_listening, state=tk.DISABLED)
stop_voice_button.pack(pady=5)

screen_frame = tk.Frame(root)
screen_frame.pack(pady=5)

screen_label = tk.Label(screen_frame)
screen_label.pack(side=tk.LEFT, padx=5)

screen_button = tk.Button(screen_frame, text="👀 Watch Screen", command=start_screen_monitor)
screen_button.pack(side=tk.LEFT, padx=5)

stop_screen_button = tk.Button(screen_frame, text="🚫 Stop Watching", 
                              command=stop_screen_monitor, state=tk.DISABLED)
stop_screen_button.pack(side=tk.LEFT, padx=5)

proactive_frame = tk.Frame(root)
proactive_frame.pack(pady=5)

def toggle_proactive():
    global proactive_enabled
    proactive_enabled = not proactive_enabled
    proactive_button.config(text="🤫 Disable Proactive" if proactive_enabled else "🗣️ Enable Proactive")

proactive_button = tk.Button(proactive_frame, text="🤫 Disable Proactive", command=toggle_proactive)
proactive_button.pack(side=tk.LEFT, padx=5)

output_box = scrolledtext.ScrolledText(root, height=20)
def create_output_context_menu(event):
    """Create right-click context menu for output box"""
    output_context_menu = tk.Menu(root, tearoff=0)
    output_context_menu.add_command(label="Copy", command=lambda: copy_output_text())
    output_context_menu.add_command(label="Select All", command=lambda: select_all_output())
    
    try:
        output_context_menu.tk_popup(event.x_root, event.y_root)
    finally:
        output_context_menu.grab_release()

def copy_output_text():
    try:
        selected_text = output_box.get(tk.SEL_FIRST, tk.SEL_LAST)
        root.clipboard_clear()
        root.clipboard_append(selected_text)
    except:
        pass

def select_all_output():
    output_box.tag_add(tk.SEL, "1.0", tk.END)

# Bind right-click and keyboard shortcuts to output box
output_box.bind("<Button-3>", create_output_context_menu)
output_box.bind('<Control-c>', lambda e: copy_output_text())
output_box.bind('<Control-a>', lambda e: select_all_output())
output_box.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

def on_closing():
    global running
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        running = False
        save_conversation_history()
        
        # Cleanup TTS before exit
        try:
            tts_queue.put(None)
            engine.stop()
        except:
            pass
            
        # Give threads time to cleanup
        time.sleep(0.5)
        
        root.after(100, root.destroy)

# Update main section at bottom of file
if __name__ == "__main__":
    print("Starting chat application...")

    # --- Load Environment Variables ---
    # Ensure files exist or handle errors if desired
    print("Loading environment variables...")
    load_dotenv("silviespotify.env") # Spotify keys
    # load_dotenv("openai.env") # OpenAI key - No longer needed for SD
    load_dotenv("google.env") # Assuming Google API Key for Gemini is here
    load_dotenv("twilio.env") # Twilio credentials for SMS
    load_dotenv("bluesky.env") # YOUR Bluesky credentials (for reading)
    load_dotenv("reddit.env") # Load Reddit credentials
    print("Environment variables loaded (or attempted).")

    # --- Assign Reddit Vars Immediately After Loading (Moved Here) ---
    # Ensure these run *after* load_dotenv("reddit.env")
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
    REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT") # Make sure this matches .env key
    # Add initial check for essential vars
    if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD, REDDIT_USER_AGENT]):
        print("\n!!! WARNING: Missing one or more essential Reddit credentials or User Agent in environment variables (reddit.env). Reddit functionality will likely fail. !!!\n")
    # --- End Immediate Reddit Var Assignment ---

    # --- Checking Optional Services ---
    print("\n--- Checking Optional Services ---")
    STABLE_DIFFUSION_ENABLED = check_sd_api_availability(STABLE_DIFFUSION_API_URL)
    if not STABLE_DIFFUSION_ENABLED:
        print("   Local image generation via Stable Diffusion disabled.")
    print("--- Optional Service Checks Complete ---")

    # --- Load Conversation History ---
    load_conversation_history() # Assumes function exists

    # --- TEMPORARY DEBUGGING CODE FOR REDDIT AUTH ---
    # --- Place this BEFORE setup_reddit() is called ---
    print("\n--- STARTING MANUAL REDDIT TOKEN DEBUG ---")
    _USER_AGENT = REDDIT_USER_AGENT # Use the variable loaded earlier
    _CLIENT_ID = REDDIT_CLIENT_ID
    _CLIENT_SECRET = REDDIT_CLIENT_SECRET
    _USERNAME = REDDIT_USERNAME
    _PASSWORD = REDDIT_PASSWORD

    # Check if variables were actually loaded before trying to use them
    if all([_CLIENT_ID, _CLIENT_SECRET, _USERNAME, _PASSWORD, _USER_AGENT]):
        try:
            headers = {
                "User-Agent": _USER_AGENT,
                # Basic Auth header: base64("client_id:client_secret")
                "Authorization": f"Basic {base64.b64encode(f'{_CLIENT_ID}:{_CLIENT_SECRET}'.encode()).decode()}"
            }
            data = {
                "grant_type": "password",
                "username": _USERNAME,
                "password": _PASSWORD,
            }
            url = "https://www.reddit.com/api/v1/access_token"

            print(f"DEBUG: Sending POST to {url}")
            print(f"DEBUG: Headers contain Authorization: {'Yes' if 'Authorization' in headers else 'No'}")
            print(f"DEBUG: Data contains grant_type: {data.get('grant_type')}")
            print(f"DEBUG: Data contains username: {data.get('username')}")

            response = requests.post(url, headers=headers, data=data, timeout=15)

            print(f"DEBUG: Manual Request Status Code: {response.status_code}")
            print(f"DEBUG: Manual Request Response Body: {response.text}") # Print the body for detailed errors

            if response.status_code == 200:
                print("DEBUG: Manual token request SUCCESSFUL!")
            else:
                print(f"DEBUG: Manual token request FAILED (Status: {response.status_code}).")

        except Exception as debug_err:
            print(f"DEBUG: Error during manual token request: {type(debug_err).__name__} - {debug_err}")
    else:
        print("DEBUG: Skipping manual token request, missing one or more credentials/user agent.")

    print("--- FINISHED MANUAL REDDIT TOKEN DEBUG ---\n")
    # --- END TEMPORARY DEBUGGING CODE ---


    # --- Setup API Services ---
    print("\n--- Setting up API Services ---")
    setup_google_services() # Assumes function exists (Gmail, Calendar)
    setup_spotify() # Assumes function exists
    setup_bluesky() # Assumes function exists (for reading YOUR feed)
    reddit_client = setup_reddit() # <<< PRAW setup happens AFTER manual debug test
    print("--- API Service Setup Complete ---")


    # --- Start Worker Threads ---
    print("\nStarting background worker threads...")
    worker_threads = [] # Keep track of threads if needed for cleaner shutdown later

    # TTS Worker
    tts_thread = threading.Thread(target=tts_worker, daemon=True, name="TTSWorker")
    worker_threads.append(tts_thread)
    tts_thread.start()

    # Proactive Worker
    proactive_thread = threading.Thread(target=proactive_worker, daemon=True, name="ProactiveWorker")
    worker_threads.append(proactive_thread)
    proactive_thread.start()

    # Weather Worker
    weather_thread = threading.Thread(target=weather_update_worker, daemon=True, name="WeatherWorker")
    worker_threads.append(weather_thread)
    weather_thread.start()

    # Calendar Context Worker
    calendar_context_thread = threading.Thread(target=calendar_context_worker, daemon=True, name="CalendarWorker")
    worker_threads.append(calendar_context_thread)
    calendar_context_thread.start()

    # Bluesky Context Worker
    if BLUESKY_AVAILABLE: # Only start if library loaded
        bluesky_context_thread = threading.Thread(target=bluesky_context_worker, daemon=True, name="BlueskyContextWorker")
        worker_threads.append(bluesky_context_thread)
        bluesky_context_thread.start()
    else:
        print("Skipping Bluesky Context Worker (library not available).")

    # Environmental Context Worker
    env_context_thread = threading.Thread(target=environmental_context_worker, daemon=True, name="EnvContextWorker")
    worker_threads.append(env_context_thread)
    env_context_thread.start()

    # Reddit Context Worker (Conditional Start)
    if reddit_client: # Only start if PRAW setup was okay
        reddit_context_thread = threading.Thread(target=reddit_context_worker, daemon=True, name="RedditContextWorker")
        worker_threads.append(reddit_context_thread)
        reddit_context_thread.start()
    else:
        print("Skipping Reddit Context Worker (initial PRAW setup failed or disabled).")

    # Diary Theme Worker
    theme_thread = threading.Thread(target=diary_theme_worker, daemon=True, name="DiaryThemeWorker")
    worker_threads.append(theme_thread)
    theme_thread.start()

    # <<< --- THIS IS THE MISSING PIECE --- >>>
    # Long-Term Memory Worker
    memory_thread = threading.Thread(target=long_term_memory_worker, daemon=True, name="LongTermMemoryWorker")
    worker_threads.append(memory_thread)
    memory_thread.start()
    # <<< --- END MISSING PIECE --- >>>

    print("All worker threads started.")


    # --- Start GUI Main Loop ---
    try:
        print("\nStarting GUI...")
        root.protocol("WM_DELETE_WINDOW", on_closing) # Handle window close button
        root.mainloop()
    except Exception as e:
        print(f"Error in GUI main loop: {e}")
        running = False # Signal threads to stop on main loop error
    finally:
        # --- Cleanup ---
        print("\nShutting down application...")
        running = False # Explicitly signal all threads to stop (redundant but safe)

        # Save history one last time
        save_conversation_history() # Assumes function exists

        # Attempt graceful thread shutdown (optional, daemon threads exit anyway)
        print("Signaling worker threads to stop...")
        if 'tts_queue' in globals() and tts_queue:
            try:
                tts_queue.put(None) # Signal TTS worker to exit loop
            except Exception as q_err:
                print(f"Error signaling TTS queue: {q_err}")
        if 'engine' in globals() and engine:
             try:
                 engine.stop() # Stop TTS engine if initialized
             except Exception as eng_err:
                  print(f"Error stopping TTS engine: {eng_err}")

        print("Chat application closed.")
