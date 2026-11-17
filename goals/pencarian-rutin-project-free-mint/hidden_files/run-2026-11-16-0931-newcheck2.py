#!/usr/bin/env python3
"""Batched check: AETHER 0x9265 + Boltbook-new 0xfd34. Read-only. One batch per contract."""
import json, subprocess, time, urllib.request
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def build(sig,args):
    d=sel(sig)
    for a in args:
        if isinstance(a,str) and a.startswith("0x") and len(a)==42: d+=enc_addr(a)
        else: d+=enc_u(int(a))
    return d
def batch(addr,views):
    calls=[]; meta=[]
    for key,sig,args in views:
        calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call","params":[{"to":addr,"data":build(sig,args)},"latest"]})
        meta.append((key,sig))
    for ep in EPS:
        try:
            out=subprocess.run(["curl","-sL","--max-time","120","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(calls)],capture_output=True,text=True,timeout=130).stdout
            res=json.loads(out)
            if not isinstance(res,list) or len(res)!=len(calls): print(" bad shape",ep,str(res)[:100]); continue
            outd={}
            for it,(key,sig) in zip(res,meta):
                r=it.get("result")
                if not isinstance(it,dict) or "error" in it or not r or r=="0x": outd[key]=None; continue
                if sig in ("name()","symbol()","tokenURI(uint256)"):
                    try:
                        b=bytes.fromhex(r[2:]); off=int.from_bytes(b[32:64],"big"); ln=int.from_bytes(b[64:96],"big")
                        outd[key]=b[96:96+ln].decode(errors="ignore")
                    except Exception: outd[key]=r
                else:
                    try: outd[key]=int(r,16)
                    except Exception: outd[key]=r
            return outd
        except Exception as e:
            print(" ep fail",ep,str(e)[:100]); continue
    return {}
U=[USER]
VIEWS=[("name","name()",[]),("symbol","symbol()",[]),("totalSupply","totalSupply()",[]),
 ("totalMinted","totalMinted()",[]),("freeClaimed","freeClaimed()",[]),("freeMinted","freeMinted()",[]),
 ("FREE_SUPPLY","FREE_SUPPLY()",[]),("FREE_CAP","FREE_CAP()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
 ("mintOpen","mintOpen()",[]),("paused","paused() ",[]),("owner","owner()",[]),
 ("cost_user_1","cost(address,uint256)",[USER,1]),("mintedBy_user","mintedBy(address)",U),
 ("balanceOf_user","balanceOf(address)",U),("contractURI","contractURI()",[])]
for label,addr in [("AETHER","0x926504d174e99DB699141049b3Dd94dF501ff813"),("BOLTBOOK-ZH-NEW","0xfd3430e86df73c4e1e55036dc368a52716b84937")]:
    t0=time.time()
    d=batch(addr,VIEWS)
    print("==",label,addr,f"({time.time()-t0:.1f}s)")
    for k,v in d.items(): print("  ",k,":",v)
    # sourcify abi names
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",headers={"User-Agent":"free-mint-search/0931"})
        with urllib.request.urlopen(req,timeout=25) as resp: m=json.loads(resp.read().decode())
        names={e["name"] for e in m.get("abi",[]) if e.get("type")=="function"}
        print("  sourcify verified, n_fns",len(names))
        print("  agent_ref:",sorted(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate","AGENT_REGISTRY","AGENT_ID"}))
        print("  free_views:",sorted(names & {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}))
        print("  has_mint:",any(n.lower().startswith("mint") for n in names),"| fns:",sorted(names))
    except Exception as e:
        print("  sourcify error:",type(e).__name__,str(e)[:120])
    # code size + registry bytes
    try:
        p={"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]}
        out=subprocess.run(["curl","-sL","--max-time","30","-X","POST",EPS[0],"-H","Content-Type: application/json","-d",json.dumps(p)],capture_output=True,text=True,timeout=40).stdout
        code=json.loads(out).get("result","")
        print("  code_bytes:",(len(code)-2)//2,"| registry_bytes:","60b9262456de011f7d15a54cdd8c48baaa8b022f" in code.lower())
    except Exception as e: print("  code error:",str(e)[:80])
