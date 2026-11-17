#!/usr/bin/env python3
"""Run 2101: Nidavellir (new sweep find) + binanceai track-B re-check. Read-only."""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from Crypto.Hash import keccak
from fast_rpc import race
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
NID = "0xd527109571b039298b65bCB26313dcbED0978c97"
MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN = "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def read_one(to, data):
    try: return to_int(race("eth_call", [{"to": to, "data": data}, "latest"]))
    except Exception: return None
def read_str(to, data):
    try: return race("eth_call", [{"to": to, "data": data}, "latest"])
    except Exception: return None
out = {"run": "2101", "time_wib": "2026-11-07 ~21:1x WIB"}
try: out["block"] = int(race("eth_blockNumber", []), 16)
except Exception as e: out["block"] = None; print("BLOCK-FAIL", e, flush=True)
print("block", out["block"], flush=True)
# Sourcify ABI for Nidavellir
try:
    req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{NID}?fields=abi", headers={"User-Agent": "free-bacot/1.0"})
    abi = json.loads(urllib.request.urlopen(req, timeout=25).read().decode()).get("abi")
    out["sourcify_verified"] = bool(abi)
    fns = [e.get("name") for e in abi if isinstance(e, dict) and e.get("type") == "function"] if abi else []
    out["functions"] = fns
    print("NID abi fns:", fns, flush=True)
except Exception as e:
    out["sourcify_verified"] = False; out["sourcify_error"] = str(e); fns = []
    print("NID sourcify FAIL", e, flush=True)
nid = {}
for sig in ["totalSupply()", "name()", "symbol()", "mintOpen()", "freeLeft()", "freeSupply()", "freeMinted()", "freeClaimed(address)", "MAX_SUPPLY()", "maxSupply()", "totalMinted()", "START_TIME()", "startTime()", "mintStart()", "price()", "mintPrice()", "freeSlots()", "FREE_SUPPLY()", "FREE_SLOTS()"]:
    if "address" in sig:
        nid[sig] = read_one(NID, sel(sig) + enc(USER))
    else:
        nid[sig] = read_one(NID, sel(sig))
    print("NID", sig, "=", nid[sig], flush=True)
# quote(user,1) and quote(1) variants
for sig in ["quote(address,uint256)", "quote(uint256)", "cost(address,uint256)", "mintCost(uint256)"]:
    try:
        if "address" in sig: d = sel(sig) + enc(USER) + enc_u(1)
        else: d = sel(sig) + enc_u(1)
        nid[sig] = read_one(NID, d)
    except Exception: nid[sig] = None
    print("NID", sig, "=", nid[sig], flush=True)
# name/symbol strings
for sig in ["name()", "symbol()"]:
    r = read_str(NID, sel(sig))
    nid[sig + "_raw"] = r
out["nidavellir"] = nid
# binanceai re-check
bai = {}
for sig in ["launched()", "failed()", "isRefundPhase()", "totalShares()"]:
    bai[sig] = read_one(MINT, sel(sig)); print("BINANCEAI", sig, "=", bai[sig], flush=True)
bai["tokenClaimed(user)"] = read_one(MINT, sel("tokenClaimed(address)") + enc(USER))
bai["tokenBalance(user)"] = read_one(TOKEN, sel("balanceOf(address)") + enc(USER))
print("BINANCEAI pass1", json.dumps(bai), flush=True)
if any(v is None for v in bai.values()):
    print("BINANCEAI retry pass", flush=True)
    for sig in ["launched()", "failed()", "isRefundPhase()", "totalShares()"]:
        if bai[sig] is None: bai[sig] = read_one(MINT, sel(sig))
    if bai["tokenClaimed(user)"] is None: bai["tokenClaimed(user)"] = read_one(MINT, sel("tokenClaimed(address)") + enc(USER))
    if bai["tokenBalance(user)"] is None: bai["tokenBalance(user)"] = read_one(TOKEN, sel("balanceOf(address)") + enc(USER))
    print("BINANCEAI pass2", json.dumps(bai), flush=True)
out["binanceai"] = bai
json.dump(out, open(f"{BASE}/run-2026-11-07-2101-nidavellir-binanceai.json", "w"), indent=1)
print("DONE", json.dumps(out, indent=1)[:1500], flush=True)
