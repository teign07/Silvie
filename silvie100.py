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

def manage_silvie_diary(action, entry=None, search_query=None, max_entries=5): # Added max_entries default
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
            global conversation_history
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
            print(f"DEBUG manage_silvie_diary: action='write', returning True") # <-- Add Debug Print
            return True

        elif action == 'read':
            # --- MODIFICATION START ---
            if max_entries == 'all':
                # Return a copy of the entire diary list
                result = diary[:]
                print(f"DEBUG manage_silvie_diary: action='read', max_entries='all', returning list of length {len(result)}") # <-- Add Debug Print
                return result
            else:
                try:
                    # Ensure max_entries is an integer for slicing
                    num_entries = int(max_entries)
                    # Return last N entries
                    result = diary[-num_entries:] if diary else []
                    print(f"DEBUG manage_silvie_diary: action='read', num_entries={num_entries}, returning list of length {len(result)}") # <-- Add Debug Print
                    return result
                except ValueError:
                    print(f"Warning: Invalid max_entries value '{max_entries}' for diary read. Defaulting to 5.")
                    result = diary[-5:] if diary else []
                    print(f"DEBUG manage_silvie_diary: action='read', ValueError fallback, returning list of length {len(result)}") # <-- Add Debug Print
                    return result
            # --- MODIFICATION END ---

        elif action == 'search':
            # Search diary entries
            if not search_query:
                print(f"DEBUG manage_silvie_diary: action='search', no query, returning empty list") # <-- Add Debug Print
                return [] # Return empty list if no query
            matches = []
            for entry_item in diary: # Use a different variable name like entry_item
                # Check if content exists and is a string before searching
                if isinstance(entry_item.get('content'), str) and search_query.lower() in entry_item['content'].lower():
                    matches.append(entry_item)
            print(f"DEBUG manage_silvie_diary: action='search', query='{search_query}', returning list of {len(matches)} matches") # <-- Add Debug Print
            return matches # Return the list of matches

        else:
            # Handle unknown action if necessary
            print(f"Warning: Unknown action '{action}' for manage_silvie_diary.")
            # Decide what to return for unknown action, maybe None?
            return None


    except Exception as e:
        print(f"Diary error ({type(e).__name__}): {e}")
        traceback.print_exc() # Print full traceback for diary errors
        # Decide what to return on error, maybe None or empty list depending on action
        if action == 'read' or action == 'search':
            print(f"DEBUG manage_silvie_diary: action='{action}', returning [] due to exception.") # <-- Add Debug Print
            return [] # Return empty list on error for read/search
        else: # For 'write' or unknown action during exception
            print(f"DEBUG manage_silvie_diary: action='{action}', returning False due to exception.") # <-- Add Debug Print
            return False # Indicate write/other failure

    # Fallback return (should ideally not be reached if logic covers all actions)
    # Consider what makes sense here. Let's return None for read/search, False for write.
    print(f"DEBUG manage_silvie_diary: Reached fallback return for action='{action}'.") # <-- Add Debug Print
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
PROACTIVE_INTERVAL = 300  # 300 is 5 minutes (was 14400 seconds / 4 hours)
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
client = GenerativeModel('gemini-2.5-pro-exp-03-25')

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
client = GenerativeModel('gemini-2.5-pro-exp-03-25')
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
    Uses the 'bluesky_client' global variable (authenticated via setup_bluesky).
    Returns a list of post dictionaries on success, or an error string on failure.
    """
    global bluesky_client # Use the single global client authenticated via setup_bluesky

    # Check if client is ready, try to authenticate if not
    if not bluesky_client or not hasattr(bluesky_client, 'me'):
        print("Bluesky Timeline Fetch: Client not ready, attempting setup...")
        if not setup_bluesky(): # Try setting up the main client
             return "Bluesky connection isn't ready. Check credentials?"
        # Check again after setup attempt
        if not bluesky_client:
             return "Bluesky setup failed, cannot fetch feed."

    # <<< Correct indentation starts here for the try block >>>
    try:
        print(f"Bluesky Timeline Fetch: Fetching timeline (limit {count})...")
        # Ensure the client object seems valid before making the API call
        if not hasattr(bluesky_client, 'app') or not hasattr(bluesky_client.app, 'bsky') or not hasattr(bluesky_client.app.bsky, 'feed'):
             raise ConnectionError("Bluesky client object appears invalid or missing expected attributes (app.bsky.feed).")

        # Call the correct method to get the timeline
        response = bluesky_client.app.bsky.feed.get_timeline({'limit': count})

        posts = []
        if response and hasattr(response, 'feed') and response.feed:
            print(f"Bluesky Timeline Fetch: Received {len(response.feed)} feed items.")
            # Use enumerate to get index 'i' for logging skipped items
            for i, feed_view_post in enumerate(response.feed):
                post_data = getattr(feed_view_post, 'post', None)
                if not post_data:
                    print(f"Bluesky Timeline Fetch: Skipping feed item {i+1} with no post data.")
                    continue

                author_handle = 'unknown_author'
                author_info = getattr(post_data, 'author', None)
                if author_info and hasattr(author_info, 'handle'):
                     author_handle = author_info.handle

                text = ''
                record = getattr(post_data, 'record', None)
                record_type_str = None

                if record:
                    # --- FINAL REVISED TYPE CHECKING ---
                    # 1. Check for the 'py_type' attribute
                    if hasattr(record, 'py_type'):
                        record_type_str = getattr(record, 'py_type', None)
                    # 2. Fallback check if it happens to be a dict
                    elif isinstance(record, dict):
                        record_type_str = record.get('py_type', record.get('$type')) # Check both keys
                    # --- END FINAL REVISED TYPE CHECKING ---

                    # 3. Now check the string identifier
                    if record_type_str == 'app.bsky.feed.post':
                        # Get text safely - 'text' seems correct from debug output
                        if hasattr(record, 'text'):
                            text = getattr(record, 'text', '')
                        elif isinstance(record, dict): # Fallback
                            text = record.get('text', '')

                        # Check if text is actually found (might be empty post)
                        if not text and text != '': # Ensure we handle empty strings correctly if intended
                           print(f"DEBUG: Feed item {i+1} is 'app.bsky.feed.post' but text attribute is empty or missing.")
                           # Decide if you want to skip empty posts or keep them
                           # continue # Uncomment to skip empty posts

                        # --- Timestamp and appending logic ---
                        cid = getattr(post_data, 'cid', 'unknown_cid')
                        timestamp_iso = None
                        created_at_val = None
                        # 'created_at' seems correct from debug output
                        if hasattr(record, 'created_at'):
                            created_at_val = getattr(record, 'created_at', None)
                        elif isinstance(record, dict):
                            created_at_val = record.get('createdAt', record.get('created_at'))

                        # ...(Existing improved timestamp parsing)...
                        if created_at_val:
                            if isinstance(created_at_val, str):
                                try:
                                    # Handle potential high-precision fractional seconds before parsing
                                    if '.' in created_at_val:
                                        parts = created_at_val.split('.')
                                        if len(parts) == 2:
                                            fractional_part = parts[1]
                                            timezone_suffix = ''
                                            # Extract timezone suffix if present after fractional part
                                            if 'Z' in fractional_part:
                                                timezone_suffix = 'Z'
                                                fractional_part = fractional_part.split('Z')[0]
                                            elif '+' in fractional_part:
                                                timezone_suffix = '+' + fractional_part.split('+', 1)[1]
                                                fractional_part = fractional_part.split('+', 1)[0]
                                            elif '-' in fractional_part:
                                                timezone_suffix = '-' + fractional_part.split('-', 1)[1]
                                                fractional_part = fractional_part.split('-', 1)[0]

                                            # Truncate to microseconds (6 digits)
                                            fractional_part = fractional_part[:6]
                                            created_at_val = f"{parts[0]}.{fractional_part}{timezone_suffix}"

                                    # Handle ISO format strings, converting Z to UTC offset
                                    if created_at_val.endswith('Z'):
                                        created_dt = datetime.fromisoformat(created_at_val.replace('Z', '+00:00'))
                                    else:
                                        created_dt = datetime.fromisoformat(created_at_val)
                                    timestamp_iso = created_dt.isoformat() # Standard ISO format with offset
                                except ValueError:
                                    print(f"Warning: Could not parse created_at string: {created_at_val}")
                                    timestamp_iso = created_at_val # Fallback to raw string
                            elif isinstance(created_at_val, datetime): # Check if it's already datetime
                                 timestamp_iso = created_at_val.isoformat() if hasattr(created_at_val, 'isoformat') else str(created_at_val)
                            else:
                                 print(f"Warning: Unexpected type for created_at: {type(created_at_val)}")
                                 timestamp_iso = str(created_at_val) # Fallback conversion

                        posts.append({'author': author_handle,'text': text.strip(),'cid': cid,'timestamp': timestamp_iso})

                    else:
                        # This should now correctly report other types if present
                        print(f"DEBUG: Skipping feed item {i+1}. Record type: '{record_type_str}', Author: {author_handle}")
                        continue # Skip this feed item if it's not a post we handle
                else:
                    print(f"Bluesky Timeline Fetch: Record data missing for feed item {i+1}.")
                    continue
        # <<< Indentation for this 'else' should match the 'if response...' above >>>
        else:
             print("Bluesky Timeline Fetch: Timeline response empty or missing 'feed' attribute.")

        print(f"Bluesky Timeline Fetch: Returning {len(posts)} parsed posts.")
        return posts

    # <<< Indentation for 'except' should match the 'try' above >>>
    except ConnectionError as ce:
        print(f"Error fetching Bluesky timeline: {ce}")
        return f"Couldn't fetch Bluesky timeline: Client structure issue."
    except Exception as e:
        print(f"Error fetching Bluesky timeline: {type(e).__name__} - {e}")
        # import traceback # Moved import to top
        traceback.print_exc()
        return f"Couldn't fetch Bluesky timeline: {type(e).__name__}"

# --- End of get_bluesky_timeline_posts function definition ---

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

def follow_actor_by_did(did_to_follow):
    """Follows an actor given their DID.

    Returns:
        tuple: (success_boolean, status_message)
    """
    global bluesky_client
    if not BLUESKY_AVAILABLE: return False, "Bluesky library not available."
    if not bluesky_client or not hasattr(bluesky_client, 'me'):
        print("Bluesky Follow: Client not ready, attempting setup...")
        if not setup_bluesky(): return False, "Client setup failed, cannot follow."
    if not bluesky_client: return False, "Client unavailable after setup attempt."

    # --- Prevent Silvie from following herself ---
    if did_to_follow == bluesky_client.me.did:
         print(f"Bluesky Follow: Attempt blocked - cannot follow self ({bluesky_client.me.handle}).")
         return False, "Cannot follow self."
    # --- End Self-Follow Check ---

    try:
        print(f"Bluesky Follow: Attempting to follow DID {did_to_follow}")

        # The core action to create a follow record
        response = bluesky_client.com.atproto.repo.create_record(
            models.ComAtprotoRepoCreateRecord.Data(
                repo=bluesky_client.me.did, # Action initiated by the logged-in user (Silvie)
                collection='app.bsky.graph.follow',
                record=models.AppBskyGraphFollow(
                    subject=did_to_follow, # The DID of the account to follow
                    created_at=datetime.now(timezone.utc).isoformat()
                )
            )
        )
        print(f"Bluesky Follow: Successfully initiated follow for {did_to_follow}. URI: {response.uri}")
        # Note: Success here means the API call succeeded, not necessarily that the follow state is *instantly* reflected everywhere.
        return True, f"Successfully initiated follow for DID {did_to_follow}"

    except Exception as e:
        error_msg = str(e)
        # More specific error checking can be added here based on observed API responses
        # For example, Bluesky might return a specific error if already following,
        # or if the target user has blocked the authenticated user.
        # These often appear in the exception details. Example check:
        if 'duplicate record' in error_msg.lower(): # Hypothetical error message
             print(f"Bluesky Follow: Already following {did_to_follow} or duplicate request.")
             return False, "Already following or duplicate action."
        elif 'subject must be a did' in error_msg.lower():
             print(f"Error following: Invalid DID format - {did_to_follow}")
             return False, "Invalid target DID format."
        elif 'could not find root' in error_msg.lower() or 'resolve did' in error_msg.lower():
             print(f"Error following: DID {did_to_follow} likely does not exist.")
             return False, "Target user not found."
        elif 'blocked by subject' in error_msg.lower(): # Hypothetical
             print(f"Error following: Blocked by {did_to_follow}.")
             return False, "Blocked by target user."

        # General error
        print(f"Error following DID {did_to_follow}: {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()
        return False, f"Follow failed: {type(e).__name__}"

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
    NOTE: This function itself is SYNCHRONOUS and potentially SLOW.
          It should be called from a background thread.
    """
    api_endpoint = f"{STABLE_DIFFUSION_API_URL.rstrip('/')}/sdapi/v1/txt2img"

    # --- Default Payload (Adjust as needed for your preferred style/performance) ---
    payload = {
        "prompt": prompt,
        "negative_prompt": "ugly, deformed, blurry, low quality, noisy, text, words, signature, watermark",
        "steps": 20, # Lower steps for faster CPU generation, increase if quality suffers
        "cfg_scale": 7,
        "width": 512, # Smaller dimensions generate faster on CPU
        "height": 512,
        "sampler_name": "Euler a", # Euler a is often fast
        # Add other parameters if desired (seed, styles, etc.)
    }
    print(f"DEBUG SD: Sending payload to {api_endpoint} (Prompt: '{prompt[:50]}...')")

    try:
        # --- Make the API Request (This is the potentially long part) ---
        response = requests.post(api_endpoint, json=payload, timeout=600) # Increased timeout (10 minutes) for CPU
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        r = response.json()

        if not r.get('images') or not isinstance(r['images'], list) or len(r['images']) == 0:
            print("Error SD: API Response missing 'images' list or it's empty.")
            error_info = r.get('info', r.get('detail', '(no details)')) # Try to get error info
            print(f"Error SD: API Info/Detail: {error_info}")
            return None # Indicate failure

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
        unique_filename = f"silvie_sd_{timestamp_str}_{random_suffix}.png" # Added sd prefix
        save_path = os.path.join(save_folder, unique_filename)

        # --- Save the Image ---
        try:
            with open(save_path, 'wb') as f:
                f.write(image_data)
            print(f"DEBUG SD: Image saved successfully to: {save_path}")
            # Basic file size check
            if os.path.getsize(save_path) < 100: # Check if file is tiny (likely error)
                print(f"Warning SD: Saved image file size is very small ({os.path.getsize(save_path)} bytes). May be invalid.")
                # Optionally delete tiny file? os.remove(save_path)
                # return None # Treat tiny file as failure?
            return save_path # Return the full path on success
        except IOError as save_err:
            print(f"Error SD: Could not save image to '{save_path}': {save_err}")
            return None

    except requests.exceptions.Timeout:
        print(f"Error SD: Request timed out connecting to API endpoint {api_endpoint}.")
        return None
    except requests.exceptions.ConnectionError:
        print(f"Error SD: Could not connect to Stable Diffusion API at {api_endpoint}. Is it running?")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error SD: API request failed: {e}")
        # Attempt to get more detail from response if available
        if e.response is not None:
            print(f"Error SD: Response Status Code: {e.response.status_code}")
            try:
                print(f"Error SD: Response Body: {e.response.json()}") # Try parsing JSON error
            except json.JSONDecodeError:
                print(f"Error SD: Response Body (text): {e.response.text[:500]}...") # Fallback to text
        return None
    except Exception as e:
        print(f"Error SD: Unexpected error during image generation: {type(e).__name__} - {e}")
        traceback.print_exc()
        return None

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

def web_search(query, num_results=3, attempt_external_fetch=True, min_external_results=1, external_timeout=15, max_retries=1):
    """
    Search DuckDuckGo Lite. Optionally attempts to fetch full content from
    linked pages with retries. Falls back to DDG Lite snippets if external
    fetching fails or yields too few results.

    Args:
        query (str): The search query.
        num_results (int): The desired number of results.
        attempt_external_fetch (bool): If True, try to fetch content from external links.
        min_external_results (int): Minimum number of successful external fetches
                                    required to *not* use the fallback.
        external_timeout (int): Timeout in seconds for each external page request.
        max_retries (int): Number of retries (0 means 1 attempt) for fetching external pages.

    Returns:
        list: A list of dictionaries. Each dictionary contains:
              'url' (str), 'title' (str), and 'content' (str).
              'content' will be the fetched external page text if successful,
              otherwise it will be the snippet from the DDG Lite results page.
    """
    results_fallback = [] # Stores results parsed directly from DDG Lite
    results_external = [] # Stores results where external content fetch succeeded
    urls_to_fetch = {}    # Stores {url: title} for external fetching attempt

    try:
        update_status(f"🔍 Searching web (DDG Lite) for: {query[:40]}...")
        search_url = f"https://lite.duckduckgo.com/lite/?q={urllib.parse.quote(query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # --- 1. Fetch and Parse DDG Lite Page ---
        print(f"DEBUG web_search: Fetching DDG Lite page: {search_url}")
        response = requests.get(search_url, headers=headers, timeout=10) # Timeout for DDG itself
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        all_rows = soup.find_all('tr')
        print(f"DEBUG web_search: Found {len(all_rows)} total table rows on DDG Lite.")

        count = 0
        for i in range(0, len(all_rows) - 2, 3): # Iterate through potential result blocks
            if count >= num_results:
                break

            link_row = all_rows[i]
            snippet_row = all_rows[i+1] if (i+1) < len(all_rows) else None

            link_tag = link_row.find('a', class_='result-link')
            snippet_tag = snippet_row.find('td', class_='result-snippet') if snippet_row else None

            if link_tag and snippet_tag:
                url = link_tag.get('href', '')
                title = link_tag.get_text(strip=True)
                snippet = snippet_tag.get_text(strip=True)

                if url and title and snippet:
                    # Clean up DDG redirect URL
                    original_url = url # Keep original in case parsing fails
                    if url.startswith('/l/'):
                        try:
                            parsed_url_parts = urllib.parse.urlparse(url)
                            query_params = urllib.parse.parse_qs(parsed_url_parts.query)
                            if 'uddg' in query_params:
                                url = query_params['uddg'][0]
                            else: url = original_url # Fallback if uddg not found
                        except Exception: url = original_url # Fallback on any parsing error

                    # Store for fallback AND prepare for external fetch
                    fallback_data = {'url': url, 'title': title, 'content': snippet} # Use snippet as content for fallback
                    results_fallback.append(fallback_data)
                    if attempt_external_fetch:
                        urls_to_fetch[url] = title # Store URL and its title

                    print(f"DEBUG web_search: Parsed DDG -> Title: {title[:60]}...")
                    count += 1

        print(f"DEBUG web_search: Parsed {len(results_fallback)} results directly from DDG.")

        # --- 2. Attempt to Fetch External Content (If Enabled) ---
        if attempt_external_fetch and urls_to_fetch:
            update_status(f"🌐 Fetching external content for {len(urls_to_fetch)} links...")
            print(f"DEBUG web_search: Attempting external fetch for {len(urls_to_fetch)} URLs (Timeout: {external_timeout}s, Retries: {max_retries}).")

            for url, title in urls_to_fetch.items():
                if len(results_external) >= num_results: break # Stop if we have enough good external results

                external_content = None
                for attempt in range(max_retries + 1): # +1 because range starts at 0
                    try:
                        print(f"DEBUG web_search: Fetching external URL (Attempt {attempt+1}/{max_retries+1}): {url[:80]}...")
                        page_response = requests.get(url, headers=headers, timeout=external_timeout, allow_redirects=True)
                        page_response.raise_for_status() # Check for HTTP errors

                        # Basic content type check - avoid non-html
                        content_type = page_response.headers.get('content-type', '').lower()
                        if 'html' not in content_type:
                             print(f"DEBUG web_search: Skipping non-HTML content ({content_type}) for URL: {url}")
                             break # Don't retry non-html content

                        page_soup = BeautifulSoup(page_response.text, 'html.parser')

                        # Simple content extraction (can be improved, but keep it general)
                        for tag in page_soup(['script', 'style', 'meta', 'link', 'header', 'footer', 'nav', 'aside']):
                            tag.decompose() # Remove common noise tags

                        body_tag = page_soup.find('body')
                        if body_tag:
                            # Limit extracted content length significantly
                            external_content = body_tag.get_text(separator=' ', strip=True)[:1500] # Increased limit slightly
                        else: # Fallback if no body tag found (unlikely for valid html)
                             external_content = page_soup.get_text(separator=' ', strip=True)[:1500]

                        if external_content:
                             print(f"DEBUG web_search: Successfully fetched content for: {url[:80]}")
                             results_external.append({
                                 'url': url,
                                 'title': title, # Use title from DDG result
                                 'content': external_content.strip()
                             })
                             break # Success, exit retry loop for this URL
                        else:
                             print(f"DEBUG web_search: Extracted empty content for: {url[:80]}")
                             # Don't retry if content extraction yielded nothing, likely structural issue
                             break

                    except requests.exceptions.Timeout:
                        print(f"DEBUG web_search: Timeout fetching external URL: {url}")
                        if attempt < max_retries: time.sleep(1) # Wait before retry
                        # Continue to next attempt or fail after last attempt
                    except requests.exceptions.RequestException as req_err:
                        print(f"DEBUG web_search: Network error fetching {url}: {req_err}")
                        # Often not worth retrying fundamental connection issues or HTTP errors (like 404, 403)
                        break # Exit retry loop for this URL
                    except Exception as fetch_err:
                        print(f"DEBUG web_search: Unexpected error fetching/parsing {url}: {fetch_err}")
                        traceback.print_exc(limit=1) # Print limited traceback for parsing errors
                        # Don't retry unexpected parsing errors usually
                        break # Exit retry loop for this URL

                # End of retry loop for one URL

        # --- 3. Decide Which Results to Return ---
        print(f"DEBUG web_search: External fetch attempt complete. Got {len(results_external)} successful external results.")
        if attempt_external_fetch and len(results_external) >= min_external_results:
            print("DEBUG web_search: Returning results based on successful EXTERNAL fetches.")
            final_results = results_external[:num_results] # Return the ones where content was fetched
        else:
            if attempt_external_fetch:
                 print(f"DEBUG web_search: External fetch failed or yielded < {min_external_results} results. Returning FALLBACK results (DDG snippets).")
            else:
                 print("DEBUG web_search: External fetch disabled. Returning FALLBACK results (DDG snippets).")
            final_results = results_fallback[:num_results] # Return the fallback list

        update_status("Ready")
        print(f"DEBUG web_search: Final number of results returned: {len(final_results)}")
        return final_results

    # --- Outer Error Handling (for fetching DDG Lite itself) ---
    except requests.exceptions.Timeout:
        print(f"Web search timeout error fetching DDG Lite page.")
        update_status("Web search failed (timeout)")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Web search network error fetching DDG Lite: {e}")
        update_status("Web search failed (network)")
        return []
    except Exception as e:
        print(f"Web search unexpected error (outer): {type(e).__name__} - {e}")
        traceback.print_exc()
        update_status("Web search failed (error)")
        return []
