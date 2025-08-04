import requests
import yt_dlp
import os
import json
from pathlib import Path
from pydub import AudioSegment
import browser_cookie3
import time

class PatreonAudioDownloader:
    def __init__(self):
        self.output_dir = Path('downloads')
        self.output_dir.mkdir(exist_ok=True)
        self.cookies = None
        self.setup_authentication()

    def setup_authentication(self):
        print("Attempting to load cookies from browsers...")
        self.cookies = self._get_cookies()
        
        if not self.cookies:
            print("\nNo browser cookies found. You can:")
            print("1. Log in to Patreon in Chrome/Firefox and restart this script")
            print("2. Enter your session cookie manually")
            choice = input("\nWould you like to enter session cookie manually? (y/n): ").lower()
            
            if choice == 'y':
                print("\nTo get your session cookie:")
                print("1. Go to Patreon and log in")
                print("2. Press F12 to open Developer Tools")
                print("3. Go to Application/Storage > Cookies > patreon.com")
                print("4. Find 'session_id' and copy its value")
                
                session_id = input("\nEnter your session_id cookie value: ").strip()
                if session_id:
                    self._create_cookie_file(session_id)

    def _get_cookies(self):
        try:
            return browser_cookie3.chrome(domain_name='.patreon.com')
        except Exception as e:
            print(f"Chrome cookie error: {str(e)}")
            try:
                return browser_cookie3.firefox(domain_name='.patreon.com')
            except Exception as e:
                print(f"Firefox cookie error: {str(e)}")
                return None

    def _create_cookie_file(self, session_id):
        # Create cookie file in Netscape format
        with open('cookies.txt', 'w') as f:
            # Write header
            f.write("# Netscape HTTP Cookie File\n")
            f.write("# https://curl.haxx.se/rfc/cookie_spec.html\n")
            f.write("# This is a generated file!  Do not edit.\n\n")
            
            # Write cookie in correct format:
            # domain_name domain_flag path secure_flag expiry name value
            expiry = int(time.time()) + 365 * 24 * 3600  # 1 year from now
            f.write(f"patreon.com\tFALSE\t/\tTRUE\t{expiry}\tsession_id\t{session_id}\n")
            f.write(f".patreon.com\tTRUE\t/\tTRUE\t{expiry}\tsession_id\t{session_id}\n")
        print("Cookie file created successfully!")

    def download_and_convert(self, url):
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
                'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
                'quiet': False,
                'verbose': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("Attempting to download with authentication...")
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)
                audio_path = str(Path(video_path).with_suffix('.mp3'))
                
                if os.path.exists(video_path):
                    video = AudioSegment.from_file(video_path)
                    video.export(audio_path, format="mp3")
                    os.remove(video_path)
                    print(f"Successfully converted to audio: {audio_path}")
                    return audio_path
                    
        except Exception as e:
            print(f"Error: {str(e)}")
            print("\nTroubleshooting tips:")
            print("1. Verify that you're logged into Patreon")
            print("2. Check if you have access to this content")
            print("3. Try entering the session cookie manually")
            print("4. Make sure your session_id is correct and not expired")
            return None

def main():
    downloader = PatreonAudioDownloader()
    
    while True:
        url = input("\nEnter Patreon video URL (or 'q' to quit): ").strip()
        if url.lower() == 'q':
            break
            
        if url:
            print("Downloading and converting to audio...")
            result = downloader.download_and_convert(url)
            if result:
                print(f"Audio saved to: {result}")
        else:
            print("Please enter a valid URL")

if __name__ == "__main__":
    main()