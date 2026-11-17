#!/usr/bin/env python3
"""Focused re-verification for Agent Panda 0x2820... (backfill window
132116366-132118974). Read-only. Retries the free-path views that
transport-failed in triage, plus a binary search for the TRUE first mint
(totalMinted 8769 vs 12 mints observed in-window -> bulk predates window).
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import race
from Crypto.Hash import keccak
from ankr import ankr_post

ADDR = "0x2820e61eD78aC29F52eDAE05F01aB552307b907C"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_NP = USER[2:].lower()
ZERO_TOPIC = "0x" + "0" * 64
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def call(data, label):
    try:
        r = race("eth_call", [{"to": ADDR, "data": data}, "latest"])
        if isinstance(r, str) and r.startswith("0x") and len(r) >= 66:
            v = int(r, 16)
            print(f"{label}: {v} (raw {r[:66]})")
            return v
        print(f"{label}: revert-or-short: {str(r)[:150]}")
        return None
    except Exception as e:
        print(f"{label}: TRANSPORT-FAIL {type(e).__name__}: {str(e)[:150]}")
        return None

print("== free-path / price / supply (retry) ==")
call(sel("free_per_wallet_agent()"), "free_per_wallet_agent()")
call(sel("freeRemainingFor(address)") + USER_NP, "freeRemainingFor(user)")
call(sel("freeMintedBy(address)") + USER_NP, "freeMintedBy(user)")
call(sel("mintedBy(address)") + USER_NP, "mintedBy(user)")
call(sel("mint_price()"), "mint_price()")
call(sel("max_supply()"), "max_supply()")
call(sel("totalMinted()"), "totalMinted()")
call(sel("mintOpen()"), "mintOpen()")
call(sel("agentRegistry()"), "agentRegistry()")
call(sel("registry()"), "registry()")
call(sel("agentId()"), "agentId()")

print("== true first mint: Ankr getLogs Transfer from-zero, binary search ==")
def has_mint(lo, hi):
    try:
        body = ankr_post("ankr_getLogs", [{"fromBlock": hex(lo), "toBlock": hex(hi),
            "address": ADDR, "topics": [TRANSFER, ZERO_TOPIC]}], timeout=30)
        logs = body.get("result", []) if isinstance(body, dict) else []
        return len(logs), (logs[0]["blockNumber"] if logs else None)
    except Exception as e:
        print(f"  getLogs {lo}-{hi} FAIL {type(e).__name__}: {str(e)[:120]}")
        return None, None

# head now
try:
    head = int(race("eth_blockNumber", []), 16)
except Exception as e:
    head = 132119742
    print("head via fallback", head)
print("head:", head)
# check recent 200k blocks first: any mint at all before window?
n, first = has_mint(131900000, 132116365)
print(f"mints in 131900000-132116365 (pre-window, backfill-covered range): {n} first={first}")
