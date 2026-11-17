#!/usr/bin/env python3
"""Targeted fresh read of 6 promotion-relevant contracts (SEVENFOLD, FCAT, JINCHAN, Roguefall, Sakura, THYRK). Read-only; writes run-2026-11-10-0931-prio6.json."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
TARGETS={
 "SEVENFOLD":"0x4ca724a354db4f743607ecc1a5f117b2e617c8ae",
 "FCAT Agents":"0x349d8FBed5DE52A4e5065E143797d7B92846Be0e",
 "JINCHAN Agents":"0xfc9269a515E56A174AD32923a45868d6e97e7EE2",
 "Roguefall":"0x5fe03829a2f94a8ba3906459258b1305f0e68934",
 "Sakura":"0xF2705A84602369069782624279837A08bdbBf6D6",
 "THYRK":"0x4D90fFC3075FB8897EDFf6d7c6269c906664a20e",
}
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try:
        if v is None or v=="0x": return None
        return int(v,16)
    except Exception: return None
def post_rpc(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def batch(addr,views):
    calls,keys=[],[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    for ep in EPS:
        try:
            res=post_rpc(ep,calls,timeout=25)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {k:(None if (isinstance(it,dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,k in zip(res,keys)}
        except Exception: continue
    return None
VIEWS=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","balanceOf(address)","freeClaimed(address)","agentFreeUsed()","agentFreeCap()","mintStart()","freeUsedByWallet(address)","mintedBy(address)"]
def get_block():
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=25)
            return int(r["result"],16)
        except Exception: continue
    return None
out={"block":get_block(),"reads":{}}
for name,addr in TARGETS.items():
    t=time.time(); got=batch(addr,VIEWS)
    d={"address":addr}; d.update(got or {})
    out["reads"][name]=d
    print(name, "totalSupply=",d.get("totalSupply"),"freeMinted=",d.get("freeMinted"),"freeClaimed=",d.get("freeClaimed"),"agentFreeUsed=",d.get("agentFreeUsed"),"bal=",d.get("balanceOf_user"),f"({time.time()-t:.1f}s)",flush=True)
json.dump(out,open(f"{BASE}/run-2026-11-10-0931-prio6.json","w"),indent=1)
print("PRIO6 DONE block",out["block"])
