#!/usr/bin/env python3
"""Run 0931: deep-dive MILLION free leg — totalMinted jumped 94->174 but all free views were None.
Retry free views with longer timeout on 3 RPCs; distinguish absent-function (revert) from RPC failure."""
import json, urllib.request
from Crypto.Hash import keccak
MILLION="0xD36B54fbd4c9fA99731b52907713c9e1983aD8a4"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(to,data,timeout=10):
    errs=[]
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=timeout) as r: out=json.load(r)
            if "error" in out: errs.append(out["error"].get("message","?")); continue
            v=out["result"]
            if not v or v=="0x": return ("empty",None)
            return ("ok",int(v,16))
        except Exception as e: errs.append(repr(e)[:80])
    return ("fail",errs)
out={}
for sig,args in [("totalMinted()",""),("freeMinted()",""),("freeClaimed()",""),("freeClaimed(address)",enc(USER)),
                 ("canFreeMint(address)",enc(USER)),("quote(address,uint256)",enc(USER)+"0000000000000000000000000000000000000000000000000000000000000001"),
                 ("mintCost(address,uint256)",enc(USER)+"0000000000000000000000000000000000000000000000000000000000000001"),
                 ("FREE_SUPPLY()",""),("freeSupply()",""),("agentRegistry()","")]:
    out[sig]=call(MILLION,sel(sig)+args)
    print(sig, out[sig], flush=True)
json.dump(out,open("run-2026-11-06-0931-million-probe.json","w"),indent=1,default=str)
