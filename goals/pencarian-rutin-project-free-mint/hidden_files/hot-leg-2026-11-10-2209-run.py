#!/usr/bin/env python3
"""Hot-leg run 2026-11-10 22:09 WIB (scheduled).
Leg 1: Sourcify feed (limit 20) - shape-check new contracts.
Leg 2: Boltbook front page EN (retry, was 0 bytes) + ZH (boltbook.fun).
Leg 4: re-read BYTEBLOOM (23.85% at 21:29, near 25% strong-lead),
NIGHTFORGE, EMBERANVIL, Cosmic Sentinel, track-C YAMA/LOWB/11-11.
Bridge read-only. Read-only; no preview/mint unless strong-lead
threshold crossed AND all guards pass (handled by parent if so).
"""
import json, subprocess, time, re, datetime, os
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-10-2209"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
RPCS = ["https://bsc.nodereal.io/", "https://bsc-dataseed.binance.org/",
        "https://bsc-dataseed1.binance.org/", "https://bsc.publicnode.com"]

def curl(url, max_time=20):
    p = subprocess.run(["curl", "-s", "--max-time", str(max_time), url],
                       capture_output=True, text=True)
    return p.stdout

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")

def words(hexstr):
    if not isinstance(hexstr, str) or not hexstr.startswith("0x"): return None
    h = hexstr[2:]
    if not h or len(h) % 64: return None
    return [int(h[i:i+64], 16) for i in range(0, len(h), 64)]

def batch_call(rpc, calls):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for i, (to, data) in enumerate(calls)])
    p = subprocess.run(["curl", "-s", "--max-time", "30", "-X", "POST", rpc,
                        "-H", "Content-Type: application/json", "--data", payload],
                       capture_output=True, text=True)
    try: return json.loads(p.stdout)
    except Exception: return {"_err": (p.stdout + p.stderr)[:200]}

def block_number(rpc):
    p = subprocess.run(["curl", "-s", "--max-time", "15", "-X", "POST", rpc,
                        "-H", "Content-Type: application/json",
                        "--data", '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'],
                       capture_output=True, text=True)
    try: return int(json.loads(p.stdout)["result"], 16)
    except Exception: return None

