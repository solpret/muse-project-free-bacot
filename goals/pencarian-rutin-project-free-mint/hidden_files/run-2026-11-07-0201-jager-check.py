#!/usr/bin/env python3
"""Focused on-chain check of EARLY lead Jager Agent Pass
0x951f705feB9dCc95D58b445BE58b869724E50707 (first-seen run 0201).
Read-only: eth_call views + first-mint log lookup via Ankr.
Never preview/mint/approve/sign."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
from Crypto.Hash import keccak

ADDR = "0x951f705feB9dCc95D58b445BE58b869724E50707"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc-dataseed.binance.org/"
OUT = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-07-0201-jager-check.json"

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
    "FREE_SUPPLY()": sel("FREE_SUPPLY()"),
    "freeSupply()": sel("freeSupply()"),
    "freeMinted()": sel("freeMinted()"),
    "freeClaimed()": sel("freeClaimed()"),
    "freeLeft()": sel("freeLeft()"),
    "mintOpen()": sel("mintOpen()"),
    "saleActive()": sel("saleActive()"),
    "saleEnded()": sel("saleEnded()"),
    "mintStart()": sel("mintStart()"),
    "mintEnd()": sel("mintEnd()"),
    "PRICE()": sel("PRICE()"),
    "price()": sel("price()"),
    "gate()": sel("gate()"),
    "AGENT_ID()": sel("AGENT_ID()"),
    "agentRegistry()": sel("agentRegistry()"),
    "owner()": sel("owner()"),
    "freeClaimed(address)": sel("freeClaimed(address)") + enc(USER),
    "freeMintCount(address)": sel("freeMintCount(address)") + enc(USER),
    "balanceOf(address)": sel("balanceOf(address)") + enc(USER),
    "quote(address,uint256)": sel("quote(address,uint256)") + enc(USER) + enc_u(0),
    "quote(address,uint256)_1": sel("quote(address,uint256)") + enc(USER) + enc_u(1),
    "mintable(address,uint256)": sel("mintable(address,uint256)") + enc(USER) + enc_u(1),
}
out = {"contract": ADDR}
for name, data in calls.items():
    try:
        r = _single(EP, "eth_call", [{"to": ADDR, "data": data}, "latest"], 10, retries=0)
        out[name] = r
    except Exception as e:
        out[name] = f"ERROR: {e}"
    time.sleep(0.15)
try:
    b = _single(EP, "eth_blockNumber", [], 10, retries=0)
    out["_block"] = int(b, 16)
except Exception as e:
    out["_block"] = f"ERROR: {e}"

# First mint on-chain: Transfer logs from zero address, first block 132063335
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
try:
    body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(132063335),
        "toBlock": hex(132063335), "pageSize": 1000, "decodeLogs": False,
        "topics": [TRANSFER, ZERO]}, timeout=30)
    logs = [l for l in body.get("result", {}).get("logs", [])
            if l.get("address", "").lower() == ADDR.lower()]
    out["first_mint_logs_block_132063335"] = [
        {"tx": l.get("transactionHash"), "to": ("0x" + l.get("topics", [""])[2][-40:]) if len(l.get("topics", [])) > 2 else None,
         "tokenId": int(l.get("topics", ["0x0"])[3], 16) if len(l.get("topics", [])) > 3 else None}
        for l in logs]
    out["first_mint_count_block"] = len(logs)
except Exception as e:
    out["first_mint_logs_error"] = str(e)
# Block timestamp of first mint block
try:
    blk = _single(EP, "eth_getBlockByNumber", [hex(132063335), False], 10, retries=0)
    out["first_block_timestamp"] = int(blk["timestamp"], 16)
except Exception as e:
    out["first_block_timestamp_error"] = str(e)
print(json.dumps(out, indent=1))
json.dump(out, open(OUT, "w"), indent=1)
