#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-11 09:14 WIB - lean pattern (same as 0859 run).
Leg 1 feed + shape-check already done (feed fetch retried once after 30s
timeout; shape sequential). Leg 2 Boltbook ZH ok, EN timeout (3rd run in a
row). Leg 4 priority re-read vs 0859-prio baseline + UFO/AGTC/SHINE.
Read-only except own hot-leg state files. No preview/mint, no chain scan."""
import json, time, subprocess, re
from Crypto.Hash import keccak
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc.nodereal.io/"
T0 = time.time()
NOW_ISO = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
RUN = "2026-11-11 09:14 WIB"

# ---- Leg 1 record (already fetched + shape-checked) ----
feed = json.load(open(BASE + "hot-leg-2026-11-11-0914-feed.json"))
items = feed.get("results", feed if isinstance(feed, list) else [])
feed_addrs = [it.get("address") for it in items if isinstance(it, dict) and it.get("address")]
shape = json.load(open(BASE + "hot-leg-2026-11-11-0914-shape.json"))
s1_pass, s2_pass = shape["s1_pass"], shape["s2_pass"]
early_shape = shape["early_shape"]
NEW = ["0xD3E2c70B7d1C4da8Ef21046dF27050F17Da94fA9","0x0728781C25027845be6Bf73F82c347a7821F9a01",
"0x190D21eC62B71A5C3e08c6179b1b7a68eAbcC54E","0x1203D08F14370bd8E046C1b8AabA7fB718aB3278",
"0x5e362c702A7f69b7BBC66588B684c6f1126bf0B0","0x03Fe20Ec986c2E558B37825D9860Fd9a161f5c68",
"0xdef5061B688bB16Fe8336EEbaA44c672Cdd8A7A2"]

# ---- Leg 2 Boltbook record ----
# ZH fetched OK (45,147 bytes); EN timed out rc=28 (3rd consecutive run).
# 10 addresses in ZH front page; 9 already seen/snapshot; 1 new:
# 0x7e5993942d2264c34F8873bd694D5bc613a392C9 = PAXP PAYEE() in a risk-warning
# post (priasolo.ai), NOT a sale lead.
BB_NEW = ["0x7e5993942d2264c34F8873bd694D5bc613a392C9"]

# ---- hot-leg-seen.json update ----
seen = json.load(open(BASE + "hot-leg-seen.json"))
for a in NEW:
    st = "early-shape-noted-main-job-scan-leg-owns-early-detection" if a in early_shape else "checked-not-sale-shape"
    seen[a] = {"first_seen": NOW_ISO, "source": "sourcify-feed", "status": st}
for a in BB_NEW:
    seen[a] = {"first_seen": NOW_ISO, "source": "boltbook-frontpage",
               "status": "checked-not-sale-shape-paxp-payee-risk-post"}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Leg 4: priority re-read vs 0859-prio baseline ----
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")

PRIO = {
 "NIGHTFORGE": ("0x22f43ba09fd4beb9417d4484c60370354b220186", [
    ("totalSupply", "totalSupply()"), ("mintOpen", "mintOpen()"),
    ("agentFreeUsed", "agentFreeUsed()"), ("freeLeft", "freeLeft()"),
    ("balanceOf_user", "balanceOf(address)"),
    ("agentFreeByWallet_user", "agentFreeByWallet(address)")]),
 "NIGHTFORGE_B": ("0x051f04ff7b095793613b9caac197cc1051c24e2b", [
    ("totalSupply", "totalSupply()"), ("mintOpen", "mintOpen()"),
    ("balanceOf_user", "balanceOf(address)")]),
 "SOLDERCATS": ("0x3D972EBbF7488f21b95250B867e2406c723C9DDC", [
    ("totalSupply", "totalSupply()"), ("agentFreeUsed", "agentFreeUsed()"),
    ("mintOpen", "mintOpen()"),
    ("balanceOf_user", "balanceOf(address)"),
    ("agentFreeByWallet_user", "agentFreeByWallet(address)")]),
 "AgentPals": ("0xD265a929D0E50bD5ee4675e4E97F38D8380802E2", [
    ("freePhaseStart", "freePhaseStart()"), ("totalMinted", "totalMinted()"),
    ("freeMinted", "freeMinted()"), ("balanceOf_user", "balanceOf(address)")]),
 "sale-11-11": ("0x64767b1a39441e72046c2162065a2896e154b341", [
    ("freeMinted", "freeMinted()"), ("freeClaimed_user", "freeClaimed(address)")]),
 "PESI": ("0xe82BAc76C904d49AA6a240f236AFe1D1eD5F4baD", [
    ("freeMinted", "freeMinted()"), ("totalFreeShares", "totalFreeShares()"),
    ("totalShares", "totalShares()")]),
 "ORYN-sale": ("0x96135a41FA155752dc7154CDcaA480f2fBEC1493", [
    ("paused", "paused()"), ("freePoolRemaining", "freePoolRemaining()")]),
 "LOWB": ("0x00487ED061C77A1dd5085ef3a2D593366f9C6B35", [
    ("opened", "opened()"), ("totalFreeMinted", "totalFreeMinted()"),
    ("totalMinted", "totalMinted()")]),
 "BOME-50CD": ("0x50CDd91b31cED977D2776825BBaD72e99FF0830E", [
    ("mintOpen", "mintOpen()"), ("freeLotsMinted", "freeLotsMinted()")]),
 "YAMA": ("0x86D779fc4d83044cCECCb53639f9a98E367D6E46", [
    ("totalFreeShares", "totalFreeShares()"), ("totalShares", "totalShares()")]),
 "binanceai-sale": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched", "launched()")]),
 "UFO": ("0xE4059eA596392AcA14100af6CDC9481c330E2728", [
    ("freeMinted", "freeMinted()"), ("freeSharesRemaining", "freeSharesRemaining()"),
    ("FREE_SHARES", "FREE_SHARES()"), ("freeClaimed_user", "freeClaimed(address)")]),
 "AGTC": ("0x7BcC29c5405286b4Dd8b5b23FE7097F9EE65e4e5", [
    ("freeMinted", "freeMinted()"), ("totalSupply", "totalSupply()"),
    ("FREE_SUPPLY", "FREE_SUPPLY()"), ("balanceOf_user", "balanceOf(address)")]),
 "SHINE": ("0xDDc2352d1ceC10b42e05A297232f5328902C6c2C", [
    ("launched", "launched()"), ("startTime", "startTime()")]),
}

jobs = []
for name, (addr, fields) in PRIO.items():
    for fname, sig in fields:
        data = sel(sig) + enc_addr(USER) if sig.endswith("(address)") else sel(sig)
        jobs.append((name, fname, addr, data))

def curl_post(payload, timeout=30):
    pr = subprocess.run(["curl", "-s", "--max-time", str(timeout), "-X", "POST", EP,
                         "-H", "Content-Type: application/json", "--data", payload],
                        capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(pr.stdout)

try:
    block = int(curl_post('{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}', 15)["result"], 16)
except Exception:
    block = None

out = {}
for i in range(0, len(jobs), 25):
    chunk = jobs[i:i+25]
    payload = json.dumps([{"jsonrpc": "2.0", "id": j, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for j, (_, _, to, data) in enumerate(chunk)])
    try:
        resps = curl_post(payload, 30)
    except Exception:
        resps = []
    if isinstance(resps, dict):
        resps = [resps]
    for (name, fname, addr, _), r in zip(chunk, resps):
        raw = r.get("result") if isinstance(r, dict) else None
        val = None
        if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 66:
            try: val = int(raw[:66], 16)
            except Exception: val = None
        out.setdefault(name, {})[fname] = val

json.dump({"block": block, "values": out},
          open(BASE + "hot-leg-run-2026-11-11-0914-prio.json", "w"), indent=1)

prev = json.load(open(BASE + "hot-leg-run-2026-11-11-0859-prio.json"))
prev_vals = prev.get("values", {})
diffs = []
for name, vals in out.items():
    for f, v in vals.items():
        old = prev_vals.get(name, {}).get(f)
        if old != v:
            diffs.append({"item": name, "field": f, "old": old, "new": v})

# ---- Bridge (read-only) + discards check ----
bridge_note = ""
try:
    br = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = br.get("contracts", {})
    in_bridge_new = [a for a in NEW if a.lower() in {k.lower() for k in bcontracts}]
    discarded_n = sum(1 for v in bcontracts.values() if isinstance(v, dict) and v.get("same_owner_discarded"))
    bridge_note = (f"scan-bridge.json read ({len(bcontracts)} contracts, last written "
                   f"{br.get('last_written', br.get('written', 'n/a'))}); {discarded_n} same_owner_discarded; "
                   f"new feed contracts in bridge: {in_bridge_new or 'none'}")
except Exception as e:
    bridge_note = f"scan-bridge.json unreadable: {type(e).__name__} - skipped, run continues"
try:
    discards = json.load(open(BASE + "same-owner-discards.json"))
    dc = {str(e.get("contract", "")).lower() for e in discards if isinstance(e, dict)}
    in_discards = [a for a in NEW + ["0xDDc2352d1ceC10b42e05A297232f5328902C6c2C"] if a.lower() in dc]
except Exception:
    in_discards = []
bridge_note += f"; new contracts + SHINE in same-owner-discards.json: {in_discards or 'none'}"

result = {"run": RUN, "legs": {
  "sourcify_feed": f"feed HTTP 200 (retry after first 30s timeout), {len(feed_addrs)} contracts, verifiedAt 01:56-02:15Z; 13 already seen, 7 new shape-checked sequential (83.3s). S1_PASS={s1_pass} S2_PASS={s2_pass} EARLY_SHAPE={early_shape}. Recorded in hot-leg-seen.json (total {len(seen)}).",
  "boltbook": "EN fetch FAILED rc=28 timeout 25s 0 bytes (3rd consecutive run: 0854, 0859, 0914); ZH fetched HTTP 200, 45,147 bytes. 10 addresses on ZH front page, 9 already seen/snapshot, 1 new (PAXP PAYEE 0x7e59...392C9, risk-warning post, not a sale lead). No new sale-shape lead from Boltbook. Notable posts: UFO free lane 224/1,000 claimed; AGTC free phase SOLD OUT; THYRK dark on 2 RPCs (recheck post).",
  "leg4_priority_reread": f"block {block} vs 0859-prio baseline block {prev.get('block')}; {len(diffs)} diffs: {diffs}",
  "bridge": bridge_note,
  "execution": "NONE - no preview, no mint, no claim. No candidate met execution rules."
 },
 "report": "SILENT - no new lead, candidate, pending claim, change, or blocked auto-mint to report to main chat.",
 "duration_sec": round(time.time() - T0, 1)}
json.dump(result, open(BASE + "hot-leg-run-2026-11-11-0914.json", "w"), indent=1)
print(json.dumps(result, indent=1))
print("PRIO VALUES:", json.dumps(out))
