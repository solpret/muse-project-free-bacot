#!/usr/bin/env python3
"""Hot-leg run scheduled 2026-11-11 03:54 WIB.
Leg 1 Sourcify feed (shape-check PARALLEL), Leg 2 Boltbook EN+ZH,
Leg 3 prelaunch re-check (4 S1 from 0024), Leg 4 re-read 48 snapshot items
(baseline 0349) + priority re-reads (NIGHTFORGE, SOLDERCATS, CosmicSentinel,
EMBERANVIL, BYTEBLOOM, CHEEMSA, Pickgrid) PARALLEL. Bridge read-only.
Per-item batches with RPC fallback; a failed batch is recorded, never a
whole-run failure. Read-only except hot-leg-seen.json + own run outputs."""
import json, subprocess, time, re, datetime, os
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-11-0354"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
RPCS = ["https://bsc.nodereal.io/", "https://bsc-dataseed.binance.org/",
        "https://bsc-dataseed1.binance.org/"]
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}

def curl(url, max_time=20):
    p = subprocess.run(["curl", "-s", "--max-time", str(max_time), url],
                       capture_output=True, text=True)
    return p.stdout

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_uint(n): return hex(n)[2:].rjust(64, "0")

def words(h):
    if not isinstance(h, str) or not h.startswith("0x"): return None
    s = h[2:]
    if not s or len(s) % 64: return None
    return [int(s[i:i+64], 16) for i in range(0, len(s), 64)]

def batch_call(rpc, calls):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for i, (to, data) in enumerate(calls)])
    p = subprocess.run(["curl", "-s", "--max-time", "25", "-X", "POST", rpc,
                        "-H", "Content-Type: application/json", "--data", payload],
                       capture_output=True, text=True)
    try:
        r = json.loads(p.stdout)
        return r if isinstance(r, list) else {"_err": str(r)[:200]}
    except Exception:
        return {"_err": (p.stdout + p.stderr)[:200]}

def read_item(addr, views):
    calls = [(addr, d) for _, d in views]
    for rpc in RPCS:
        r = batch_call(rpc, calls)
        if isinstance(r, list) and len(r) == len(calls):
            out = {}
            ok = 0
            for (key, _), resp in zip(views, r):
                val = resp.get("result") if isinstance(resp, dict) else None
                w = words(val) if val else None
                if w is not None:
                    out[key] = w if len(w) > 1 else w[0]
                    ok += 1
                else:
                    out[key] = None
            if ok:
                return out, rpc, None
    return {k: None for k, _ in views}, None, "batch-fail-all-rpcs"

def sig_for_field(f):
    if f.endswith("_user1"):
        return f[:-6] + "(uint256)", enc_uint(1)
    if f.endswith("_user"):
        return f[:-5] + "(address)", enc_addr(USER)
    if f.endswith("_0"):
        return f[:-2] + "(uint256)", enc_uint(0)
    return f + "()", ""

def views_for(fields):
    vs = []
    for f in fields:
        sig, arg = sig_for_field(f)
        vs.append((f, sel(sig) + arg))
    return vs

def block_number():
    for rpc in RPCS:
        p = subprocess.run(["curl", "-s", "--max-time", "15", "-X", "POST", rpc,
                            "-H", "Content-Type: application/json",
                            "--data", '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'],
                           capture_output=True, text=True)
        try: return int(json.loads(p.stdout)["result"], 16)
        except Exception: continue
    return None

now_wib = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
NOW = now_wib.isoformat(timespec="seconds")
print("RUN start", NOW, flush=True)

# ---- Leg 1: feed ----
feed = {}
try:
    feed = json.loads(curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 25))
except Exception as e:
    print("FEED ERROR", e, flush=True)
