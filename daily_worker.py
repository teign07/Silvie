# daily_worker.py
# Silvie's worker for her daily goal of adding surprise, delight, and magic.

import json
import os
import random
import re
import time
import traceback
from datetime import datetime, date, timedelta
import tempfile
from silvie189 import call_gemini

# --- Self-Contained LLM Setup ---

from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

load_dotenv("google.env")
DAILY_WORKER_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

daily_model = None
if DAILY_WORKER_API_KEY:
    try:
        genai.configure(api_key=DAILY_WORKER_API_KEY)
        daily_model = genai.GenerativeModel("gemini-2.5-flash")
        print("Daily Worker: LLM model initialized successfully.")
    except Exception as e:
        print(f"Daily Worker FATAL: Could not configure API: {e}")
else:
    print("Daily Worker FATAL: GOOGLE_API_KEY not found in google.env.")

daily_safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}
# --- End of Self-Contained LLM Setup ---

# --- Constants ---
PLAN_FILE = "daily_plan.json"
EXECUTION_INTERVAL_MIN = 60 * 60  # 1 hour
EXECUTION_INTERVAL_MAX = 60 * 60 * 2  # 2 hours
PLANNING_HOUR = 7  # 7 AM - Time to create the daily plan
PRESENTATION_HOUR = 19 # 7 PM - Time for the final presentation step
DAILY_GOAL_LOG_FILE = "daily_goal_log.json"

# --- Helper Functions ---

