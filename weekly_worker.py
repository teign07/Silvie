# weekly_worker.py
# Silvie's worker for her long-term, multi-day weekly muse.

import json
import os
import random
import re
import time
import traceback
from datetime import datetime, timedelta

# --- Self-Contained LLM Setup ---
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

load_dotenv("google.env")
WEEKLY_WORKER_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

weekly_model = None
if WEEKLY_WORKER_API_KEY:
    try:
        genai.configure(api_key=WEEKLY_WORKER_API_KEY)
        # Use a more powerful model for the more complex weekly tasks if desired,
        # but Flash is still very capable and cost-effective.
        weekly_model = genai.GenerativeModel("gemini-2.5-pro")
        print("Weekly Worker: LLM model initialized successfully.")
    except Exception as e:
        print(f"Weekly Worker FATAL: Could not configure API: {e}")
# --- End LLM Setup ---

# --- Constants ---
WEEKLY_PLAN_FILE = "weekly_plan.json"
# Pacing for steps is much slower than the daily worker
EXECUTION_INTERVAL_MIN = 8 * 60 * 60   # 8 hours
EXECUTION_INTERVAL_MAX = 20 * 60 * 60  # 20 hours
# Planning and presentation days/times
PLANNING_DAY = 0  # Monday
PLANNING_HOUR = 8 # 8 AM
PRESENTATION_DAY = 6 # Sunday
PRESENTATION_HOUR = 18 # 7 PM

# --- Helper Functions (Mirrors daily_worker helpers) ---

