# pacing_worker.py

import time
import random
import traceback
from datetime import datetime

# --- Pacing Configuration ---
# A central dictionary to define the timing parameters.
# This makes it very easy to tune Silvie's "personality".
PACING_CONFIG = {
    # Base interval in seconds for each level
    "quiet":  {"base": 7200, "jitter": 1800}, # Base: 2 hours, Jitter: +/- 30 mins
    "normal": {"base": 3600, "jitter": 900},  # Base: 1 hour,  Jitter: +/- 15 mins
    "chatty": {"base": 1800, "jitter": 600},  # Base: 30 mins, Jitter: +/- 10 mins
}

# How user activity affects the interval. Thresholds are in seconds.
USER_ACTIVITY_MODIFIERS = {
    "recent_interaction_threshold": 600,  # 10 minutes
    "recent_interaction_multiplier": 0.5, # Halve the interval if user is active
    "long_inactivity_threshold": 5400,    # 1.5 hours
    "long_inactivity_multiplier": 1.75,   # Nearly double the interval if user is inactive
}

# How Silvie's own "energy" (circadian rhythm) affects the interval.
CIRCADIAN_MODIFIERS = {
    "morning": 0.85, # 15% more likely to be proactive in the morning
    "afternoon": 1.0,  # Baseline
    "evening": 1.25, # 25% less likely in the evening
    "night": 2.5,    # Much less likely at night
}

def pacing_worker(app_state):
    """
    The heart of Silvie's proactive pacing.
    This worker dynamically calculates when Silvie should next consider a
    proactive action based on her configured level, user activity, and her
    own circadian state.
    """
    print("Pacing Engine Worker: Starting. My purpose is to decide *when* Silvie acts.")
    
    # Give other workers a moment to initialize the app_state
    time.sleep(20)

    is_first_run_of_session = True

    while getattr(app_state, "running", True):
        try:
            # --- 1. Get Current State from the AppState "Bulletin Board" ---
            current_level = getattr(app_state, 'pacing_level', 'normal')
            last_interaction = getattr(app_state, 'last_user_interaction_time', time.time())
            circadian_state = getattr(app_state, 'circadian_state', 'afternoon')

            config = PACING_CONFIG.get(current_level, PACING_CONFIG["normal"])
            base_interval = config["base"]

            # --- 2. Calculate Interval Adjustments ---
            
            # Adjust for User Activity
            time_since_last_interaction = time.time() - last_interaction
            if time_since_last_interaction < USER_ACTIVITY_MODIFIERS["recent_interaction_threshold"]:
                activity_modifier = USER_ACTIVITY_MODIFIERS["recent_interaction_multiplier"]
                print(f"Pacing Engine: User is active. Applying modifier: {activity_modifier}x")
            elif time_since_last_interaction > USER_ACTIVITY_MODIFIERS["long_inactivity_threshold"]:
                activity_modifier = USER_ACTIVITY_MODIFIERS["long_inactivity_multiplier"]
                print(f"Pacing Engine: User is inactive. Applying modifier: {activity_modifier}x")
            else:
                activity_modifier = 1.0 # Normal activity level

            # Adjust for Silvie's Circadian Rhythm
            circadian_modifier = CIRCADIAN_MODIFIERS.get(circadian_state, 1.0)
            if circadian_modifier != 1.0:
                 print(f"Pacing Engine: Circadian state is '{circadian_state}'. Applying modifier: {circadian_modifier}x")

            # --- 3. Calculate Final Interval with Jitter ---
            modified_interval = base_interval * activity_modifier * circadian_modifier
            
            # Special logic for the very first run of the session
            if is_first_run_of_session:
                # Set a much shorter, predictable first interval
                final_interval = random.uniform(600, 900) # 10-15 minutes for the first run
                print("Pacing Engine: First run of session. Overriding interval for initial greeting.")
                is_first_run_of_session = False # Flip the flag so this only runs once
            else:
                # Normal calculation with jitter for all subsequent runs
                jitter = random.uniform(-config["jitter"], config["jitter"])
                final_interval = max(300, modified_interval + jitter) # Ensure at least a 5-minute interval

            print(f"Pacing Engine: Calculated next proactive interval: {final_interval / 60:.2f} minutes.")

            # --- 4. Set the "Go Time" on the AppState for the proactive_worker ---
            app_state.proactive_go_time = time.time() + final_interval
            ts = datetime.fromtimestamp(app_state.proactive_go_time).strftime("%H:%M:%S")
            print(f"Pacing Engine: Next proactive window is at {ts}")

            # --- 5. Sleep until the next calculation cycle ---
            # This worker's job is to set the time, then wait for the *next* cycle.
            # It will sleep for the interval it just set, plus a little extra, ensuring
            # the proactive_worker has plenty of time to act before this worker runs again.
            snooze_duration = final_interval + random.randint(30, 120)

            sleep_end_time = time.time() + snooze_duration
            while time.time() < sleep_end_time:
                if not getattr(app_state, 'running', True):
                    break
                time.sleep(15) # Check every 15 seconds for shutdown signal

        except Exception as e:
            print(f"!!! Pacing Engine Worker Error: {type(e).__name__} - {e}")
            traceback.print_exc()
            time.sleep(60) # Wait a minute before retrying on error
            
    print("Pacing Engine Worker: Thread stopped.")