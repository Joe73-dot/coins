import hmac
import hashlib
import time
import os
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow requests from your Netlify dashboard

# ── Load API credentials from environment variables (never hardcode!) ──────────
API_KEY    = os.environ.get("COINS_API_KEY", "")
API_SECRET = os.environ.get("COINS_API_SECRET", "")
BASE_URL   = "https://api.coins.ph"

# ── HMAC-SHA256 Signer ─────────────────────────────────────────────────────────
def sign_request(method: str, path: str, body: str = "") -> dict:
    """
    Returns headers with Coins.ph HMAC-SHA256 signature.
    Coins.ph signature format:
      message  = timestamp + method.upper() + path + body
      signature = HMAC-SHA256(secret, message)
    """
    timestamp = str(int(time.time() * 1000))
    message   = timestamp + method.upper() + path + body
    signature = hmac.new(
        API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return {
        "Content-Type":    "application/json",
        "X-COINS-APIKEY":  API_KEY,
        "X-COINS-TIMESTAMP": timestamp,
        "X-COINS-SIGNATURE": signature,
    }

# ── Helper: safe GET ───────────────────────────────────────────────────────────
def coins_get(path: str) -> dict:
    headers = sign_request("GET", path)
    url     = BASE_URL + path
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()

# ── PHP conversion rate (used as fallback if Binance unavailable) ──────────────
PHP_RATE = 57.5

# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return jsonify({"status": "CoinsBot Backend Online", "version": "1.0"})


# ── 1. Prices: PEPE & BONK ────────────────────────────────────────────────────
@app.route("/prices")
def get_prices():
    """
    Fetch PEPE and BONK ticker data.
    Uses Binance public API (no key needed) — PEPE/BONK not listed on Coins.ph exchange.
    """
    results = {}
    pairs   = ["PEPEUSDT", "BONKUSDT"]

    for pair in pairs:
        coin = pair.replace("USDT", "").lower()
        try:
            resp = requests.get(
                f"https://api.binance.com/api/v3/ticker/24hr?symbol={pair}",
                timeout=10
            )
            resp.raise_for_status()
            b = resp.json()

            # Validate required fields exist
            if "lastPrice" not in b:
                raise ValueError(f"Unexpected Binance response: {b}")

            price_usdt = float(b["lastPrice"])
            results[coin] = {
                "price_usdt": price_usdt,
                "price_php":  round(price_usdt * PHP_RATE, 10),
                "change_pct": float(b["priceChangePercent"]),
                "high_usdt":  float(b["highPrice"]),
                "low_usdt":   float(b["lowPrice"]),
                "volume":     float(b["volume"]),
                "source":     "binance"
            }
        except Exception as e:
            results[coin] = {"error": str(e)}

    return jsonify(results)


# ── 2. PHP Wallet Balance ──────────────────────────────────────────────────────
@app.route("/balance")
def get_balance():
    """
    Fetch wallet balances from Coins.ph account.
    Returns PHP, PEPE, BONK balances.
    """
    try:
        data     = coins_get("/api/v2/account")
        balances = data.get("data", {}).get("balances", [])

        # Filter only the coins we care about
        target   = {"PHP", "PEPE", "BONK", "USDT"}
        filtered = {
            b["asset"]: {
                "free":   float(b.get("free", 0)),
                "locked": float(b.get("locked", 0)),
                "total":  float(b.get("free", 0)) + float(b.get("locked", 0))
            }
            for b in balances if b.get("asset") in target
        }
        return jsonify({"balances": filtered})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── 3. Buy/Sell Signal Generator ───────────────────────────────────────────────
@app.route("/signal/<coin>")
def get_signal(coin: str):
    """
    Generate a BUY/SELL/HOLD signal for PEPE or BONK
    using price position in 24h range + change percent.
    """
    coin = coin.upper()
    if coin not in ("PEPE", "BONK"):
        return jsonify({"error": "Unsupported coin. Use PEPE or BONK."}), 400

    try:
        pair = f"{coin}USDT"
        # Fetch ticker directly from Binance (PEPE/BONK not on Coins.ph)
        resp  = requests.get(
            f"https://api.binance.com/api/v3/ticker/24hr?symbol={pair}",
            timeout=10
        )
        resp.raise_for_status()
        b     = resp.json()
        if "lastPrice" not in b:
            raise ValueError(f"Unexpected Binance response: {b}")
        price = float(b["lastPrice"])
        high  = float(b["highPrice"])
        low   = float(b["lowPrice"])
        chg   = float(b["priceChangePercent"])

        # Position in 24h range (0 = at low, 1 = at high)
        rng      = high - low
        position = (price - low) / rng if rng > 0 else 0.5

        # Signal logic
        if chg <= -4 and position < 0.35:
            signal  = "BUY"
            reason  = "Oversold — near 24h low"
            strength = "STRONG"
        elif chg <= -2 and position < 0.45:
            signal  = "BUY"
            reason  = "Mild dip — watch volume"
            strength = "MODERATE"
        elif chg >= 5 and position > 0.75:
            signal  = "SELL"
            reason  = "Overbought — near 24h high"
            strength = "STRONG"
        elif chg >= 2.5 and position > 0.6:
            signal  = "SELL"
            reason  = "Gaining — consider partial TP"
            strength = "MODERATE"
        else:
            signal  = "HOLD"
            reason  = "Neutral zone — wait for clearer signal"
            strength = "WEAK"

        return jsonify({
            "coin":      coin,
            "signal":    signal,
            "strength":  strength,
            "reason":    reason,
            "price_usdt": price,
            "price_php":  round(price * PHP_RATE, 10),
            "change_pct": chg,
            "position":   round(position, 3),
            "timestamp":  int(time.time() * 1000)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── 4. Health Check (for Render uptime ping) ───────────────────────────────────
@app.route("/ping")
def ping():
    return jsonify({"pong": True, "ts": int(time.time())})


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
