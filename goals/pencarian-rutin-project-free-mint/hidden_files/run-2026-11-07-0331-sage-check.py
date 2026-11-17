#!/usr/bin/env python3
"""Fresh read of Sage Trials sale 0xB0d58925E1075c4E4C02B72f4Bbb3656A6f0b3A3
for run 0331 snapshot add (already reported by hot-leg 01:56 WIB; this run
only verifies fresh state + adds to snapshot for tracking). Read-only."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak

ADDR = "0xB0d58925E1075c4E4C02B72f4Bbb3656A6f0b3A3"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc-dataseed.binance.org/"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")

calls = {
    "name()": sel("name()"),
    "symbol()": sel("symbol()"),
    "totalSupply()": sel("totalSupply()"),
    "MAX_SUPPLY()": sel("MAX_SUPPLY()"),
    "mintOpen()": sel("mintOpen()"),
    "saleActive()": sel("saleActive()"),
    "mintStart()": sel("mintStart()"),
    "freeClaimed(address)": sel("freeClaimed(address)") + enc(USER),
    "balanceOf(address)": sel("balanceOf(address)") + enc(USER),
    "quote(address,uint256)": sel("quote(address,uint256)") + enc(USER) + enc_u(0),
    "PRICE()": sel("PRICE()"),
}
out = {}
for name, data in calls.items():
    try:
        r = _single(EP, "eth_call", [{"to": ADDR, "data": data}, "latest"], 10, retries=0)
        out[name] = r
    except Exception as e:
        out[name] = f"ERROR: {e}"
try:
    b = _single(EP, "eth_blockNumber", [], 10, retries=0)
    out["_block"] = int(b, 16)
except Exception as e:
    out["_block"] = f"ERROR: {e}"
print(json.dumps(out, indent=1))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-07-0331-sage-check.json", "w"), indent=1)
