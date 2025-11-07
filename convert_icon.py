#!/usr/bin/env python3
"""
Convert icon.png to icon.ico for Windows executable icon.
"""

from PIL import Image
import os

def convert_png_to_ico():
    """Convert icon.png to icon.ico."""
    if not os.path.exists('icon.png'):
        print("icon.png not found!")
        return False
    
    try:
        # Open the PNG image
        img = Image.open('icon.png')
        
        # Convert to ICO format with multiple sizes (Windows prefers multiple sizes)
        # Common sizes: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Resize image for each size
        images = []
        for size in sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            images.append(resized)
        
        # Save as ICO
        img.save('icon.ico', format='ICO', sizes=[(s[0], s[1]) for s in sizes])
        print("✓ Successfully converted icon.png to icon.ico")
        return True
    except Exception as e:
        print(f"✗ Error converting icon: {e}")
        return False

if __name__ == '__main__':
    convert_png_to_ico()

