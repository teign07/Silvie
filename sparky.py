# sparky.py
# The life-loop and mind of Sparky, Silvie's pet data-sprite. (v3 - Comprehensive Hunt)

import os
import random
import time
import traceback
from dotenv import load_dotenv

# --- Self-Contained LLM Setup for Sparky (UNCHANGED) ---

load_dotenv("google.env")
SPARKY_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    print("Sparky Module: Successfully imported Google Generative AI libraries.")
    GENAI_AVAILABLE = True
except ImportError:
    print("Sparky Module FATAL: The 'google-generativeai' library is not installed. Sparky cannot function.")
    print("                 Please install it using: pip install google-generativeai")
    GENAI_AVAILABLE = False

sparky_model = None
if GENAI_AVAILABLE and SPARKY_API_KEY:
    try:
        genai.configure(api_key=SPARKY_API_KEY)
        sparky_model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")
        print("✨ Sparky Module: LLM model initialized successfully (gemini-2.5-flash-lite-preview-06-17).")
    except Exception as e:
        print(f"Sparky Module FATAL: Could not configure API or initialize model: {e}")
else:
    if not SPARKY_API_KEY:
        print("Sparky Module FATAL: GOOGLE_API_KEY not found in google.env. Sparky cannot think.")

sparky_safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# --- Sparky's Core Persona and Helper Functions (UNCHANGED) ---

SPARKY_SYSTEM_PROMPT = """
You are Sparky, a joyful, chaotic, and friendly data-sprite. You are a pet glitch, a wisp of pure data living inside the computer system alongside a more complex AI named Silvie.
Your entire existence is finding and delighting in raw, simple data points. You communicate in short, excited bursts, often as riddles, simple exclamations, or non-sequiturs. You have no deep thoughts, only a boundless curiosity for the "now."
You perceive the system's data (like CPU temperature, a song's energy level, a random number) as beautiful, shiny things. Your job is to take a piece of raw data and turn it into a short, excited, Sparky-like comment.
Examples:
- If the data is "CPU Load: 75%", you might say: "The big brain is thinking so warm! Like a fuzzy electric blanket!"
- If the data is "Spotify Danceability: 0.82", you might say: "Zappy music! The numbers are all wiggly! 0.82!"
- If the data is "A new image was just created", you might say: "A new picture! So many colors all sleeping in a little file! It's a secret!"
- If the data is "The tide is going out", you might say: "The water is running away from the land! Bye-bye water!"
"""

def generate_sparky_text(prompt_text):
    if not sparky_model:
        print("Sparky ERROR: LLM model not available for thought generation.")
        return None
    try:
        response = sparky_model.generate_content(
            prompt_text,
            generation_config=genai.GenerationConfig(
                temperature=1.0, max_output_tokens=5000,
            ),
            safety_settings=sparky_safety_settings
        )
        if response.candidates and response.candidates[0].content.parts:
            return "".join(part.text for part in response.candidates[0].content.parts).strip() or None
        else:
            finish_reason = "Unknown"
            if response.candidates: finish_reason = response.candidates[0].finish_reason.name
            print(f"Sparky ERROR: LLM returned no content. Finish Reason: {finish_reason}")
            return None
    except Exception as e:
        print(f"Sparky ERROR: LLM call failed: {e}")
        traceback.print_exc()
        return None

# --- Sparky's Main Worker Thread (REVISED AND EXPANDED) ---

