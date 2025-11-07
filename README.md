# HomeStrip - Interactive LED Strip Controller

An Arduino-based LED strip that responds to your computer activity - mouse movements, keyboard typing, and more! The strip provides visual feedback based on your PC usage patterns.

## Features

- 🖱️ **Mouse Movement**: Strip fades to red (1-second smooth transition) when you move your mouse
- ⌨️ **Keyboard Typing**: LEDs light up sequentially as you type, moving forward with each keystroke
- ⬅️ **Backspace Support**: Moves backward through LEDs when you press backspace
- ⚡ **Space Bar Flash**: Flashes the entire strip red when you press space
- ⏱️ **Auto-Fade**: Automatically fades to red after 5 seconds of no typing, and fades to black after 5 seconds of no activity
- 🎨 **Configurable Colors**: Customize the "red" color to any RGB value you want
- 🔌 **Auto-Detection**: Automatically detects CH340 Arduino on any COM port
- 🖥️ **System Tray App**: Runs in the background with a system tray icon (Windows)
- ⚙️ **Runtime Controls**: Right-click the tray icon to enable/disable features:
  - Toggle keyboard reaction on/off
  - Toggle mouse reaction on/off
  - Stay On mode (keeps LEDs lit even when idle)

## Hardware Requirements

- Arduino board (Uno, Nano, or compatible)
- WS2812B/NeoPixel LED strip (30 LEDs)
- USB cable to connect Arduino to PC
- CH340 USB-to-Serial chip (common on many Arduino clones)

## Software Requirements

- Arduino IDE
- Python 3.7+ (for PC-side monitoring)
- Required Python packages (see Installation)

## Installation

### 1. Arduino Setup

1. Install the **Adafruit NeoPixel** library in Arduino IDE:
   - Go to `Sketch` → `Include Library` → `Manage Libraries`
   - Search for "Adafruit NeoPixel" and install it

2. Connect your LED strip:
   - Data pin → Arduino pin 5 (or change `LED_PIN` in the code)
   - VCC → 5V (or external power supply for longer strips)
   - GND → GND

3. Upload `HomeStrip.ino` to your Arduino

### 2. PC-Side Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure settings (optional):
   - Edit `config.py` to customize:
     - Serial port (default: AUTO - auto-detects CH340)
     - LED color RGB values (default: bright red 255,0,0)

3. Run the monitor:
   ```bash
   python pc_monitor.py
   ```

## Configuration

### Color Configuration

Edit `config.py` to change the LED color:

```python
RED_R = 255  # Red component (0-255)
RED_G = 0    # Green component (0-255)
RED_B = 0    # Blue component (0-255)
```

**Example colors:**
- Orange: `RED_R = 255, RED_G = 165, RED_B = 0`
- Pink: `RED_R = 255, RED_G = 20, RED_B = 147`
- Purple: `RED_R = 128, RED_G = 0, RED_B = 128`
- Cyan: `RED_R = 0, RED_G = 255, RED_B = 255`

### Serial Port Configuration

The script auto-detects CH340 Arduinos by default. To manually specify a port:

```python
SERIAL_PORT = 'COM3'  # Windows
# or
SERIAL_PORT = '/dev/ttyUSB0'  # Linux
```

### Command Line Color Override

You can also override the color when running the script:

```bash
python pc_monitor.py 255 100 0  # Orange color
```

## Building an Executable

To create a standalone `.exe` file (no Python required):

### Quick Build (Windows)
Double-click `build.bat`

### Python Build Script
```bash
python build_exe.py
```

### Manual Build
```bash
pyinstaller --onefile --name HomeStripMonitor --windowed --icon icon.ico --add-data "config.py;." --add-data "icon.png;." pc_monitor.py
```

**Note:** The build scripts automatically convert `icon.png` to `icon.ico` for Windows (required for executable file icons).

The executable will be in the `dist/` folder. See `docs/build_instructions.md` for more details.

**Note:** The executable runs as a system tray application. After launching, look for the icon in the system tray (bottom right on Windows). Right-click the icon to access the menu with options to enable/disable features.

### System Tray Menu

When running the executable, you'll see an icon in the system tray. Right-click it to access:

