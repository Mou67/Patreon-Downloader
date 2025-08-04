@echo off
title Patreon Audio Downloader
echo.
echo ==============================================
echo     Patreon Audio Downloader v1.0
echo ==============================================
echo.
echo Starting application...
echo.

REM Change to the directory where the script is located
cd /d "%~dp0"

REM Check if the exe exists
if not exist "dist\PatreonAudioDownloader.exe" (
    echo ERROR: PatreonAudioDownloader.exe not found in dist folder!
    echo Please make sure the file exists.
    echo.
    pause
    exit /b 1
)

REM Run the application
echo Launching GUI...
start "" "dist\PatreonAudioDownloader.exe"

echo.
echo Application started successfully!
echo You can close this window now.
echo.
timeout /t 3 /nobreak >nul
