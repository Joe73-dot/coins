import hmac
import hashlib
import time
import os
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── Credentials from Render environment variables ─────────────────────────────
API_KEY    = os.environ.get("COINS_API_KEY", "")
API_SECRET = os.environ.get("COINS_API_SECRET", "")

# ── Correct Coins.ph Pro API base ─────────────────────────────────────────────
PUBLIC_BASE  = "https://api.pro.coins.ph"
PRIVATE_BASE = "https://api.pro.coins.ph"

# ── HMAC-SHA256 Signer ────────────────────────────────────────────────────────
def fetch_ticker(symbol: str) -> dict:
    path = "/openapi/quote/v1/ticker/24hr"
    url  = PUBLIC_BASE + path
    resp = requests.get(url, params={"symbol": symbol}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, list):
        for item in data:
            if item.get("symbol") == symbol:
                return item
        raise ValueError(f"Symbol {symbol} not found")
    return data

def fetch_account() -> dict:
    path  = "/openapi/v1/account"
    ts    = str(int(time.time() * 1000))
    query = f"timestamp={ts}"
    sig   = hmac.new(
        API_SECRET.encode("utf-8"),
        query.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    headers = {"X-COINS-APIKEY": API_KEY}
    resp = requests.get(
        PRIVATE_BASE + path,
        params={"timestamp": ts, "signature": sig},
        headers=headers,
        timeout=10
    )
    resp.raise_for_status()
    return resp.json()

@app.route("/")
def index():
    return jsonify({"status": "CoinsBot Backend Online", "version": "2.0"})

@app.route("/prices")
def get_prices():
    results = {}
    pairs = {"pepe": "PEPEPHP", "bonk": "BONKPHP"}
    for coin, symbol in pairs.items():
        try:
            t = fetch_ticker(symbol)
            results[coin] = {
                "price_php":  float(t["lastPrice"]),
                "change_pct": float(t.get("priceChangePercent", 0)),
                "high_php":   float(t.get("highPrice", 0)),
                "low_php":    float(t.get("lowPrice", 0)),
                "volume":     float(t.get("volume", 0)),
                "symbol":     symbol,
                "source":     "coins.ph"
            }
        except Exception as e:
            results[coin] = {"error": str(e), "symbol": symbol}
    return jsonify(results)

@app.route("/balance")
def get_balance():
    if not API_KEY or not API_SECRET:
        return jsonify({"error": "API keys not set in environment"}), 500
    try:
        data     = fetch_account()
        balances = data.get("balances", [])
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

@app.route("/signal/<coin>")
def get_signal(coin: str):
    coin = coin.upper()
    if coin not in ("PEPE", "BONK"):
        return jsonify({"error": "Use PEPE or BONK"}), 400
    symbol = f"{coin}PHP"
    try:
        t     = fetch_ticker(symbol)
        price = float(t["lastPrice"])
        high  = float(t.get("highPrice", price))
        low   = float(t.get("lowPrice", price))
        chg   = float(t.get("priceChangePercent", 0))
        rng   = high - low
        pos   = (price - low) / rng if rng > 0 else 0.5

        if chg <= -4 and pos < 0.35:
            signal, reason, strength = "BUY",  "Oversold — near 24h low",        "STRONG"
        elif chg <= -2 and pos < 0.45:
            signal, reason, strength = "BUY",  "Mild dip — watch volume",         "MODERATE"
        elif chg >= 5 and pos > 0.75:
            signal, reason, strength = "SELL", "Overbought — near 24h high",      "STRONG"
        elif chg >= 2.5 and pos > 0.6:
            signal, reason, strength = "SELL", "Gaining — consider partial TP",   "MODERATE"
        else:
            signal, reason, strength = "HOLD", "Neutral — wait for clear signal", "WEAK"

        return jsonify({
            "coin": coin, "symbol": symbol,
            "signal": signal, "strength": strength, "reason": reason,
            "price_php": price, "change_pct": chg,
            "position": round(pos, 3),
            "timestamp": int(time.time() * 1000)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ping")
def ping():
    return jsonify({"pong": True, "ts": int(time.time())})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
