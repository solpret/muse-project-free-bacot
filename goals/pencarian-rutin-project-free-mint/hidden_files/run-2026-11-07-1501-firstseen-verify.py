#!/usr/bin/env python3
"""Verify first-seen 0xe652... (run 1501) directly: ABI shape + on-chain views."""
import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from Crypto.Hash import keccak
from fast_rpc import batch
from ankr import ankr_post
ADDR = "0xe65215428421449ba7D46A4686a2b52E35c15f30"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
# ABI via Sourcify
try:
    req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi,metadata", headers={"User-Agent": "free-bacot/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        meta = json.loads(r.read().decode())
    abi = meta.get("abi", [])
    fns = [e.get("name") for e in abi if isinstance(e, dict) and e.get("type") == "function"]
    print("ABI fns (%d): %s" % (len(fns), fns), flush=True)
    print("registry in abi raw:", REG in json.dumps(abi).lower(), flush=True)
except Exception as e:
    print("SOURCIFY FAIL", type(e).__name__, e, flush=True)
# on-chain views
views = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "owner()", "name()", "symbol()", "agentRegistry()", "AGENT_ID()", "quote(uint256)", "PRICE()"]
calls = [("eth_call", [{"to": ADDR, "data": sel(v)}, "latest"]) for v in views]
try:
    res = batch(calls, endpoint="https://bsc-dataseed1.bnbchain.org/", timeout=10)
    for v, r in zip(views, res):
        print(f"  {v} -> {r}", flush=True)
except Exception as e:
    print("BATCH FAIL", e, flush=True)
# first-mint logs: Transfer from zero in window
try:
    body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(132168529), "toBlock": hex(132169528), "pageSize": 1000, "decodeLogs": False, "topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef", "0x"+"00"*32, None, None], "address": [ADDR.lower()]}, timeout=30)
    logs = body.get("result", {}).get("logs", [])
    print(f"first-mint logs in window: {len(logs)}", flush=True)
    for l in logs[:5]:
        print("  block", int(l["blockNumber"], 16), "tx", l["transactionHash"], flush=True)
except Exception as e:
    print("LOGS FAIL", type(e).__name__, e, flush=True)
