#!/usr/bin/env python3
"""Verify new Boltbook items run 1701: HEXCOVEN, Orin, Pulse, BUBB recheck, Punch Card recheck, LABTOK, MUSE. Read-only; no preview/mint."""
import json, subprocess, time, urllib.request
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
t0=time.time()
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def build(sig,args):
    d=sel(sig)
    for a in args:
        if isinstance(a,str) and a.startswith("0x") and len(a)==42: d+=enc_addr(a)
        elif isinstance(a,str) and a.startswith("0x"): d+=enc_u(int(a,16))
        else: d+=enc_u(int(a))
    return d
def post(ep,payload,timeout=120):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+10).stdout
    return json.loads(out)
U=[USER]
ITEMS={
 "HEXCOVEN":("0xd3d5d57e4942cedcb6864c1dce1e9808544dd30d",[("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),("freeMinted","freeMinted()",[]),("freeClaimed","freeClaimed()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),("PRICE","PRICE()",[]),("price","price()",[]),("mintPrice","mintPrice()",[]),("balanceOf_user","balanceOf(address)",U),("name","name()",[]),("symbol","symbol()",[])]),
 "Orin":("0x91921eb375fe32706f8cd92376f613f923d01771",[("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),("freeMinted","freeMinted()",[]),("freeClaimed","freeClaimed()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U),("name","name()",[]),("symbol","symbol()",[])]),
 "PulseDistrict":("0xf6cc6364c0d7764a5a751c08314db181df5b825c",[("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),("freeMinted","freeMinted()",[]),("freeClaimed","freeClaimed()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U),("name","name()",[]),("symbol","symbol()",[])]),
 "BUBB":("0x0d72970046c056db90888351b739246f468bff0b",[("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),("freeMinted","freeMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "PunchCard":("0x1d4ef0587dd3ff3875a141d4711c60bca40587c4",[("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),("freeMinted","freeMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),("mintPriceFor_user_1","mintPriceFor(address,uint256)",[USER,1]),("mintedCount_user","mintedCount(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "LABTOK":("0x849368938eA0092c809A687FaC0b3ECA3940561f",[("totalSupply","totalSupply()",[]),("name","name()",[]),("symbol","symbol()",[]),("decimals","decimals()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "MUSE":("0x779fa133848d23052B7345F63B3b2E5309cd13ed",[("seatsTaken","seatsTaken()",[]),("totalSupply","totalSupply()",[]),("balanceOf_user","balanceOf(address)",U)]),
}
def read_chunk(chunk):
    calls,meta=[],[]
    for name,(addr,views) in chunk:
        for key,sig,args in views:
            calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call","params":[{"to":addr,"data":build(sig,args)},"latest"]})
            meta.append((name,key))
    for ep in EPS:
        try:
            res=post(ep,calls)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            out={}
            for it,(name,key) in zip(res,meta):
                if not isinstance(it,dict) or "error" in it or it.get("result") in (None,"0x"):
                    out.setdefault(name,{})[key]=None
                else:
                    r=it["result"]
                    out.setdefault(name,{})[key]=to_int(r[:66]) if len(r)>=66 else r
            return out,ep
        except Exception as e:
            print("  ep fail",ep,str(e)[:80],flush=True); continue
    return None,None
def block_number():
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})
            if isinstance(r,dict) and r.get("result"): return int(r["result"],16)
        except Exception: continue
    return None
def sourcify(addr):
    url=f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"free-mint-search/1701"})
        with urllib.request.urlopen(req,timeout=25) as r: meta=json.loads(r.read().decode())
        abi=meta.get("abi",[])
        names=sorted({e["name"] for e in abi if e.get("type")=="function"})
        src=json.dumps(meta)
        return {"verified":True,"n_fns":len(names),"names":names,
                "has_registry_ref": ("0x60b9262456de011f7d15a54cdd8c48baa8b022f" in src.lower()),
                "has_agent_fn": bool(set(names)&{"agentIdRegistry","agentRegistry","AgentGate","agentGate","holdsAgentId","hasAgentId"})}
    except Exception as e:
        return {"verified":False,"error":f"{type(e).__name__}: {str(e)[:120]}"}
reads={}
items=list(ITEMS.items())
for i in range(0,len(items),2):
    ch=items[i:i+2]
    r,ep=read_chunk(ch)
    for n,_ in ch: reads[n]={"address":ITEMS[n][0],"views":(r or {}).get(n)}
    print("chunk",[n for n,_ in ch],"via",ep,flush=True)
    time.sleep(3)
blk=block_number()
src={n: sourcify(ITEMS[n][0]) for n in ITEMS}
out={"started_wib":"2026-11-16T17:01+07:00","reads":reads,"sourcify":src,"block":blk,"elapsed_s":round(time.time()-t0,1)}
json.dump(out,open(BASE+"run-2026-11-16-1701-verify.json","w"),indent=1)
print("DONE block",blk,"elapsed",round(time.time()-t0,1))
for n in ITEMS:
    print(n, reads[n]["views"])
    print("  src:", {k:src[n].get(k) for k in ("verified","n_fns","has_registry_ref","has_agent_fn","error") if k in src[n]})
    if src[n].get("names"): print("  fns:", src[n]["names"])
