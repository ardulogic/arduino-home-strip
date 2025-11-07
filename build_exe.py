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
    
    # PyInstaller command
    # Determine path separator based on platform
    if sys.platform == 'win32':
        data_sep = ';'
    else:
        data_sep = ':'
    
    cmd = [
        'pyinstaller',
        '--onefile',  # Create a single executable file
        '--name', 'HomeStripMonitor',  # Name of the executable
        '--console',  # Keep console window (for debugging)
        '--add-data', f'config.py{data_sep}.',  # Include config.py
        'pc_monitor.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✓ Build successful!")
        print(f"Executable created in: dist/HomeStripMonitor.exe")
        print("\nYou can now run HomeStripMonitor.exe without Python installed!")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed: {e}")
        print("\nMake sure PyInstaller is installed:")
        print("  pip install pyinstaller")
        sys.exit(1)
    except FileNotFoundError:
        print("\n✗ PyInstaller not found!")
        print("\nPlease install PyInstaller first:")
        print("  pip install pyinstaller")
        sys.exit(1)

if __name__ == '__main__':
    build_exe()