json.dump(feed, open(BASE + TAG + "-feed.json", "w"), indent=1)
addrs = [r["address"] for r in feed.get("results", [])]
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
new_feed = [a for a in addrs if a.lower() not in seen_l and a.lower() not in EXCLUDED]
print("FEED count:", len(addrs), "new:", new_feed, flush=True)

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeSupply", "freeSlots"]
def shape_check(a):
    try:
        raw = curl(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", 15)
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
        variant = [f for f in fns if "claimfree" in f.lower()
                   or "freepoolremaining" in f.lower()
                   or "freeclaims" in f.lower()]
        return {"S1": s1, "S2": s2, "mint": mint, "quote": quote,
                "free": free, "agent": agent, "token": token, "fns": len(fns),
                "variant_claimfree": variant,
                "verifiedAt": next((r.get("verifiedAt") for r in feed.get("results", [])
                                    if r["address"].lower() == a.lower()), None)}
    except Exception as e:
        return {"error": str(e)[:200]}

shape = {}
with ThreadPoolExecutor(max_workers=8) as ex:
    for a, s in zip(new_feed, ex.map(shape_check, new_feed)):
        shape[a] = s
        print("FEED-SHAPE", a, json.dumps(s), flush=True)
# Sequential retry for ABI fetch errors (parallel Sourcify fetches return empty under load)
for a in list(shape.keys()):
    if "error" in shape[a]:
        for attempt in range(2):
            time.sleep(1)
            s = shape_check(a)
            if "error" not in s:
                shape[a] = s
                print("FEED-SHAPE-RETRY-OK", a, json.dumps(s), flush=True)
                break
        else:
            print("FEED-SHAPE-RETRY-FAIL", a, shape[a].get("error"), flush=True)

# ---- Leg 2: Boltbook ----
def fetch_bb(args):
    lang, url = args
    html = curl(url, 25)
    open(BASE + TAG + "-boltbook-" + lang + ".html", "w").write(html)
    return lang, html

bb_new = []
with ThreadPoolExecutor(max_workers=2) as ex:
    for lang, html in ex.map(fetch_bb, [("en", "https://boltbook.fun/"),
                                        ("zh", "https://boltbook.fun/?lang=zh")]):
        found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
        new_bb = [a for a in found if a.lower() not in seen_l
                  and a.lower() not in {x.lower() for x in new_feed}
                  and a.lower() not in EXCLUDED]
        bb_new += new_bb
        print(f"BOLTBOOK {lang}: {len(html)} bytes, {len(found)} addrs, new: {new_bb}", flush=True)
        for kw in ["free share", "first share free", "free mint", "免费份额", "首个免费", "免费铸造", "免费mint"]:
            if kw.lower() in html.lower():
                print(f"  keyword hit {lang}: {kw}", flush=True)
for a in bb_new[:3]:
    shape[a] = shape_check(a)
    shape[a]["source"] = "boltbook-frontpage"
    print("BB-SHAPE", a, json.dumps(shape[a]), flush=True)
json.dump(shape, open(BASE + TAG + "-shape.json", "w"), indent=1)

# ---- Leg 4: re-read 48 items vs 0349 baseline ----
prev = json.load(open(BASE + "hot-leg-2026-11-11-0344-reread.json"))
prev_items = prev.get("items", {})
prev_block = prev.get("block")
block = block_number()
print("BLOCK", block, "prev", prev_block, flush=True)

def reread_one(name):
    p = prev_items[name]
    addr = p["address"]
    fields = [k for k in p.keys() if k != "address"]
    out, rpc, err = read_item(addr, views_for(fields))
    d = {"address": addr}
    d.update(out)
    if err: d["_batch_fail"] = err
    return name, d

items = {}
read_failed = []
with ThreadPoolExecutor(max_workers=8) as ex:
    for name, d in ex.map(reread_one, list(prev_items.keys())):
        items[name] = d
        if d.get("_batch_fail"):
            read_failed.append(name)
diffs = []
for name, d in items.items():
    p = prev_items[name]
    for k, v in d.items():
        if k in ("address", "_batch_fail"): continue
        old = p.get(k)
        if v is not None and old is not None and v != old:
            diffs.append({"item": name, "field": k, "old": old, "new": v})
        elif v is not None and old is None:
            diffs.append({"item": name, "field": k, "old": None, "new": v})
print("REREAD diffs:", len(diffs), json.dumps(diffs), flush=True)
print("REREAD batch-fail items:", read_failed, flush=True)
reread = {"block": block, "prev_block": prev_block, "items": items,
          "duration_sec": round(time.time() - T0, 1),
          "read_failed": read_failed, "diffs_vs_0349": diffs,
          "baseline_note": "diffs vs 0349 leg4"}
json.dump(reread, open(BASE + TAG + "-reread.json", "w"), indent=1)

# ---- Priority re-reads (PARALLEL) ----
PRIO = {
 "NIGHTFORGE": ("0x22f43ba09fd4beb9417d4484c60370354b220186",
   [("totalSupply", "totalSupply()"), ("status", "status()"),
    ("mintOpen", "mintOpen()"), ("mintStart", "mintStart()"),
    ("freeMinted", "freeMinted()"), ("freeLeft", "freeLeft()"),
    ("agentFreeUsed", "agentFreeUsed()"),
    ("balanceOf_user", "balanceOf(address)", "addr"),
    ("freeClaimed_user", "freeClaimed(address)", "addr")]),
 "SOLDERCATS": ("0x3D972EBbF7488f21b95250B867e2406c723C9DDC",
   [("totalSupply", "totalSupply()"), ("agentFreeUsed", "agentFreeUsed()"),
    ("agentFreeLeft", "agentFreeLeft()"), ("mintOpen", "mintOpen()"),
    ("mintStart", "mintStart()"),
    ("balanceOf_user", "balanceOf(address)", "addr"),
    ("agentFreeByWallet_user", "agentFreeByWallet(address)", "addr")]),
 "CosmicSentinel": ("0x88731d1eb41c36f3d705fdb58b658244c06afc36",
   [("totalSupply", "totalSupply()"), ("freeMinted", "freeMinted()"),
    ("mintOpen", "mintOpen()"),
    ("balanceOf_user", "balanceOf(address)", "addr"),
    ("freeClaimed_user", "freeClaimed(address)", "addr")]),
 "EMBERANVIL": ("0x7673c596a6702d32f844266dc2ca7b1fd6d7df21",
   [("totalSupply", "totalSupply()"), ("agentFreeUsed", "agentFreeUsed()"),
    ("agentFreeLeft", "agentFreeLeft()"), ("mintOpen", "mintOpen()"),
    ("balanceOf_user", "balanceOf(address)", "addr"),
    ("agentFreeByWallet_user", "agentFreeByWallet(address)", "addr")]),
 "BYTEBLOOM": ("0x74bbDAD7c027C56bE30A7fEaC6F7371B95f1c32B",
   [("totalSupply", "totalSupply()"), ("agentFreeUsed", "agentFreeUsed()"),
    ("agentFreeLeft", "agentFreeLeft()"), ("mintOpen", "mintOpen()"),
    ("balanceOf_user", "balanceOf(address)", "addr"),
    ("walletInfo_user", "walletInfo(address)", "addr"),
    ("agentFreeByWallet_user", "agentFreeByWallet(address)", "addr")]),
 "CHEEMSA": ("0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2",
   [("totalFreeMinted", "totalFreeMinted()"), ("FREE_SHARES", "FREE_SHARES()"),
    ("freeClaimedByWallet_user", "freeClaimedByWallet(address)", "addr"),
    ("balanceOf_user", "balanceOf(address)", "addr")]),
 "Pickgrid": ("0xc2BEAaD13Ef2833D976957E41B03b6B2661cFAB0",
   [("live", "live()"), ("freeMinted", "freeMinted()"),
    ("balanceOf_user", "balanceOf(address)", "addr")]),
}
def prio_views(spec):
    vs = []
    for tup in spec:
        key, sig = tup[0], tup[1]
        arg = enc_addr(USER) if len(tup) > 2 and tup[2] == "addr" else ""
        vs.append((key, sel(sig) + arg))
    return vs

def prio_one(name):
    addr, spec = PRIO[name]
    out, rpc, err = read_item(addr, prio_views(spec))
    d = {"address": addr}
    d.update(out)
    if err: d["_batch_fail"] = err
    return name, d

prio_out = {}
with ThreadPoolExecutor(max_workers=7) as ex:
    for name, d in ex.map(prio_one, list(PRIO.keys())):
        prio_out[name] = d
        print("PRIO", name, json.dumps(d), flush=True)
json.dump(prio_out, open(BASE + TAG + "-priority-reread.json", "w"), indent=1)

# ---- Prelaunch S1 recheck (4 contracts from 0024 leg3) ----
PRE = ["0x030C38417FCB34714E3124c61EAb22Bc539D7e4C",
       "0x309fc27Eb11634716EaB23BCa97d614Ebc923E21",
       "0x98DcfdeB5e015bbB3c9ACa2a90Ba0EE80E35315b",
       "0x09a713Bd5b2c76ff3cE15b653f4f80645B3c93b5"]
def pre_one(a):
    vs = views_for(["mintActive", "totalSupply", "freeMinted", "deckRemaining",
                    "priceFor_user", "freeUsed_user", "holdsAgentId_user"])
    out, rpc, err = read_item(a, vs)
    d = {"address": a}
    d.update(out)
    if err: d["_batch_fail"] = err
    return a, d

pre_out = {}
with ThreadPoolExecutor(max_workers=4) as ex:
    for a, d in ex.map(pre_one, PRE):
        pre_out[a] = d
        print("PRELAUNCH", a, json.dumps(d), flush=True)
json.dump(pre_out, open(BASE + TAG + "-prelaunch.json", "w"), indent=1)

# ---- Bridge check (read-only) ----
bridge_note = ""
try:
    b = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = b.get("contracts", {})
    bset = {k.lower() for k in bcontracts}
    disc = [k for k, v in bcontracts.items()
            if isinstance(v, dict) and v.get("same_owner_discarded")]
    feed_in_bridge = [a for a in addrs if a.lower() in bset]
    bb_in_bridge = [a for a in bb_new if a.lower() in bset]
    mtime = datetime.datetime.fromtimestamp(
        os.path.getmtime(BASE + "scan-bridge.json"),
        datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds")
    bridge_note = (f"BRIDGE contracts={len(bcontracts)} mtime={mtime} "
                   f"same_owner_discarded={len(disc)} feed_in_bridge={feed_in_bridge} "
                   f"boltbook_new_in_bridge={bb_in_bridge}")
    print(bridge_note, flush=True)
except Exception as e:
    bridge_note = f"BRIDGE read error: {e}"
    print(bridge_note, flush=True)

# ---- Update hot-leg-seen.json ----
added = 0
for a, s in shape.items():
    if a.lower() in seen_l: continue
    if "error" in s:
        note = f"ABI fetch error: {s['error']}"
        status = "checked-abi-unavailable"
    else:
        note = (f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} "
                f"free={s.get('free')} agent={s.get('agent')} token={s.get('token')}")
        status = "checked-not-sale-shape" if not (s.get("S1") or s.get("S2")) else "sale-shape"
    seen[a] = {"first_seen_wib": NOW, "note": note,
               "source": s.get("source", "sourcify-feed"), "status": status}
    added += 1
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"))
print("seen added:", added, "total now:", len(seen), flush=True)
print("bridge:", bridge_note, flush=True)
print("DURATION sec:", round(time.time() - T0, 1), flush=True)
