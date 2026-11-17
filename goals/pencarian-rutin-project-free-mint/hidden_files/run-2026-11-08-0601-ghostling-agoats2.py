#!/usr/bin/env python3
"""Retry lean verify Ghostling + Agent Goats + Voltoad (run 0601). Read-only.
Sequential, one endpoint, 15s timeout; few views."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed.binance.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
VIEWS = ["name()", "symbol()", "totalSupply()", "freeClaimed()", "FREE_SUPPLY()",
         "MAX_SUPPLY()", "mintOpen()", "owner()", "balanceOf(address)",
         "freeLeft(address)", "freeUsed(address)"]
def read(addr):
    calls, keys = [], []
    for sig in VIEWS:
        base = sig.split("(")[0]
        if "(address)" in sig:
            calls.append(("eth_call", [{"to": addr, "data": sel(sig) + enc(USER)}, "latest"])); keys.append(base + "_user")
        else:
            calls.append(("eth_call", [{"to": addr, "data": sel(sig)}, "latest"])); keys.append(base)
    calls.append(("eth_call", [{"to": addr, "data": sel("quote(address,uint256)") + enc(USER) + "1".rjust(64, "0")}, "latest"])); keys.append("quote_user1")
    for ep in EPS:
        try:
            res = batch(calls, endpoint=ep, timeout=15)
            d = {"_ep": ep}
            for k, v in zip(keys, res):
                if k in ("name", "symbol"):
                    try:
                        if isinstance(v, str) and v.startswith("0x") and len(v) > 130:
                            ln = int(v[130:194], 16); d[k] = bytes.fromhex(v[194:194+ln*2]).decode(errors="ignore")
                        else: d[k] = v
                    except Exception: d[k] = v
                elif k == "owner":
                    d[k] = ("0x" + v[-40:]) if isinstance(v, str) and len(v) >= 42 else v
                else:
                    d[k] = to_int(v)
            return d
        except Exception as e:
            print(f"  {addr[:10]} via {ep} failed: {str(e)[:100]}", flush=True)
            time.sleep(2)
            continue
    return {"error": "all endpoints failed"}
out = {}
for name, addr in {
  "Ghostling": "0x6a4847cb5f658943222fbd23d2520049f824789d",
  "AgentGoats": "0x0e9e0a3b46dc0d36a1ab64f553dd8a0693e6aaa6",
  "Voltoad": "0xbc95e0a5bb1305958ba3263c6e9943b7a2554757",
}.items():
    print(f"reading {name}...", flush=True)
    out[name] = read(addr); out[name]["address"] = addr
try:
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=10)[0], 16)
except Exception as e:
    out["block"] = f"ERR:{e}"
json.dump(out, open("run-2026-11-08-0601-ghostling-agoats2.json", "w"), indent=1)
for k, v in out.items():
    if isinstance(v, dict): print(k, v)
