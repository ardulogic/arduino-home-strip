#!/usr/bin/env python3
"""
PC-side monitor for Arduino LED strip control.
Monitors mouse and keyboard activity and sends commands via serial.
Runs as a system tray application.
"""

import serial
import serial.tools.list_ports
import time
from pynput import mouse, keyboard
from threading import Lock, Thread
import sys
import os
import pystray
from PIL import Image
import sounddevice as sd
import numpy as np

# Try to import from config file, otherwise use defaults
try:
    from config import SERIAL_PORT, BAUD_RATE, RED_R, RED_G, RED_B
except ImportError:
    # Default configuration
    SERIAL_PORT = 'COM3'  # Change this to your Arduino's COM port
    BAUD_RATE = 115200
    RED_R = 255  # Configurable red color RGB values
    RED_G = 0
    RED_B = 0

# Global state
last_mouse_pos = None
mouse_moved = False
serial_lock = Lock()
arduino = None
last_mouse_command_time = 0
MOUSE_THROTTLE_MS = 50  # Throttle mouse commands to avoid flooding

# Feature toggles
react_to_keyboard = True
react_to_mouse = True
stay_on = True
react_to_audio = True

# Listeners
mouse_listener = None
keyboard_listener = None
tray_icon = None

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def send_command(cmd):
    """Send a command to Arduino via serial."""
    global arduino
    if arduino and arduino.is_open:
        try:
            with serial_lock:
                arduino.write((cmd + '\n').encode())
        except Exception as e:
            pass  # Silently fail in tray mode

def on_mouse_move(x, y):
    """Handle mouse movement."""
    global last_mouse_pos, mouse_moved, last_mouse_command_time, react_to_mouse
    
    if not react_to_mouse:
        return
    
    if last_mouse_pos is None:
        last_mouse_pos = (x, y)
        return
    
    # Only send if mouse actually moved (not just tiny jitter)
    # and throttle to avoid flooding the serial port
    current_time = time.time() * 1000
    if (abs(x - last_mouse_pos[0]) > 2 or abs(y - last_mouse_pos[1]) > 2) and \
       (current_time - last_mouse_command_time > MOUSE_THROTTLE_MS):
        mouse_moved = True
        send_command('M')
        last_mouse_pos = (x, y)
        last_mouse_command_time = current_time

def on_key_press(key):
    """Handle key press."""
    global mouse_moved, react_to_keyboard
    
    if not react_to_keyboard:
        return
    
    # Reset mouse moved flag when typing
    mouse_moved = False
    
    try:
        # Handle special keys
        if key == keyboard.Key.backspace:
            send_command('B')
        elif key == keyboard.Key.space:
            send_command('S')
        else:
            # Regular key press
            send_command('K')
    except AttributeError:
        # Regular character key
        send_command('K')

def find_ch340_port():
    """Auto-detect CH340 Arduino COM port."""
    ports = serial.tools.list_ports.comports()
    
    # First, try to find by description containing "CH340"
    for port in ports:
        if 'CH340' in port.description.upper() or 'USB-SERIAL' in port.description.upper():
            return port.device
    
    # If not found by description, try to find by VID/PID (CH340 common IDs)
    # CH340 VID: 0x1A86, PID: 0x7523
    for port in ports:
        if hasattr(port, 'vid') and hasattr(port, 'pid'):
            if port.vid == 0x1A86:  # CH340 vendor ID
                return port.device
    
    # If still not found, try the first available port
    if ports:
        return ports[0].device
    
    return None

