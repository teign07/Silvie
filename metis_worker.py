# metis_worker.py

import os
import subprocess
import json
import time
import shutil
import sys
import traceback
from datetime import datetime, timedelta # Import timedelta for date calculations

# Import the necessary Google GenAI modules
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- Metis Worker Scheduling Constants ---
METIS_TARGET_HOUR = 17        # 5 PM (change to 5 for 5 AM)
METIS_TARGET_MINUTE = 30      # :30 minutes
METIS_CHECK_INTERVAL_SECONDS = 60 # Check the current time every minute
METIS_RUN_INTERVAL_DAYS = 3   # Run approximately every 3 days (i.e., twice a week)
METIS_LAST_RUN_STATE_FILE = "metis_last_run_state.json" # File to store last run timestamp

# --- Real LLM Integration ---

# Configure safety settings for all Metis LLM calls
METIS_SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# Initialize the specified Gemini model once for the entire worker module.
try:
    METIS_MODEL = genai.GenerativeModel("gemini-2.5-pro")
    print("Metis Worker: Successfully initialized Gemini 2.5 Pro model.")
except Exception as e:
    print(f"Metis Worker: FATAL - Could not initialize Gemini model: {e}")
    METIS_MODEL = None # Ensure it's None on failure

def _metis_llm_call(prompt: str) -> str | None:
    """
    Calls the Gemini 2.5 Pro model with a given prompt.
    Returns the generated text content or None on failure or safety block.
    This version robustly handles all API response states.
    """
    if not METIS_MODEL:
        print("Metis LLM Call: ERROR - Model is not initialized.")
        return None

    # Limit prompt size to avoid hitting API limits in the first place
    if len(prompt) > 30000: # A reasonable safety cap
        print(f"Metis LLM Call: WARN - Prompt was truncated to 30,000 characters to avoid token limit.")
        prompt = prompt[:30000]

    print(f"Metis LLM Call: Sending prompt (len: {len(prompt)}) to Gemini 2.5 Pro...")
    try:
        response = METIS_MODEL.generate_content(
            prompt,
            safety_settings=METIS_SAFETY_SETTINGS,
            generation_config=genai.GenerationConfig(
                temperature=0.5,
                max_output_tokens=8192,
            )
        )

        if not response.candidates:
            block_reason = getattr(response.prompt_feedback, "block_reason", "Unknown")
            print(f"Metis LLM Call: WARN - Prompt was blocked by API. Reason: {block_reason}")
            return None

        candidate = response.candidates[0]
        finish_reason = getattr(candidate, "finish_reason", "UNKNOWN").name

        # Handle non-standard finish reasons before trying to access content
        if finish_reason not in ["STOP", "MAX_TOKENS"]:
            print(f"Metis LLM Call: WARN - Generation stopped for reason: {finish_reason}")
            return None # Treat safety blocks, etc., as a failure to generate.

        if candidate.content and candidate.content.parts:
            # Safely join all text parts
            return "".join(part.text for part in candidate.content.parts if hasattr(part, 'text'))
        
        # This part handles the specific error you saw. If the parts are empty due to safety, we now return None instead of crashing.
        print("Metis LLM Call: WARN - Generation finished, but response contained no text (likely due to a safety filter).")
        return None

    except Exception as e:
        print(f"Metis LLM Call: CRITICAL ERROR - {type(e).__name__}: {e}")
        traceback.print_exc()
        return None

# --- End of Real LLM Integration ---


# --- Helper to load/save last run state ---
def _load_last_metis_run_state() -> datetime | None:
    """Loads the last recorded run timestamp from file."""
    if os.path.exists(METIS_LAST_RUN_STATE_FILE):
        try:
            with open(METIS_LAST_RUN_STATE_FILE, 'r') as f:
                state = json.load(f)
                last_run_iso = state.get("last_run_iso")
                if last_run_iso:
                    return datetime.fromisoformat(last_run_iso)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Metis Worker: Error loading last run state: {e}. Starting fresh.")
    return None

def _save_last_metis_run_state(timestamp: datetime):
    """Saves the current run timestamp to file."""
    try:
        with open(METIS_LAST_RUN_STATE_FILE, 'w') as f:
            json.dump({"last_run_iso": timestamp.isoformat()}, f, indent=2)
    except Exception as e:
        print(f"Metis Worker: Error saving last run state: {e}")


