#!/usr/bin/env python3
"""WNO track-C lead verification, run 1431. Read-only."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WNO="0x8C969a4CD49E4774908e667702C3d7C3ece164D0"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG="0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def post_rpc(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def call(to,data):
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]},timeout=25)
            if "error" in r: continue
            v=r.get("result")
            if not v or v=="0x": return None
            return v
        except Exception: continue
    return None
def u1(sig,args=""):
    v=call(WNO,sel(sig)+args)
    return int(v,16) if v else None
def addr(sig):
    v=call(WNO,sel(sig))
    return ("0x"+v[-40:]) if v else None
out={}
out["registry"]=addr("registry()")
out["FREE_SHARES"]=u1("FREE_SHARES()")
out["totalFreeShares"]=u1("totalFreeShares()")
out["totalShares"]=u1("totalShares()")
out["totalPaidShares"]=u1("totalPaidShares()")
out["TOKENS_PER_SHARE"]=u1("TOKENS_PER_SHARE()")
out["PRICE"]=u1("PRICE()")
out["MAX_SHARES"]=u1("MAX_SHARES()")
out["MAX_PER_TX"]=u1("MAX_PER_TX()")
out["totalRaised"]=u1("totalRaised()")
out["freeUsed_user"]=u1("freeUsed(address)",enc(USER))
out["sharesOf_user"]=u1("sharesOf(address)",enc(USER))
out["isAgent_user"]=u1("isAgent(address)",enc(USER))
out["owner"]=addr("owner()")
q=call(WNO,sel("quote(address,uint256)")+enc(USER)+"0".rjust(64,"0").replace("0"*63+"0","0"*63+"1"))
# quote(user,1): encode 1 as uint256
q=call(WNO,sel("quote(address,uint256)")+enc(USER)+"%064x"%1)
if q:
    vals=[int(q[2+i*64:2+(i+1)*64],16) for i in range(3)]
    out["quote_user_1_raw"]=vals
ov=call(WNO,sel("overview()"))
if ov:
    out["overview"]=[int(ov[2+i*64:2+(i+1)*64],16) for i in range(7)]
print(json.dumps(out,indent=1))
# owner vs same-owner-discards
try:
    disc=json.load(open(f"{BASE}/same-owner-discards.json"))
    owners=set()
    if isinstance(disc,list):
        for e in disc:
            if isinstance(e,dict):
                for k in ("owner","deployer","address"):
                    if e.get(k): owners.add(str(e[k]).lower())
            elif isinstance(e,str): owners.add(e.lower())
    elif isinstance(disc,dict):
        for k,v in disc.items():
            owners.add(k.lower())
            if isinstance(v,dict) and v.get("owner"): owners.add(str(v["owner"]).lower())
    print("DISCARD_OWNERS_COUNT",len(owners))
    print("WNO_OWNER_IN_DISCARDS", (out.get("owner") or "").lower() in owners)
    print("WNO_OWNER", out.get("owner"))
except Exception as e:
    print("DISCARD CHECK ERROR", e)
json.dump(out,open(f"{BASE}/run-2026-11-10-1431-wno.json","w"),indent=1)
