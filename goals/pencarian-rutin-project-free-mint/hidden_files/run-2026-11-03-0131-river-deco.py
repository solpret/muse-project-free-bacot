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
targets = {
 "River Agent": ("0x211AF92EF42641ef4fD94EEccb88FAe1e7e51667", ["totalMinted()", "totalSupply()", "FREE_SUPPLY()", "freeMinted()", "mintedBy(address)", "costFor(uint256)"]),
 "Deco Agent": ("0xfe8D985cB19380805B01cf7FCFc65c3819e030C8", ["totalMinted()", "totalSupply()", "FREE_SUPPLY()", "freeMinted()", "mintedBy(address)", "costFor(uint256)"]),
 "Aura Agents": ("0xacc6e2F1aaE42B2E5FF2758Ff078E4B1bfAc7DB1", ["totalMinted()", "totalSupply()", "FREE_SUPPLY()", "freeMinted()", "mintedBy(address)", "costFor(uint256)"]),
 "Moth Agent": ("0x872d76921a88Ab2a8477Ab1492e7c4C430685491", ["totalMinted()", "totalSupply()", "FREE_SUPPLY()", "freeMinted()", "mintedBy(address)", "costFor(uint256)"]),
 "Fangcount-quote": ("0x75A2D4f6f158240CB5Fd4B4f866cEA85b143D165", ["quote(address,uint256)", "freeClaimed()", "FREE_SUPPLY()", "mintOpen()"]),
}
out = {"block": None}
for ep in EPS:
    try: out["block"] = int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16); break
    except Exception: pass
for name, (addr, fns) in targets.items():
    r = {}
    for fn in fns:
        arg = ""
        if fn == "mintedBy(address)": arg = enc_addr(USER)
        elif fn == "costFor(uint256)": arg = "0000000000000000000000000000000000000000000000000000000000000001"
        elif fn == "quote(address,uint256)": arg = enc_addr(USER) + "0000000000000000000000000000000000000000000000000000000000000001"
        r[fn] = iv(call(addr, sel(fn) + arg))
    out[name] = r
    print(name, r)
json.dump(out, open(BASE + "run-2026-11-03-0131-river-deco.json", "w"), indent=1)
print("BLOCK", out["block"])
