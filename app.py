<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>CoinsBot Monitor</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
<style>
  :root {
    --bg:     #020c10;
    --panel:  #040f15;
    --border: #0d3040;
    --accent: #00e5ff;
    --green:  #00ff88;
    --red:    #ff3355;
    --yellow: #ffd600;
    --dim:    #1a3a4a;
    --text:   #a0d8e8;
    --muted:  #2a5a70;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:var(--bg); color:var(--text); font-family:'Share Tech Mono',monospace; min-height:100vh; overflow-x:hidden; }
  body::before { content:''; position:fixed; inset:0; background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,229,255,0.012) 2px,rgba(0,229,255,0.012) 4px); pointer-events:none; z-index:9999; }
  body::after  { content:''; position:fixed; inset:0; background-image:linear-gradient(rgba(0,229,255,0.025) 1px,transparent 1px),linear-gradient(90deg,rgba(0,229,255,0.025) 1px,transparent 1px); background-size:40px 40px; pointer-events:none; z-index:0; }

  .wrap { position:relative; z-index:1; max-width:860px; margin:0 auto; padding:18px 14px 40px; }

  header { display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid var(--border); padding-bottom:14px; margin-bottom:20px; }
  .logo { font-family:'Orbitron',sans-serif; font-weight:900; font-size:1.25rem; color:var(--accent); letter-spacing:3px; text-shadow:0 0 24px rgba(0,229,255,0.5); }
  .logo span { color:var(--green); }
  .header-right { text-align:right; font-size:0.7rem; }
  #live-time { color:var(--accent); font-size:0.85rem; }
  .sub { color:var(--muted); margin-top:2px; letter-spacing:1px; }

  .banner { display:flex; align-items:center; gap:10px; background:var(--panel); border:1px solid var(--border); border-left:3px solid var(--green); padding:10px 16px; margin-bottom:20px; border-radius:2px; transition:border-left-color 0.4s; }
  .dot { width:9px; height:9px; border-radius:50%; background:var(--green); box-shadow:0 0 8px var(--green); flex-shrink:0; animation:blink 1.6s infinite; }
  .dot.off { background:var(--red); box-shadow:0 0 8px var(--red); animation:none; }
  @keyframes blink { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.4;transform:scale(0.8)} }
  .banner-label { font-family:'Orbitron',sans-serif; font-size:0.65rem; letter-spacing:2px; color:var(--green); }
  .banner-label.off { color:var(--red); }
  .banner-right { margin-left:auto; font-size:0.68rem; color:var(--muted); }
  #last-update { color:var(--accent); }

  .price-row { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:20px; }
  .pcard { background:var(--panel); border:1px solid var(--border); padding:18px 16px; border-radius:2px; position:relative; overflow:hidden; }
  .pcard::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg,var(--accent),transparent); }
  .pcard-pair { font-family:'Orbitron',sans-serif; font-size:0.6rem; letter-spacing:3px; color:var(--muted); margin-bottom:6px; }
  .pcard-price { font-family:'Orbitron',sans-serif; font-size:1.3rem; font-weight:700; color:var(--accent); text-shadow:0 0 14px rgba(0,229,255,0.3); margin-bottom:5px; transition:color 0.35s; }
  .pcard-price.up   { color:var(--green); text-shadow:0 0 14px rgba(0,255,136,0.35); }
  .pcard-price.down { color:var(--red);   text-shadow:0 0 14px rgba(255,51,85,0.35); }
  .pcard-meta { display:flex; gap:14px; font-size:0.7rem; }
  .up-txt  { color:var(--green); }
  .dn-txt  { color:var(--red); }
  .neu-txt { color:var(--muted); }

  .balance-row { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-bottom:20px; }
  .bcard { background:var(--panel); border:1px solid var(--border); padding:12px 14px; border-radius:2px; }
  .bcard-label { font-family:'Orbitron',sans-serif; font-size:0.55rem; letter-spacing:3px; color:var(--muted); margin-bottom:5px; }
  .bcard-val { font-family:'Orbitron',sans-serif; font-size:0.95rem; font-weight:700; color:var(--accent); }
  .bcard-locked { font-size:0.65rem; color:var(--muted); margin-top:3px; }

  .sec-title { font-family:'Orbitron',sans-serif; font-size:0.6rem; letter-spacing:3px; color:var(--muted); margin-bottom:10px; display:flex; align-items:center; gap:8px; }
  .sec-title::after { content:''; flex:1; height:1px; background:var(--border); }

  /* ── AUTO-TRADE PANEL ── */
  .trade-panel {
    background:var(--panel); border:1px solid var(--border);
    border-left:3px solid var(--yellow);
    border-radius:2px; padding:16px 18px; margin-bottom:20px;
  }

  .trade-top { display:flex; align-items:center; justify-content:space-between; margin-bottom:14px; flex-wrap:wrap; gap:10px; }

  .trade-title { font-family:'Orbitron',sans-serif; font-size:0.7rem; letter-spacing:2px; color:var(--yellow); }

  .trade-config { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:14px; }

  .cfg-item { display:flex; flex-direction:column; gap:4px; }
  .cfg-label { font-size:0.6rem; color:var(--muted); letter-spacing:1px; }
  .cfg-input {
    background:#020c10; border:1px solid var(--border);
    color:var(--accent); font-family:'Share Tech Mono',monospace;
    font-size:0.8rem; padding:6px 10px; border-radius:2px;
    width:100%; outline:none;
    transition:border-color 0.2s;
  }
  .cfg-input:focus { border-color:var(--accent); }

  .trade-btns { display:flex; gap:10px; flex-wrap:wrap; }

  .btn {
    font-family:'Orbitron',sans-serif; font-size:0.6rem; letter-spacing:2px;
    padding:9px 16px; border-radius:2px; cursor:pointer;
    border:1px solid; transition:all 0.2s; flex:1; min-width:100px;
    text-align:center;
  }
  .btn-execute {
    background:rgba(0,255,136,0.08); color:var(--green);
    border-color:rgba(0,255,136,0.4);
  }
  .btn-execute:hover { background:rgba(0,255,136,0.18); box-shadow:0 0 12px rgba(0,255,136,0.2); }
  .btn-execute:disabled { opacity:0.4; cursor:not-allowed; }

  .btn-cancel-all {
    background:rgba(255,51,85,0.08); color:var(--red);
    border-color:rgba(255,51,85,0.3);
  }
  .btn-cancel-all:hover { background:rgba(255,51,85,0.18); }

  .btn-refresh {
    background:transparent; color:var(--accent);
    border-color:var(--border);
  }
  .btn-refresh:hover { border-color:var(--accent); }

  /* Trade result box */
  .trade-result {
    margin-top:12px; padding:10px 14px;
    background:#020c10; border:1px solid var(--border);
    border-radius:2px; font-size:0.72rem; display:none;
  }
  .trade-result.show { display:block; }
  .trade-result.ok   { border-left:3px solid var(--green); color:var(--green); }
  .trade-result.warn { border-left:3px solid var(--yellow); color:var(--yellow); }
  .trade-result.err  { border-left:3px solid var(--red);   color:var(--red); }

  /* Toggle switch */
  .toggle-wrap { display:flex; align-items:center; gap:10px; }
  .toggle-label { font-size:0.65rem; color:var(--muted); }

  .toggle {
    position:relative; display:inline-block;
    width:40px; height:20px;
  }
  .toggle input { opacity:0; width:0; height:0; }
  .slider {
    position:absolute; cursor:pointer; inset:0;
    background:var(--dim); border-radius:20px;
    transition:0.3s;
  }
  .slider:before {
    content:''; position:absolute;
    width:14px; height:14px; left:3px; bottom:3px;
    background:var(--muted); border-radius:50%; transition:0.3s;
  }
  input:checked + .slider { background:rgba(0,255,136,0.3); }
  input:checked + .slider:before { transform:translateX(20px); background:var(--green); }

  /* Signals */
  .signals-wrap { background:var(--panel); border:1px solid var(--border); border-radius:2px; margin-bottom:20px; overflow:hidden; }
  .sig-row { display:grid; grid-template-columns:80px 80px 1fr auto auto; align-items:center; gap:10px; padding:11px 16px; border-bottom:1px solid var(--dim); font-size:0.75rem; }
  .sig-row:last-child { border-bottom:none; }
  .sig-time   { color:var(--muted); font-size:0.68rem; }
  .sig-coin   { font-family:'Orbitron',sans-serif; font-size:0.62rem; letter-spacing:1px; }
  .sig-reason { color:var(--muted); font-size:0.68rem; }
  .sig-price  { color:var(--text); font-size:0.72rem; text-align:right; }
  .badge { font-family:'Orbitron',sans-serif; font-size:0.58rem; letter-spacing:2px; padding:3px 9px; border-radius:2px; min-width:48px; text-align:center; }
  .badge.BUY  { background:rgba(0,255,136,0.1); color:var(--green); border:1px solid rgba(0,255,136,0.3); }
  .badge.SELL { background:rgba(255,51,85,0.1);  color:var(--red);   border:1px solid rgba(255,51,85,0.3); }
  .badge.HOLD { background:rgba(255,214,0,0.08); color:var(--yellow);border:1px solid rgba(255,214,0,0.25); }

  /* Open orders */
  .orders-wrap { background:var(--panel); border:1px solid var(--border); border-radius:2px; margin-bottom:20px; overflow:hidden; }
  .order-row { display:grid; grid-template-columns:auto 1fr auto auto auto; align-items:center; gap:10px; padding:10px 16px; border-bottom:1px solid var(--dim); font-size:0.72rem; }
  .order-row:last-child { border-bottom:none; }
  .order-id { color:var(--muted); font-size:0.6rem; }
  .btn-cancel-order { font-family:'Orbitron',sans-serif; font-size:0.55rem; padding:3px 8px; border-radius:2px; background:rgba(255,51,85,0.08); color:var(--red); border:1px solid rgba(255,51,85,0.3); cursor:pointer; }
  .btn-cancel-order:hover { background:rgba(255,51,85,0.2); }
  .no-orders { padding:14px 16px; font-size:0.72rem; color:var(--muted); text-align:center; }

  /* Log */
  .log-wrap { background:var(--panel); border:1px solid var(--border); border-radius:2px; padding:12px 16px; max-height:160px; overflow-y:auto; }
  .log-wrap::-webkit-scrollbar { width:3px; }
  .log-wrap::-webkit-scrollbar-thumb { background:var(--muted); }
  .log-line { display:flex; gap:10px; font-size:0.68rem; padding:2px 0; border-bottom:1px solid rgba(13,48,64,0.3); }
  .log-ts  { color:var(--muted); flex-shrink:0; }
  .log-msg { color:var(--text); }
  .log-msg.ok   { color:var(--green); }
  .log-msg.warn { color:var(--yellow); }
  .log-msg.err  { color:var(--red); }

  footer { margin-top:28px; text-align:center; font-size:0.6rem; color:var(--muted); letter-spacing:2px; border-top:1px solid var(--border); padding-top:14px; }

  @media(max-width:540px){
    .price-row,.trade-config { grid-template-columns:1fr; }
    .balance-row { grid-template-columns:1fr 1fr; }
    .sig-row { grid-template-columns:70px 65px 1fr auto; }
    .sig-reason { display:none; }
    .order-row { grid-template-columns:1fr auto auto auto; }
    .order-id { display:none; }
  }