- **React to Keyboard**: Toggle keyboard monitoring (✓ when enabled)
- **React to Mouse**: Toggle mouse monitoring (✓ when enabled)  
- **Stay On**: Keep LEDs lit even when idle (sends keep-alive signals)
- **Exit**: Close the application

## How It Works

### Behavior Modes

1. **Idle Mode**: Strip is off (black)
2. **Mouse Active**: Strip fades to red when mouse moves
3. **Keyboard Active**: Single LED lights up and moves forward with each keystroke
4. **Auto-Fade**: After 5 seconds of inactivity, automatically transitions

### Communication Protocol

The PC sends simple commands via serial:
- `M` - Mouse moved
- `K` - Key pressed
- `B` - Backspace pressed
- `S` - Space pressed
- `C,r,g,b` - Set color (RGB values)

## Troubleshooting

### Arduino Not Detected

1. **Check COM Port**:
   - Windows: Device Manager → Ports (COM & LPT)
   - Look for "USB-SERIAL CH340" or similar
   - Update `config.py` if auto-detection fails

2. **Driver Issues**:
   - Install CH340 drivers if needed
   - Download from: https://github.com/WCHSoftGroup/ch34xser_linux or manufacturer website

3. **Port Already in Use**:
   - Close Arduino IDE Serial Monitor
   - Close any other programs using the port

### LED Strip Not Working

1. **Check Connections**:
   - Data pin connected to pin 5 (or your configured pin)
   - Power supply adequate (external 5V recommended for 30+ LEDs)
   - GND connected

2. **Verify LED Count**:
   - Make sure `NUM_LEDS` in `HomeStrip.ino` matches your strip (default: 30)

3. **Test with Arduino IDE**:
   - Upload a simple NeoPixel test sketch to verify hardware

### Python Script Issues

1. **Missing Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Permission Errors (Linux/Mac)**:
   - May need to add user to dialout group: `sudo usermod -a -G dialout $USER`
   - Log out and back in

3. **Keyboard/Mouse Monitoring Fails**:
   - On Linux, may need: `sudo pip install pynput`
   - On some systems, pynput requires additional permissions

## File Structure

```
HomeStrip/
├── HomeStrip.ino          # Arduino code
├── pc_monitor.py          # Python monitoring script (system tray app)
├── config.py              # Configuration file
├── icon.png               # Application icon (PNG format)
├── icon.ico               # Application icon (ICO format, auto-generated)
├── convert_icon.py        # Icon conversion utility
├── build_exe.py           # Build script for executable
├── build.bat              # Windows batch build script
├── refresh_icon_cache.bat # Windows icon cache refresh utility
├── requirements.txt       # Python dependencies
├── docs/
│   └── build_instructions.md  # Detailed build guide
└── README.md              # This file
```

## Customization

### Changing LED Pin

Edit `HomeStrip.ino`:
```cpp
#define LED_PIN 5  // Change to your pin
```

### Changing Number of LEDs

Edit `HomeStrip.ino`:
```cpp
#define NUM_LEDS 30  // Change to your LED count
```

### Adjusting Timeouts

Edit `HomeStrip.ino`:
```cpp
const unsigned long IDLE_TIMEOUT = 5000;  // 5 seconds (milliseconds)
const unsigned long TRANSITION_TIME = 1000;  // 1 second fade (milliseconds)
```

## License

This project is open source. Feel free to modify and use as needed.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements!

## Credits

- Uses [Adafruit NeoPixel Library](https://github.com/adafruit/Adafruit_NeoPixel)
- Uses [pynput](https://github.com/moses-palmer/pynput) for input monitoring
- Uses [PySerial](https://github.com/pyserial/pyserial) for serial communication
- Uses [pystray](https://github.com/moses-palmer/pystray) for system tray functionality
- Uses [Pillow](https://github.com/python-pillow/Pillow) for image processing

## Quick Start

1. **Upload Arduino code**: Open `HomeStrip.ino` in Arduino IDE and upload to your board
2. **Install Python dependencies**: `pip install -r requirements.txt`
3. **Run the monitor**: `python pc_monitor.py` (or use the built executable)
4. **Configure** (optional): Edit `config.py` to customize colors and settings
5. **Enjoy**: Move your mouse or type to see the LEDs react!

