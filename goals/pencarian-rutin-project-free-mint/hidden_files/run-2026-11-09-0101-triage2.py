#!/usr/bin/env python3
"""Triage2 run 0101: verify Gryphlume first mint near seen block, Backdoor proper
walkback, bytecode registry check for Gryphlume/Backdoor/YAOQIAN. Read-only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from fast_rpc import _post as _fr_post
import onchain_nft_scan as scan

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]
OUT = f"{BASE}/run-2026-11-09-0101-triage2.json"

def block_ts(blk):
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                                "params": [hex(blk), False]}, timeout=25, retries=0)
            ts = out.get("result", {}).get("timestamp")
            return int(ts, 16) if ts else None
        except Exception:
            continue
    return None

def code_has_registry(addr):
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                                "params": [addr, "latest"]}, timeout=25, retries=0)
            code = (out.get("result") or "").lower()
            return {"code_len": len(code), "registry_bytes": REG in code,
                    "registry_addr_in_code": "60b9262456de011f7d15a54cdd8c48baaa8b022f" in code}
        except Exception:
            continue
    return {"error": "rpc fail"}

def mints_in(addr, frm, to):
    logs, _ = scan.ankr_logs(frm, to, [scan.TRANSFER, scan.ZERO_TOPIC])
    mine = [l for l in logs if l.get("address", "").lower() == addr.lower()]
    return mine

def proper_first_mint(addr, start, max_back=60000):
    """Walk back from `start` until a 1000-block chunk with ZERO mints; return
    earliest mint block found (true first mint if an empty chunk is reached)."""
    to = start
    earliest = None
    searched = 0
    while searched < max_back and to > 0:
        frm = max(0, to - 999)
        mine = mints_in(addr, frm, to)
        print(f"  {addr[:10]} {frm}-{to}: {len(mine)} mints", flush=True)
        if not mine:
            break
        earliest = min(int(l["blockNumber"], 16) for l in mine)
        to = frm - 1
        searched += 1000
    return {"first_block": earliest, "first_block_ts": block_ts(earliest) if earliest else None,
            "empty_chunk_reached": searched < max_back or to <= 0,
            "searched_back_blocks": searched}

res = {}
# calibrate seen semantics: Dragon Agent
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
print("Dragon seen value:", seen.get("contracts", {}).get("0xaa87b6b3ecdd3202a80d109a91e88783fffb0be6"), flush=True)
print("Gryphlume seen value:", seen.get("contracts", {}).get("0x8ea465abd41aec8b6f1bd80a7c6c37d3ae85529c"), flush=True)

G = "0x8ea465abd41aec8b6f1bd80a7c6c37d3ae85529c"
print("Gryphlume code:", code_has_registry(G), flush=True)
print("Gryphlume mints near seen block 131197799...", flush=True)
mine = mints_in(G, 131196799, 131198799)
print("  mints 131196799-131198799:", len(mine), "first:", min((int(l['blockNumber'],16) for l in mine), default=None), flush=True)
res["Gryphlume_seen_check"] = {"mints_around_seen": len(mine),
    "first_in_window": min((int(l["blockNumber"], 16) for l in mine), default=None)}
if mine:
    b = min(int(l["blockNumber"], 16) for l in mine)
    res["Gryphlume_seen_check"]["first_ts"] = block_ts(b)
    # walk back from there to find true first mint
    print("Gryphlume proper walkback from", b, flush=True)
    res["Gryphlume_first_mint"] = proper_first_mint(G, b)
    print("GRYPHLUME FIRST:", json.dumps(res["Gryphlume_first_mint"], default=str), flush=True)

B = "0x9c6a008f73a1d1941f4763b88c6ee8c8e4ef8b0a"
print("Backdoor code:", code_has_registry(B), flush=True)
print("Backdoor proper walkback from 132421804 (23:45 WIB automint block)...", flush=True)
res["Backdoor_first_mint"] = proper_first_mint(B, 132421804)
print("BACKDOOR FIRST:", json.dumps(res["Backdoor_first_mint"], default=str), flush=True)

Y = "0x75148608e41C4f3A325F4DBC040B2B60CDc772d6"
print("YAOQIAN code:", code_has_registry(Y), flush=True)
res["YAOQIAN_code"] = code_has_registry(Y)
# YAOQIAN share mints: Transfer-from-zero on the sale contract in last 3000 blocks?
mine = mints_in(Y, 132437000, 132440000)
print("YAOQIAN mints last 3000 blocks:", len(mine), flush=True)
res["YAOQIAN_recent_mints"] = len(mine)

with open(OUT, "w") as f:
    json.dump(res, f, indent=1, default=str)
print("TRIAGE2 DONE", flush=True)
