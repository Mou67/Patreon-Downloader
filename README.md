# Patreon Audio Downloader 🎵

A user-friendly Windows application for downloading and converting Patreon content to MP3 files.

## 📦 Download & Installation

The application is available as a standalone `.exe` file - **no Python installation required**!

### System Requirements:
- Windows 10/11
- FFmpeg (for audio conversion)

### FFmpeg Installation:
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract it to a folder (e.g., `C:\ffmpeg`)
3. Add the `bin` folder to your system PATH

**OR** use Chocolatey:
```powershell
choco install ffmpeg
```

## 🚀 Usage

1. **Start the application**: Double-click on `PatreonAudioDownloader.exe`

2. **Setup authentication**:
   - Click on "How to get Session ID?" for instructions
   - Get your Session-ID from Patreon.com
   - Enter it and click "Set Cookie"

3. **Download content**:
   - Paste the Patreon URL
   - Choose output directory (optional)
   - Click "Download & Convert"
   - Track progress in the progress bar

## 🔐 Getting Session-ID

1. Go to [Patreon.com](https://www.patreon.com) and log in
2. Press `F12` for Developer Tools
3. Go to "Application" tab (Chrome) or "Storage" tab (Firefox)
4. Expand "Cookies" → "https://www.patreon.com"
5. Look for the cookie "session_id"
6. Copy the complete value
7. Paste it into the application

## ⚠️ Important Notes

- **Respect copyrights**: Only download content you are authorized to access
- **Session-ID is private**: Never share this with others
- **Personal use only**: Use the application responsibly

## 🛠️ Troubleshooting

### "FFmpeg not found" error:
- Make sure FFmpeg is installed and available in PATH
- Test with `ffmpeg -version` in command prompt

### Cookie issues:
- Make sure you are logged into Patreon
- Check if the Session-ID was copied correctly
- Session-IDs expire - get a new one if needed

### Download errors:
- Check your internet connection
- Make sure you have access to the content
- Try with a new Session-ID

## 📁 File Structure

```
PatreonAudioDownloader.exe    # Main application
downloads/                    # Default output directory
cookies.txt                   # Temporary cookie file (auto-created)
```

## 🔄 Updates

For updates, visit the original project or create a new .exe version from the source code.

---

**Version:** 1.0.0  
**Built with:** Python 3.13, tkinter, yt-dlp, PyInstaller
