# light_service.py (v3 - Simplified, No Manual Override)
# Manages both the expressive Desk Lamp and the passive Ambient Bulb.

import re
import time
import threading
import traceback
from datetime import datetime
import pytz
from lifxlan import LifxLAN, Light, Device
import random

# --- Constants and Configuration ---
DESK_LAMP_LABEL = "Silvie Lamp"
AMBIENT_BULB_LABEL = "Silvie Aura"
BELFAST_TZ = 'America/New_York'
ALLOWED_START_HOUR = 8
ALLOWED_END_HOUR = 22

# --- Global Bulb Objects ---
desk_lamp = None
ambient_bulb = None
app_state = None

# --- Helper Functions for Effects (Unchanged) ---
def _perform_pulse(bulb, from_color_hsbk, to_color_hsbk, period_s, cycles):
    # This function's code is unchanged
    print(f"Executing custom PULSE effect for {cycles} cycles.")
    fade_duration_ms = int((period_s / 2) * 1000)
    for i in range(int(cycles)):
        if not app_state.running: break
        bulb.set_color(to_color_hsbk, duration=fade_duration_ms)
        time.sleep(period_s / 2)
        bulb.set_color(from_color_hsbk, duration=fade_duration_ms)
        time.sleep(period_s / 2)
    print("Custom PULSE effect finished.")

def _perform_breathe(bulb, color_hsbk, period_s, cycles):
    # This function's code is unchanged
    print(f"Executing custom BREATHE effect for {cycles} cycles.")
    fade_duration_ms = int((period_s / 2) * 1000)
    off_color_hsbk = [color_hsbk[0], color_hsbk[1], 0, color_hsbk[3]]
    for i in range(int(cycles)):
        if not app_state.running: break
        bulb.set_color(off_color_hsbk, duration=fade_duration_ms)
        time.sleep(period_s / 2)
        bulb.set_color(color_hsbk, duration=fade_duration_ms)
        time.sleep(period_s / 2)
    print("Custom BREATHE effect finished.")

def _perform_flicker(bulb, base_color_hsbk, duration_s):
    # This function's code is unchanged
    print(f"Executing custom FLICKER effect for {duration_s} seconds.")
    start_time = time.time()
    base_h, base_s, _, base_k = base_color_hsbk
    bulb.set_color([base_h, base_s, int(65535 * 0.6), base_k], duration=200)
    time.sleep(0.2)
    while time.time() - start_time < duration_s:
        if not app_state.running: break
        random_brightness = random.uniform(0.35, 0.75)
        random_duration_ms = random.randint(100, 400)
        random_sleep_s = random.uniform(0.05, 0.2)
        bulb.set_color([base_h, base_s, int(65535 * random_brightness), base_k], duration=random_duration_ms)
        time.sleep(random_sleep_s)
    bulb.set_color(base_color_hsbk, duration=1000)
    print("Custom FLICKER effect finished.")

# --- Main Service Functions ---
def initialize_lights(main_app_state):
    """Finds BOTH target bulbs on the network and initializes the service."""
    global desk_lamp, ambient_bulb, app_state
    app_state = main_app_state
    print("Light Service: Discovering bulbs…")
    
    try:
        lifx = LifxLAN(2)
        devices = lifx.get_devices()
        
        for dev in devices:
            label = dev.get_label()
            if label == DESK_LAMP_LABEL:
                desk_lamp = Light(dev.mac_addr, dev.ip_addr)
                print(f"✓ Desk Lamp ('{DESK_LAMP_LABEL}') found.")
            elif label == AMBIENT_BULB_LABEL:
                ambient_bulb = Light(dev.mac_addr, dev.ip_addr)
                print(f"✓ Ambient Bulb ('{AMBIENT_BULB_LABEL}') found.")
        
        if not desk_lamp: print(f"✗ Warning: Desk Lamp ('{DESK_LAMP_LABEL}') not found.")
        if not ambient_bulb: print(f"✗ Warning: Ambient Bulb ('{AMBIENT_BULB_LABEL}') not found.")

        # Attach the single, simplified command handler to the app_state.
        app_state.set_desk_lamp = handle_desk_lamp_command

    except Exception as e:
        print(f"!!! CRITICAL ERROR during light initialization: {e}")
        traceback.print_exc()

