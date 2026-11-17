#!/usr/bin/env python3
"""Verify3 ChimpAgent 0x57D41Ff... run 2201: correct selectors (AGENT_ID(),
freeLeft(address)), free amounts, first-mint logs via Ankr. Read-only."""
import json, urllib.request, sys
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0x57D41Ff4895A19f518a0Ec3A2Fa56284a85f5689"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
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

def as_int(v):
    try: return int(v, 16)
    except Exception: return None
def as_addr(v):
    if v and len(v) >= 66: return "0x" + v[-40:]
    return None

jobs = {
    "AGENT_ID()": ("addr", ""), "FACTORY()": ("addr", ""),
    "FREE_PER_WALLET()": ("int", ""), "MINT_AMOUNT()": ("int", ""),
    "MINT_DURATION()": ("int", ""), "MINT_DEADLINE()": ("int", ""),
    "freeLeft(address)": ("int", enc(USER)),
    "quote(address,uint256)": ("int", enc(USER) + format(1, "064x")),
    "quote(address,uint256)_5": ("int", enc(USER) + format(5, "064x")),
    "totalMints()": ("int", ""), "mintOpen()": ("int", ""),
    "mintedBy(address)": ("int", enc(USER)),
    "dev()": ("addr", ""), "owner()": ("addr", ""),
}
calls = {}
for sig, (kind, args) in jobs.items():
    real = sig.replace("_5", "")
    calls[sig] = (kind, sel(real) + args)

with ThreadPoolExecutor(max_workers=10) as ex:
    futs = {sig: ex.submit(raw, data) for sig, (kind, data) in calls.items()}
    res = {}
    for sig, (kind, _) in calls.items():
        v = futs[sig].result()
        if v is None: res[sig] = None
        elif kind == "int": res[sig] = as_int(v)
        else: res[sig] = as_addr(v)

# First Transfer (mint) logs via Ankr module, chunked from deploy-ish range
from ankr import ankr_post
logs = []
try:
    body = ankr_post("ankr_getLogs", {"blockchain": "bsc",
        "fromBlock": hex(132000000), "toBlock": hex(132033700),
        "pageSize": 1000, "decodeLogs": False,
        "topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                   "0x" + "00" * 32],
        "address": [ADDR.lower()]}, timeout=60)
    logs = body.get("result", {}).get("logs", [])
except Exception as e:
    res["ankr_error"] = str(e)
res["transfer_logs_132000000_132033700"] = len(logs)
if logs:
    first = logs[0]
    res["first_mint_block"] = int(first["blockNumber"], 16)
    res["first_mint_tx"] = first.get("transactionHash")
    res["first_mint_to"] = "0x" + first["topics"][2][-40:] if len(first.get("topics", [])) > 2 else None
    res["distinct_minters"] = len(set("0x" + l["topics"][2][-40:] for l in logs if len(l.get("topics", [])) > 2))
    # block timestamp via fast_rpc
    sys.path.insert(0, "/home/hatch/workspace/fast_exec")
    from fast_rpc import _single
    try:
        blk = _single(RPC, "eth_getBlockByNumber", [hex(res["first_mint_block"]), False], 10, retries=0)
        res["first_mint_timestamp"] = int(blk["timestamp"], 16)
    except Exception as e:
        res["first_mint_timestamp_error"] = str(e)
json.dump(res, open(f"{BASE}/run-2026-11-06-2201-57d41-verify3.json", "w"), indent=1)
print(json.dumps(res, indent=1))
