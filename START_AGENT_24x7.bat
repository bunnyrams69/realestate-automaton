@echo off
title Real Estate AI Agent - 24/7 Always-On Runner
color 0A
echo ========================================================
echo   REAL ESTATE AI SALES & MARKETING AUTOMATION AGENT
echo   Starting 24/7 Background Services & Meta Webhook Sync...
echo ========================================================
cd /d "%~dp0"

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

python scripts\keep_bot_online.py
pause