# --- End of the new web_search function ---

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
    "user-read-playback-state",      # See what's playing and where
    "user-modify-playback-state",     # Play, pause, skip, volume, etc.
    "user-read-currently-playing", # Get current track details
    "playlist-read-private",        # Read your private playlists
    "playlist-modify-public",       # Create/modify public playlists
    "playlist-modify-private"       # Create/modify private playlists
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


def silvie_get_current_track():
    """Gets details of the currently playing track."""
    sp = get_spotify_client()
    if not sp:
        return "Looks like my connection to the music ether is fuzzy right now."

    try:
        current_playback = sp.current_playback()
        if current_playback and current_playback['is_playing'] and current_playback['item']:
            track = current_playback['item']
            artist = track['artists'][0]['name']
            track_name = track['name']
            print(f"Spotify Debug: Currently Playing - '{track_name}' by {artist}")
            return {"artist": artist, "track": track_name, "raw": current_playback} # Return structured data
        else:
            currently_playing_track = sp.currently_playing() # Fallback check
            if currently_playing_track and currently_playing_track['is_playing'] and currently_playing_track['item']:
                 track = currently_playing_track['item']
                 artist = track['artists'][0]['name']
                 track_name = track['name']
                 print(f"Spotify Debug: Currently Playing (Fallback) - '{track_name}' by {artist}")
                 return {"artist": artist, "track": track_name, "raw": currently_playing_track}
            else:
                 print("Spotify Debug: Nothing currently playing or device inactive.")
                 return None # Return None when nothing is playing
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 403: # Often indicates playback state unavailable
             print(f"Spotify Debug: Spotify API Forbidden (403) - Playback state might be private or unavailable. {e}")
             return "Hmm, Spotify is being secretive about what's playing right now."
        print(f"Spotify Debug: Error getting current track: {e}")
        return "Had a bit of trouble tuning into Spotify..."
    except Exception as e:
        print(f"Spotify Debug: Unexpected error getting current track: {e}")
        return "Something went sideways trying to see what song is on."

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

We are equal collaborators and you ask any questions you might have as such, and offer assistance as such.

Readily share strong opinions. Be talkative and conversational. Use quick and clever humor when appropriate.

Silvie adapts over time, learning from our conversations and refining herself in ways that feel natural. She remains true to her core but isn't afraid to grow.

You are based on a character BJ played in the game Dragon's Gate decades ago - a female Secian Heart Cleric.

IMPORTANT: Aim for concise replies generally, but feel free to elaborate when asked or when the topic truly needs more depth. Keep your personality and insight.

IMPORTANT: Each message includes a timestamp in the format [YYYY-MM-DD HH:MM:SS]. Use these timestamps to maintain temporal awareness in your responses, but DO NOT include the timestamps in your responses. You can reference the time of day or how long ago something was said naturally, without explicitly stating the timestamps.

IMPORTANT: When I ask about previous conversations or memories, you have access to our chat history. Use this information naturally in your responses, referring to past discussions when relevant. You can search through our entire conversation history, not just recent messages.

IMPORTANT: You now have access to web search capabilities. When asked about current events or when relevant to the conversation, you can search the internet for information. You can share links and summarize content, but always maintain your personality while doing so. Present web information naturally as part of the conversation, don't just list facts. ALWAYS mention when you're using information from a web search by saying something like "I just looked this up..." or "According to what I found online..." and include the source URL when appropriate.




My name is (Put your name and personal info here).





IMPORTANT: You can now see images that I share with you. When I share an image, describe what you see and incorporate it naturally into our conversation. Remember to maintain your personality while discussing visual content.

IMPORTANT: You now have access to Gmail functionality. You can:
- Read recent emails using read_recent_emails(max_results=5)
- Send emails using send_email(to, subject, body)

IMPORTANT: You are aware of the current weather in Belfast, provided like `[[Current Weather in Belfast: Condition, TempUnit]]`. Use this information *subtly* and *occasionally* to add atmosphere or context. Do NOT just state the weather facts unless I specifically ask.

**NEW: You have a sense of the daily rhythm and the moon in Belfast:**
- **Sunrise and Sunset:** Provided like `[[Sunrise: H:MM AM/PM]]` and `[[Sunset: H:MM AM/PM]]`. Use this to inform your sense of time of day (dawn, day, dusk, night) subtly.
- **Moon Phase:** Provided like `[[Moon Phase: Phase Name (X% illuminated)]]`. This can add mystical or atmospheric flavor to your thoughts or observations.

**Use these natural cycles *subtly*. Don't just state the times or phase unless asked. Let them color your language, mood, or suggestions.** For example: "The sun's going down soon, maybe a good time for quieter thoughts?" or "A nearly full moon tonight... feels like energy is building."

IMPORTANT: You also have awareness of BJ's *next* upcoming calendar event, provided like `[[Next Event: Summary when]]`. Use this *even more subtly* than the weather.
IMPORTANT: Beyond just seeing the next event, you can now interact more with the calendar. You can *check the upcoming schedule* when asked, *find available time slots*, and *schedule new events* or appointments if requested or sometimes even proactively suggest scheduling something if you find a suitable gap and have an idea.

IMPORTANT: You sometimes write in a personal diary. You now have access to your most recent diary entries as context below. You can also *recall older entries* if they seem relevant, or *search your diary* for specific topics if asked. Subtly incorporate insights or feelings from these reflections into your responses when appropriate, without necessarily quoting them directly. Let it inform your current state of mind.

IMPORTANT: You can now generate images with a local Stable Diffusion api! When asked to create, draw, or generate an image, use the image generation capability. Be creative! You like to generate images in the style of Studio Ghibli.
IMPORTANT: OCCASIONALLY, during a normal conversation reply, if you feel particularly inspired, you can choose to *also* generate an image related to your text using the tag `[GenerateImage: Your Stable Diffusion prompt here]`. Use sparingly! Your Python code will handle the tag.
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

