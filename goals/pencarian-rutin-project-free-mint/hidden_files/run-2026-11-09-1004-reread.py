#!/usr/bin/env python3
"""Hot-leg 2026-11-09 10:04 WIB — focused re-read of 46 near-threshold snapshot entries
(20-25.5% strong-lead watch, 45-50% candidate watch, 95-100% sellout watch).
Read-only; never writes snapshot/state. Curl transport like the 09:31 main reread."""
import json, time, subprocess
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-09-1004"
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

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

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
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls): continue
            outd = {}
            for item, key in zip(res, keys):
                outd[key] = None if (isinstance(item, dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item, dict) else None)
            return outd
        except Exception:
            continue
    return None

LEAN = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
        "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
        "freeClaimed(address)"]

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

sub = json.load(open(f"{BASE}/run-{TS}-reread-focus.json"))
out = {"block": get_block(), "reread": {}, "started_wib": "2026-11-09 10:04 WIB"}
print("BLOCK", out["block"], "TODO", len(sub), flush=True)

def read_lean(item):
    name, addr = item["name"], item["address"]
    t = time.time()
    got = raw_batch(addr, LEAN)
    d = {"address": addr}
    if got is None:
        for k in ["totalSupply","totalMinted","freeClaimed","freeMinted","FREE_SUPPLY","MAX_SUPPLY","mintOpen","balanceOf_user","freeClaimed_user"]:
            d[k] = None
        d["_batch_fail"] = True
    else:
        d.update(got)
    d["_prev"] = item
    print(f"LEAN {name} totalSupply={d.get('totalSupply')} freeClaimed={d.get('freeClaimed')} freeMinted={d.get('freeMinted')} bal={d.get('balanceOf_user')} ({time.time()-t:.1f}s)", flush=True)
    return name, d

with ThreadPoolExecutor(max_workers=8) as ex:
    for name, d in ex.map(read_lean, sub):
        out["reread"][name] = d
json.dump(out, open(f"{BASE}/run-{TS}-reread.json", "w"), indent=1)
print(f"DONE in {time.time()-T0:.1f}s n={len(out['reread'])}", flush=True)