def handle_desk_lamp_command(command_str):
    """
    Parses a command string and controls the DESK LAMP.
    This action NO LONGER affects the ambient bulb.
    """
    if not desk_lamp:
        print("Warning: Desk lamp not found. Skipping light command.")
        return
    if not app_state:
        print("CRITICAL ERROR: app_state not initialized in light_service.")
        return

    # <<< --- DELETED --- >>>
    # The manual override logic has been completely removed from this function.

    now = datetime.now(pytz.timezone(BELFAST_TZ))
    if not (ALLOWED_START_HOUR <= now.hour < ALLOWED_END_HOUR):
        print(f"Desk lamp command '{command_str}' ignored due to quiet hours.")
        return

    print(f"DEBUG Desk Lamp: Received command string: '{command_str}'")
    
    try:
        # The rest of the parsing and control logic remains the same
        params = dict(re.findall(r'(\w+)=([\d\._-]+)', command_str))

        if "effect" in params:
            effect_name = params.get("effect", "").lower()
            if desk_lamp.get_power() == 0:
                desk_lamp.set_power("on")
                time.sleep(0.1)

            if effect_name == "pulse":
                from_h, from_s, from_v = int(params.get("from_h", -1)), int(params.get("from_s", -1)), int(params.get("from_v", -1))
                if from_h != -1 and from_s != -1 and from_v != -1: from_color = [int((from_h/360)*65535), int((from_s/100)*65535), int((from_v/100)*65535), 3500]
                else: from_color = desk_lamp.get_color()
                to_h, to_s, to_v = int(params.get("to_h", 0)), int(params.get("to_s", 0)), int(params.get("to_v", 0))
                to_color = [int((to_h/360)*65535), int((to_s/100)*65535), int((to_v/100)*65535), 3500]
                period_s, cycles = float(params.get("period", 2.0)), max(1, float(params.get("cycles", 3)))
                threading.Thread(target=_perform_pulse, args=(desk_lamp, from_color, to_color, period_s, cycles)).start()

        else: # Simple color set for the desk lamp
            h, s, v, duration = int(float(params.get('h', 0))), int(float(params.get('s', 0))), int(float(params.get('v', 100))), int(float(params.get('duration', 2000)))
            h_lifx, s_lifx, v_lifx = int((h / 360) * 65535), int((s / 100) * 65535), int((v / 100) * 65535)
            
            if desk_lamp.get_power() == 0 and v > 0: desk_lamp.set_power("on")
            desk_lamp.set_color([h_lifx, s_lifx, v_lifx, 3500], duration=duration)

    except Exception as e:
        print(f"!!! CRITICAL ERROR handling desk lamp command '{command_str}': {e}")
        traceback.print_exc()

# --- Helper functions for the Ambient Bulb Worker (Unchanged) ---
def _hsv_for_time(now):
    t = now.hour + now.minute / 60
    if 6 <= t < 10:   return (35, 100, 80)
    if 10 <= t < 16:  return (42, 20, 100)
    if 16 <= t < 20:  return (25, 100, 90)
    return (260, 80, 20)

def _mood_tweak(hsv, weather_str, mood_hint_str):
    h, s, v = hsv
    full_context = (str(weather_str) + str(mood_hint_str)).lower()

    # Apply the tweaks as before
    if "energetic" in full_context: v = v + 20
    if "quiet" in full_context or "calm" in full_context: v = v - 30
    if "rain" in full_context or "fog" in full_context:
        h = 200
        s = 40
    if "clear" in full_context: s = s + 15

    # --- THIS IS THE FIX ---
    # After all modifications, clamp all values to their legal ranges before returning.
    final_h = h % 360  # Use modulo for hue to wrap it around correctly
    final_s = max(0, min(100, s)) # Clamp saturation between 0 and 100
    final_v = max(10, min(100, v)) # Clamp brightness between 10 (min brightness) and 100

    return (final_h, final_s, final_v)

# --- The Ambient Bulb Worker Thread ---
def ambient_bulb_worker(shared_app_state):
    """Gently adjusts the AMBIENT BULB's color over time, completely independently."""
    global ambient_bulb, app_state
    app_state = shared_app_state

    print("Ambient Light Worker: Thread started.")
    time.sleep(45)

    while app_state.running:
        try:
            if not ambient_bulb:
                print("Ambient Light Worker: Ambient bulb not found. Re-scanning in 5 minutes...")
                time.sleep(300)
                continue
            
            # <<< --- DELETED --- >>>
            # The check for manual_override has been completely removed.
            # This worker will now always run.

            now = datetime.now(pytz.timezone(BELFAST_TZ))
            desired_power_state = 65535 if (ALLOWED_START_HOUR <= now.hour < ALLOWED_END_HOUR) else 0

            try:
                current_power = ambient_bulb.get_power()
            except Exception as e:
                print(f"Ambient Light Worker: Could not get bulb power. Error: {e}")
                time.sleep(60)
                continue
            
            if current_power != desired_power_state:
                ambient_bulb.set_power(desired_power_state, duration=5000)
                time.sleep(5)

            if desired_power_state > 0:
                weather_str = getattr(app_state, 'current_weather_info', {}).get('condition', '')
                mood_hint_str = getattr(app_state, 'current_mood_hint', '') or ''
                
                base_hsv = _hsv_for_time(now)
                tweaked_hsv = _mood_tweak(base_hsv, weather_str, mood_hint_str)
                h, s, v = tweaked_hsv
                h_lifx, s_lifx, v_lifx = int((h / 360) * 65535), int((s / 100) * 65535), int((v / 100) * 65535)

                print(f"Ambient Light Worker: Setting ambient color H={h},S={s},V={v} over 60s.")
                ambient_bulb.set_color([h_lifx, s_lifx, v_lifx, 3500], duration=60000)
            
            time.sleep(3600)

        except Exception as e:
            print(f"ERROR in ambient_bulb_worker loop: {e}")
            traceback.print_exc()
            time.sleep(300)
            
    print("Ambient Light Worker: Thread stopped.")