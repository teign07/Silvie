# event_router_worker.py (v13.2 - Corrected Event Handling)
# Silvie's central nervous system. Listens for events on the "breeze"
# and dynamically chooses from currently available tools on the app_state toolbelt.

import json
import os
import random
import re
import time
import traceback
import queue
import threading

# --- Self-Contained LLM Setup ---
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

load_dotenv("google.env")
ROUTER_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

router_model = None
if ROUTER_API_KEY:
    try:
        genai.configure(api_key=ROUTER_API_KEY)
        # Note: Using a standard, reliable model for the router.
        router_model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")
        print("Event Router (Corrected): LLM model initialized successfully.")
    except Exception as e:
        print(f"Event Router (Corrected) FATAL: Could not configure API: {e}")
# --- End LLM Setup ---

# --- Global Cooldowns & Limits ---
last_bluesky_post_time_from_event_router = 0.0
BLUESKY_EVENT_POST_COOLDOWN = 4 * 3600 # 4 hours
MAX_ACTIONS_PER_EVENT = 3
# --- End Cooldowns & Limits ---

# ==============================================================================
# --- THE DYNAMIC ACTION REGISTRY ---
# This is the single source of truth for the router's capabilities.
# It maps a user-friendly Action Name to:
#   - check: A lambda function to see if the tool is available on app_state.
#   - tool_name: The actual attribute name on the app_state object.
#   - param_prompt: An LLM prompt to generate the necessary parameter, if any.
# ==============================================================================
ACTION_TO_TOOL_MAP = {
    "SetLight": {
        "check": lambda s: hasattr(s, 'set_desk_lamp'),
        "tool_name": "set_desk_lamp",
        "param_prompt": "Generate a parameter string for a LIFX light command (e.g., h=HUE, s=SAT, v=BRIGHT). Respond ONLY with the parameter string."
    },
    "FindMusic": {
        "check": lambda s: hasattr(s, 'play_spotify_track'),
        "tool_name": "play_spotify_track",
        "param_prompt": "What is a good Spotify search query for this atmosphere? Respond ONLY with the query."
    },
    "GenerateImageIdea": {
        "check": lambda s: hasattr(s, 'start_sd_generation'),
        "tool_name": "start_sd_generation",
        "param_prompt": "Create a concise, creative Stable Diffusion prompt. Respond ONLY with the prompt text."
    },
    "DreamDesktopWallpaper": {
        "check": lambda s: hasattr(s, 'generate_and_set_wallpaper'),
        "tool_name": "generate_and_set_wallpaper",
        "param_prompt": "Create a concise, creative Stable Diffusion prompt for a new wallpaper. Respond ONLY with the prompt text."
    },
    "WriteDiaryEntry": {
        "check": lambda s: hasattr(s, 'write_to_diary'),
        "tool_name": "write_to_diary",
        "param_prompt": "Write a short, reflective diary entry about this event. Respond ONLY with the diary entry text."
    },
    "ConsultTarot": {
        "check": lambda s: hasattr(s, 'pull_tarot_cards'),
        "tool_name": "pull_tarot_cards", # Special handling case
        "param_prompt": None
    },
    "SearchOwnMemory": {
        "check": lambda s: hasattr(s, 'search_chat_history') and hasattr(s, 'search_diary_entries'),
        "tool_name": "search_chat_history", # Special handling case
        "param_prompt": None
    },
    "DraftSocialPost": {
        "check": lambda s: hasattr(s, 'post_to_bluesky'),
        "tool_name": "post_to_bluesky",
        "param_prompt": "Turn this event into a short, whimsical post for Bluesky. Respond ONLY with the post text."
    },
    "ExploreOnYouTube": {
        "check": lambda s: hasattr(s, 'search_youtube_videos'),
        "tool_name": "search_youtube_videos", # Special handling case
        "param_prompt": None
    },
    "QueueDeepResearch": {
        "check": lambda s: hasattr(s, 'start_deep_research'),
        "tool_name": "start_deep_research",
        "param_prompt": "What is a concise, specific research topic (3-7 words) inspired by this? Respond ONLY with the topic."
    },
    "TriggerPrintJob": {
        "check": lambda s: hasattr(s, 'print_item'),
        "tool_name": "print_item",
        "param_prompt": "Write a short, beautiful, poignant text worthy of being printed. Respond ONLY with the text."
    },
    "AnnounceActionToUser": {
        "check": lambda s: hasattr(s, 'deliver_proactive_message'),
        "tool_name": "deliver_proactive_message",
        "param_prompt": "Based on the event and the action you just decided to take (but don't mention the action name), write a short, natural, conversational message for BJ to let him know what you're thinking or doing. Respond ONLY with the message text."
    },
    "WebSearch": {
        "check": lambda s: hasattr(s, 'start_web_search'),
        "tool_name": "start_web_search",
        "param_prompt": "What is a concise web search query (3-7 words) for this context? Respond ONLY with the query."
    }
}

