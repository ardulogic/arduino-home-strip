"""
Configuration file for LED strip control.
Modify these values to customize the behavior.
"""

# Serial port configuration
# Set to 'AUTO' to auto-detect CH340 Arduino, or specify a port like 'COM3'
# Windows: Usually COM3, COM4, etc. (check Device Manager)
# Linux/Mac: Usually /dev/ttyUSB0, /dev/ttyACM0, etc.
SERIAL_PORT = 'AUTO'  # Auto-detect CH340, or specify like 'COM3'
BAUD_RATE = 115200

# LED color configuration (RGB values, 0-255)
# Default: bright red
RED_R = 255
RED_G = 0
RED_B = 0

# You can change to other colors, for example:
# Orange: RED_R = 255, RED_G = 165, RED_B = 0
# Pink: RED_R = 255, RED_G = 20, RED_B = 147
# Purple: RED_R = 128, RED_G = 0, RED_B = 128

# Note: Audio visualization LED range is configured in HomeStrip.ino
# Edit AUDIO_START_LED and AUDIO_END_LED constants in the Arduino code

