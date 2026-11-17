#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-11 10:14 WIB - LEG 4 RECOVERY (prio re-read +
bridge/discards). The consolidated run was killed by the 170s timeout during
leg 4 (shape-check of 9 new feed contracts ate ~135s). Legs 1-3 + seen update
already done. Read-only except own hot-leg state files."""
import json, time, subprocess
from Crypto.Hash import keccak
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP_NODE = "https://bsc.nodereal.io/"
EP_DATA = "https://bsc-dataseed.binance.org/"
T0 = time.time()
NOW_ISO = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")

def curl_json_post(url, payload, timeout):
    pr = subprocess.run(["curl", "-s", "--max-time", str(timeout), "-X", "POST", url,
                         "-H", "Content-Type: application/json", "--data", payload],
                        capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(pr.stdout)

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

block = None
for ep in (EP_NODE, EP_DATA):
    try:
        block = int(curl_json_post(ep, '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}', 10)["result"], 16)
        break
    except Exception:
        continue

out = {}
chunk_notes = []
for i in range(0, len(jobs), 25):
    chunk = jobs[i:i+25]
    payload = json.dumps([{"jsonrpc": "2.0", "id": j, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for j, (_, _, to, data) in enumerate(chunk)])
    resps = []
    for ep in (EP_NODE, EP_DATA):
        try:
            resps = curl_json_post(ep, payload, 20)
            if resps:
                break
        except Exception:
            resps = []
    if isinstance(resps, dict):
        resps = [resps]
    if not resps:
        chunk_notes.append(f"chunk {i//25+1}: EMPTY on both RPCs")
    for (name, fname, addr, _), r in zip(chunk, resps):
        raw = r.get("result") if isinstance(r, dict) else None
        val = None
        if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 66:
            try: val = int(raw[:66], 16)
            except Exception: val = None
        out.setdefault(name, {})[fname] = val

json.dump({"block": block, "values": out},
          open(BASE + "hot-leg-run-2026-11-11-1014-prio.json", "w"), indent=1)

prev = json.load(open(BASE + "hot-leg-run-2026-11-11-0959-prio.json"))
prev_vals = prev.get("values", {})
diffs = []
for name, vals in out.items():
    for f, v in vals.items():
        old = prev_vals.get(name, {}).get(f)
        if old != v:
            diffs.append({"item": name, "field": f, "old": old, "new": v})

# ---- Bridge (read-only) + discards check (same as consolidated script) ----
bridge_note = ""
try:
    br = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = br.get("contracts", {})
    shape = json.load(open(BASE + "hot-leg-2026-11-11-1014-shape.json"))
    NEW = [s["address"] for s in shape["shapes"]]
    in_bridge_new = [a for a in NEW if a.lower() in {k.lower() for k in bcontracts}]
    discarded_n = sum(1 for v in bcontracts.values() if isinstance(v, dict) and v.get("same_owner_discarded"))
    bridge_note = (f"scan-bridge.json read ({len(bcontracts)} contracts, "
                   f"{discarded_n} same_owner_discarded; new feed contracts in bridge: {in_bridge_new or 'none'})")
except Exception as e:
    bridge_note = f"scan-bridge.json unreadable: {type(e).__name__} - skipped, run continues"
try:
    discards = json.load(open(BASE + "same-owner-discards.json"))
    dc = {str(e.get("contract", "")).lower() for e in discards if isinstance(e, dict)}
    dc |= {str(e).lower() for e in discards if isinstance(e, str)}
    shape = json.load(open(BASE + "hot-leg-2026-11-11-1014-shape.json"))
    NEW = [s["address"] for s in shape["shapes"]]
    in_discards = [a for a in NEW + ["0xDDc2352d1ceC10b42e05A297232f5328902C6c2C"] if a.lower() in dc]
except Exception:
    in_discards = []
bridge_note += f"; new contracts + SHINE in same-owner-discards.json: {in_discards or 'none'}"

shape = json.load(open(BASE + "hot-leg-2026-11-11-1014-shape.json"))
seen = json.load(open(BASE + "hot-leg-seen.json"))
result = {"run": "2026-11-11 10:14 WIB", "legs": {
  "sourcify_feed": "feed HTTP 200; 20 contracts, verifiedAt 2026-11-11T03:10:27Z..2026-11-11T02:40:54Z; 9 new, 0 excluded hit. S1_PASS=[] S2_PASS=[] EARLY_SHAPE=[]. Recorded in hot-leg-seen.json (total %d)." % len(seen),
  "boltbook": "EN FAILED rc=0 0 bytes (10th consecutive EN outage run); ZH HTTP 200 45887 bytes, 10 addr, 0 new vs seen+snap after update. BB_NEW=none new (5 ZH addrs added to seen as checked-not-sale-shape).",
  "leg4_priority_reread": f"block {block} vs 0959-prio baseline block {prev.get('block')}; {len(diffs)} diffs: {diffs}; chunk notes: {chunk_notes or 'none'}",
  "bridge": bridge_note,
  "execution": "NONE - no preview, no mint, no claim. No candidate met execution rules.",
  "recovery_note": "Consolidated run hit the 170s timeout during leg 4 (shape-check of 9 new feed contracts took ~135s); legs 1-3 + seen update had completed. This recovery script ran leg 4 + bridge only."
 },
 "report": "SILENT - no new lead, candidate, pending claim, change, or blocked auto-mint to report to main chat (pending diff review below).",
 "duration_sec_recovery": round(time.time() - T0, 1)}
json.dump(result, open(BASE + "hot-leg-run-2026-11-11-1014.json", "w"), indent=1)
print(json.dumps(result, indent=1))
print("PRIO VALUES:", json.dumps(out))
print("DIFFS:", json.dumps(diffs, indent=1))
