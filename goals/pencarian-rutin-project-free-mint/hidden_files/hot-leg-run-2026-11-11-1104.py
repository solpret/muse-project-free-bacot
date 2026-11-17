#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-11 11:04 WIB - lean pattern (same as 1054 run).
Leg 1 Sourcify feed + shape-check genuinely new contracts only.
Leg 2 Boltbook EN+ZH. Leg 3 retry 0xddf252ad ABI + re-read Bot Fighters 0x58a7.
Leg 4 priority re-read vs 1059-prio baseline.
Read-only except own hot-leg state files. No preview/mint, no chain scan.
Skip any leg that stalls; target <2 min."""
import json, time, subprocess, re, os
from Crypto.Hash import keccak
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc.nodereal.io/"
EP2 = "https://bsc-dataseed.binance.org/"
T0 = time.time()
NOW_ISO = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
RUN = "2026-11-11 11:04 WIB"
STAMP = "2026-11-11-1104"

def curl(url, timeout=20, post=None, ep=None):
    cmd = ["curl", "-s", "--max-time", str(timeout)]
    if post is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "--data", post]
    cmd.append(ep or url)
    pr = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
    return pr.stdout, pr.returncode

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def batch_call(addr, datas, timeout=25):
    calls = [{"jsonrpc": "2.0", "id": i+1, "method": "eth_call",
              "params": [{"to": addr, "data": d}, "latest"]} for i, (_, d) in enumerate(datas)]
    payload = json.dumps(calls)
    for ep in (EP, EP2):
        try:
            out, rc = curl(None, timeout, post=payload, ep=ep)
            resps = json.loads(out)
            if isinstance(resps, dict): resps = [resps]
            if len(resps) != len(calls): continue
            outd = {}
            for (key, _), r in zip(datas, resps):
                outd[key] = r.get("result") if isinstance(r, dict) and "error" not in r else None
            return outd
        except Exception:
            continue
    return None

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

REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F".lower()
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed",
              "freeMinted","freePoolRemaining"]
def shape_check(addr):
    try:
        out, rc = curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", 20)
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

s1_pass, s2_pass, early_shape = [], [], []
shapes = {}
# Retry the one abi-timeout contract from 1034 (0xddf252ad, Boltbook ZH).
retry_addrs = [a for a, v in seen.items()
               if isinstance(v, dict) and v.get("status") == "abi-timeout-retry-next-run"]
for a in retry_addrs:
    r = shape_check(a)
    shapes[a] = r
    if r.get("S1"): s1_pass.append(a)
    if r.get("S2"): s2_pass.append(a)
    if r.get("early_shape") and not r.get("S1") and not r.get("S2"): early_shape.append(a)
    st = "abi-timeout-retry-next-run" if "error" in r else (
        "S1-sale-shape" if r.get("S1") else "S2-sale-shape" if r.get("S2") else
        "early-shape-noted-main-job-scan-leg-owns-early-detection" if r.get("early_shape")
        else "checked-not-sale-shape")
    seen[a] = {"first_seen": seen[a].get("first_seen", NOW_ISO), "source": seen[a].get("source", "sourcify-feed"),
               "status": st,
               "note": f"retry 1104: S1={r.get('S1')} S2={r.get('S2')} mint={r.get('mint')} quote={r.get('quote')} free={r.get('free')} agent={r.get('agent')} token={r.get('token')} err={r.get('error')}"}
for a in new_feed:
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
# Shape-check genuinely new Boltbook addresses in-run (body leg 2: a mention
# carrying a full contract address is a lead to shape-check under leg 1).
bb_shapes = {}
for lang in ("en", "zh"):
    for a in bb.get(lang, {}).get("new", []):
        r = shape_check(a)
        bb_shapes[a] = r
        if r.get("S1"): s1_pass.append(a)
        if r.get("S2"): s2_pass.append(a)
        if r.get("early_shape") and not r.get("S1") and not r.get("S2"): early_shape.append(a)
        st = "abi-timeout-retry-next-run" if "error" in r else (
            "S1-sale-shape" if r.get("S1") else "S2-sale-shape" if r.get("S2") else
            "early-shape-noted-main-job-scan-leg-owns-early-detection" if r.get("early_shape")
            else "checked-not-sale-shape")
        seen[a] = {"first_seen": NOW_ISO, "source": f"boltbook-{lang}",
                   "status": st,
                   "note": f"boltbook-shape 1104: S1={r.get('S1')} S2={r.get('S2')} mint={r.get('mint')} quote={r.get('quote')} free={r.get('free')} agent={r.get('agent')} token={r.get('token')} err={r.get('error')}"}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---------- Leg 3: re-read Bot Fighters 0x58a7 (age still unverified; state only) ----------
NEW_S1 = "0x58a704d9e02FE11c0A61683AE7F606E4366F13eb"
verify58 = {}
views58 = [
    ("freeMinted", sel("freeMinted()")), ("totalSupply", sel("totalSupply()")),
    ("paidMinted", sel("paidMinted()")), ("paused", sel("paused()")),
    ("walletFreeUsed_user", sel("walletFreeUsed(address)") + enc_addr(USER)),
    ("balanceOf_user", sel("balanceOf(address)") + enc_addr(USER)),
]
raw58 = batch_call(NEW_S1, views58, timeout=25)
if raw58:
    for k, v in raw58.items():
        verify58[k] = to_int(v)
json.dump(verify58, open(BASE + f"hot-leg-{STAMP}-verify-58a7.json", "w"), indent=1)

# ---------- Leg 4: priority re-read vs 1059-prio baseline ----------
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
 "YAMA": ("0x86D779fc4d83044cCECCb53639f9a98E367D6E46", [
    ("totalFreeShares", "totalFreeShares()"), ("totalShares", "totalShares()")]),
}
jobs = []
for name, (addr, fields) in PRIO.items():
    for fname, sig in fields:
        data = sel(sig) + enc_addr(USER) if sig.endswith("(address)") else sel(sig)
        jobs.append((name, fname, addr, data))

def curl_post(payload, timeout=25, ep=EP):
    pr = subprocess.run(["curl", "-s", "--max-time", str(timeout), "-X", "POST", ep,
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
    resps = []
    for ep in (EP, EP2):
        try:
            resps = curl_post(payload, 25, ep)
            if isinstance(resps, list) and len(resps) == len(chunk):
                break
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

prev = json.load(open(BASE + "hot-leg-run-2026-11-11-1059-prio.json"))
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
                    f"{len(feed_addrs)} contracts; {len(new_feed)} new; "
                    f"retried abi-timeout {retry_addrs}; "
                    f"S1_PASS={s1_pass} S2_PASS={s2_pass} EARLY_SHAPE={early_shape}; shapes: {shapes}"),
  "boltbook": json.dumps(bb) + f"; boltbook-new-shape-check: {bb_shapes}",
  "verify_58a7": json.dumps(verify58),
  "leg4_priority_reread": f"block {block} vs 1059-prio baseline block {prev.get('block')}; {len(diffs)} diffs: {diffs}",
  "bridge": bridge_note,
  "execution": "NONE this leg - no new strong lead / track-C lead; no preview/mint/claim."
 },
 "report": "SILENT unless a diff above is a promotion/change/blocked item, or a new S1/S2 lead appears.",
 "duration_sec": round(time.time() - T0, 1)}
json.dump(result, open(BASE + f"hot-leg-run-{STAMP}.json", "w"), indent=1)
print(json.dumps(result, indent=1))
print("PRIO VALUES:", json.dumps(out))
print("VERIFY58:", json.dumps(verify58))