</style>
</head>
<body>
<div class="wrap">

  <header>
    <div class="logo">COINS<span>BOT</span></div>
    <div class="header-right">
      <div id="live-time">--:--:--</div>
      <div class="sub">PHST · COINS.PH</div>
    </div>
  </header>

  <!-- STATUS -->
  <div class="banner" id="banner">
    <div class="dot" id="dot"></div>
    <div class="banner-label" id="banner-label">CONNECTING...</div>
    <div class="banner-right">Last update: <span id="last-update">—</span></div>
  </div>

  <!-- PRICES -->
  <div class="price-row">
    <div class="pcard">
      <div class="pcard-pair">PEPE / PHP</div>
      <div class="pcard-price" id="pepe-price">₱—</div>
      <div class="pcard-meta"><span id="pepe-chg" class="neu-txt">—%</span><span id="pepe-src" class="neu-txt">—</span></div>
    </div>
    <div class="pcard">
      <div class="pcard-pair">BONK / PHP</div>
      <div class="pcard-price" id="bonk-price">₱—</div>
      <div class="pcard-meta"><span id="bonk-chg" class="neu-txt">—%</span><span id="bonk-src" class="neu-txt">—</span></div>
    </div>
  </div>

  <!-- BALANCE -->
  <div class="sec-title">WALLET BALANCE</div>
  <div class="balance-row">
    <div class="bcard">
      <div class="bcard-label">PHP</div>
      <div class="bcard-val" id="bal-php">—</div>
      <div class="bcard-locked" id="bal-php-lk">locked: —</div>
    </div>
    <div class="bcard">
      <div class="bcard-label">BONK</div>
      <div class="bcard-val" id="bal-bonk">—</div>
      <div class="bcard-locked" id="bal-bonk-lk">locked: —</div>
    </div>
    <div class="bcard">
      <div class="bcard-label">PEPE</div>
      <div class="bcard-val" id="bal-pepe">—</div>
      <div class="bcard-locked" id="bal-pepe-lk">locked: —</div>
    </div>
  </div>

  <!-- AUTO-TRADE PANEL -->
  <div class="sec-title">AUTO-TRADE · BONK/PHP</div>
  <div class="trade-panel">
    <div class="trade-top">
      <div class="trade-title">⚡ LIMIT ORDER EXECUTOR</div>
      <div class="toggle-wrap">
        <span class="toggle-label">AUTO</span>
        <label class="toggle">
          <input type="checkbox" id="auto-toggle" onchange="toggleAuto(this)">
          <span class="slider"></span>
        </label>
        <span class="toggle-label" id="auto-status-txt">OFF</span>
      </div>
    </div>

    <div class="trade-config">
      <div class="cfg-item">
        <span class="cfg-label">MAX TRADE (PHP)</span>
        <input class="cfg-input" id="cfg-max-php" type="number" value="200" min="10" step="10">
      </div>
      <div class="cfg-item">
        <span class="cfg-label">MIN SIGNAL STRENGTH</span>
        <select class="cfg-input" id="cfg-min-strength">
          <option value="STRONG">STRONG only</option>
          <option value="MODERATE" selected>MODERATE+</option>
        </select>
      </div>
    </div>

    <div class="trade-btns">
      <button class="btn btn-execute" id="btn-execute" onclick="executeTrade()">▶ EXECUTE NOW</button>
      <button class="btn btn-cancel-all" onclick="cancelAllOrders()">✕ CANCEL ALL ORDERS</button>
      <button class="btn btn-refresh" onclick="fetchAll()">⟳ REFRESH</button>
    </div>

    <div class="trade-result" id="trade-result"></div>
  </div>

  <!-- OPEN ORDERS -->
  <div class="sec-title">OPEN ORDERS</div>
  <div class="orders-wrap" id="orders-wrap">
    <div class="no-orders">No open orders</div>
  </div>

  <!-- SIGNALS -->
  <div class="sec-title">LIVE SIGNALS</div>
  <div class="signals-wrap" id="signals-wrap">
    <div class="sig-row">
      <span class="sig-time">--:--:--</span>
      <span class="sig-coin">——</span>
      <span class="sig-reason">Waiting for backend...</span>
      <span class="sig-price">—</span>
      <span class="badge HOLD">HOLD</span>
    </div>
  </div>

  <!-- LOG -->
  <div class="sec-title">ACTIVITY LOG</div>
  <div class="log-wrap" id="log-wrap"></div>

  <footer>COINSBOT MONITOR · BONK/PHP AUTO-TRADE · IMPASUGONG, BUKIDNON</footer>
