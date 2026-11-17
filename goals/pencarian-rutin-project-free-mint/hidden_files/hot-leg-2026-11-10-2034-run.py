#!/usr/bin/env python3
"""Hot-leg run 2026-11-10 20:34 WIB.
Leg 1: Sourcify recently-verified feed (limit 20).
Leg 2: Boltbook front page EN + ZH (boltbook.fun).
Leg 4 (priority): re-read BYTEBLOOM + KERNELMONK (near 25% strong-lead
threshold; 20:09 read: 17.4% / 20.75%). Read-only. No preview/mint.
"""
import json, subprocess, time, re
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-10-2034"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
RPCS = ["https://bsc.nodereal.io/", "https://bsc-dataseed.binance.org/",
        "https://bsc-dataseed1.binance.org/", "https://bsc.publicnode.com"]

def curl(url, max_time=25):
    p = subprocess.run(["curl", "-s", "--max-time", str(max_time), url],
                       capture_output=True, text=True)
    return p.stdout

# ---- Leg 1: Sourcify feed ----
feed_raw = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc")
feed = None
try:
    feed = json.loads(feed_raw)
except Exception:
    feed_raw2 = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc")
    try: feed = json.loads(feed_raw2)
    except Exception: feed = {"_error": (feed_raw[:200] + feed_raw2[:200])}
json.dump(feed, open(BASE + TAG + "-feed.json", "w"), indent=1)
addrs = [r["address"] for r in feed.get("results", [])] if isinstance(feed, dict) else []
print("FEED count:", len(addrs))
print("FEED verifiedAt range:", [(r["address"], r.get("verifiedAt")) for r in feed.get("results", [])][:3] if addrs else "none")

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
new_feed = [a for a in addrs if a.lower() not in seen_l]
print("FEED new vs seen:", new_feed)

# ---- Leg 2: Boltbook ----
for lang, url in [("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")]:
    html = curl(url)
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
    "KERNELMONK": "0x016b9CE7508628e4Fb19E4fAF3129Fdc41b150d7",
}
CALLS = [  # (field, data)
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
    # partial: take first rpc that returned a list at all
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
print("DURATION sec:", round(time.time() - T0, 1))
