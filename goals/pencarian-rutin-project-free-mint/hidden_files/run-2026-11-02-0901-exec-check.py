#!/usr/bin/env python3
"""Fresh exec-check for 6 strong-lead promotions, run 2026-11-02 09:01 WIB. Read-only."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0), None
        except Exception as e: err = f"{type(e).__name__}: {str(e)[:160]}"
    return None, err
def block():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
    return None
TARGETS = {
 "Lensorb": "0x1edfd1e6c6b132e88f5b09b1dbe025037b5b0539",
 "Hotpotsage": "0xEbAdb5Be9692b0BF25E8A5F3351C35DdC58f195d",
 "Plutopop": "0xE4cA7AaA82253717C0d897C10d58D59821631509",
 "Ghoulipop": "0xb2d236EC0473792eC6727e5bf41084Df3eA0137F",
 "Servobun": "0xbd297cb5158F4DcA02C336A59556FDBfa6609A70",
 "Xianyulo": "0x5bF46eF8E5e09fFFfd928e30077b4d4674CBA4b0",
}
tests = [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""), ("MAX_SUPPLY()", ""),
 ("mintOpen()", ""), ("mintedBy(address)", enc_addr(USER)[2:]), ("freeUsed(address)", enc_addr(USER)[2:]),
 ("freeLeft(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:]),
 ("AGENT_ID()", "")]
out = {"block": block()}
for name, addr in TARGETS.items():
    d = {}
    for fn, arg in tests:
        v, e = call(addr, sel(fn) + arg)
        try: iv = int(v, 16) if v else None
        except Exception: iv = None
        d[fn] = {"int": iv, "raw": v, "error": e if v is None else None}
    v, e = call(addr, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(1)[2:])
    d["quote_user_1"] = {"raw": v, "error": e}
    out[name] = d
print(json.dumps(out, indent=1))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0901-exec-check.json", "w"), indent=1)