</div>

<script>
const API = "https://coins-276f.onrender.com";
const REFRESH_MS = 30000;

const signals = [];
const logs    = [];
let prevPrices   = { pepe: null, bonk: null };
let autoInterval = null;
let autoEnabled  = false;

// ── Clock ─────────────────────────────────────────────────────────────────────
function tick() {
  document.getElementById("live-time").textContent =
    new Date().toLocaleTimeString("en-PH", { hour12: false });
}
setInterval(tick, 1000); tick();

// ── Log ───────────────────────────────────────────────────────────────────────
function log(msg, cls = "") {
  const ts = new Date().toLocaleTimeString("en-PH", { hour12: false });
  logs.unshift({ ts, msg, cls });
  if (logs.length > 50) logs.pop();
  document.getElementById("log-wrap").innerHTML =
    logs.map(l => `<div class="log-line"><span class="log-ts">[${l.ts}]</span><span class="log-msg ${l.cls}">${l.msg}</span></div>`).join("");
}

// ── Status ────────────────────────────────────────────────────────────────────
function setStatus(online, msg) {
  document.getElementById("dot").className        = online ? "dot" : "dot off";
  document.getElementById("banner-label").className = online ? "banner-label" : "banner-label off";
  document.getElementById("banner-label").textContent = msg;
  document.getElementById("banner").style.borderLeftColor = online ? "var(--green)" : "var(--red)";
}