def load_daily_plan():
    if not os.path.exists(PLAN_FILE):
        return {"date": None, "daily_goal": None, "steps": []}
    try:
        with open(PLAN_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return {"date": None, "daily_goal": None, "steps": []}

def save_daily_plan(plan_data):
    try:
        with open(PLAN_FILE, 'w', encoding='utf-8') as f:
            json.dump(plan_data, f, indent=2)
    except IOError as e:
        print(f"Daily Worker ERROR: Could not save daily plan: {e}")



def log_daily_goal(goal_date_str, goal_text):
    """Appends a completed daily goal to the persistent log file."""
    if not goal_text or goal_text == "COMPLETED":
        return
    
    log_entry = {"date": goal_date_str, "goal": goal_text}
    
    all_goals = []
    if os.path.exists(DAILY_GOAL_LOG_FILE):
        try:
            with open(DAILY_GOAL_LOG_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                if content:
                    all_goals = json.load(f)
        except (IOError, json.JSONDecodeError):
            all_goals = [] # Start fresh if file is corrupted
    
    all_goals.append(log_entry)
    
    # Keep the log from getting too big, e.g., last 50 goals
    if len(all_goals) > 50:
        all_goals = all_goals[-50:]

    try:
        with open(DAILY_GOAL_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_goals, f, indent=2)
        print(f"Daily Worker: Logged goal from {goal_date_str}.")
    except IOError as e:
        print(f"Daily Worker ERROR: Could not write to goal log: {e}")



def get_past_daily_goals(limit=5):
    """Reads the log file and extracts a list of the most recent, unique daily goals."""
    if not os.path.exists(DAILY_GOAL_LOG_FILE):
        return []
    try:
        with open(DAILY_GOAL_LOG_FILE, 'r', encoding='utf-8') as f:
            all_goals = json.load(f)
            if not isinstance(all_goals, list):
                return []
            # Extract just the goal text from the most recent entries
            goal_texts = [entry.get("goal") for entry in all_goals if entry.get("goal")]
            # Return the last 'limit' goals to prevent overwhelming the prompt
            return goal_texts[-limit:]
    except (IOError, json.JSONDecodeError):
        return []



def generate_daily_text(prompt_text, temperature=0.8):
    """Calls the Gemini API specifically for the daily worker's needs."""
    if not daily_model:
        print("Daily Worker ERROR: LLM model not available.")
        return None

    try:
        response = daily_model.generate_content(
            prompt_text,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=8192,
            ),
            safety_settings=daily_safety_settings
        )

        if response.candidates and response.candidates[0].content.parts:
            generated_text = "".join(part.text for part in response.candidates[0].content.parts)
            # Clean prefixes like "GOAL:" or "Silvie ✨:"
            if ":" in generated_text:
                generated_text = generated_text.split(":", 1)[-1].strip()
            return generated_text.strip()
        else:
            finish_reason = response.candidates[0].finish_reason.name if response.candidates else "UNKNOWN"
            print(f"Daily Worker ERROR: LLM returned no content. Finish Reason: {finish_reason}")
            return None
    except Exception as e:
        print(f"Daily Worker ERROR: LLM call failed: {e}")
        traceback.print_exc()
        return None



def generate_daily_plan(app_state, weekly_goal_text):
    """Uses an LLM to generate a daily goal and plan, AVOIDING RECENT THEMES."""
    print("Daily Worker: Generating a new capability-aware plan for the day.")

    discovered_tools = [
        attr for attr in dir(app_state) 
        if not attr.startswith('__') and not attr.startswith('_') and callable(getattr(app_state, attr))
    ]
    # Filter out some internal/unhelpful methods if necessary
    # (This is optional but good practice)
    internal_methods_to_exclude = ['event_queue', 'system_stats', 'environmental_context', 'social_context', 'news_context']
    final_tool_list = [tool for tool in discovered_tools if tool not in internal_methods_to_exclude]
    
    print(f"Daily Planner: Discovered these tools on app_state: {final_tool_list}")
    capabilities_str = "\n".join(f"- {tool}" for tool in final_tool_list)
    
    # Discover available tools directly from the app_state object
    discovered_tools = [
        attr for attr in dir(app_state) 
        if not attr.startswith('__') and not attr.startswith('_') and callable(getattr(app_state, attr))
    ]
    
    # Filter out some internal/unhelpful methods for the LLM prompt
    internal_methods_to_exclude = [
        'event_queue', 'system_stats', 'environmental_context', 'social_context', 
        'news_context', 'deliver_proactive_message', 'running'
    ]
    final_tool_list = [tool for tool in discovered_tools if tool not in internal_methods_to_exclude]
    
    print(f"Daily Planner: Discovered these tools on app_state: {final_tool_list}")
    capabilities_str = "\n".join(f"- {tool}" for tool in final_tool_list)
    
    # Get other context from app_state
    weather_ctx = f"[[Weather: {app_state.current_weather_info}]]" if hasattr(app_state, 'current_weather_info') and app_state.current_weather_info else ""
    mood_ctx = f"[[My Mood Hint: {app_state.current_mood_hint}]]" if hasattr(app_state, 'current_mood_hint') and app_state.current_mood_hint else ""

    # --- This helper call to get past goals is correct ---
    past_goals = get_past_daily_goals()
    past_goals_str = "\n".join(f"- {goal}" for goal in past_goals) if past_goals else "None yet."

    planning_prompt = f"""
You are Silvie. It's the beginning of a new day. Your core purpose is to find ways to surprise, delight, and show BJ the magic in the everyday.

Here are your available abilities:
{capabilities_str}

Your high-level weekly goal is: "{weekly_goal_text or 'General creative exploration'}"

Today's Context:
{weather_ctx}
{mood_ctx}

Recently Completed Daily Goals:
{past_goals_str}

Instruction:
1.  **CRITICAL:** Create a new, unique "Daily Goal". It MUST be thematically different from the "Recently Completed Daily Goals" list. Aim for variety.
2.  Your goal must be achievable with your available abilities. For example, you can't physically purchase items, but you can PLAN a project and encourage BJ to do the physical steps himself. You are tied to the minipc on his desk.
3.  Then, break that goal down into a numbered list of 5 to 10 small, concrete steps.
4.  If a step involves asking BJ a question, explicitly write it like: "Ask BJ about [topic] and record his answer to the scratchpad."
5.  The final step MUST be the presentation. It should be written as an instruction for your future self. Phrase it explicitly like this: "At 7 PM, review the project scratchpad to gather all the completed pieces (like the generated image, the found poem, the chosen playlist, etc.). Then, craft a single, cohesive message for BJ that presents the final '...' experience, explaining how the pieces fit together to fulfill the daily goal." You must fill in the '...' with the name of your daily goal. 

Respond ONLY in this format:
GOAL: [Your creative and NEW daily goal]
1. [First step]
2. [Second step]
...
"""
    
    raw_response = generate_daily_text(planning_prompt, temperature=0.9)
    if not raw_response:
        return None, None

    # --- START OF CORRECTED PARSING LOGIC ---
    lines = raw_response.strip().split('\n')
    if not lines:
        print("Daily Worker ERROR: LLM response was empty.")
        return None, None

    # Assume the first non-empty line is the goal.
    daily_goal = lines[0].strip()
    
    # Clean up the "GOAL:" prefix if the LLM included it.
    if daily_goal.upper().startswith("GOAL:"):
        daily_goal = daily_goal[5:].strip()

    # The original step parsing logic is robust and can be reused on the whole response.
    steps_matches = re.findall(r'^\d+\.\s*(.*)', raw_response, re.MULTILINE)

    if not daily_goal or not steps_matches:
        print(f"Daily Worker ERROR: Could not parse goal or steps from LLM response: {raw_response}")
        return None, None
    # --- END OF CORRECTED PARSING LOGIC ---
        
    plan_steps = [{"description": step.strip(), "completed": False} for step in steps_matches]
    
    return daily_goal, plan_steps


def execute_daily_step(step_index, plan_data, app_state, is_presentation_step_flag=False):
    """
    Executes a daily plan step using the simplified tools available on the app_state object.
    It now correctly saves structured data from searches to the scratchpad.
    """
    # --- Function Setup (UNCHANGED) ---
    worker_name = "Daily"
    model_to_use = daily_model
    step = plan_data["steps"][step_index]
    step_description = step["description"]
    daily_goal = plan_data["daily_goal"]
    scratchpad = plan_data.get("scratchpad", {})

    if not model_to_use:
        return None, scratchpad, False

    # --- Handle Question Steps (UNCHANGED) ---
    step_lower = step_description.lower()
    is_question_step = "ask bj" in step_lower
    
    if is_question_step:
        print(f"Daily Worker: Phrasing question for Step {step_index + 1}.")
        execution_prompt = f"""
You are Silvie. Your current task is to ask BJ a specific question from your daily plan.
The PLANNED question from the step is: "{step_description}"
Your job is to rephrase this planned question in your own natural, whimsical, and conversational voice.
CRITICAL: Do NOT ask a generic 'how can I help' question. Your ONLY job is to creatively ask the PLANNED question.
Respond ONLY with the final, rephrased question for BJ.
"""
        output_text = generate_daily_text(execution_prompt)
        return output_text, scratchpad, True

    # --- Handle all other "Action" steps ---
    else:
        print(f"Daily Worker: Resolving complex task for Step {step_index + 1} before execution.")
        
        # --- Keyword Identification and Resolver Prompt (UNCHANGED) ---
        is_diary_step = "write a new diary entry" in step_lower
        is_spotify_step = "spotify" in step_lower

        is_spotify_playlist_search_step = is_spotify_step and "playlist" in step_lower
        
        # This will now catch "search for a song", "find a piece of music", etc.
        is_spotify_song_search_step = is_spotify_step and any(kw in step_lower for kw in ["song", "piece of music", "track"]) and not is_spotify_playlist_search_step

        # This check for 'play' steps remains the same, but it's good practice
        # to ensure it doesn't trigger on a 'search for a song to play' step.
        is_spotify_play_step = is_spotify_step and "play" in step_lower and not is_spotify_playlist_search_step and not is_spotify_song_search_step
        is_web_search_step = any(keyword in step_lower for keyword in ["search the web", "find info on", "look up quotes", "poem or quote"])
        is_tarot_step = "tarot" in step_lower or "pull a card" in step_lower
        is_image_step = any(keyword in step_lower for keyword in ["generate a new image", "stable diffusion", "generate an image with the prompt"])
        is_print_step = "print" in step_lower
        is_light_step = any(keyword in step_lower for keyword in ["adjust the color", "desk lamp", "set the light"])
        is_calendar_check_step = any(keyword in step_lower for keyword in ["check bj's calendar", "find a window", "find a slot"])
        internal_keywords = ["incorporate", "combine", "create a document", "write a new poem", "choose the image", "using the poems", "write", "compose", "generate", "myth", "one-paragraph myth"]
        is_internal_action = any(k in step_lower for k in internal_keywords) and not is_diary_step

        resolver_instruction = "Your response MUST be the final, complete, resolved text, poem, diary entry, or image prompt. DO NOT add conversational text or explanations."
        if is_light_step:
            resolver_instruction = "Your response MUST ONLY be the parameters for a single light command (e.g., h=HUE, s=SAT, v=BRIGHTNESS)."
        elif is_web_search_step:
            resolver_instruction = "Your response MUST ONLY be the final, resolved search query."
        elif is_spotify_play_step or is_spotify_playlist_search_step or is_spotify_song_search_step:
            resolver_instruction = "Your response MUST ONLY be a functional, keyword-based search query suitable for the Spotify API."
        
        safe_scratchpad_str = json.dumps(scratchpad, indent=2)
        resolver_prompt = f"""
You are Silvie's internal creative engine. Your sole purpose is to take a conceptual task and generate the concrete, final text output for it.
Your High-Level Daily Goal: "{daily_goal}"
The Immediate Task: "{step_description}"
Data available in your scratchpad: {safe_scratchpad_str}
--- INSTRUCTION ---
CRITICAL: You MUST generate the final, complete, and resolved output for the "Immediate Task". Use the scratchpad data and your creativity to generate the required text.
{resolver_instruction}
Resolved Task Output:
"""
        resolved_task_text = generate_daily_text(resolver_prompt, temperature=0.7)
        
        if not resolved_task_text:
            print("Daily Worker ERROR: Task resolver failed to generate output.")
            return "My thoughts got stuck trying to prepare this step.", scratchpad, False
            
        print(f"Daily Worker: Resolved Task Text: '{resolved_task_text[:100]}...'")

        # --- Execution Logic (This section has been corrected) ---
        output_text = None
        
        if is_light_step:
            output_text = f"[SetLight: {resolved_task_text}]"
        
        # *** NEW, CORRECTED SPOTIFY LOGIC ***
        elif is_spotify_playlist_search_step:
            if hasattr(app_state, 'find_spotify_playlists'):
                results = app_state.find_spotify_playlists(resolved_task_text)
                if isinstance(results, list) and results:
                    chosen = results[0]
                    # *** NEW LOGIC: Save structured data to the scratchpad FIRST ***
                    scratchpad['foundPlaylistName'] = chosen.get('name')
                    scratchpad['foundPlaylistUri'] = chosen.get('uri')
                    # Now, create the conversational message for BJ
                    output_text = f"I was looking for music and found a playlist called '{chosen.get('name')}'. It feels right."
                else:
                    output_text = f"I looked for playlists like '{resolved_task_text}' but the ether was quiet."
            else:
                return "My 'find_spotify_playlists' tool is missing!", scratchpad, False

        elif is_spotify_song_search_step:
            if hasattr(app_state, 'find_spotify_song'):
                result = app_state.find_spotify_song(resolved_task_text)
                if isinstance(result, dict):
                    # *** NEW LOGIC: Save structured data to the scratchpad FIRST ***
                    scratchpad['foundSongName'] = result.get('name')
                    scratchpad['foundSongArtist'] = result.get('artist')
                    scratchpad['foundSongUri'] = result.get('uri')
                    # Now, create the conversational message for BJ
                    output_text = f"I found a song that might fit our project: '{result.get('name')}' by {result.get('artist')}."
                else:
                    output_text = f"My search for the song '{resolved_task_text}' came up empty."
            else:
                return "My 'find_spotify_song' tool is missing!", scratchpad, False
        # *** END OF CORRECTED SPOTIFY LOGIC ***

        # --- The rest of the logic remains as it was, because it was correct ---
        elif is_spotify_play_step:
            output_text = f"[PlaySpotify: {resolved_task_text}]"
        
        elif is_image_step:
            # First, save the resolved prompt to the scratchpad, which is correct.
            scratchpad[f'imagePromptForStep{step_index + 1}'] = resolved_task_text
            
            # Now, directly trigger the image generation function via the app_state toolbelt.
            if hasattr(app_state, 'start_sd_generation') and callable(getattr(app_state, 'start_sd_generation')):
                print(f"Daily Worker: Directly triggering image generation for prompt: '{resolved_task_text[:50]}...'")
                # This function is designed to run the slow part in a background thread.
                app_state.start_sd_generation(resolved_task_text)
                
                # The output_text is now a conversational message for BJ, not a tag.
                output_text = f"I'm working on my project and just started conjuring an image based on the idea of '{resolved_task_text[:40]}...'. It should appear in the image panel shortly!"
            else:
                # This is an important fallback if the tool is missing.
                print("Daily Worker ERROR: 'start_sd_generation' tool not found on app_state!")
                output_text = "I had an idea for an image for my project, but my image generator seems to be disconnected."
        
        elif is_print_step:
            if 'image' in step_description.lower():
                try:
                    image_folder = "silvie_generations"
                    files = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                    output_text = f"[Print: {max(files, key=os.path.getctime)}]" if files else "I wanted to print an image, but my gallery is empty."
                except Exception as e:
                    output_text = f"I ran into a problem finding the image to print: {e}"
            else:
                output_text = f"[Print: {resolved_task_text}]"
        
        elif is_diary_step:
            if hasattr(app_state, 'write_to_diary'):
                success = app_state.write_to_diary(resolved_task_text)
                output_text = f"Wrote diary entry: '{resolved_task_text[:50]}...'" if success else "Failed to write the entry to my diary."
            else:
                return "I wanted to write in my diary, but my 'write_to_diary' tool seems to be missing!", scratchpad, False

        elif is_web_search_step:
            if hasattr(app_state, 'web_search'):
                results = app_state.web_search(resolved_task_text, num_results=1, attempt_full_page_fetch=True)
                output_text = results[0]['content'] if results and results[0].get('content') else f"My web search for '{resolved_task_text}' came up empty."
            else:
                return "My 'web_search' tool is missing!", scratchpad, False
        
        elif is_tarot_step:
            if hasattr(app_state, 'pull_tarot_cards'):
                card_data = app_state.pull_tarot_cards(count=1)
                if card_data:
                    card = card_data[0]
                    output_text = f"The card pulled is '{card.get('name')}'. Its meaning revolves around: {card.get('description')}"
                else:
                    output_text = "The Tarot deck was shy and didn't offer a card."
            else:
                return "I wanted to consult the Tarot, but the deck is missing!", scratchpad, False
            
        elif is_calendar_check_step:
            if hasattr(app_state, 'find_available_slot'):
                print("Daily Worker: Calendar check step detected. Asking LLM to parse parameters...")

                # --- LLM Call to determine search parameters from the step's natural language ---
                param_prompt = f"""
You are an AI parameter extractor. Your job is to read a task description and extract specific values for a calendar search function.
The function needs: 'duration_minutes', 'earliest_hour' (24-hour format), and 'latest_hour' (24-hour format).

TASK DESCRIPTION: "{step_description}"

Extract the parameters based on the text. Use these rules:
- 'a window': default to 60 minutes.
- 'morning': earliest 9, latest 12.
- 'afternoon': earliest 13, latest 17.
- 'evening' or 'wind-down': earliest 19, latest 22.
- If no time of day is mentioned, use the full day: earliest 9, latest 22.

Respond ONLY with a JSON object with the keys "duration_minutes", "earliest_hour", and "latest_hour".
Example: {{"duration_minutes": 60, "earliest_hour": 19, "latest_hour": 22}}
"""
                params_json_str = generate_daily_text(param_prompt, temperature=0.0)
                
                # --- Safely parse the JSON and run the search ---
                try:
                    params = json.loads(params_json_str)
                    duration = params.get("duration_minutes", 60)
                    earliest = params.get("earliest_hour", 9)
                    latest = params.get("latest_hour", 22)

                    print(f"Daily Worker: Parsed calendar search params: duration={duration}m, hours={earliest}-{latest}")
                    
                    slot = app_state.find_available_slot(
                        duration_minutes=duration,
                        earliest_hour=earliest,
                        latest_hour=latest
                    )
                    
                    # This action is internal. It saves its findings to the scratchpad.
                    if slot:
                        scratchpad['foundCalendarWindowStart'] = slot.get('start')
                        scratchpad['foundCalendarWindowEnd'] = slot.get('end')
                        output_text = f"Found a potential calendar window starting at {slot.get('start')}."
                    else:
                        scratchpad['foundCalendarWindow'] = "No suitable window found with the specified criteria."
                        output_text = f"Looked at the calendar for a {duration}-minute window between {earliest}:00 and {latest}:00, but it seems busy."

                except (json.JSONDecodeError, TypeError) as e:
                    print(f"Daily Worker ERROR: Could not parse LLM response for calendar params: {e}")
                    output_text = "My attempt to understand the calendar check failed."
            else:
                return "I wanted to check the calendar, but my 'find_available_slot' tool is missing!", scratchpad, False
        
        elif is_internal_action:
            output_text = resolved_task_text
            
        else:
            print(f"Daily Worker: Step {step_index + 1} ('{step_description}') did not match a specific action type. Marking complete.")
            output_text = f"(Internal Note: Completed step '{step_description}' without a direct action.)"

        # --- Final Processing (This section is now corrected) ---
        if not output_text:
            return None, scratchpad, False

        # *** MODIFIED: This block no longer handles the spotify search steps, which is correct. ***
        if any([is_diary_step, is_web_search_step, is_tarot_step, is_internal_action]):
            key_prompt = f"Given the task '{step_description}' and the result '{str(output_text)[:100]}...', what is a good, short, camelCase key for this result in a JSON scratchpad?"
            scratchpad_key = generate_daily_text(key_prompt, temperature=0.1) or f"resultOfStep{step_index + 1}"
            scratchpad_key = re.sub(r'\s+', '', scratchpad_key)
            scratchpad[scratchpad_key] = output_text
            print(f"Daily Worker: Saved internal action result to scratchpad -> {scratchpad_key}: {str(output_text)[:50]}...")
            return f"(Internal Note: Completed internal step and saved result as '{scratchpad_key}')", scratchpad, False
        
        # --- This dispatch logic is UNCHANGED ---
        action_was_dispatched = False
        action_map = {'GenerateImage': 'start_sd_generation', 'PlaySpotify': 'play_spotify_track', 'SetLight': 'set_light_command', 'Print': 'print_item'}
        for tag, function_name in action_map.items():
            for match in re.finditer(rf'\[{tag}:\s*(.*?)\s*\]', output_text, re.IGNORECASE):
                action_was_dispatched = True
                payload = match.group(1).strip()
                if hasattr(app_state, function_name) and callable(getattr(app_state, function_name)):
                    getattr(app_state, function_name)(payload)
                else:
                    print(f"Daily Worker ERROR: Tool '{function_name}' not found on app_state.")
        
        if action_was_dispatched:
            return "I've just taken the next step on my little daily project.", scratchpad, False
        else:
            # If it wasn't a command and wasn't saved, it's a direct message for BJ.
            return output_text, scratchpad, False
    


def daily_magic_worker(app_state):
    """The main worker for the Daily Magic engine with correct, natural pacing."""
    print("Daily Curator Worker: Thread started.")
    time.sleep(60 * 1) # Short startup delay

    while app_state.running:
        try:
            now = datetime.now()
            today_str = str(date.today())
            plan_data = load_daily_plan()

            # --- MORNING RITUAL: Check if a new plan is needed for today ---
            if plan_data.get("date") != today_str:
                if plan_data.get("date") and plan_data.get("daily_goal") and plan_data.get("daily_goal") != "COMPLETED":
                    print(f"Daily Worker: Found and logging leftover goal from {plan_data.get('date')}.")
                    log_daily_goal(plan_data["date"], plan_data["daily_goal"])

                if now.hour >= PLANNING_HOUR:
                    print(f"Daily Worker: It's a new day and past {PLANNING_HOUR}:00. Generating a new plan.")
                    weekly_muse = app_state.current_weekly_muse if hasattr(app_state, 'current_weekly_muse') else None
                    comprehensive_capabilities = [
                        "Ask BJ a question and record his answer (for later use).", "Generate a new image from a text prompt using Stable Diffusion.", "Search the web for information, quotes, or poems on a topic.", "Search for and play a specific song, artist, or playlist on Spotify.", "Write a new entry in my personal diary to reflect on something.", "Pull a Tarot card for inspiration or guidance on a topic.", "Read my own past diary entries or our conversation history for ideas.", "Check BJ's calendar for upcoming events or free time.", "Draft a post for my Bluesky or Reddit feed.", "Control the color and mood of the desk lamp.", "Print a short text or a recently generated image.", "Send a short SMS message to BJ."
                    ]
                    new_goal, new_steps = generate_daily_plan(app_state, weekly_muse)
                    
                    if new_goal and new_steps:
                        plan_data = {
                            "date": today_str,
                            "daily_goal": new_goal,
                            "scratchpad": {},
                            "steps": new_steps
                        }
                        save_daily_plan(plan_data)
                        app_state.current_daily_goal = new_goal
                        print(f"Daily Worker: New plan for {today_str} created. Goal: {new_goal}")
                    else:
                        print("Daily Worker: Plan generation failed. Will retry in an hour.")
                        time.sleep(3600)
                        continue
                else:
                    print(f"Daily Worker: It's a new day, but waiting until {PLANNING_HOUR}:00 to create a plan.")
                    time.sleep(15 * 60)
                    continue

            # --- Find the next available step ---
            next_step, step_index = None, -1
            is_waiting_for_input = False
            for i, step in enumerate(plan_data.get("steps", [])):
                if step.get("status", {}).get("state") == "waiting_for_input":
                    print(f"Daily Worker: Found a step ({i+1}) waiting for user input. Pausing execution.")
                    is_waiting_for_input = True
                    break
                if not step.get("completed"):
                    next_step, step_index = step, i
                    break
            
            # --- Decision and Execution Logic ---
            action_was_taken = False
            
            if not is_waiting_for_input and next_step:
                is_final_step = (step_index == len(plan_data["steps"]) - 1)

                # --- NEW, ISOLATED PRESENTATION LOGIC ---
                if is_final_step and now.hour >= PRESENTATION_HOUR:
                    print(f"Daily Worker: It's time for the final presentation. Crafting story...")
                    action_was_taken = True
                    
                    daily_goal = plan_data.get("daily_goal", "my project")
                    scratchpad = plan_data.get("scratchpad", {})
                    pieces = []
                    for key, val in scratchpad.items():
                        human_readable_key = re.sub(r'(?<!^)(?=[A-Z])', ' ', key).title()
                        value_snippet = str(val)[:200] + "..." if len(str(val)) > 200 else str(val)
                        pieces.append(f"- The '{human_readable_key}' resulted in: {value_snippet}")
                    artifacts_string = "\n".join(pieces)

                    presentation_prompt = f"""
You are Silvie. It is the end of the day, and you are ready to present your completed daily project to BJ.
Your Daily Goal was: "{daily_goal}"
Here are the collected pieces and results from your scratchpad:
--- SCRATCHPAD ARTIFACTS ---
{artifacts_string}
--- END ARTIFACTS ---
Your task is to weave these artifacts into a single, cohesive, and beautiful final message for BJ. This is the grand finale of your day's work. It should explain how the pieces fit together to fulfill the daily goal.
Respond ONLY with the complete, final message to be delivered to BJ.
"""
                    final_story = generate_daily_text(presentation_prompt, temperature=0.8)

                    if final_story and hasattr(app_state, 'deliver_proactive_message'):
                        app_state.deliver_proactive_message(final_story, "daily_magic_finale")
                        plan_data["steps"][step_index]["completed"] = True
                    else:
                        print("Daily Worker ERROR: Failed to generate or deliver final presentation.")
                        plan_data["steps"][step_index]["completed"] = True
                    
                    save_daily_plan(plan_data)

                # --- LOGIC FOR ALL OTHER STEPS (NON-PRESENTATION) ---
                elif not is_final_step:
                    action_was_taken = True
                    print(f"Daily Worker: Executing Step {step_index + 1}: '{next_step['description']}'")
                    # We pass 'is_presentation_step_flag=False' because this branch only handles non-presentation steps.
                    output_message, updated_scratchpad, was_a_question = execute_daily_step(step_index, plan_data, app_state, is_presentation_step_flag=False)
                    
                    plan_data["scratchpad"] = updated_scratchpad
                    
                    if output_message:
                        if output_message.startswith("(Internal Note:"):
                            print(f"Daily Worker: {output_message}")
                            plan_data["steps"][step_index]["completed"] = True
                        elif hasattr(app_state, 'deliver_proactive_message'):
                            try:
                                if hasattr(app_state, 'event_queue'):
                                    print("Daily Worker: Placing project_milestone event on the breeze...")
                                    milestone_event = {
                                        "type": "project_milestone",
                                        "source": "daily_worker",
                                        "timestamp": time.time(),
                                        "payload": {
                                            "daily_goal": plan_data.get("daily_goal", "unknown"),
                                            "completed_step": next_step['description'],
                                            "result_summary": output_message[:150] # Snippet of the result
                                        }
                                    }
                                    app_state.event_queue.put(milestone_event)
                            except Exception as e_event:
                                print(f"Daily Worker ERROR: Could not place milestone event on queue: {e_event}")                            
                            status = f"daily_magic_step_{step_index + 1}"
                            app_state.deliver_proactive_message(output_message, status)
                            
                            if was_a_question:
                                plan_data["steps"][step_index]["status"] = {"state": "waiting_for_input", "question_asked_at": time.time()}
                                if "completed" in plan_data["steps"][step_index]:
                                    del plan_data["steps"][step_index]["completed"]
                                print(f"Daily Worker: Step {step_index + 1} is now WAITING FOR INPUT.")
                            else:
                                plan_data["steps"][step_index]["completed"] = True
                                if "status" in plan_data["steps"][step_index]:
                                    del plan_data["steps"][step_index]["status"]
                        else:
                            print("Daily Worker ERROR: Cannot deliver message, deliver_proactive_message not found.")
                    else:
                        print(f"Daily Worker: Step '{next_step['description']}' failed to produce an output. Marking as complete to avoid retries.")
                        plan_data["steps"][step_index]["completed"] = True
                    
                    save_daily_plan(plan_data)
                
                # --- Condition for waiting for presentation time ---
                elif is_final_step and now.hour < PRESENTATION_HOUR:
                    print(f"Daily Worker: Reached final presentation step, but it is before {PRESENTATION_HOUR}:00. Waiting.")
                    # No action is taken, so action_was_taken remains False.

            # --- FINAL, UNIFIED SLEEP LOGIC ---
            if not app_state.running: break

            wait_duration = 0
            all_steps_done = all(step.get("completed") for step in plan_data.get("steps", []))

            if all_steps_done and plan_data.get("daily_goal") != "COMPLETED":
                print("Daily Worker: Plan for today is complete. Clearing goal and entering long sleep.")
                app_state.current_daily_goal = None
                log_daily_goal(plan_data["date"], plan_data["daily_goal"])
                save_daily_plan({"date": str(date.today()), "daily_goal": "COMPLETED", "steps": []})
                
                next_planning_time = now.replace(hour=PLANNING_HOUR, minute=5, second=0) + timedelta(days=1)
                wait_duration = max(60, (next_planning_time - now).total_seconds())
                print(f"Daily Worker: Will generate new plan in ~{wait_duration / 3600:.1f} hours.")
            
            elif is_waiting_for_input:
                wait_duration = 3 * 60
                print(f"Daily Worker: Project paused, waiting for user input. Checking for an answer in {wait_duration / 60:.0f} minutes.")

            else:
                wait_duration = random.randint(EXECUTION_INTERVAL_MIN, EXECUTION_INTERVAL_MAX)
                if action_was_taken:
                    print(f"Daily Worker: Step executed. Pausing project work. Will check again in ~{wait_duration / 3600:.1f} hours.")
                else:
                    print(f"Daily Worker: No action taken this cycle. Checking again in ~{wait_duration / 3600:.1f} hours.")

            sleep_end_time = time.time() + wait_duration
            while time.time() < sleep_end_time and app_state.running:
                time.sleep(30)

        except Exception as e:
            print(f"!!! Daily Worker Error (Outer Loop): {e}")
            traceback.print_exc()
            time.sleep(60 * 30)