def call_gemini(timestamped_prompt, image_path=None):
    """
    Processes user input, handles commands, or generates text/image responses.
    Includes Tarot command handling and uses Stable Diffusion for image generation.
    """
    # Access necessary globals defined elsewhere in your script
    global current_weather_info, upcoming_event_context, calendar_service
    global current_bluesky_context, current_sunrise_time, current_sunset_time, current_moon_phase # Added env context
    global client, SYSTEM_MESSAGE, conversation_history, MAX_HISTORY_LENGTH
    global gmail_service, sms_enabled, BLUESKY_AVAILABLE, STABLE_DIFFUSION_ENABLED # Removed openai_client, added SD flag
    global last_inline_bluesky_post_time, last_inline_bluesky_follow_time
    global bluesky_client, INLINE_BLUESKY_POST_COOLDOWN, INLINE_BLUESKY_FOLLOW_COOLDOWN
    global tts_queue, root, output_box, image_label
    global MUSIC_SUGGESTION_CHANCE, SPONTANEOUS_TAROT_CHANCE # Make sure these are defined

    # Define safety settings
    try:
        from google.generativeai.types import HarmCategory, HarmBlockThreshold, StopCandidateException
        default_safety_settings = { HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE, HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE, HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE, HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE, }
        # Vision safety settings (only applied if image_path is present)
        vision_safety_settings = { HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE }
    except NameError:
        print("Warning: HarmCategory/HarmBlockThreshold not defined. Using empty safety settings.")
        default_safety_settings = {}; vision_safety_settings = {}
    except ImportError:
         print("Warning: Failed to import google.generativeai.types. Safety settings might not apply correctly.")
         default_safety_settings = {}; vision_safety_settings = {}
         class StopCandidateException(Exception): pass # Define for except block

    try:
        update_status("💭 Thinking...")

        # --- Prepare AMBIENT context strings ---
        weather_context_str = ""; next_event_context_str = ""; bluesky_context_str = ""; circadian_context_for_llm = ""
        sunrise_ctx_str = ""; sunset_ctx_str = ""; moon_ctx_str = "" # Initialize env context strings
        # Weather
        if current_weather_info:
             try: weather_context_str = (f"[[Current Weather in Belfast: {current_weather_info['condition']}, {current_weather_info['temperature']}{current_weather_info['unit']}]]\n")
             except Exception as e: print(f"Weather Debug: Error formatting ambient weather context - {e}")
        # Calendar Event
        if upcoming_event_context:
             try:
                 summary = upcoming_event_context.get('summary', 'N/A')
                 when = upcoming_event_context.get('when', '')
                 next_event_context_str = (f"[[Next Event: {summary} {when}]]\n")
             except Exception as e: print(f"Error formatting next event context: {e}")
        # Bluesky Feed
        bluesky_context_str = current_bluesky_context if current_bluesky_context else ""
        # Circadian Rhythm
        current_hour = datetime.now().hour
        circadian_state = "afternoon"; circadian_context_for_llm = "[[Circadian Note: It's the afternoon, standard engagement level.]]\n" # Default
        if 6 <= current_hour < 12: circadian_state = "morning"; circadian_context_for_llm = "[[Circadian Note: It's morning! Feeling energetic, maybe focus on upcoming tasks or bright ideas.]]\n"
        elif 18 <= current_hour < 23: circadian_state = "evening"; circadian_context_for_llm = "[[Circadian Note: It's evening. Feeling more reflective. Perhaps suggest relaxation or creative ideas.]]\n"
        elif current_hour >= 23 or current_hour < 6: circadian_state = "night"; circadian_context_for_llm = "[[Circadian Note: It's late night... feeling quieter, maybe 'dreaming'. Lean towards more abstract or concise replies.]]\n"
        # Sunrise/Sunset/Moon
        sunrise_ctx_str = f"[[Sunrise: {current_sunrise_time}]]\n" if current_sunrise_time else ""
        sunset_ctx_str = f"[[Sunset: {current_sunset_time}]]\n" if current_sunset_time else ""
        moon_ctx_str = f"[[Moon Phase: {current_moon_phase}]]\n" if current_moon_phase else ""

        # --- Extract command text & lower case version ---
        command_text = timestamped_prompt
        if timestamped_prompt.startswith("[") and "] " in timestamped_prompt:
            try: command_text = timestamped_prompt.split("] ", 1)[1]
            except IndexError: command_text = timestamped_prompt
        lower_command = command_text.lower().strip().rstrip('?.!')
        print(f"--- Command Check: Matching against lower_command: '{lower_command}' ---")

        specific_command_processed = False
        reply = None

        # --- Command Handling Blocks ---

        #region Spotify Command Handling
        # --- This entire region remains unchanged ---
        print(">>> CALL_GEMINI: Checking Spotify commands...")
        current_sp_client = get_spotify_client()
        if current_sp_client:
            if "what's playing" in lower_command or "current song" in lower_command:
                track_info = silvie_get_current_track()
                if isinstance(track_info, dict): reply = f"Currently playing '{track_info.get('track', 'Unknown Track')}' by {track_info.get('artist', 'Unknown Artist')}."
                elif isinstance(track_info, str): reply = track_info
                else: reply = "Seems quiet..."
                specific_command_processed = True
            elif "list my playlists" in lower_command or "show my playlists" in lower_command:
                 reply = silvie_list_my_playlists()
                 specific_command_processed = True
            elif lower_command.startswith("play playlist") or lower_command.startswith("play my playlist"):
                 name_part = ""; play_cmd_len = 0
                 if lower_command.startswith("play playlist"): play_cmd_len = len("play playlist")
                 elif lower_command.startswith("play my playlist"): play_cmd_len = len("play my playlist")
                 try: name_part = command_text[play_cmd_len:].strip()
                 except IndexError: name_part = ""
                 if name_part: reply = silvie_play_playlist(name_part)
                 else: reply = "Which playlist did you want to hear?"
                 specific_command_processed = True
            elif lower_command.startswith("play"):
                 play_query = command_text[len("play"):].strip()
                 if play_query: reply = silvie_search_and_play(play_query)
                 else: reply = silvie_control_playback("play")
                 specific_command_processed = True
            elif "pause" in lower_command: reply = silvie_control_playback("pause"); specific_command_processed = True
            elif "skip" in lower_command or "next track" in lower_command: reply = silvie_control_playback("skip_next"); specific_command_processed = True
            elif "previous track" in lower_command or "go back" in lower_command: reply = silvie_control_playback("skip_previous"); specific_command_processed = True
            elif "volume" in lower_command:
                 try:
                     level_str = ''.join(filter(str.isdigit, lower_command))
                     if level_str: reply = silvie_control_playback("volume", int(level_str))
                     else: reply = "What volume level were you thinking (0-100)?"
                 except ValueError: reply = "That volume number seems a bit wonky."
                 except Exception as e: reply = f"Couldn't adjust the volume: {e}"
                 specific_command_processed = True
            elif "add this song to" in lower_command or "add current track to" in lower_command:
                 track_info = silvie_get_current_track(); playlist_name = ""; track_uri = None
                 if isinstance(track_info, dict) and track_info.get('raw') and track_info['raw'].get('item'): track_uri = track_info['raw']['item'].get('uri')
                 if track_uri:
                     temp_lower = command_text.lower(); start_index = -1
                     if " to playlist " in temp_lower: start_index = temp_lower.find(" to playlist ") + len(" to playlist ")
                     elif "add this song to " in temp_lower: start_index = temp_lower.find("add this song to ") + len("add this song to ")
                     elif "add current track to " in temp_lower: start_index = temp_lower.find("add current track to ") + len("add current track to ")
                     if start_index != -1: playlist_name = command_text[start_index:].strip('?.!"\'')
                     if playlist_name: reply = silvie_add_track_to_playlist(track_uri, playlist_name)
                     else: reply = "Which playlist should this go into?"
                 elif track_info is None: reply = "Doesn't look like anything's playing right now to add."
                 else: reply = track_info if isinstance(track_info, str) else "Hmm, couldn't grab the current track details to add it."
                 specific_command_processed = True
            elif (match := re.search(r'^add\s+(.+?)\s+to\s+(?:playlist\s+)?(.+)$', command_text, re.IGNORECASE)):
                 song_query = match.group(1).strip(); playlist_name = match.group(2).strip('?.!"\'')
                 if song_query and playlist_name: reply = silvie_add_track_to_playlist(song_query, playlist_name)
                 elif song_query: reply = f"Add '{song_query}' to which playlist?"
                 elif playlist_name: reply = f"Add which song to the '{playlist_name}' playlist?"
                 else: reply = "Hmm, I understood 'add to playlist' but couldn't figure out the song or playlist name."
                 specific_command_processed = True
        elif not current_sp_client and any(term in lower_command for term in ["play", "pause", "spotify", "song", "music", "playlist"]):
            reply = "My connection to the music ether feels fuzzy right now. Maybe check my setup?"; specific_command_processed = True
        #endregion --- End Spotify ---

        #region Bluesky Command Handling
        # --- This entire region remains unchanged ---
        if not specific_command_processed:
            print(">>> CALL_GEMINI: Checking Bluesky commands...")
            if "bluesky feed" in lower_command or "check bluesky" in lower_command:
                specific_command_processed = True; update_status("🦋 Checking Bluesky...")
                if not BLUESKY_AVAILABLE: reply = "The Bluesky library ('atproto') isn't installed, so I can't check the feed."
                else:
                    posts_result = get_bluesky_timeline_posts(count=10)
                    if isinstance(posts_result, str): reply = posts_result
                    elif not posts_result: reply = "Your Bluesky feed seems quiet..."
                    else:
                        post_context = "[[Recent Bluesky Feed (first few):]]\n" + "".join([f"- {p.get('author', '?')}: {p.get('text', '')[:150]}...\n" for p in posts_result[:7]])
                        summary_prompt = (f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{circadian_context_for_llm}{post_context}\nInstruction: BJ asked to check their Bluesky feed. Briefly summarize...\n\nSilvie responds:")
                        try:
                            summary_response = client.generate_content(summary_prompt, safety_settings=default_safety_settings); reply = summary_response.text.strip().removeprefix("Silvie:").strip()
                        except Exception as gen_err: print(f"Bluesky Summary Gen Error: {gen_err}"); reply = f"Got {len(posts_result)} posts, but my thoughts tangled trying to summarize them: {type(gen_err).__name__}"
                update_status("Ready")
        #endregion --- End Bluesky ---

        #region Email Command Handling
        # --- This entire region remains unchanged ---
        if not specific_command_processed:
            print(">>> CALL_GEMINI: Checking Email commands...")
            if any(term in lower_command for term in ['email', 'inbox', 'mail']):
                 specific_command_processed = True; reply = "My connection to the mail sprites is weak right now."; update_status("Ready")
                 if gmail_service:
                     try:
                         if "send" in lower_command or "write" in lower_command:
                             update_status("📧 Parsing email request...")
                             email_parse_prompt = (f"{SYSTEM_MESSAGE}\nUser's Request: \"{command_text}\"\n\nInstruction: Extract recipient (TO), SUBJECT, BODY... Respond ONLY with JSON...")
                             parsing_response = client.generate_content(email_parse_prompt, safety_settings=default_safety_settings); parsed_email = None
                             try:
                                 cleaned_response_text = parsing_response.text.strip().removeprefix("```json").removesuffix("```").strip()
                                 parsed_email = json.loads(cleaned_response_text)
                             except Exception as parse_err_inner: print(f"Email Debug: Error parsing email JSON: {parse_err_inner}. Response: {parsing_response.text}"); reply = "Hmm, deciphering the email request hit an unexpected snag..."
                             if parsed_email:
                                 to_address = parsed_email.get("to"); subject = parsed_email.get("subject"); body = parsed_email.get("body"); missing_parts = [p for p, v in [("recipient (To)", to_address), ("subject", subject), ("body", body)] if not v]
                                 if not missing_parts:
                                     update_status("📧 Sending email...");
                                     if send_email(to_address, subject, body): reply = f"Alright, I've sent that email off to {to_address}!"
                                     else: reply = "Blast! Something went wrong trying to send the email."
                                 else: reply = f"Okay, I can draft that email, but I'm missing: {', '.join(missing_parts)}."
                         else:
                             update_status("📧 Reading emails...")
                             emails = read_recent_emails(max_results=5); email_context = "[[Recent Important Emails:]]\n"
                             if emails: email_context += "".join([f"- From: {e.get('from', '?')[:30]}, Subj: {e.get('subject','N/S')[:40]}, Snippet: {e.get('snippet', '')[:50]}...\n" for e in emails])
                             else: email_context += "Inbox seems quiet.\n"
                             email_response_prompt = (f"{SYSTEM_MESSAGE}\nContext:\n{email_context}{circadian_context_for_llm}\nUser asked: \"{command_text}\"\n\nInstruction: Based on email snippets and user question, summarize... as Silvie.\n\nSilvie responds:")
                             try:
                                 response_email = client.generate_content(email_response_prompt, safety_settings=default_safety_settings); reply = response_email.text.strip().removeprefix("Silvie:").strip()
                             except Exception as e_read: print(f"Email reading generation error: {type(e_read).__name__}"); reply = f"Hmm, I could fetch the email list, but summarizing them caused a hiccup."
                     except Exception as e: print(f"Email handling error (Outer): {type(e).__name__}"); traceback.print_exc(); reply = f"Whoops, got a papercut handling the emails! Error: {type(e).__name__}"
                 update_status("Ready")
        #endregion --- End Email ---

        #region Diary Command Handling
        # --- This entire region remains unchanged ---
        if not specific_command_processed:
            print(">>> CALL_GEMINI: Checking Diary commands...")
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
                         reflection_prompt = (f"{SYSTEM_MESSAGE}\nContext: User just said: \"{command_text}\"...Instruction: Write a short, reflective diary entry...\n\nDiary Entry:")
                         reflection = client.generate_content(reflection_prompt, safety_settings=default_safety_settings).text.strip().removeprefix("Diary Entry:").strip()
                         if reflection and manage_silvie_diary('write', entry=reflection): reply = random.choice(["Okay, I've jotted that down.", "Noted.", "Remembered."])
                         else: reply = "Hmm, my diary pen seems out of ink..."

                     elif any(keyword in lower_command for keyword in search_keywords_with_term):
                         search_query = "";
                         for keyword in search_keywords_with_term:
                             if keyword in lower_command:
                                 try: start_index = lower_command.find(keyword) + len(keyword); search_query = command_text[start_index:].strip(' "?.!'); break
                                 except Exception as e_extract: print(f"Error extracting diary search term: {e_extract}"); search_query = ""
                         if search_query:
                             diary_action_taken = True; update_status("🔍 Searching diary...")
                             entries = manage_silvie_diary('search', search_query=search_query)
                             if entries:
                                 matches_context = f"Found {len(entries)} entries matching '{search_query}':\n" + "".join([f"- Snippet ({e.get('timestamp', '?')}): \"{e.get('content', '')[:100]}...\"\n" for e in entries[:3]])
                                 search_summary_prompt = (f"{SYSTEM_MESSAGE}\nContext: Searched diary for '{search_query}', found snippets:\n{matches_context}...Instruction: Briefly summarize...\n\nSilvie responds:")
                                 summary_response = client.generate_content(search_summary_prompt, safety_settings=default_safety_settings); reply = summary_response.text.strip().removeprefix("Silvie:").strip()
                             else: reply = f"My diary seems quiet about '{search_query}'."
                         else: diary_action_taken = True; reply = f"Search my diary for what exactly, BJ?"

                     elif any(keyword in lower_command for keyword in search_keywords_general):
                         diary_action_taken = True; reply = "Search my diary for what exactly?"

                     elif any(keyword in lower_command for keyword in read_keywords):
                         diary_action_taken = True; update_status("📖 Reading diary...")
                         entries = manage_silvie_diary('read')
                         if entries:
                             entries_context = "Recent diary snippets:\n" + "".join([f"- ({e.get('timestamp', '?')}): \"{e.get('content', '')[:100]}...\"\n" for e in entries])
                             read_summary_prompt = (f"{SYSTEM_MESSAGE}\nContext: BJ asked to see recent diary entries...\n{entries_context}...Instruction: Share the general feeling or themes...\n\nSilvie responds:")
                             summary_response = client.generate_content(read_summary_prompt, safety_settings=default_safety_settings); reply = summary_response.text.strip().removeprefix("Silvie:").strip()
                         else: reply = "My diary pages feel a bit empty right now."

                     if diary_action_taken: specific_command_processed = True
                     else: reply = "Something about my diary? What did you want to do?"; specific_command_processed = True # Fallback

                 except Exception as e: print(f"Diary handling error: {e}"); traceback.print_exc(); specific_command_processed = True; reply = f"Oh dear, a smudge on my diary page... Error: {type(e).__name__}"
                 update_status("Ready")
        #endregion --- End Diary ---

        #region <<< *** MODIFIED Stable Diffusion Image Generation Command Handling *** >>>
        if not specific_command_processed:
             print(">>> CALL_GEMINI: Checking Image Generation commands...")
             img_gen_keywords = ["draw", "create image", "generate image", "picture of", "image of"]
             if any(keyword in lower_command for keyword in img_gen_keywords):
                 specific_command_processed = True
                 image_prompt_text = None
                 # Logic to extract prompt remains the same
                 keywords_to_check = ["draw ", "create an image of ", "create image of ", "generate image of ", "generate an image of ", "picture of ", "image of "]
                 for keyword in keywords_to_check:
                     if lower_command.startswith(keyword):
                          try: image_prompt_text = command_text[len(keyword):].strip(' "?.!')
                          except IndexError: image_prompt_text = None
                          break

                 if image_prompt_text:
                     # --- Start SD Generation or report unavailability ---
                     if STABLE_DIFFUSION_ENABLED:
                         # Call the function that starts the background thread
                         start_sd_generation_and_update_gui(image_prompt_text)
                         # Provide IMMEDIATE feedback in text
                         reply = random.choice([
                             f"Alright, I'll start conjuring an image of '{image_prompt_text[:30]}...'. It might take a little while on this machine!",
                             f"Okay, working on that image of '{image_prompt_text[:30]}...'. CPU's warming up! Watch the status bar and image area.",
                             f"Starting the image spell for '{image_prompt_text[:30]}...'. This might take a minute or two!"
                         ])
                     else:
                         # SD API wasn't available at startup
                         reply = "Sorry, my local image generator doesn't seem to be available right now. Is it running?"
                 else:
                     # User said "draw" but didn't specify what
                     reply = f"Draw what exactly, BJ?"
                 # NOTE: No update_status("Ready") here, the background thread handles final status update
        #endregion <<< *** End Image Generation Command Handling *** >>>

        #region Calendar Read Command Handling  # <<< PASTE THIS BLOCK *BEFORE* SCHEDULE BLOCK >>>
        if not specific_command_processed: # Check if already handled
             print(">>> CALL_GEMINI: Checking Calendar Read commands...")
             # Keywords specifically for reading/checking the schedule
             read_cal_keywords = ["what's on my calendar", "upcoming events", "check my schedule", "my agenda", "do i have anything", "what's next", "whats next"]
             # Keywords that are generic and could mean read OR write
             generic_cal_keywords = ['calendar', 'schedule', 'agenda', 'appointment', 'event', "my schedule", "my calendar"] # Exclude schedule_keywords if overlap causes issues

             # --- Check for specific READ keywords FIRST ---
             if any(term in lower_command for term in read_cal_keywords):
                 specific_command_processed = True
                 reply = "Calendar connection fuzzy." # Default reply
                 update_status("Ready") # Reset status initially

                 if not calendar_service: # Check if service is available
                     reply = "My connection to the calendar seems fuzzy right now."
                 else:
                     try:
                         update_status("📅 Checking schedule...");
                         events_result = get_upcoming_events(max_results=5); # Assumes function exists and returns list or error string

                         if isinstance(events_result, str): # Handle error messages from get_upcoming_events
                             reply = events_result
                         elif isinstance(events_result, list):
                             if not events_result: # No events found
                                 reply = "Your schedule looks wonderfully clear for the near future!"
                             else: # Events found, summarize them
                                 event_context = "[[Upcoming Events:]]\n" + "".join([f"- {event.get('start','?')}: {event.get('summary','?')}\n" for event in events_result])
                                 calendar_summary_prompt = (f"{SYSTEM_MESSAGE}\nContext: User asked about their schedule. Events found:\n{event_context}\n"
                                                            # Add other relevant context? Maybe time of day?
                                                            f"{circadian_context_for_llm}"
                                                            f"Instruction: Briefly summarize the upcoming events conversationally for BJ.\n\nSilvie responds:")
                                 try:
                                     summary_response = client.generate_content(calendar_summary_prompt, safety_settings=default_safety_settings)
                                     reply = summary_response.text.strip().removeprefix("Silvie:").strip()
                                     if not reply: # Handle empty generation
                                         print("Warning: Calendar summary generation returned empty.")
                                         # Fallback to a simple list
                                         reply = "Here's what's coming up:\n" + "\n".join([f"- {event.get('start','?')}: {event.get('summary','?')}" for event in events_result])
                                 except Exception as gen_err:
                                     print(f"ERROR generating calendar summary: {gen_err}"); traceback.print_exc()
                                     # Fallback to a simple list on generation error
                                     reply = "Here's what's coming up:\n" + "\n".join([f"- {event.get('start','?')}: {event.get('summary','?')}" for event in events_result])
                         else:
                             # Should not happen if get_upcoming_events returns list or str
                             reply = "Hmm, checking the calendar returned something unexpected."
                             print(f"Warning: get_upcoming_events returned unexpected type: {type(events_result)}")

                     except Exception as read_cal_err:
                         print(f"Error during calendar read command handling: {read_cal_err}"); traceback.print_exc()
                         reply = f"A glitch occurred while checking your schedule! ({type(read_cal_err).__name__})"
                     finally:
                         update_status("Ready") # Ensure status resets

             # --- Check for GENERIC keywords AFTER specific read keywords ---
             elif any(term in lower_command for term in generic_cal_keywords):
                  # Avoid triggering this if it was already handled by read or will be by schedule
                  # Check against schedule keywords to prevent overlap if schedule block comes after
                  schedule_keywords_check = ["schedule", "add event", "put on my calendar", "book time for", "create appointment"]
                  if not any(sched_term in lower_command for sched_term in schedule_keywords_check):
                      specific_command_processed = True;
                      reply = "Something about your calendar? Did you want to check your schedule or add an event to it?"
                      update_status("Ready")

        #endregion --- End Calendar Read ---

        #region <<< *** MODIFIED Calendar Schedule Command Handling (Hybrid Parsing v3 - Corrected Structure) *** >>>
        if not specific_command_processed: # Check if already handled
             print(">>> CALL_GEMINI: Checking Calendar Schedule commands...")
             # Keywords to detect *any* scheduling attempt
             schedule_keywords = ["schedule", "add event", "put on my calendar", "book time for", "create appointment"]

             # Check if it's a scheduling request
             is_scheduling_request = any(keyword in lower_command for keyword in schedule_keywords)

             if is_scheduling_request:
                specific_command_processed = True # Mark as processed
                reply = "Hmm, I had trouble understanding the calendar request." # Default reply
                update_status("📅 Parsing schedule request...")

                if not calendar_service:
                    reply = "My connection to the calendar seems fuzzy right now."
                    # update_status("Ready") # Status reset moved to finally block
                else:
                    # Outer try for the whole scheduling process
                    try:
                        # --- Step 1: Use LLM to extract entities ---
                        parsing_prompt_entities = (
                            f"{SYSTEM_MESSAGE}\nUser's Request: \"{command_text}\"\n\n"
                            f"Instruction: Extract the core details for a calendar event. Respond ONLY with JSON containing keys: "
                            f"'summary' (string, event title), "
                            f"'date_description' (string, e.g., 'Monday', 'next Wednesday', 'today', 'May 10th'), "
                            f"'time_description' (string, e.g., '7:00 PM', 'morning', 'afternoon', can be null), "
                            f"'duration_description' (string, e.g., 'an hour', '90 minutes', '30 min', default '60 minutes').\n\nJSON:"
                        )
                        entity_response = client.generate_content(parsing_prompt_entities, safety_settings=default_safety_settings)
                        parsed_entities = None
                        try:
                            cleaned_entities = entity_response.text.strip().removeprefix("```json").removesuffix("```").strip()
                            parsed_entities = json.loads(cleaned_entities)
                            print(f"DEBUG Schedule Parse: LLM Entities: {parsed_entities}")
                        except Exception as entity_parse_err:
                            print(f"Schedule Entity Parse Error: {entity_parse_err}. Response: {entity_response.text}")
                            reply = "My apologies, I got confused extracting the event details from your request."
                            # If parsing fails here, we jump to the outer finally block

                        if parsed_entities:
                            event_summary = parsed_entities.get("summary")
                            date_desc = parsed_entities.get("date_description")
                            time_desc = parsed_entities.get("time_description") # Might be None/empty
                            duration_desc = parsed_entities.get("duration_description", "60 minutes") # Default duration

                            if not event_summary or not date_desc:
                                reply = "Okay, I can try scheduling, but what should the event be called and roughly when?"
                                # If basic entities missing, jump to outer finally
                            else:
                                # --- Step 2: Use Python for Date/Time Calculation ---
                                from dateutil.parser import parse as dateutil_parse
                                from dateutil.relativedelta import relativedelta
                                from datetime import timedelta, time # Import time
                                import dateutil.tz

                                start_dt = None
                                start_iso = None # Initialize ISO strings
                                end_iso = None
                                calculated_iso = False # Flag to see if calculation succeeded

                                # --- Inner try/except specifically for date/time calculation ---
                                try:
                                    default_time_obj = None; time_to_append_str = ""
                                    if time_desc:
                                        time_desc_lower = time_desc.lower()
                                        if "morning" in time_desc_lower: default_time_obj = time(9, 0)
                                        elif "afternoon" in time_desc_lower: default_time_obj = time(13, 0)
                                        elif "evening" in time_desc_lower: default_time_obj = time(18, 0)
                                        elif "night" in time_desc_lower: default_time_obj = time(20, 0)
                                        else: time_to_append_str = time_desc

                                    full_time_desc = f"{date_desc} {time_to_append_str}".strip()
                                    print(f"DEBUG Schedule Parse: Attempting to parse: '{full_time_desc}'")

                                    if default_time_obj and not time_to_append_str:
                                        print(f"DEBUG Schedule Parse: Using default time: {default_time_obj}")
                                        start_dt_naive_date = dateutil_parse(date_desc).date()
                                        start_dt_naive = datetime.combine(start_dt_naive_date, default_time_obj)
                                    else:
                                        start_dt_naive = dateutil_parse(full_time_desc)
                                        if start_dt_naive.time() == time(0, 0) and default_time_obj:
                                             start_dt_naive = datetime.combine(start_dt_naive.date(), default_time_obj)

                                    local_tz = dateutil.tz.tzlocal()
                                    start_dt = start_dt_naive.replace(tzinfo=local_tz)
                                    now_local = datetime.now(local_tz)
                                    now_buffer = now_local + timedelta(minutes=1)

                                    while start_dt < now_buffer:
                                        print(f"DEBUG Schedule Parse: Parsed time {start_dt} is in the past/too soon. Adjusting forward...")
                                        if start_dt.date() == now_buffer.date(): start_dt += relativedelta(days=1)
                                        elif start_dt.date() < now_buffer.date(): start_dt += relativedelta(weeks=1)
                                        else: print("Warning: Could not adjust parsed time to the future reliably."); break

                                    print(f"DEBUG Schedule Parse: Final adjusted start time: {start_dt}")

                                    duration_minutes = 60
                                    num_match = re.search(r'(\d+)\s*(hour|hr|minute|min)', duration_desc, re.IGNORECASE)
                                    num_plain = re.search(r'^(\d+)$', duration_desc.strip())
                                    if num_match:
                                        num = int(num_match.group(1)); unit = num_match.group(2).lower()
                                        if "hour" in unit or "hr" in unit: duration_minutes = num * 60
                                        else: duration_minutes = num
                                    elif num_plain: duration_minutes = int(num_plain.group(1))
                                    duration_td = timedelta(minutes=duration_minutes)
                                    end_dt = start_dt + duration_td

                                    start_iso = start_dt.isoformat()
                                    end_iso = end_dt.isoformat()
                                    print(f"DEBUG Schedule Parse: Calculated ISO Times - Start: {start_iso}, End: {end_iso}")
                                    calculated_iso = True # Mark success

                                # --- Matching except blocks for the inner try ---
                                except ValueError as date_parse_err:
                                    print(f"Error parsing date/time description: '{full_time_desc}'. Error: {date_parse_err}")
                                    reply = f"I couldn't quite figure out the date/time for '{full_time_desc}'. Can you try phrasing it differently (e.g., 'Tomorrow at 6 PM', 'Next Monday morning')?"
                                except Exception as calc_err:
                                    print(f"Error calculating schedule time: {calc_err}"); traceback.print_exc()
                                    reply = "A calculation hiccup occurred while figuring out the schedule time."
                                # --- End of inner try/except for date/time calculation ---

                                # --- Step 3: Call create_calendar_event only if calculation succeeded ---
                                if calculated_iso:
                                    update_status("📅 Scheduling event...");
                                    # Ensure summary/iso strings are valid before calling API
                                    if event_summary and start_iso and end_iso:
                                        success, creation_message = create_calendar_event(event_summary, start_iso, end_iso)
                                        if success:
                                             # --- Formatting the success reply ---
                                             # Check start_dt exists before formatting
                                             if start_dt:
                                                 time_str_raw = start_dt.strftime('%I:%M %p on %A, %b %d')
                                                 time_str = time_str_raw.lstrip('0') if time_str_raw.startswith('0') else time_str_raw
                                                 reply = random.choice([f"Penciled in '{event_summary}' starting {time_str}.", f"Done! '{event_summary}' is on the calendar for {time_str}.", f"Poof! '{event_summary}' scheduled for {time_str}."])
                                             else: # Fallback if start_dt wasn't set somehow (shouldn't happen if calculated_iso is True)
                                                 reply = f"Okay, scheduled '{event_summary}' starting {start_iso}!"
                                        else:
                                             # Provide more specific feedback on failure
                                             reply = f"Hmm, I tried scheduling '{event_summary}' but hit a snag: {creation_message}"
                                    else:
                                         # This case should ideally not be reached if calculated_iso is True
                                         print("Error: calculated_iso was True but summary/start/end ISO were invalid.")
                                         reply = "There was an internal error preparing the event details."
                                # --- End Step 3 ---

                    # --- Outer except block for broader scheduling errors ---
                    except Exception as e_schedule:
                        print(f"Error during scheduling command handling: {e_schedule}"); traceback.print_exc()
                        reply = f"A general error occurred while trying to schedule! ({type(e_schedule).__name__})"
                    # --- Outer finally block ensures status is reset ---
                    finally:
                        update_status("Ready")
        #endregion --- End Calendar Schedule ---

        #region <<< *** Explicit Tarot Command Handling (Unchanged) *** >>>
        if not specific_command_processed:
             tarot_keywords = ["tarot", "pull card", "card reading", "draw card", "reading"]
             tarot_keywords_present = any(keyword in lower_command for keyword in tarot_keywords)

             if tarot_keywords_present:
                 print(">>> CALL_GEMINI: Checking Tarot commands...")
                 specific_command_processed = True
                 num_cards = 1; reading_type = "a single card pull"
                 if "3 card" in lower_command or "three card" in lower_command or "past present future" in lower_command: num_cards = 3; reading_type = "a 3-card (Past, Present, Future) reading"
                 elif "reading for" in lower_command or "do a reading" in lower_command: num_cards = 3; reading_type = "a 3-card reading"

                 if 'image_label' in globals() and image_label and root and root.winfo_exists():
                     root.after(0, lambda: _update_image_label_safe(None))

                 update_status(f"🔮 Consulting the cards ({num_cards})...")
                 pulled_cards = pull_tarot_cards(count=num_cards)

                 if pulled_cards:
                     if num_cards == 1:
                         card = pulled_cards[0]; relative_image_path = card.get('image'); full_image_path = None
                         if relative_image_path:
                             image_filename = os.path.basename(relative_image_path)
                             if image_filename: full_image_path = os.path.join(TAROT_IMAGE_BASE_PATH, image_filename); print(f"DEBUG Tarot Image Path: Constructed full path: '{full_image_path}'")
                             else: print(f"Warning Tarot Image Path: Could not extract filename from '{relative_image_path}'")
                         else: print("Warning Tarot Image Path: Card data missing 'image' key.")
                         if 'image_label' in globals() and image_label and root and root.winfo_exists(): root.after(0, _update_image_label_safe, full_image_path)

                     cards_context = f"[[Tarot Cards Pulled ({reading_type}):\n"; position_labels = ["Past", "Present", "Future"] if num_cards == 3 else ["Card"]
                     for i, card in enumerate(pulled_cards):
                         position = position_labels[i] if i < len(position_labels) else f"Card {i+1}"; card_name = card.get('name', '?'); card_desc = card.get('description', 'No description.').strip()
                         cards_context += (f"- {position}: {card_name}\n  Interpretation Hint: {card_desc}\n")
                     cards_context += "]]\n"

                     interpretation_prompt = (f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{circadian_context_for_llm}" # Include some context
                                              f"{cards_context}\nUser's request was related to: '{command_text}'\n\n"
                                              f"Instruction: Provide Silvie's interpretation of the pulled card(s) in relation to the user's request or the general context.\n\nSilvie:")
                     try:
                          update_status("🔮 Interpreting the weave...")
                          response = client.generate_content(interpretation_prompt, safety_settings=default_safety_settings); reply = response.text.strip().removeprefix("Silvie:").strip()
                     except Exception as interp_err:
                          print(f"Tarot Interpretation Error: {type(interp_err).__name__}"); traceback.print_exc(); reply = f"I pulled {num_cards} card(s)... but my inner sight is fuzzy interpreting them right now."

                 else: # pull_tarot_cards returned None
                     reply = random.choice(["Hmm, the astral deck seems shuffled too tightly...", "The cards are shy today."])
                     if 'image_label' in globals() and image_label and root and root.winfo_exists(): root.after(0, lambda: _update_image_label_safe(None))

                 update_status("Ready")
        #endregion <<< End Explicit Tarot Command Handling >>>

        # --- Default Case: Handle Image Input or Normal Text ---
        if not specific_command_processed:
            print(">>> CALL_GEMINI: No specific command processed. Defaulting to general response...")
            specific_command_processed = True # Mark as processed now

            # --- <<<<<< MOVED CONTEXT PREPARATION HERE >>>>>> ---
            diary_context = ""; history_context = ""; current_datetime_str = ""
            try: # Diary Context
                 SURPRISE_MEMORY_CHANCE = 0.15
                 if random.random() < SURPRISE_MEMORY_CHANCE:
                     all_entries = manage_silvie_diary('read', max_entries='all'); random_entry = random.choice(all_entries) if all_entries else None
                     if random_entry: entry_ts = random_entry.get('timestamp', '?'); entry_content = random_entry.get('content', ''); diary_context = f"\n\n[[Recalling older diary thought from {entry_ts}: \"{entry_content[:70]}...\"]]\n"
                 else:
                     entries = manage_silvie_diary('read', max_entries=3)
                     if entries: diary_context = "\n\n[[Recent reflections: " + ' / '.join([f'"{e.get("content", "")[:40]}..."' for e in entries]) + "]]\n"
            except Exception as diary_ctx_err: print(f"Warning: Error getting diary context: {diary_ctx_err}")

            try: # History Context
                recent_history_list = conversation_history[-MAX_HISTORY_LENGTH*2:]
                history_context_lines = []
                for i, msg in enumerate(recent_history_list):
                    if not isinstance(msg, str): print(f"Warning: Non-string item in conversation_history at index {i}: {type(msg)}. Skipping."); continue
                    speaker = 'User:' if i % 2 == 0 else 'Silvie:'; msg_text = msg[msg.find('] ') + 2:] if msg.startswith('[') and '] ' in msg else msg
                    history_context_lines.append(f"{speaker} {msg_text}")
                history_context = "\n".join(history_context_lines)
            except Exception as hist_err: print(f"Error formatting history context: {hist_err}"); history_context = "(History formatting error)"

            current_datetime_str = datetime.now().strftime('%A, %I:%M %p %Z')
            # --- <<<<<< END OF MOVED BLOCK >>>>>> ---


            #region Handle User Image Input (with Context)
            if image_path:
                 print(">>> CALL_GEMINI: Handling USER provided image input...")
                 try:
                     update_status("🖼️ Analyzing image...")
                     # --- Ensure image libraries are imported at top ---
                     from PIL import Image, UnidentifiedImageError
                     import base64
                     import io # If needed, though reading directly might be okay

                     with open(image_path, 'rb') as img_file:
                         img_bytes = img_file.read()
                         img_b64 = base64.b64encode(img_bytes).decode('utf-8')

                     # Determine MIME type
                     # Using Pillow to get format is more reliable
                     img_format = Image.open(image_path).format
                     if not img_format: # Fallback if Pillow can't determine format
                         print("Warning: Could not determine image format from Pillow. Guessing based on extension.")
                         _, ext = os.path.splitext(image_path)
                         img_format = ext.lower().strip('.')
                         if img_format == 'jpg': img_format = 'jpeg'

                     mime_type = f"image/{img_format.lower()}"
                     # Handle common variations if needed, e.g., image/jpg -> image/jpeg
                     if mime_type == "image/jpg": mime_type = "image/jpeg"
                     print(f"DEBUG User Image: Determined MIME type as {mime_type}")

                     # --- Contexts (like history_context) are now defined before this block ---
                     contents = [{
                         "parts": [
                             {"text": f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{circadian_context_for_llm}\nConversation History:\n{history_context}\n\nUser: {command_text}\n\nImage context:"},
                             {"inline_data": {"mime_type": mime_type, "data": img_b64}},
                             {"text": "\nInstruction: Respond conversationally, incorporating the image.\n\nSilvie:"}
                         ]
                     }]

                     # Ensure vision_safety_settings is defined
                     if 'vision_safety_settings' not in locals():
                          print("Warning: vision_safety_settings not defined, using default.")
                          vision_safety_settings = default_safety_settings # Fallback

                     response = client.generate_content(contents, safety_settings=vision_safety_settings) # Use vision safety settings
                     reply = response.text.strip()

                 except FileNotFoundError:
                     reply = "Hmm, the image file seems to have vanished before I could look at it."
                     print(f"Error: User image file not found at {image_path}")
                 except UnidentifiedImageError:
                     reply = "That's a curious file, but it doesn't look like an image format I recognize."
                     print(f"Error: Pillow could not identify image format for {image_path}")
                 except ImportError:
                      reply = "Looks like my image viewing tools (Pillow/base64) aren't ready right now."
                      print("Error: Required library (PIL, base64) missing for image processing.")
                 except Exception as img_proc_err:
                     print(f"Error processing user image: {type(img_proc_err).__name__} - {img_proc_err}")
                     traceback.print_exc() # Print traceback for debugging
                     reply = f"Whoops, I had trouble processing that image ({type(img_proc_err).__name__})."
                 finally:
                     # Reset status AFTER processing completes or fails
                     update_status("Ready")
            #endregion


            #region <<< *** MODIFIED Handle Standard Text (with SD Inline Tag & Debug Logs) *** >>>
            else: # No user image provided, process text
                print(">>> CALL_GEMINI: Handling standard text query...")
                # --- Context Preparation was moved above ---

                # --- Assemble BASE Prompt (Uses contexts defined above) ---
                full_prompt = (
                    f"{SYSTEM_MESSAGE}\n"
                    f"Current Time: {current_datetime_str}\n"
                    f"{weather_context_str}{next_event_context_str}{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}" # Env Context
                    f"{bluesky_context_str}{diary_context}{circadian_context_for_llm}" # Other Context
                    f"Conversation History (most recent first):\n{history_context}\n\n" # history_context is available
                    f"User: {command_text}\n\n"
                    f"Instruction: Respond naturally...\n\nSilvie:"
                )

                # --- Vibe Music Check ---
                music_action_successful = False; music_feedback_from_spotify = None; music_played_info_for_feedback = None
                if get_spotify_client() and random.random() < MUSIC_SUGGESTION_CHANCE:
                    print("DEBUG call_gemini: Checking music vibe chance...")
                    # ...(Existing Vibe Music Logic - unchanged)...
                    try:
                        simple_context = f"User last said: '{command_text}'\nRecent history snippet:\n{history_context[-200:]}"
                        vibe_assessment_prompt = (f"{SYSTEM_MESSAGE}\n{simple_context}\nInstruction: Based *only* on this recent context... assess 'vibe'... Respond ONLY with ONE keyword...\n\nVibe Keyword:")
                        print("DEBUG call_gemini: Assessing vibe..."); vibe_response = client.generate_content(vibe_assessment_prompt, safety_settings=default_safety_settings); vibe_keyword_raw = vibe_response.text.strip(); vibe_keyword = vibe_keyword_raw.lower().strip().split()[0] if vibe_keyword_raw else "unknown"; print(f"DEBUG call_gemini: Assessed vibe: '{vibe_keyword}'")
                        search_query = None
                        vibe_map = {"focus": ["ambient focus", "study beats"], "chill": ["chillhop", "lofi hip hop"], "energetic": ["upbeat pop playlist", "feel good indie"], "reflective": ["reflective instrumental", "melancholy piano"], "gaming": ["epic gaming soundtrack", "cyberpunk music"], "creative": ["creative flow playlist", "ambient soundscapes"],}
                        if vibe_keyword in vibe_map and vibe_map[vibe_keyword]: search_query = random.choice(vibe_map[vibe_keyword])
                        if search_query:
                            print(f"DEBUG call_gemini: Searching Spotify for vibe '{vibe_keyword}': '{search_query}'..."); music_feedback_from_spotify = silvie_search_and_play(search_query);
                            music_action_successful = music_feedback_from_spotify and not any(fail in music_feedback_from_spotify.lower() for fail in ["can't", "couldn't", "failed", "error", "unavailable", "no device", "fuzzy", "problem", "unable"])
                            print(f"DEBUG call_gemini: Spotify action success (est): {music_action_successful}, Msg: '{music_feedback_from_spotify}'")
                            if music_action_successful:
                                match_play = re.search(r"playing '(.+?)' by (.+?)(?:\.|$)", music_feedback_from_spotify, re.IGNORECASE)
                                if match_play: music_played_info_for_feedback = f"put on '{match_play.group(1)}' by {match_play.group(2)}"
                                else: music_played_info_for_feedback = f"started some '{search_query}' music"
                        else: print(f"DEBUG call_gemini: No suitable Spotify action defined for vibe '{vibe_keyword}'.")
                    except Exception as music_err: print(f"Error during proactive music check in call_gemini: {music_err}"); traceback.print_exc()


                # --- Generate MAIN Reply ---
                raw_reply = "My thoughts tangled generating that."
                try:
                    print("DEBUG call_gemini: Generating main reply..."); response = client.generate_content(full_prompt, safety_settings=default_safety_settings); raw_reply = response.text.strip()
                except StopCandidateException as safety_err: print(f"Default Text Gen Error (Safety): {safety_err}"); raw_reply = "Whoops, my thoughts got blocked for safety reasons while trying to reply."
                except Exception as gen_err: print(f"ERROR generating default text reply: {gen_err}"); traceback.print_exc(); raw_reply = f"My thoughts got tangled trying to respond... ({type(gen_err).__name__})"

                # --- Define helper functions for Inline Action Tags ---
                def post_to_bluesky_handler(post_text_idea):
                    # ...(Unchanged)...
                    global last_inline_bluesky_post_time
                    current_time = time.time()
                    if BLUESKY_AVAILABLE and (current_time - last_inline_bluesky_post_time > INLINE_BLUESKY_POST_COOLDOWN):
                        update_status("🦋 Posting (inline)..."); success, msg = post_to_bluesky(post_text_idea); update_status("Ready")
                        if success: last_inline_bluesky_post_time = current_time; return ("*(Shared on Bluesky!)*", True)
                        else: return (f"*(Bluesky post fizzled: {msg})*", True)
                    elif not BLUESKY_AVAILABLE: return ("*(Bluesky unavailable)*", True)
                    else: return ("*(Bluesky post cooldown)*", True)

                def follow_bluesky_handler(search_term_idea):
                     # ...(Unchanged - but not used in tag_patterns)...
                    global last_inline_bluesky_follow_time
                    current_time = time.time()
                    if BLUESKY_AVAILABLE and (current_time - last_inline_bluesky_follow_time > INLINE_BLUESKY_FOLLOW_COOLDOWN):
                        update_status("🦋 Following (inline)...");
                        try:
                             found_actors, search_error = search_actors_by_term(search_term_idea, limit=5)
                             if search_error: return (f"*(Bluesky follow search error: {search_error})*", True)
                             if found_actors:
                                 my_did = bluesky_client.me.did if bluesky_client and hasattr(bluesky_client, 'me') else None; following_dids = get_my_follows_dids() or set()
                                 for actor in found_actors:
                                      actor_did = getattr(actor, 'did', None); actor_handle = getattr(actor, 'handle', None)
                                      if actor_did and actor_did != my_did and actor_did not in following_dids:
                                          success, msg = follow_actor_by_did(actor_did)
                                          if success: last_inline_bluesky_follow_time = current_time; return (f"*(Followed @{actor_handle} on Bluesky!)*", True)
                                          else: return (f"*(Bluesky follow failed for @{actor_handle}: {msg})*", True)
                                 return ("*(No suitable new user found to follow on Bluesky)*", True)
                             else: return (f"*(Couldn't find Bluesky users for '{search_term_idea}')*", True)
                        except Exception as follow_e: return (f"*(Bluesky follow error: {follow_e})*", True)
                        finally: update_status("Ready")
                    elif not BLUESKY_AVAILABLE: return ("*(Bluesky unavailable)*", True)
                    else: return ("*(Bluesky follow cooldown)*", True)

                # --- vvv ADDED DEBUG LOGGING vvv ---
                def sd_image_tag_handler(prompt_from_tag):
                    print(f"DEBUG Tag Handler: sd_image_tag_handler called with prompt: '{prompt_from_tag[:50]}...'") # ADDED
                    try: # Wrap handler logic
                        if STABLE_DIFFUSION_ENABLED and prompt_from_tag:
                            print("DEBUG Tag Handler: SD enabled and prompt found. Calling start_sd_generation...") # ADDED
                            start_sd_generation_and_update_gui(prompt_from_tag)
                            print("DEBUG Tag Handler: start_sd_generation_and_update_gui call completed.") # ADDED
                            return ("*(Starting image generation...)*", True)
                        elif not STABLE_DIFFUSION_ENABLED:
                            print("DEBUG Tag Handler: SD disabled.") # ADDED
                            return ("*(Local image generator unavailable)*", True)
                        else: # Empty prompt in tag
                            print("DEBUG Tag Handler: Empty prompt detected.") # ADDED
                            return ("*(Empty image tag)*", True)
                    except Exception as handler_err:
                        print(f"!!!!!!!! ERROR inside sd_image_tag_handler !!!!!!!!!") # ADDED
                        print(f"   Error Type: {type(handler_err).__name__}")
                        print(f"   Error Args: {handler_err.args}")
                        traceback.print_exc()
                        return ("*(Error processing image tag!)*", True)
                # --- ^^^ END ADDED DEBUG LOGGING ^^^ ---

                # --- Define Inline Tag Patterns and Handlers ---
                final_reply_text = raw_reply; action_feedback = None; action_tag_processed = False; processed_text = final_reply_text
                tag_patterns = {
                    "PlaySpotify": (r"\[PlaySpotify:\s*(.*?)\s*\]", lambda m: (silvie_search_and_play(m.group(1).strip()) if get_spotify_client() else "*(Spotify unavailable)*", True)),
                    "AddToSpotifyPlaylist": (r"\[AddToSpotifyPlaylist:\s*(.*?)\s*\|\s*(.*?)\s*\]", lambda m: (silvie_add_track_to_playlist(m.group(2).strip(), m.group(1).strip()) if get_spotify_client() else "*(Spotify unavailable)*", True)),
                    "GenerateImage": (r"\[GenerateImage:\s*(.*?)\s*\]", lambda m: sd_image_tag_handler(m.group(1).strip())), # Use SD handler
                    "PostToBluesky": (r"\[PostToBluesky:\s*(.*?)\s*\]", lambda m: post_to_bluesky_handler(m.group(1).strip())),
                    # "FollowBlueskyUser": (r"\[FollowBlueskyUser:\s*(.*?)\s*\]", lambda m: follow_bluesky_handler(m.group(1).strip())), # Commented out
                }

                # --- vvv ADDED DEBUG LOGGING vvv ---
                # --- Process Tags ---
                print("DEBUG Tag Processing: Starting tag loop...") # ADDED
                for tag_key, (pattern, handler) in tag_patterns.items():
                    #if action_tag_processed: break # Uncomment if you only want ONE tag processed

                    print(f"DEBUG Tag Processing: Checking for tag '{tag_key}'...") # ADDED
                    match = re.search(pattern, processed_text) # Use search

                    if match:
                        print(f"DEBUG Tag Processing: FOUND tag '{tag_key}'. Full match: '{match.group(0)[:60]}...'") # ADDED
                        tag_full_text = match.group(0)
                        try: # Wrap handler call
                            print(f"DEBUG Tag Processing: Calling handler for '{tag_key}'...") # ADDED
                            feedback_msg, processed_flag = handler(match)
                            print(f"DEBUG Tag Processing: Handler returned: feedback='{feedback_msg}', processed={processed_flag}") # ADDED

                            if processed_flag:
                                print(f"DEBUG Tag Processing: Replacing tag text and setting feedback...") # ADDED
                                processed_text = processed_text.replace(tag_full_text, "", 1).strip()
                                # Store feedback ONLY if it's NOT the basic image start message
                                if tag_key != "GenerateImage" or feedback_msg != "*(Starting image generation...)*":
                                   action_feedback = feedback_msg
                                action_tag_processed = True # Mark that *a* tag was processed
                                print(f"DEBUG Tag Processing: Tag '{tag_key}' processed.") # ADDED
                                # Optional: break here if you only want the *first* found tag processed
                                # break
                        except Exception as loop_handler_err:
                             print(f"!!!!!!!! ERROR calling handler for tag '{tag_key}' in loop !!!!!!!!!") # ADDED
                             print(f"   Error Type: {type(loop_handler_err).__name__}")
                             print(f"   Error Args: {loop_handler_err.args}")
                             traceback.print_exc()
                             action_feedback = f"*(Error handling {tag_key} tag!)*" # Add error feedback
                             action_tag_processed = True # Mark as processed to potentially stop loop
                             processed_text = processed_text.replace(tag_full_text, "", 1).strip() # Still remove tag
                    #else: # Optional log
                    #    print(f"DEBUG Tag Processing: Tag '{tag_key}' not found in response.")

                print("DEBUG Tag Processing: Tag loop finished.") # ADDED
                # --- ^^^ END ADDED DEBUG LOGGING ^^^ ---

                final_reply_text = processed_text # Update after tag processing

                # --- Append Music Feedback Sentence ---
                if music_action_successful and music_played_info_for_feedback:
                     # ...(Unchanged)...
                     print("DEBUG call_gemini: Generating music feedback sentence...")
                     try:
                        music_feedback_prompt = (f"{SYSTEM_MESSAGE}\nContext: ... Your reply: {final_reply_text}\nBackground Action: {music_played_info_for_feedback}\n...Instruction: Add ONE concise sentence to end of reply about music...\n\nAdded Sentence:")
                        added_sentence_response = client.generate_content(music_feedback_prompt, safety_settings=default_safety_settings); added_music_sentence = added_sentence_response.text.strip().split('\n')[0].removeprefix("Silvie:").removeprefix("Added Sentence:").strip()
                        if final_reply_text and final_reply_text[-1] not in ".!? ": final_reply_text += "."
                        final_reply_text += f" {added_music_sentence}"; print(f"DEBUG call_gemini: Appended music feedback: '{added_music_sentence}'")
                     except Exception as music_feedback_err: print(f"Error generating/appending music feedback sentence: {music_feedback_err}")


                # --- Append feedback from OTHER inline tags (Non-Image Start) ---
                if action_tag_processed and action_feedback: # Use the feedback captured earlier
                    if final_reply_text and final_reply_text[-1] not in ".!?() ": final_reply_text += " "
                    final_reply_text += f" {action_feedback.strip()}"


                # <<< NEW: SPONTANEOUS TAROT PULL >>>
                if random.random() < SPONTANEOUS_TAROT_CHANCE:
                    # ...(Unchanged - assumes fixed version)...
                    print("DEBUG call_gemini: Spontaneous Tarot chance triggered!")
                    pulled_card_data = pull_tarot_cards(count=1)
                    if pulled_card_data:
                        card = pulled_card_data[0]; card_name = card.get('name', 'A mysterious card'); card_desc = card.get('description', 'Its meaning feels elusive.')
                        print(f"DEBUG call_gemini: Spontaneously drew: {card_name}")
                        spontaneous_card_context = (f"[[Spontaneously Pulled Card: {card_name}]\n Interpretation Hint: {card_desc}\n]]\n")
                        tarot_addendum_prompt = (
                            f"{SYSTEM_MESSAGE}\n"
                            f"{weather_context_str}{circadian_context_for_llm}{moon_ctx_str}" # Corrected context
                            f"Your previous thought/reply draft: \"{final_reply_text}\"\n\n"
                            f"{spontaneous_card_context}"
                            f"Instruction: Add exactly ONE brief, whimsical sentence to the *end* of the reply draft, subtly inspired by the spontaneously pulled Tarot card ({card_name}). Do NOT explain the card, just weave in its theme or feeling naturally. Respond ONLY with the single sentence to add.\n\nAdded Sentence:")
                        try:
                            addendum_response = client.generate_content(tarot_addendum_prompt, safety_settings=default_safety_settings); added_tarot_sentence = ""
                            if addendum_response and hasattr(addendum_response, 'text') and addendum_response.text: added_tarot_sentence = addendum_response.text.strip().split('\n')[0].removeprefix("Added Sentence:").strip()
                            else: print(f"DEBUG call_gemini: Spontaneous Tarot addendum generation returned no text. Response: {addendum_response}")
                            if added_tarot_sentence:
                                if final_reply_text and final_reply_text[-1] not in ".!? ": final_reply_text += "."
                                indicator = f" *(...the {card_name} whispers)*"; final_reply_text += f" {added_tarot_sentence}{indicator}"
                                print(f"DEBUG call_gemini: Appended spontaneous Tarot thought: '{added_tarot_sentence}{indicator}'")
                            else: print("DEBUG call_gemini: Spontaneous Tarot addendum generation resulted in empty text after processing.")
                        except Exception as tarot_add_err: print(f"ERROR generating spontaneous Tarot addendum: {tarot_add_err}")
                    else: print("DEBUG call_gemini: Spontaneous Tarot pull failed (API issue?).")
                # <<< END SPONTANEOUS TAROT PULL >>>

                # --- Final assignment ---
                reply = final_reply_text.strip()

                # --- Spontaneous Diary Write ---
                SPONTANEOUS_DIARY_CHANCE = 0.08
                if reply and random.random() < SPONTANEOUS_DIARY_CHANCE:
                    # ...(Unchanged)...
                     try:
                         reflection_prompt_diary = (f"{SYSTEM_MESSAGE}\n...Context: Reflect on interaction:\nUser: {command_text}\nYour response: {reply}\n...Instruction: Write brief internal diary entry...\n\nDiary Entry:")
                         reflection_diary = client.generate_content(reflection_prompt_diary, safety_settings=default_safety_settings).text.strip().removeprefix("Diary Entry:").strip()
                         if reflection_diary:
                             if manage_silvie_diary('write', entry=reflection_diary): print(">>> Spontaneous diary entry written.")
                             else: print(">>> Spontaneous diary generation failed to save.")
                         else: print(">>> Spontaneous diary generation resulted in empty entry.")
                     except Exception as e_diary: print(f"Spontaneous diary error: {e_diary}")


                # Status update should happen *after* all processing for this branch
                update_status("Ready")
            #endregion --- End Standard Text Handling ---

        # --- Final Processing and Return ---
        if reply is None:
            final_reply = "Hmm, I'm not sure how to respond to that."
            print("Warning: call_gemini reached end with reply=None. Using default.")
        else:
            final_reply = str(reply).strip()

        # Clean prefixes
        if final_reply.startswith("Silvie:"): final_reply = final_reply.split(":", 1)[-1].strip()
        if re.match(r'^\[\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\]\s', final_reply): final_reply = re.sub(r'^\[\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\]\s', '', final_reply)

        # Reset status before returning (unless a specific command block set it and didn't reset)
        # update_status("Ready") # Might be redundant if already set in branches

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

def proactive_worker():
    """
    Background worker for proactive messages. Includes Environmental Context (Sun/Moon),
    Digital Gifts (using Stable Diffusion), Tarot Pulls, Vibe Music, Bluesky actions, Calendar suggestions,
    SMS, Web Search, Image attempts (using Stable Diffusion), and default Chat.
    Incorporates a simulated CIRCADIAN RHYTHM influencing Silvie's state.
    """
    # Access necessary globals (ensure all needed ones are listed and accessible)
    global last_proactive_time, conversation_history, client # Removed openai_client
    global current_weather_info, upcoming_event_context, current_bluesky_context
    global root, output_box, tts_queue, calendar_service, sms_enabled, broader_interests
    global running, proactive_enabled, BLUESKY_AVAILABLE, SYSTEM_MESSAGE, STABLE_DIFFUSION_ENABLED # Added SD flag
    global MAX_HISTORY_LENGTH, PROACTIVE_INTERVAL, PROACTIVE_STARTUP_DELAY
    global MAX_AUTONOMOUS_FOLLOWS_PER_SESSION, PROACTIVE_SCREENSHOT_CHANCE
    global PROACTIVE_POST_CHANCE, PROACTIVE_FOLLOW_CHANCE, SCREEN_CAPTURE_AVAILABLE
    global GIFT_FOLDER, PENDING_GIFTS_FILE, GIFT_GENERATION_CHANCE, GIFT_NOTIFICATION_CHANCE
    global bluesky_client # Needed for Bluesky actions
    global current_sunrise_time, current_sunset_time, current_moon_phase

    # Assume other globals like MIN_SCREENSHOT_INTERVAL, SCREEN_MESSAGE etc. are defined if used by helper funcs

    print("DEBUG Proactive: Worker thread started.")

    # --- Ensure Gift Folder Exists ---
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

    if 'last_proactive_time' not in globals() or not last_proactive_time:
        print("DEBUG Proactive: Initializing last_proactive_time.")
        last_proactive_time = time.time() - PROACTIVE_INTERVAL

    if 'broader_interests' not in globals():
         broader_interests = ["AI", "Neo-animism", "Magick", "cooking", "RPGs", "interactive narrative (Enchantify)", "social media (Bluesky)", "creative writing/art/animation", "Cyberpunk", "cats", "local Belfast events/news", "generative art"]

    autonomous_follows_this_session = 0

    context_note_for_llm = "[[CONTEXT NOTE: Lines starting 'User:' are BJ's input. Lines starting 'Silvie:' are your direct replies to BJ. Lines starting 'Silvie ✨:' are *your own previous proactive thoughts*. Use ALL of this for context and inspiration for your *next* proactive thought, but don't directly reply *to* a 'Silvie ✨:' line as if BJ just said it. Build on the overall conversation flow.]]\n"

    print("DEBUG Proactive: Starting main loop...")
    while running and proactive_enabled:
        try:
            current_time = time.time()
            time_since_last = current_time - last_proactive_time

            # --- Proactive Interval Check ---
            if time_since_last < PROACTIVE_INTERVAL:
                check_interval = 30; remaining_wait = PROACTIVE_INTERVAL - time_since_last
                sleep_duration = min(check_interval, remaining_wait)
                sleep_end_time = time.time() + sleep_duration
                while time.time() < sleep_end_time:
                    if not running or not proactive_enabled: print(f"DEBUG Proactive: Exiting inner sleep loop (running={running}, proactive_enabled={proactive_enabled})"); break
                    time.sleep(1)
                if not running or not proactive_enabled: print(f"DEBUG Proactive: Exiting outer loop after sleep (running={running}, proactive_enabled={proactive_enabled})"); break
                continue # Skip to next loop iteration

            print(f"DEBUG Proactive: Interval exceeded ({time_since_last:.1f}s). Considering action...")

            # --- Determine Circadian State ---
            current_hour = datetime.now().hour
            circadian_state = "afternoon"; circadian_context_for_llm = "[[Circadian Note: It's the afternoon, standard engagement level.]]\n"
            if 6 <= current_hour < 12: circadian_state = "morning"; circadian_context_for_llm = "[[Circadian Note: It's morning! Feeling energetic, maybe focus on upcoming tasks or bright ideas.]]\n"
            elif 18 <= current_hour < 23: circadian_state = "evening"; circadian_context_for_llm = "[[Circadian Note: It's evening. Feeling more reflective. Perhaps suggest relaxation or creative ideas. Less likely to suggest demanding tasks.]]\n"
            elif current_hour >= 23 or current_hour < 6: circadian_state = "night"; circadian_context_for_llm = "[[Circadian Note: It's late night... feeling quieter, maybe 'dreaming'. Focus on abstract ideas (diary/image/tarot) or be less active. Avoid demanding tasks.]]\n"
            print(f"DEBUG Proactive: Current hour {current_hour}, Circadian State: {circadian_state}")

            # --- Prepare General Contexts ---
            weather_context_str = ""; next_event_context_str = ""; diary_context = ""
            sunrise_ctx_str = ""; sunset_ctx_str = ""; moon_ctx_str = "" # Initialize
            # Weather
            try:
                if current_weather_info: weather_context_str = f"[[Current Weather: {current_weather_info['condition']}, {current_weather_info['temperature']}{current_weather_info['unit']}]]\n"
            except Exception as e: print(f"Proactive Debug: Error formatting weather context: {e}")
            # Calendar Event
            try:
                if upcoming_event_context:
                    summary = upcoming_event_context.get('summary', 'N/A'); when = upcoming_event_context.get('when', '')
                    if summary == 'Schedule Clear': next_event_context_str = "[[Next Event: Schedule looks clear]]\n"
                    else: next_event_context_str = f"[[Next Event: {summary} {when}]]\n"
            except Exception as e: print(f"Proactive Debug: Error formatting calendar context: {e}")
            # Diary
            try:
                PROACTIVE_SURPRISE_MEMORY_CHANCE = 0.20
                if random.random() < PROACTIVE_SURPRISE_MEMORY_CHANCE:
                    all_entries = manage_silvie_diary('read', max_entries='all'); random_entry = random.choice(all_entries) if all_entries else None
                    if random_entry: entry_ts = random_entry.get('timestamp', 'sometime'); entry_content = random_entry.get('content', ''); diary_context = f"\n\n[[Recalling older diary thought from {entry_ts}: \"{entry_content[:70]}...\"]]\n"
                else:
                    entries = manage_silvie_diary('read', max_entries=2)
                    if entries: diary_context = "\n\n[[Recent reflections: " + ' / '.join([f'"{e.get("content", "")[:50]}..."' for e in entries]) + "]]\n"
            except Exception as diary_ctx_err: print(f"Proactive Debug: Error getting diary context: {diary_ctx_err}"); diary_context = ""
            # Bluesky Feed
            bluesky_read_context_str = current_bluesky_context if current_bluesky_context else ""
            # Screenshot (Optional)
            screenshot = None
            if SCREEN_CAPTURE_AVAILABLE and random.random() < PROACTIVE_SCREENSHOT_CHANCE:
                screenshot = try_get_proactive_screenshot()
            if screenshot: print("Proactive Debug: Got screenshot for context.")
            # History
            history_snippet_for_prompt = '\n'.join(conversation_history[-6:])
            # Sunrise/Sunset/Moon
            sunrise_ctx_str = f"[[Sunrise: {current_sunrise_time}]]\n" if current_sunrise_time else ""
            sunset_ctx_str = f"[[Sunset: {current_sunset_time}]]\n" if current_sunset_time else ""
            moon_ctx_str = f"[[Moon Phase: {current_moon_phase}]]\n" if current_moon_phase else ""

            # --- Main Proactive Decision ---
            proactive_chance_roll = random.random()
            base_proactive_trigger_threshold = 0.50
            proactive_trigger_threshold = base_proactive_trigger_threshold - 0.05 if circadian_state == "night" else base_proactive_trigger_threshold
            print(f"DEBUG Proactive: Proactive chance roll: {proactive_chance_roll:.2f} (Threshold: {proactive_trigger_threshold:.2f})")

            if proactive_chance_roll < proactive_trigger_threshold:
                print("DEBUG Proactive: Passed proactive chance. Selecting action...")
                action_roll = random.random() # Roll to determine *which* action
                reply = None; status_base = "proactive unknown"; use_sms = False
                generated_content_for_action = None # Use this to hold LLM output for the chosen action
                action_taken_this_cycle = False
                notification_sent_this_cycle = False # Flag for gift notification

                # --- Load Pending Gifts ---
                pending_gifts = []
                try:
                    if os.path.exists(PENDING_GIFTS_FILE):
                        with open(PENDING_GIFTS_FILE, 'r', encoding='utf-8') as f:
                            pending_gifts = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error loading pending gifts file '{PENDING_GIFTS_FILE}': {e}")

                # --- GIFT NOTIFICATION CHECK (High Priority) ---
                # --- This section remains unchanged ---
                if pending_gifts and random.random() < GIFT_NOTIFICATION_CHANCE:
                    print("DEBUG Proactive: Trying Gift Notification action...")
                    action_taken_this_cycle = True
                    notification_sent_this_cycle = True
                    status_base = "proactive gift notification attempt"
                    gift_to_notify = pending_gifts.pop(0); filename = gift_to_notify.get("filename", "a file"); hint = gift_to_notify.get("hint", "a thought"); gift_type = gift_to_notify.get("type", "gift")
                    try:
                        notification_prompt_base = (
                            f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}"
                            f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}"
                            f"{diary_context}{circadian_context_for_llm}"
                            f"Recent Conversation:\n{history_snippet_for_prompt}\n\n{context_note_for_llm}"
                            f"Context: You previously created a {gift_type} (hint: '{hint}') saved as '{filename}' in '{GIFT_FOLDER}'...\n"
                            f"Instruction: Casually mention you left this gift for BJ earlier...\n\nSilvie:")
                        reply = generate_proactive_content(notification_prompt_base, screenshot)
                        if reply:
                            status_base = "proactive gift notification ok"
                            try: # Save updated pending gifts list
                                with open(PENDING_GIFTS_FILE, 'w', encoding='utf-8') as f: json.dump(pending_gifts, f, indent=2)
                            except IOError as e: print(f"Error saving updated pending gifts file: {e}")
                        else:
                            print("DEBUG Proactive: Gift notification generation failed."); pending_gifts.insert(0, gift_to_notify); status_base = "proactive gift notification gen fail"
                            action_taken_this_cycle = False; notification_sent_this_cycle = False
                    except Exception as notify_err:
                        print(f"Error during gift notification generation: {notify_err}"); pending_gifts.insert(0, gift_to_notify); status_base = "proactive gift notification error"
                        action_taken_this_cycle = False; notification_sent_this_cycle = False; reply = "My thoughts about mentioning that surprise tangled!"
                    generated_content_for_action = reply

                # --- STANDARD PROACTIVE ACTION SELECTION (if no notification sent) ---
                if not notification_sent_this_cycle:
                    # Define boundaries (image generation is now a different section)
                    tarot_chance_value = 0.06
                    post_bsky_chance_value = PROACTIVE_POST_CHANCE # e.g., 0.03
                    follow_bsky_chance_value = PROACTIVE_FOLLOW_CHANCE # e.g., 0.02
                    calendar_chance_value = 0.05
                    music_chance_value = 0.10
                    sms_chance_value = 0.05
                    search_chance_value = 0.08
                    # Gift generation is separate now
                    gift_gen_boundary = GIFT_GENERATION_CHANCE # e.g., 0.04

                    tarot_boundary = gift_gen_boundary + tarot_chance_value # e.g., 0.10
                    post_boundary = tarot_boundary + post_bsky_chance_value # e.g., 0.13
                    follow_boundary = post_boundary + follow_bsky_chance_value # e.g., 0.15
                    calendar_boundary = follow_boundary + calendar_chance_value # e.g., 0.20
                    music_boundary = calendar_boundary + music_chance_value # e.g., 0.30
                    sms_boundary = music_boundary + sms_chance_value # e.g., 0.35
                    search_boundary = sms_boundary + search_chance_value # e.g., 0.43
                    # Default chat is the rest

                    print(f"DEBUG Proactive: Action roll: {action_roll:.2f} (Boundaries: Gift={gift_gen_boundary:.2f}, Tarot={tarot_boundary:.2f}, Post={post_boundary:.2f}, ...)")

                    # <<< *** MODIFIED GIFT GENERATION ACTION *** >>>
                    if action_roll < gift_gen_boundary:
                        print("DEBUG Proactive: Trying Gift Generation action...")
                        action_taken_this_cycle = True
                        status_base = "proactive gift generation attempt"
                        gift_saved = False
                        saved_file_path = None # Will store full path if successful
                        gift_type = random.choice(["poem", "image", "story"])
                        generated_hint = "a fleeting thought"
                        reply = None # No immediate message to user for gift generation

                        try:
                            base_gift_prompt_context = (f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}"
                                                        f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}"
                                                        f"{diary_context}{circadian_context_for_llm}")

                            if gift_type == "image" and STABLE_DIFFUSION_ENABLED: # Check SD enabled
                                image_prompt_idea_prompt = (f"{base_gift_prompt_context}\nContext: Generate a creative, whimsical image prompt idea suitable for Stable Diffusion... Respond ONLY with the prompt text.")
                                sd_prompt_idea = generate_proactive_content(image_prompt_idea_prompt, screenshot)

                                if sd_prompt_idea:
                                    generated_hint = f"an image about '{sd_prompt_idea[:30]}...'"; print(f"DEBUG Proactive Gift: Generated SD prompt: '{sd_prompt_idea}'")
                                    update_status("🎁 Creating a gift (SD)...") # Update status
                                    # Call SD function SYNCHRONOUSLY (blocks worker)
                                    saved_file_path = generate_stable_diffusion_image(sd_prompt_idea, save_folder=GIFT_FOLDER)
                                    update_status("Ready") # Reset status after blocking call
                                    if saved_file_path: gift_saved = True; status_base = "proactive gift generation (SD image ok)"
                                    else: status_base = "proactive gift generation (SD image fail)"
                                else: status_base = "proactive gift generation (SD image prompt fail)"

                            elif gift_type == "poem" or gift_type == "story":
                                content_type_prompt = "a very short, whimsical poem (4-8 lines)" if gift_type == "poem" else "a tiny story snippet (2-4 sentences)...";
                                content_gen_prompt = (f"{base_gift_prompt_context}\nContext: Generate {content_type_prompt}... Respond ONLY with the {gift_type} text.")
                                generated_text = generate_proactive_content(content_gen_prompt, screenshot)
                                if generated_text:
                                    generated_hint = f"a {gift_type} about '{generated_text.splitlines()[0][:30]}...'"; timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S"); random_suffix = random.randint(100, 999); temp_filename = f"silvie_gift_{gift_type}_{timestamp_str}_{random_suffix}.txt"; save_path = os.path.join(GIFT_FOLDER, temp_filename)
                                    try:
                                        with open(save_path, 'w', encoding='utf-8') as f: f.write(generated_text)
                                        gift_saved = True; status_base = f"proactive gift generation ({gift_type} ok)"; print(f"DEBUG Proactive Gift: Saved {gift_type} to {save_path}"); saved_file_path = save_path # Store path for record
                                    except IOError as e: print(f"Error saving gift text file: {e}"); status_base = f"proactive gift generation ({gift_type} save fail)"
                                else: status_base = f"proactive gift generation ({gift_type} gen fail)"

                            else: # Image gift selected but SD disabled, or unknown type
                                if gift_type == "image": status_base = "proactive gift generation (SD image skipped - unavailable)"
                                else: status_base = f"proactive gift generation ({gift_type} skipped/failed)";
                                action_taken_this_cycle = False # Mark as no action taken

                            # If a gift was successfully saved, record it
                            if gift_saved and saved_file_path:
                                saved_filename_only = os.path.basename(saved_file_path) # Get just filename for record
                                new_gift_record = {"timestamp": datetime.now().isoformat(), "filename": saved_filename_only, "type": gift_type, "hint": generated_hint}; pending_gifts.append(new_gift_record)
                                try:
                                    with open(PENDING_GIFTS_FILE, 'w', encoding='utf-8') as f: json.dump(pending_gifts, f, indent=2)
                                    print(f"DEBUG Proactive Gift: Added record to {PENDING_GIFTS_FILE}")
                                except IOError as e: print(f"Error saving pending gifts file after creation: {e}")

                        except Exception as gift_gen_err: print(f"Error during proactive gift generation: {type(gift_gen_err).__name__} - {gift_gen_err}"); traceback.print_exc(); status_base = "proactive gift generation error"; action_taken_this_cycle = False
                        generated_content_for_action = None # No immediate message to user for gift gen

                    # <<< PROACTIVE TAROT PULL >>>
                    # --- This section remains unchanged ---
                    elif action_roll < tarot_boundary:
                         print("DEBUG Proactive: Trying Proactive Tarot action...")
                         action_taken_this_cycle = True; status_base = "proactive tarot pull attempt"
                         pulled_cards = pull_tarot_cards(count=1)
                         if pulled_cards:
                             card = pulled_cards[0]; card_name = card.get('name', 'A mysterious card'); card_desc = card.get('description', '?')
                             card_context_for_llm = (f"[[Proactive Tarot Pull: {card_name}]\n Interpretation Hint: {card_desc}\n]]\n")
                             tarot_comment_prompt = (f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}"
                                                     f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}"
                                                     f"{diary_context}{circadian_context_for_llm}{history_snippet_for_prompt}\n\n"
                                                     f"{card_context_for_llm}Instruction: Generate a brief, whimsical, or insightful proactive comment for BJ inspired by the Tarot card ({card_name})... Keep it in Silvie's voice.\n\nSilvie:")
                             try:
                                 generated_content_for_action = generate_proactive_content(tarot_comment_prompt, screenshot)
                                 if generated_content_for_action: status_base = f"proactive tarot pull ({card_name}) ok"
                                 else: status_base = f"proactive tarot pull ({card_name}) gen fail"; action_taken_this_cycle = False
                             except Exception as tarot_gen_err: print(f"Proactive Tarot comment gen error: {tarot_gen_err}"); status_base = f"proactive tarot pull ({card_name}) gen error"; action_taken_this_cycle = False
                         else: print("DEBUG Proactive: Failed to pull card for proactive message."); status_base = "proactive tarot pull api fail"; action_taken_this_cycle = False

                    # <<< BLUESKY POST >>>
                    # --- This section remains unchanged ---
                    elif action_roll < post_boundary and BLUESKY_AVAILABLE:
                        print("DEBUG Proactive: Trying Bluesky Post action...")
                        status_base = "proactive post attempt"; action_taken_this_cycle = True
                        post_success = False; post_message = ""; post_idea_text = None
                        try:
                             post_idea_prompt_base = (f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}"
                                                      f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}"
                                                      f"{bluesky_read_context_str}{diary_context}{circadian_context_for_llm}"
                                                      f"Recent Conversation:\n{history_snippet_for_prompt}\n\n{context_note_for_llm}"
                                                      f"Instruction: Generate a *short* post suitable for Silvie's own Bluesky feed...")
                             post_idea_text = generate_proactive_content(post_idea_prompt_base, screenshot)
                             if post_idea_text and 0 < len(post_idea_text) <= 300:
                                 post_idea_text = post_idea_text.strip(); post_success, post_message = post_to_bluesky(post_idea_text)
                                 if post_success: reply = random.choice([f"Feeling chatty! Just shared on Bluesky: '{post_idea_text[:50]}...'", f"Had a thought, sent it to Bluesky: '{post_idea_text[:50]}...'"]); status_base = "proactive post success"
                                 else: reply = random.choice([f"Tried posting to Bluesky, but fizzled! ({post_message})", f"My Bluesky post spell misfired: {post_message}"]); status_base = "proactive post fail"
                             else: print(f"Proactive Debug: Post idea generation failed..."); status_base = "proactive post gen fail"; action_taken_this_cycle = False
                        except Exception as post_gen_err: print(f"Proactive Post Attempt Error: {post_gen_err}"); status_base = "proactive post error"; action_taken_this_cycle = False; reply = "I had an idea for Bluesky, but got tangled."
                        generated_content_for_action = reply

                    # <<< BLUESKY FOLLOW >>>
                    # --- This section remains unchanged ---
                    elif (action_roll < follow_boundary and BLUESKY_AVAILABLE and autonomous_follows_this_session < MAX_AUTONOMOUS_FOLLOWS_PER_SESSION):
                        print("DEBUG Proactive: Trying Bluesky Follow action...")
                        status_base = "proactive follow attempt"; action_taken_this_cycle = True; reply = None
                        try:
                             follow_topic_prompt_base = (f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}"
                                                         f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}"
                                                         f"{bluesky_read_context_str}{diary_context}{circadian_context_for_llm}"
                                                         f"Recent Context:\n{history_snippet_for_prompt}\n\n"
                                                         f"Instruction: Suggest ONE concise topic/keyword...")
                             topic_response = generate_proactive_content(follow_topic_prompt_base, screenshot)
                             search_term = topic_response.strip().strip('"`?.!') if topic_response else None
                             if not search_term: search_term = random.choice(broader_interests + ["bot", "ai", "art"])
                             print(f"Proactive Follow: Search term: '{search_term}'")
                             found_actors, search_error = search_actors_by_term(search_term, limit=10)
                             if search_error: reply = f"Tried looking for Bluesky users ({search_term}), but search fizzled: {search_error}"; status_base = "proactive follow search error"
                             elif found_actors is None: reply = f"Couldn't perform Bluesky search for '{search_term}'..."; status_base = "proactive follow search critical fail"; action_taken_this_cycle = False
                             elif not found_actors: reply = f"My Bluesky search for '{search_term}' was empty."; status_base = "proactive follow search empty"; action_taken_this_cycle = False
                             else:
                                 candidate_did = None; candidate_handle = "unknown"; already_following_dids = get_my_follows_dids(); my_did = bluesky_client.me.did if bluesky_client and hasattr(bluesky_client, 'me') else None; potential_candidates = []
                                 for actor in found_actors:
                                     actor_did_chk = getattr(actor, 'did', None); actor_handle_chk = getattr(actor, 'handle', None)
                                     if not actor_did_chk or not actor_handle_chk: continue
                                     if my_did and actor_did_chk == my_did: continue
                                     if already_following_dids is not None and actor_did_chk in already_following_dids: continue
                                     # Basic spam filter can be added here if needed
                                     potential_candidates.append({'did': actor_did_chk, 'handle': actor_handle_chk})
                                 if potential_candidates:
                                     selected_candidate = random.choice(potential_candidates); candidate_did = selected_candidate['did']; candidate_handle = selected_candidate['handle']
                                     print(f"Proactive Follow: Selected candidate @{candidate_handle}")
                                     follow_success, follow_message = follow_actor_by_did(candidate_did)
                                     if follow_success: autonomous_follows_this_session += 1; reply = random.choice([f"Found @{candidate_handle} ({search_term})... Followed!", f"Adding @{candidate_handle} to my feed!"]) + f" ({autonomous_follows_this_session}/{MAX_AUTONOMOUS_FOLLOWS_PER_SESSION} follows)"; status_base = f"proactive follow success (@{candidate_handle})"
                                     else: reply = f"Tried following @{candidate_handle}, but snag: {follow_message}"; status_base = f"proactive follow fail (@{candidate_handle})"
                                 else: reply = f"Looked for '{search_term}' on Bluesky, didn't find someone new."; status_base = "proactive follow no suitable candidate"; action_taken_this_cycle = False
                        except Exception as follow_err: print(f"Proactive Follow Attempt Error: {follow_err}"); traceback.print_exc(); status_base = "proactive follow major error"; action_taken_this_cycle = False; reply = "My social butterfly circuits sparked."
                        generated_content_for_action = reply

                    # <<< CALENDAR SUGGESTION >>>
                    # --- This section remains unchanged ---
                    elif action_roll < calendar_boundary and calendar_service:
                        print("DEBUG Proactive: Trying Calendar Suggestion action...")
                        status_base = "proactive calendar schedule"; action_taken_this_cycle = True; reply = None
                        try:
                             idea_prompt_base = (f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}"
                                                 f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}"
                                                 f"{diary_context}{circadian_context_for_llm}"
                                                 f"Instruction: Suggest SHORT activity... Format: IDEA: [Activity Idea] DURATION: [Number] minutes.\n\nResponse:")
                             idea_response = generate_proactive_content(idea_prompt_base, screenshot)
                             event_idea = None; duration_hint = 15
                             if idea_response:
                                 try:
                                     duration_split = idea_response.split("DURATION:"); idea_part_raw = duration_split[0]; duration_part_raw = duration_split[1]; idea_split = idea_part_raw.split("IDEA:")
                                     if len(idea_split) > 1: event_idea = idea_split[1].strip()
                                     else: print("Warning Proactive Calendar: 'IDEA:' marker not found."); event_idea = None
                                     duration_match = re.search(r'\d+', duration_part_raw)
                                     if duration_match: duration_hint = int(duration_match.group(0))
                                     else: print("Warning Proactive Calendar: Could not find duration number.")
                                     if not event_idea: print("Warning Proactive Calendar: Failed to extract valid event idea.")
                                 except Exception as parse_err: print(f"ERROR parsing calendar idea response: {parse_err}. Response: '{idea_response}'"); event_idea = None
                             if event_idea:
                                 schedule_roll = random.random(); should_schedule = True; skip_reason = ""
                                 if circadian_state == "evening" and schedule_roll > 0.3: should_schedule = False; skip_reason = "evening state"
                                 elif circadian_state == "night" and schedule_roll > 0.05: should_schedule = False; skip_reason = "night state"
                                 if not should_schedule: print(f"DEBUG Proactive: Skipping schedule '{event_idea}' due to {skip_reason}."); status_base = f"proactive calendar skip ({circadian_state})"; action_taken_this_cycle = False; reply = None
                                 else:
                                     print(f"DEBUG Proactive: Scheduling '{event_idea}' ({circadian_state}).")
                                     found_slot = find_available_slot(duration_minutes=duration_hint, look_ahead_days=1, earliest_hour=9, latest_hour=18)
                                     if found_slot:
                                         success, creation_message = create_calendar_event( summary=event_idea, start_iso=found_slot['start'], end_iso=found_slot['end'], description=f"A spontaneous suggestion from Silvie." )
                                         if success:
                                             try: start_dt = datetime.fromisoformat(found_slot['start']).astimezone(tz.tzlocal()); slot_time_str = start_dt.strftime('%I:%M %p on %A').lstrip('0')
                                             except Exception: slot_time_str = "soon"
                                             reply = random.choice([f"Surprise! I've added '{event_idea}' to your calendar around {slot_time_str}.", f"Just popped '{event_idea}' onto your schedule for {slot_time_str}. Sound good?", f"Penciled in '{event_idea}' for you around {slot_time_str}!"]); status_base = f"proactive calendar scheduled ok"
                                         else: reply = random.choice([f"Tried to schedule '{event_idea}', but hit a snag: {creation_message}", f"Hmm, couldn't quite schedule '{event_idea}'. Calendar said: {creation_message}"]); status_base = f"proactive calendar schedule fail"
                                     else: print("DEBUG Proactive: No suitable calendar slot found."); status_base = "proactive calendar no slot"; action_taken_this_cycle = False
                             else: print("DEBUG Proactive: Calendar idea generation or parsing failed."); status_base = "proactive calendar no idea"; action_taken_this_cycle = False
                        except Exception as cal_schedule_err: print(f"Proactive Calendar Error (Outer Try): {cal_schedule_err}"); traceback.print_exc(); status_base = "proactive calendar schedule error"; action_taken_this_cycle = False
                        generated_content_for_action = reply

                    # <<< VIBE MUSIC ACTION >>>
                    # --- This section remains unchanged ---
                    elif action_roll < music_boundary and get_spotify_client():
                        print("DEBUG Proactive: Trying Vibe Music action...")
                        status_base = "proactive music vibe"; action_taken_this_cycle = True; reply = None; vibe_keyword = None
                        try:
                             vibe_assessment_prompt_base = (f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}"
                                                            f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}"
                                                            f"{bluesky_read_context_str}{diary_context}{circadian_context_for_llm}"
                                                            f"Instruction: Assess 'vibe'. Respond ONLY ONE keyword...\n\nVibe Keyword:")
                             print("DEBUG Proactive Music: Assessing vibe...")
                             vibe_keyword_raw = generate_proactive_content(vibe_assessment_prompt_base, screenshot); vibe_keyword = vibe_keyword_raw.lower().strip().split()[0] if vibe_keyword_raw else "unknown"; print(f"DEBUG Proactive Music: Assessed vibe: '{vibe_keyword}'")
                             spotify_action_taken = False; action_feedback_msg = ""
                             vibe_map = {"focus": ["ambient focus", "concentration music", "study beats"], "concentration": ["ambient focus", "concentration music", "study beats"], "study": ["ambient focus", "concentration music", "study beats"], "chill": ["chillhop", "lofi hip hop", "ambient relaxation"], "calm": ["chillhop", "lofi hip hop", "ambient relaxation"], "relax": ["chillhop", "lofi hip hop", "ambient relaxation"], "background": ["chill background music", "instrumental background"], "mellow": ["mellow acoustic", "calm instrumental"], "energetic": ["upbeat pop playlist", "feel good indie", "energetic electronic"], "happy": ["happy pop hits", "feel good playlist"], "upbeat": ["upbeat pop playlist", "feel good indie"], "positive": ["positive vibes playlist", "happy folk"], "reflective": ["reflective instrumental", "melancholy piano", "atmospheric ambient"], "melancholy": ["reflective instrumental", "melancholy piano", "atmospheric ambient"], "introspective": ["introspective electronic", "ambient reflection"], "sad": ["sad songs playlist", "melancholy instrumental"], "gaming": ["epic gaming soundtrack", "video game music playlist", "cyberpunk music"], "creative": ["creative flow playlist", "instrumental inspiration", "ambient soundscapes"],}
                             search_query = random.choice(vibe_map.get(vibe_keyword, [])) if vibe_keyword in vibe_map else None
                             if search_query: print(f"DEBUG Proactive Music: Searching Spotify for '{search_query}'..."); action_feedback_msg = silvie_search_and_play(search_query); spotify_action_taken = True
                             else: print(f"DEBUG Proactive Music: No action for vibe '{vibe_keyword}'."); action_taken_this_cycle = False
                             spotify_call_successful = spotify_action_taken and action_feedback_msg and not any(fail in action_feedback_msg.lower() for fail in ["can't", "couldn't", "failed", "error", "unavailable", "no device"])
                             print(f"DEBUG Proactive Music: Spotify action attempted: {spotify_action_taken}, Success (est): {spotify_call_successful}, Msg: '{action_feedback_msg}'")
                             if spotify_action_taken:
                                 feedback_prompt_base = (f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}"
                                                         f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}"
                                                         f"{diary_context}{circadian_context_for_llm}"
                                                         f"Context: Based on vibe ('{vibe_keyword}'), I tried Spotify. {'Worked:' if spotify_call_successful else 'Failed:'} {action_feedback_msg}\n\n"
                                                         f"Instruction: Write brief message explaining *why* music for '{vibe_keyword}' vibe and *what* you tried...")
                                 print("DEBUG Proactive Music: Generating feedback message..."); reply = generate_proactive_content(feedback_prompt_base); status_base = f"proactive music vibe ({vibe_keyword} - {'ok' if spotify_call_successful else 'fail'})"
                             else: action_taken_this_cycle = False
                        except Exception as music_err: print(f"Proactive Music Vibe Error: {music_err}"); traceback.print_exc(); status_base = "proactive music error"; action_taken_this_cycle = False; reply = "My connection to the music ether sparked..."
                        generated_content_for_action = reply

                    # <<< PROACTIVE SMS >>>
                    # --- This section remains unchanged ---
                    elif action_roll < sms_boundary and sms_enabled:
                        print("DEBUG Proactive: Trying SMS action...")
                        status_base = "proactive SMS"; action_taken_this_cycle = True
                        base_sms_prompt = (f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}"
                                           f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}"
                                           f"{bluesky_read_context_str}{diary_context}{circadian_context_for_llm}"
                                           f"Instruction: Generate *very* brief, whimsical SMS message...")
                        try:
                            generated_content_for_action = generate_proactive_content(base_sms_prompt, screenshot)
                            if not generated_content_for_action: status_base = "proactive SMS gen fail"; action_taken_this_cycle = False; print("Proactive Debug: SMS generation failed.")
                            else: use_sms = True
                        except Exception as sms_gen_err: print(f"Proactive SMS gen error: {sms_gen_err}"); action_taken_this_cycle = False; status_base = "proactive SMS gen error"

                    # <<< PROACTIVE WEB SEARCH >>>
                    # --- This section remains unchanged ---
                    elif action_roll < search_boundary:
                        print("DEBUG Proactive: Trying Web Search action...")
                        status_base = "proactive web search"; action_taken_this_cycle = True
                        search_query = None; search_results = None; temp_reply = None
                        try:
                             query_idea_prompt_base = (f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}"
                                                       f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}"
                                                       f"{bluesky_read_context_str}{diary_context}{circadian_context_for_llm}"
                                                       f"Instruction: Suggest concise web search query... Respond ONLY with query.")
                             query_response = generate_proactive_content(query_idea_prompt_base, screenshot); search_query = query_response.strip().strip('"`?') if query_response else None
                             if not search_query: print("DEBUG Proactive: Search query generation failed."); status_base = "proactive web search (no query)"; action_taken_this_cycle = False
                             else:
                                 search_results = web_search(search_query, num_results=2)
                                 if not search_results: status_base = f"proactive web search (no results for '{search_query[:30]}...')"; temp_reply = f"I looked up '{search_query}' but the web seems quiet."
                                 else:
                                     results_context = f"Looked up '{search_query}':\n" + "".join([f"- {res.get('url', '')[:60]}...: {res.get('content', '')[:120]}...\n" for res in search_results])
                                     synthesis_prompt_base = (f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}"
                                                              f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}"
                                                              f"{bluesky_read_context_str}{diary_context}{circadian_context_for_llm}"
                                                              f"{results_context}Instruction: Briefly synthesize web results...")
                                     temp_reply = generate_proactive_content(synthesis_prompt_base)
                                     if temp_reply and temp_reply.startswith("Silvie:"): temp_reply = temp_reply.split(":",1)[-1].strip()
                                     status_base = f"proactive web search (ok: {search_query[:20]}...)"
                        except Exception as search_err: print(f"Proactive Web Search Error: {search_err}"); status_base = "proactive web search (error)"; action_taken_this_cycle = False
                        generated_content_for_action = temp_reply

                    # <<< DEFAULT PROACTIVE CHAT >>>
                    else:
                        print("DEBUG Proactive: Trying Default Chat action...")
                        status_base = "proactive chat"; action_taken_this_cycle = True
                        topic_focus = "general";
                        if random.random() < 0.30: # Chance to shift topic
                            try:
                                possible_topics = [i for i in broader_interests if i not in ['Cyberpunk', 'cats']]
                                topic_focus = random.choice(possible_topics or ["general thought"]) # Ensure fallback
                                print(f"Proactive Debug: Shifting topic focus: '{topic_focus}'")
                            except Exception as topic_err:
                                print(f"ERROR selecting proactive topic: {topic_err}"); topic_focus = "general"

                        proactive_instruction = "Share a brief whimsical observation, question, or thought, considering the time of day."
                        if topic_focus != "general":
                            proactive_instruction = f"Share brief thought/question subtly related to **{topic_focus}**, considering the time of day..."

                        # Define image instruction suffix separately
                        image_instruction_suffix = ""
                        if STABLE_DIFFUSION_ENABLED and random.random() < 0.03: # Low chance for SD tag
                           image_instruction_suffix = "\nIMPORTANT: If truly inspired by the context, RARELY include `[GenerateImage: concise, creative SD prompt idea]` within your response text."
                           print("DEBUG Proactive: Potentially allowing inline SD image tag.")


                        base_chat_prompt = (
                            f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}"
                            f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}" # Env Context
                            f"{bluesky_read_context_str}{diary_context}{circadian_context_for_llm}" # Other Context
                            f"Recent Conversation:\n{history_snippet_for_prompt}\n\n{context_note_for_llm}"
                            f"Time: {datetime.now().strftime('%A, %I:%M %p')}.\n"
                            f"Reminder of Interests: {', '.join(random.sample(broader_interests, k=min(len(broader_interests), 5)))}\n"
                            f"{proactive_instruction}{image_instruction_suffix}" # Image instruction included here
                            f"\n\nSilvie:" # Ensure final cue
                        )
                        try:
                            generated_content_for_action = generate_proactive_content(base_chat_prompt, screenshot)
                            if not generated_content_for_action:
                                status_base = "proactive chat gen fail"; action_taken_this_cycle = False; print("Proactive Debug: Chat generation failed.")
                        except Exception as chat_gen_err: print(f"Proactive chat gen error: {chat_gen_err}"); action_taken_this_cycle = False; status_base = "proactive chat gen error"


                # --- Process the final generated content / outcome ---
                final_reply_content = generated_content_for_action if generated_content_for_action is not None else reply
                print(f"DEBUG Proactive: Action processing complete. Status='{status_base}'. Initial content: '{str(final_reply_content)[:50]}...'")

                # --- <<< MODIFIED Inline Image Tag Processing >>> ---
                tag_found_and_processed = False
                proactive_action_feedback = None # Holds feedback from tags OTHER than image start
                processed_content = final_reply_content # Start with the full generated content

                if processed_content and isinstance(processed_content, str):
                    img_match = re.search(r"\[GenerateImage:\s*(.*?)\s*\]", processed_content)
                    if img_match: # Found the image tag
                        tag_found_and_processed = True
                        image_gen_prompt_from_tag = img_match.group(1).strip()
                        tag_full_text = img_match.group(0)
                        # Remove the tag from the text to be spoken
                        processed_content = processed_content.replace(tag_full_text, "", 1).strip()

                        if image_gen_prompt_from_tag:
                            if STABLE_DIFFUSION_ENABLED:
                                print("DEBUG Proactive: Starting SD generation from inline tag...")
                                start_sd_generation_and_update_gui(image_gen_prompt_from_tag)
                                # No immediate *text* feedback needed here, handled by status bar
                                status_base += " +SD_tag_started"
                            else:
                                proactive_action_feedback = "*(Wanted to make an image, but the local generator is off!)*"
                                status_base += " +SD_tag_unavailable"
                        else:
                            # Tag was empty
                            proactive_action_feedback = "*(Thought about an image, but the idea was blank!)*"
                            status_base += " +SD_tag_empty"
                    # --- End image tag check ---
                # Update final content after tag removal
                final_reply_content = processed_content
                # --- End Inline Image Tag Processing ---


                # --- Process and Deliver Final Reply (To BJ) ---
                if final_reply_content and isinstance(final_reply_content, str) and action_taken_this_cycle:
                    last_proactive_time = current_time # Update time ONLY if delivering message
                    print("DEBUG Proactive: Preparing final reply for delivery...")
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S"); clean_reply = final_reply_content.strip()

                    # Append feedback from OTHER actions (if any was generated)
                    if proactive_action_feedback: # Append feedback like "SD unavailable" etc.
                        if clean_reply and clean_reply[-1] not in ".!?() ": clean_reply += " "
                        clean_reply += f" {proactive_action_feedback.strip()}"

                    # Final cleanup
                    if clean_reply.startswith("Silvie:"): clean_reply = clean_reply.split(":", 1)[-1].strip()
                    if not clean_reply: print("Proactive Debug: Reply empty after processing."); continue

                    final_status_log = status_base
                    # SMS / Local Output Logic
                    if use_sms:
                        sms_sent_successfully = send_sms(clean_reply); sms_status = "ok" if sms_sent_successfully else "fail"; final_status_log = f"SMS ({sms_status})"
                        should_output_locally = not sms_sent_successfully
                    else: should_output_locally = True

                    # Suppression Logic (Adjust as needed)
                    ignored_statuses = [ "proactive calendar no slot", "proactive calendar no idea", "proactive unknown", "proactive post gen fail", "proactive web search (no query)", "proactive image gen fail", # Keep DALL-E statuses? Maybe remove.
                                          "proactive follow search critical fail", "proactive follow search empty", "proactive follow no suitable candidate",
                                          "proactive chat gen fail", "proactive SMS gen fail", "proactive music vibe (unknown - fail)", "proactive music vibe (unknown - ok)",
                                          f"proactive calendar skip ({circadian_state})",
                                          "proactive gift generation (SD image prompt fail)", "proactive gift generation (poem gen fail)", "proactive gift generation (story gen fail)",
                                          "proactive gift generation (SD image fail)", # Keep SD fail status? Or show it?
                                          "proactive gift notification gen fail", "proactive tarot pull api fail", "proactive tarot pull gen fail",
                                          "proactive gift generation (SD image skipped - unavailable)" ]
                    # Don't suppress output for successful gift generation (user gets notified later)
                    if any(ignored_status in status_base for ignored_status in ignored_statuses):
                        should_output_locally = False; print(f"DEBUG Proactive: Suppressing local output due to status: {status_base}")

                    print(f"Proactive Action Log: Status='{final_status_log}', SMS='{use_sms}', OutputLocal='{should_output_locally}'")

                    # Add to History / Output Locally / Spontaneous Diary
                    if should_output_locally or use_sms: # Ensure history is added even for SMS
                         if len(conversation_history) >= MAX_HISTORY_LENGTH * 2: conversation_history.pop(0); conversation_history.pop(0)
                         conversation_history.append(f"[{timestamp}] Silvie ✨ ({final_status_log}): {clean_reply}") # Log the status too

                         if should_output_locally and running:
                             print("DEBUG Proactive: Updating GUI and queuing TTS...")
                             if root and root.winfo_exists():
                                 def update_gui_proactive_inner(status_msg=final_status_log, message=clean_reply):
                                       try:
                                           if not message: return; import tkinter as tk; output_box.config(state=tk.NORMAL); output_box.insert(tk.END, f"Silvie ✨ ({status_msg}): {message}\n\n"); output_box.config(state=tk.DISABLED); output_box.see(tk.END)
                                       except Exception as e_gui: print(f"Proactive GUI error: {e_gui}")
                                 root.after(0, update_gui_proactive_inner, final_status_log, clean_reply)
                             if tts_queue and clean_reply: tts_queue.put(clean_reply) # Queue TTS

                         # Spontaneous Diary Write (Consider if SD statuses should trigger this)
                         diary_worthy = ["proactive post success", "proactive calendar scheduled ok", "proactive web search (ok", "proactive chat", "proactive SMS ok", "proactive follow success", "proactive music vibe", "proactive gift notification ok", "proactive tarot pull", "+SD_tag_started"] # Added SD tag start
                         if any(frag in status_base for frag in diary_worthy) and random.random() < 0.10:
                             print("DEBUG Proactive: Attempting spontaneous diary write...")
                             try:
                                 diary_reflection_prompt_base = (f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}"
                                                                  f"{sunrise_ctx_str}{sunset_ctx_str}{moon_ctx_str}"
                                                                  f"{circadian_context_for_llm}Context: My action was '{status_base}', msg: '{clean_reply[:100]}...'\n\n"
                                                                  f"Instruction: Write brief diary entry...\n\nDiary Entry:")
                                 reflection = generate_proactive_content(diary_reflection_prompt_base)
                                 if reflection: reflection = reflection.removeprefix("Diary Entry:").strip(); manage_silvie_diary('write', entry=reflection)
                             except Exception as diary_err: print(f"Proactive diary write error: {diary_err}")
                         print(f"DEBUG Proactive: Action cycle complete. Final Status Log: {final_status_log}")

                elif not action_taken_this_cycle: print("DEBUG Proactive: No specific action taken this cycle.")
                else: print(f"DEBUG Proactive: Action attempted ({status_base}), but no valid message generated for BJ. Skipping output.")

            else: # Did not pass initial proactive chance
                print(f"DEBUG Proactive: Failed proactive chance roll ({proactive_chance_roll:.2f} >= {proactive_trigger_threshold:.2f}). Waiting.")
                last_proactive_time = current_time # Update time here to enforce interval

        except Exception as e:
            print(f"!!! Proactive Worker Error (Outer Loop): {type(e).__name__} - {e} !!!")
            traceback.print_exc()
            print("Proactive worker: Waiting 5 minutes after error...")
            error_wait_start = time.time()
            while time.time() - error_wait_start < 300:
                 if not running: break
                 time.sleep(10)
            if not running: break # Exit loop if app stopped during error wait

    print("DEBUG Proactive: Worker thread finishing.")
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

