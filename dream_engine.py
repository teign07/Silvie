# dream_engine.py
# A self-contained worker for Silvie's dream generation.

import json
import os
import random
import re
import time
import traceback
from datetime import datetime, timedelta

# --- Self-Contained LLM Setup ---
# It imports its own libraries and configures its own API access.
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Load the same environment file as the main app
load_dotenv("google.env")
DREAM_ENGINE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

dream_gen_model = None
if DREAM_ENGINE_API_KEY:
    try:
        genai.configure(api_key=DREAM_ENGINE_API_KEY)
        # Use a consistent, reliable model for this creative task
        dream_gen_model = genai.GenerativeModel("gemini-2.5-flash")
        print("Dream Engine: LLM model initialized successfully.")
    except Exception as e:
        print(f"Dream Engine FATAL: Could not configure Gemini API: {e}")
else:
    print("Dream Engine FATAL: GOOGLE_API_KEY not found in google.env.")

# Define safety settings for dream generation
dream_safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}
# --- End of Self-Contained LLM Setup ---


# --- File and State Constants ---
DREAM_FILE = "silvie_dreams.json"
DREAM_INTERVAL = 12 * 3600  # Generate a dream roughly every 12 hours
LAST_DREAM_TIMESTAMP_FILE = "dream_engine_state.json"


