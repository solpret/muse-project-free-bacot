#!/usr/bin/env python3
"""Leg 3 on-chain verification for 0x3807470b75f332461d8aae40501e83a7e1fe1819 (Boltbook S1, run 2026-11-07 02:04). Read-only."""
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

def raw(to, data, timeout=6):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                o = json.load(r)
            if "error" in o:
                continue
            v = o.get("result")
            if v is None or v == "0x":
                return None
            return v
        except Exception:
            continue
    return "transport-fail"

def dec_str(hexv):
    if not hexv or hexv == "transport-fail":
        return hexv
    try:
        b = bytes.fromhex(hexv[2:])
        if len(b) < 64:
            return hexv
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

def call(sig, args=""):
    return raw(ADDR, sel(sig) + args)

tasks = {
    "name": ("str", lambda: call("name()")),
    "symbol": ("str", lambda: call("symbol()")),
    "MAX_SUPPLY": ("uint", lambda: call("MAX_SUPPLY()")),
    "FREE_SUPPLY": ("uint", lambda: call("FREE_SUPPLY()")),
    "FREE_PER_WALLET": ("uint", lambda: call("FREE_PER_WALLET()")),
    "PRICE": ("uint", lambda: call("PRICE()")),
    "mintOpen": ("uint", lambda: call("mintOpen()")),
    "totalSupply": ("uint", lambda: call("totalSupply()")),
    "freeClaimed": ("uint", lambda: call("freeClaimed()")),
    "freeFor_user_1": ("uint", lambda: call("freeFor(address,uint256)", enc(USER) + enc_uint(1))),
    "freeLeft_user": ("uint", lambda: call("freeLeft(address)", enc(USER))),
    "freeUsed_user": ("uint", lambda: call("freeUsed(address)", enc(USER))),
    "quote_user_1": ("uint", lambda: call("quote(address,uint256)", enc(USER) + enc_uint(1))),
    "mintedBy_user": ("uint", lambda: call("mintedBy(address)", enc(USER))),
    "balanceOf_user": ("uint", lambda: call("balanceOf(address)", enc(USER))),
    "owner": ("raw", lambda: call("owner()")),
    "AGENT_ID": ("raw", lambda: call("AGENT_ID()")),
    "contractURI": ("str", lambda: call("contractURI()")),
    "tokenURI_1": ("str", lambda: call("tokenURI(uint256)", enc_uint(1))),
    "IMAGE": ("raw", lambda: call("IMAGE()")),
}

def run_one(item):
    k, (typ, fn) = item
    v = fn()
    if typ == "str":
        v = dec_str(v)
    elif typ == "uint":
        v = dec_uint(v)
    return k, v

with ThreadPoolExecutor(max_workers=10) as ex:
    res = dict(ex.map(run_one, tasks.items()))

# block number
blk = None; via = None
for rpc in RPCS:
    try:
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
        req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as r:
            o = json.load(r)
        if "result" in o:
            blk = int(o["result"], 16); via = rpc; break
    except Exception:
        continue
res["block"] = blk; res["via"] = via
json.dump(res, open(f"{BASE}/hot-leg-run-2026-11-07-0204-leg3-3807.json", "w"), indent=1)
print(json.dumps(res, indent=1))