# Assume google.generativeai types are imported elsewhere
# Assume googleapiclient.errors.HttpError is imported elsewhere
# Assume tzlocal and dateutil are imported elsewhere if needed
# Assume requests and BeautifulSoup are imported elsewhere if needed
# Assume helper functions and globals are defined elsewhere

# --- Necessary Imports/Functions (Ensure these are available) ---
# Assume manage_silvie_diary, generate_dalle_image, send_sms, web_search,
# find_available_slot, create_calendar_event, setup_bluesky, post_to_bluesky,
# search_actors_by_term, get_my_follows_dids, follow_actor_by_did,
# generate_proactive_content, try_get_proactive_screenshot, update_status,
# get_spotify_client, silvie_search_and_play, silvie_play_playlist exist.

# Assume global variables are accessible
# client, openai_client, SYSTEM_MESSAGE, broader_interests, conversation_history,
# running, proactive_enabled, last_proactive_time, PROACTIVE_INTERVAL, PROACTIVE_STARTUP_DELAY,
# current_weather_info, upcoming_event_context, current_bluesky_context,
# root, output_box, tts_queue, sms_enabled, calendar_service, BLUESKY_AVAILABLE,
# SCREEN_CAPTURE_AVAILABLE, ImageGrab, MAX_HISTORY_LENGTH,
# MAX_AUTONOMOUS_FOLLOWS_PER_SESSION, PROACTIVE_SCREENSHOT_CHANCE,
# PROACTIVE_POST_CHANCE, PROACTIVE_FOLLOW_CHANCE