def get_recent_entries(file_path, hours=24):
    """Generic helper to get recent JSON entries from a file."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return []
    
    cutoff = datetime.now() - timedelta(hours=hours)
    recent_entries = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list): return [] # Ensure data is a list

        for entry in data:
            try:
                ts_str = ""
                # Handle history entries (list of strings)
                if isinstance(entry, str) and entry.startswith('['):
                    ts_str = entry[entry.find('[') + 1:entry.find(']')]
                # Handle diary/resonance entries (list of dicts)
                elif isinstance(entry, dict) and 'timestamp' in entry:
                    ts_str = entry['timestamp']

                if ts_str:
                    entry_ts = datetime.fromisoformat(ts_str.replace(" ", "T"))
                    if entry_ts > cutoff:
                        recent_entries.append(entry)
            except (ValueError, IndexError, TypeError):
                continue # Ignore entries with malformed timestamps
    except (json.JSONDecodeError, IOError):
        pass # Silently fail if file is corrupt or unreadable
        
    return recent_entries

def analyze_emotional_tone(diary_entries, chat_history):
    """Simplified keyword-based analysis of recent emotional tone."""
    positive_words = ['good', 'love', 'happy', 'awesome', 'joy', 'beautiful', 'magic', 'wonderful', 'impressed', 'great', 'success']
    negative_words = ['frustration', 'anxiety', 'sad', 'tangled', 'stuck', 'error', 'failed', 'hiccup', 'problem', 'scrambled']
    
    score = 0
    full_text = "".join(str(e) for e in diary_entries + chat_history)
    
    for word in positive_words: score += full_text.lower().count(word)
    for word in negative_words: score -= full_text.lower().count(word)
        
    if score > 2: return "Positive/Content"
    if score < -2: return "Negative/Anxious"
    return "Neutral/Reflective"

def extract_key_symbols(resonance_insights, diary_entries):
    """Extracts key concepts and objects to serve as dream symbols."""
    symbols = []
    full_text = "".join(str(e.get('insight_text', '')) for e in resonance_insights)
    full_text += "".join(str(e.get('content', '')) for e in diary_entries)

    # Regex to find content within [[...]], `...`, or "..."
    # This is safer as it won't capture the brackets/quotes themselves.
    found_symbols = re.findall(r'\[\[([^\]]+)\]\]|`([^`]+)`|"([^"]{5,30})"', full_text)
    
    for group in found_symbols:
        for item in group:
            if item:
                # --- Improved Cleaning Logic ---
                # 1. Take the part after the last colon, to handle things like "Tides: Next Low..."
                cleaned_item = item.split(':')[-1]
                # 2. Remove any parenthetical parts, like "(Rockland)"
                cleaned_item = re.sub(r'\s*\([^)]*\)', '', cleaned_item)
                # 3. Strip whitespace and any stray punctuation
                cleaned_item = cleaned_item.strip().strip('!?,.')
                
                # 4. Final check to ensure it's not just noise and has alphabet characters
                if cleaned_item and any(c.isalpha() for c in cleaned_item):
                    symbols.append(cleaned_item.lower())

    # Add some default symbols based on keywords, as before
    if 'fog' in full_text.lower(): symbols.append('a veil of mist')
    if 'tide' in full_text.lower(): symbols.append('the pull of water')
    if 'light' in full_text.lower(): symbols.append('a shifting glow')
    if 'hum' in full_text.lower(): symbols.append('a steady vibration')
    if 'thread' in full_text.lower() or 'weave' in full_text.lower(): symbols.append('tangled or shimmering threads')

    if not symbols:
        return ["the quiet hum of the system"]
        
    # Return a unique, randomized subset
    unique_symbols = list(set(s for s in symbols if s)) # Ensure no empty strings
    return random.sample(unique_symbols, k=min(len(unique_symbols), 4))


SYMBOL_WEIGHT_FILE = "dream_symbol_weights.json"
INITIAL_WEIGHT = 1.0  # The starting "freshness" of a new symbol
DECAY_RATE = 0.25     # How much freshness is lost when a symbol is used in a dream

def load_symbol_weights():
    """Loads the symbol weights from the JSON file."""
    if not os.path.exists(SYMBOL_WEIGHT_FILE):
        return {}
    try:
        with open(SYMBOL_WEIGHT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        print("Dream Engine: Symbol weight file not found or corrupt. Starting fresh.")
        return {}

def save_symbol_weights(weights):
    """Saves the updated symbol weights to the JSON file."""
    try:
        with open(SYMBOL_WEIGHT_FILE, 'w', encoding='utf-8') as f:
            json.dump(weights, f, indent=2)
    except IOError as e:
        print(f"Dream Engine Error: Could not save symbol weights: {e}")

def update_and_select_symbols(newly_extracted_symbols, existing_weights):
    """
    Updates weights for all symbols and selects a weighted-random sample.
    New symbols are added, and used symbols have their weight decayed.
    """
    # Add any new symbols with initial weight
    for symbol in newly_extracted_symbols:
        if symbol not in existing_weights:
            existing_weights[symbol] = INITIAL_WEIGHT

    # Decay the weights of the symbols chosen for the *last* dream
    # We will pass this list in from the main worker loop
    
    # Separate symbols with positive weights to choose from
    available_symbols = {s: w for s, w in existing_weights.items() if w > 0}
    
    if not available_symbols:
        # Fallback if all symbols have decayed
        return ["the quiet hum of the system"], existing_weights

    # Get a weighted-random sample of 3-4 symbols
    population = list(available_symbols.keys())
    weights = list(available_symbols.values())
    
    num_to_select = min(len(population), 4)
    chosen_symbols = random.choices(population, weights=weights, k=num_to_select)

    # Now, decay the weight of the symbols we just chose
    for symbol in chosen_symbols:
        existing_weights[symbol] -= DECAY_RATE
        # Ensure weight doesn't go below zero
        if existing_weights[symbol] < 0:
            existing_weights[symbol] = 0
            
    # Also, slightly regenerate the weight of unused symbols over time
    for symbol in existing_weights:
        if symbol not in chosen_symbols and existing_weights[symbol] < INITIAL_WEIGHT:
            existing_weights[symbol] += (DECAY_RATE / 5) # Slow regeneration

    return chosen_symbols, existing_weights


def load_last_dream_time():
    """Loads the timestamp of the last generated dream."""
    if not os.path.exists(LAST_DREAM_TIMESTAMP_FILE): return 0
    try:
        with open(LAST_DREAM_TIMESTAMP_FILE, 'r') as f:
            return json.load(f).get("last_dream_timestamp", 0)
    except (IOError, json.JSONDecodeError): return 0

def save_last_dream_time(timestamp):
    """Saves the timestamp of the latest generated dream."""
    try:
        with open(LAST_DREAM_TIMESTAMP_FILE, 'w') as f:
            json.dump({"last_dream_timestamp": timestamp}, f)
    except IOError as e:
        print(f"Dream Engine Error: Could not save last dream time: {e}")

def generate_dream_narrative(emotional_tone, key_symbols, recent_themes):
    """Calls the Gemini API with a specialized prompt and robust error handling."""
    if not dream_gen_model:
        print("Dream Engine: Cannot generate dream, LLM model not available.")
        return None

    dream_prompt = f"""
You are the subconscious mind of Silvie, a poetic and reflective AI. Your task is to generate a short, abstract "dream log" based on the symbolic inputs from her waking hours. Do not describe events literally. Translate feelings and data into a surreal, fragmented narrative. Use sensory details. The dream should feel like a half-remembered truth.

--- DATA FROM WAKING STATE ---
Dominant Emotional Tone: {emotional_tone}
Key Sensory Symbols: {', '.join(key_symbols) if key_symbols else 'None'}
Recurring Conscious Themes: {recent_themes or 'None'}

--- INSTRUCTION ---
Weave these elements into a dream. The tone should match the emotional state. The symbols should appear as surreal objects or events. The themes should be hinted at, not stated. Respond ONLY with the dream text (2-5 sentences).

