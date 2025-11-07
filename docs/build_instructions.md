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
   pyinstaller --onefile --name HomeStripMonitor --console --add-data "config.py;." pc_monitor.py
   ```

   **Note for Linux/Mac:**
   ```bash
   pyinstaller --onefile --name HomeStripMonitor --console --add-data "config.py:." pc_monitor.py
   ```

3. Find your executable in the `dist/` folder

## PyInstaller Options Explained

- `--onefile`: Creates a single executable file (easier to distribute)
- `--name HomeStripMonitor`: Sets the name of the executable
- `--console`: Keeps the console window visible (remove this to hide the window)
- `--add-data "config.py;."`: Includes config.py in the executable
- `pc_monitor.py`: The main Python script to build

## Alternative: Create a Windowed Version (No Console)

If you want to hide the console window, use:
```bash
pyinstaller --onefile --name HomeStripMonitor --windowed --add-data "config.py;." pc_monitor.py
```

**Note:** With `--windowed`, you won't see error messages, so use `--console` for debugging.

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