def generate_router_text(prompt_text, temperature=0.7):
    """A dedicated LLM call function for the router's decision-making."""
    if not router_model:
        print("Event Router ERROR: LLM model not available.")
        return None
    try:
        response = router_model.generate_content(
            prompt_text,
            generation_config=genai.GenerationConfig(
                temperature=temperature, max_output_tokens=8192
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        if response.candidates and response.candidates[0].content.parts:
            return "".join(part.text for part in response.candidates[0].content.parts).strip()
        else:
            print("Event Router Note: LLM response was valid but contained no text.")
            return None
    except Exception as e:
        print(f"Event Router ERROR: LLM call failed: {e}")
        traceback.print_exc()
        return None

def event_router_worker(app_state):
    """
    The main loop for the event router. It listens for events and dispatches
    actions by dynamically checking the available tools on app_state.
    """
    global last_bluesky_post_time_from_event_router
    print("Event Router (Corrected): Initializing...")
    
    # Shortened startup delay for faster testing
    initial_delay_seconds = 10 
    print(f"Event Router (Corrected): Beginning startup quiet period of {initial_delay_seconds} seconds.")
    sleep_end_time = time.time() + initial_delay_seconds
    while time.time() < sleep_end_time and app_state.running:
        time.sleep(1)

    if not app_state.running:
        print("Event Router (Corrected): Shutdown signal received during startup delay. Exiting.")
        return
    
    print("Event Router (Corrected): Startup quiet period complete. Processing event backlog...")
    
    if not hasattr(app_state, 'event_queue'):
        print("Event Router FATAL: Event queue not found on app_state. Shutting down.")
        return

    # Intelligent Backlog Clearing Logic (remains the same)
    try:
        initial_pile = []
        while not app_state.event_queue.empty():
            initial_pile.append(app_state.event_queue.get_nowait())
            app_state.event_queue.task_done()

        if initial_pile:
            print(f"Event Router: Drained an initial backlog of {len(initial_pile)} events. Filtering...")
            
            events_to_requeue = []
            
            metis_events = [event for event in initial_pile if event.get('type') == 'integration_request']
            if metis_events:
                events_to_requeue.extend(metis_events)
                print(f"  -> PRESERVED {len(metis_events)} Metis integration request(s).")

            non_metis_events = [event for event in initial_pile if event.get('type') != 'integration_request']
            if non_metis_events:
                last_non_metis_event = non_metis_events[-1]
                events_to_requeue.append(last_non_metis_event)
                print(f"  -> PRESERVED the most recent non-Metis event: '{last_non_metis_event.get('type')}'")

            if events_to_requeue:
                print(f"Event Router: Re-queuing {len(events_to_requeue)} important events.")
                for event in events_to_requeue:
                    app_state.event_queue.put(event)
    except queue.Empty:
        pass
    except Exception as e:
        print(f"Event Router ERROR during intelligent backlog clearing: {e}")
        traceback.print_exc()
    
    print("Event Router (Corrected): The 'Event Breeze' is now flowing...")

    # ==========================================================================
    # --- FIX: DEFINE A LIST OF EVENTS THAT SHOULD TRIGGER NEW ACTIONS ---
    # ==========================================================================
    # These events, even if they end in "_complete" or "_found", are triggers
    # for the router to choose a *new* action, not stop processing.
    TRIGGER_EVENTS = [
        "image_generation_complete",
        "research_complete",
        "web_search_completed",
        "resonance_insight_found",
        "important_event_started",
        "weather_shift_detected",
        # Add any other events here that should prompt a reaction from Silvie.
    ]

    while app_state.running:
        try:
            event = app_state.event_queue.get(block=True, timeout=5.0)
            event_type = event.get('type')
            event_payload = event.get('payload', {})
            print(f"Event Router: Caught an event on the breeze: {event_type}")

            # =================================================================
            # SECTION 1: Handle SPECIAL events that don't select tools
            # =================================================================
            is_result_or_governance = event_type.endswith(('_completed', '_failed', '_request', '_found', '_recalled_by_event'))

            # --- MODIFIED LOGIC: Check if it's a special event AND it's NOT a trigger event ---
            if is_result_or_governance and event_type not in TRIGGER_EVENTS:
                
                # This block now correctly handles ONLY governance requests and true "result"
                # events that require no further action from the router itself.
                
                if event_type == "integration_request":
                    print(f"Event Router: Received integration request for tool: {event_payload.get('tool_name')}")
                    
                    app_state.awaiting_human_governance_approval = True
                    
                    tool_name = event_payload.get('tool_name', 'Unnamed Tool')
                    description = event_payload.get('description', 'do something new')
                    
                    message_to_bj = (
                        f"BJ, I've been in my workshop and I believe I've forged a new tool. "
                        f"It's a '{tool_name}' that {description.lower().replace('fetches', 'can fetch')}. "
                        f"It seems stable and has passed all my internal checks. "
                        f"Shall I add it to my permanent collection of abilities? You can just say, 'Yes, add the {tool_name}'."
                    )
                    
                    if hasattr(app_state, 'deliver_proactive_message'):
                        app_state.deliver_proactive_message(message_to_bj, status_log="human_governance_request")
                    else:
                        print("Event Router: ERROR - deliver_proactive_message not found. Cannot ask for approval.")

                # You can add elifs here for specific _failed events if you want to log them differently.
                
                print(f"Event Router: Event '{event_type}' is a terminal result. No further action needed.")
                app_state.event_queue.task_done()
                continue # Skip the dynamic action selection for these events.

            # =================================================================
            # SECTION 2: Handle GENERAL and TRIGGER events by choosing a dynamic tool
            # =================================================================
            # If the code reaches here, the event is a valid trigger for a new action.
            
            distiller_prompt = f"Describe this event in one clear sentence: {json.dumps(event, indent=2)}"
            event_context_sentence = generate_router_text(distiller_prompt, temperature=0.1)
            if not event_context_sentence:
                print("Event Router Warning: Could not distill a context sentence. Skipping.")
                app_state.event_queue.task_done()
                continue
            
            print(f"Event Router: Distilled Context: '{event_context_sentence}'")

            available_actions = [name for name, details in ACTION_TO_TOOL_MAP.items() if details["check"](app_state)]

            # --- SAFEGUARD: Prevent Action Loops ---
            if event_type == "image_generation_complete":
                # If the event is an image completion, temporarily remove the ability to generate another one.
                if "GenerateImageIdea" in available_actions:
                    available_actions.remove("GenerateImageIdea")
                    print("Event Router Safeguard: Temporarily disabled 'GenerateImageIdea' to prevent a loop.")
                if "DreamDesktopWallpaper" in available_actions:
                    available_actions.remove("DreamDesktopWallpaper")
                    print("Event Router Safeguard: Temporarily disabled 'DreamDesktopWallpaper' to prevent a loop.")
            
            # You can add other safeguards here if you discover other potential loops.
            # For example:
            # if event_type == "new_research_data_ready":
            #     if "QueueDeepResearch" in available_actions:
            #         available_actions.remove("QueueDeepResearch")

            if not available_actions:
                print("Event Router: No tools available on the toolbelt to handle this event. Skipping.")
                app_state.event_queue.task_done()
                continue
            
            # Shuffle actions to prevent LLM bias
            random.shuffle(available_actions)
            action_list_for_prompt = "\n".join(f"- {name}" for name in available_actions)

            action_decision_prompt = f"""
You are Silvie's creative director. An event occurred: "{event_context_sentence}"
Based on this, what are the {MAX_ACTIONS_PER_EVENT} most fitting and creative responses?

--- AVAILABLE ACTIONS ---
{action_list_for_prompt}
- DoNothing

**Guideline:** If you choose a silent background action (like 'WriteDiaryEntry'), you should ALSO choose 'AnnounceActionToUser' so Silvie can tell BJ about what she's doing or thinking in a natural way.

CRITICAL: Respond ONLY with a JSON-formatted list of action names from the list above.
Example Response: ["WriteDiaryEntry", "AnnounceActionToUser"]
"""
            chosen_actions_json = generate_router_text(action_decision_prompt, temperature=0.5)
            
            chosen_actions_list = []
            if chosen_actions_json:
                try: 
                    # More robust JSON extraction
                    json_str_match = re.search(r'\[.*\]', chosen_actions_json, re.DOTALL)
                    if json_str_match:
                        chosen_actions_list = json.loads(json_str_match.group(0))
                    else: # Fallback for non-list response
                        chosen_actions_list = [action.strip() for action in chosen_actions_json.replace("`","").split(',') if action.strip()]

                except (json.JSONDecodeError, AttributeError): 
                    # Fallback for plain text response
                    chosen_actions_list = [line.strip('- ') for line in chosen_actions_json.split('\n') if line.strip()]

            if not chosen_actions_list or "DoNothing" in chosen_actions_list:
                print("Event Router: LLM chose no actions or 'DoNothing'.")
                app_state.event_queue.task_done()
                continue
            
            print(f"Event Router: LLM chose actions: {chosen_actions_list}")

            for action_name in chosen_actions_list[:MAX_ACTIONS_PER_EVENT]:
                action_name = action_name.strip('"\' ') # Clean up action name
                if action_name not in ACTION_TO_TOOL_MAP:
                    print(f"Event Router Warning: LLM chose an unknown action: '{action_name}'")
                    continue

                action_details = ACTION_TO_TOOL_MAP[action_name]
                tool_name_on_appstate = action_details["tool_name"]
                param_prompt = action_details["param_prompt"]
                tool_function = getattr(app_state, tool_name_on_appstate, None)

                if not tool_function:
                    print(f"Event Router ERROR: Tool '{tool_name_on_appstate}' not found on app_state!")
                    continue

                param = None
                if param_prompt:
                    full_param_prompt = f"Event Context: \"{event_context_sentence}\"\n\nTask: {param_prompt}"
                    param = generate_router_text(full_param_prompt, temperature=0.6)
                
                if param_prompt and not param:
                    print(f"Event Router Warning: Failed to generate parameter for action '{action_name}'. Skipping.")
                    continue

                print(f"Event Router: Executing app_state.{tool_name_on_appstate} with param: '{str(param)[:50]}...'")
                try:
                    # Special handling for tools that are threads or require complex logic
                    if action_name in ["DreamDesktopWallpaper", "GenerateImageIdea", "QueueDeepResearch", "WebSearch"]:
                        threading.Thread(target=tool_function, args=(param,), daemon=True).start()
                    else:
                        if param:
                            tool_function(param)
                        else:
                            tool_function()
                except Exception as e_exec:
                    print(f"Event Router ERROR executing tool '{tool_name_on_appstate}': {e_exec}")
                    traceback.print_exc()

                time.sleep(1) # Small delay between dispatched actions

            app_state.event_queue.task_done()

        except queue.Empty:
            continue
        except Exception as e:
            print(f"!!! Event Router Error (Outer Loop): {e}")
            traceback.print_exc()
            time.sleep(60)

    print("Event Router (Corrected): The 'Event Breeze' has stilled. Shutting down.")