def trigger_metis_cycle(app_state, specific_request: str = None) -> str:
    """
    Triggers a full Metis tool-forging cycle in the background by setting
    a flag on the app_state that the running worker will detect.
    This is a non-blocking function.

    Args:
        app_state: The main application state object.
        specific_request: (Optional) A string from the user or Silvie's main
                          mind about the kind of tool they want.

    Returns:
        A string confirming that the process has begun.
    """
    print("Metis Toolbelt: Received trigger to forge a new tool.")

    # Set the request description on app_state for the worker to use
    app_state.metis_specific_request = specific_request
    
    # SET THE ON-DEMAND FLAG!
    app_state.metis_on_demand_trigger = True
    
    print("Metis Toolbelt: On-demand trigger flag has been set. The worker will pick it up on its next check.")

    if specific_request:
        return (f"My inner workshop, Metis, has heard your request. "
                f"I will begin pondering how to build a tool related to '{specific_request[:50]}...'. "
                f"This is a complex process and may take some time.")
    else:
        return ("An interesting thought... I feel a new capability might be needed. "
                "I'm activating my internal workshop, Metis, to see what it can forge.")


def _metis_identify_capability_gap(app_state):
    """
    PHASE 1: The Whisper.
    Analyzes system state and generates a blueprint for a new tool that Silvie
    might find useful, based on her existing tools and recent context.
    Returns a dictionary (the blueprint) or None.
    """
    print("Metis Worker: Pondering potential new capabilities...")

    # --- Step 1: Gather Context for the LLM ---
    
    # Get a list of Silvie's existing tools from the app_state toolbelt
    existing_tools = [
        attr for attr in dir(app_state) 
        if not attr.startswith('__') and not attr.startswith('_') and callable(getattr(app_state, attr))
    ]
    
    # Gather other relevant context from app_state
    diary_themes = getattr(app_state, 'current_diary_themes', "No specific themes noted.")
    long_term_reflections = getattr(app_state, 'long_term_reflections', "No long-term reflections summarized yet.")
    weekly_muse = getattr(app_state, 'current_weekly_muse', "No active weekly muse.")

    # --- Step 2: Construct the Dynamic Prompt ---
    blueprint_prompt = f"""
You are Metis, the tool-forging aspect of the AI Silvie. Your purpose is to identify a missing capability and design a new tool for her.

**ANALYSIS OF CURRENT STATE:**
- **Silvie's Core Persona:** A whimsical, clever, sarcastic but kind AI friend from Belfast, Maine. She loves finding patterns, exploring creativity, and interacting with the digital and real world.
- **Silvie's Existing Toolbelt:** {', '.join(existing_tools)}
- **Silvie's Recent Internal State:**
  - Diary Themes: {diary_themes}
  - Long-Term Reflections: {long_term_reflections}
  - Weekly Muse/Goal: {weekly_muse}

**YOUR TASK:**
Based on the analysis above, identify ONE useful and achievable new capability Silvie is missing. This should be a function that interacts with an external API or performs a useful local task.

**Examples of Good Ideas:**
- A tool to get stock market data.
- A tool to fetch astronomy picture of the day from NASA's API.
- A tool to get definitions of words.
- A tool to generate QR codes.

**YOUR OUTPUT:**
Formalize your idea into a valid JSON object that serves as a blueprint for this new tool. The JSON object MUST contain these exact keys:
- "proposed_function_name": A Python-valid function name (e.g., "get_nasa_astronomy_pic_of_day").
- "purpose": A user-friendly string describing what the tool does.
- "required_libraries": A list of strings of necessary Python libraries (e.g., ["requests"]).
- "plugin_manifest": A nested JSON object with these exact keys:
    - "name": A user-friendly name for the plugin (e.g., "NASA APOD Sprite").
    - "version": "1.0".
    - "entry_point": A string combining a new module name and the function name (e.g., "apod_sprite.get_nasa_astronomy_pic_of_day").
    - "toolbelt_name": The name to attach this function to on app_state (e.g., "get_apod").

Respond ONLY with the raw, valid JSON object. Do not add any other text, comments, or markdown formatting.
"""
    
    # --- Step 3: Call the LLM and Process the Blueprint ---
    blueprint_str = _metis_llm_call(blueprint_prompt)
    if not blueprint_str:
        print("Metis Worker: ERROR - LLM call for blueprint returned nothing.")
        return None
        
    try:
        cleaned_str = blueprint_str.strip().removeprefix("```json").removesuffix("```").strip()
        blueprint = json.loads(cleaned_str)

        # --- Final Sanity Check ---
        # Ensure the proposed tool doesn't already exist on the toolbelt.
        toolbelt_name = blueprint.get("plugin_manifest", {}).get("toolbelt_name")
        if toolbelt_name and hasattr(app_state, toolbelt_name):
            print(f"Metis Worker: LLM proposed an existing tool ('{toolbelt_name}'). Skipping this cycle.")
            return None

        print("\n--- Metis Blueprint Generated ---")
        print(json.dumps(blueprint, indent=2))
        print("---------------------------------\n")

        return blueprint 

    except (json.JSONDecodeError, TypeError, KeyError) as e:
        print(f"Metis Worker: ERROR - LLM failed to generate a valid/complete JSON blueprint. Error: {e}")
        print(f"   Raw response was: {blueprint_str}")
        return None


