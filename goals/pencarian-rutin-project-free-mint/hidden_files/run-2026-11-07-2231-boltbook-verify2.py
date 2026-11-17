#!/usr/bin/env python3
"""Boltbook 2231 targeted re-read (deadline-hit contracts + PBOYZ free views).
Read-only; _fast_single sequential fallback."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as _fast_single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/",
       "https://rpc.ankr.com/bsc"]
DEADLINE = time.time() + 240
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def raw(to, data):
    if time.time() > DEADLINE: return "deadline"
    for ep in EPS:
        try:
            v = _fast_single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
            if v is None or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception: continue
    return None
def call(to, sig, args=""): return raw(to, sel(sig) + args)

blk=None
for ep in EPS:
    try:
        v=_fast_single(ep,"eth_blockNumber",[],8,retries=0)
        if v: blk=int(v,16); break
    except Exception: continue
print("head block:", blk, flush=True)
PBOYZ="0xafb50403c0838d5b45f8748138ba33a70e23b8cf"
FLEET="0x5bc4fb61270c2628c93bf507c4ba125b868d34ff"
AGCC="0x6288DFe86f22B53eEB6886aE2D78941de7483743"
AGC="0x63dea5aCdbE1F27c968907D08610A5f0A0284bA6"
out={"run":"2231","block":blk,"contracts":{}}
specs={
 PBOYZ: (["totalMinted()","totalFreeMinted()","FREE_ALLOCATION()","freeAllocationRemaining()",
          "freeSaleActive()","freePhaseClosed()","mintPrice()","agentRegistry()","MAX_SUPPLY()",
          "totalPaidMinted()","remainingSupply()"],
         [("walletFreeRemaining(address)","walletFreeRemaining_user"),
          ("freeMintedByWallet(address)","freeMintedByWallet_user"),
          ("walletMinted(address)","walletMinted_user"),
          ("balanceOf(address)","balanceOf_user"),
          ("hasAgentId(address)","hasAgentId_user")]),
 FLEET: (["totalSupply()","totalMinted()","totalPaid()","MAX_SUPPLY()","mintOpen()",
          "FREE_PER_WALLET()","registry()","MINT_PRICE()"],
         [("quote(address,uint256)","quote_user_1"),
          ("hasAgentId(address)","hasAgentId_user"),
          ("mintedBy(address)","mintedBy_user"),
          ("balanceOf(address)","balanceOf_user")]),
 AGCC: (["totalShares()","PRICE_PER_SHARE()","AGENT_ID_REGISTRY()","freePositionCount()",
         "agc()","pair()","EPOCH()","MAX_SHARES()"],
        [("freeAvailableFor(address)","freeAvailableFor_user"),
         ("freeClaimed(address)","freeClaimed_user")]),
 AGC: (["totalSupply()","decimals()","openTime()","trading()","pair()","MAX_SUPPLY()"],
       [("balanceOf(address)","balanceOf_user")]),
}
for addr,(views,uviews) in specs.items():
    row={}
    for v in views: row[v]=call(addr,v)
    for v,k in uviews:
        args=enc(USER)
        if v.startswith("quote"): args+=format(1,"064x")
        row[k]=call(addr,v,args)
    out["contracts"][addr]=row
    print(addr, row, flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-07-2231-boltbook-onchain2.json","w"), indent=1)
print("DONE", flush=True)
