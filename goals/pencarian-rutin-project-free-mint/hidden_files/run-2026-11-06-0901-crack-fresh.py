#!/usr/bin/env python3
"""Run 0901: fresh on-chain verification for Crack pre-execution (track-C lead direct mint).
Reads all lead legs fresh with per-RPC retries; a failed read is None (UNVERIFIED), never 0."""
import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
ADDR="0xAeA1433dBD9e7edE0914d996C2Dad692E6e01e09"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org","https://bsc-dataseed3.bnbchain.org"]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(data, tries=2):
    for _ in range(tries):
        for ep in EPS:
            try:
                out=_single(ep,"eth_call",[{"to":ADDR,"data":data},"latest"],8,retries=0)
                if out is None or out=="0x": return None
                return int(out,16)
            except Exception:
                continue
    return None
def call_raw(data, tries=2):
    for _ in range(tries):
        for ep in EPS:
            try:
                out=_single(ep,"eth_call",[{"to":ADDR,"data":data},"latest"],8,retries=0)
                return out
            except Exception:
                continue
    return None
out={}
out["totalSupply"]=call(sel("totalSupply()"))
out["totalMinted"]=call(sel("totalMinted()"))
out["publicRemaining"]=call(sel("publicRemaining()"))
out["mintOpen"]=call(sel("mintOpen()"))
out["mintMode"]=call(sel("mintMode()"))
out["price"]=call(sel("price()"))
out["MAX_SUPPLY"]=call(sel("MAX_SUPPLY()"))
out["reserve"]=call(sel("reserve()"))
out["reserveMinted"]=call(sel("reserveMinted()"))
out["freeUsed_user"]=call(sel("freeUsed(address)")+enc(USER))
out["mintCost_user_1"]=call(sel("mintCost(address,uint256)")+enc(USER)+format(1,"064x"))
out["hasAgentId_user"]=call(sel("hasAgentId(address)")+enc(USER))
out["balanceOf_user"]=call(sel("balanceOf(address)")+enc(USER))
out["mintedBy_user"]=call(sel("mintedBy(address)")+enc(USER))
out["maxPerWallet"]=call(sel("maxPerWallet()"))
out["walletInfo_raw"]=call_raw(sel("walletInfo(address)")+enc(USER))
out["stats_raw"]=call_raw(sel("stats()"))
# block number
for ep in EPS:
    try:
        out["block"]=int(_single(ep,"eth_blockNumber",[],8,retries=0),16); break
    except Exception: continue
print(json.dumps(out, indent=1), flush=True)
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-06-0901-crack-fresh.json","w"), indent=1)