// ── Prices ────────────────────────────────────────────────────────────────────
async function fetchPrices() {
  try {
    const data = await (await fetch(`${API}/prices`)).json();
    ["pepe","bonk"].forEach(coin => {
      const d = data[coin];
      if (!d || d.error) { log(`${coin.toUpperCase()} price error: ${d?.error}`, "err"); return; }
      const el  = document.getElementById(`${coin}-price`);
      const chg = d.change_pct;
      el.className = "pcard-price" + (prevPrices[coin] !== null ? (d.price_php > prevPrices[coin] ? " up" : d.price_php < prevPrices[coin] ? " down" : "") : "");
      prevPrices[coin] = d.price_php;
      el.textContent = "₱" + d.price_php.toFixed(8);
      const chgEl = document.getElementById(`${coin}-chg`);
      chgEl.className = chg >= 0 ? "up-txt" : "dn-txt";
      chgEl.textContent = (chg >= 0 ? "+" : "") + chg.toFixed(2) + "%";
      document.getElementById(`${coin}-src`).textContent = d.source;
    });
    document.getElementById("last-update").textContent = new Date().toLocaleTimeString("en-PH",{hour12:false});
    return true;
  } catch(e) { log("Price fetch failed: " + e.message, "err"); return false; }
}

// ── Balance ───────────────────────────────────────────────────────────────────
async function fetchBalance() {
  try {
    const data = await (await fetch(`${API}/balance`)).json();
    if (data.error) { log("Balance: " + data.error, "warn"); return; }
    const bal = data.balances || {};
    const fmt = v => v !== undefined ? v.toLocaleString("en-PH", {maximumFractionDigits:4}) : "—";
    ["PHP","BONK","PEPE"].forEach(asset => {
      const k = asset.toLowerCase();
      const b = bal[asset];
      const v = document.getElementById(`bal-${k}`);
      const l = document.getElementById(`bal-${k}-lk`);
      if(v) v.textContent = b ? fmt(b.free) : "—";
      if(l) l.textContent = b ? "locked: " + fmt(b.locked) : "locked: —";
    });
  } catch(e) { log("Balance fetch failed: " + e.message, "warn"); }
}

