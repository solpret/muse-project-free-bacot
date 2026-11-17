#!/usr/bin/env python3
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
    return None
def iv(v):
    try: return int(v, 16) if v else None
    except Exception: return None
out = {}
for ep in EPS:
    try: out["block"] = int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16); break
    except Exception: pass
for name, addr in [("Opera Agent", "0x32ddd7d98bB711976cCfE19548Df52D0cdeC197c"),
                   ("Silk Agent", "0xF888787f39dD5a5adCEC1b0d9833cF40a655c60e")]:
    r = {}
    for fn, arg in [("totalMinted()", ""), ("FREE_SUPPLY()", ""), ("MAX_SUPPLY()", ""), ("PRICE()", ""),
                    ("mintedBy(address)", enc_addr(USER)), ("costFor(uint256)", "0000000000000000000000000000000000000000000000000000000000000001")]:
        r[fn] = iv(call(addr, sel(fn) + arg))
    out[name] = r
    print(name, r)
json.dump(out, open(BASE + "run-2026-11-03-0201-opera-silk.json", "w"), indent=1)
print("BLOCK", out["block"])
