#!/usr/bin/env python3
"""Fresh read of GiraffeValley 0x9F589ABd36E702129E5D33aE0d0C961F8D9f9Ca0
for run 0331 — early lead from backfill, already reported by companion job.
This run only verifies fresh state; report only on promotion/status change.
Read-only."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak

ADDR = "0x9F589ABd36E702129E5D33aE0d0C961F8D9f9Ca0"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc-dataseed.binance.org/"
OUT = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-07-0331-giraffe-check.json"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")

calls = {
    "name()": sel("name()"),
    "symbol()": sel("symbol()"),
    "totalSupply()": sel("totalSupply()"),
    "totalMinted()": sel("totalMinted()"),
    "MAX_SUPPLY()": sel("MAX_SUPPLY()"),
    "FREE_POOL()": sel("FREE_POOL()"),
    "freeRemaining()": sel("freeRemaining()"),
    "FREE_PER_WALLET()": sel("FREE_PER_WALLET()"),
    "freeMinted()": sel("freeMinted()"),
    "mintOpen()": sel("mintOpen()"),
    "saleActive()": sel("saleActive()"),
    "saleEnded()": sel("saleEnded()"),
    "gate()": sel("gate()"),
    "freeMintCount(address)": sel("freeMintCount(address)") + enc(USER),
    "balanceOf(address)": sel("balanceOf(address)") + enc(USER),
    "quote(address,uint256)": sel("quote(address,uint256)") + enc(USER) + enc_u(1),
    "mintable(address,uint256)": sel("mintable(address,uint256)") + enc(USER) + enc_u(1),
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
json.dump(out, open(OUT, "w"), indent=1)