// ── Signals ───────────────────────────────────────────────────────────────────
async function fetchSignals() {
  for (const coin of ["pepe","bonk"]) {
    try {
      const data = await (await fetch(`${API}/signal/${coin}`)).json();
      if (data.error) { log(`${coin} signal: ${data.error}`, "err"); continue; }
      const ts = new Date().toLocaleTimeString("en-PH",{hour12:false});
      signals.unshift({ ts, coin: coin.toUpperCase()+"/PHP", reason: data.reason,
                        price: "₱"+data.price_php.toFixed(8), signal: data.signal, strength: data.strength });
    } catch(e) { log(`${coin} signal failed`, "err"); }
  }
  if (signals.length > 10) signals.splice(10);
  document.getElementById("signals-wrap").innerHTML =
    signals.length ? signals.map(s => `
      <div class="sig-row">
        <span class="sig-time">${s.ts}</span>
        <span class="sig-coin">${s.coin}</span>
        <span class="sig-reason">${s.reason}</span>
        <span class="sig-price">${s.price}</span>
        <span class="badge ${s.signal}">${s.signal}</span>
      </div>`).join("") :
    `<div class="sig-row"><span class="sig-time">—</span><span class="sig-coin">—</span><span class="sig-reason">Waiting...</span><span></span><span class="badge HOLD">HOLD</span></div>`;
}

