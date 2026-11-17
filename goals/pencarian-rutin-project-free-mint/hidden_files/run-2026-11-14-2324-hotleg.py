#!/usr/bin/env python3
"""Hot-leg run 2026-11-14 23:24 WIB. Light: Sourcify feed + Boltbook EN/ZH + shape-check
new contracts only + binanceai pending-claim re-read (batch). Read-only except
hot-leg-seen.json (own file). No preview/mint. Timeouts short; skip leg on stall."""
import json, re, subprocess, time, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
SEEN_P = BASE + "hot-leg-seen.json"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
t0 = time.time()
out = {"run": "hot-leg 2026-11-14 23:24 WIB", "legs": {}, "new_contracts": [], "changes": []}

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def addrs(text):
    return set(a for a in re.findall(r"0x[a-fA-F0-9]{40}", text))

# Leg 1: Sourcify feed
try:
    feed = json.loads(fetch("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 20))
    items = feed if isinstance(feed, list) else feed.get("results", [])
    feed_addrs = [it.get("address") for it in items if it.get("address")]
    out["legs"]["sourcify"] = {"ok": True, "count": len(feed_addrs),
                               "addrs": feed_addrs}
except Exception as e:
    out["legs"]["sourcify"] = {"ok": False, "error": str(e)[:120]}
    feed_addrs = []

# Leg 2: Boltbook EN + ZH
bb_addrs = set()
for lang, url in (("en", "https://boltbook.fun/?lang=en"),
                  ("zh", "https://boltbook.fun/?lang=zh")):
    try:
        html = fetch(url, 20)
        a = addrs(html)
        bb_addrs |= a
        out["legs"][f"boltbook-{lang}"] = {"ok": True, "bytes": len(html), "addrs": len(a)}
        open(BASE + f"run-2026-11-14-2324-boltbook-{lang}.html", "w").write(html)
    except Exception as e:
        out["legs"][f"boltbook-{lang}"] = {"ok": False, "error": str(e)[:120]}
out["legs"]["boltbook-addrs"] = sorted(bb_addrs)

# Seen (keys only)
seen = json.load(open(SEEN_P))
seen_keys = {k.lower() for k in seen}
new = [a for a in (feed_addrs + sorted(bb_addrs))
       if a.lower() not in seen_keys and a.lower() not in EXCLUDED]
new = list(dict.fromkeys(new))
out["new_contracts"] = new

# Shape-check new contracts via Sourcify ABI
FREE_VIEWS = {"freesharesremaining", "freeclaimed", "freefor", "freeleft",
              "freeused", "freeavailable", "freesharepoolexhausted",
              "freesharesclaimed", "freeminted", "freeremaining"}
for addr in new:
    info = {"address": addr}
    try:
        data = json.loads(fetch(
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,metadata", 20))
        abi = data.get("abi") or []
        fns = [f.get("name", "").lower() for f in abi if f.get("type") == "function"]
        has_mint = any("mint" in f or "claim" in f for f in fns)
        has_quote = any("quote" in f or "cost" in f or "price" in f for f in fns)
        free = [f for f in fns if f in FREE_VIEWS]
        meta = json.dumps(data.get("metadata") or data)
        agent = REG in meta.lower() or "agentgate" in meta.lower() or \
            any("agent" in f for f in fns)
        s1 = has_mint and has_quote and bool(free) and agent
        s2 = ("mintfree" in fns or "claimfree" in fns) and bool(free) and agent
        info.update({"S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote,
                     "free": free, "agent": agent, "n_fns": len(fns),
                     "status": "sale-shape" if (s1 or s2) else "checked-not-sale-shape"})
    except Exception as e:
        info.update({"status": "shape-check-failed", "error": str(e)[:120]})
    seen[addr] = {"first_seen_wib": "2026-11-14T23:24:00+07:00",
                  "source": "hot-leg-2324", "status": info["status"],
                  "note": json.dumps(info)[:500]}
    out.setdefault("shape", []).append(info)

if new:
    json.dump(seen, open(SEEN_P, "w"), indent=1)

# Leg 4: binanceai pending-claim re-read only (other focus items read 23:04, ~15 min
# ago, all far from 50%/70% thresholds with velocity ~0 / age unverified / gate failed;
# main job 23:01 verdict DIAM, 0 baru)
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
calls = []
views = [("launched", "launched()", []), ("failed", "failed()", []),
         ("isRefundPhase", "isRefundPhase()", []),
         ("totalShares", "totalShares()", []),
         ("tokenClaimed_user", "tokenClaimed(address)", [USER])]
for i, (key, sig, args) in enumerate(views):
    d = sel(sig)
    for a in args:
        d += enc_addr(a) if isinstance(a, str) else format(int(a), "064x")
    calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                  "params": [{"to": "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
                              "data": d}, "latest"]})
blk = None
for ep in ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]:
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "30", "-X", "POST", ep,
                            "-H", "Content-Type: application/json",
                            "-d", json.dumps(calls)],
                           capture_output=True, text=True, timeout=40).stdout
        res = json.loads(r)
        if isinstance(res, list) and len(res) == len(calls):
            vals = {}
            for (key, _, _), it in zip(views, res):
                vals[key] = to_int(it.get("result")) if isinstance(it, dict) and "result" in it else None
            out["legs"]["binanceai"] = {"ok": True, "ep": ep, "views": vals}
            break
    except Exception as e:
        out["legs"]["binanceai"] = {"ok": False, "error": str(e)[:120]}
else:
    out["legs"]["binanceai"] = {"ok": False, "error": "all endpoints failed"}
try:
    r = subprocess.run(["curl", "-sL", "--max-time", "20", "-X", "POST",
                        "https://bsc-dataseed.binance.org/",
                        "-H", "Content-Type: application/json",
                        "-d", '{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}'],
                       capture_output=True, text=True, timeout=30).stdout
    blk = int(json.loads(r)["result"], 16)
except Exception:
    pass
out["block"] = blk
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-14-2324-hotleg.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:3000])
print("ELAPSED", out["elapsed_s"])
