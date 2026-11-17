#!/usr/bin/env python3
"""Targeted re-read run 0634: only tier-critical contracts (WFPASS sellout watch,
Stampooor/SEVEN gate-blocked strong leads, Eco early, AGCR watchlist).
Short per-call timeouts; skip on fail, never block. Read-only; writes
run-2026-11-12-0634-verify-key.json."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def post_rpc(ep,payload,timeout=15):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def raw_batch(addr,views):
    calls,keys=[],[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res=post_rpc(ep,calls,timeout=15)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {key:(None if (isinstance(it,dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,key in zip(res,keys)}
        except Exception: continue
    return None
def get_block():
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=15)
            return int(r["result"],16)
        except Exception: continue
    return None
VIEWS=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()",
       "mintOpen()","balanceOf(address)","freeClaimed(address)","freeUsed(address)","freeUsedBy(address)",
       "mintedBy(address)","freeMintedBy(address)","mintStart()","mintOpenedAt()","freePoolSize()",
       "totalFreeCount()","freeLeft()","firstFreeUsed()","paidMinted()","isAgent(address)","freeAvailable(address)",
       "freePerWallet()","PRICE()","price()","saleStart()","saleEnd()","AGENT_ID_REGISTRY()","agentIdRegistry()","mintOpenSat()"]
TARGETS={
 "WFPASS":"0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C",
 "Stampooor":"0x467696af8c2206B977B24081445104632dc1D459",
 "SEVEN":"0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96",
 "Eco":"0xd31b168F7b6f3dB39BEd89433124595aaa91cfF3",
 "AGCR":"0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc",
 "CRTSAINTS":"0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F",
 "NAOMI":"0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9",
}
out={"block":get_block(),"started_wib":"2026-11-12 06:34 WIB (key re-read)","verify":{}}
print("BLOCK",out["block"],flush=True)
for name,addr in TARGETS.items():
    t=time.time(); got=raw_batch(addr,VIEWS)
    d={"address":addr}
    if got is None: d["_batch_fail"]=True
    else: d.update(got)
    out["verify"][name]=d
    print(name, {k:v for k,v in d.items() if v is not None}, f"({time.time()-t:.1f}s)", flush=True)
json.dump(out,open(BASE+"run-2026-11-12-0634-verify-key.json","w"),indent=1)
print("KEY VERIFY DONE")
