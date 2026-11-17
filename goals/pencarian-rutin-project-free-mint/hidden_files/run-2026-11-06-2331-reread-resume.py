#!/usr/bin/env python3
"""Resume lean re-read run 2331 — 2301-style raw() (3 RPCs, timeout 5s), read-only.
Resumes from run-2026-11-06-2331-reread.json; skips already-read contracts.
Never writes snapshot/state/watermark.
"""
import json, urllib.request, time, os
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-2331"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed2.bnbchain.org"]
T0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(to, data, timeout=5):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None

def call(to, sig, args=""): return raw(to, sel(sig) + args)

LEAN = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
        "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()"]
TC_VIEWS = ["totalSupply()", "freeMinted()", "freeSharesRemaining()", "balanceOf(address)"]

out = json.load(open(f"{BASE}/run-{TS}-reread.json"))
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
contracts = snap.get("contracts", {})
track_c = snap.get("track_c", {})

def save():
    with open(f"{BASE}/run-{TS}-reread.json.tmp", "w") as f:
        json.dump(out, f, indent=1)
    os.replace(f"{BASE}/run-{TS}-reread.json.tmp", f"{BASE}/run-{TS}-reread.json")

def read_lean(item):
    name, addr = item
    t = time.time()
    d = {"address": addr}
    for sig in LEAN:
        d[sig.split("(")[0]] = call(addr, sig)
    d["balanceOf_user"] = call(addr, "balanceOf(address)", enc(USER))
    d["freeClaimed_user"] = call(addr, "freeClaimed(address)", enc(USER))
    print(f"LEAN {name} totalSupply={d.get('totalSupply')} freeClaimed={d.get('freeClaimed')} bal={d.get('balanceOf_user')} ({time.time()-t:.1f}s)", flush=True)
    return name, d

def read_tc(item):
    name, addr = item
    t = time.time()
    d = {"address": addr}
    for sig in TC_VIEWS:
        key = sig.split("(")[0] + ("_user" if "(address)" in sig else "")
        d[key] = call(addr, sig, enc(USER) if "(address)" in sig else "")
    d["freeClaimed_user"] = call(addr, "freeClaimed(address)", enc(USER))
    print(f"TC {name} totalSupply={d.get('totalSupply')} freeMinted={d.get('freeMinted')} ({time.time()-t:.1f}s)", flush=True)
    return name, d

rest = [(k, v.get("address")) for k, v in contracts.items()
        if k not in out["reread"] and v.get("address")]
print(f"RESUME-REST contracts: {len(rest)} (already read: {len(out['reread'])})", flush=True)
with ThreadPoolExecutor(max_workers=10) as ex:
    for name, d in ex.map(read_lean, rest):
        out["reread"][name] = d
        save()

tc_items = []
for k, v in track_c.items():
    if k in out["track_c"]: continue
    a = v.get("address") or v.get("sale") or v.get("token")
    if a and isinstance(a, str) and a.startswith("0x"):
        tc_items.append((k, a))
print(f"RESUME-TRACK_C items: {len(tc_items)} (already read: {len(out['track_c'])})", flush=True)
with ThreadPoolExecutor(max_workers=10) as ex:
    for name, d in ex.map(read_tc, tc_items):
        out["track_c"][name] = d
        save()

print(f"REREAD-RESUME DONE in {time.time()-T0:.1f}s reread={len(out['reread'])} track_c={len(out['track_c'])}", flush=True)
