#!/usr/bin/env python3
"""Verify OchreMedallion 0xF3A8... (probe-possible-sale, Sourcify exact_match). Read-only batched eth_call."""
import json, subprocess
from eth_abi import encode, decode
from eth_hash.auto import keccak
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR="0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig): return keccak(sig.encode()).hex()[:8]
def enc(sig, args=(), types=()):
    return "0x"+sel(sig)+encode(types, args).hex() if types else "0x"+sel(sig)
CALLS=[
 ("name","name()",(),()),
 ("symbol","symbol()",(),()),
 ("freeMinted","freeMinted()",(),()),
 ("FREE_SUPPLY","FREE_SUPPLY()",(),()),
 ("freeRemaining","freeRemaining()",(),()),
 ("saleOpen","saleOpen()",(),()),
 ("mintOpen","mintOpen()",(),()),
 ("isFreeOpen","isFreeOpen()",(),()),
 ("saleStart","saleStart()",(),()),
 ("SALE_END","SALE_END()",(),()),
 ("saleEnd","saleEnd()",(),()),
 ("agentIdRegistry","agentIdRegistry()",(),()),
 ("freeAvailable_user","freeAvailable(address)",(USER,),("address",)),
 ("freeMintedBy_user","freeMintedBy(address)",(USER,),("address",)),
 ("remainingQuota_user","remainingQuota(address)",(USER,),("address",)),
 ("costOf_user_1","costOf(address,uint256)",(USER,1),("address","uint256")),
 ("quote_user_1","quote(address,uint256)",(USER,1),("address","uint256")),
 ("totalSupply","totalSupply()",(),()),
 ("totalMinted","totalMinted()",(),()),
 ("FREE_PER_WALLET","FREE_PER_WALLET()",(),()),
 ("PRICE","PRICE()",(),()),
 ("contractURI","contractURI()",(),()),
]
reqs=[{"jsonrpc":"2.0","id":i,"method":"eth_call","params":[{"to":ADDR,"data":enc(s,a,t)},"latest"]} for i,(n,s,a,t) in enumerate(CALLS)]
body=subprocess.run(["curl","-sS","-m","30","-H","Content-Type: application/json","-d",json.dumps(reqs),"https://bsc-dataseed.binance.org/"],capture_output=True,text=True,timeout=40).stdout
resp=json.loads(body)
by={it["id"]:it for it in resp}
out={}
DEC={"name":("string",),"symbol":("string",),"contractURI":("string",),"agentIdRegistry":("address",),
 "saleOpen":("bool",),"mintOpen":("bool",),"isFreeOpen":("bool",),
 "quote_user_1":("uint256","uint256","uint256","bool","string")}
for i,(n,s,a,t) in enumerate(CALLS):
    r=by.get(i,{}).get("result")
    if not r or r=="0x": out[n]=None; continue
    try:
        types=DEC.get(n,("uint256",))
        v=decode(types, bytes.fromhex(r[2:]))
        out[n]= v[0] if len(v)==1 else list(v)
    except Exception as e:
        out[n]=f"decode-error {e} raw={r[:80]}"
import time
out["_checked_wib"]=time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time()+7*3600))
print(json.dumps(out, indent=1, default=str))
json.dump(out, open(f"{HF}/hot-leg-2026-11-13-1434-f3a8-verify.json","w"), indent=1, default=str)
