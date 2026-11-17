#!/usr/bin/env python3
"""Supplement 13:09 run — re-read 6 leg4 tail targets skipped on deadline (T0+195)."""
import json, subprocess, time
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG="2026-11-12-1309"
T0=time.time(); DEADLINE=T0+100
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
now_wib=datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def post_rpc(ep,payload,timeout=15):
    outb=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(outb)
def get_block():
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=15)
            return int(r["result"],16)
        except Exception: continue
    return None
def raw_batch(addr,views):
    calls,keys=[],[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    for ep in EPS:
        if time.time()>DEADLINE: return None
        try:
            res=post_rpc(ep,calls,timeout=15)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {key:(None if (isinstance(it,dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,key in zip(res,keys)}
        except Exception: continue
    return None
VIEWS=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","balanceOf(address)","freeClaimed(address)","freeUsed(address)","mintedBy(address)","freeMintedBy(address)","mintStart()","freeLeft()","freeAvailable(address)","saleStart()","saleEnd()","PRICE()","price()","launched()","freeSharesLeft()","openedAt()","freeSharesRemaining()","freeClaimedByWallet(address)","currentState()","finalized()","refunding()","totalFreeMinted()","FREE_SHARES()","freeLeftFor(address)"]
TARGETS=[("0x2e50","0x2e508C6510d9550031932f0D6Fe691DCe38E66E3"),("Kongtou-AirdropCnNFT","0xb5A132A2Efd8351DA2c04e38E2568dd8DC5b1c1a"),("0x7Eb9","0x7Eb92041aa3037e39baA88154F279e3D9F85c593"),("NAOMI","0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9"),("AgenticGangster","0x0a2a07ef09dd7d83e2312476f0588abaa3e34ce3"),("Airdrop-417d","0x417d04C0a323fC89cDBbEf4D361161fCfA45baF9")]
block=get_block()
reads={}
for name,addr in TARGETS:
    if time.time()>DEADLINE: reads[name]={"address":addr,"error":"deadline-hit-skipped"}; continue
    r=raw_batch(addr,VIEWS)
    reads[name]={"address":addr,"views":r}
    if r: reads[name]["summary"]={k:v for k,v in r.items() if v is not None}
out={"started_wib":now_wib,"block":block,"reads":reads,"elapsed_s":round(time.time()-T0,1)}
json.dump(out,open(BASE+"run-2026-11-12-1309-verify2-supplement.json","w"),indent=1)
print(json.dumps(out,indent=1))
