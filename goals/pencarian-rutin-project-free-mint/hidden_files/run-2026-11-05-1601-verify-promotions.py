#!/usr/bin/env python3
"""Run 1601 promotion verification: Thronemind / Smeltbots / Hashseers / PassAgentX /
Agent Frogs / DYOR + Pulsekeep recheck. Read-only, no preview/mint."""
import json, sys, urllib.request, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-05-1601"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc-dataseed2.bnbchain.org", "https://bsc.publicnode.com"]
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

TARGETS = {
 "Thronemind": "0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90",
 "Smeltbots": "0xdC0004F3Efcc2aEA6052e138d3f1e680ca5D9b8e",
 "Hashseers": "0x7E634ED532a7b7b781262A0d4220ac3c3Ba6B688",
 "PassAgentX": "0x08b1A979Dd997492EEcc010fe986eA2e2925e620",
 "Agent Frogs": "0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31",
}
out = {}
for name, addr in TARGETS.items():
    d = {"address": addr}
    d["totalSupply"] = call(addr, "totalSupply()")
    d["totalMinted"] = call(addr, "totalMinted()")
    d["freeClaimed"] = call(addr, "freeClaimed()")
    d["freeMinted"] = call(addr, "freeMinted()")
    d["FREE_CAP"] = call(addr, "FREE_CAP()")
    d["FREE_SUPPLY"] = call(addr, "FREE_SUPPLY()")
    d["MAX_SUPPLY"] = call(addr, "MAX_SUPPLY()")
    d["mintedBy_user"] = call(addr, "mintedBy(address)", enc(USER))
    d["freeUsed_user"] = call(addr, "freeUsed(address)", enc(USER))
    d["freeLeft_user"] = call(addr, "freeLeft(address)", enc(USER))
    d["canFreeMint_user"] = call(addr, "canFreeMint(address)", enc(USER))
    d["claimedFree_user"] = call(addr, "claimedFree(address)", enc(USER))
    d["quote_user_1"] = call(addr, "quote(address,uint256)", enc(USER) + enc_uint(1))
    d["mintOpen"] = call(addr, "mintOpen()")
    d["REGISTRY"] = call(addr, "REGISTRY()")
    d["AGENT_ID"] = call(addr, "AGENT_ID()")
    if name == "PassAgentX":
        d["mintStart"] = call(addr, "mintStart()")
        d["mintEnd"] = call(addr, "mintEnd()")
    print(name, d, flush=True)
    out[name] = d

# first-mint age verification for Thronemind + Agent Frogs (Smeltbots already verified 13:10:38 WIB)
for name, lo in [("Thronemind", 131755000), ("Agent Frogs", 131650000)]:
    addr = TARGETS[name]
    fm = first_mint(addr, lo, 131792170)
    ts = block_ts(fm) if fm else None
    print(name, "FIRST_MINT", fm, "TS", ts, flush=True)
    out[name]["firstMintBlock"] = fm
    out[name]["firstMintTs"] = ts

# recheck anomalies
print("DYOR totalSupply recheck:", call("0x86956Bc830EB62110820Ae79164BeF61c7E31936", "totalSupply()"), flush=True)
print("DYOR totalMinted recheck:", call("0x86956Bc830EB62110820Ae79164BeF61c7E31936", "totalMinted()"), flush=True)
print("Pulsekeep totalSupply recheck:", call("0x65c89bD01A03B9B9B73eD29d3B3aF8D2eb034DFc", "totalSupply()"), flush=True)
print("Pulsekeep freeMinted recheck:", call("0x65c89bD01A03B9B9B73eD29d3B3aF8D2eb034DFc", "freeMinted()"), flush=True)
out["DYOR_recheck_totalSupply"] = call("0x86956Bc830EB62110820Ae79164BeF61c7E31936", "totalSupply()")
out["Pulsekeep_recheck"] = {
    "totalSupply": call("0x65c89bD01A03B9B9B73eD29d3B3aF8D2eb034DFc", "totalSupply()"),
    "freeMinted": call("0x65c89bD01A03B9B9B73eD29d3B3aF8D2eb034DFc", "freeMinted()"),
}
json.dump(out, open(f"{BASE}/run-{TS}-verify-promotions.json", "w"), indent=1)
print("SAVED", flush=True)
