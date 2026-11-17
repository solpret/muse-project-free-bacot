#!/usr/bin/env python3
"""Run 2101: retry S1-hit 0x5f76cAb7 views via curl transport (dataseed slow tonight)
+ eth_getCode registry-byte check for FMA + hit. Read-only.
Writes run-2026-11-09-2101-hit-retry.json."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return None if v in (None, "0x") else int(v, 16)
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def call(addr, sig, arg=None, arg2=None):
    data = sel(sig)
    if arg is not None: data += enc(arg)
    if arg2 is not None: data += str(arg2).rjust(64, "0")
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                              "params": [{"to": addr, "data": data}, "latest"]})
            if isinstance(r, dict) and "result" in r:
                return to_int(r["result"])
        except Exception:
            continue
    return None

def get_code(addr):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                              "params": [addr, "latest"]})
            if isinstance(r, dict) and "result" in r:
                return r["result"]
        except Exception:
            continue
    return None

out = {"run": "2026-11-09-2101"}
blk = None
for ep in EPS:
    try:
        r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []})
        blk = int(r["result"], 16); break
    except Exception: continue
out["block"] = blk
print("BLOCK", blk, flush=True)

HIT = "0x5f76cAb7B054e088563D5098E17bD0dc430e61aE"
views = {}
for sig in ["name()", "symbol()", "decimals()", "totalSupply()", "freeUsed()", "FREE_SUPPLY()",
            "FREE_SHARES()", "freeSharesRemaining()", "freeMinted()", "totalMinted()",
            "mintPrice()", "price()", "launched()", "launchTime()", "opened()", "mintCount()",
            "MAX_MINTS()", "maxSupply()", "MAX_SUPPLY()"]:
    views[sig] = call(HIT, sig)
for sig in ["freeClaimed(address)", "freeUsed(address)", "hasMinted(address)", "balanceOf(address)",
            "freeSharesClaimed(address)", "minted(address)"]:
    views[sig + "_user"] = call(HIT, sig, USER)
views["quote(address,uint256)_user1"] = call(HIT, "quote(address,uint256)", USER, 1)
views["cost(uint256)_1"] = call(HIT, "cost(uint256)", None, 1) if False else None
for sig in ["agentRegistry()", "registry()", "AGENT_ID()", "agentId()", "REGISTRY()"]:
    views[sig] = call(HIT, sig)
code = get_code(HIT)
views["_code_len"] = len(code) if code else None
views["_registry_in_bytecode"] = (REG in code.lower()) if code else None
out["hit"] = {"address": HIT, "views": views}
print("HIT", json.dumps(views), flush=True)

FMA = "0xA45CA208d015C81Bf2f5e606437e4f9d1D8C2FE8"
fma_code = get_code(FMA)
out["FMA_bytecode"] = {"address": FMA, "code_len": len(fma_code) if fma_code else None,
                       "registry_in_bytecode": (REG in fma_code.lower()) if fma_code else None}
print("FMA bytecode registry:", out["FMA_bytecode"], flush=True)

with open(f"{BASE}/run-2026-11-09-2101-hit-retry.json", "w") as f:
    json.dump(out, f, indent=1)
print("HIT-RETRY DONE", flush=True)