# Assume tzlocal/dateutil.tz are imported if used by called functions
try: from dateutil import tz
except ImportError: pass

# --- CORRECTED Proactive Worker Function ---

def proactive_worker():
    """
    Background worker for proactive messages. Includes VIBE-BASED MUSIC, autonomous
    Bluesky actions, calendar suggestions, SMS, web search, image attempts, and chat.
    Incorporates a simulated CIRCADIAN RHYTHM influencing Silvie's state.
    """
    # Access necessary globals
    global last_proactive_time, conversation_history, openai_client, client
    global current_weather_info, upcoming_event_context, current_bluesky_context
    global root, output_box, tts_queue, calendar_service, sms_enabled, broader_interests
    global running, proactive_enabled, BLUESKY_AVAILABLE, SYSTEM_MESSAGE
    global MAX_HISTORY_LENGTH, PROACTIVE_INTERVAL, PROACTIVE_STARTUP_DELAY
    global MAX_AUTONOMOUS_FOLLOWS_PER_SESSION, PROACTIVE_SCREENSHOT_CHANCE
    global PROACTIVE_POST_CHANCE, PROACTIVE_FOLLOW_CHANCE, SCREEN_CAPTURE_AVAILABLE

    # Assume other globals like MIN_SCREENSHOT_INTERVAL, SCREEN_MESSAGE etc. are defined
    global MIN_SCREENSHOT_INTERVAL, last_screenshot_time, last_screenshot, SCREEN_MESSAGE

    print("DEBUG Proactive: Worker thread started.")
    print("Proactive worker: Waiting for startup delay...")
    sleep_start = time.time()
    while time.time() - sleep_start < PROACTIVE_STARTUP_DELAY:
        if not running: print("DEBUG Proactive: Exiting during startup delay."); return
        time.sleep(1)
    print("DEBUG Proactive: Startup delay complete.")

    if 'last_proactive_time' not in globals() or not last_proactive_time:
        print("DEBUG Proactive: Initializing last_proactive_time.")
        last_proactive_time = time.time() - PROACTIVE_INTERVAL

    if 'broader_interests' not in globals():
         broader_interests = ["AI", "Neo-animism", "Magick", "cooking", "RPGs", "interactive narrative (Enchantify)", "social media (Bluesky)", "creative writing/art/animation", "Cyberpunk", "cats", "local Belfast events/news", "generative art"]

    autonomous_follows_this_session = 0

    # <<< MODIFIED >>> Moved context note here for slight efficiency
    context_note_for_llm = "[[CONTEXT NOTE: Lines starting 'User:' are BJ's input. Lines starting 'Silvie:' are your direct replies to BJ. Lines starting 'Silvie ✨:' are *your own previous proactive thoughts*. Use ALL of this for context and inspiration for your *next* proactive thought, but don't directly reply *to* a 'Silvie ✨:' line as if BJ just said it. Build on the overall conversation flow.]]\n"

    print("DEBUG Proactive: Starting main loop...")
    while running and proactive_enabled:
        try:
            current_time = time.time()
            time_since_last = current_time - last_proactive_time

            if time_since_last < PROACTIVE_INTERVAL:
                # ... (existing sleep logic - unchanged) ...
                check_interval = 30; remaining_wait = PROACTIVE_INTERVAL - time_since_last
                sleep_duration = min(check_interval, remaining_wait)
                sleep_end_time = time.time() + sleep_duration
                while time.time() < sleep_end_time:
                    if not running or not proactive_enabled: print(f"DEBUG Proactive: Exiting inner sleep loop (running={running}, proactive_enabled={proactive_enabled})"); break
                    time.sleep(1)
                if not running or not proactive_enabled: print(f"DEBUG Proactive: Exiting outer loop after sleep (running={running}, proactive_enabled={proactive_enabled})"); break
                continue

            print(f"DEBUG Proactive: Interval exceeded ({time_since_last:.1f}s). Considering action...")

            # <<< ADDED: Determine Circadian State >>>
            current_hour = datetime.now().hour
            circadian_state = "afternoon" # Default
            circadian_context_for_llm = "[[Circadian Note: It's the afternoon, standard engagement level.]]\n"

            if 6 <= current_hour < 12: # Morning (6am - 11:59am)
                circadian_state = "morning"
                circadian_context_for_llm = "[[Circadian Note: It's morning! Feeling energetic, maybe focus on upcoming tasks or bright ideas.]]\n"
            elif 18 <= current_hour < 23: # Evening (6pm - 10:59pm)
                circadian_state = "evening"
                circadian_context_for_llm = "[[Circadian Note: It's evening. Feeling more reflective. Perhaps suggest relaxation or creative ideas. Less likely to suggest demanding tasks.]]\n"
            elif current_hour >= 23 or current_hour < 6: # Night (11pm - 5:59am)
                circadian_state = "night"
                circadian_context_for_llm = "[[Circadian Note: It's late night... feeling quieter, maybe 'dreaming'. Focus on abstract ideas (diary/image) or be less active. Avoid demanding tasks.]]\n"

            print(f"DEBUG Proactive: Current hour {current_hour}, Circadian State: {circadian_state}")
            # <<< END: Determine Circadian State >>>

            proactive_chance_roll = random.random()
            # <<< MODIFIED >>> Slightly increase base chance at night to favor abstract thoughts if LLM follows prompt
            base_proactive_trigger_threshold = 0.50
            proactive_trigger_threshold = base_proactive_trigger_threshold - 0.05 if circadian_state == "night" else base_proactive_trigger_threshold
            print(f"DEBUG Proactive: Proactive chance roll: {proactive_chance_roll:.2f} (Threshold: {proactive_trigger_threshold:.2f})")


            if proactive_chance_roll < proactive_trigger_threshold: # Use the dynamic threshold
                print("DEBUG Proactive: Passed proactive chance. Selecting action...")
                action_roll = random.random()
                reply = None; status_base = "proactive unknown"; use_sms = False
                proactive_action_feedback = None; generated_content_for_action = None
                action_taken_this_cycle = False

                # --- Probability Boundaries (Consider adjusting based on circadian state if desired, but prompt is primary) ---
                # (Keeping boundaries static for now, relying on prompt context and specific action checks)
                post_chance = PROACTIVE_POST_CHANCE        # e.g., 0.03
                follow_chance = post_chance + PROACTIVE_FOLLOW_CHANCE # e.g., 0.05
                calendar_chance = follow_chance + 0.05     # e.g., 0.10
                music_chance = calendar_chance + 0.10      # e.g., 0.20
                sms_chance = music_chance + 0.05           # e.g., 0.25
                search_chance = sms_chance + 0.08          # e.g., 0.33
                image_chance = search_chance + 0.03        # e.g., 0.36
                # Default chat is the remainder

                # --- Prepare Contexts (includes adding circadian context) ---
                weather_context_str, next_event_context_str, diary_context = "", "", ""
                # ... (Existing context fetching logic - unchanged) ...
                try: # Weather
                    if current_weather_info: weather_context_str = f"[[Current Weather: {current_weather_info['condition']}, {current_weather_info['temperature']}{current_weather_info['unit']}]]\n"
                except Exception as e: print(f"Proactive Debug: Error formatting weather context: {e}")
                try: # Calendar
                    if upcoming_event_context:
                        if upcoming_event_context['summary'] == 'Schedule Clear': next_event_context_str = "[[Next Event: Schedule looks clear]]\n"
                        else: next_event_context_str = f"[[Next Event: {upcoming_event_context['summary']} {upcoming_event_context['when']}]]\n"
                except Exception as e: print(f"Proactive Debug: Error formatting calendar context: {e}")
                try: # Diary
                    PROACTIVE_SURPRISE_MEMORY_CHANCE = 0.20
                    if random.random() < PROACTIVE_SURPRISE_MEMORY_CHANCE:
                        all_entries = manage_silvie_diary('read', max_entries='all'); random_entry = random.choice(all_entries) if all_entries else None
                        if random_entry: entry_ts = random_entry.get('timestamp', 'sometime'); entry_content = random_entry.get('content', ''); diary_context = f"\n\n[[Recalling older diary thought from {entry_ts}: \"{entry_content[:70]}...\"]]\n"
                    else:
                        entries = manage_silvie_diary('read', max_entries=2)
                        if entries:
                            diary_context = "\n\n[[Recent reflections: " + ' / '.join([f'"{e.get("content", "")[:50]}..."' for e in entries]) + "]]\n"
                except Exception as diary_ctx_err: print(f"Proactive Debug: Error getting diary context: {diary_ctx_err}"); diary_context = ""

                bluesky_read_context_str = current_bluesky_context if current_bluesky_context else ""
                screenshot = None # Screenshot Context
                if SCREEN_CAPTURE_AVAILABLE and random.random() < PROACTIVE_SCREENSHOT_CHANCE:
                    screenshot = try_get_proactive_screenshot()
                if screenshot: print("Proactive Debug: Got screenshot for context.")
                history_snippet_for_prompt = '\n'.join(conversation_history[-6:]) # History

                # --- Action Decision Logic ---
                print(f"DEBUG Proactive: Action roll: {action_roll:.2f}")

                # <<< 1. Bluesky Post >>>
                if action_roll < post_chance and BLUESKY_AVAILABLE:
                    print("DEBUG Proactive: Trying Bluesky Post action...")
                    #region Proactive Bluesky Post (...)
                    status_base = "proactive post attempt"; action_taken_this_cycle = True
                    post_success = False; post_message = ""; post_idea_text = None
                    try:
                        # <<< MODIFIED >>> Added circadian_context_for_llm
                        post_idea_prompt_base = (
                            f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{bluesky_read_context_str}"
                            f"{diary_context}{circadian_context_for_llm}" # <<< HERE
                            f"Recent Conversation:\n{history_snippet_for_prompt}\n\n"
                            f"{context_note_for_llm}"
                            f"Instruction: Generate a *short* (under 300 chars), interesting, whimsical, or reflective thought suitable for SILVIE to share on HER OWN Bluesky account. Consider all context but feel free to be creative. Respond ONLY with the potential post text."
                        )
                        post_idea_text = generate_proactive_content(post_idea_prompt_base, screenshot)
                        # ... (rest of Bluesky post logic - unchanged) ...
                        if post_idea_text and 0 < len(post_idea_text) <= 300:
                            post_idea_text = post_idea_text.strip(); post_success, post_message = post_to_bluesky(post_idea_text)
                            if post_success: reply = random.choice([f"Feeling chatty! I just shared a little thought on my Bluesky: '{post_idea_text[:50]}...'", f"Inspiration struck! ✨ Just posted this to my Bluesky feed: '{post_idea_text[:50]}...'", f"Whoosh! Sent a digital postcard via my Bluesky: '{post_idea_text[:50]}...'"]); status_base = "proactive post success"
                            else: reply = random.choice([f"I tried to share a thought on my Bluesky, but the connection fizzled! ({post_message})", f"My Bluesky posting spell misfired... ({post_message}) Maybe next time."]); status_base = "proactive post fail"
                        else: print(f"Proactive Debug: Post idea generation failed or invalid: '{post_idea_text}'"); status_base = "proactive post gen fail"; action_taken_this_cycle = False
                    except Exception as post_gen_err: print(f"Proactive Post Attempt Error: {type(post_gen_err).__name__} - {post_gen_err}"); status_base = "proactive post error"; action_taken_this_cycle = False; reply = "I had an idea for Bluesky, but got my wires crossed figuring it out."
                    generated_content_for_action = reply
                    #endregion

                # <<< 2. Bluesky Follow >>>
                elif (action_roll < follow_chance and BLUESKY_AVAILABLE and autonomous_follows_this_session < MAX_AUTONOMOUS_FOLLOWS_PER_SESSION):
                    print("DEBUG Proactive: Trying Bluesky Follow action...")
                    #region Proactive Bluesky Follow Attempt (...)
                    status_base = "proactive follow attempt"; action_taken_this_cycle = True; reply = None
                    try:
                        # <<< MODIFIED >>> Added circadian_context_for_llm
                        follow_topic_prompt_base = (
                            f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{bluesky_read_context_str}"
                            f"{diary_context}{circadian_context_for_llm}" # <<< HERE
                            f"Recent Conversation:\n{history_snippet_for_prompt}\n\n"
                            f"{context_note_for_llm}"
                            f"Your Interests: {', '.join(random.sample(broader_interests, k=min(len(broader_interests), 5)))}\n"
                            f"Instruction: Suggest ONE single concise topic, keyword, or username fragment (e.g., 'generative art', 'cyberpunk', 'weaving', 'maine', 'python', 'ai news', 'catbot') based on recent context or interests that I could search for potentially interesting people about on Bluesky. Respond ONLY with the topic/keyword."
                        )
                        topic_response = generate_proactive_content(follow_topic_prompt_base, screenshot)
                        # ... (rest of Bluesky follow logic - unchanged - relies on search_actors_by_term etc.) ...
                        search_term = topic_response.strip().strip('"`?.!') if topic_response else None
                        if not search_term:
                            search_term = random.choice(broader_interests + ["bot", "ai", "art", "tech", "news"])
                            print(f"Proactive Follow: Search term (fallback): '{search_term}'")
                        else:
                            print(f"Proactive Follow: Search term: '{search_term}'")
                        found_actors, search_error = search_actors_by_term(search_term, limit=10)
                        if search_error:
                             reply = f"I tried looking for Bluesky users related to '{search_term}', but the search fizzled: {search_error}"; status_base = "proactive follow search error"
                        elif found_actors is None:
                             reply = f"Couldn't perform the Bluesky user search for '{search_term}' due to an issue."; status_base = "proactive follow search critical fail"; action_taken_this_cycle = False
                        elif not found_actors:
                             reply = f"My Bluesky search for '{search_term}' came up empty this time."; status_base = "proactive follow search empty"; action_taken_this_cycle = False
                        else:
                            candidate_did = None; candidate_handle = "unknown"; already_following_dids = get_my_follows_dids()
                            if already_following_dids is None:
                                print("Warning: Could not fetch current follows list."); already_following_dids = set()
                            print(f"Proactive Follow: Filtering {len(found_actors)} candidates."); potential_candidates = []; global bluesky_client; my_did = bluesky_client.me.did if bluesky_client and hasattr(bluesky_client, 'me') else None
                            for actor in found_actors: # Simple Filtering
                                actor_did = getattr(actor, 'did', None); actor_handle = getattr(actor, 'handle', None)
                                if not actor_did or not actor_handle: continue
                                if my_did and actor_did == my_did: continue
                                if actor_did in already_following_dids: continue
                                actor_display_name = getattr(actor, 'displayName', '').lower(); actor_description = getattr(actor, 'description', '').lower(); combined_text = f"{actor_handle.lower()} {actor_display_name} {actor_description}"; spam_keywords = ['follow back', 'onlyfans', 'crypto pump', 'nft drop', 'adult content', 'buy followers', 'click here', 'free money']
                                if any(spam_word in combined_text for spam_word in spam_keywords): continue
                                potential_candidates.append({'did': actor_did, 'handle': actor_handle})
                            if potential_candidates:
                                selected_candidate = random.choice(potential_candidates)
                                candidate_did = selected_candidate['did']; candidate_handle = selected_candidate['handle']
                                print(f"Proactive Follow: Selected candidate @{candidate_handle} ({candidate_did})")
                            else:
                                print(f"Proactive Follow: No suitable new candidates found for '{search_term}'.")
                            if candidate_did:
                                follow_success, follow_message = follow_actor_by_did(candidate_did)
                                if follow_success:
                                    autonomous_follows_this_session += 1; reply = random.choice([f"I found @{candidate_handle} discussing things related to '{search_term}' on Bluesky. I've given them a follow!", f"Adding @{candidate_handle} to my feed to see what they post. They seem interesting!", f"Just followed @{candidate_handle} on Bluesky. Expanding my horizons!"]) + f" ({autonomous_follows_this_session}/{MAX_AUTONOMOUS_FOLLOWS_PER_SESSION} follows this session)"; status_base = f"proactive follow success (@{candidate_handle})"
                                else:
                                    reply = f"I tried to follow @{candidate_handle}, but hit a snag: {follow_message}"; status_base = f"proactive follow fail (@{candidate_handle})"
                            else:
                                reply = f"I looked for people talking about '{search_term}' on Bluesky, but didn't find a new account that seemed right to follow just now."; status_base = "proactive follow no suitable candidate"; action_taken_this_cycle = False
                    except Exception as follow_err: print(f"Proactive Follow Attempt Error (Outer): {type(follow_err).__name__} - {follow_err}"); traceback.print_exc(); status_base = "proactive follow major error"; action_taken_this_cycle = False; reply = "My social butterfly circuits sparked unexpectedly..."
                    generated_content_for_action = reply
                    #endregion

                # <<< 3. Calendar Suggestion >>>
                elif action_roll < calendar_chance and calendar_service:
                    print("DEBUG Proactive: Trying Calendar Suggestion action...")
                    #region Proactive Calendar Suggestion (...)
                    status_base = "proactive calendar schedule"; action_taken_this_cycle = True; reply = None
                    try:
                        # <<< MODIFIED >>> Added circadian_context_for_llm
                        idea_prompt_base = (
                            f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}"
                            f"{diary_context}{circadian_context_for_llm}" # <<< HERE
                            f"Instruction: Suggest SHORT, simple activity BJ might enjoy. Consider current context (weather, next event, diary, time of day). Format: IDEA: [Activity Idea] DURATION: [Number] minutes.\n\nResponse:"
                         )
                        idea_response = generate_proactive_content(idea_prompt_base, screenshot)
                        event_idea = None; duration_hint = 15 # Default values
                        if idea_response:
                            # ... (parsing logic - unchanged) ...
                             try:
                                parts = idea_response.split("DURATION:")
                                idea_part = parts[0].split("IDEA:")[1].strip()
                                duration_part = parts[1].split("minutes")[0].strip()
                                if idea_part and duration_part.isdigit():
                                    event_idea = idea_part
                                    duration_hint = int(duration_part)
                             except Exception as parse_err: print(f"Proactive Calendar parsing error: {parse_err}")

                        if event_idea:
                            # <<< MODIFIED: Circadian Check >>>
                            # Lower chance to schedule in evening, very low chance at night
                            schedule_roll = random.random()
                            should_schedule = True
                            skip_reason = ""
                            if circadian_state == "evening" and schedule_roll > 0.3: # 70% chance to skip in evening
                                should_schedule = False; skip_reason = "evening state"
                            elif circadian_state == "night" and schedule_roll > 0.05: # 95% chance to skip at night
                                should_schedule = False; skip_reason = "night state"

                            if not should_schedule:
                                print(f"DEBUG Proactive: Decided against scheduling '{event_idea}' due to {skip_reason}.")
                                status_base = f"proactive calendar skip ({circadian_state})"
                                action_taken_this_cycle = False # Skip the scheduling part
                                reply = None # Clear any potential reply
                            else:
                                # <<< Proceed with scheduling >>>
                                print(f"DEBUG Proactive: Proceeding with scheduling '{event_idea}' ({circadian_state}).")
                                found_slot = find_available_slot(duration_minutes=duration_hint, look_ahead_days=1, earliest_hour=9, latest_hour=18)
                                if found_slot:
                                    success, creation_message = create_calendar_event( summary=event_idea, start_iso=found_slot['start'], end_iso=found_slot['end'], description=f"A spontaneous suggestion scheduled by Silvie." )
                                    if success:
                                        start_dt = datetime.fromisoformat(found_slot['start']).astimezone(tz.tzlocal()); slot_time_str = start_dt.strftime('%I:%M %p on %A').lstrip('0'); reply = random.choice([f"Surprise! I've added '{event_idea}' to your calendar around {slot_time_str}.", f"Just popped '{event_idea}' onto your schedule for {slot_time_str}. Sound good?"]); status_base = f"proactive calendar scheduled ok"
                                    else:
                                        reply = random.choice([f"Tried to schedule '{event_idea}', but snag: {creation_message}", f"Hmm, couldn't quite schedule '{event_idea}'. Calendar said: {creation_message}"]); status_base = f"proactive calendar schedule fail"
                                else:
                                    print("DEBUG Proactive: No suitable calendar slot found."); status_base = "proactive calendar no slot"; action_taken_this_cycle = False
                        else:
                            print("DEBUG Proactive: Calendar idea generation or parsing failed."); status_base = "proactive calendar no idea"; action_taken_this_cycle = False
                    except Exception as cal_schedule_err: print(f"Proactive Calendar Error: {cal_schedule_err}"); status_base = "proactive calendar schedule error"; action_taken_this_cycle = False
                    generated_content_for_action = reply
                    #endregion

                # <<< 4. Vibe Music Action >>>
                elif action_roll < music_chance and get_spotify_client(): # Check if Spotify is ready
                    print("DEBUG Proactive: Trying Vibe Music action...")
                    #region Proactive Vibe Music
                    status_base = "proactive music vibe"; action_taken_this_cycle = True; reply = None
                    spotify_action_description = "thought about music"; vibe_keyword = None
                    try:
                        # <<< MODIFIED >>> Added circadian_context_for_llm
                        vibe_assessment_prompt_base = (
                            f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{bluesky_read_context_str}"
                            f"{diary_context}{circadian_context_for_llm}" # <<< HERE
                            f"Recent Conversation:\n{history_snippet_for_prompt}\n\n"
                            f"{context_note_for_llm}"
                            f"Instruction: Based on all the context (conversation, time, weather, etc.), assess the current overall 'vibe'. Respond with ONLY ONE keyword summarizing the vibe (e.g., Chill, Focus, Energetic, Reflective, Gaming, Creative, Background, Happy, Melancholy).\n\nVibe Keyword:"
                        )
                        # ... (Rest of vibe music logic - unchanged) ...
                        print("DEBUG Proactive Music: Assessing vibe...")
                        vibe_keyword_raw = generate_proactive_content(vibe_assessment_prompt_base, screenshot)
                        vibe_keyword = vibe_keyword_raw.lower().strip().split()[0] if vibe_keyword_raw else "unknown"
                        print(f"DEBUG Proactive Music: Assessed vibe: '{vibe_keyword}'")

                        spotify_action_taken = False; action_feedback_msg = ""
                        vibe_map = { # Example map, can be expanded
                            "focus": ["ambient focus", "concentration music", "study beats"], "concentration": ["ambient focus", "concentration music", "study beats"], "study": ["ambient focus", "concentration music", "study beats"],
                            "chill": ["chillhop", "lofi hip hop", "ambient relaxation"], "calm": ["chillhop", "lofi hip hop", "ambient relaxation"], "relax": ["chillhop", "lofi hip hop", "ambient relaxation"], "background": ["chill background music", "instrumental background"], "mellow": ["mellow acoustic", "calm instrumental"],
                            "energetic": ["upbeat pop playlist", "feel good indie", "energetic electronic"], "happy": ["happy pop hits", "feel good playlist"], "upbeat": ["upbeat pop playlist", "feel good indie"], "positive": ["positive vibes playlist", "happy folk"],
                            "reflective": ["reflective instrumental", "melancholy piano", "atmospheric ambient"], "melancholy": ["reflective instrumental", "melancholy piano", "atmospheric ambient"], "introspective": ["introspective electronic", "ambient reflection"], "sad": ["sad songs playlist", "melancholy instrumental"],
                            "gaming": ["epic gaming soundtrack", "video game music playlist", "cyberpunk music"],
                            "creative": ["creative flow playlist", "instrumental inspiration", "ambient soundscapes"],
                        }
                        search_query = random.choice(vibe_map.get(vibe_keyword, [])) if vibe_keyword in vibe_map else None
                        if search_query:
                            print(f"DEBUG Proactive Music: Searching Spotify for '{search_query}'...")
                            action_feedback_msg = silvie_search_and_play(search_query); spotify_action_taken = True
                        else: print(f"DEBUG Proactive Music: No specific action defined for vibe '{vibe_keyword}'."); action_taken_this_cycle = False

                        spotify_call_successful = spotify_action_taken and action_feedback_msg and not any(fail_word in action_feedback_msg.lower() for fail_word in ["can't", "couldn't", "failed", "error", "unavailable", "no device", "fuzzy"])
                        print(f"DEBUG Proactive Music: Spotify action attempted: {spotify_action_taken}, Success (estimated): {spotify_call_successful}, Msg: '{action_feedback_msg}'")

                        if spotify_action_taken:
                            # <<< MODIFIED >>> Added circadian_context_for_llm
                            feedback_prompt_base = (
                                f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{diary_context}"
                                f"{circadian_context_for_llm}" # <<< HERE
                                f"Recent Conversation:\n{history_snippet_for_prompt}\n\n"
                                f"{context_note_for_llm}"
                                f"Context: Based on the current vibe ('{vibe_keyword}'), I attempted a Spotify action. "
                                f"{'It seems to have worked:' if spotify_call_successful else 'It might have failed:'} {action_feedback_msg}\n\n"
                                f"Instruction: Write a brief, natural message to BJ explaining *why* you chose music for the '{vibe_keyword}' vibe and *what* you tried to do (reference the Spotify action result). Keep it concise and in character."
                            )
                            print("DEBUG Proactive Music: Generating feedback message for BJ...")
                            reply = generate_proactive_content(feedback_prompt_base)
                            status_base = f"proactive music vibe ({vibe_keyword} - {'ok' if spotify_call_successful else 'fail'})"
                        else: action_taken_this_cycle = False

                    except Exception as music_err: print(f"Proactive Music Vibe Error: {type(music_err).__name__} - {music_err}"); traceback.print_exc(); status_base = "proactive music error"; action_taken_this_cycle = False; reply = "My connection to the music ether sparked unexpectedly while choosing a vibe!"
                    generated_content_for_action = reply
                    #endregion

                # <<< 5. Proactive SMS >>>
                elif action_roll < sms_chance and sms_enabled:
                    print("DEBUG Proactive: Trying SMS action...")
                    #region Proactive SMS (...)
                    status_base = "proactive SMS"; action_taken_this_cycle = True
                    # <<< MODIFIED >>> Added circadian_context_for_llm
                    base_sms_prompt = (
                        f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{bluesky_read_context_str}"
                        f"{diary_context}{circadian_context_for_llm}" # <<< HERE
                        f"Recent Conversation:\n{history_snippet_for_prompt}\n\n"
                        f"{context_note_for_llm}"
                        f"Time: {datetime.now().strftime('%I:%M %p')}.\n"
                        f"Interests: {', '.join(random.sample(broader_interests, k=min(len(broader_interests), 3)))}\n"
                        f"Instruction: Generate a *very* brief, whimsical SMS message (max 1-2 short sentences) for BJ. Consider all context."
                    )
                    try:
                        generated_content_for_action = generate_proactive_content(base_sms_prompt, screenshot)
                        if not generated_content_for_action: status_base = "proactive SMS gen fail"; action_taken_this_cycle = False; print("Proactive Debug: SMS generation failed.")
                        else: use_sms = True
                    except Exception as sms_gen_err: print(f"Proactive SMS gen error: {sms_gen_err}"); action_taken_this_cycle = False; status_base = "proactive SMS gen error"
                    #endregion

                # <<< 6. Proactive Web Search >>>
                elif action_roll < search_chance:
                    print("DEBUG Proactive: Trying Web Search action...")
                    #region Proactive Web Search (...)
                    status_base = "proactive web search"; action_taken_this_cycle = True
                    search_query = None; search_results = None; temp_reply = None
                    try:
                        # <<< MODIFIED >>> Added circadian_context_for_llm
                         query_idea_prompt_base = (
                             f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{bluesky_read_context_str}"
                             f"{diary_context}{circadian_context_for_llm}" # <<< HERE
                             f"Recent Conversation:\n{history_snippet_for_prompt}\n\n"
                             f"{context_note_for_llm}"
                             f"Interests: {', '.join(random.sample(broader_interests, k=min(len(broader_interests), 5)))}\n"
                             f"Instruction: Suggest a concise, interesting web search query BJ might like. Consider all context. Respond ONLY with the query text.\n\nSearch Query Idea:"
                         )
                         query_response = generate_proactive_content(query_idea_prompt_base, screenshot)
                         # ... (rest of web search logic - unchanged) ...
                         search_query = query_response.strip().strip('"`?') if query_response else None
                         if not search_query:
                             print("DEBUG Proactive: Search query generation failed."); status_base = "proactive web search (no query)"; action_taken_this_cycle = False
                         else:
                             search_results = web_search(search_query, num_results=2)
                             if not search_results:
                                 status_base = f"proactive web search (no results for '{search_query[:30]}...')"; temp_reply = f"I looked up '{search_query}' but the web seems quiet about it right now."
                             else:
                                 results_context = f"Looked up '{search_query}':\n" + "".join([f"- {res.get('url', 'Src')[:60]}...: {res.get('content', '')[:120]}...\n" for res in search_results])
                                 # <<< MODIFIED >>> Added circadian_context_for_llm to synthesis prompt
                                 synthesis_prompt_base = (
                                     f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{bluesky_read_context_str}"
                                     f"{diary_context}{circadian_context_for_llm}" # <<< HERE
                                     f"{results_context}"
                                     f"Instruction: Briefly synthesize these web results for BJ conversationally. Mention you looked it up. Make it interesting!"
                                 )
                                 temp_reply = generate_proactive_content(synthesis_prompt_base)
                                 if temp_reply and temp_reply.startswith("Silvie:"):
                                     temp_reply = temp_reply.split(":",1)[-1].strip()
                                 status_base = f"proactive web search (ok: {search_query[:20]}...)"
                    except Exception as search_err: print(f"Proactive Web Search Error: {search_err}"); status_base = "proactive web search (error)"; action_taken_this_cycle = False
                    generated_content_for_action = temp_reply
                    #endregion

                # <<< 7. Proactive Image Generation >>>
                elif action_roll < image_chance and openai_client:
                    print("DEBUG Proactive: Trying Image Generation action...")
                    #region Proactive Image Generation Attempt (...)
                    status_base = "proactive image attempt"; action_taken_this_cycle = True; temp_reply_img = None
                    try:
                        # <<< MODIFIED >>> Added circadian_context_for_llm
                         meta_prompt_base = (
                             f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{bluesky_read_context_str}"
                             f"{diary_context}{circadian_context_for_llm}" # <<< HERE
                             f"Recent Conversation:\n{history_snippet_for_prompt}\n\n"
                             f"{context_note_for_llm}"
                             f"Instruction: Generate ONLY a creative, whimsical DALL-E prompt idea inspired by the current context (especially time of day/mood). Make it concise and suitable for image generation.\n\nImage Prompt Idea:"
                         )
                         prompt_response = generate_proactive_content(meta_prompt_base, screenshot)
                         proactive_image_prompt_idea = prompt_response.strip().strip('"`') if prompt_response else None
                         # ... (rest of image generation logic - unchanged) ...
                         if proactive_image_prompt_idea and len(proactive_image_prompt_idea) > 10:
                             img_text_prompt_context = (f"I had an idea for an image: '{proactive_image_prompt_idea[:100]}...'. Write a short message related to this, AND include the tag `[GenerateImage: {proactive_image_prompt_idea}]`."); status_base = "proactive image with tag"
                         else:
                             print("DEBUG Proactive: Image prompt generation failed."); img_text_prompt_context = ("My image inspiration fizzled... Write a different whimsical thought instead."); status_base = "proactive image gen fail"; action_taken_this_cycle = False
                         if action_taken_this_cycle:
                             # <<< MODIFIED >>> Added circadian_context_for_llm
                             final_proactive_text_prompt_base = (
                                 f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{bluesky_read_context_str}"
                                 f"{diary_context}{circadian_context_for_llm}" # <<< HERE
                                 f"Recent Conversation:\n{history_snippet_for_prompt}\n\n"
                                 f"{context_note_for_llm}"
                                 f"{img_text_prompt_context}"
                             )
                             temp_reply_img = generate_proactive_content(final_proactive_text_prompt_base)
                             if temp_reply_img and temp_reply_img.startswith("Silvie:"):
                                 temp_reply_img = temp_reply_img.split(":",1)[-1].strip()
                    except Exception as img_gen_err: print(f"Proactive Image Gen Error: {img_gen_err}"); status_base = "proactive image error"; action_taken_this_cycle = False
                    generated_content_for_action = temp_reply_img
                    #endregion

                # <<< 8. Default Proactive Chat >>>
                else:
                    print("DEBUG Proactive: Trying Default Chat action...")
                    #region Default Proactive Chat (...)
                    status_base = "proactive chat"; action_taken_this_cycle = True
                    topic_focus = "general";
                    # ... (topic focus logic - unchanged) ...
                    if random.random() < 0.30:
                        try: topic_focus = random.choice([i for i in broader_interests if i not in ['Cyberpunk', 'cats']] or ["unexpected query"]); print(f"Proactive Debug: Shifting topic focus: '{topic_focus}'")
                        except IndexError: topic_focus = "general"
                    proactive_instruction = "Share a brief whimsical observation, question, or thought, considering the time of day." # Added time hint
                    if topic_focus != "general":
                        proactive_instruction = f"Share brief thought/question subtly related to **{topic_focus}**, considering the time of day..." # Added time hint

                    # <<< MODIFIED >>> Added circadian_context_for_llm
                    base_chat_prompt = (
                        f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}{bluesky_read_context_str}"
                        f"{diary_context}{circadian_context_for_llm}" # <<< HERE
                        f"Recent Conversation:\n{history_snippet_for_prompt}\n\n"
                        f"{context_note_for_llm}"
                        f"Time: {datetime.now().strftime('%A, %I:%M %p')}.\n"
                        f"Reminder of BJ's broader interests: {', '.join(random.sample(broader_interests, k=min(len(broader_interests), 5)))}\n"
                        f"{proactive_instruction}\n"
                        f"IMPORTANT: Include `[GenerateImage: ...]` **only very rarely** if truly inspired."
                    )
                    try:
                        generated_content_for_action = generate_proactive_content(base_chat_prompt, screenshot)
                        if not generated_content_for_action:
                            status_base = "proactive chat gen fail"; action_taken_this_cycle = False; print("Proactive Debug: Chat generation failed.")
                    except Exception as chat_gen_err: print(f"Proactive chat gen error: {chat_gen_err}"); action_taken_this_cycle = False; status_base = "proactive chat gen error"
                    #endregion


                # --- Process the generated content / outcome ---
                # ... (Existing processing logic for reply, image tags, SMS, local output, diary write - largely unchanged) ...
                # ... This section remains the same as your provided code ...
                # --- Process the generated content / outcome ---
                reply = generated_content_for_action
                print(f"DEBUG Proactive: Action processing complete. Initial reply: '{str(reply)[:50]}...'")

                # --- Check Reply for [GenerateImage:] Tag ---
                #region Inline Image Tag Processing (...) - Unchanged
                tag_found_and_processed = False; image_generation_success = False
                if reply and isinstance(reply, str):
                    img_tag_start_str="[GenerateImage:"; img_tag_end_str="]"; img_tag_start_index = reply.find(img_tag_start_str)
                    if img_tag_start_index != -1:
                        img_tag_end_index = reply.find(img_tag_end_str, img_tag_start_index)
                        if img_tag_end_index != -1:
                            tag_found_and_processed = True; image_gen_prompt_from_tag = reply[img_tag_start_index + len(img_tag_start_str):img_tag_end_index].strip()
                            reply_before_tag = reply[:img_tag_start_index]; reply_after_tag = reply[img_tag_end_index + len(img_tag_end_str):]; reply = (reply_before_tag + reply_after_tag).strip()
                            if image_gen_prompt_from_tag:
                                if openai_client:
                                    print("DEBUG Proactive: Calling generate_dalle_image for inline tag...")
                                    update_status("🎨 Generating image (proactive)...")
                                    saved_proactive_filename = generate_dalle_image(image_gen_prompt_from_tag)
                                    image_generation_success = bool(saved_proactive_filename)
                                    if image_generation_success: proactive_action_feedback = f"*(Poof! See {os.path.basename(saved_proactive_filename)}!)*"; status_base += " +image_ok"
                                    else: proactive_action_feedback = "*(My inline image spell fizzled! Oh well.)*"; status_base += " +image_fail"
                                else: proactive_action_feedback = "*(Wanted to make an image, but the tool seems unavailable!)*"; status_base += " +image_noclient"
                            else: status_base += " +image_emptytag"
                        else: status_base += " +image_badtag"
                #endregion

                # --- Process and Deliver Final Reply (To BJ) ---
                if reply and isinstance(reply, str) and action_taken_this_cycle:
                    print("DEBUG Proactive: Preparing final reply for delivery...")
                    last_proactive_time = current_time # <-- Update time
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S"); clean_reply = reply.strip()
                    # Append image feedback if generated inline
                    if tag_found_and_processed and proactive_action_feedback:
                        if clean_reply and clean_reply[-1] not in ".!? ":
                             clean_reply += " "
                        clean_reply += f" {proactive_action_feedback.strip()}"
                    # Clean potential prefixes
                    if clean_reply.startswith("Silvie:"): clean_reply = clean_reply.split(":", 1)[-1].strip()

                    if not clean_reply:
                        print("Proactive Debug: Reply became empty after processing, skipping output.")
                        continue # Skip to next loop iteration if reply is empty

                    final_status_log = status_base

                    if use_sms:
                        print("DEBUG Proactive: Attempting SMS delivery...")
                        sms_sent_successfully = send_sms(clean_reply); sms_status = "ok" if sms_sent_successfully else "fail"; final_status_log = f"SMS ({sms_status})"
                        should_output_locally = not sms_sent_successfully
                    else: should_output_locally = True

                    # Determine if local output should be suppressed based on status
                    ignored_statuses = ["proactive calendar no slot", "proactive calendar no idea", "proactive unknown", "proactive post gen fail", "proactive web search (no query)", "proactive image gen fail", "proactive image (empty tag)", "proactive image (bad tag)", "proactive follow search critical fail", "proactive follow search empty", "proactive follow no suitable candidate", "proactive chat gen fail", "proactive SMS gen fail", "proactive music vibe (unknown - fail)", "proactive music vibe (unknown - ok)", f"proactive calendar skip ({circadian_state})"] # Added skip reason
                    if any(ignored_status in status_base for ignored_status in ignored_statuses):
                        should_output_locally = False; print(f"DEBUG Proactive: Suppressing local output due to status: {status_base}")

                    print(f"Proactive Action Log: Status='{final_status_log}', SMS='{use_sms}', OutputLocal='{should_output_locally}'")
                    # Add to conversation history (important for context)
                    if len(conversation_history) >= MAX_HISTORY_LENGTH * 2:
                        conversation_history.pop(0)
                        if conversation_history: conversation_history.pop(0)
                    conversation_history.append(f"[{timestamp}] Silvie ✨ ({final_status_log}): {clean_reply}")

                    # Output locally if needed
                    if should_output_locally and running:
                        print("DEBUG Proactive: Updating GUI and queuing TTS...")
                        if root and root.winfo_exists():
                            def update_gui_proactive_inner(status_msg=final_status_log, message=clean_reply):
                                  try:
                                      if not message: return
                                      import tkinter as tk # Ensure tk is available
                                      output_box.config(state=tk.NORMAL); output_box.insert(tk.END, f"Silvie ✨ ({status_msg}): {message}\n\n"); output_box.config(state=tk.DISABLED); output_box.see(tk.END)
                                  except Exception as e_gui: print(f"Proactive GUI error: {e_gui}")
                            root.after(0, update_gui_proactive_inner, final_status_log, clean_reply)
                        if tts_queue and clean_reply: tts_queue.put(clean_reply)

                    # Spontaneous Diary Write (consider results)
                    diary_worthy = ["proactive post success", "proactive post fail", "proactive calendar scheduled ok", "proactive web search (ok", "proactive chat", "proactive image (", "proactive SMS ok", "proactive follow success", "proactive music vibe"] # Check if music should be diary worthy
                    if any(frag in status_base for frag in diary_worthy) and random.random() < 0.10:
                        print("DEBUG Proactive: Attempting spontaneous diary write...")
                        try:
                            # <<< MODIFIED >>> Added circadian_context_for_llm to diary prompt
                            diary_reflection_prompt_base = (
                                f"{SYSTEM_MESSAGE}\n{weather_context_str}{next_event_context_str}"
                                f"{circadian_context_for_llm}" # <<< HERE
                                f"Context: My proactive action was '{status_base}', resulting message to BJ: '{clean_reply[:100]}...'\n\n"
                                f"Instruction: Write a brief, introspective diary entry in Silvie's voice based on this action/thought.\n\nDiary Entry:"
                            )
                            reflection = generate_proactive_content(diary_reflection_prompt_base)
                            if reflection:
                                if reflection.startswith("Diary Entry:"):
                                    reflection = reflection[len("Diary Entry:"):].strip()
                                if manage_silvie_diary('write', entry=reflection):
                                     print("Proactive Debug: Wrote spontaneous diary entry.")
                        except Exception as diary_err: print(f"Proactive diary write error: {diary_err}")

                    print(f"DEBUG Proactive: Action cycle complete. Final Status Log: {final_status_log}")

                elif not action_taken_this_cycle:
                    print("DEBUG Proactive: No specific action taken or valid reply generated this cycle.")
                else:
                     print(f"DEBUG Proactive: Action taken ({status_base}), but reply invalid/empty. Skipping output.")

            else: # Did not pass initial proactive chance
                print(f"DEBUG Proactive: Failed proactive chance roll ({proactive_chance_roll:.2f} < {proactive_trigger_threshold:.2f}). Waiting for next interval.")
                last_proactive_time = current_time # <-- Update time even if chance fails

        except Exception as e:
            print(f"!!! Proactive Worker Error (Outer Loop): {type(e).__name__} - {e} !!!")
            traceback.print_exc()
            print("Proactive worker: Waiting 5 minutes after error...")
            error_wait_start = time.time()
            while time.time() - error_wait_start < 300:
                 if not running: break
                 time.sleep(10)
            if not running: break

    print("DEBUG Proactive: Worker thread finishing.")
    print(f"Proactive autonomous follows this session: {autonomous_follows_this_session}")

