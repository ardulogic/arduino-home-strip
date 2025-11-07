# Building an Executable from Python Code

This guide shows you how to create a standalone `.exe` file from the Python monitor script.

## Method 1: Using the Build Script (Easiest)

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Run the build script:
   ```bash
   python build_exe.py
   ```

3. The executable will be created in the `dist/` folder as `HomeStripMonitor.exe`

## Method 2: Manual PyInstaller Command

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Run PyInstaller:
   ```bash
   pyinstaller --onefile --name HomeStripMonitor --windowed --icon icon.ico --add-data "config.py;." --add-data "icon.png;." pc_monitor.py
   ```

   **Note:** The build script automatically converts `icon.png` to `icon.ico` if needed (Windows requires .ico format for executable icons).

   **Note for Linux/Mac:**
   ```bash
   pyinstaller --onefile --name HomeStripMonitor --windowed --icon icon.png --add-data "config.py:." --add-data "icon.png:." pc_monitor.py
   ```

3. Find your executable in the `dist/` folder

## PyInstaller Options Explained

- `--onefile`: Creates a single executable file (easier to distribute)
- `--name HomeStripMonitor`: Sets the name of the executable
- `--windowed`: Hides the console window (required for system tray app)
- `--icon icon.ico`: Sets the icon for the executable (Windows requires .ico format, auto-converted from icon.png if needed)
- `--add-data "config.py;."`: Includes config.py in the executable
- `--add-data "icon.png;."`: Includes icon.png in the executable (for system tray)
- `pc_monitor.py`: The main Python script to build

**Note:** The application runs as a system tray app, so `--windowed` is required. The icon will appear in the system tray (bottom right on Windows).

## Troubleshooting

### "PyInstaller not found"
Install it: `pip install pyinstaller`

### "Module not found" errors
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Large file size
The executable includes Python and all dependencies, so it will be large (usually 20-50 MB). This is normal.

### Antivirus warnings
Some antivirus software may flag PyInstaller executables as suspicious. This is a false positive. You can:
- Add an exception for the executable
- Use `--clean` flag: `pyinstaller --clean --onefile ...`

## Distribution

Once built, you can distribute just the `HomeStripMonitor.exe` file. Users don't need Python installed to run it!

Make sure to include `config.py` if users need to customize settings, or the executable will use default values.

