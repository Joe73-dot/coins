# CoinsBot Backend — Render.com Deployment Guide

## Files
- `app.py`          → Flask API with Coins.ph HMAC signing
- `requirements.txt`→ Python dependencies
- `Procfile`        → Render start command

## API Endpoints
| Endpoint         | Description                        |
|------------------|------------------------------------|
| GET /            | Health check                       |
| GET /ping        | Uptime ping                        |
| GET /prices      | PEPE & BONK prices (PHP + USDT)    |
| GET /balance     | Your PHP, PEPE, BONK balances      |
| GET /signal/pepe | BUY/SELL/HOLD signal for PEPE      |
| GET /signal/bonk | BUY/SELL/HOLD signal for BONK      |

## Deploy to Render.com (Step by Step)

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "CoinsBot backend"
git remote add origin https://github.com/YOUR_USERNAME/coinsbot-backend.git
git push -u origin main
```

### 2. Create Render Web Service
1. Go to render.com → New → Web Service
2. Connect your GitHub repo
3. Settings:
   - **Name:** coinsbot-backend
   - **Runtime:** Python 3
   - **Build Command:** pip install -r requirements.txt
   - **Start Command:** gunicorn app:app
   - **Plan:** Free

### 3. Add Environment Variables
In Render dashboard → Environment → Add:
- `COINS_API_KEY`    = your Coins.ph API key
- `COINS_API_SECRET` = your Coins.ph API secret

### 4. Deploy
Click "Create Web Service" — Render auto-deploys.
Your backend URL will be: https://coinsbot-backend.onrender.com

## Keep-Alive (Free Tier Fix)
Render free tier sleeps after 15 min inactivity.
Use UptimeRobot (free) to ping /ping every 5 minutes:
1. Go to uptimerobot.com
2. Add Monitor → HTTP(s)
3. URL: https://coinsbot-backend.onrender.com/ping
4. Interval: every 5 minutes
