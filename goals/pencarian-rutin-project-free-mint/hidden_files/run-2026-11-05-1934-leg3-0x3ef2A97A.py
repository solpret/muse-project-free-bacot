#!/usr/bin/env python3
"""Leg 3 probe run 1934: S1 new contract 0x3ef2A97A... — fast on-chain verification.
Read-only. Writes run-2026-11-05-1934-leg3-0x3ef2A97A.json."""
import json, urllib.request, datetime
from Crypto.Hash import keccak

RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x3ef2A97Abf2E43182eACAe323B82d2CAC2132C6A"
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def rpc(method, params, timeout=8):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: out = json.load(r)
            if "error" in out: return None
            return out["result"]
        except Exception:
            continue
    return None

def call(sig, args=""):
    v = rpc("eth_call", [{"to": ADDR, "data": sel(sig) + args}, "latest"])
    if not v or v == "0x": return None
    try: return int(v, 16)
    except Exception: return v

def call_str(sig, args=""):
    v = rpc("eth_call", [{"to": ADDR, "data": sel(sig) + args}, "latest"])
    if not v or v == "0x": return None
    try:
        b = bytes.fromhex(v[2:])
        off = int.from_bytes(b[32:64], "big")
        ln = int.from_bytes(b[64:96], "big")
        return b[96:96+ln].decode()
    except Exception:
        return v

blk = rpc("eth_blockNumber", [])
blk = int(blk, 16) if blk else None
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
out = {"block": blk, "now_wib": now.strftime("%Y-%m-%d %H:%M:%S"), "address": ADDR}
out["name"] = call_str("name()")
out["symbol"] = call_str("symbol()")
out["AGENT_ID"] = call("AGENT_ID()")
out["owner"] = call("owner()")
out["FREE_SUPPLY"] = call("FREE_SUPPLY()")
out["FREE_PER_WALLET"] = call("FREE_PER_WALLET()")
out["MAX_SUPPLY"] = call("MAX_SUPPLY()")
out["MAX_PER_WALLET"] = call("MAX_PER_WALLET()")
out["PRICE"] = call("PRICE()")
out["mintOpen"] = call("mintOpen()")
out["totalSupply"] = call("totalSupply()")
out["freeClaimed"] = call("freeClaimed()")
out["freeLeft_user"] = call("freeLeft(address)", enc(USER))
out["freeUsed_user"] = call("freeUsed(address)", enc(USER))
out["freeFor_user_1"] = call("freeFor(address,uint256)", enc(USER) + enc_uint(1))
out["quote_user_1"] = call("quote(address,uint256)", enc(USER) + enc_uint(1))
out["mintedBy_user"] = call("mintedBy(address)", enc(USER))
out["balanceOf_user"] = call("balanceOf(address)", enc(USER))

# First mint: Transfer events from zero address, last ~4000 blocks (contract verified 19:23 WIB today)
TRANSFER = "0x" + keccak.new(digest_bits=256, data=b"Transfer(address,address,uint256)").hexdigest()
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
first = None
if blk:
    logs = rpc("eth_getLogs", [{"fromBlock": hex(max(0, blk-4000)), "toBlock": "latest",
                                "address": ADDR, "topics": [TRANSFER, ZERO_TOPIC]}], timeout=15)
    if logs:
        first_block = min(int(l["blockNumber"], 16) for l in logs)
        out["first_mint_block"] = first_block
        out["mint_log_count_window"] = len(logs)
        bh = rpc("eth_getBlockByNumber", [hex(first_block), False], timeout=8)
        if bh:
            ts = int(bh["timestamp"], 16)
            dt = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7)))
            out["first_mint_wib"] = dt.strftime("%Y-%m-%d %H:%M:%S")
            out["age_minutes"] = round((now.timestamp() - ts) / 60, 1)
print(json.dumps(out, indent=1))
json.dump(out, open(HF + "run-2026-11-05-1934-leg3-0x3ef2A97A.json", "w"), indent=1)