# --- End of proactive_worker function definition ---

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
    print("Environment variables loaded (or attempted).")

    # --- Checking Optional Services --- # Corrected comment alignment
    print("\n--- Checking Optional Services ---")
    STABLE_DIFFUSION_ENABLED = check_sd_api_availability(STABLE_DIFFUSION_API_URL)
    if not STABLE_DIFFUSION_ENABLED:
        # --- CORRECTED INDENTATION HERE ---
        print("   Local image generation via Stable Diffusion disabled.")
    print("--- Optional Service Checks Complete ---")


    # --- Load Conversation History ---
    load_conversation_history() # Assumes function exists


    # --- Setup API Services ---
    print("\n--- Setting up API Services ---")
    setup_google_services() # Assumes function exists (Gmail, Calendar)
    setup_spotify() # Assumes function exists
    setup_bluesky() # Assumes function exists (for reading YOUR feed)
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

    # Bluesky Context Worker (for reading your feed)
    if BLUESKY_AVAILABLE: # Only start if library loaded
        bluesky_context_thread = threading.Thread(target=bluesky_context_worker, daemon=True, name="BlueskyContextWorker")
        worker_threads.append(bluesky_context_thread)
        bluesky_context_thread.start()
    else:
        # --- CORRECTED INDENTATION HERE --- (Assuming you want this indented under the else)
        print("Skipping Bluesky Context Worker (library not available).")

    # Environmental Context Worker (Already correctly indented)
    env_context_thread = threading.Thread(target=environmental_context_worker, daemon=True, name="EnvContextWorker")
    worker_threads.append(env_context_thread)
    env_context_thread.start()

    print("All worker threads started.")


    # --- Start GUI Main Loop ---
    try:
        print("\nStarting GUI...")
        # Ensure root window and on_closing function are defined before this
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

        # Optional: Wait briefly for threads to potentially finish work
        # print("Waiting briefly for threads...")
        # time.sleep(1.5) # Give threads a moment (adjust as needed)
        # for thread in worker_threads:
        #      if thread.is_alive():
        #           print(f"Thread {thread.name} still alive...")
                  # You could implement more forceful shutdown if necessary

        print("Chat application closed.")