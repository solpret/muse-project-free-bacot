#!/usr/bin/env python3
"""Track-C re-read for run 0131 (main reread died during first TC item). Read-only."""
import json, sys, time, os
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch, race as _race
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
T0 = time.time()
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
TC_VIEWS = ["totalSupply()", "freeMinted()", "freeSharesRemaining()", "balanceOf(address)", "freeClaimed(address)"]
MINIMAL = ["totalSupply()", "balanceOf(address)"]
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
track_c = snap.get("track_c", {})
out = {"block": None, "track_c": {}, "started_wib": "2026-11-07 01:31 WIB"}
try: out["block"] = int(_race("eth_blockNumber", []), 16)
except Exception as e: print("BLOCK-FAIL", e, flush=True)
print("BLOCK", out["block"], flush=True)
def read_tc(item):
    name, addr = item
    t = time.time()
    d = {"address": addr}
    got = batch_views(addr, TC_VIEWS)
    if got is None:
        got = batch_views(addr, MINIMAL)
        if got is not None:
            d.update(got)
            for k in ["freeMinted", "freeSharesRemaining", "freeClaimed_user"]: d.setdefault(k, None)
        else:
            for k in ["totalSupply", "freeMinted", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"]: d[k] = None
    else:
        d.update(got)
    print(f"TC {name} totalSupply={d.get('totalSupply')} freeMinted={d.get('freeMinted')} ({time.time()-t:.1f}s)", flush=True)
    return name, d
tc_items = []
for k, v in track_c.items():
    if not isinstance(v, dict): continue
    a = v.get("address") or v.get("sale") or v.get("token")
    if a and isinstance(a, str) and a.startswith("0x"): tc_items.append((k, a))
print(f"TC items: {len(tc_items)}", flush=True)
with ThreadPoolExecutor(max_workers=10) as ex:
    for name, d in ex.map(read_tc, tc_items):
        out["track_c"][name] = d
        with open(f"{BASE}/run-2026-11-07-0131-reread-tc.json.tmp", "w") as f: json.dump(out, f, indent=1)
        os.replace(f"{BASE}/run-2026-11-07-0131-reread-tc.json.tmp", f"{BASE}/run-2026-11-07-0131-reread-tc.json")
print(f"TC REREAD DONE in {time.time()-T0:.1f}s track_c={len(out['track_c'])}", flush=True)
