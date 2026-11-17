#!/usr/bin/env python3
"""Hot-leg 0034 completion: remaining PRIO items, PRELAUNCH recheck, bridge, seen update.
Main run script was killed by the 280s timeout during the PRIO loop (after SOLDERCATS)."""
import json, subprocess, time, datetime, os
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-11-0034"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
RPCS = ["https://bsc.nodereal.io/", "https://bsc-dataseed.binance.org/",
        "https://bsc-dataseed1.binance.org/"]
now_wib = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
NOW = now_wib.isoformat(timespec="seconds")

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
    return [(f, sel(sig_for_field(f)[0]) + sig_for_field(f)[1]) for f in fields]

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

# Re-run ALL prio items (idempotent; SOLDERCATS/NIGHTFORGE values already printed in main run)
prio_out = {}
for name, (addr, spec) in PRIO.items():
    out, rpc, err = read_item(addr, prio_views(spec))
    d = {"address": addr}
    d.update(out)
    if err: d["_batch_fail"] = err
    prio_out[name] = d
    print("PRIO", name, json.dumps(d), "via", rpc, flush=True)
json.dump(prio_out, open(BASE + TAG + "-priority-reread.json", "w"), indent=1)

# Prelaunch S1 recheck (4 contracts from 0024 leg3)
PRE = ["0x030C38417FCB34714E3124c61EAb22Bc539D7e4C",
       "0x309fc27Eb11634716EaB23BCa97d614Ebc923E21",
       "0x98DcfdeB5e015bbB3c9ACa2a90Ba0EE80E35315b",
       "0x09a713Bd5b2c76ff3cE15b653f4f80645B3c93b5"]
pre_out = {}
for a in PRE:
    vs = views_for(["mintActive", "totalSupply", "freeMinted", "deckRemaining",
                    "priceFor_user", "freeUsed_user", "holdsAgentId_user"])
    out, rpc, err = read_item(a, vs)
    d = {"address": a}
    d.update(out)
    if err: d["_batch_fail"] = err
    pre_out[a] = d
    print("PRELAUNCH", a, json.dumps(d), "via", rpc, flush=True)
json.dump(pre_out, open(BASE + TAG + "-prelaunch.json", "w"), indent=1)

# Bridge check (read-only)
try:
    b = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = b.get("contracts", {})
    bset = {k.lower() for k in bcontracts}
    disc = [k for k, v in bcontracts.items()
            if isinstance(v, dict) and v.get("same_owner_discarded")]
    feed = json.load(open(BASE + TAG + "-feed.json"))
    addrs = [r["address"] for r in feed.get("results", [])]
    feed_in_bridge = [a for a in addrs if a.lower() in bset]
    mtime = datetime.datetime.fromtimestamp(
        os.path.getmtime(BASE + "scan-bridge.json"),
        datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds")
    bridge_note = (f"BRIDGE contracts={len(bcontracts)} mtime={mtime} "
                   f"same_owner_discarded={len(disc)} feed_in_bridge={feed_in_bridge} "
                   f"boltbook_new_in_bridge=[]")
    print(bridge_note, flush=True)
except Exception as e:
    bridge_note = f"BRIDGE read error: {e}"
    print(bridge_note, flush=True)

# Update hot-leg-seen.json from shape.json (21 items)
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
shape = json.load(open(BASE + TAG + "-shape.json"))
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
