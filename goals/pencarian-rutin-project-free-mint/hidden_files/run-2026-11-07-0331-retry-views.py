#!/usr/bin/env python3
"""Run 0331 retry of Bearlambo + MAGES key views via Ankr eth_call (fast_rpc was
degrading with all-endpoint OSError). Read-only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(addr, sig, args="", tag=""):
    try:
        r=ankr_post("eth_call",[{"to":addr,"data":sel(sig)+args},"latest"],timeout=25)
        res=r.get("result")
        if res is None: return {"error":str(r)[:200]}
        return {"raw":res}
    except Exception as e:
        return {"error":f"{type(e).__name__}: {e}"[:200]}
def pint(v):
    try:
        if isinstance(v,dict) and "raw" in v: return int(v["raw"],16)
    except Exception: return None
    return v
def paddr(v):
    try:
        if isinstance(v,dict) and "raw" in v: return "0x"+v["raw"][-40:]
    except Exception: return None
    return v
out={}
RLAM="0xcb43cd9ac0a157820a44a49465494f300f37f1da"
rlam={}
for sig in ["agentRegistry()","AGENT_ID()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","totalSupply()","freeClaimed(address)"]:
    args=enc(USER) if "address" in sig else ""
    r=call(RLAM,sig,args)
    rlam[sig]={"int":pint(r),"addr":paddr(r),"err":r.get("error")}
    print("RLAM",sig,"=",rlam[sig],flush=True)
rlam["balanceOf(user)"]=pint(call(RLAM,"balanceOf(address)",enc(USER)))
print("RLAM balanceOf(user)=",rlam["balanceOf(user)"],flush=True)
out["Bearlambo"]=rlam
MAGES="0xbD709301473aC208f1bc4be598aE53295d311459"
m={}
for sig in ["wezardsNFT()","magesToken()","agentRegistry()","freeClaimsOpen()","paidClaimsOpen()","claimsPermanentlyEnded()","paused()","MAX_FREE_CLAIMS()","MAX_PAID_CLAIMS()","freeClaimsCompleted()","paidClaimsCompleted()","FREE_REWARD()","PAID_REWARD()","PAID_PRICE()","remainingRewardLiability()"]:
    r=call(MAGES,sig)
    m[sig]={"int":pint(r),"addr":paddr(r),"err":r.get("error")}
    print("MAGES",sig,"=",m[sig],flush=True)
out["MAGES"]=m
# user Wezards NFT balance (needs wezardsNFT address)
wnft=m.get("wezardsNFT()",{}).get("addr")
out["wezardsNFT"]=wnft
if wnft and wnft.startswith("0x") and wnft!="0x0000000000000000000000000000000000000000":
    bal=pint(call(wnft,"balanceOf(address)",enc(USER)))
    print("USER WezardsNFT balance =",bal,flush=True)
    out["userWezardsBalance"]=bal
    # if user holds, check first token id via tokenOfOwnerByIndex(0) if exists
    if bal and bal>0:
        tid=pint(call(wnft,"tokenOfOwnerByIndex(address,uint256)",enc(USER)+"0"*63+"0"))
        print("USER WezardsNFT token0 =",tid,flush=True)
        out["userWezardsToken0"]=tid
        if tid is not None:
            fc=pint(call(MAGES,"freeClaimedNFT(uint256)",hex(tid)[2:].rjust(64,"0")))
            print("freeClaimedNFT(token0) =",fc,flush=True)
            out["freeClaimedNFT_token0"]=fc
json.dump(out,open(f"{BASE}/run-2026-11-07-0331-retry-views.json","w"),indent=1)
print("wrote run-2026-11-07-0331-retry-views.json",flush=True)
