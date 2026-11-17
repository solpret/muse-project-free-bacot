#!/usr/bin/env python3
"""Verify NOGENT + Hakuna + 0x57787441 (Boltbook leads run 1531). Read-only."""
import json, subprocess, urllib.request
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
    v=call(to,sel(sig))
    if not v: return None
    try:
        ln=int(v[2+64:2+128],16)
        return bytes.fromhex(v[2+128:2+128+ln*2]).decode("utf-8","replace")
    except Exception: return f"<raw {v[:80]}>"
def a(to,sig):
    v=call(to,sel(sig))
    return ("0x"+v[-40:]) if v else None
def getcode(to):
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[to,"latest"]},timeout=25)
            if "result" in r and r["result"] not in (None,"0x"): return r["result"]
        except Exception: continue
    return None
def sourcify(addr):
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",headers={"User-Agent":"free-bacot/1531"})
        with urllib.request.urlopen(req,timeout=30) as r: return json.loads(r.read().decode())
    except Exception as e: return {"error":str(e)[:120]}
ADDRS={
 "nogent":"0x1b6e6f62528de674c12bc2c04c159336d3db049e",
 "hakuna":"0x75f9e01af66a6b3b5f169d1d9c88e6f356a01e2f",
 "x5778":"0x577874415214780b37eb8966c41563954b76a8b8",
}
out={}
for k,addr in ADDRS.items():
    code=getcode(addr)
    out[k]={"address":addr,
     "name":s(addr,"name()"),"symbol":s(addr,"symbol()"),
     "totalSupply":u(addr,"totalSupply()"),"MAX_SUPPLY":u(addr,"MAX_SUPPLY()"),
     "FREE_SUPPLY":u(addr,"FREE_SUPPLY()"),"freeMinted":u(addr,"freeMinted()"),
     "freeClaimed":u(addr,"freeClaimed()"),"freeLeft":u(addr,"freeLeft()"),
     "FREE_PER_WALLET":u(addr,"FREE_PER_WALLET()"),"MAX_PER_WALLET":u(addr,"MAX_PER_WALLET()"),
     "mintOpen":u(addr,"mintOpen()"),"mintPrice":u(addr,"mintPrice()"),"price":u(addr,"price()"),
     "costOf_user_1":u(addr,"costOf(address,uint256)",enc(USER)+"%064x"%1),
     "costFor_user_1":u(addr,"costFor(address,uint256)",enc(USER)+"%064x"%1),
     "priceOf_1":u(addr,"priceOf(uint256)","%064x"%1),
     "mintedBy_user":u(addr,"mintedBy(address)",enc(USER)),
     "freeMintedBy_user":u(addr,"freeMintedBy(address)",enc(USER)),
     "owner":a(addr,"owner()"),"agentRegistry":a(addr,"agentRegistry()"),"agentId":a(addr,"agentId()"),
     "WEBSITE":s(addr,"WEBSITE()"),"X":s(addr,"X()"),"contractURI":s(addr,"contractURI()"),
     "code_len": (len(code)-2)//2 if code else None,
     "registry_bytes": (REG[2:].lower() in code.lower()) if code else None,
    }
    meta=sourcify(addr)
    out[k]["sourcify"]="exact_match" if meta.get("stdJson") or meta.get("creationMatch") else ("error:"+str(meta.get("error","?"))[:80] if "error" in meta else "not_verified")
    abi=meta.get("abi") or []
    out[k]["abi_fns"]=sorted({e["name"] for e in abi if e.get("type")=="function"}) if abi else []
print(json.dumps(out,indent=1))
disc=json.load(open(f"{BASE}/same-owner-discards.json"))
owners={str(e.get('owner','')).lower() for e in disc if isinstance(e,dict) and e.get('owner')}
contracts={str(e.get('contract','')).lower() for e in disc if isinstance(e,dict)}
for k,addr in ADDRS.items():
    o=out[k].get("owner")
    print(k,"owner",o,"in_discards_owner:",(o or "").lower() in owners,"contract_in_discards:",addr.lower() in contracts)
json.dump(out,open(f"{BASE}/run-2026-11-10-1531-new-verify.json","w"),indent=1)
