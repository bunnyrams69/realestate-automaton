@echo off
title Real Estate AI - Admin Dashboard
color 0B
echo ========================================================
echo   REAL ESTATE AI SALES & MARKETING AUTOMATION DASHBOARD
echo   Connecting to Cloud Backend: https://realestate-automaton.onrender.com
echo ========================================================
cd /d "%~dp0frontend"

echo Starting Next.js Web Dashboard on http://localhost:3000 ...
start "" "http://localhost:3000"
npm run dev
pause
