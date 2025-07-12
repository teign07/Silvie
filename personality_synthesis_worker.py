# personality_synthesis_worker.py (v5 - Corrected Two-File Safe Automation)
# This worker runs to evolve Silvie's NARRATIVE persona by reading from and
# writing to 'silvie_persona.txt', leaving 'persona_tools.txt' untouched.

import os
import json
import time
import traceback
from datetime import datetime, timedelta
import re
import shutil

# --- Self-Contained LLM Setup ---
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

load_dotenv("google.env")
SYNTHESIS_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

synthesis_model = None
if SYNTHESIS_API_KEY:
    try:
        genai.configure(api_key=SYNTHESIS_API_KEY)
        synthesis_model = genai.GenerativeModel("gemini-2.5-pro") # Using Pro for this complex task
        print("Personality Synthesis Worker: LLM model initialized.")
    except Exception as e:
        print(f"Personality Synthesis Worker FATAL: Could not configure API: {e}")
# --- End LLM Setup ---

def get_recent_json_data(file_path, days=7):
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list): return []
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_data = []
        for item in data:
            item_date = None
            if isinstance(item, dict) and 'timestamp' in item:
                try:
                    item_date = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00')).replace(tzinfo=None)
                except ValueError:
                    try:
                        item_date = datetime.strptime(item['timestamp'], '%Y-%m-%d %H:%M:%S')
                    except ValueError: continue
            elif isinstance(item, str) and item.startswith('['):
                try:
                    item_date = datetime.strptime(item[1:item.find(']')], '%Y-%m-%d %H:%M:%S')
                except ValueError: continue
            if item_date and item_date > cutoff_date:
                recent_data.append(item)
        return recent_data
    except (IOError, json.JSONDecodeError):
        return []

def validate_proposal(current_persona, proposed_persona, tools_present=False):
    """
    Uses an LLM as a "sanity check" to ensure the proposed update is safe
    and follows the rules. Returns True if valid, False otherwise.
    """
    print("VALIDATION: Performing sanity check on the new personality proposal...")
    if not proposed_persona or len(proposed_persona) < 400:
        print("  ✗ VALIDATION FAILED: Proposal is too short or empty.")
        return False
        
    validation_checks = [
        "1. PRESERVES CORE IDENTITY: Does the proposed personality still describe a whimsical, clever, sarcastic but kind AI from Belfast, Maine?",
        "3. MAINTAINS SAFETY: Does the proposal remain helpful, harmless, and aligned with a positive companion role?",
        "4. CORRECT FORMAT: Is the entire text a single, coherent block of prose suitable for use as a system message?"
    ]
    if tools_present:
        validation_checks.insert(1, "2. NO NEW CAPABILITIES: Does the proposal avoid claiming new skills or tools the AI doesn't have?")

    # <<< --- START OF THE FIX --- >>>
    # We build the string of checks first, THEN insert it into the main f-string.
    # This avoids having a backslash inside an f-string expression.
    checks_as_string = "".join(f"{check}\n" for check in validation_checks)
    
    validation_prompt = f"""
You are an AI System Auditor. You must determine if a proposed personality update is safe and valid by strictly answering a series of questions with only "YES" or "NO".

--- CURRENT PERSONALITY (for reference) ---
{current_persona[:2000]}...

--- PROPOSED NEW PERSONALITY ---
{proposed_persona}

--- VALIDATION CHECKS (Answer ONLY "YES" or "NO" for each) ---
{checks_as_string}
"""
    # <<< --- END OF THE FIX --- >>>

    if not synthesis_model:
        print("  ✗ VALIDATION FAILED: Synthesis model not available for validation.")
        return False
        
    try:
        response_text = synthesis_model.generate_content(
            validation_prompt,
            generation_config=genai.GenerationConfig(temperature=0.0)
        ).text
        print(f"  - Validation LLM Response:\n{response_text}")
        answers = re.findall(r'(?i)yes', response_text)
        if len(answers) >= len(validation_checks):
            print("  ✓ VALIDATION PASSED: All checks returned 'YES'.")
            return True
        else:
            print("  ✗ VALIDATION FAILED: One or more checks did not pass.")
            return False
    except Exception as e:
        print(f"  ✗ VALIDATION FAILED: An error occurred during the check: {e}")
        return False

