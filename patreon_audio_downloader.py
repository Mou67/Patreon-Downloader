import requests
import yt_dlp
import os
import json
from pathlib import Path
import subprocess
import browser_cookie3
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading

class PatreonAudioDownloader:
    def __init__(self, progress_callback=None, log_callback=None):
        self.output_dir = Path('downloads')
        self.output_dir.mkdir(exist_ok=True)
        self.cookies = None
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.setup_authentication()

    def log(self, message):
        """Log message to console and GUI if callback is provided"""
        print(message)
        if self.log_callback:
            self.log_callback(message)

    def setup_authentication(self):
        self.log("Attempting to load cookies from browsers...")
        self.cookies = self._get_cookies()
        
        if not self.cookies:
            self.log("\nNo browser cookies found.")
            return False
        return True

    def setup_manual_authentication(self, session_id):
        """Setup authentication with manual session ID"""
        if session_id:
            self._create_cookie_file(session_id)
            return True
        return False

    def _get_cookies(self):
        try:
            return browser_cookie3.chrome(domain_name='.patreon.com')
        except Exception as e:
            self.log(f"Chrome cookie error: {str(e)}")
            try:
                return browser_cookie3.firefox(domain_name='.patreon.com')
            except Exception as e:
                self.log(f"Firefox cookie error: {str(e)}")
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
        self.log("Cookie file created successfully!")

    def download_and_convert(self, url):
        try:
            def progress_hook(d):
                if self.progress_callback and d['status'] == 'downloading':
                    if 'total_bytes' in d:
                        percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                        self.progress_callback(percent)
                    elif 'total_bytes_estimate' in d:
                        percent = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                        self.progress_callback(percent)

            # Download directly as MP3 to avoid conversion issues
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
                'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
                'quiet': True,
                'verbose': False,
                'progress_hooks': [progress_hook],
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.log("Attempting to download with authentication...")
                info = ydl.extract_info(url, download=True)
                
                # The output file will be the MP3 version after post-processing
                base_filename = ydl.prepare_filename(info)
                audio_path = str(Path(base_filename).with_suffix('.mp3'))
                
                if os.path.exists(audio_path):
                    self.log(f"Successfully downloaded and converted to audio: {audio_path}")
                    return audio_path
                else:
                    # Sometimes the filename might be different, let's search for MP3 files
                    base_name = Path(base_filename).stem
                    for file in self.output_dir.glob(f"{base_name}*.mp3"):
                        self.log(f"Found converted audio file: {file}")
                        return str(file)
                    
                    self.log("Could not find the converted audio file")
                    return None
                    
        except Exception as e:
            error_msg = f"Error: {str(e)}\n\nTroubleshooting tips:\n1. Verify that you're logged into Patreon\n2. Check if you have access to this content\n3. Try entering the session cookie manually\n4. Make sure your session_id is correct and not expired\n5. Make sure FFmpeg is installed on your system"
            self.log(error_msg)
            return None

class PatreonGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Patreon Audio Downloader")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Initialize downloader
        self.downloader = None
        self.current_download = None
        
        self.setup_ui()
        self.setup_downloader()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # URL input
        ttk.Label(main_frame, text="Patreon URL:").grid(row=0, column=0, sticky="w", pady=5)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=(5, 0))
        
        # Download button
        self.download_btn = ttk.Button(main_frame, text="Download & Convert", command=self.start_download)
        self.download_btn.grid(row=0, column=2, pady=5, padx=(5, 0))
        
        # Progress bar
        ttk.Label(main_frame, text="Progress:").grid(row=1, column=0, sticky="w", pady=5)
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=1, column=1, columnspan=2, sticky="ew", pady=5, padx=(5, 0))
        
        # Output directory selection
        ttk.Label(main_frame, text="Output Directory:").grid(row=2, column=0, sticky="w", pady=5)
        self.output_var = tk.StringVar(value=str(Path('downloads').absolute()))
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=2, column=1, columnspan=2, sticky="ew", pady=5, padx=(5, 0))
        output_frame.columnconfigure(0, weight=1)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_var, state='readonly')
        self.output_entry.grid(row=0, column=0, sticky="ew")
        ttk.Button(output_frame, text="Browse", command=self.browse_output).grid(row=0, column=1, padx=(5, 0))
        
        # Authentication section
        auth_frame = ttk.LabelFrame(main_frame, text="Authentication", padding="5")
        auth_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=10)
        auth_frame.columnconfigure(1, weight=1)
        
        # Session ID input
        ttk.Label(auth_frame, text="Session ID:").grid(row=0, column=0, sticky="w", pady=2)
        self.session_var = tk.StringVar()
        self.session_entry = ttk.Entry(auth_frame, textvariable=self.session_var, show="*", width=40)
        self.session_entry.grid(row=0, column=1, sticky="ew", pady=2, padx=(5, 0))
        ttk.Button(auth_frame, text="Set Cookie", command=self.set_manual_cookie).grid(row=0, column=2, pady=2, padx=(5, 0))
        
        # Help button for cookie instructions
        ttk.Button(auth_frame, text="How to get Session ID?", command=self.show_cookie_help).grid(row=1, column=0, columnspan=3, pady=5)
        
        # Status display
        ttk.Label(main_frame, text="Status:").grid(row=4, column=0, sticky="nw", pady=5)
        self.status_text = scrolledtext.ScrolledText(main_frame, height=10, width=60)
        self.status_text.grid(row=4, column=1, columnspan=2, sticky="nsew", pady=5, padx=(5, 0))
        
        # Configure grid weights for status text
        main_frame.rowconfigure(4, weight=1)
        
        # Clear log button
        ttk.Button(main_frame, text="Clear Log", command=self.clear_log).grid(row=5, column=1, pady=5, sticky="w", padx=(5, 0))
        
    def setup_downloader(self):
        """Initialize the downloader with GUI callbacks"""
        try:
            self.downloader = PatreonAudioDownloader(
                progress_callback=self.update_progress,
                log_callback=self.log_message
            )
            
            # Check initial authentication status
            if self.downloader.cookies:
                self.log_message("✓ Browser cookies loaded successfully!")
            else:
                self.log_message("⚠ No browser cookies found. Please enter session ID manually.")
        except Exception as e:
            self.log_message(f"Error initializing downloader: {str(e)}")
            # Create a basic downloader without callbacks if initialization fails
            self.downloader = PatreonAudioDownloader()
    
    def log_message(self, message):
        """Add message to status display"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Clear the status log"""
        self.status_text.delete(1.0, tk.END)
    
    def update_progress(self, percent):
        """Update progress bar"""
        self.progress['value'] = percent
        self.root.update_idletasks()
    
    def browse_output(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(initialdir=self.output_var.get())
        if directory:
            self.output_var.set(directory)
            if self.downloader:
                self.downloader.output_dir = Path(directory)
    
    def set_manual_cookie(self):
        """Set manual session cookie"""
        session_id = self.session_var.get().strip()
        if not session_id:
            messagebox.showwarning("Warning", "Please enter a session ID")
            return
        
        if self.downloader and self.downloader.setup_manual_authentication(session_id):
            self.log_message("✓ Session cookie set successfully!")
            messagebox.showinfo("Success", "Session cookie has been set!")
        else:
            messagebox.showerror("Error", "Failed to set session cookie")
    
    def show_cookie_help(self):
        """Show instructions for getting session cookie"""
        help_text = """How to get your Patreon Session ID:

1. Go to Patreon.com and log in to your account
2. Press F12 to open Developer Tools
3. Go to the "Application" tab (Chrome) or "Storage" tab (Firefox)
4. In the left sidebar, expand "Cookies" and click on "https://www.patreon.com"
5. Look for a cookie named "session_id"
6. Copy the entire value of this cookie
7. Paste it into the Session ID field above and click "Set Cookie"

Note: The session ID is sensitive information - keep it private!"""
        
        messagebox.showinfo("Cookie Help", help_text)
    
    def start_download(self):
        """Start download in a separate thread"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a Patreon URL")
            return
        
        if not url.startswith('https://www.patreon.com/'):
            messagebox.showwarning("Warning", "Please enter a valid Patreon URL")
            return
        
        # Disable download button during download
        self.download_btn.config(state='disabled')
        self.progress['value'] = 0
        
        # Start download in separate thread
        self.current_download = threading.Thread(target=self.download_worker, args=(url,))
        self.current_download.daemon = True
        self.current_download.start()
    
    def download_worker(self, url):
        """Worker function for downloading"""
        try:
            if not self.downloader:
                raise Exception("Downloader not initialized")
                
            result = self.downloader.download_and_convert(url)
            
            # Update UI in main thread
            self.root.after(0, self.download_complete, result)
            
        except Exception as e:
            self.root.after(0, self.download_error, str(e))
    
    def download_complete(self, result):
        """Called when download is complete"""
        self.download_btn.config(state='normal')
        self.progress['value'] = 100
        
        if result:
            self.log_message(f"✓ Download completed successfully!")
            self.log_message(f"File saved to: {result}")
            messagebox.showinfo("Success", f"Audio file saved to:\n{result}")
        else:
            self.log_message("✗ Download failed!")
            messagebox.showerror("Error", "Download failed. Check the log for details.")
    
    def download_error(self, error):
        """Called when download encounters an error"""
        self.download_btn.config(state='normal')
        self.progress['value'] = 0
        self.log_message(f"✗ Error: {error}")
        messagebox.showerror("Error", f"An error occurred:\n{error}")
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()

def main():
    # Create and run GUI
    app = PatreonGUI()
    app.run()

if __name__ == "__main__":
    main()