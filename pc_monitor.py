#!/usr/bin/env python3
"""
PC-side monitor for Arduino LED strip control.
Monitors mouse and keyboard activity and sends commands via serial.
"""

import serial
import serial.tools.list_ports
import time
from pynput import mouse, keyboard
from threading import Lock
import sys

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

# State
last_mouse_pos = None
mouse_moved = False
serial_lock = Lock()
arduino = None
last_mouse_command_time = 0
MOUSE_THROTTLE_MS = 50  # Throttle mouse commands to avoid flooding

def send_command(cmd):
    """Send a command to Arduino via serial."""
    global arduino
    if arduino and arduino.is_open:
        try:
            with serial_lock:
                arduino.write((cmd + '\n').encode())
        except Exception as e:
            print(f"Error sending command: {e}")

def on_mouse_move(x, y):
    """Handle mouse movement."""
    global last_mouse_pos, mouse_moved, last_mouse_command_time
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
    global mouse_moved
    
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
            print(f"Found CH340 device: {port.device} - {port.description}")
            return port.device
    
    # If not found by description, try to find by VID/PID (CH340 common IDs)
    # CH340 VID: 0x1A86, PID: 0x7523
    for port in ports:
        if hasattr(port, 'vid') and hasattr(port, 'pid'):
            if port.vid == 0x1A86:  # CH340 vendor ID
                print(f"Found CH340 device by VID/PID: {port.device} - {port.description}")
                return port.device
    
    # If still not found, list all available ports and let user choose
    if ports:
        print("\nCH340 device not automatically detected. Available COM ports:")
        for i, port in enumerate(ports, 1):
            print(f"  {i}. {port.device} - {port.description}")
        
        # Try the first available port (common case)
        print(f"\nTrying first available port: {ports[0].device}")
        return ports[0].device
    
    return None

def main():
    """Main function to set up monitoring."""
    global arduino, RED_R, RED_G, RED_B
    
    # Override with command line arguments if provided
    if len(sys.argv) == 4:
        try:
            RED_R = int(sys.argv[1])
            RED_G = int(sys.argv[2])
            RED_B = int(sys.argv[3])
            print(f"Using command line color: RGB({RED_R}, {RED_G}, {RED_B})")
        except ValueError:
            print("Invalid RGB values. Using config/default values.")
    
    # Auto-detect CH340 port if not specified or if specified port doesn't work
    port_to_use = SERIAL_PORT
    
    # If SERIAL_PORT is None or empty, or if we want to auto-detect, find CH340
    if not SERIAL_PORT or SERIAL_PORT == 'AUTO' or SERIAL_PORT.upper() == 'AUTO':
        print("Auto-detecting CH340 Arduino...")
        detected_port = find_ch340_port()
        if detected_port:
            port_to_use = detected_port
        else:
            print("ERROR: No COM ports found. Please connect your Arduino.")
            sys.exit(1)
    
    # Try to connect to Arduino
    global arduino
    print(f"Connecting to Arduino on {port_to_use}...")
    try:
        arduino = serial.Serial(port_to_use, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for Arduino to initialize
        print("Connected to Arduino!")
    except Exception as e:
        # If connection failed and we used a specific port, try auto-detection
        if port_to_use == SERIAL_PORT and SERIAL_PORT != 'AUTO':
            print(f"Failed to connect to {SERIAL_PORT}, trying auto-detection...")
            detected_port = find_ch340_port()
            if detected_port and detected_port != SERIAL_PORT:
                try:
                    port_to_use = detected_port
                    arduino = serial.Serial(port_to_use, BAUD_RATE, timeout=1)
                    time.sleep(2)
                    print(f"Connected to Arduino on {port_to_use}!")
                except Exception as e2:
                    print(f"Failed to connect to auto-detected port: {e2}")
                    sys.exit(1)
            else:
                print(f"Failed to connect to Arduino: {e}")
                sys.exit(1)
        else:
            print(f"Failed to connect to Arduino: {e}")
            print("\nPlease check:")
            print(f"1. Arduino is connected")
            print("2. No other program is using the serial port")
            print("3. Arduino drivers are installed (CH340 driver)")
            print("\nTo manually specify a port, set SERIAL_PORT in config.py")
            sys.exit(1)
    
    # Send initial color configuration
    send_command(f'C,{RED_R},{RED_G},{RED_B}')
    print(f"Set LED color to RGB({RED_R}, {RED_G}, {RED_B})")
    
    # Set up mouse and keyboard listeners
    print("\nStarting mouse and keyboard monitoring...")
    print("Press Ctrl+C to stop\n")
    
    mouse_listener = mouse.Listener(on_move=on_mouse_move)
    keyboard_listener = keyboard.Listener(on_press=on_key_press)
    
    mouse_listener.start()
    keyboard_listener.start()
    
    try:
        # Keep the script running
        mouse_listener.join()
        keyboard_listener.join()
    except KeyboardInterrupt:
        print("\nStopping...")
        mouse_listener.stop()
        keyboard_listener.stop()
        if arduino:
            arduino.close()
        print("Done!")

if __name__ == '__main__':
    main()

