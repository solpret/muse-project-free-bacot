#!/usr/bin/env python3
"""Re-read run 2026-11-08 12:31 WIB v2 — raw JSON-RPC batch, per-item error tolerant.
Read-only; never writes snapshot/state/watermark. Resumes partial 1231 reread.json.
"""
import json, sys, time, os
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-08-1231"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
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
    """One HTTP POST with all views; per-item errors -> None. Tries endpoints in order."""
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

LEAN = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
        "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
        "freeClaimed(address)"]
TC_VIEWS = ["totalSupply()", "freeMinted()", "freeSharesRemaining()",
            "balanceOf(address)", "freeClaimed(address)"]

out_path = f"{BASE}/run-{TS}-reread.json"
if os.path.exists(out_path):
    out = json.load(open(out_path))
    print(f"RESUME: already have {len(out.get('reread', {}))} contracts, {len(out.get('track_c', {}))} track_c", flush=True)
else:
    out = {"block": None, "reread": {}, "track_c": {}, "started_wib": "2026-11-08 12:31 WIB"}

def get_block():
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber",
                                "params": []}, timeout=8, retries=0)
            return int(out["result"], 16)
        except Exception:
            continue
    return None

if out.get("block") is None:
    out["block"] = get_block()
print("BLOCK", out["block"], flush=True)

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
contracts = snap.get("contracts", {})
track_c = snap.get("track_c", {})

def save():
    tmp = out_path + ".tmp"
    with open(tmp, "w") as f: json.dump(out, f, indent=1)
    os.replace(tmp, out_path)

LOW = ("sold-out", "age-excluded", "minted-by-user", "excluded", "promotion-discarded",
       "same-owner-discarded", "paid-only")
def prio(name):
    st = str(contracts[name].get("status") or "")
    return 1 if any(x in st for x in LOW) else 0

todo = [(k, v.get("address")) for k, v in contracts.items()
        if v.get("address") and k not in out["reread"]]
todo.sort(key=lambda it: prio(it[0]))
print(f"TODO contracts: {len(todo)} (have {len(out['reread'])})", flush=True)

def read_lean(item):
    name, addr = item
    t = time.time()
    got = raw_batch(addr, LEAN)
    d = {"address": addr}
    if got is None:
        for k in ["totalSupply", "totalMinted", "freeClaimed", "freeMinted",
                  "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "balanceOf_user",
                  "freeClaimed_user"]:
            d[k] = None
        d["_batch_fail"] = True
    else:
        d.update(got)
    print(f"LEAN {name} totalSupply={d.get('totalSupply')} freeClaimed={d.get('freeClaimed')} bal={d.get('balanceOf_user')} ({time.time()-t:.1f}s)", flush=True)
    return name, d

done = [0]
with ThreadPoolExecutor(max_workers=16) as ex:
    for name, d in ex.map(read_lean, todo):
        out["reread"][name] = d
        done[0] += 1
        if done[0] % 20 == 0:
            save()
save()
print(f"CONTRACTS DONE total={len(out['reread'])} in {time.time()-T0:.1f}s", flush=True)

def read_tc(item):
    name, addr = item
    t = time.time()
    got = raw_batch(addr, TC_VIEWS)
    d = {"address": addr}
    if got is None:
        for k in ["totalSupply", "freeMinted", "freeSharesRemaining",
                  "balanceOf_user", "freeClaimed_user"]:
            d[k] = None
        d["_batch_fail"] = True
    else:
        d.update(got)
    print(f"TC {name} totalSupply={d.get('totalSupply')} freeMinted={d.get('freeMinted')} ({time.time()-t:.1f}s)", flush=True)
    return name, d

tc_items = []
for k, v in track_c.items():
    if k in out["track_c"]: continue
    if not isinstance(v, dict): continue
    a = v.get("address") or v.get("sale") or v.get("token")
    if a and isinstance(a, str) and a.startswith("0x"):
        tc_items.append((k, a))
print(f"TODO track_c: {len(tc_items)} (have {len(out['track_c'])})", flush=True)
with ThreadPoolExecutor(max_workers=16) as ex:
    for name, d in ex.map(read_tc, tc_items):
        out["track_c"][name] = d
        done[0] += 1
        if done[0] % 20 == 0:
            save()
save()
print(f"REREAD-V2 DONE in {time.time()-T0:.1f}s reread={len(out['reread'])} track_c={len(out['track_c'])}", flush=True)