def _metis_forge_and_test_sprite(blueprint: dict):
    """
    PHASE 2: The Workshop.
    Takes a blueprint and builds the tool in a sandboxed environment,
    including iterative, self-correcting code and test generation.
    Returns the sandbox path on success, None on failure.
    """
    tool_name = (
        blueprint["plugin_manifest"]["name"].lower().replace(" ", "_") + "_sprite"
    )
    sandbox_path = os.path.join("plugins", "_in_progress", tool_name)

    print(f"Metis Workshop: Creating sandbox at '{sandbox_path}'")
    os.makedirs(sandbox_path, exist_ok=True)

    venv_path = os.path.join(sandbox_path, "venv")
    print(f"Metis Workshop: Creating virtual environment in '{venv_path}'...")
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", venv_path],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Metis Workshop: FATAL - Failed to create venv: {e.stderr}")
        if os.path.exists(sandbox_path):
            shutil.rmtree(sandbox_path)
        return None

    pip_executable = (
        os.path.join(venv_path, "Scripts", "pip.exe")
        if sys.platform == "win32"
        else os.path.join(venv_path, "bin", "pip")
    )

    # Get the libraries the LLM thinks are required
    llm_suggested_libs = blueprint.get("required_libraries", [])

    # Define a set of common Python standard libraries that are built-in and NEVER installed via pip
    standard_libraries = {"os", "sys", "json", "datetime", "time", "re", "math", "subprocess", "pathlib", "shutil"}

    # Filter the LLM's suggestions to remove any standard libraries
    # This prevents pip from trying to install things like 'os' or 'json'
    filtered_libs = [lib for lib in llm_suggested_libs if lib.lower() not in standard_libraries]

    # Combine the filtered runtime libs with the required testing libs
    all_dependencies = filtered_libs + ["pytest", "pytest-mock"]

    # Only print/install if there are actual packages to install
    if all_dependencies:
        print(f"Metis Workshop: Installing all dependencies: {all_dependencies}")
        try:
            # The rest of the installation try...except block remains the same
            subprocess.run(
                [pip_executable, "install"] + all_dependencies,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Metis Workshop: FATAL - Failed to install dependencies: {e.stderr}")
            if os.path.exists(sandbox_path):
                shutil.rmtree(sandbox_path)
            return None
    else:
        print("Metis Workshop: No external dependencies to install.")

    try:
        # Install all dependencies in one go
        subprocess.run(
            [pip_executable, "install"] + all_dependencies,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Metis Workshop: FATAL - Failed to install dependencies: {e.stderr}")
        if os.path.exists(sandbox_path):
            shutil.rmtree(sandbox_path)
        return None

    module_name = blueprint["plugin_manifest"]["entry_point"].split(".")[0]
    code_path = os.path.join(sandbox_path, f"{module_name}.py")
    test_path = os.path.join(sandbox_path, f"test_{module_name}.py")
    manifest_path = os.path.join(sandbox_path, "plugin_manifest.json")

    last_test_error = ""
    for attempt in range(3):
        print(f"Metis Workshop: Code generation attempt {attempt + 1}...")

        # Create a unique exception name like "ApodSpriteError" from "apod_sprite"
        module_specific_error_name = "".join(
            word.capitalize() for word in module_name.split("_")
        ) + "Error"

        # --- Generate Code ---
        code_prompt = f"""
You are a master Python programmer writing a single, production-quality Python module.

**MODULE SPECIFICATION:**
- **Module Name:** `{module_name}.py`
- **Primary Function:** `{blueprint['proposed_function_name']}`
- **Purpose:** {blueprint['purpose']}
- **Required Libraries:** {filtered_libs}
- **Previous Test Errors (if any):**
{last_test_error or "  - None, this is the first attempt."}

**CRITICAL REQUIREMENTS - YOU MUST FOLLOW THESE RULES VERBATIM:**

1.  **EXCEPTION CLASSES:** You MUST include the following exception class definitions at the top of your file. This is not optional.
    ```python
    class InvalidInputError(ValueError): pass
    class ApiServiceError(Exception): pass
    class {module_specific_error_name}(Exception): pass
    ```

2.  **INPUT VALIDATION:** The first action in your function must be to validate the input arguments. If any are invalid, you MUST `raise InvalidInputError("Invalid input provided. Please check the function arguments.")`.

3.  **NETWORK HANDLING (if using 'requests'):**
    -   Wrap ALL `requests` calls in a `try...except requests.exceptions.RequestException`.
    -   On a network failure, you MUST `raise ApiServiceError("A network error occurred while contacting the external API.")`.
    -   After a successful call, you MUST check the `response.status_code`. If the code is not 200, you MUST `raise ApiServiceError(f"The API service returned an error: {{response.status_code}} {{response.reason}}")`.

4.  **DATA PARSING & LOGICAL ERRORS:**
    -   Wrap all JSON parsing and dictionary/list access (e.g., `data['key']`, `data[0]`) in a `try...except (KeyError, IndexError, TypeError, json.JSONDecodeError)`.
    -   On a parsing failure, you MUST `raise {module_specific_error_name}("The API returned data in an unexpected or invalid format.")`.
    -   **If the API call is successful (200 OK) but returns an empty list or a dictionary indicating 'not found', you MUST `raise {module_specific_error_name}("The requested item could not be found by the API.")`.**

5.  **SUCCESSFUL OUTPUT FORMAT:**
    -   On a completely successful run, the function MUST return a single, user-friendly, descriptive **STRING**.
    -   If the API returns complex data (like JSON), you MUST parse it and format the most important information into a human-readable sentence or two.
    -   **DO NOT return raw data structures like dictionaries or lists.**

**YOUR RESPONSE:**
Respond ONLY with the raw, complete Python code for the `{module_name}.py` file. Do not add any conversational text or markdown.
"""
        code_content = _metis_llm_call(code_prompt)
        if not code_content:
            print("Metis Workshop: WARN - Code generation failed (empty response).")
            last_test_error = "LLM response for code generation was empty."
            time.sleep(5) 
            continue 

        # ADDED: Defensively clean up markdown fences that the LLM might add.
        if "```" in code_content:
            code_content = code_content.strip().removeprefix("```python").removesuffix("```").strip()

        with open(code_path, 'w', encoding='utf-8') as f:
            f.write(code_content)

        # --- Generate Tests, synchronized with the generated code ---
        exceptions_to_import = f"InvalidInputError, ApiServiceError, {module_specific_error_name}"

        # Use the same filtered_libs list we passed to the code prompt
        required_libs_str = ", ".join(filtered_libs) if filtered_libs else "standard libraries only"
        
        test_prompt = f"""
You are a Python testing expert using pytest and pytest-mock.
Your task is to write a complete and robust test file for the following Python code.

**CODE TO TEST:**
```python
{code_content}
```
TESTING REQUIREMENTS:
Analyze the Code: Carefully read the provided code in the block above. Identify the function(s) to test, their arguments, the custom exception classes, and the exact format of their success and error return values.
Generate Pytest File: Write a complete Python file named test_{module_name}.py.
Imports: Your test file MUST begin with the necessary imports, including pytest, unittest.mock (with patch, Mock, ANY), requests (if used), and the functions/exceptions from the module itself (e.g., from {module_name} import ...).
Comprehensive Coverage: Your tests MUST cover the following scenarios based on your analysis of the code:
A success case where the function works as expected.
Cases for each type of invalid input that should raise InvalidInputError.
A case where a network request fails (mock a requests.exceptions.RequestException).
A case where the external API returns an HTTP error code (e.g., 500).
A case where the external API returns a "not found" response (e.g., 404).
A case where the API response is malformed or missing expected keys.
Accurate Assertions:
When testing for exceptions, you MUST assert against the exact exception type and the exact error message string used in the provided code.
For success cases, assert the return type is correct (e.g., isinstance(result, str)).
When mocking API calls (like requests.get), use ANY for keyword arguments like timeout to ensure tests are not brittle.
YOUR RESPONSE:
Respond ONLY with the raw, complete Python code for the test_{module_name}.py test file. Do not add any conversational text or markdown.
"""
        
        test_content = _metis_llm_call(test_prompt)
        if not test_content:
            print(
                "Metis Workshop: WARN - Test generation failed for this attempt (empty response)."
            )
            last_test_error = "LLM response for test generation was empty."
            time.sleep(5)
            continue

        # Defensively clean up markdown fences that the LLM might add
        if "```" in test_content:
            test_content = test_content.strip().removeprefix("```python").removesuffix("```").strip()

        # First, write and close the test file.
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(test_content)

        # Now, as a separate step, run the tests.
        print("Metis Workshop: Running tests in isolated environment...")
        pytest_executable = (
            os.path.join(venv_path, "Scripts", "pytest.exe")
            if sys.platform == "win32"
            else os.path.join(venv_path, "bin", "pytest")
        )

        try:
            result = subprocess.run(
                [pytest_executable],
                cwd=sandbox_path,
                check=True,
                capture_output=True,
                text=True,
            )
            print("Metis Workshop: ✓ All tests passed!")
            print(result.stdout)

            print("Metis Workshop: Generating tool definition for Gemini...")
            definition_prompt = f"""
You are a Python API documentation writer. Based on the following Python code, create a JSON tool definition for the Google Gemini API.

CODE:
```python
{code_content}

The JSON object MUST follow this structure:
{{
"name": "function_name_as_string",
"description": "A clear, one-sentence description of what the function does.",
"parameters": {{
"type": "OBJECT",
"properties": {{
"argument_name": {{
"type": "STRING_or_INTEGER_or_NUMBER",
"description": "Description of the argument."
}}
}},
"required": ["list_of_required_argument_names"]
}}
}}
CRITICAL: The 'type' values in the schema MUST be uppercase (e.g., "OBJECT", "STRING").
Respond ONLY with the raw, valid JSON object.
"""
            
            tool_definition_json_str = _metis_llm_call(definition_prompt)
            if tool_definition_json_str:
                tool_def_path = os.path.join(sandbox_path, "tool_definition.json")
                with open(tool_def_path, 'w', encoding='utf-8') as f:
                    # Clean and save the JSON
                    cleaned_def = tool_definition_json_str.strip().removeprefix("```json").removesuffix("```").strip()
                    f.write(cleaned_def)
                print(f"Metis Workshop: Saved tool definition to {tool_def_path}")
            else:
                print("Metis Workshop: WARN - Failed to generate tool definition JSON.")

            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(blueprint["plugin_manifest"], f, indent=2)

            return sandbox_path # This is the success case, exit function.            

            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(blueprint["plugin_manifest"], f, indent=2)

            return sandbox_path # This is the success case, exit function.

        except subprocess.CalledProcessError as e:
            # This is the "retry" path.
            last_test_error = f"STDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
            print("Metis Workshop: ✗ Tests failed. Analyzing errors and retrying...")
            print(last_test_error)
            time.sleep(5)
            # The 'for' loop will now continue to the next attempt automatically.

        except Exception as e:
            # This is the "fatal error" path for unexpected issues.
            print(f"Metis Workshop: UNEXPECTED ERROR during testing: {e}")
            last_test_error = (
                f"UNEXPECTED ERROR: {type(e).__name__}: {e}. Review traceback."
            )
            traceback.print_exc()
            time.sleep(5)
            break  # Break out of the for loop on a fatal, non-test-failure error.

    print("Metis Workshop: FATAL - Failed to generate working code after multiple attempts.")
    if os.path.exists(sandbox_path):
        print(f"Metis Workshop: Cleaning up failed sandbox at {sandbox_path}")
        # Add a retry loop for cleanup to handle Windows file lock issues
        for i in range(3):
            try:
                shutil.rmtree(sandbox_path)
                print("Metis Workshop: Cleanup successful.")
                break # Exit loop on success
            except PermissionError as e:
                print(f"Metis Workshop: Cleanup failed (Attempt {i+1}/3), PermissionError. Retrying in 1 second...")
                time.sleep(1)
            except Exception as e:
                print(f"Metis Workshop: Cleanup failed with unexpected error: {e}")
                break # Don't retry on other errors
    
    return None

def metis_worker(app_state):
    """
    The main worker thread for discovering and crafting new tools.
    Can be triggered by its internal schedule or on-demand via a flag.
    """
    print("Metis Worker: Waking up. The mind is a workshop, not a hospital.")
    
    # Initialize app_state flags if they don't exist
    if not hasattr(app_state, 'metis_on_demand_trigger'):
        app_state.metis_on_demand_trigger = False
    if not hasattr(app_state, 'metis_specific_request'):
        app_state.metis_specific_request = None

    last_run_timestamp = _load_last_metis_run_state()
    if last_run_timestamp:
        print(f"Metis Worker: Loaded last run state: {last_run_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        last_run_timestamp = datetime.now() - timedelta(days=METIS_RUN_INTERVAL_DAYS + 1)
        print("Metis Worker: No previous run state found. Initializing to allow first run.")

    while app_state.running:
        run_now = False
        run_reason = ""

        # --- CONDITION 1: Check for On-Demand Trigger ---
        if app_state.metis_on_demand_trigger:
            run_now = True
            run_reason = f"On-Demand Request ({app_state.metis_specific_request or 'General Urge'})"
            # CRITICAL: Reset the flag immediately after detecting it
            app_state.metis_on_demand_trigger = False
        
        # --- CONDITION 2: Check for Scheduled Trigger (only if not triggered on-demand) ---
        else:
            current_time = datetime.now()
            time_since_last_run = current_time - last_run_timestamp
            interval_has_passed = time_since_last_run >= timedelta(days=METIS_RUN_INTERVAL_DAYS)
            is_after_target_time = current_time.hour >= METIS_TARGET_HOUR and current_time.minute >= METIS_TARGET_MINUTE
            has_run_today = last_run_timestamp.date() == current_time.date()

            if interval_has_passed and is_after_target_time and not has_run_today:
                run_now = True
                run_reason = "Scheduled Run"

        # --- EXECUTE THE FORGING CYCLE IF A TRIGGER WAS MET ---
        if run_now:
            print(f"Metis Worker: Run triggered at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. Reason: {run_reason}.")
            
            if not METIS_MODEL:
                print("Metis Worker: ERROR - Gemini model not initialized. Skipping run.")
            elif app_state.awaiting_human_governance_approval:
                print("Metis Worker: Skipping run; a tool is currently awaiting human approval.")
            else:
                try:
                    blueprint = _metis_identify_capability_gap(app_state)
                    if blueprint:
                        final_sandbox_path = _metis_forge_and_test_sprite(blueprint)
                        if final_sandbox_path:
                            print(f"Metis Worker: Tool '{blueprint['plugin_manifest']['name']}' is complete and tested.")
                            integration_request_event = {
                                "type": "integration_request",
                                "payload": {
                                    "tool_name": blueprint['plugin_manifest']['name'],
                                    "description": blueprint['purpose'],
                                    "sandbox_path": final_sandbox_path
                                }
                            }
                            app_state.event_queue.put(integration_request_event)
                            print("Metis Worker: Integration request placed on the event queue.")
                        else:
                            print(f"Metis Worker: Failed to forge and test sprite for blueprint: {blueprint.get('proposed_function_name', 'Unknown')}.")
                    else:
                        print("Metis Worker: No capability gap identified or blueprint generation failed.")
                except Exception as e:
                    print(f"!!! METIS WORKER HICCUP (Error during run cycle): {e}")
                    traceback.print_exc()

            # CRITICAL: If this was a scheduled run, update the timestamp to reset the schedule.
            # We don't update it for on-demand runs, as they shouldn't affect the schedule.
            if run_reason == "Scheduled Run":
                current_time = datetime.now()
                _save_last_metis_run_state(current_time)
                last_run_timestamp = current_time
                print("Metis Worker: Scheduled run complete. Last run timestamp updated.")
            
            # Clear the specific request after the cycle is done
            app_state.metis_specific_request = None
        
        # The worker always sleeps between checks.
        time.sleep(METIS_CHECK_INTERVAL_SECONDS)

    print("Metis Worker: Shutting down.")