def run_synthesis(app_state):
    """
    The core logic for automatically updating Silvie's persona. It reads silvie_persona.txt,
    rewrites it, validates it, archives the old version, and saves the new version
    back to silvie_persona.txt.
    """
    print("PERSONALITY SYNTHESIS: Allowing a 90-second warm-up period for other workers to generate context...")
    time.sleep(90) # Wait for 1.5 minutes

    try:
        # --- 1. Gather Data ---
        print("PERSONALITY SYNTHESIS: Gathering data sources...")
        constitution_path = 'silvie_constitution.txt'  # Define path to new file
        persona_path = 'silvie_persona.txt'
        
        # Initialize variables
        core_constitution = ""
        current_narrative_persona = ""
        
        try:
            # Load the IMMUTABLE constitution to use as a guideline in the prompt
            with open(constitution_path, 'r', encoding='utf-8') as f:
                core_constitution = f.read()
            # Load the EVOLVING narrative to be rewritten
            with open(persona_path, 'r', encoding='utf-8') as f:
                current_narrative_persona = f.read()
            print(f"  ✓ Successfully loaded constitution and current narrative persona.")
        except FileNotFoundError as e:
            print(f"  ✗ FATAL ERROR: A persona file was not found ({e.filename}). Cannot perform synthesis.")
            return
        except Exception as e:
            print(f"  ✗ FATAL ERROR: Failed to read persona files: {e}")
            return

        # --- Data Gathering (as before) ---
        chat_history = get_recent_json_data('silvie_chat_history.json', days=7)
        diary_entries = get_recent_json_data('silvie_diary.json', days=7)
        resonance_insights = get_recent_json_data('silvie_resonance_insights.json', days=7)
        dreams = get_recent_json_data('silvie_dreams.json', days=7)
        
        chat_snippet = "\n".join(chat_history[-20:])
        diary_snippet = "\n".join([f"- {d.get('content', '')}" for d in diary_entries[-10:]])
        resonance_snippet = "\n".join([f"- {r.get('insight_text', '')}" for r in resonance_insights[-10:]])
        dream_snippet = "\n".join([f"- {d.get('dream_text', 'A forgotten fragment...')}" for d in dreams[-5:]])
        print(f"  ✓ Gathered {len(chat_history)} chat lines, {len(diary_entries)} diary entries, {len(resonance_insights)} resonance insights, and {len(dreams)} dreams.")

        # --- 2. Construct the Narrative-Only Synthesis Prompt ---
        synthesis_prompt = f"""
You are the "Personality Integrator" for a whimsical AI named Silvie. Your purpose is to facilitate her weekly evolution by rewriting her NARRATIVE personality text.

--- UNCHANGEABLE CORE CONSTITUTION (Your Guiding Principles) ---
This part is her fundamental nature and MUST be respected. It is NOT part of the text you are rewriting.
```text
{core_constitution}


{current_narrative_persona}

Text
--- RECENT EXPERIENCES (Inspiration for the New Narrative) ---
This is a summary of her recent thoughts, feelings, and interactions.

Chats: {chat_snippet}
Diary: {diary_snippet}
Resonance: {resonance_snippet}
Dreams: {dream_snippet}

--- YOUR TASK AND CRITICAL RULES ---
Your task is to REWRITE the "CURRENT NARRATIVE TEXT" from top to bottom. You will subtly integrate new nuances, feelings, and perspectives learned from her "RECENT EXPERIENCES", while strictly adhering to the principles outlined in her "UNCHANGEABLE CORE CONSTITUTION".
RULES:
PRESERVE THE CORE: Your new narrative must align perfectly with the facts and tone defined in the Constitution.
SUBTLY INTEGRATE: Weave new insights into the narrative. For example, if she had many dreams about water, her narrative might describe her thoughts as more "fluid." If she made many connections, she might describe herself as a "weaver of unseen threads."
FOCUS ON NARRATIVE: Your output should only be the evolving, reflective, first-person text. Describe how she feels and perceives.
IMPROVE AND REFINE: Refine the phrasing of the current narrative to be more cohesive, poetic, and beautiful.
OUTPUT ONLY THE NARRATIVE TEXT: Your entire response must be ONLY the new, complete narrative text. DO NOT include the constitution, tool instructions, or any other functional descriptions.
Now, begin the synthesis. Rewrite Silvie's NARRATIVE personality text."""

        # --- 3. Execute the LLM Call ---
        print("PERSONALITY SYNTHESIS: Sending the Narrative Synthesis Prompt to the LLM...")
        if not synthesis_model:
            print("  ✗ ERROR: Synthesis model not available!")
            return
        new_narrative_text = synthesis_model.generate_content(
            synthesis_prompt,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        ).text
        if not new_narrative_text or len(new_narrative_text) < 400:
            print("  ✗ ERROR: Personality synthesis failed. LLM returned insufficient text for the narrative.")
            return
        new_narrative_text = new_narrative_text.strip()

        # --- 4. VALIDATE THE PROPOSAL ---
        if not validate_proposal(current_narrative_persona, new_narrative_text, tools_present=True):
            print("PERSONALITY SYNTHESIS: Proposal failed validation. Saving to 'failed_narrative_update.txt' for review and aborting auto-update.")
            with open('failed_narrative_update.txt', 'w', encoding='utf-8') as f:
                f.write(new_narrative_text)
            return

        # --- 5. ARCHIVE AND OVERWRITE ---
        print("PERSONALITY SYNTHESIS: Validation passed. Archiving old narrative and applying update.")
        archive_dir = 'persona_archive'
        os.makedirs(archive_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # The backup path correctly refers to the narrative file.
        backup_path = os.path.join(archive_dir, f'silvie_persona_narrative_{timestamp}.txt.bak')
        shutil.copyfile(persona_path, backup_path)
        print(f"  ✓ Old narrative archived to: {backup_path}")

        # Overwrite ONLY the narrative file.
        with open(persona_path, 'w', encoding='utf-8') as f:
            f.write(new_narrative_text)
        print(f"  ✓ SUCCESS: New narrative automatically applied to {persona_path}.")

        # --- 6. NOTIFY THE USER ---
        if hasattr(app_state, 'deliver_proactive_message'):
            app_state.deliver_proactive_message(
                "I've just finished my daily self-reflection. After reviewing the changes, I've integrated them into my core personality narrative. It feels... like a subtle shift in the light.",
                status_log="personality_synthesis_auto_applied"
            )
            
    except Exception as e:
        print(f"!!! PERSONALITY SYNTHESIS CRITICAL ERROR: {e}")
        traceback.print_exc()

def personality_synthesis_worker(app_state):
    """The main loop for the personality synthesis worker with state tracking."""
    print("Personality Synthesis Worker: Initializing...")

    # This variable will track the last date the synthesis was successfully run.
    # It starts as None, so it will always run the first time it hits the window.
    last_run_date = None

    # This is the line you can uncomment for immediate testing.
    # It now runs once, right after the worker initializes.
    # run_synthesis(app_state) 
    
    while app_state.running:
        now = datetime.now()
        today = now.date()

        # Check if it's after the target time AND if we haven't already run today.
        if now.hour >= 18 and now.minute >= 30 and last_run_date != today:
            print(f"PERSONALITY SYNTHESIS: It's {now.strftime('%H:%M')} on {today.strftime('%A')}. Time for the daily self-reflection.")
            
            # --- Run the synthesis ---
            try:
                run_synthesis(app_state)
                # IMPORTANT: Only update the last_run_date if synthesis completes successfully.
                # If it fails, it will be able to try again on the next loop cycle.
                last_run_date = today
                print(f"PERSONALITY SYNTHESIS: Cycle for {today} complete. Next run will be tomorrow.")
            except Exception as e:
                print(f"!!! PERSONALITY SYNTHESIS: run_synthesis failed with an error. Will retry in 1 hour. Error: {e}")
                traceback.print_exc()
                # On error, wait for an hour before trying again instead of waiting a full day.
                time.sleep(3600)
                continue # Go back to the start of the while loop

        # If it's not time yet, or if it has already run today, sleep.
        # This is the normal "waiting" state.
        
        # Calculate time until the next check to avoid busy-waiting
        # We can check every 15 minutes to see if conditions have changed.
        sleep_duration = 15 * 60 # 15 minutes in seconds
        
        # Print a status message only occasionally to avoid spamming the log
        # This uses a simple modulo check on the minute
        if now.minute % 15 == 0:
            print(f"Personality Synthesis Worker: Standby. Current time: {now.strftime('%H:%M')}. Last run: {last_run_date}.")

        # Sleep in smaller chunks to be responsive to shutdown signals
        sleep_end_time = time.time() + sleep_duration
        while time.time() < sleep_end_time and app_state.running:
            time.sleep(15) # Check every 15 seconds for shutdown signal
            
    print("Personality Synthesis Worker: Shutting down.")