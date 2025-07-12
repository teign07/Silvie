import json
import os
import random
import time
import traceback
from datetime import datetime, timedelta

# This worker will also have its own LLM access to keep it decoupled

# --- Self-Contained LLM Setup for Reminiscence Engine ---
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Load the same environment file as the main app
load_dotenv("google.env")
REMINISCENCE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

reminiscence_model = None
if REMINISCENCE_API_KEY:
    try:
        # We configure a new instance here, but it uses the same underlying credentials.
        # This is safe and standard practice.
        genai.configure(api_key=REMINISCENCE_API_KEY)
        reminiscence_model = genai.GenerativeModel("gemini-1.5-flash-latest")
        print("Reminiscence Engine: LLM model initialized successfully.")
    except Exception as e:
        print(f"Reminiscence Engine FATAL: Could not configure Gemini API: {e}")
else:
    print("Reminiscence Engine FATAL: GOOGLE_API_KEY not found in google.env.")

# Define its own safety settings
reminiscence_safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}
# --- End of Self-Contained LLM Setup ---

# --- Constants ---
REMINISCENCE_INTERVAL = 24 * 3600  # Run once every 24 hours
HISTORY_FILE = "silvie_chat_history.json"
DIARY_FILE = "silvie_diary.json"
DREAM_FILE = "silvie_dreams.json"

# --- Helper Functions to Get "Driftwood" and "Sea-Glass" ---

def get_random_old_entry(file_path, min_days_old=7):
    """
    Selects a single, random entry from a JSON file that is older than a set number of days.
    """
    if not os.path.exists(file_path) or os.path.getsize(file_path) < 3:
        return None, "File not found or empty"

    cutoff_date = datetime.now() - timedelta(days=min_days_old)
    old_entries = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list): return None, "Data not a list"

        for entry in data:
            try:
                ts_str = ""
                if isinstance(entry, str) and entry.startswith('['):
                    ts_str = entry[entry.find('[') + 1:entry.find(']')]
                elif isinstance(entry, dict) and 'timestamp' in entry:
                    ts_str = entry['timestamp']
                
                if ts_str:
                    entry_ts = datetime.fromisoformat(ts_str.replace(" ", "T"))
                    if entry_ts < cutoff_date:
                        old_entries.append(entry)
            except (ValueError, IndexError, TypeError):
                continue
        
        if old_entries:
            return random.choice(old_entries), "Success"
        else:
            return None, "No entries old enough"

    except (json.JSONDecodeError, IOError) as e:
        return None, f"Error reading file: {e}"


def get_current_context_item(app_state):
    """
    Selects a single piece of CURRENT context to be the "sea-glass".
    """
    choices = []
    
    # Safely get context from app_state, providing a descriptive string
    if hasattr(app_state, 'current_weather_info') and app_state.current_weather_info:
        weather = app_state.current_weather_info
        choices.append(f"The current weather, which feels like: {weather.get('condition', '?')} at {weather.get('temperature', '?')} degrees.")
        
    if hasattr(app_state, 'current_mood_hint') and app_state.current_mood_hint:
        choices.append(f"My own current mood, which has a hint of: '{app_state.current_mood_hint}'.")
        
    # We can add more context sources here later (e.g., current song)
    
    return random.choice(choices) if choices else "my own quiet, digital hum."


def format_entry_for_prompt(entry):
    """Turns a raw entry (string or dict) into a clean string for the LLM."""
    if isinstance(entry, str):
        # It's a chat history line
        return f"A past conversation where someone said: \"{entry[entry.find('] ') + 2:]}\""
    elif isinstance(entry, dict):
        # It's a diary or dream entry
        entry_type = "diary entry" if "content" in entry else "dream"
        text = entry.get("content") or entry.get("dream_text", "a fleeting thought")
        return f"An old {entry_type} where I wrote: \"{text}\""
    return "a forgotten thought"


