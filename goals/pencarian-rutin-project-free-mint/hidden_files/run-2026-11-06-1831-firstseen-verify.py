#!/usr/bin/env python3
"""Run 1831: on-chain state read for 5 scan first-seen agent-shaped contracts."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def call(addr, sig, args=""):
    data = sel(sig) + args
    for ep in EPS:
        try:
            v = _single(ep, "eth_call", [{"to": addr, "data": data}, "latest"], 6, retries=0)
            if v in (None, "0x", ""): return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None
VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
         "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
         "mintedBy(address)", "freeUsed(address)", "canFreeMint(address)",
         "claimedFree(address)", "quote(address,uint256)", "costOf(address,uint256)",
         "price()", "FREE_PER_WALLET()", "freeFor(address)", "freeLeft()",
         "spotsLeft()", "freeQuota()", "remainingFree()", "agentRegistry()",
         "agentId()", "agentGateOn()"]
TARGETS = {
 "Kaiju": "0xC6d31279d529F3219575447A7Fbe888E176369a9",
 "Peepers": "0x318692c7c8DABDf3dAaf4Ed0F1d3646f70070fb9",
 "PropertyAgent": "0x8bfA8AF37E85Cd5232B57DC1276671769F97Ed41",
 "Goblins": "0x712373aCF9c1C17806fEF4C8687c7F33128D37F3",
 "Sprouts": "0x5B5922F98bA068E7474cC57E2ecbd11c4DB7De79",
}
out = {}
for name, addr in TARGETS.items():
    d = {"address": addr}
    for sig in VIEWS:
        key = sig.split("(")[0]
        if "address" in sig and "uint256" in sig:
            v = call(addr, sig, enc(USER) + enc_uint(1)); key += "_user_1"
        elif "address" in sig:
            v = call(addr, sig, enc(USER)); key += "_user"
        else:
            v = call(addr, sig)
        d[key] = v
    print(name, d, flush=True)
    out[name] = d
json.dump(out, open(f"{BASE}/run-2026-11-06-1831-firstseen-verify.json", "w"), indent=1)
print("DONE", flush=True)
