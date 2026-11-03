"""
Always-On WhatsApp AI Agent Daemon & Meta Webhook Auto-Synchronizer
Automatically starts Uvicorn and Cloudflare Tunnel, extracts the public URL,
and updates the Meta Graph API webhook subscription so the bot replies 24/7.
"""

import os
import re
import sys
import time
import subprocess
import httpx
from dotenv import load_dotenv

load_dotenv()

APP_ID = "2367985254044058"
APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "a0880d2b24000eb200f0db2fa7c92c86")
WABA_ID = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "1726168285155060")
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "RealEstate_Verify_Secret_2026")
API_TOKEN = os.getenv("WHATSAPP_API_TOKEN", "")


def update_meta_webhook(public_url: str):
    """Update Meta Webhook Subscription via Graph API."""
    callback_url = f"{public_url.rstrip('/')}/api/v1/webhook"
    app_token = f"{APP_ID}|{APP_SECRET}"
    print(f"\n[+] Registering webhook URL with Meta: {callback_url}")

    with httpx.Client(timeout=15.0) as client:
        # 1. Update App Subscription
        sub_url = f"https://graph.facebook.com/v21.0/{APP_ID}/subscriptions"
        params = {
            "access_token": app_token,
            "object": "whatsapp_business_account",
            "callback_url": callback_url,
            "verify_token": VERIFY_TOKEN,
            "fields": "messages",
        }
        res = client.post(sub_url, params=params)
        print(f"[+] App Subscriptions API response: {res.status_code} - {res.text}")

        # 2. Subscribe WABA to App
        if API_TOKEN:
            waba_url = f"https://graph.facebook.com/v21.0/{WABA_ID}/subscribed_apps"
            headers = {"Authorization": f"Bearer {API_TOKEN}"}
            res_waba = client.post(waba_url, headers=headers)
            print(f"[+] WABA Subscribed Apps API response: {res_waba.status_code} - {res_waba.text}")

    # Update .env file
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "WEBHOOK_BASE_URL=" in content:
            new_content = re.sub(r'WEBHOOK_BASE_URL=".*?"', f'WEBHOOK_BASE_URL="{public_url}"', content)
        else:
            new_content = content + f'\nWEBHOOK_BASE_URL="{public_url}"\n'
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"[+] Updated .env with WEBHOOK_BASE_URL={public_url}")


def main():
    print("=" * 60)
    print("  REAL ESTATE AI AGENT - 24/7 AUTO-RUNNER & SYNC")
    print("=" * 60)

    # 1. Ensure Uvicorn is running
    server_running = False
    try:
        with httpx.Client(timeout=2.0) as client:
            r = client.get("http://127.0.0.1:8000/health")
            if r.status_code == 200:
                print("[+] Local Uvicorn server is already running on http://127.0.0.1:8000")
                server_running = True
    except Exception:
        pass

    uvicorn_proc = None
    if not server_running:
        print("[+] Starting Uvicorn backend server on port 8000...")
        uvicorn_proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        time.sleep(3)

    # 2. Start Cloudflare Tunnel
    print("[+] Launching Cloudflare Tunnel to expose port 8000...")
    tunnel_proc = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "http://127.0.0.1:8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    tunnel_url = None
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

    for line in iter(tunnel_proc.stdout.readline, ""):
        print(f" [tunnel] {line.strip()}")
        match = url_pattern.search(line)
        if match:
            tunnel_url = match.group(0)
            print("\n" + "*" * 60)
            print(f"  FOUND LIVE TUNNEL URL: {tunnel_url}")
            print("*" * 60)
            break

    if not tunnel_url:
        print("[-] Failed to extract Cloudflare tunnel URL.")
        return

    # 3. Verify handshake and update Meta
    time.sleep(2)
    update_meta_webhook(tunnel_url)

    print("\n" + "=" * 60)
    print("  >>> SUCCESS! Real Estate AI Agent is LIVE & LISTENING <<<")
    print("  You can now send messages from WhatsApp at ANY TIME!")
    print("  Keep this window open to maintain 24/7 connectivity.")
    print("=" * 60 + "\n")

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nStopping services...")
        tunnel_proc.terminate()
        if uvicorn_proc:
            uvicorn_proc.terminate()


if __name__ == "__main__":
    main()
