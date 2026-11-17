#!/usr/bin/env python3
"""Hot-leg 2054 leg3 retry: direct dataseed eth_call (fast_rpc batch failed -32002 eth_call unavailable).
NUSA + Oddlode + Project402 pool reads + 0x7Bd361 near-miss S2-equivalent probe."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-2054"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPC = "https://bsc-dataseed.bnbchain.org/"
t0 = time.time()

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def call(addr, sig, arg=""):
    data = sel(sig)
    if arg == "USER": data += enc_addr(USER)
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": addr, "data": data}, "latest"]})
    out = subprocess.run(["curl", "-sL", "--max-time", "20", "-X", "POST", RPC,
                          "-H", "Content-Type: application/json", "-d", payload],
                         capture_output=True, text=True).stdout
    try:
        r = json.loads(out).get("result")
        return int(r, 16) if r else None
    except Exception:
        return None
def block_number():
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []})
    out = subprocess.run(["curl", "-sL", "--max-time", "20", "-X", "POST", RPC,
                          "-H", "Content-Type: application/json", "-d", payload],
                         capture_output=True, text=True).stdout
    try:
        return int(json.loads(out).get("result"), 16)
    except Exception:
        return None

NUSA = "0x7D08289E962f5aEc00d56D67322eb2FD056B687c"
ODD = "0xce18531F9F639ca2351CA15FB2032D925b917472"
P402 = "0xd80d0095746999c93ae837b1de1569d5814405dc"
NEAR = "0x7Bd361A88beC064283F77Af8dc781E6A84ceAaE9"
vals = {}
plan = [
    (NUSA, ["freeMinted()", "sharesMinted()", "paidShares()", "soldOut()", "closed()"], ""),
    (NUSA, ["freeAvailable(address)", "freeClaimed(address)", "hasMinted(address)"], "USER"),
    (ODD, ["freeMinted()", "totalSupply()"], ""),
    (ODD, ["freeClaimed(address)", "balanceOf(address)"], "USER"),
    (P402, ["freeMinted()", "FREE_CAP()", "totalMinted()", "totalSupply()", "mintOpen()"], ""),
    (P402, ["freeClaimed(address)"], "USER"),
    (NEAR, ["FREE_SHARES()", "freeSold()", "launched()", "saleOpen()", "saleStart()", "saleEnd()", "launchTime()", "totalSupply()"], ""),
    (NEAR, ["freeClaimed(address)", "userShares(address)"], "USER"),
]
for addr, sigs, arg in plan:
    for sig in sigs:
        vals.setdefault(addr, {})[sig] = call(addr, sig, arg)
blk = block_number()
# pair() returns address, not int - read raw
def call_raw(addr, sig):
    data = sel(sig)
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": addr, "data": data}, "latest"]})
    out = subprocess.run(["curl", "-sL", "--max-time", "20", "-X", "POST", RPC,
                          "-H", "Content-Type: application/json", "-d", payload],
                         capture_output=True, text=True).stdout
    try:
        return json.loads(out).get("result")
    except Exception:
        return None
vals[NEAR]["pair()"] = call_raw(NEAR, "pair()")
vals[NEAR]["name_raw"] = call_raw(NEAR, "name()")
vals[NEAR]["symbol_raw"] = call_raw(NEAR, "symbol()")
log = {"block": blk, "values": vals, "elapsed_sec": round(time.time() - t0, 1)}
json.dump(log, open(BASE + TAG + "-fresh-reads.json", "w"), indent=1)
print(json.dumps(log, indent=1))
print("ELAPSED", round(time.time() - t0, 1))
