#!/usr/bin/env python3
"""Run 2026-11-08 18:01 WIB: (a) binanceai track-B re-check (light), (b) lean re-read of the
32 scan-bridge contracts missing from the snapshot (not discarded). Read-only; writes only
its own output JSON. A failed read is None = UNVERIFIED, never zero."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN = "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
T0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def raw_batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            out = _fr_post(ep, calls, timeout=8, retries=0)
            if not isinstance(out, list) or len(out) != len(calls):
                continue
            res = {}
            for item, key in zip(out, keys):
                if isinstance(item, dict) and "error" in item:
                    res[key] = None
                else:
                    res[key] = to_int(item.get("result")) if isinstance(item, dict) else None
            return res
        except Exception:
            continue
    return None

out = {"started_wib": "2026-11-08 18:01 WIB", "binanceai": {}, "bridge": {}}

# (a) binanceai
b = raw_batch(MINT, ["launched()", "failed()", "isRefundPhase()", "totalShares()", "tokenClaimed(address)"])
tok = raw_batch(TOKEN, ["balanceOf(address)", "totalSupply()"])
out["binanceai"] = {"mint": MINT, "token": TOKEN, "views": b, "tokenViews": tok}
print("BINANCEAI", b, tok, flush=True)

# (b) bridge contracts missing from snapshot
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
snap_addrs = {v.get("address", "").lower() for v in snap.get("contracts", {}).values()}
bridge = json.load(open(f"{BASE}/scan-bridge.json"))
missing = [(k, v) for k, v in bridge.get("contracts", {}).items()
           if k.lower() not in snap_addrs and not v.get("same_owner_discarded")]
print(f"BRIDGE missing: {len(missing)}", flush=True)
LEAN = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
        "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
        "freeClaimed(address)", "name()", "symbol()"]

def read_bridge(item):
    addr, meta = item
    got = raw_batch(addr, LEAN)
    d = {"bridge_note": str(meta.get("note", ""))[:200],
         "reported_as": meta.get("reported_as"),
         "first_seen": str(meta.get("first_seen", ""))[:80]}
    if got is None:
        d["_batch_fail"] = True
        for k in ["totalSupply", "totalMinted", "freeClaimed", "freeMinted",
                  "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "balanceOf_user",
                  "freeClaimed_user", "name", "symbol"]:
            d[k] = None
    else:
        d.update(got)
    print(f"BRIDGE {addr} totalSupply={d.get('totalSupply')} freeClaimed={d.get('freeClaimed')} mintOpen={d.get('mintOpen')}", flush=True)
    return addr, d

with ThreadPoolExecutor(max_workers=8) as ex:
    for addr, d in ex.map(read_bridge, missing):
        out["bridge"][addr] = d

out["elapsed_s"] = round(time.time() - T0, 1)
with open(f"{BASE}/run-2026-11-08-1801-bridge-binanceai.json", "w") as f:
    json.dump(out, f, indent=1)
print(f"DONE in {out['elapsed_s']}s", flush=True)
