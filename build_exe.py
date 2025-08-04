#!/usr/bin/env python3
"""
Build script for creating a Windows executable of the Patreon Audio Downloader
"""
import subprocess
import sys
import os
from pathlib import Path

def build_exe():
    """Build the executable using PyInstaller"""
    
    # Get the current directory
    current_dir = Path(__file__).parent
    
    # PyInstaller command with optimized settings
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=PatreonAudioDownloader",
        "--onefile",  # Create a single exe file
        "--windowed",  # No console window (GUI only)
        "--icon=NONE",  # You can add an icon file path here if you have one
        "--add-data=requirements.txt;.",  # Include requirements.txt
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.scrolledtext",
        "--hidden-import=browser_cookie3",
        "--hidden-import=yt_dlp",
        "--hidden-import=requests",
        "--collect-all=yt_dlp",
        "--collect-all=browser_cookie3",
        str(current_dir / "patreon_audio_downloader.py")
    ]
    
    print("🚀 Building executable...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=current_dir)
        
        print("✅ Build successful!")
        print("\n📁 Output location:")
        exe_path = current_dir / "dist" / "PatreonAudioDownloader.exe"
        print(f"   {exe_path}")
        
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"   Size: {size_mb:.1f} MB")
        
        print("\n📋 Instructions:")
        print("1. The .exe file is in the 'dist' folder")
        print("2. You can copy it anywhere and run it independently")
        print("3. No Python installation needed on target machines")
        print("4. Make sure FFmpeg is available on the target system for audio conversion")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Build failed!")
        print(f"Error: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

if __name__ == "__main__":
    build_exe()
