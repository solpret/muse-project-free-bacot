#!/usr/bin/env python3
"""Confirm Swarmdrake 0x3807... sold-out + retry failed reads + first-mint age. Read-only."""
import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

ADDR = "0x3807470b75f332461d8aae40501e83a7e1fe1819"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc-dataseed.binance.org",
        "https://bsc.publicnode.com", "https://rpc.ankr.com/bsc",
        "https://bsc-dataseed-public.bnbchain.org"]
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def rpc_call(rpc, method, params, timeout=8):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        o = json.load(r)
    if "error" in o:
        raise RuntimeError(str(o["error"])[:120])
    return o.get("result")

def call(sig, args=""):
    data = sel(sig) + args
    for rpc in RPCS:
        try:
            v = rpc_call(rpc, "eth_call", [{"to": ADDR, "data": data}, "latest"])
            if v is None or v == "0x":
                return None, rpc
            return v, rpc
        except Exception:
            continue
    return "transport-fail", None

def dec_str(hexv):
    if not hexv or hexv == "transport-fail":
        return hexv
    try:
        b = bytes.fromhex(hexv[2:])
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode("utf-8", "replace")
    except Exception as e:
        return f"decode-fail:{e}"

def dec_uint(hexv):
    if not hexv or hexv == "transport-fail":
        return hexv
    try:
        return int(hexv, 16)
    except Exception:
        return hexv

out = {}
for name, sig, args, dec in [
    ("totalSupply", "totalSupply()", "", dec_uint),
    ("MAX_SUPPLY", "MAX_SUPPLY()", "", dec_uint),
    ("FREE_SUPPLY", "FREE_SUPPLY()", "", dec_uint),
    ("freeClaimed", "freeClaimed()", "", dec_uint),
    ("mintOpen", "mintOpen()", "", dec_uint),
    ("freeUsed_user", "freeUsed(address)", enc(USER), dec_uint),
    ("symbol", "symbol()", "", dec_str),
    ("tokenURI_1", "tokenURI(uint256)", enc_uint(1), dec_str),
    ("quote_user_1", "quote(address,uint256)", enc(USER) + enc_uint(1), dec_uint),
]:
    v, via = call(sig, args)
    out[name] = {"value": dec(v), "via": via}

# First-mint age: Transfer events from zero address, chunked backwards from latest block.
blk = None
for rpc in RPCS:
    try:
        blk = int(rpc_call(rpc, "eth_blockNumber", []), 16)
        break
    except Exception:
        continue
out["latest_block"] = blk
topic_transfer = "0x" + keccak.new(digest_bits=256, data=b"Transfer(address,address,uint256)").hexdigest()
topic_zero = "0x" + "0" * 64
first_mint = None
if blk:
    CH = 5000
    end = blk
    start = max(0, blk - 40000)  # ~33h window
    while end > start and first_mint is None:
        frm = max(start, end - CH + 1)
        found = None
        for rpc in RPCS:
            try:
                logs = rpc_call(rpc, "eth_getLogs", [{"fromBlock": hex(frm), "toBlock": hex(end),
                                                       "address": ADDR, "topics": [topic_transfer, topic_zero]}], timeout=10)
                if logs:
                    found = logs
                    break
            except Exception:
                continue
        if found:
            first_mint = {"block": int(found[0]["blockNumber"], 16), "tx": found[0]["transactionHash"],
                          "count_in_chunk": len(found)}
            break
        end = frm - 1
out["first_mint"] = first_mint
if first_mint:
    for rpc in RPCS:
        try:
            b = rpc_call(rpc, "eth_getBlockByNumber", [hex(first_mint["block"]), False])
            out["first_mint_block_ts"] = int(b["timestamp"], 16)
            break
        except Exception:
            continue
json.dump(out, open(f"{BASE}/hot-leg-run-2026-11-07-0204-leg3-3807-confirm.json", "w"), indent=1)
print(json.dumps(out, indent=1))
