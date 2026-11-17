#!/usr/bin/env python3
"""Leg 3 on-chain verification for new S1 contract 0x250e800025a9a7861970e253bab6975a57f80567 (Wuyuhive), hot-leg run 2026-11-07 03:39 WIB. Read-only."""
import json, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0x250e800025a9a7861970e253bab6975a57f80567"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed.binance.org", "https://rpc.ankr.com/bsc",
        "https://bsc-dataseed-public.bnbchain.org"]
out = {"contract": ADDR, "name": "Wuyuhive"}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(data, rpcs=RPCS):
    for rpc in rpcs:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": ADDR, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=6) as r:
                o = json.load(r)
            if "error" in o:
                continue
            v = o.get("result")
            return v, rpc
        except Exception:
            continue
    return None, None

def call(sig, args=""):
    return raw(sel(sig) + args)

def u256(v):
    if v is None or v == "0x" or v == "":
        return None
    try:
        return int(v, 16)
    except Exception:
        return v

def decode_string(v):
    # ABI string: offset(32) + len(32) + data
    if not v or len(v) < 130:
        return None
    try:
        ln = int(v[66:130], 16)
        b = bytes.fromhex(v[130:130 + ln * 2])
        return b.decode("utf-8", "replace")
    except Exception as e:
        return f"<decode error {e}>"

def decode_bool(v):
    if v is None:
        return None
    try:
        return int(v, 16) != 0
    except Exception:
        return v

def decode_addr(v):
    if not v:
        return None
    try:
        return "0x" + v[-40:]
    except Exception:
        return v

views = {
    "name": ("name()", decode_string),
    "symbol": ("symbol()", decode_string),
    "totalSupply": ("totalSupply()", u256),
    "FREE_SUPPLY": ("FREE_SUPPLY()", u256),
    "FREE_PER_WALLET": ("FREE_PER_WALLET()", u256),
    "MAX_SUPPLY": ("MAX_SUPPLY()", u256),
    "MAX_PER_WALLET": ("MAX_PER_WALLET()", u256),
    "PRICE": ("PRICE()", u256),
    "AGENT_ID": ("AGENT_ID()", decode_addr),
    "freeClaimed_total": ("freeClaimed()", u256),
    "mintOpen": ("mintOpen()", decode_bool),
    "owner": ("owner()", decode_addr),
    "contractURI": ("contractURI()", decode_string),
    "quote_user_1": ("quote(address,uint256)", u256, enc(USER) + enc_uint(1)),
    "freeLeft_user": ("freeLeft(address)", u256, enc(USER)),
    "freeUsed_user": ("freeUsed(address)", u256, enc(USER)),
    "freeFor_user_1": ("freeFor(address,uint256)", u256, enc(USER) + enc_uint(1)),
    "mintedBy_user": ("mintedBy(address)", u256, enc(USER)),
}
res = {}
for key, spec in views.items():
    sig, dec = spec[0], spec[1]
    args = spec[2] if len(spec) > 2 else ""
    v, rpc = call(sig, args)
    res[key] = dec(v)
    res[key + "_via"] = rpc
out["views"] = res

# Block number for reference
blk = None
for rpc in RPCS:
    try:
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
        req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as r:
            o = json.load(r)
        blk = int(o["result"], 16)
        out["block"] = blk
        out["block_via"] = rpc
        break
    except Exception:
        continue

# First-mint probe: Transfer events from zero address to this contract, recent 3000 blocks (~2.5h)
# Topic0 Transfer, topic1 = zero address, topic2 = any. Use eth_getLogs with address filter.
def get_logs(from_block, to_block):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                               "params": [{"fromBlock": hex(from_block), "toBlock": hex(to_block),
                                           "address": ADDR,
                                           "topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                                                      "0x0000000000000000000000000000000000000000000000000000000000000000"]}]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                o = json.load(r)
            if "error" in o:
                return None, rpc, o["error"]
            return o.get("result", []), rpc, None
        except Exception as e:
            continue
    return None, None, "transport"

if blk:
    logs, lrpc, lerr = get_logs(max(0, blk - 3000), blk)
    out["first_mint_probe"] = {"window_blocks": 3000, "from": blk - 3000, "to": blk,
                               "via": lrpc, "error": lerr,
                               "n_mint_transfers": len(logs) if logs is not None else None,
                               "first": logs[0] if logs else None}
json.dump(out, open(f"{BASE}/leg3-0339-wuyuhive.json", "w"), indent=1)
print(json.dumps(out, indent=1))
