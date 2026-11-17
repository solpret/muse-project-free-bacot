#!/usr/bin/env python3
"""Lean retry for free-mint-search run 2026-11-13 22:31 WIB.
Retries the 9 transport-FAILED verify items + first read of Sourcify-new
mintFree NFT 0x5877D2bb. Read-only; writes run-2026-11-13-2231-retry.json."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
t0=time.time()
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def post_rpc(ep,payload,timeout=20):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def build_data(sig,args):
    d=sel(sig)
    for a in args:
        if isinstance(a,str) and a.startswith("0x") and len(a)==42: d+=enc_addr(a)
        else: d+=enc_u(int(a))
    return d
def raw_batch(addr,views):
    calls,keys=[],[]
    for i,(key,sig,args) in enumerate(views):
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":build_data(sig,args)},"latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res=post_rpc(ep,calls,timeout=20)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            out={}
            for it,key in zip(res,keys):
                if not isinstance(it,dict) or "error" in it or it.get("result") in (None,"0x"): out[key]=None
                else:
                    r=it["result"]; out[key]=to_int(r[:66]) if len(r)>=66 else r
            return out
        except Exception: continue
    return None
U=[USER]
ITEMS={
 "Agentx": ("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492", [("totalMinted","totalMinted()",[]),("freeMinted","freeMinted()",[]),("FREE_CAP","FREE_CAP()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),("freeClaimed_user","freeClaimed(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "Zero": ("0x89B340435e4fD27e00442f7F1b3a3b3244b4E647", [("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "BUBB": ("0x0d72970046c056db90888351b739246f468bff0b", [("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "JNTM": ("0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b", [("freeClaimed","freeClaimed()",[]),("freeLeft","freeLeft()",[]),("FREE_LOTS_CAP","FREE_LOTS_CAP()",[]),("TOTAL_LOTS","TOTAL_LOTS()",[]),("totalMinted","totalMinted()",[]),("mintStart","mintStart()",[]),("opened","opened()",[]),("freeClaimedByAgent_user","freeClaimedByAgent(address)",U)]),
 "AgentMuse": ("0x779fa133848d23052B7345F63B3b2E5309cd13ed", [("freeClaimed","freeClaimed()",[]),("FREE_SHARES","FREE_SHARES()",[]),("bookedTotal","bookedTotal()",[]),("openedAt","openedAt()",[]),("DOORS_OPEN","DOORS_OPEN()",[]),("bookedOf_user","bookedOf(address)",U)]),
 "OUTY": ("0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412", [("minted","minted()",[]),("freeSold","freeSold()",[]),("paidSold","paidSold()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),("START","START()",[]),("FREE_END","FREE_END()",[]),("phase","phase()",[]),("freeOpen","freeOpen()",[]),("freeQuotaOf_user","freeQuotaOf(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "PX24": ("0xe712510fcb27935e657e41ebb97982d6b123136c", [("totalSupply","totalSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U),("costOf_user_1","costOf(address,uint256)",[USER,1])]),
 "SKRR": ("0x9081f02876c173d0c69f042959cfd0d61c668b17", [("totalSupply","totalSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U),("costOf_user_1","costOf(address,uint256)",[USER,1])]),
 "Thor": ("0x8aa9d6a09caf475593852e681b58b26dc94edd56", [("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "Feed-5877": ("0x5877D2bb9F226cC3E438F4d656cAeb27DEAFC576", [("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),("mintFree","mintFree()",[]),("balanceOf_user","balanceOf(address)",U)]),
}
reads,ok={},0
for name,(addr,views) in ITEMS.items():
    r=raw_batch(addr,views)
    reads[name]={"address":addr,"views":r}
    if r is not None: ok+=1
    print(name,"OK" if r is not None else "FAIL",json.dumps(r)[:240],flush=True)
def block_number():
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=15)
            if isinstance(r,dict) and r.get("result"): return int(r["result"],16)
        except Exception: continue
    return None
blk=block_number()
out={"started_wib":"2026-11-13T22:31+07:00","reads":reads,"reads_ok":ok,"reads_total":len(ITEMS),"block":blk,"elapsed_s":round(time.time()-t0,1)}
json.dump(out,open(BASE+"run-2026-11-13-2231-retry.json","w"),indent=1)
print("DONE reads_ok",ok,"/",len(ITEMS),"block",blk,"elapsed",round(time.time()-t0,1))
