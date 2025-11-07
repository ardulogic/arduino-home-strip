#!/usr/bin/env python3
"""
Build script to create an executable from pc_monitor.py
Run: python build_exe.py
"""

import subprocess
import sys
import os

def build_exe():
    """Build executable using PyInstaller."""
    print("Building executable...")
    print("This will create a standalone .exe file that doesn't require Python to be installed.\n")
    
    # Convert PNG to ICO if needed (Windows requires ICO for executable icon)
    if sys.platform == 'win32' and os.path.exists('icon.png') and not os.path.exists('icon.ico'):
        print("Converting icon.png to icon.ico for Windows executable...")
        try:
            from PIL import Image
            img = Image.open('icon.png')
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            images = []
            for size in sizes:
                resized = img.resize(size, Image.Resampling.LANCZOS)
                images.append(resized)
            img.save('icon.ico', format='ICO', sizes=[(s[0], s[1]) for s in sizes])
            print("Icon converted successfully\n")
        except Exception as e:
            print(f"Warning: Could not convert icon: {e}\n")
    
    # PyInstaller command
    # Determine path separator based on platform
    if sys.platform == 'win32':
        data_sep = ';'
    else:
        data_sep = ':'
    
    # Check for icon file (prefer .ico on Windows, .png otherwise)
    icon_flag = []
    if sys.platform == 'win32':
        if os.path.exists('icon.ico'):
            icon_flag = ['--icon', 'icon.ico']
            print("Using icon.ico for executable icon")
        elif os.path.exists('icon.png'):
            icon_flag = ['--icon', 'icon.png']
            print("Using icon.png for executable icon (consider converting to .ico)")
    else:
        if os.path.exists('icon.png'):
            icon_flag = ['--icon', 'icon.png']
            print("Using icon.png for executable icon")
    
    cmd = [
        'pyinstaller',
        '--onefile',  # Create a single executable file
        '--name', 'HomeStripMonitor',  # Name of the executable
        '--windowed',  # Hide console window (system tray app)
        '--hiddenimport', 'serial',  # Include pyserial (imported as 'serial')
        '--add-data', f'config.py{data_sep}.',  # Include config.py
        '--add-data', f'icon.png{data_sep}.',  # Include icon.png for system tray
    ]
    
    # Add icon flag if icon file exists
    if icon_flag:
        cmd.extend(icon_flag)
    else:
        print("Warning: No icon file found (icon.png or icon.ico)")
    
    cmd.append('pc_monitor.py')
    
    try:
        subprocess.run(cmd, check=True)
        print("\nBuild successful!")
        print(f"Executable created in: dist/HomeStripMonitor.exe")
        print("\nYou can now run HomeStripMonitor.exe without Python installed!")
        if icon_flag:
            print("\nNote: If the icon doesn't appear in Windows Explorer, try:")
            print("  1. Press F5 to refresh the folder")
            print("  2. Run refresh_icon_cache.bat to clear Windows icon cache")
            print("  3. Or manually: Delete the .exe, rebuild, then refresh folder")
            print("\nThe icon IS embedded in the executable (check the .spec file).")
            print("This is usually a Windows icon cache issue.")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed: {e}")
        print("\nMake sure PyInstaller is installed:")
        print("  pip install pyinstaller")
        sys.exit(1)
    except FileNotFoundError:
        print("\nPyInstaller not found!")
        print("\nPlease install PyInstaller first:")
        print("  pip install pyinstaller")
        sys.exit(1)

if __name__ == '__main__':
    build_exe()

