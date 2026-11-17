#!/usr/bin/env python3
"""Run 1601 verify-2: Thronemind first-mint ts, Hashseers first-mint, Agent Frogs slot retry. Read-only."""
import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc-dataseed2.bnbchain.org", "https://bsc-dataseed3.bnbchain.org"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
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
            with urllib.request.urlopen(req, timeout=8) as r: out = json.load(r)
            if "error" in out: return None
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception: continue
    return None
def call(to, sig, args=""): return raw(to, sel(sig) + args)
def block_ts(n):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                               "params": [hex(n), False]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r:
                return int(json.load(r)["result"]["timestamp"], 16)
        except Exception: continue
    return None
def any_mint(addr, lo, hi):
    params = {"blockchain": "bsc", "fromBlock": hex(lo), "toBlock": hex(hi),
              "pageSize": 1000, "decodeLogs": False, "topics": [TRANSFER, ZERO], "address": addr}
    body = ankr_post("ankr_getLogs", params, timeout=30)
    logs = (body.get("result", {}) or {}).get("logs", []) if isinstance(body, dict) else []
    for lg in logs:
        if len(lg.get("topics", [])) == 4:
            return int(lg["blockNumber"], 16)
    return None
def first_mint(addr, lo, hi):
    if any_mint(addr, lo, hi) is None: return None
    while lo < hi:
        mid = (lo + hi) // 2
        if any_mint(addr, lo, mid) is not None: hi = mid
        else: lo = mid + 1
    return lo
out = {}
out["Thronemind_firstMintTs"] = block_ts(131762375)
print("Thronemind first-mint block 131762375 ts:", out["Thronemind_firstMintTs"], flush=True)
fm = first_mint("0x7E634ED532a7b7b781262A0d4220ac3c3Ba6B688", 131755000, 131792170)
out["Hashseers_firstMintBlock"] = fm
out["Hashseers_firstMintTs"] = block_ts(fm) if fm else None
print("Hashseers FIRST_MINT:", fm, "TS:", out["Hashseers_firstMintTs"], flush=True)
AF = "0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31"
out["AgentFrogs_slot"] = {
    "balanceOf_user": call(AF, "balanceOf(address)", enc(USER)),
    "freeClaimed_user": call(AF, "freeClaimed(address)", enc(USER)),
    "freeUsed_user": call(AF, "freeUsed(address)", enc(USER)),
    "canFreeMint_user": call(AF, "canFreeMint(address)", enc(USER)),
    "claimedFree_user": call(AF, "claimedFree(address)", enc(USER)),
    "quote_user_1": call(AF, "quote(address,uint256)", enc(USER) + enc_uint(1)),
    "totalSupply": call(AF, "totalSupply()"),
    "freeClaimed": call(AF, "freeClaimed()"),
}
print("AgentFrogs slot retry:", out["AgentFrogs_slot"], flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-05-1601-verify2.json", "w"), indent=1)
print("SAVED", flush=True)