// ── Open Orders ───────────────────────────────────────────────────────────────
async function fetchOpenOrders() {
  try {
    const data = await (await fetch(`${API}/orders/open`)).json();
    const orders = data.orders || [];
    const wrap   = document.getElementById("orders-wrap");
    if (!orders.length) {
      wrap.innerHTML = `<div class="no-orders">No open orders</div>`;
      return;
    }
    wrap.innerHTML = orders.map(o => `
      <div class="order-row">
        <span class="order-id">#${String(o.orderId).slice(-6)}</span>
        <span class="badge ${o.side}">${o.side}</span>
        <span>Qty: ${parseFloat(o.origQty).toLocaleString()}</span>
        <span>₱${parseFloat(o.price).toFixed(8)}</span>
        <button class="btn-cancel-order" onclick="cancelOne('${o.orderId}')">CANCEL</button>
      </div>`).join("");
    log(`${orders.length} open order(s)`, "warn");
  } catch(e) { log("Orders fetch failed: " + e.message, "warn"); }
}

// ── Execute Trade ─────────────────────────────────────────────────────────────
async function executeTrade() {
  const btn    = document.getElementById("btn-execute");
  const result = document.getElementById("trade-result");
  btn.disabled = true;
  btn.textContent = "EXECUTING...";
  result.className = "trade-result show warn";
  result.textContent = "Placing order...";

  try {
    const res  = await fetch(`${API}/trade/execute`, { method: "POST",
      headers: { "Content-Type": "application/json" } });
    const data = await res.json();

    if (data.error) {
      result.className = "trade-result show err";
      result.textContent = "❌ ERROR: " + data.error;
      log("Trade error: " + data.error, "err");
    } else if (data.status === "skipped") {
      result.className = "trade-result show warn";
      result.textContent = "⏸ SKIPPED: " + data.reason;
      log("Trade skipped: " + data.reason, "warn");
    } else if (data.status === "order_placed") {
      result.className = "trade-result show ok";
      result.textContent = `✅ ${data.side} ORDER PLACED — ${parseInt(data.quantity).toLocaleString()} BONK @ ₱${parseFloat(data.limit_price).toFixed(8)} (₱${data.php_value} total) | Order #${String(data.order_id).slice(-6)}`;
      log(`${data.side} order: ${parseInt(data.quantity).toLocaleString()} BONK @ ₱${parseFloat(data.limit_price).toFixed(8)}`, "ok");
      await fetchOpenOrders();
      await fetchBalance();
    }
  } catch(e) {
    result.className = "trade-result show err";
    result.textContent = "❌ FAILED: " + e.message;
    log("Execute failed: " + e.message, "err");
  }

  btn.disabled = false;
  btn.textContent = "▶ EXECUTE NOW";
}

// ── Cancel One ────────────────────────────────────────────────────────────────
async function cancelOne(orderId) {
  try {
    const data = await (await fetch(`${API}/orders/cancel/${orderId}`, { method: "DELETE" })).json();
    log(`Order #${String(orderId).slice(-6)} cancelled`, "ok");
    await fetchOpenOrders();
  } catch(e) { log("Cancel failed: " + e.message, "err"); }
}

// ── Cancel All ────────────────────────────────────────────────────────────────
async function cancelAllOrders() {
  try {
    const data   = await (await fetch(`${API}/orders/open`)).json();
    const orders = data.orders || [];
    if (!orders.length) { log("No open orders to cancel", "warn"); return; }
    for (const o of orders) await cancelOne(o.orderId);
    log(`Cancelled ${orders.length} order(s)`, "ok");
  } catch(e) { log("Cancel all failed: " + e.message, "err"); }
}

// ── Auto Toggle ───────────────────────────────────────────────────────────────
function toggleAuto(cb) {
  autoEnabled = cb.checked;
  document.getElementById("auto-status-txt").textContent = autoEnabled ? "ON" : "OFF";
  if (autoEnabled) {
    log("Auto-trade ENABLED — runs every 30s", "ok");
    autoInterval = setInterval(executeTrade, 30000);
  } else {
    log("Auto-trade DISABLED", "warn");
    clearInterval(autoInterval);
  }
}

// ── Fetch All ─────────────────────────────────────────────────────────────────
async function fetchAll() {
  setStatus(true, "FETCHING...");
  const ok = await fetchPrices();
  await fetchBalance();
  await fetchSignals();
  await fetchOpenOrders();
  setStatus(ok, ok ? "BOT ONLINE · COINS.PH" : "BACKEND OFFLINE");
}

// ── Init ──────────────────────────────────────────────────────────────────────
log("CoinsBot v3 Dashboard started", "ok");
log("Auto-trade: BONK/PHP limit orders");
fetchAll();
setInterval(fetchAll, REFRESH_MS);
</script>
</body>
</html>
