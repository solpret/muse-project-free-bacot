#!/usr/bin/env python3
"""Run 0801: probe Agent Creatures + Data Synth + Crown Race Pass. Read-only."""
import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0801"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com", "https://bsc-dataseed2.bnbchain.org"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def raw(to, data):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=6) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception: continue
    return None
def call(to, sig, args=""): return raw(to, sel(sig) + args)
def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=6) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None
VIEWS = ["totalSupply()", "totalMinted()", "freeMinted()", "freeClaimed()", "freeLeft()", "FREE_SUPPLY()", "MAX_SUPPLY()", "PRICE()", "mintOpen()", "mintedBy(address)", "freeUsed(address)", "balanceOf(address)", "quote(address,uint256)", "costOf(address,uint256)", "agentRegistry()", "AGENT_ID()", "owner()"]
ITEMS = {
 "Agent Creatures": ("0xF7245511A890a42F911c776824c665E2da3cedb3", VIEWS),
 "Data Synth": ("0x7Bd19ee3c72b4544787EbA0ebD655e1376FE3642", VIEWS),
 "Crown Race Pass": ("0x924B1c9203EBC3EE3D4Fd2Af758B2DBDD3856e0c", VIEWS),
}
def read_item(args):
    name, (addr, views) = args
    d = {"address": addr}
    for sig in views:
        key = sig.split("(")[0]
        if "address" in sig and "uint256" in sig:
            v = call(addr, sig, enc(USER) + enc_uint(1)); key += "_user_1"
        elif "address" in sig:
            v = call(addr, sig, enc(USER)); key += "_user"
        else:
            v = call(addr, sig)
        d[key] = v
    print(name, d, flush=True)
    return name, d
blk = block()
print("BLOCK", blk, flush=True)
out = {"block": blk, "probe": {}}
with ThreadPoolExecutor(max_workers=8) as ex:
    for name, d in ex.map(read_item, list(ITEMS.items())):
        out["probe"][name] = d
        json.dump(out, open(f"{BASE}/run-{TS}-early-probe3.json", "w"), indent=1)
print("DONE", flush=True)
