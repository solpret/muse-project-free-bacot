#!/usr/bin/env python3
"""Hot-leg re-read 2026-11-07 18:34 WIB. Read-only; resumes item list from 1829 reread file."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch, race
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-07-1834"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def batch_views(addr, views):
    calls, keys = [], []
    for sig in views:
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        elif "(uint256)" in sig:
            data = sel(sig) + enc_uint(1); key = base + "_1"
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
def single(addr, sig, arg=""):
    data = sel(sig) + arg
    for ep in EPS:
        try:
            from fast_rpc import _single
            v = _single(ep, "eth_call", [{"to": addr, "data": data}, "latest"], 8, retries=0)
            return to_int(v)
        except Exception:
            continue
    return None
LEAN = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)", "freeClaimed(address)"]
MINIMAL = ["totalSupply()", "balanceOf(address)"]
ITEMS = {
 "Orchidia": "0x09bcdd97186f6f37521bd1b281d329e48ac54b89",
 "Agent Goats": "0x0E9E0a3B46dC0d36A1Ab64f553Dd8A0693E6aAa6",
 "Tacotron": "0x05debe4445232205ae7e79d02cb5de5aa0641eff",
 "Agent Frogs": "0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31",
 "Wuyuhive": "0x250e800025a9a7861970e253bab6975a57f80567",
 "Thronemind": "0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90",
}
LEADS = {
 "CipherAgent": "0x158b5e25015758a94703A27c152889451E5d52E5",
 "MarsAgent": "0x2231FdAe405c33dc4993f8C577c453802FF1AcE9",
}
out = {"block": None, "items": {}, "leads": {}, "started_wib": "2026-11-07 18:34 WIB"}
try:
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=8)[0], 16)
except Exception:
    try: out["block"] = int(race("eth_blockNumber", []), 16)
    except Exception as e: print("BLOCK-FAIL", e, flush=True)
print("BLOCK", out["block"], flush=True)
for name, addr in ITEMS.items():
    d = {"address": addr}
    got = batch_views(addr, LEAN)
    if got is None:
        got = batch_views(addr, MINIMAL)
        if got is not None:
            d.update(got)
            for k in ["totalMinted","freeClaimed","freeMinted","FREE_SUPPLY","MAX_SUPPLY","mintOpen","freeClaimed_user"]:
                d.setdefault(k, None)
            d["_fallback"] = "minimal"
        else:
            for k in ["totalSupply","totalMinted","freeClaimed","freeMinted","FREE_SUPPLY","MAX_SUPPLY","mintOpen","balanceOf_user","freeClaimed_user"]:
                d[k] = None
            d["_fallback"] = "failed"
    else:
        d.update(got); d["_fallback"] = "lean"
    out["items"][name] = d
    print(f"LEAN {name} ts={d.get('totalSupply')} fc={d.get('freeClaimed')} bal={d.get('balanceOf_user')} fb={d['_fallback']}", flush=True)
for name, addr in LEADS.items():
    d = {"address": addr}
    d["totalMints"] = single(addr, "totalMints()")
    d["MAX_MINTS"] = single(addr, "MAX_MINTS()")
    d["mintOpen"] = single(addr, "mintOpen()")
    d["freeLeft_user"] = single(addr, "freeLeft(address)", enc(USER))
    d["quote_user"] = single(addr, "quote(address,uint256)", enc(USER) + enc_uint(1))
    d["mintedBy_user"] = single(addr, "mintedBy(address)", enc(USER))
    d["balanceOf_user"] = single(addr, "balanceOf(address)", enc(USER))
    out["leads"][name] = d
    print(f"LEAD {name} totalMints={d['totalMints']} mintOpen={d['mintOpen']} freeLeft={d['freeLeft_user']} quote={d['quote_user']} mintedBy={d['mintedBy_user']} bal={d['balanceOf_user']}", flush=True)
json.dump(out, open(f"{BASE}/hot-leg-2026-11-07-1834-reread.json", "w"), indent=1)
print("SAVED", flush=True)