def setup_arduino():
    """Connect to Arduino."""
    global arduino, RED_R, RED_G, RED_B
    
    # Override with command line arguments if provided
    if len(sys.argv) == 4:
        try:
            RED_R = int(sys.argv[1])
            RED_G = int(sys.argv[2])
            RED_B = int(sys.argv[3])
        except ValueError:
            pass
    
    # Auto-detect CH340 port if not specified or if specified port doesn't work
    port_to_use = SERIAL_PORT
    
    # If SERIAL_PORT is None or empty, or if we want to auto-detect, find CH340
    if not SERIAL_PORT or SERIAL_PORT == 'AUTO' or SERIAL_PORT.upper() == 'AUTO':
        detected_port = find_ch340_port()
        if detected_port:
            port_to_use = detected_port
        else:
            return False
    
    # Try to connect to Arduino
    try:
        arduino = serial.Serial(port_to_use, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for Arduino to initialize
        
        # Send initial color configuration
        send_command(f'C,{RED_R},{RED_G},{RED_B}')
        return True
    except Exception:
        # If connection failed and we used a specific port, try auto-detection
        if port_to_use == SERIAL_PORT and SERIAL_PORT != 'AUTO':
            detected_port = find_ch340_port()
            if detected_port and detected_port != SERIAL_PORT:
                try:
                    port_to_use = detected_port
                    arduino = serial.Serial(port_to_use, BAUD_RATE, timeout=1)
                    time.sleep(2)
                    send_command(f'C,{RED_R},{RED_G},{RED_B}')
                    return True
                except Exception:
                    return False
        return False

def toggle_keyboard(icon, item):
    """Toggle keyboard reaction."""
    global react_to_keyboard, keyboard_listener, tray_icon
    react_to_keyboard = not react_to_keyboard
    if tray_icon:
        tray_icon.menu = create_menu()

def toggle_mouse(icon, item):
    """Toggle mouse reaction."""
    global react_to_mouse, tray_icon
    react_to_mouse = not react_to_mouse
    if tray_icon:
        tray_icon.menu = create_menu()

def toggle_stay_on(icon, item):
    """Toggle stay on mode."""
    global stay_on, tray_icon
    stay_on = not stay_on
    if tray_icon:
        tray_icon.menu = create_menu()

def toggle_audio(icon, item):
    """Toggle audio reaction."""
    global react_to_audio, tray_icon
    react_to_audio = not react_to_audio
    if tray_icon:
        tray_icon.menu = create_menu()
    # Clear audio visualization when disabled
    if not react_to_audio and arduino and arduino.is_open:
        send_command('A,0')

def exit_app(icon, item):
    """Exit the application."""
    global mouse_listener, keyboard_listener, arduino, tray_icon
    if mouse_listener:
        mouse_listener.stop()
    if keyboard_listener:
        keyboard_listener.stop()
    if arduino:
        arduino.close()
    icon.stop()
    sys.exit(0)

def create_menu():
    """Create the tray menu with current states."""
    global react_to_keyboard, react_to_mouse, stay_on, react_to_audio
    return pystray.Menu(
        pystray.MenuItem(
            lambda text: f"React to Keyboard: {'✓' if react_to_keyboard else '✗'}",
            toggle_keyboard
        ),
        pystray.MenuItem(
            lambda text: f"React to Mouse: {'✓' if react_to_mouse else '✗'}",
            toggle_mouse
        ),
        pystray.MenuItem(
            lambda text: f"React to Audio: {'✓' if react_to_audio else '✗'}",
            toggle_audio
        ),
        pystray.MenuItem(
            lambda text: f"Stay On: {'✓' if stay_on else '✗'}",
            toggle_stay_on
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit", exit_app)
    )

def setup_tray():
    """Set up the system tray icon."""
    global tray_icon
    
    # Load icon
    try:
        icon_path = get_resource_path("icon.png")
        image = Image.open(icon_path)
    except Exception:
        # Fallback to a simple icon if file not found
        image = Image.new('RGB', (64, 64), color='red')
    
    # Create menu
    menu = create_menu()
    
    tray_icon = pystray.Icon("HomeStrip", image, "HomeStrip Monitor", menu)
    return tray_icon

def start_listeners():
    """Start mouse and keyboard listeners."""
    global mouse_listener, keyboard_listener
    mouse_listener = mouse.Listener(on_move=on_mouse_move)
    keyboard_listener = keyboard.Listener(on_press=on_key_press)
    mouse_listener.start()
    keyboard_listener.start()

def keep_alive_thread():
    """Thread to send keep-alive commands when Stay On is enabled."""
    global stay_on
    while True:
        time.sleep(4)  # Send every 4 seconds (before 5 second timeout)
        if stay_on and arduino and arduino.is_open:
            send_command('M')  # Send mouse command to reset idle timer

def audio_callback(indata, frames, time_info, status):
    """Callback function for audio stream."""
    global react_to_audio
    if not react_to_audio or not arduino or not arduino.is_open:
        return
    
    # Calculate RMS (Root Mean Square) for audio level
    rms = np.sqrt(np.mean(indata**2))
    
    # Convert to level (0-20, Arduino will clamp to its configured range)
    # Use logarithmic scaling for better visualization
    # RMS values are typically 0.0 to 1.0, so scale appropriately
    # Adjust multiplier (2000) for sensitivity - higher = more sensitive
    # Arduino uses AUDIO_START_LED and AUDIO_END_LED constants to determine range
    level = int(min(20, max(0, rms * 2000)))  # Max 20, Arduino will clamp to its range
    
    # Always send level (even 0) to keep visualization updated
    send_command(f'A,{level}')

def audio_capture_thread():
    """Thread to capture audio and send levels to Arduino.
    
    Note: On Windows, to capture system audio (what you hear), you may need to:
    - Enable "Stereo Mix" in Windows Sound settings (Recording devices)
    - Or use a virtual audio cable
    - Or set the default input device to a loopback device
    """
    global react_to_audio
    try:
        # Try to use default input device (may need to be set to loopback/sterio mix on Windows)
        # Open audio stream (stereo input, 44100 Hz sample rate, small blocksize for low latency)
        with sd.InputStream(callback=audio_callback, channels=2, samplerate=44100, blocksize=512, dtype='float32'):
            while True:
                time.sleep(0.1)  # Small sleep to prevent CPU spinning
    except Exception as e:
        # Silently handle audio errors (device not available, etc.)
        # Audio visualization will simply not work if capture fails
        pass

def main():
    """Main function to set up monitoring."""
    global arduino
    
    # Connect to Arduino
    if not setup_arduino():
        # Still show tray icon even if Arduino connection fails
        # User can try to reconnect later
        pass
    
    # Start listeners
    start_listeners()
    
    # Start keep-alive thread
    keep_alive = Thread(target=keep_alive_thread, daemon=True)
    keep_alive.start()
    
    # Start audio capture thread
    audio_thread = Thread(target=audio_capture_thread, daemon=True)
    audio_thread.start()
    
    # Set up and run tray icon
    icon = setup_tray()
    icon.run()

if __name__ == '__main__':
    main()