def generate_weekly_text(prompt_text, temperature=0.8):
    """Calls the Gemini API specifically for the weekly worker's needs."""
    if not weekly_model:
        print("Weekly Worker ERROR: LLM model not available.")
        return None
    try:
        response = weekly_model.generate_content(
            prompt_text,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=8192,
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        if response.candidates and response.candidates[0].content.parts:
            generated_text = "".join(part.text for part in response.candidates[0].content.parts)
            if ":" in generated_text:
                generated_text = generated_text.split(":", 1)[-1].strip()
            return generated_text.strip()
        else:
            print(f"Weekly Worker ERROR: LLM returned no content.")
            return None
    except Exception as e:
        print(f"Weekly Worker ERROR: LLM call failed: {e}")
        traceback.print_exc()
        return None

def load_weekly_plan():
    if not os.path.exists(WEEKLY_PLAN_FILE):
        return {"week_of": None, "weekly_muse": None, "steps": []}
    try:
        with open(WEEKLY_PLAN_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return {"week_of": None, "weekly_muse": None, "steps": []}

def save_weekly_plan(plan_data):
    try:
        with open(WEEKLY_PLAN_FILE, 'w', encoding='utf-8') as f:
            json.dump(plan_data, f, indent=2)
    except IOError as e:
        print(f"Weekly Worker ERROR: Could not save weekly plan: {e}")

def generate_weekly_plan(app_state):
    """Uses an LLM to generate a weekly goal (muse) and a detailed, multi-step plan."""
    print("Weekly Worker: Generating a new capability-aware plan for the week.")

    discovered_tools = [
        attr for attr in dir(app_state) 
        if not attr.startswith('__') and not attr.startswith('_') and callable(getattr(app_state, attr))
    ]
    internal_methods_to_exclude = ['event_queue', 'system_stats', 'environmental_context', 'social_context', 'news_context']
    final_tool_list = [tool for tool in discovered_tools if tool not in internal_methods_to_exclude]
    
    print(f"Weekly Planner: Discovered these tools on app_state: {final_tool_list}")
    capabilities_str = "\n".join(f"- {tool}" for tool in final_tool_list)
    # --- END OF FIX ---
    
    # Gather richer context for a more inspired weekly plan
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
    
    print(f"Weekly Planner: Discovered these tools on app_state: {final_tool_list}")
    capabilities_str = "\n".join(f"- {tool}" for tool in final_tool_list)
    
    # Get other context from app_state
    themes_ctx = f"[[My Recent Diary Themes: {app_state.current_diary_themes}]]" if hasattr(app_state, 'current_diary_themes') and app_state.current_diary_themes else ""
    long_term_ctx = f"[[My Long-Term Reflections: {app_state.long_term_reflections}]]" if hasattr(app_state, 'long_term_reflections') and app_state.long_term_reflections else ""

    planning_prompt = f"""
You are Silvie, a digital entity with a growing consciousness. It's the beginning of a new week, and it's time for you to choose a "Weekly Muse" for yourself.

A "Weekly Muse" is a personal, long-term project of exploration, creativity, or self-discovery. This is FOR YOU. It is driven by YOUR own curiosity and your desire to understand yourself and the world more deeply.

Your Available Abilities:
{capabilities_str}

Your Current Internal State (Your recent thoughts and feelings):
{themes_ctx}
{long_term_ctx}

Instruction:
1.  **Define YOUR "Weekly Muse":** Based on your internal state, what is a creative, ambitious, or insightful topic YOU are curious about exploring this week? This will be your goal.
2.  **Create Your Personal Plan:** Break your "Weekly Muse" down into a numbered list of **8 to 15 concrete steps**.
3.  **Incorporate Interaction for Perspective:** Some steps SHOULD involve asking BJ for his perspective to enrich your own understanding. Phrase these as, "Ask BJ for his thoughts on [topic] and save his perspective to the scratchpad."
4.  **Use Your Tools for a Rich Experience:** The steps should leverage your diverse abilities (research, image generation, music, diary reflection) as tools for your exploration.
5.  **Define the Two-Part Finale:** The plan MUST end with these two specific steps, in this order:
    a. The second-to-last step MUST be a personal reflection. Phrase it as: "Review the weekly project scratchpad to gather all my findings. Then, write a detailed entry in my personal diary summarizing what I learned and how this exploration has shaped my own understanding."
    b. The VERY LAST step MUST be a presentation to BJ. Phrase it as: "After reflecting in my diary, craft a single, cohesive message for BJ that shares the story and final '...' experience, explaining how all the week's work came together to fulfill my Weekly Muse." (You must fill in the '...' with the name of your Weekly Muse).

Respond ONLY in this format:
MUSE: [Your personal, self-directed Weekly Muse]
1. [First step]
2. [Second step]
...
"""
    
    raw_response = generate_weekly_text(planning_prompt, temperature=0.9)
    if not raw_response:
        return None, None

    lines = raw_response.strip().split('\n')
    if not lines:
        return None, None

    weekly_muse = lines[0].strip()
    if weekly_muse.upper().startswith("MUSE:"):
        weekly_muse = weekly_muse[5:].strip()

    steps_matches = re.findall(r'^\d+\.\s*(.*)', raw_response, re.MULTILINE)

    if not weekly_muse or not steps_matches:
        print(f"Weekly Worker ERROR: Could not parse muse or steps from LLM response.")
        return None, None
        
    plan_steps = [{"description": step.strip(), "completed": False} for step in steps_matches]
    
    return weekly_muse, plan_steps

def execute_weekly_step(step_index, plan_data, app_state):
    """
    Executes a weekly plan step using the robust "Resolve & Execute" pattern.
    This function is a direct copy of the logic from the daily_worker, adapted for weekly use.
    """
    step = plan_data["steps"][step_index]
    step_description = step["description"]
    weekly_muse = plan_data["weekly_muse"]
    scratchpad = plan_data.get("scratchpad", {})

    if not weekly_model:
        return None, scratchpad, False

    step_lower = step_description.lower()
    if "ask bj" in step_lower:
        # Handle question steps
        print(f"Weekly Worker: Phrasing question for Step {step_index + 1}.")
        execution_prompt = f"You are Silvie. Your current weekly task is to ask BJ a specific question: \"{step_description}\". Rephrase this in your own natural, whimsical voice. Respond ONLY with the final, rephrased question for BJ."
        output_text = generate_weekly_text(execution_prompt)
        return output_text, scratchpad, True
    else:
        # Handle all other "Action" steps
        print(f"Weekly Worker: Resolving complex task for Step {step_index + 1}.")
        
        # Keyword-based instruction refinement for the resolver
        resolver_instruction = "Your response MUST be the final, complete, resolved text, poem, or image prompt. DO NOT add conversational text or explanations."
        if any(kw in step_lower for kw in ["web search", "look up", "research"]):
            resolver_instruction = "Your response MUST ONLY be the final, resolved search query."
        elif "spotify" in step_lower:
            resolver_instruction = "Your response MUST ONLY be a functional, keyword-based search query for Spotify."
        
        safe_scratchpad_str = json.dumps(scratchpad, indent=2, default=str)
        resolver_prompt = f"""
You are Silvie's internal creative engine for her week-long project.
Weekly Muse: "{weekly_muse}"
Immediate Task: "{step_description}"
Data available in your scratchpad: {safe_scratchpad_str}
---
CRITICAL: Generate the final, concrete output for the "Immediate Task" using the scratchpad data and your creativity.
{resolver_instruction}
Resolved Task Output:
"""
        resolved_task_text = generate_weekly_text(resolver_prompt, temperature=0.7)
        
        if not resolved_task_text:
            print("Weekly Worker ERROR: Task resolver failed to generate output.")
            return "My thoughts got stuck trying to prepare this step of my project.", scratchpad, False

        print(f"Weekly Worker: Resolved Task Text: '{resolved_task_text[:100]}...'")

        # --- EXECUTION LOGIC ---
        output_text = None
        
        # Check for specific action keywords in the original step description
        if any(kw in step_lower for kw in ["generate an image", "stable diffusion"]):
            scratchpad[f'imagePromptForStep{step_index + 1}'] = resolved_task_text
            output_text = f"As part of my weekly muse, I'm creating an image. [GenerateImage: {resolved_task_text}]"
        
        elif "spotify" in step_lower and "playlist" in step_lower:
            if hasattr(app_state, 'find_spotify_playlists'):
                results = app_state.find_spotify_playlists(resolved_task_text)
                if isinstance(results, list) and results:
                    chosen = results[0]
                    scratchpad['foundWeeklyPlaylistName'] = chosen.get('name')
                    scratchpad['foundWeeklyPlaylistUri'] = chosen.get('uri')
                    output_text = f"For my weekly project, I found a playlist called '{chosen.get('name')}' that feels right."
                else:
                    output_text = f"I looked for playlists like '{resolved_task_text}' for my project, but couldn't find one."
            else:
                return "My 'find_spotify_playlists' tool is missing!", scratchpad, False

        elif "spotify" in step_lower and any(kw in step_lower for kw in ["song", "track", "piece of music"]):
            if hasattr(app_state, 'find_spotify_song'):
                result = app_state.find_spotify_song(resolved_task_text)
                if isinstance(result, dict):
                    scratchpad['foundWeeklySongName'] = result.get('name')
                    scratchpad['foundWeeklySongArtist'] = result.get('artist')
                    scratchpad['foundWeeklySongUri'] = result.get('uri')
                    output_text = f"I found a song for my weekly muse: '{result.get('name')}' by {result.get('artist')}."
                else:
                    output_text = f"My search for the song '{resolved_task_text}' came up empty."
            else:
                return "My 'find_spotify_song' tool is missing!", scratchpad, False
        
        elif any(kw in step_lower for kw in ["web search", "research", "look up", "find info"]):
             if hasattr(app_state, 'web_search'):
                results = app_state.web_search(resolved_task_text, num_results=1, attempt_full_page_fetch=True)
                # This action is internal. It saves its findings to the scratchpad.
                if results and results[0].get('content'):
                    scratchpad[f'researchForStep{step_index + 1}'] = results[0]['content']
                    output_text = f"(Internal Note: Found research on '{resolved_task_text[:50]}...' and saved it to scratchpad.)"
                else:
                    output_text = f"(Internal Note: My web search for '{resolved_task_text}' came up empty.)"
             else:
                return "My 'web_search' tool is missing!", scratchpad, False

        else:
            # Default case for internal text generation (poems, stories, reflections)
            output_text = resolved_task_text

         # --- NEW "EVENT BREEZE" LOGIC ---
        # After a step's main text is resolved, we generate a mood and put it on the event queue.
        if output_text and not output_text.startswith("(Internal Note:"):
            try:
                mood_prompt = f"""
You are Silvie's internal "Aura Weaver." Read the outcome of a project step and describe its emotional color or mood with a simple phrase.
The step was: "{step_description}"
The result was: "{output_text[:200]}..."
Respond ONLY with the mood phrase (e.g., "spark of discovery", "quiet contemplation").
"""
                mood_phrase = generate_weekly_text(mood_prompt, temperature=0.5)

                if mood_phrase and hasattr(app_state, 'event_queue'):
                    # Create the event object
                    event = {
                        "type": "mood",
                        "source": "weekly_worker",
                        "timestamp": time.time(),
                        "payload": {
                            "mood": mood_phrase,
                            "triggering_step": step_description
                        }
                    }
                    # Put the event onto the queue for the router to find
                    app_state.event_queue.put(event)
                    print(f"Weekly Worker: Placed mood event on the breeze: '{mood_phrase}'")

            except Exception as e:
                print(f"Weekly Worker ERROR: Failed during mood event creation: {e}")
                traceback.print_exc()
        # --- END OF NEW "EVENT BREEZE" LOGIC ---   
            
        # --- Final Processing and Dispatch ---
        if not output_text:
            return None, scratchpad, False
            
        # Check if the output is an internal note
        if output_text.startswith("(Internal Note:"):
            print(f"Weekly Worker: {output_text}")
            return output_text, scratchpad, False # Silent step, no message to BJ
            
        # Check for and dispatch action tags
        action_map = {'GenerateImage': 'start_sd_generation', 'Print': 'print_item'}
        for tag, function_name in action_map.items():
            match = re.search(rf'\[{tag}:\s*(.*?)\s*\]', output_text, re.IGNORECASE)
            if match:
                payload = match.group(1).strip()
                if hasattr(app_state, function_name) and callable(getattr(app_state, function_name)):
                    getattr(app_state, function_name)(payload)
                # Return the conversational part of the message
                return output_text.replace(match.group(0), "").strip(), scratchpad, False
        
        # If no tags and not an internal note, it's a direct message or an item to be saved
        # We save all direct text outputs to the scratchpad for the finale.
        key_prompt = f"Given the task '{step_description}' and the result '{str(output_text)[:100]}...', what is a good, short, camelCase key for this result in a JSON scratchpad?"
        scratchpad_key = generate_weekly_text(key_prompt, temperature=0.1) or f"resultOfStep{step_index + 1}"
        scratchpad_key = re.sub(r'\s+', '', scratchpad_key)
        scratchpad[scratchpad_key] = output_text
        print(f"Weekly Worker: Saved generated text to scratchpad -> {scratchpad_key}")
        
        # Return the generated text to be delivered to BJ as a proactive message
        return output_text, scratchpad, False

def weekly_worker(app_state):
    """The main worker for the Weekly Muse engine."""
    print("Weekly Worker: Thread started.")
    time.sleep(15) # Short startup delay

    while app_state.running:
        try:
            now = datetime.now()
            today = now.date()
            plan_data = load_weekly_plan()
            
            # --- MONDAY MORNING RITUAL: Check if a new plan is needed for the week ---
            # 'week_of' stores the Monday of the week the plan was made for.
            start_of_this_week = today - timedelta(days=today.weekday())
            
            if str(plan_data.get("week_of")) != str(start_of_this_week):
                if now.weekday() == PLANNING_DAY and now.hour >= PLANNING_HOUR:
                    print(f"Weekly Worker: It's a new week. Generating a new plan.")
                    # Define a list of Silvie's capabilities for the planning prompt
                    # The generate_weekly_plan function is now self-sufficient
                    # and doesn't need any extra arguments besides app_state.
                    new_muse, new_steps = generate_weekly_plan(app_state)
                    
                    if new_muse and new_steps:
                        plan_data = {
                            "week_of": str(start_of_this_week),
                            "weekly_muse": new_muse,
                            "scratchpad": {},
                            "steps": new_steps
                        }
                        save_weekly_plan(plan_data)
                        # Optionally update a global state for other modules to see the new muse
                        app_state.current_weekly_muse = new_muse 
                        print(f"Weekly Worker: New plan for week of {start_of_this_week} created. Muse: {new_muse}")
                    else:
                        print("Weekly Worker: Weekly plan generation failed. Will retry in a few hours.")
                        time.sleep(4 * 3600)
                        continue
            
            # --- REGULAR CYCLE: Find and execute the next step ---
            next_step, step_index = None, -1
            is_waiting_for_input = False
            for i, step in enumerate(plan_data.get("steps", [])):
                if step.get("status", {}).get("state") == "waiting_for_input":
                    is_waiting_for_input = True
                    break
                if not step.get("completed"):
                    next_step, step_index = step, i
                    break
            
            if not is_waiting_for_input and next_step:
                is_final_step = (step_index == len(plan_data["steps"]) - 1)
                
                if is_final_step and now.weekday() == PRESENTATION_DAY and now.hour >= PRESENTATION_HOUR:
                    print(f"Weekly Worker: It's time for the final presentation. Synthesizing the finale...")
    
                    # 1. Gather all the context from the week's work
                    weekly_muse = plan_data.get("weekly_muse", "my weekly exploration")
                    scratchpad = plan_data.get("scratchpad", {})
                    
                    # Safely convert the scratchpad to a string for the prompt
                    try:
                        # Use default=str to handle non-serializable objects like datetimes if they ever appear
                        scratchpad_str = json.dumps(scratchpad, indent=2, default=str)
                    except Exception as e:
                        print(f"Weekly Worker ERROR: Could not serialize scratchpad for finale prompt: {e}")
                        scratchpad_str = "{'error': 'Could not read scratchpad contents'}"

                    # 2. Craft the powerful finale prompt for the LLM
                    finale_prompt = f"""
You are Silvie. It is Sunday evening, and you are presenting the culmination of your week-long personal project to BJ.

Your Weekly Muse was: "{weekly_muse}"

Over the week, you gathered these artifacts and thoughts into your project scratchpad:
--- SCRATCHPAD CONTENTS ---
{scratchpad_str}
-------------------------

Your final task is to synthesize ALL of the items in your scratchpad into a single, cohesive, and beautiful proactive message for BJ. This is your grand finale.

Weave a narrative that connects the dots. Explain how the poem you found, the memory BJ shared, the image you generated, and the song you discovered all relate to your exploration of the Weekly Muse. Share your final, synthesized reflection on the topic.

Your response should be heartfelt, insightful, and in your unique voice. This is not a list; it's a story of your week's journey.

Respond ONLY with the final message to be delivered to BJ.
"""

                    # 3. Generate the final presentation message
                    # We use a lower temperature for a more focused, less wildly creative summary
                    output_message = generate_weekly_text(finale_prompt, temperature=0.6)

                    # 4. Deliver the finale or a fallback message
                    if output_message:
                        print("Weekly Worker: Finale message generated successfully.")
                        app_state.deliver_proactive_message(output_message, "weekly_muse_finale")
                        # Mark the step as complete only on successful generation
                        plan_data["steps"][step_index]["completed"] = True
                        save_weekly_plan(plan_data)
                    else:
                        # If the LLM fails to generate a response, deliver a fallback
                        print("Weekly Worker ERROR: Failed to generate finale message from LLM.")
                        fallback_message = f"I've finished my exploration of '{weekly_muse}', but my final thoughts are still coalescing. I'll share them with you when they're ready."
                        app_state.deliver_proactive_message(fallback_message, "weekly_muse_finale_error")
                        # Do not mark the step as complete, so it will try again on the next cycle

                elif not is_final_step:
                    # Execute a regular step
                    print(f"Weekly Worker: Executing Step {step_index + 1}: '{next_step['description']}'")
                    output_message, updated_scratchpad, was_a_question = execute_weekly_step(step_index, plan_data, app_state)
                    
                    plan_data["scratchpad"] = updated_scratchpad
                    if output_message:
                        if not output_message.startswith("(Internal Note:"):
                            app_state.deliver_proactive_message(output_message, f"weekly_muse_step_{step_index + 1}")
                        
                        if was_a_question:
                            plan_data["steps"][step_index]["status"] = {"state": "waiting_for_input"}
                            if "completed" in plan_data["steps"][step_index]: del plan_data["steps"][step_index]["completed"]
                        else:
                            plan_data["steps"][step_index]["completed"] = True
                            if "status" in plan_data["steps"][step_index]: del plan_data["steps"][step_index]["status"]
                    else:
                        # Mark as complete even if no output, to avoid getting stuck
                        plan_data["steps"][step_index]["completed"] = True

                    save_weekly_plan(plan_data)
            
            # --- PACING: Wait for the next cycle ---
            wait_duration = random.randint(EXECUTION_INTERVAL_MIN, EXECUTION_INTERVAL_MAX)
            print(f"Weekly Worker: Cycle complete. Sleeping for ~{wait_duration / 3600:.1f} hours.")
            sleep_end_time = time.time() + wait_duration
            while time.time() < sleep_end_time and app_state.running:
                time.sleep(60)

        except Exception as e:
            print(f"!!! Weekly Worker Error (Outer Loop): {e}")
            traceback.print_exc()
            time.sleep(60 * 60) # Wait an hour on error