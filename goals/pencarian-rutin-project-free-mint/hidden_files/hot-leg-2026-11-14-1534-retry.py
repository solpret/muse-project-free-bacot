#!/usr/bin/env python3
"""One-off retry of failed re-read chunks 1-2 (10 items) from hot-leg 1534 run.
Smaller batches (2 items), binance dataseed first. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/",
     "https://bsc-dataseed2.bnbchain.org/","https://bsc-rpc.publicnode.com/"]
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
        d+=enc_addr(a) if isinstance(a,str) and a.startswith("0x") and len(a)==42 else enc_u(int(a))
    return d
def post(ep,payload,timeout=45):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
        "-H","Content-Type: application/json","-d",json.dumps(payload)],
        capture_output=True,text=True,timeout=timeout+10).stdout
    return json.loads(out)
U=[USER]
ITEMS={
 "PIXEL FROGS": ("0x454054e55FA2D7Ba37df7F3ceA269696f19037dF", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("freeLeft","freeLeft()",[]),("FREE_CAP","FREE_CAP()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintStart","mintStart()",[]),("mintEnd","mintEnd()",[]),
    ("freeClaimed_user","freeClaimed(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "WANGCAI": ("0x61A2ff9Be3db25e23886bC59D92d44fAa05959Cd", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "YUANBAO": ("0xE8cF9969f8E8601a5Fed1DD39dE0E6c7959E7f9E", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "B77D-Kryntar": ("0xB77D3495d3ed4427dA78c9D0f7Cb76C21c23D9fe", [
    ("totalMinted","totalMinted()",[]),("mintOpen","mintOpen()",[]),
    ("standardRemaining","standardRemaining()",[]),("legendaryRemaining","legendaryRemaining()",[]),
    ("hasAgentId_user","hasAgentId(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "RaceAgents": ("0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_MAX","FREE_MAX()",[]),("mintOpen","mintOpen()",[])]),
 "Pengu": ("0x5AEc03C90656743475810926B2B2bd443D5c26a4", [
    ("freeMinted","freeMinted()",[]),("FREE_CAP","FREE_CAP()",[]),
    ("totalMinted","totalMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("freeClaimed_user","freeClaimed(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "Zephyra": ("0x00a9791be6317d6e3a6c60f75a706c870d882048", [
    ("totalMinted","totalMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("mintedBy_user","mintedBy(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "DragonAgents": ("0xad0D8ac3D61fC8ab397B7136C69fcBf1281a4998", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "BinanceAI-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched","launched()",[]),("failed","failed()",[]),
    ("isRefundPhase","isRefundPhase()",[]),("totalShares","totalShares()",[]),
    ("tokenClaimed_user","tokenClaimed(address)",U)]),
 "AngelEye-77D9": ("0x77D98247BA3dDAfa9ffBceA1F13d3e4cFe3f2d4C", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("freeRemaining","freeRemaining()",[]),
    ("FREE_POOL","FREE_POOL()",[]),("saleActive","saleActive()",[]),
    ("mintStart","mintStart()",[]),("mintEnd","mintEnd()",[])]),
}
def read_chunk(chunk):
    calls,meta=[],[]
    for name,(addr,views) in chunk:
        for key,sig,args in views:
            calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call",
                "params":[{"to":addr,"data":build(sig,args)},"latest"]})
            meta.append((name,key))
    for ep in EPS:
        try:
            res=post(ep,calls,timeout=45)
            if not isinstance(res,list) or len(res)!=len(calls):
                print(f"  ep {ep} bad shape: {str(res)[:120]}",flush=True); continue
            n_ok=sum(1 for it in res if isinstance(it,dict) and "result" in it and it.get("result") not in (None,"0x"))
            print(f"  ep {ep} ok-results {n_ok}/{len(calls)}",flush=True)
            if n_ok==0: continue
            out={}
            for it,(name,key) in zip(res,meta):
                if not isinstance(it,dict) or "error" in it or it.get("result") in (None,"0x"):
                    out.setdefault(name,{})[key]=None
                else:
                    r=it["result"]; out.setdefault(name,{})[key]=to_int(r[:66]) if len(r)>=66 else r
            return out,ep
        except Exception as e:
            print(f"  ep {ep} exc {str(e)[:100]}",flush=True); continue
    return None,None
items=list(ITEMS.items())
reads={}
for i in range(0,len(items),2):
    ch=items[i:i+2]
    r,ep=read_chunk(ch)
    print(f"chunk {[n for n,_ in ch]} -> {ep}",flush=True)
    for n,_ in ch: reads[n]={"address":ITEMS[n][0],"views":r.get(n) if r else None}
blk=None
for ep in EPS:
    try:
        r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=45)
        if isinstance(r,dict) and r.get("result"): blk=int(r["result"],16); break
    except Exception: continue
ok=sum(1 for n in reads if reads[n]["views"] is not None and any(v is not None for v in reads[n]["views"].values()))
print("retry ok items:",ok,"/",len(reads),"block",blk,"elapsed",round(time.time()-t0,1))
json.dump({"run":"hot-leg 1534 retry chunks 1-2","reads":reads,"block":blk,
           "elapsed_s":round(time.time()-t0,1)},
          open(BASE+"hot-leg-run-2026-11-14-1534-retry.json","w"),indent=1)
