# Deployment & Infrastructure Guide

**Hosting Target:** Render (Backend), Supabase (Database), Vercel (Frontend)  
**Local Tunneling:** Cloudflare Quick Tunnels (`cloudflared`)  
**Resource Footprint:** Zero Docker Desktop required; ultra-lightweight hosted architecture.  

---

## 1. Hosting Architecture Overview

```
[ Customer / WhatsApp Meta Cloud ]
                │
                ▼
  [ Cloudflare Quick Tunnel (Dev) / Render HTTPS (Prod) ]
                │
                ▼
  [ Render Web Service: FastAPI Python App (Uvicorn) ]
         │                              │
         ▼                              ▼
  [ Supabase PostgreSQL ]        [ Vercel: Next.js Admin Dashboard ]
```

---

## 2. Local Development & Webhook Tunneling (Cloudflare)

WhatsApp Business Platform Cloud API requires an internet-accessible HTTPS endpoint to deliver webhooks.
Because `cloudflared.exe` is already installed in this environment, local webhook testing is seamless and costs nothing:

```powershell
# 1. Start the FastAPI local server
.\.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000

# 2. In a separate terminal, launch Cloudflare Quick Tunnel (no account required)
cloudflared tunnel --url http://localhost:8000
```
`cloudflared` outputs a public URL (e.g. `https://random-words.trycloudflare.com`).  
Set this URL in the Meta Developer Portal as your Webhook Callback URL:  
`https://random-words.trycloudflare.com/api/v1/webhooks/whatsapp`

---

## 3. Production Deployment: Render (Backend)

- **Service Type:** Web Service
- **Runtime:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2`
- **Health Check Path:** `/health`
- **Environment Variables:** Configure via the Render Environment dashboard using the parameters defined in `.env.example`.

---

## 4. Production Deployment: Supabase (Database)

1. Create a Supabase project at [supabase.com](https://supabase.com).
2. Copy the **Connection String (Transaction Pooler / Port 6543 or Session / 5432)** to `DATABASE_URL`.
3. Migrations are executed via Alembic:
   ```bash
   alembic upgrade head
   ```

---

## 5. Production Deployment: Vercel (Frontend Dashboard)

- **Framework:** Next.js
- **Root Directory:** `frontend/` (when constructed in Phase 4/9)
- **Environment Variables:** `NEXT_PUBLIC_API_URL=https://your-render-app.onrender.com/api/v1`
