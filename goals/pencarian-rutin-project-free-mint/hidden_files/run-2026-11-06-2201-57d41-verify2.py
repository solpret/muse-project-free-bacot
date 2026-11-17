#!/usr/bin/env python3
"""Lean verify 0x57D41Ff... run 2201: parallel single-RPC reads, critical views only."""
import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0x57D41Ff4895A19f518a0Ec3A2Fa56284a85f5689"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
RPC = "https://bsc-dataseed1.bnbchain.org"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")

def raw(data, method="eth_call", params=None):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                       "params": params or [{"to": ADDR, "data": data}, "latest"]}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            out = json.load(r)
        if "error" in out: return None
        return out["result"]
    except Exception:
        return None

def call(sig, args=""):
    return raw(sel(sig) + args)

def as_int(v):
    try: return int(v, 16)
    except Exception: return None
def as_addr(v):
    if v and len(v) >= 66: return "0x" + v[-40:]
    return None
def as_str(v):
    if not v or len(v) < 130: return None
    try:
        ln = int(v[66:130], 16)
        return bytes.fromhex(v[130:130 + ln * 2]).decode("utf-8", "replace")
    except Exception:
        return None

jobs = {
    "name()": ("str", ""), "symbol()": ("str", ""), "decimals()": ("int", ""),
    "totalSupply()": ("int", ""), "mintOpen()": ("int", ""),
    "freeLeft()": ("int", ""), "PRICE()": ("int", ""),
    "max_supply()": ("int", ""), "MAX_SUPPLY()": ("int", ""),
    "free_per_wallet()": ("int", ""), "totalMints()": ("int", ""),
    "mint_deadline()": ("int", ""), "MINT_DEADLINE()": ("int", ""),
    "agent_id()": ("addr", ""), "factory()": ("addr", ""),
    "pair()": ("addr", ""), "tradingOpen()": ("int", ""),
    "mintedBy(address)": ("int", enc(USER)),
    "balanceOf(address)": ("int", enc(USER)),
    "quote(address,uint256)": ("raw", enc(USER) + format(1, "064x")),
}
with ThreadPoolExecutor(max_workers=10) as ex:
    futs = {sig: ex.submit(call, sig, args) for sig, (k, args) in jobs.items()}
    code_fut = ex.submit(raw, "0x", "eth_getCode", [ADDR, "latest"])
    block_fut = ex.submit(raw, "0x", "eth_blockNumber", [])
    res = {}
    for sig, (kind, _) in jobs.items():
        v = futs[sig].result()
        if v is None: res[sig] = None
        elif kind == "int": res[sig] = as_int(v)
        elif kind == "addr": res[sig] = as_addr(v)
        elif kind == "str": res[sig] = as_str(v)
        else: res[sig] = v
    code = code_fut.result()
    blk = block_fut.result()
res["block"] = int(blk, 16) if blk else None
res["code_len"] = len(code) - 2 if code else None
res["registry_bytes_in_code"] = bool(code and REGISTRY[2:].lower() in code.lower())
json.dump(res, open(f"{BASE}/run-2026-11-06-2201-57d41-verify.json", "w"), indent=1)
print(json.dumps(res, indent=1))
