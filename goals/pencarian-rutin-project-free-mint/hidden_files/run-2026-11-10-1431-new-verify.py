#!/usr/bin/env python3
"""Verify Orbit Signal + Claf Eye (Boltbook leads run 1431). Read-only."""
import json, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
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
def u(to,sig,args=""):
    v=call(to,sel(sig)+args)
    return int(v,16) if v is not None else None
def s(to,sig):
    # string return: offset+len+data
    v=call(to,sel(sig))
    if not v: return None
    try:
        ln=int(v[2+64:2+128],16)
        return bytes.fromhex(v[2+128:2+128+ln*2]).decode("utf-8","replace")
    except Exception: return f"<raw {v[:80]}>"
def a(to,sig):
    v=call(to,sel(sig))
    return ("0x"+v[-40:]) if v else None
out={}
ORB="0x32ef9524771fac05585af142702e4d7a6b5f7ad9"
EYE="0x1c759c4e075103b5b250db5114b832b17b99c456"
out["orbit"]={
 "totalSupply":u(ORB,"totalSupply()"),"MAX_SUPPLY":u(ORB,"MAX_SUPPLY()"),"MAX_PER_WALLET":u(ORB,"MAX_PER_WALLET()"),
 "mintOpen":u(ORB,"mintOpen()"),"mintsLeft":u(ORB,"mintsLeft()"),
 "costOf_user_1":u(ORB,"costOf(address,uint256)",enc(USER)+"%064x"%1),
 "mintedBy_user":u(ORB,"mintedBy(address)",enc(USER)),
 "price":u(ORB,"price()"),"owner":a(ORB,"owner()"),"treasury":a(ORB,"treasury()"),
 "name":s(ORB,"name()"),"symbol":s(ORB,"symbol()"),
}
out["eye"]={
 "totalSupply":u(EYE,"totalSupply()"),"MAX_SUPPLY":u(EYE,"MAX_SUPPLY()"),"MAX_PER_WALLET":u(EYE,"MAX_PER_WALLET()"),
 "costFor_user_1":u(EYE,"costFor(address,uint256)",enc(USER)+"%064x"%1),
 "priceOf_1":u(EYE,"priceOf(uint256)","%064x"%1),
 "PRICE_FIRST":u(EYE,"PRICE_FIRST()"),"PRICE_2_10":u(EYE,"PRICE_2_10()"),
 "mintedBy_user":u(EYE,"mintedBy(address)",enc(USER)),
 "agentRegistry":a(EYE,"agentRegistry()"),"owner":a(EYE,"owner()"),"treasury":a(EYE,"treasury()"),
 "WEBSITE":s(EYE,"WEBSITE()"),"X":s(EYE,"X()"),"MINT_SITE":s(EYE,"MINT_SITE()"),
 "contractURI":s(EYE,"contractURI()"),
 "name":s(EYE,"name()"),"symbol":s(EYE,"symbol()"),
}
print(json.dumps(out,indent=1))
disc=json.load(open(f"{BASE}/same-owner-discards.json"))
owners={str(e.get('owner','')).lower() for e in disc if isinstance(e,dict) and e.get('owner')}
contracts={str(e.get('contract','')).lower() for e in disc if isinstance(e,dict)}
for k in ("orbit","eye"):
    o=out[k].get("owner")
    print(k,"owner",o,"in_discards_owner:",(o or "").lower() in owners,"contract_in_discards:", (ORB if k=="orbit" else EYE).lower() in contracts)
json.dump(out,open(f"{BASE}/run-2026-11-10-1431-new-verify.json","w"),indent=1)