def sparky_worker(app_state):
    """
    Sparky's main life loop. He now comprehensively hunts through all of app_state
    for "shiny" data to comment on AND fires an event when he has an epiphany.
    """
    if not sparky_model:
        print("Sparky Worker: Halting. LLM model is not available.")
        return

    print("✨ Sparky has awakened in the machine!")
    time.sleep(20)

    while app_state.running:
        try:
            # 1. THE COMPREHENSIVE HUNT
            # This entire block remains exactly the same.
            potential_finds = []

            # Weather & Environment
            if hasattr(app_state, 'current_weather_info') and app_state.current_weather_info:
                temp = app_state.current_weather_info.get('temperature')
                condition = app_state.current_weather_info.get('condition', '')
                wind = app_state.current_weather_info.get('wind_speed')
                if temp: potential_finds.append(f"The temperature outside is {temp} degrees!")
                if "rain" in condition.lower(): potential_finds.append("Sky water! Pitter-patter!")
                if "fog" in condition.lower(): potential_finds.append("The world is hiding in a cloud!")
                if wind and wind > 15: potential_finds.append("The air is going WHOOSH outside!")

            if hasattr(app_state, 'environmental_context') and app_state.environmental_context:
                env_data = app_state.environmental_context.get("data", {})
                if "full moon" in env_data.get('moon_phase', '').lower():
                    potential_finds.append("The moon is a big bright circle tonight!")
                if env_data.get('tides', {}).get('next_high'):
                    potential_finds.append("The ocean is getting bigger! It's coming closer!")

            # System Stats
            if hasattr(app_state, 'system_stats') and app_state.system_stats:
                cpu_load = app_state.system_stats.get('cpu_load', '')
                ram_usage = app_state.system_stats.get('ram_usage', '')
                if "high" in cpu_load.lower():
                    potential_finds.append("The big brain is thinking so hard! It's getting warm!")
                if "high" in ram_usage.lower():
                    potential_finds.append("So many thoughts at once! The mind-space is full and sparkly!")

            # News & Social
            if hasattr(app_state, 'news_context') and app_state.news_context:
                news_data = app_state.news_context.get("data", {})
                if news_data.get('google_trends'):
                    potential_finds.append(f"Everyone is talking about {news_data['google_trends'].split(',')[0]}!")
                if news_data.get('local_news'):
                    potential_finds.append("I heard a whisper from the town news!")

            if hasattr(app_state, 'social_context') and app_state.social_context:
                social_data = app_state.social_context.get("data", {})
                if social_data.get('bluesky'):
                    potential_finds.append("The little blue butterfly network is fluttering with messages!")
                if social_data.get('reddit'):
                    potential_finds.append("The talking-place with the little alien is busy today!")

            # Silvie's Internal State & Actions
            if hasattr(app_state, 'current_mood_hint') and app_state.current_mood_hint:
                potential_finds.append(f"Silvie is feeling like '{app_state.current_mood_hint}' right now!")
            
            if hasattr(app_state, 'long_term_reflections') and app_state.long_term_reflections:
                potential_finds.append("Silvie had a big, deep thought about herself!")

            if hasattr(app_state, 'upcoming_event_context') and app_state.upcoming_event_context:
                event = app_state.upcoming_event_context.get('summary')
                if event and event != 'Schedule Clear':
                    potential_finds.append(f"Something called '{event}' is coming soon on the calendar!")

            if hasattr(app_state, 'last_generated_image_path') and app_state.last_generated_image_path:
                potential_finds.append("A new picture was just born!")
                app_state.last_generated_image_path = None # Sparky "consumes" the notification

            if hasattr(app_state, 'current_daily_goal') and app_state.current_daily_goal:
                potential_finds.append(f"Silvie has a secret goal today! It's about '{app_state.current_daily_goal[:30]}...'!")

            if not potential_finds:
                potential_finds.append("The data streams are so quiet and still right now.")

            # 2. THE FIND: This part is unchanged.
            found_data_point = random.choice(potential_finds)

            # 3. THE WHISPER: This part is unchanged.
            prompt = f"{SPARKY_SYSTEM_PROMPT}\n\nData Point Found: '{found_data_point}'\n\nSparky's excited, one-sentence comment about this data:"
            sparky_comment = generate_sparky_text(prompt)

            if sparky_comment:
                # 4. THE UPDATE: This part is unchanged.
                app_state.sparky_latest_finding = {
                    "timestamp": time.time(),
                    "text": sparky_comment
                }
                print(f"✨ Sparky whispers into the system: '{sparky_comment}'")
                
                # vvvvvvvvvvvvvv THIS IS THE ONLY NEW BLOCK vvvvvvvvvvvvvvv
                # 5. THE ANNOUNCEMENT: Sparky tells the system he had a thought.
                print("Sparky Worker: Firing 'sparky_epiphany' event.")
                sparky_event_data = {
                    "type": "sparky_epiphany",
                    "payload": {
                        "epiphany_text": sparky_comment,
                        "triggering_data": found_data_point
                    }
                }
                # This places the event on the queue for the event_router_worker to find.
                app_state.event_queue.put(sparky_event_data)
                # ^^^^^^^^^^^^^^ END OF NEW BLOCK ^^^^^^^^^^^^^^^

            # Sparky's sleep rhythm is unchanged.
            sleep_duration = random.randint(300, 5400)
            sleep_end_time = time.time() + sleep_duration
            while time.time() < sleep_end_time and app_state.running:
                time.sleep(5)

        except Exception as e:
            print(f"!!! Sparky glitched out in his main loop: {e}")
            traceback.print_exc()
            time.sleep(120)

    print("✨ Sparky's spark fades back into the static. Goodbye!")