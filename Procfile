import hmac
import hashlib
import time
import os
import requests
import json
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── Credentials ───────────────────────────────────────────────────────────────
API_KEY    = os.environ.get("COINS_API_KEY", "")
API_SECRET = os.environ.get("COINS_API_SECRET", "")
BASE_URL   = "https://api.pro.coins.ph"

# ── Safety Config (edit these to your comfort level) ─────────────────────────
MAX_TRADE_PHP   = float(os.environ.get("MAX_TRADE_PHP", "200"))   # Max PHP per order
TRADE_ENABLED   = os.environ.get("TRADE_ENABLED", "true").lower() == "true"
SYMBOL          = "BONKPHP"
COIN            = "BONK"

# ── In-memory trade log (resets on redeploy) ──────────────────────────────────
trade_log = []

# ── HMAC Signer ───────────────────────────────────────────────────────────────
def sign(params: dict) -> str:
    query = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    return hmac.new(
        API_SECRET.encode("utf-8"),
        query.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

def auth_headers() -> dict:
    return {"X-COINS-APIKEY": API_KEY}

# ── Public: Ticker ────────────────────────────────────────────────────────────
def fetch_ticker(symbol: str) -> dict:
    resp = requests.get(
        BASE_URL + "/openapi/quote/v1/ticker/24hr",
        params={"symbol": symbol}, timeout=10
    )
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, list):
        for item in data:
            if item.get("symbol") == symbol:
                return item
        raise ValueError(f"{symbol} not found")
    return data

# ── Private: Account ──────────────────────────────────────────────────────────
def fetch_account() -> dict:
    ts     = str(int(time.time() * 1000))
    params = {"timestamp": ts}
    params["signature"] = sign(params)
    resp = requests.get(
        BASE_URL + "/openapi/v1/account",
        params=params, headers=auth_headers(), timeout=10
    )
    resp.raise_for_status()
    return resp.json()

# ── Private: Place Limit Order ────────────────────────────────────────────────
def place_limit_order(side: str, quantity: str, price: str) -> dict:
    """
    side: BUY or SELL
    quantity: amount of BONK
    price: limit price in PHP
    """
    ts     = str(int(time.time() * 1000))
    params = {
        "symbol":      SYMBOL,
        "side":        side,
        "type":        "LIMIT",
        "quantity":    quantity,
        "price":       price,
        "timeInForce": "GTC",   # Good Till Cancelled
        "timestamp":   ts,
    }
    params["signature"] = sign(params)
    resp = requests.post(
        BASE_URL + "/openapi/v1/order",
        params=params, headers=auth_headers(), timeout=10
    )
    resp.raise_for_status()
    return resp.json()

# ── Private: Cancel Order ─────────────────────────────────────────────────────
def cancel_order(order_id: str) -> dict:
    ts     = str(int(time.time() * 1000))
    params = {
        "symbol":    SYMBOL,
        "orderId":   order_id,
        "timestamp": ts,
    }
    params["signature"] = sign(params)
    resp = requests.delete(
        BASE_URL + "/openapi/v1/order",
        params=params, headers=auth_headers(), timeout=10
    )
    resp.raise_for_status()
    return resp.json()

# ── Private: Open Orders ──────────────────────────────────────────────────────
def fetch_open_orders() -> list:
    ts     = str(int(time.time() * 1000))
    params = {"symbol": SYMBOL, "timestamp": ts}
    params["signature"] = sign(params)
    resp = requests.get(
        BASE_URL + "/openapi/v1/openOrders",
        params=params, headers=auth_headers(), timeout=10
    )
    resp.raise_for_status()
    return resp.json()

# ── Signal logic ──────────────────────────────────────────────────────────────
def compute_signal(t: dict) -> dict:
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

    return {
        "signal": signal, "reason": reason, "strength": strength,
        "price_php": price, "change_pct": chg, "position": round(pos, 3),
        "high_php": high, "low_php": low
    }

# ── Log helper ────────────────────────────────────────────────────────────────
def log_trade(action: str, detail: dict):
    trade_log.insert(0, {
        "ts": int(time.time() * 1000),
        "time": time.strftime("%H:%M:%S", time.localtime()),
        "action": action,
        **detail
    })
    if len(trade_log) > 50:
        trade_log.pop()

# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return jsonify({
        "status": "CoinsBot Backend Online",
        "version": "3.0",
        "trade_enabled": TRADE_ENABLED,
        "max_trade_php": MAX_TRADE_PHP,
        "symbol": SYMBOL
    })

# ── Prices ────────────────────────────────────────────────────────────────────
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
            results[coin] = {"error": str(e)}
    return jsonify(results)

# ── Balance ───────────────────────────────────────────────────────────────────
@app.route("/balance")
def get_balance():
    if not API_KEY or not API_SECRET:
        return jsonify({"error": "API keys not configured"}), 500
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

# ── Signal ────────────────────────────────────────────────────────────────────
@app.route("/signal/<coin>")
def get_signal(coin: str):
    coin = coin.upper()
    if coin not in ("PEPE", "BONK"):
        return jsonify({"error": "Use PEPE or BONK"}), 400
    try:
        t   = fetch_ticker(f"{coin}PHP")
        sig = compute_signal(t)
        return jsonify({"coin": coin, "symbol": f"{coin}PHP",
                        "timestamp": int(time.time() * 1000), **sig})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── AUTO-TRADE: Execute ───────────────────────────────────────────────────────
