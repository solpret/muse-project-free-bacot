#!/usr/bin/env python3
"""Ninetailix 0x80921572... follow-up run 0231: first-mint age + current state.
READ-ONLY. Block timestamp via dataseed (Ankr returns fake timestamps)."""
import json, sys, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0x809215729bcbff2ef31dea5efd6c12a6b788ba9a"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def sel(sig): return "0x" + keccak(sig.encode()).hex()[:8]
def call(data, to=ADDR):
    for ep in EPS:
        try:
            r = _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 10, retries=0)
            if isinstance(r, str) and r.startswith("0x") and len(r) >= 66: return int(r, 16)
            return None
        except Exception: continue
    return None
def block_ts(n):
    for ep in EPS:
        try:
            b = _single(ep, "eth_getBlockByNumber", [hex(n), False], 10, retries=0)
            if isinstance(b, dict) and b.get("timestamp"):
                ts = int(b["timestamp"], 16)
                return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
        except Exception: continue
    return None
out = {"address": ADDR, "first_mint_block_scan": 131064636}
out["first_mint_time_wib"] = block_ts(131064636)
for v in ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "FREE_PER_WALLET()", "mintOpen()"]:
    out[v] = call(sel(v))
out["freeClaimed(user)"] = call(sel("freeClaimed(address)") + USER[2:].lower().rjust(64, "0"))
out["mintedBy(user)"] = call(sel("mintedBy(address)") + USER[2:].lower().rjust(64, "0"))
out["freeLeft(user)"] = call(sel("freeLeft(address)") + USER[2:].lower().rjust(64, "0"))
out["head"] = int(_single(EPS[0], "eth_blockNumber", [], 10, retries=0), 16)
json.dump(out, open(f"{BASE}/run-2026-11-08-0231-ninetailix.json", "w"), indent=1)
print(json.dumps(out, indent=1), flush=True)
