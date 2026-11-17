#!/usr/bin/env python3
"""Boltbook 2231 on-chain verify: new non-snapshot addresses from front page.
Read-only. Uses fast_rpc.race per call (single calls; batch reverts kill
whole batch). User wallet = agent wallet 0xeb23... (baw).
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as _fast_single
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/",
       "https://rpc.ankr.com/bsc"]
DEADLINE = time.time() + 280

def sel(sig):
    k = keccak.new(digest_bits=256)
    k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def call(to, data, block="latest"):
    if time.time() > DEADLINE:
        return "ERR:deadline"
    for ep in EPS:
        try:
            v = _fast_single(ep, "eth_call", [{"to": to, "data": data}, block], 8, retries=0)
            return v
        except Exception:
            continue
    return "ERR:all-endpoints-failed"

def u256(r):
    if not isinstance(r, str) or not r.startswith("0x"):
        return None
    try:
        return int(r, 16)
    except Exception:
        return None

def dec_str(r):
    # decode abi string return
    if not isinstance(r, str) or len(r) < 130:
        return None
    try:
        b = bytes.fromhex(r[2:])
        ln = int.from_bytes(b[64:96], "big")
        return b[96:96+ln].decode("utf-8", "replace")
    except Exception:
        return None

VIEWS = ["totalSupply()", "totalMinted()", "MAX_SUPPLY()", "FREE_SUPPLY()",
         "mintOpen()", "mintActive()", "PRICE()", "price()",
         "freeLeft()", "freeClaimed()", "freeMinted()", "freeSupply()",
         "agentRegistry()", "REGISTRY()", "owner()", "name()", "symbol()",
         "contractURI()", "baseURI()", "mintPrice()", "MAX_PER_WALLET()",
         "freeCap()", "agentFreeCap()", "agentFreeUsed()", "mintEnd()",
         "startTime()", "MINT_START()", "costOf(address,uint256)",
         "quote(address,uint256)", "freeFor(address)", "freeAvailable(address)",
         "balanceOf(address)", "freeClaimed(address)", "freeMinted(address)",
         "mintedBy(address)", "mintedCount(address)", "hasAgentId(address)",
         "eligibility(address)"]
USER_VIEWS = {"costOf(address,uint256)", "quote(address,uint256)",
              "freeFor(address)", "freeAvailable(address)", "balanceOf(address)",
              "freeClaimed(address)", "freeMinted(address)", "mintedBy(address)",
              "mintedCount(address)", "hasAgentId(address)", "eligibility(address)"}

CONTRACTS = {
    "0x3c7d328027ca0068e7cd8709d64d9161bc35de93": "BRAINROT ZOO (ROT)",
    "0xafb50403c0838d5b45f8748138ba33a70e23b8cf": "PIXEL BOYZ (PBOYZ)",
    "0x5bc4fb61270c2628c93bf507c4ba125b868d34ff": "Binance Fleet Genesis",
    "0x6288DFe86f22B53eEB6886aE2D78941de7483743": "AGCC minter (agcc.fun)",
    "0x63dea5aCdbE1F27c968907D08610A5f0A0284bA6": "AGC token (agcc.fun)",
}

out = {"run": "2231", "user": USER, "contracts": {}}
blk = None
for ep in EPS:
    try:
        v = _fast_single(ep, "eth_blockNumber", [], 8, retries=0)
        if v:
            blk = int(v, 16); break
    except Exception:
        continue
out["block"] = blk
print("head block:", out["block"], flush=True)

for addr, label in CONTRACTS.items():
    row = {"label": label, "views": {}}
    for v in VIEWS:
        data = sel(v)
        if v in USER_VIEWS:
            data += USER_PAD
            if v in ("costOf(address,uint256)", "quote(address,uint256)"):
                data += "1".rjust(64, "0")
        r = call(addr, data)
        if isinstance(r, str) and r.startswith("0x"):
            iv = u256(r)
            s = dec_str(r)
            row["views"][v] = {"int": iv, "str": s} if s else {"int": iv}
        else:
            row["views"][v] = {"error": str(r)[:120]}
    out["contracts"][addr] = row
    ts = row["views"].get("totalSupply()", {}).get("int")
    print(addr, label, "totalSupply=", ts, flush=True)

json.dump(out, open(f"{BASE}/run-2026-11-07-2231-boltbook-onchain.json", "w"), indent=1)
print("DONE", flush=True)
