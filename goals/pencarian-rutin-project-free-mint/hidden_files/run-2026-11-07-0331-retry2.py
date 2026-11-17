#!/usr/bin/env python3
"""Run 0331 retry #2: direct curl eth_call to bsc-dataseed1 for MAGES + RLAM key views.
Read-only."""
import json, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP="https://bsc-dataseed1.bnbchain.org/"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(addr, sig, args=""):
    payload=json.dumps({"jsonrpc":"2.0","method":"eth_call","params":[{"to":addr,"data":sel(sig)+args},"latest"],"id":1})
    try:
        r=subprocess.run(["curl","-sS","--max-time","20","-H","Content-Type: application/json","-d",payload,EP],
                         capture_output=True,text=True,timeout=30)
        d=json.loads(r.stdout)
        if "result" in d: return d["result"]
        return {"error":str(d.get("error"))[:160]}
    except Exception as e:
        return {"error":f"{type(e).__name__}: {e}"[:160]}
def pint(v):
    try: return int(v,16)
    except Exception: return v
def paddr(v):
    try: return "0x"+v[-40:]
    except Exception: return v
out={}
MAGES="0xbD709301473aC208f1bc4be598aE53295d311459"
m={}
for sig in ["wezardsNFT()","magesToken()","MAGES_TOKEN_ADDRESS()","agentRegistry()","freeClaimsOpen()","paidClaimsOpen()","claimsPermanentlyEnded()","paused()","MAX_FREE_CLAIMS()","MAX_PAID_CLAIMS()","freeClaimsCompleted()","paidClaimsCompleted()","FREE_REWARD()","PAID_REWARD()","PAID_PRICE()","remainingRewardLiability()"]:
    r=call(MAGES,sig)
    m[sig]={"int":pint(r),"addr":paddr(r)} if isinstance(r,str) else {"error":r}
    print("MAGES",sig,"=",m[sig],flush=True)
out["MAGES"]=m
wnft=m.get("wezardsNFT()",{}).get("addr")
out["wezardsNFT"]=wnft
if isinstance(wnft,str) and wnft.startswith("0x") and wnft!="0x0000000000000000000000000000000000000000":
    bal=pint(call(wnft,"balanceOf(address)",enc(USER)))
    print("USER WezardsNFT balance =",bal,flush=True)
    out["userWezardsBalance"]=bal
    if isinstance(bal,int) and bal>0:
        tid=pint(call(wnft,"tokenOfOwnerByIndex(address,uint256)",enc(USER)+"0"*63+"0"))
        print("USER WezardsNFT token0 =",tid,flush=True)
        out["userWezardsToken0"]=tid
        if isinstance(tid,int):
            fc=pint(call(MAGES,"freeClaimedNFT(uint256)",hex(tid)[2:].rjust(64,"0")))
            print("freeClaimedNFT(token0) =",fc,flush=True)
            out["freeClaimedNFT_token0"]=fc
RLAM="0xcb43cd9ac0a157820a44a49465494f300f37f1da"
rl={}
for sig in ["agentRegistry()","AGENT_ID()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","totalSupply()"]:
    r=call(RLAM,sig)
    rl[sig]={"int":pint(r),"addr":paddr(r)} if isinstance(r,str) else {"error":r}
    print("RLAM",sig,"=",rl[sig],flush=True)
rl["balanceOf(user)"]=pint(call(RLAM,"balanceOf(address)",enc(USER)))
print("RLAM balanceOf(user)=",rl["balanceOf(user)"],flush=True)
out["Bearlambo"]=rl
json.dump(out,open(f"{BASE}/run-2026-11-07-0331-retry-views.json","w"),indent=1)
print("wrote run-2026-11-07-0331-retry-views.json",flush=True)
