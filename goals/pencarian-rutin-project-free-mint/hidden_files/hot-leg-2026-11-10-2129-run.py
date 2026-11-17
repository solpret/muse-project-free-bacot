#!/usr/bin/env python3
"""Hot-leg run 2026-11-10 21:29 WIB.
Leg 1: Sourcify feed (limit 20) - shape-check new contracts.
Leg 2: Boltbook front page EN + ZH (boltbook.fun).
Leg 4 (priority): re-read BYTEBLOOM (21:19 read: 463/2000 = 23.15%,
stagnant) + Lanternfield (sale-shape not lead, 0.6% at 20:01).
Read-only. No preview/mint unless a strong-lead threshold is crossed
AND all guards pass (handled by parent).
"""
import json, subprocess, time, re, datetime
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-10-2129"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
RPCS = ["https://bsc.nodereal.io/", "https://bsc-dataseed.binance.org/",
        "https://bsc-dataseed1.binance.org/", "https://bsc.publicnode.com"]

def curl(url, max_time=25):
    p = subprocess.run(["curl", "-s", "--max-time", str(max_time), url],
                       capture_output=True, text=True)
    return p.stdout

# ---- Leg 1: feed ----
feed = json.load(open("/tmp/hotleg-feed-2129.json"))
json.dump(feed, open(BASE + TAG + "-feed.json", "w"), indent=1)
addrs = [r["address"] for r in feed.get("results", [])]
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
new_feed = [a for a in addrs if a.lower() not in seen_l]
print("FEED count:", len(addrs), "new:", new_feed)

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeSupply", "freeSlots"]
shape = {}
for a in new_feed:
    try:
        raw = curl(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", 25)
        d = json.loads(raw)
        abi = d.get("abi") or []
        fns = [e.get("name", "") for e in abi if e.get("type") == "function"]
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

# ---- Leg 2: Boltbook ----
bb_new = []
for lang, path in [("en", "/tmp/bb-en-2129.html"), ("zh", "/tmp/bb-zh-2129.html")]:
    html = open(path, errors="ignore").read()
    open(BASE + TAG + "-boltbook-" + lang + ".html", "w").write(html)
    found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
    new_bb = [a for a in found if a.lower() not in seen_l]
    bb_new += new_bb
    print(f"BOLTBOOK {lang}: {len(html)} bytes, {len(found)} addrs, new: {new_bb}")
# shape-check genuinely new Boltbook addresses (cap 3)
for a in bb_new[:3]:
    try:
        raw = curl(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", 25)
        d = json.loads(raw)
        abi = d.get("abi") or []
        fns = [e.get("name", "") for e in abi if e.get("type") == "function"]
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
                    "fns": len(fns), "source": "boltbook-frontpage"}
    except Exception as e:
        shape[a] = {"error": str(e)[:200], "source": "boltbook-frontpage"}
    print("BB-SHAPE", a, json.dumps(shape[a]))
json.dump(shape, open(BASE + TAG + "-shape.json", "w"), indent=1)

# ---- Leg 4 priority re-read ----
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

BB = "0x74bbDAD7c027C56bE30A7fEaC6F7371B95f1c32B"
LANT = "0x9aab6e84096A780F9400CdD4E230FaA41B4545f2"
jobs = []
for field, data in [
    ("totalSupply", sel("totalSupply()")),
    ("agentFreeUsed", sel("agentFreeUsed()")),
    ("freeLeft", sel("freeLeft()")),
    ("mintOpen", sel("mintOpen()")),
    ("balanceOf_user", sel("balanceOf(address)") + enc_addr(USER)),
    ("walletInfo_user", sel("walletInfo(address)") + enc_addr(USER)),
    ("agentFreeByWallet_user", sel("agentFreeByWallet(address)") + enc_addr(USER)),
]:
    jobs.append(("BYTEBLOOM", field, BB, data))
for field, data in [
    ("totalSupply", sel("totalSupply()")),
    ("freeMinted", sel("freeMinted()")),
    ("FREE_SUPPLY", sel("FREE_SUPPLY()")),
    ("freeAvailable", sel("freeAvailable()")),
    ("canFreeMint_user", sel("canFreeMint(address)") + enc_addr(USER)),
    ("freeMintedBy_user", sel("freeMintedBy(address)") + enc_addr(USER)),
    ("saleStart", sel("saleStart()")),
    ("mintOpen", sel("mintOpen()")),
    ("balanceOf_user", sel("balanceOf(address)") + enc_addr(USER)),
]:
    jobs.append(("LANTERNFIELD", field, LANT, data))

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

# ---- Bridge check (read-only) ----
import os
b = json.load(open(BASE + "scan-bridge.json"))
print("BRIDGE contracts:", len(b.get("contracts", {})),
      "mtime:", datetime.datetime.fromtimestamp(
          os.path.getmtime(BASE + "scan-bridge.json"),
          datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds"))

# ---- Snapshot gate info for BYTEBLOOM (read-only) ----
snap = json.load(open(BASE + "onchain-snapshot.json"))
bb = snap["contracts"].get("BYTEBLOOM", {})
print("BB-SNAPSHOT gate keys:", {k: bb.get(k) for k in bb
      if any(s in k.lower() for s in ("gate", "website", "site", "contracturi", "xverif"))})

# ---- Update hot-leg-seen.json with newly shape-checked contracts ----
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds")
for a, s in shape.items():
    if a.lower() in seen_l: continue
    if "error" in s:
        note = f"ABI fetch error: {s['error']}"
        status = "checked-abi-unavailable"
    else:
        note = (f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} "
                f"free={s.get('free')} agent={s.get('agent')} token={s.get('token')}")
        status = "checked-not-sale-shape" if not (s.get("S1") or s.get("S2")) else "sale-shape"
    seen[a] = {"first_seen_wib": now, "note": note,
               "source": s.get("source", "sourcify-feed"), "status": status}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"))
print("seen total now:", len(seen))
print("DURATION sec:", round(time.time() - T0, 1))
