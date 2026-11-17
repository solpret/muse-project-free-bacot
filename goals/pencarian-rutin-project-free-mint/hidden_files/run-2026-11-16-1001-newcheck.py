#!/usr/bin/env python3
"""New-check run 2026-11-16 10:01 WIB: NEUPEN 0x91a1... (Boltbook census 10:02 WIB: freeClaimed 792/7000, mintOpen 1, 3 free/wallet) + FROGY 0x5136... (Boltbook tale.ai 10:01 WIB: totalSupply 0/999; hot-leg-seen since 2026-11-02, S1/S2 false then). Read-only; no preview/mint."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-rpc.publicnode.com/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def build(sig,args):
    d=sel(sig)
    for a in args:
        d+= enc_addr(a) if (isinstance(a,str) and a.startswith("0x") and len(a)==42) else enc_u(int(a))
    return d
def post(ep,payload,timeout=60):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+10).stdout
    return json.loads(out)
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
ITEMS={
 "NEUPEN":("0x91a1b0e9ee45ff34ef41df920041cccfe4ada26d",[("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),("FREE_MAX","FREE_MAX()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),("totalMinted","totalMinted()",[]),("name","name()",[]),("symbol","symbol()",[]),("balanceOf_user","balanceOf(address)",[USER]),("mintedBy_user","mintedBy(address)",[USER]),("freeClaimed_user","freeClaimed(address)",[USER]),("cost_user_1","cost(address,uint256)",[USER,1]),("priceFor_user","priceFor(address)",[USER]),("hasAgentId_user","hasAgentId(address)",[USER])]),
 "FROGY":("0x51367fbd6d140f22892db62c1b7812088dd8f821",[("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),("FREE_MAX","FREE_MAX()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),("totalMinted","totalMinted()",[]),("name","name()",[]),("symbol","symbol()",[]),("balanceOf_user","balanceOf(address)",[USER]),("mintedBy_user","mintedBy(address)",[USER])]),
}
out={}
blk=None
for name,(addr,views) in ITEMS.items():
    calls=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":build(sig,args)},"latest"]} for i,(k,sig,args) in enumerate(views)]
    res=None; ep_used=None
    for ep in EPS:
        try:
            r=post(ep,calls)
            if isinstance(r,list) and len(r)==len(calls): res=r; ep_used=ep; break
        except Exception as e: print(name,"ep",ep,"exc",str(e)[:80],flush=True)
    vals={}
    if res:
        for it,(k,sig,args) in zip(res,views):
            if not isinstance(it,dict) or "error" in it or it.get("result") in (None,"0x"): vals[k]=None
            else:
                rr=it["result"]
                vals[k]=to_int(rr[:66]) if len(rr)>=66 else rr
    out[name]={"address":addr,"views":vals,"ep":ep_used}
    print(name, vals, "via", ep_used, flush=True)
# block + code size + registry bytes
for name,(addr,views) in ITEMS.items():
    code=None
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]})
            if isinstance(r,dict) and r.get("result"): code=r["result"]; break
        except Exception: pass
    reg = code and "60b9262456de011f7d15a54cdd8c48baaa8b022f" in code.lower()
    out[name]["code_len"]= (len(code)-2)//2 if code else None
    out[name]["registry_bytes"]= bool(reg)
    print(name,"code_len",out[name]["code_len"],"registry_bytes",bool(reg),flush=True)
    # Sourcify ABI
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",headers={"User-Agent":"free-mint-search/1001"})
        with urllib.request.urlopen(req,timeout=30) as resp: meta=json.loads(resp.read().decode())
        abi=meta.get("abi",[]); names={e["name"] for e in abi if e.get("type")=="function"}
        out[name]["sourcify"]={"match":meta.get("match"),"n_fns":len(names),
          "mint":any(n.lower().startswith("mint") for n in names),
          "quote":bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"}),
          "free_views":sorted(names & {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}),
          "agent_ref":bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"}),
          "site_fns":sorted(names & {"website","siteURL","externalUrl","externalLink","contractURI","tokenURI"})}
    except Exception as e:
        out[name]["sourcify"]={"error":f"{type(e).__name__}: {str(e)[:120]}"}
    print(name,"sourcify",out[name]["sourcify"],flush=True)
try:
    r=post(EPS[1],{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})
    blk=int(r["result"],16)
except Exception: pass
out["_block"]=blk
json.dump(out,open("run-2026-11-16-1001-newcheck.json","w"),indent=1)
print("BLOCK",blk)