@app.route("/trade/execute", methods=["POST"])
def execute_trade():
    """
    Checks current BONK/PHP signal and places a limit order if BUY or SELL.
    Safety checks:
      - TRADE_ENABLED must be true
      - Order value must not exceed MAX_TRADE_PHP
      - Must have sufficient balance
      - Only STRONG or MODERATE signals trigger trades
    """
    if not TRADE_ENABLED:
        return jsonify({"status": "skipped", "reason": "Trading disabled (TRADE_ENABLED=false)"}), 200

    if not API_KEY or not API_SECRET:
        return jsonify({"error": "API keys not configured"}), 500

    try:
        # 1. Get current price and signal
        t   = fetch_ticker(SYMBOL)
        sig = compute_signal(t)
        price     = sig["price_php"]
        signal    = sig["signal"]
        strength  = sig["strength"]

        # 2. Only act on STRONG or MODERATE signals
        if signal == "HOLD" or strength == "WEAK":
            log_trade("SKIP", {"symbol": SYMBOL, "signal": signal,
                                "reason": sig["reason"], "price_php": price})
            return jsonify({"status": "skipped", "signal": signal,
                            "reason": "Signal too weak to trade"})

        # 3. Get balances
        acct     = fetch_account()
        balances = {b["asset"]: float(b.get("free", 0))
                    for b in acct.get("balances", [])}
        php_free  = balances.get("PHP", 0)
        bonk_free = balances.get("BONK", 0)

        # 4. Calculate order
        if signal == "BUY":
            # Use up to MAX_TRADE_PHP, but not more than available PHP
            php_to_spend = min(MAX_TRADE_PHP, php_free)
            if php_to_spend < 10:
                log_trade("SKIP", {"symbol": SYMBOL, "signal": signal,
                                    "reason": "Insufficient PHP balance",
                                    "php_free": php_free})
                return jsonify({"status": "skipped",
                                "reason": f"Insufficient PHP balance: ₱{php_free:.2f}"})

            # Limit price: 0.5% below current (safer entry)
            limit_price = round(price * 0.995, 8)
            quantity    = round(php_to_spend / limit_price, 0)  # whole BONK units

            if quantity < 1:
                return jsonify({"status": "skipped", "reason": "Quantity too small"})

            order = place_limit_order("BUY", str(int(quantity)), f"{limit_price:.8f}")
            log_trade("BUY", {
                "symbol": SYMBOL, "quantity": quantity,
                "limit_price": limit_price, "php_spent": php_to_spend,
                "order_id": order.get("orderId"), "reason": sig["reason"]
            })
            return jsonify({
                "status": "order_placed", "side": "BUY",
                "symbol": SYMBOL, "quantity": int(quantity),
                "limit_price": limit_price, "php_value": round(quantity * limit_price, 2),
                "order_id": order.get("orderId"),
                "signal": signal, "strength": strength, "reason": sig["reason"]
            })

        elif signal == "SELL":
            # Sell up to what MAX_TRADE_PHP worth of BONK
            max_bonk_to_sell = min(bonk_free, MAX_TRADE_PHP / price)
            quantity = round(max_bonk_to_sell, 0)

            if quantity < 1 or bonk_free < 1:
                log_trade("SKIP", {"symbol": SYMBOL, "signal": signal,
                                    "reason": "Insufficient BONK balance",
                                    "bonk_free": bonk_free})
                return jsonify({"status": "skipped",
                                "reason": f"Insufficient BONK balance: {bonk_free:.0f}"})

            # Limit price: 0.5% above current (safer exit)
            limit_price = round(price * 1.005, 8)
            order = place_limit_order("SELL", str(int(quantity)), f"{limit_price:.8f}")
            log_trade("SELL", {
                "symbol": SYMBOL, "quantity": quantity,
                "limit_price": limit_price,
                "php_value": round(quantity * limit_price, 2),
                "order_id": order.get("orderId"), "reason": sig["reason"]
            })
            return jsonify({
                "status": "order_placed", "side": "SELL",
                "symbol": SYMBOL, "quantity": int(quantity),
                "limit_price": limit_price, "php_value": round(quantity * limit_price, 2),
                "order_id": order.get("orderId"),
                "signal": signal, "strength": strength, "reason": sig["reason"]
            })

    except Exception as e:
        log_trade("ERROR", {"symbol": SYMBOL, "error": str(e)})
        return jsonify({"error": str(e)}), 500

# ── Open Orders ───────────────────────────────────────────────────────────────
@app.route("/orders/open")
def open_orders():
    try:
        orders = fetch_open_orders()
        return jsonify({"orders": orders, "count": len(orders)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Cancel Order ──────────────────────────────────────────────────────────────
@app.route("/orders/cancel/<order_id>", methods=["DELETE"])
def cancel(order_id: str):
    try:
        result = cancel_order(order_id)
        log_trade("CANCEL", {"order_id": order_id})
        return jsonify({"status": "cancelled", "order_id": order_id, "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Trade Log ─────────────────────────────────────────────────────────────────
@app.route("/trade/log")
def get_trade_log():
    return jsonify({"log": trade_log, "count": len(trade_log)})

# ── Trade Status ──────────────────────────────────────────────────────────────
@app.route("/trade/status")
def trade_status():
    return jsonify({
        "trade_enabled": TRADE_ENABLED,
        "symbol": SYMBOL,
        "max_trade_php": MAX_TRADE_PHP,
        "log_count": len(trade_log)
    })

# ── Ping ──────────────────────────────────────────────────────────────────────
@app.route("/ping")
def ping():
    return jsonify({"pong": True, "ts": int(time.time())})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
