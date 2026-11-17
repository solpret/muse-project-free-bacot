#!/usr/bin/env python3
"""Track-C re-read run 2331 — pinned-endpoint batch(), fail-fast. Read-only.
Resumes from run-2026-11-06-2331-reread.json (contracts already done).
Skips track_c note-strings (not contracts).
"""
import json, sys, time, os
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-2331"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]
T0 = time.time()
ADDR_FALLBACK = {
 "Ikigai-Ihigi": "0x3611455bE1FC2c6987FE9d016971b7E40B341684",
 "ASOC-43cE": "0x43cEef9313CB8c4ca3757bA841C44DF40A223205",
}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def batch_views(addr, views):
    calls, keys = [], []
    for sig in views:
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append(("eth_call", [{"to": addr, "data": data}, "latest"]))
        keys.append(key)
    for ep in EPS:
        try:
            res = batch(calls, endpoint=ep, timeout=8)
            return {k: to_int(v) for k, v in zip(keys, res)}
        except Exception:
            continue
    return None

TC_VIEWS = ["totalSupply()", "freeMinted()", "freeSharesRemaining()",
            "balanceOf(address)", "freeClaimed(address)"]
MINIMAL = ["totalSupply()", "balanceOf(address)"]

out = json.load(open(f"{BASE}/run-{TS}-reread.json"))
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
track_c = snap.get("track_c", {})

def save():
    with open(f"{BASE}/run-{TS}-reread.json.tmp", "w") as f:
        json.dump(out, f, indent=1)
    os.replace(f"{BASE}/run-{TS}-reread.json.tmp", f"{BASE}/run-{TS}-reread.json")

def read_tc(item):
    name, addr = item
    t = time.time()
    d = {"address": addr}
    got = batch_views(addr, TC_VIEWS)
    if got is None:
        got = batch_views(addr, MINIMAL)
        if got is not None:
            d.update(got)
            for k in ["freeMinted", "freeSharesRemaining", "freeClaimed_user"]:
                d.setdefault(k, None)
        else:
            for k in ["totalSupply", "freeMinted", "freeSharesRemaining",
                      "balanceOf_user", "freeClaimed_user"]:
                d[k] = None
    else:
        d.update(got)
    print(f"TC {name} totalSupply={d.get('totalSupply')} freeMinted={d.get('freeMinted')} ({time.time()-t:.1f}s)", flush=True)
    return name, d

tc_items, skipped = [], []
for k, v in track_c.items():
    if k in out["track_c"]:
        continue
    if isinstance(v, str):
        skipped.append(k); continue
    a = v.get("address") or v.get("sale") or v.get("token") or ADDR_FALLBACK.get(k)
    if a and isinstance(a, str) and a.startswith("0x"):
        tc_items.append((k, a))
    else:
        skipped.append(k)
print(f"TC items: {len(tc_items)}, skipped (notes/no-address): {len(skipped)} {skipped}", flush=True)
with ThreadPoolExecutor(max_workers=10) as ex:
    for name, d in ex.map(read_tc, tc_items):
        out["track_c"][name] = d
        save()
print(f"TC DONE in {time.time()-T0:.1f}s track_c={len(out['track_c'])}", flush=True)
