#!/usr/bin/env python3
"""Targeted retry 19:09 run: AgentPals slot + fresh pool; Stampooor pool/slot. Publicnode first, 3 attempts each, 15s timeout."""
import json, time, urllib.request
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc.publicnode.com","https://bsc.nodereal.io/","https://bsc-dataseed.binance.org/"]
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x","").rjust(64,"0")
def call(addr,sig,args="",attempts=3):
    data=sel(sig)+args
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}).encode()
    for att in range(attempts):
        for ep in EPS:
            try:
                req=urllib.request.Request(ep,data=body,headers={"Content-Type":"application/json"})
                with urllib.request.urlopen(req,timeout=15) as r: j=json.loads(r.read().decode())
                if "error" in j: return {"error":str(j["error"])[:150]}
                raw=j["result"]
                if raw in (None,"0x"): return {"error":"empty-return"}
                if len(raw)>=66:
                    v=raw[2:66]
                    if set(v)<=set("0123456789abcdef"):
                        try: return int(v,16)
                        except Exception: return raw
                return raw
            except Exception as e:
                last=e; continue
        time.sleep(2)
    return {"error":f"all-endpoints-failed: {type(last).__name__}: {str(last)[:100]}"}
def block():
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=15) as r: return int(json.loads(r.read().decode())["result"],16)
        except Exception: continue
    return None
U=enc_addr(USER)
AP="0xD265a929D0E50bD5ee4675e4E97F38D8380802E2"
ST="0x467696af8c2206B977B24081445104632dc1D459"
out={"block":block(),"agentpals":{
 "freeMinted":call(AP,"freeMinted()"),
 "totalMinted":call(AP,"totalMinted()"),
 "freePhaseStart":call(AP,"freePhaseStart()"),
 "hasFreeMinted_user":call(AP,"hasFreeMinted(address)",U),
 "balanceOf_user":call(AP,"balanceOf(address)",U),
 "contractURI":call(AP,"contractURI()"),
 "baseURI":call(AP,"baseURI()"),
},"stampooor":{
 "freeMinted":call(ST,"freeMinted()"),
 "totalMinted":call(ST,"totalMinted()"),
 "FREE_SUPPLY":call(ST,"FREE_SUPPLY()"),
 "mintOpen":call(ST,"mintOpen()"),
 "freeAvailable_user":call(ST,"freeAvailable(address)",U),
 "balanceOf_user":call(ST,"balanceOf(address)",U),
}}
print(json.dumps(out,indent=1))
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-11-1909-agentpals.json","w"),indent=1)
