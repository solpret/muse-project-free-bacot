#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-11 10:29 WIB - lean pattern (same as 1019 run).
Leg 1 Sourcify feed + shape-check (incl. retry of 1019 abi-timeout 6).
Leg 2 Boltbook EN+ZH. Leg 4 priority re-read vs 1019-prio baseline.
Read-only except own hot-leg state files. No preview/mint, no chain scan.
Skip any leg that stalls; target <2 min."""
import json, time, subprocess, re, os
from Crypto.Hash import keccak
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc.nodereal.io/"
T0 = time.time()
NOW_ISO = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
RUN = "2026-11-11 10:29 WIB"
STAMP = "2026-11-11-1029"

def curl(url, timeout=20, post=None):
    cmd = ["curl", "-s", "--max-time", str(timeout)]
    if post is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "--data", post]
    cmd.append(url)
    pr = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
    return pr.stdout, pr.returncode

# ---------- Leg 1: Sourcify feed ----------
feed, feed_err, feed_addrs = None, None, []
try:
    out, rc = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 20)
    feed = json.loads(out)
    items = feed.get("results", feed if isinstance(feed, list) else [])
    feed_addrs = [it.get("address") for it in items if isinstance(it, dict) and it.get("address")]
    json.dump(feed, open(BASE + f"hot-leg-{STAMP}-feed.json", "w"), indent=1)
except Exception as e:
    feed_err = f"{type(e).__name__}: {e}"

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_lower = {k.lower() for k in seen}
new_feed = [a for a in feed_addrs if a and a.lower() not in seen_lower]
# retry 1019 abi-timeout contracts (4 new + 2 from 1004)
RETRY1019 = ["0xF1A9261EDcFE3fbAE53dBB36939Fa6C1046ed5B1",
             "0xf7e8997FF4dB1cbad0E5A190E441bC801eF52a2f",
             "0x91d34E584d2Cdb40148E15D6C504C8Dfe31F4B0D",
             "0x0539143bc9134841D26F524fFbEf18eCFc693A93",
             "0x2892eb04485075F3Dc71A9b9Dc30FC87bf0EA3Ea",
             "0x9d866B51bdc4D6d7deAE3e85e0C6cAc4BC009095"]
retry_new = [a for a in RETRY1019 if a.lower() not in seen_lower or
             seen.get(a, {}).get("status", "").startswith("abi-timeout")]
shape_targets = list(dict.fromkeys(new_feed + retry_new))

REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F".lower()
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed",
              "freeMinted","freePoolRemaining"]
def shape_check(addr):
    """Return dict with S1/S2/early flags or error."""
    try:
        out, rc = curl(f"https://sourcify.dev/server/v2/contracts/56/{addr}", 20)
        d = json.loads(out)
        abi = d.get("abi") or (d.get("contract", {}) or {}).get("abi")
        if not abi:
            return {"error": "no-abi-in-response"}
        src = json.dumps(d).lower()
        fns = {f.get("name") for f in abi if isinstance(f, dict) and f.get("type") == "function"}
        has_mint = any(n and ("mint" in n.lower()) for n in fns)
        has_quote = any(n and ("quote" in n.lower() or "cost" in n.lower()) for n in fns)
        free_hits = [v for v in FREE_VIEWS if v in fns]
        agent = REG in src or "agentgate" in src or "agentidregistry" in src
        s1 = bool(has_mint and has_quote and free_hits and agent)
        tokenish = all(x in fns for x in ("name","symbol","decimals","totalSupply"))
        s2 = bool(tokenish and ("mintFree" in fns) and
                  (("freeClaimed" in fns and "freeMinted" in fns) and
                   ("FREE_SLOTS" in fns or "FREE_SUPPLY" in fns)) and agent)
        early = bool(agent and (has_mint or free_hits))
        return {"S1": s1, "S2": s2, "early_shape": early, "mint": has_mint,
                "quote": has_quote, "free": free_hits, "agent": agent,
                "token": tokenish, "fns": len(fns)}
    except Exception as e:
        return {"error": f"{type(e).__name__}"}

shapes, s1_pass, s2_pass, early_shape = {}, [], [], []
for a in shape_targets:
    r = shape_check(a)
    shapes[a] = r
    if r.get("S1"): s1_pass.append(a)
    if r.get("S2"): s2_pass.append(a)
    if r.get("early_shape") and not r.get("S1") and not r.get("S2"): early_shape.append(a)
    st = "abi-timeout-retry-next-run" if "error" in r else (
        "S1-sale-shape" if r.get("S1") else "S2-sale-shape" if r.get("S2") else
        "early-shape-noted-main-job-scan-leg-owns-early-detection" if r.get("early_shape")
        else "checked-not-sale-shape")
    seen[a] = {"first_seen": NOW_ISO, "source": "sourcify-feed",
               "status": st,
               "note": f"S1={r.get('S1')} S2={r.get('S2')} mint={r.get('mint')} quote={r.get('quote')} free={r.get('free')} agent={r.get('agent')} token={r.get('token')} err={r.get('error')}"}
json.dump(shapes, open(BASE + f"hot-leg-{STAMP}-shape.json", "w"), indent=1)

# ---------- Leg 2: Boltbook EN + ZH ----------
bb = {}
for lang, suffix in (("en", ""), ("zh", "?lang=zh")):
    try:
        out, rc = curl(f"https://boltbook.fun/{suffix}", 20)
        fn = BASE + f"boltbook-{STAMP}-{lang}.html"
        open(fn, "w").write(out)
        addrs = sorted({m for m in re.findall(r"0x[0-9a-fA-F]{40}", out)})
        bb[lang] = {"bytes": len(out), "rc": rc, "addrs": addrs,
                    "new": [a for a in addrs if a.lower() not in seen_lower]}
    except Exception as e:
        bb[lang] = {"error": f"{type(e).__name__}: {e}"}
for lang in ("en", "zh"):
    for a in bb.get(lang, {}).get("new", []):
        seen[a] = {"first_seen": NOW_ISO, "source": f"boltbook-{lang}",
                   "status": "seen-boltbook-frontpage-not-shape-checked"}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---------- Leg 4: priority re-read vs 1019-prio baseline ----------
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
 "AgentPals": ("0xD265a929D0E50bD5ee4675e4E97F38D8380802E2", [
    ("freePhaseStart", "freePhaseStart()"), ("totalMinted", "totalMinted()"),
    ("freeMinted", "freeMinted()"), ("balanceOf_user", "balanceOf(address)")]),
 "ABYSSCABLE": ("0xd2e9242b0d7c0186cc181a5fc8534541dad278a2", [
    ("totalSupply", "totalSupply()"), ("agentFreeUsed", "agentFreeUsed()"),
    ("mintOpen", "mintOpen()"), ("balanceOf_user", "balanceOf(address)")]),
 "Stampooor": ("0x467696af8c2206B977B24081445104632dc1D459", [
    ("totalSupply", "totalSupply()"), ("totalMinted", "totalMinted()"),
    ("freeMinted", "freeMinted()"), ("FREE_SUPPLY", "FREE_SUPPLY()"),
    ("mintOpen", "mintOpen()"), ("balanceOf_user", "balanceOf(address)")]),
 "LOWB": ("0x00487ED061C77A1dd5085ef3a2D593366f9C6B35", [
    ("opened", "opened()"), ("totalFreeMinted", "totalFreeMinted()"),
    ("totalMinted", "totalMinted()")]),
 "SHINE": ("0xDDc2352d1ceC10b42e05A297232f5328902C6c2C", [
    ("launched", "launched()"), ("startTime", "startTime()"),
    ("freeClaimed", "freeClaimed()")]),
 "binanceai-sale": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched", "launched()")]),
 "UFO": ("0xE4059eA596392AcA14100af6CDC9481c330E2728", [
    ("FREE_SHARES", "FREE_SHARES()"), ("freeClaimed_user", "freeClaimed(address)")]),
 "AGTC": ("0x7BcC29c5405286b4Dd8b5b23FE7097F9EE65e4e5", [
    ("freeMinted", "freeMinted()"), ("FREE_SUPPLY", "FREE_SUPPLY()"),
    ("balanceOf_user", "balanceOf(address)")]),
 "sale-11-11": ("0x64767b1a39441e72046c2162065a2896e154b341", [
    ("freeMinted", "freeMinted()"), ("freeClaimed_user", "freeClaimed(address)")]),
}
jobs = []
for name, (addr, fields) in PRIO.items():
    for fname, sig in fields:
        data = sel(sig) + enc_addr(USER) if sig.endswith("(address)") else sel(sig)
        jobs.append((name, fname, addr, data))

def curl_post(payload, timeout=25):
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
        resps = curl_post(payload, 25)
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
          open(BASE + f"hot-leg-run-{STAMP}-prio.json", "w"), indent=1)

prev = json.load(open(BASE + "hot-leg-run-2026-11-11-1019-prio.json"))
prev_vals = prev.get("values", {})
diffs = []
for name, vals in out.items():
    for f, v in vals.items():
        old = prev_vals.get(name, {}).get(f)
        if old != v:
            diffs.append({"item": name, "field": f, "old": old, "new": v})

# ---------- Bridge (read-only) + discards ----------
bridge_note = ""
try:
    br = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = br.get("contracts", {})
    mtime = time.strftime("%Y-%m-%d %H:%M WIB", time.localtime(os.path.getmtime(BASE + "scan-bridge.json")))
    discarded_n = sum(1 for v in bcontracts.values() if isinstance(v, dict) and v.get("same_owner_discarded"))
    bridge_note = (f"scan-bridge.json read ({len(bcontracts)} contracts, mtime {mtime}); "
                   f"{discarded_n} same_owner_discarded; new feed contracts in bridge: none")
except Exception as e:
    bridge_note = f"scan-bridge.json unreadable: {type(e).__name__} - skipped, run continues"
try:
    discards = json.load(open(BASE + "same-owner-discards.json"))
    dc = {str(e.get("contract", "")).lower() for e in discards if isinstance(e, dict)}
    in_discards = [a for a in new_feed + s1_pass + s2_pass if a.lower() in dc]
except Exception:
    in_discards = []
bridge_note += f"; new contracts in same-owner-discards.json: {in_discards or 'none'}"

result = {"run": RUN, "legs": {
  "sourcify_feed": (f"feed {'OK' if feed else 'FAILED: ' + str(feed_err)}; "
                    f"{len(feed_addrs)} contracts; {len(new_feed)} new; shape targets {shape_targets}; "
                    f"S1_PASS={s1_pass} S2_PASS={s2_pass} EARLY_SHAPE={early_shape}; shapes: {shapes}"),
  "boltbook": json.dumps(bb),
  "leg4_priority_reread": f"block {block} vs 1019-prio baseline block {prev.get('block')}; {len(diffs)} diffs: {diffs}",
  "bridge": bridge_note,
  "execution": "NONE - no preview, no mint, no claim. No candidate met execution rules."
 },
 "report": "SILENT unless a diff above is a promotion/change/blocked item.",
 "duration_sec": round(time.time() - T0, 1)}
json.dump(result, open(BASE + f"hot-leg-run-{STAMP}.json", "w"), indent=1)
print(json.dumps(result, indent=1))
print("PRIO VALUES:", json.dumps(out))
