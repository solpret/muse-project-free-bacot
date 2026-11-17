#!/usr/bin/env python3
"""Resume run 0701 re-read: read contracts/track_c missing from the partial
0701 JSON (killed mid-run ~23:39 UTC). Same LEAN/MINIMAL approach, same
endpoints. Read-only on shared state; writes only the 0701 JSON (incremental)."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]
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
            calls.append(("eth_call", [{"to": addr, "data": sel(sig) + enc(USER)}, "latest"])); keys.append(base + "_user")
        else:
            calls.append(("eth_call", [{"to": addr, "data": sel(sig)}, "latest"])); keys.append(base)
    for ep in EPS:
        try:
            res = batch(calls, endpoint=ep, timeout=8)
            return {k: to_int(v) for k, v in zip(keys, res)}
        except Exception:
            continue
    return None
LEAN = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
        "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
        "freeClaimed(address)"]
MINIMAL = ["totalSupply()", "balanceOf(address)"]
TC_VIEWS = ["totalSupply()", "freeMinted()", "freeSharesRemaining()",
            "balanceOf(address)", "freeClaimed(address)"]
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
out = json.load(open(f"{BASE}/run-2026-11-08-0701-reread.json"))
def save():
    json.dump(out, open(f"{BASE}/run-2026-11-08-0701-reread.json", "w"), indent=1)
def read_lean(item):
    name, addr = item
    t = time.time()
    got = batch_views(addr, LEAN)
    d = {"address": addr}
    if got is None:
        got = batch_views(addr, MINIMAL)
        if got is not None:
            d.update(got)
            for k in ["totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "freeClaimed_user"]:
                d.setdefault(k, None)
        else:
            for k in ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"]:
                d[k] = None
    else:
        d.update(got)
    print(f"RESUME {name} totalSupply={d.get('totalSupply')} bal={d.get('balanceOf_user')} ({time.time()-t:.1f}s)", flush=True)
    return name, d
def read_tc(item):
    name, addr = item
    t = time.time()
    got = batch_views(addr, TC_VIEWS)
    d = {"address": addr}
    if got is None:
        got = batch_views(addr, MINIMAL)
        if got is not None:
            d.update(got)
            for k in ["freeMinted", "freeSharesRemaining", "freeClaimed_user"]:
                d.setdefault(k, None)
        else:
            for k in ["totalSupply", "freeMinted", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"]:
                d[k] = None
    else:
        d.update(got)
    print(f"RESUME-TC {name} totalSupply={d.get('totalSupply')} ({time.time()-t:.1f}s)", flush=True)
    return name, d
contracts = snap.get("contracts", {})
rest = [(k, v.get("address")) for k, v in contracts.items() if v.get("address") and k not in out["reread"]]
print(f"RESUME contracts missing: {len(rest)}", flush=True)
with ThreadPoolExecutor(max_workers=10) as ex:
    for name, d in ex.map(read_lean, rest):
        out["reread"][name] = d
        save()
tc = snap.get("track_c", {})
tc_items = []
for k, v in tc.items():
    if k in out["track_c"]: continue
    if not isinstance(v, dict): continue
    a = v.get("address") or v.get("sale") or v.get("token")
    if a and isinstance(a, str) and a.startswith("0x"):
        tc_items.append((k, a))
print(f"RESUME track_c missing: {len(tc_items)}", flush=True)
with ThreadPoolExecutor(max_workers=10) as ex:
    for name, d in ex.map(read_tc, tc_items):
        out["track_c"][name] = d
        save()
print(f"RESUME DONE in {time.time()-T0:.1f}s reread={len(out['reread'])} track_c={len(out['track_c'])}", flush=True)