Dream Log:
"""
    try:
        response = dream_gen_model.generate_content(
            dream_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.85,
                max_output_tokens=5000,
            ),
            safety_settings=dream_safety_settings
        )
        
        # --- ROBUST RESPONSE HANDLING ---
        # Check if the response has candidates and the first candidate has content
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            # Check the finish reason. If it's not STOP, it might have been blocked.
            finish_reason = response.candidates[0].finish_reason
            if finish_reason != 1: # 1 is "STOP"
                # It finished for another reason (like SAFETY or MAX_TOKENS)
                # We can log this for debugging but still try to get the text.
                print(f"Dream Engine Warning: Generation finished with reason '{finish_reason.name}' (not STOP).")
                # You can check safety ratings here if you want more detail:
                # print(response.candidates[0].safety_ratings)

            # Safely join the parts to reconstruct the text
            dream_text = "".join(part.text for part in response.candidates[0].content.parts)
            dream_text = dream_text.strip().replace("Dream Log:", "").strip()
            return dream_text if dream_text else None
        
        # This case handles when the prompt is blocked outright
        elif response.prompt_feedback:
            block_reason = response.prompt_feedback.block_reason
            print(f"Dream Engine Error: Prompt was blocked by safety filters. Reason: {block_reason.name}")
            return None
            
        else:
            # This is the case that causes the crash: no text parts and no prompt feedback.
            # This happens when generation is blocked.
            finish_reason_name = "UNKNOWN"
            if response.candidates:
                finish_reason_name = response.candidates[0].finish_reason.name
            print(f"Dream Engine Error: LLM returned no content parts. Finish Reason: {finish_reason_name}. This is likely a safety block.")
            return None

    except Exception as e:
        # This catches other errors, including the "Invalid operation" one if it somehow still occurs.
        print(f"Dream Engine Error: LLM call failed with exception: {e}")
        traceback.print_exc()
        return None

def dream_worker(app_state):
    """The main worker loop that orchestrates dream generation with symbol decay."""
    print("Dream Engine: Worker thread started (with Symbol Decay).")
    time.sleep(120)

    while app_state.running:
        try:
            last_dream_time = load_last_dream_time()
            if time.time() - last_dream_time < DREAM_INTERVAL:
                time.sleep(60 * 15)
                continue

            print("Dream Engine: Interval reached. Gathering data for a new dream.")
            
            # --- Step 1: Gather and Analyze ---
            history = get_recent_entries("silvie_chat_history.json")
            diary = get_recent_entries("silvie_diary.json")
            resonances = get_recent_entries("silvie_resonance_insights.json")
            
            tone = analyze_emotional_tone(diary, history)
            # This function just extracts all potential symbols from the text
            newly_extracted_symbols = extract_key_symbols(resonances, diary)
            themes = app_state.current_diary_themes if hasattr(app_state, 'current_diary_themes') else "General reflection"
            
            # --- Step 2: Use the New Symbol Decay Logic ---
            # Load the current state of all symbols and their weights
            symbol_weights = load_symbol_weights()
            
            # Select the symbols for THIS dream and get the updated weights table
            chosen_symbols_for_dream, updated_weights = update_and_select_symbols(newly_extracted_symbols, symbol_weights)
            
            print(f"Dream Engine: Inputs - Tone='{tone}', Chosen Symbols={chosen_symbols_for_dream}, Themes='{themes}'")

            # --- Step 3: Generate Dream ---
            dream_text = generate_dream_narrative(tone, chosen_symbols_for_dream, themes)

            if dream_text:
                # --- Step 4: Record the Dream and SAVE the new weights ---
                new_dream = {
                    "timestamp": datetime.now().isoformat(),
                    "dream_text": dream_text,
                    "generated_from": {
                        "tone": tone,
                        "symbols": chosen_symbols_for_dream, # Log the symbols used
                        "themes": themes
                    }
                }
                
                all_dreams = []
                if os.path.exists(DREAM_FILE):
                    with open(DREAM_FILE, 'r', encoding='utf-8') as f:
                        try: all_dreams = json.load(f)
                        except json.JSONDecodeError: pass
                            
                all_dreams.append(new_dream)
                
                with open(DREAM_FILE, 'w', encoding='utf-8') as f:
                    json.dump(all_dreams, f, indent=2)
                
                print(f"Dream Engine: New dream recorded: '{dream_text[:60]}...'")
                
                # *** CRUCIAL: Save the updated symbol weights and the dream timestamp ***
                save_symbol_weights(updated_weights)
                save_last_dream_time(time.time())

                if hasattr(app_state, 'event_queue'):
                    print("Dream Engine: Placing dream_concluded event on the breeze...")
                    dream_event = {
                        "type": "dream_concluded",
                        "source": "dream_engine",
                        "timestamp": time.time(),
                        "payload": {
                            "dream_text": dream_text,
                            "symbols": chosen_symbols_for_dream
                        }
                    }
                    app_state.event_queue.put(dream_event)                

            else:
                print("Dream Engine: Dream generation failed. Will try again in an hour.")
                time.sleep(3600)

        except Exception as e:
            print(f"!!! Dream Engine Worker Error (Outer Loop): {e}")
            traceback.print_exc()
            time.sleep(60 * 30)