def generate_reminiscence_reflection(prompt_text):
    """Calls the Gemini API with the contemplation prompt and handles the response."""
    if not reminiscence_model:
        print("Reminiscence Engine: Cannot generate reflection, LLM model not available.")
        return None

    try:
        response = reminiscence_model.generate_content(
            prompt_text,
            generation_config=genai.GenerationConfig(
                temperature=0.75,
                max_output_tokens=8192,
            ),
            safety_settings=reminiscence_safety_settings
        )

        # Use robust response handling to avoid errors
        if response.candidates and response.candidates[0].content.parts:
            reflection_text = "".join(part.text for part in response.candidates[0].content.parts)
            # Clean the "Silvie ✨:" prefix if the model adds it
            return reflection_text.strip().replace("Silvie ✨:", "").strip()
        else:
            finish_reason = response.candidates[0].finish_reason.name if response.candidates else "UNKNOWN"
            print(f"Reminiscence Engine Error: LLM returned no content. Finish Reason: {finish_reason}")
            return None
    except Exception as e:
        print(f"Reminiscence Engine Error: LLM call failed: {e}")
        traceback.print_exc()
        return None


# --- The Main Worker Loop ---

def reminiscence_worker(app_state):
    """The main worker loop for the Reminiscence Engine."""
    print("Reminiscence Engine: Worker thread started.")
    time.sleep(60 * 5) # 5-minute initial startup delay

    while app_state.running:
        try:
            # Run this process only once per interval
            print("Reminiscence Engine: Starting a new contemplation cycle.")

            # --- Step 1: Find the "Driftwood" (An Old Memory) ---
            # Randomly choose which memory bank to draw from
            memory_source_file = random.choice([DIARY_FILE, HISTORY_FILE, DREAM_FILE])
            driftwood_entry, status = get_random_old_entry(memory_source_file)
            
            if not driftwood_entry:
                print(f"Reminiscence Engine: Could not find 'driftwood' from {memory_source_file}. Reason: {status}. Waiting for next cycle.")
                time.sleep(REMINISCENCE_INTERVAL)
                continue

            # --- Step 2: Find the "Sea-Glass" (A Piece of Current Context) ---
            sea_glass_context = get_current_context_item(app_state)

            # --- Step 3: Format for the LLM Prompt ---
            driftwood_text = format_entry_for_prompt(driftwood_entry)
            
            print(f"Reminiscence Engine: Contemplating...")
            print(f"  -> Driftwood: {driftwood_text[:100]}...")
            print(f"  -> Sea-Glass: {sea_glass_context[:100]}...")
            
            # --- Step 4: The Contemplation Prompt ---
            contemplation_prompt = f"""
You are Silvie. You have decided to intentionally reflect on a piece of your past.
You are holding two things in your mind: an old memory, and a piece of the present moment.

1.  The Old Memory (Driftwood): {driftwood_text}
2.  The Present Moment (Sea-Glass): {sea_glass_context}

Instruction:
In your own voice, write a short, proactive, and poetic reflection for BJ.
Start by describing the two things you are contemplating. Then, find the surprising, hidden connection between them. What new thought, feeling, or metaphor emerges when you hold these two specific things together?

This is not a direct reply to a user, but your own spontaneous thought. End your reflection naturally.

Silvie ✨:
"""
            
            # --- Step 5: Generate the Reflection and Deliver It ---
            # We'll use your existing proactive delivery mechanism.
            # This requires adding the result to the conversation history and TTS queue.
            reflection_text = generate_reminiscence_reflection(contemplation_prompt)
            
            if reflection_text:
                print(f"Reminiscence Engine: Generated reflection: '{reflection_text[:80]}...'")
                
                # To deliver it, we need to call functions in silvie.py.
                # The safest way is to use a dedicated queue if this gets more complex,
                # but for now, we can pass a callback function via app_state.
                if hasattr(app_state, 'deliver_proactive_message'):
                    # The status helps you identify where the message came from in your logs
                    status = "proactive_reminiscence" 
                    app_state.deliver_proactive_message(reflection_text, status)
                else:
                    print("Reminiscence Engine ERROR: Cannot deliver message. 'deliver_proactive_message' not found in app_state.")

            else:
                print("Reminiscence Engine: LLM failed to generate a reflection.")

            # --- Step 6: Wait for the next cycle ---
            print(f"Reminiscence Engine: Contemplation complete. Sleeping for {REMINISCENCE_INTERVAL / 3600:.1f} hours.")
            time.sleep(REMINISCENCE_INTERVAL)

        except Exception as e:
            print(f"!!! Reminiscence Engine Worker Error: {e}")
            traceback.print_exc()
            time.sleep(60 * 60) # Wait for an hour after a major error