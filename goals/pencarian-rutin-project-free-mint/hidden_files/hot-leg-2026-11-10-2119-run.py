#!/usr/bin/env python3
"""Hot-leg run 2026-11-10 21:19 WIB.
Leg 1: Sourcify feed (limit 20) - shape-check 4 new contracts.
Leg 2: Boltbook front page EN + ZH (boltbook.fun) - already fetched to /tmp.
Leg 4 (priority): re-read BYTEBLOOM (near 25% strong-lead
threshold; 20:59 read: 445/2000 = 22.25%, ETA ~21:33 WIB). KERNELMONK
already minted 20:59, slot used - not re-read. Read-only. No preview/mint unless
a strong-lead threshold is crossed AND all guards pass (handled by parent).
"""
import json, subprocess, time, re
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-10-2119"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
RPCS = ["https://bsc.nodereal.io/", "https://bsc-dataseed.binance.org/",
        "https://bsc-dataseed1.binance.org/", "https://bsc.publicnode.com"]

def curl(url, max_time=25):
    p = subprocess.run(["curl", "-s", "--max-time", str(max_time), url],
                       capture_output=True, text=True)
    return p.stdout

# ---- Leg 1: feed (already saved to /tmp) ----
feed = json.load(open("/tmp/hotleg-feed-2119.json"))
json.dump(feed, open(BASE + TAG + "-feed.json", "w"), indent=1)
addrs = [r["address"] for r in feed.get("results", [])]
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
new_feed = [a for a in addrs if a.lower() not in seen_l]
print("FEED count:", len(addrs), "new:", new_feed)

# ---- Shape-check new feed contracts via Sourcify ABI ----
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeSupply", "freeSlots"]
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
shape = {}
for a in new_feed:
    try:
        raw = curl(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", 25)
        d = json.loads(raw)
        abi = d.get("abi") or []
        fns = [e.get("name", "") for e in abi if e.get("type") == "function"]
        src = json.dumps(d)[:2000].lower()
        mint = [f for f in fns if "mint" in f.lower()]
        quote = [f for f in fns if "quote" in f.lower() or "cost" in f.lower()]
        free = [f for f in fns if any(v.lower() in f.lower() for v in FREE_VIEWS)]
        agent = [f for f in fns if "agent" in f.lower() or "registry" in f.lower()]
        token = [f for f in fns if f in ("name", "symbol", "decimals", "totalSupply")]
        s1 = bool(mint and quote and free and agent)
        s2 = bool(token == ["name", "symbol", "decimals", "totalSupply"] and
                  any(f in fns for f in ("mintFree",)) and free and agent)
        shape[a] = {"S1": s1, "S2": s2, "mint": mint, "quote": quote,
                    "free": free, "agent": agent, "token": token,
                    "fns": len(fns),
                    "verifiedAt": next((r.get("verifiedAt") for r in feed["results"]
                                        if r["address"].lower() == a.lower()), None)}
    except Exception as e:
        shape[a] = {"error": str(e)[:200]}
    print(a, json.dumps(shape[a]))
json.dump(shape, open(BASE + TAG + "-shape.json", "w"), indent=1)

# ---- Leg 2: Boltbook (files already fetched) ----
for lang, path in [("en", "/tmp/bb-en-2119.html"), ("zh", "/tmp/bb-zh-2119.html")]:
    html = open(path, errors="ignore").read()
    open(BASE + TAG + "-boltbook-" + lang + ".html", "w").write(html)
    found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
    new_bb = [a for a in found if a.lower() not in seen_l]
    print(f"BOLTBOOK {lang}: {len(html)} bytes, {len(found)} addrs, new: {new_bb}")

# ---- Leg 4 priority: BYTEBLOOM + KERNELMONK ----
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")

def words(hexstr):
    if not isinstance(hexstr, str) or not hexstr.startswith("0x"): return None
    h = hexstr[2:]
    return [int(h[i:i+64], 16) for i in range(0, len(h) - 63, 64)] if len(h) % 64 == 0 else None

def batch_call(rpc, calls):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for i, (to, data) in enumerate(calls)])
    p = subprocess.run(["curl", "-s", "--max-time", "30", "-X", "POST", rpc,
                        "-H", "Content-Type: application/json", "--data", payload],
                       capture_output=True, text=True)
    try: return json.loads(p.stdout)
    except Exception: return {"_err": p.stdout[:200] + p.stderr[:200]}

def block_number(rpc):
    p = subprocess.run(["curl", "-s", "--max-time", "15", "-X", "POST", rpc,
                        "-H", "Content-Type: application/json",
                        "--data", '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'],
                       capture_output=True, text=True)
    try: return int(json.loads(p.stdout)["result"], 16)
    except Exception: return None

CONTRACTS = {
    "BYTEBLOOM": "0x74bbDAD7c027C56bE30A7fEaC6F7371B95f1c32B",
}
CALLS = [
    ("totalSupply", sel("totalSupply()")),
    ("agentFreeUsed", sel("agentFreeUsed()")),
    ("freeLeft", sel("freeLeft()")),
    ("mintOpen", sel("mintOpen()")),
    ("status", sel("status()")),
    ("balanceOf_user", sel("balanceOf(address)") + enc_addr(USER)),
    ("walletInfo_user", sel("walletInfo(address)") + enc_addr(USER)),
    ("agentFreeByWallet_user", sel("agentFreeByWallet(address)") + enc_addr(USER)),
]
jobs = []
for name, addr in CONTRACTS.items():
    for field, data in CALLS:
        jobs.append((name, field, addr, data))

result = None; used_rpc = None; block = None
for rpc in RPCS:
    r = batch_call(rpc, [(a, d) for (_, _, a, d) in jobs])
    if isinstance(r, list) and len(r) == len(jobs) and all(
            isinstance(x, dict) and "result" in x and x["result"] for x in r):
        result, used_rpc = r, rpc
        break
    print("RPC", rpc, "incomplete/empty, trying next")
if result is None:
    for rpc in RPCS:
        r = batch_call(rpc, [(a, d) for (_, _, a, d) in jobs])
        if isinstance(r, list) and len(r) == len(jobs):
            result, used_rpc = r, rpc
            break
if used_rpc:
    block = block_number(used_rpc)
print("RPC used:", used_rpc, "block:", block)

out = {"block": block, "rpc": used_rpc, "items": {}, "failed": []}
for (name, field, addr, _), resp in zip(jobs, result or []):
    val = resp.get("result") if isinstance(resp, dict) else None
    if not val:
        out["failed"].append({"item": name, "field": field})
        continue
    w = words(val)
    if w is None:
        out["failed"].append({"item": name, "field": field, "raw": val[:80]})
        continue
    entry = out["items"].setdefault(name, {"address": addr})
    entry[field] = w if len(w) > 1 else w[0]
json.dump(out, open(BASE + TAG + "-priority-reread.json", "w"), indent=1)
print(json.dumps(out, indent=1))

# ---- Update hot-leg-seen.json with new feed contracts ----
import datetime
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds")
for a, s in shape.items():
    if a.lower() in seen_l: continue
    note = f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} free={s.get('free')} agent={s.get('agent')} token={s.get('token')}"
    seen[a] = {"first_seen_wib": now, "note": note, "source": "sourcify-feed",
               "status": "checked-not-sale-shape" if not (s.get("S1") or s.get("S2")) else "sale-shape"}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"))
print("seen total now:", len(seen))
print("DURATION sec:", round(time.time() - T0, 1))