# ---- Leg 1: feed ----
feed = json.load(open("/tmp/hotleg-feed-2209.json"))
json.dump(feed, open(BASE + TAG + "-feed.json", "w"), indent=1)
addrs = [r["address"] for r in feed.get("results", [])]
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
new_feed = [a for a in addrs if a.lower() not in seen_l]
print("FEED count:", len(addrs), "new:", new_feed)

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeSupply", "freeSlots"]
def shape_check(a):
    try:
        raw = curl(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", 20)
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
        return {"S1": s1, "S2": s2, "mint": mint, "quote": quote,
                "free": free, "agent": agent, "token": token, "fns": len(fns),
                "verifiedAt": next((r.get("verifiedAt") for r in feed["results"]
                                    if r["address"].lower() == a.lower()), None)}
    except Exception as e:
        return {"error": str(e)[:200]}

shape = {}
for a in new_feed:
    shape[a] = shape_check(a)
    print("FEED-SHAPE", a, json.dumps(shape[a]))

# ---- Leg 2: Boltbook ----
bb_new = []
for lang, path in [("en", "/tmp/bb-en-2209.html"), ("zh", "/tmp/bb-zh-2209.html")]:
    try:
        html = open(path, errors="ignore").read()
    except Exception as e:
        html = ""
        print(f"BOLTBOOK {lang}: READ ERROR {e}")
    open(BASE + TAG + "-boltbook-" + lang + ".html", "w").write(html)
    found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
    new_bb = [a for a in found if a.lower() not in seen_l and a.lower() not in {x.lower() for x in new_feed}]
    bb_new += new_bb
    print(f"BOLTBOOK {lang}: {len(html)} bytes, {len(found)} addrs, new: {new_bb}")
for a in bb_new[:3]:
    shape[a] = shape_check(a)
    shape[a]["source"] = "boltbook-frontpage"
    print("BB-SHAPE", a, json.dumps(shape[a]))
json.dump(shape, open(BASE + TAG + "-shape.json", "w"), indent=1)

# ---- Snapshot gate info for priority items (read-only) ----
snap = json.load(open(BASE + "onchain-snapshot.json"))
for nm in ("BYTEBLOOM", "NIGHTFORGE", "EMBERANVIL", "Cosmic Sentinel"):
    e = snap["contracts"].get(nm, {})
    print(nm, "gate/website:", {k: e.get(k) for k in e if any(s in k.lower() for s in ("gate", "website", "site", "contracturi", "xverif", "launch"))})

# ---- Leg 4: batched re-read ----
BB = "0x74bbDAD7c027C56bE30A7fEaC6F7371B95f1c32B"
NF = "0x22f43ba09fd4beb9417d4484c60370354b220186"
EA = "0x7673c596a6702d32f844266dc2ca7b1fd6d7df21"
CS = "0x88731d1eb41c36f3d705fdb58b658244c06afc36"
YAMA = "0x86D779fc4d83044cCECCb53639f9a98E367D6E46"
LOWB = "0x00487ED061C77A1dd5085ef3a2D593366f9C6B35"
ELEVEN = "0x64767b1a39441e72046c2162065a2896e154b341"
jobs = []
def J(name, field, addr, data): jobs.append((name, field, addr, data))
for f, d in [("totalSupply", sel("totalSupply()")),
             ("agentFreeUsed", sel("agentFreeUsed()")),
             ("agentFreeLeft", sel("agentFreeLeft()")),
             ("mintOpen", sel("mintOpen()")),
             ("balanceOf_user", sel("balanceOf(address)") + enc_addr(USER)),
             ("walletInfo_user", sel("walletInfo(address)") + enc_addr(USER)),
             ("agentFreeByWallet_user", sel("agentFreeByWallet(address)") + enc_addr(USER))]:
    J("BYTEBLOOM", f, BB, d)
for nm, addr in [("NIGHTFORGE", NF), ("EMBERANVIL", EA)]:
    for f, d in [("totalSupply", sel("totalSupply()")),
                 ("mintOpen", sel("mintOpen()")),
                 ("mintStart", sel("mintStart()")),
                 ("freeMinted", sel("freeMinted()")),
                 ("freeLeft", sel("freeLeft()")),
                 ("agentFreeUsed", sel("agentFreeUsed()")),
                 ("balanceOf_user", sel("balanceOf(address)") + enc_addr(USER)),
                 ("freeClaimed_user", sel("freeClaimed(address)") + enc_addr(USER))]:
        J(nm, f, addr, d)
for f, d in [("totalSupply", sel("totalSupply()")),
             ("freeMinted", sel("freeMinted()")),
             ("mintOpen", sel("mintOpen()")),
             ("balanceOf_user", sel("balanceOf(address)") + enc_addr(USER)),
             ("freeClaimed_user", sel("freeClaimed(address)") + enc_addr(USER))]:
    J("CosmicSentinel", f, CS, d)
for f, d in [("freeSharesRemaining", sel("freeSharesRemaining()")),
             ("totalShares", sel("totalShares()")),
             ("totalFreeShares", sel("totalFreeShares()"))]:
    J("YAMA", f, YAMA, d)
for f, d in [("opened", sel("opened()")),
             ("totalFreeMinted", sel("totalFreeMinted()")),
             ("totalMinted", sel("totalMinted()"))]:
    J("LOWB", f, LOWB, d)
for f, d in [("freeMinted", sel("freeMinted()")),
             ("FREE_MINTS", sel("FREE_MINTS()")),
             ("freeClaimed_user", sel("freeClaimed(address)") + enc_addr(USER)),
             ("balanceOf_user", sel("balanceOf(address)") + enc_addr(USER))]:
    J("ELEVEN", f, ELEVEN, d)

result = None; used_rpc = None; block = None
for rpc in RPCS:
    r = batch_call(rpc, [(a, d) for (_, _, a, d) in jobs])
    if isinstance(r, list) and len(r) == len(jobs):
        ok = sum(1 for x in r if isinstance(x, dict) and x.get("result"))
        if ok >= len(jobs) * 0.6:
            result, used_rpc = r, rpc
            break
    print("RPC", rpc, "incomplete, trying next")
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
        out["failed"].append({"item": name, "field": field, "raw": str(val)[:80]})
        continue
    entry = out["items"].setdefault(name, {"address": addr})
    entry[field] = w if len(w) > 1 else w[0]
json.dump(out, open(BASE + TAG + "-priority-reread.json", "w"), indent=1)
print(json.dumps(out, indent=1))

# ---- Bridge check (read-only) ----
try:
    b = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = b.get("contracts", {})
    snap_addrs = {str(e.get("address", "")).lower() for e in snap.get("contracts", {}).values() if isinstance(e, dict)}
    snap_addrs |= {str(e.get("sale", "")).lower() for e in snap.get("track_c", {}).values() if isinstance(e, dict)}
    not_in_snap = [a for a in bcontracts if a.lower() not in snap_addrs]
    disc = [a for a, e in bcontracts.items() if isinstance(e, dict) and e.get("same_owner_discarded")]
    print("BRIDGE contracts:", len(bcontracts), "not_in_snapshot:", len(not_in_snap),
          "same_owner_discarded:", len(disc),
          "mtime:", datetime.datetime.fromtimestamp(
              os.path.getmtime(BASE + "scan-bridge.json"),
              datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds"))
    print("BRIDGE not-in-snapshot sample:", not_in_snap[:10])
except Exception as e:
    print("BRIDGE read error:", e)

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
