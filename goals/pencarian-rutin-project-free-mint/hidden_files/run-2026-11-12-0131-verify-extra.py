#!/usr/bin/env python3
"""Extra targeted reads run 0131: SUDOSAINTS launch-time views (age decision),
Eco (hot-leg 0109 early lead, add to snapshot), Pickgrid (72% age-unverified).
Read-only; writes run-2026-11-12-0131-verify-extra.json."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def post_rpc(ep,payload,timeout=25):
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
            res=post_rpc(ep,calls,timeout=25)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {key:(None if (isinstance(it,dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,key in zip(res,keys)}
        except Exception: continue
    return None
def get_block():
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=25)
            return int(r["result"],16)
        except Exception: continue
    return None
VIEWS=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","FREE_CAP()",
       "MAX_SUPPLY()","mintOpen()","balanceOf(address)","freeClaimed(address)","freeUsed(address)",
       "mintedBy(address)","mintStart()","mintOpenedAt()","saleStart()","freePoolSize()",
       "totalFreeCount()","freeLeft()","firstFreeUsed()","paidMinted()","isAgent(address)",
       "freeAvailable(address)","freePerWallet()","PRICE()","price()","AGENT_ID_REGISTRY()",
       "agentIdRegistry()","holdsAgentId(address)","freeCountBy(address)","mintsBy(address)"]
TARGETS={
 "SUDOSAINTS":"0x869d330bb48e7ab32da16745ef9a36a69d34f12f",
 "Eco":"0xd31b168F7b6f3dB39BEd89433124595aaa91cfF3",
 "Pickgrid":"0x7f541bcc33abed0e64455565da723e949c6f76f0",
}
out={"block":get_block(),"started_wib":"2026-11-12 01:31 WIB","verify":{}}
print("BLOCK",out["block"],flush=True)
for name,addr in TARGETS.items():
    t=time.time(); got=raw_batch(addr,VIEWS)
    d={"address":addr}
    if got is None: d["_batch_fail"]=True
    else: d.update(got)
    out["verify"][name]=d
    print(name, {k:v for k,v in d.items() if v is not None}, f"({time.time()-t:.1f}s)", flush=True)
json.dump(out,open(BASE+"run-2026-11-12-0131-verify-extra.json","w"),indent=1)
print("VERIFY-EXTRA DONE")
