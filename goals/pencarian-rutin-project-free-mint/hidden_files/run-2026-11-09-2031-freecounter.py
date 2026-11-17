#!/usr/bin/env python3
"""Resolve freeMinted vs freeClaimed counters for Agentic / BAHUANG3 / Lenx. Read-only."""
import json, urllib.request
from Crypto.Hash import keccak
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org","https://bsc-dataseed.binance.org"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def rpc(method,params,timeout=20):
    for u in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
            req=urllib.request.Request(u,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=timeout) as r: out=json.load(r)
            if "error" in out: continue
            return out["result"]
        except Exception: continue
    return None
def call(addr,sig):
    v=rpc("eth_call",[{"to":addr,"data":sel(sig)},"latest"])
    if v is None or v=="0x": return None
    try: return int(v,16)
    except Exception: return v
VIEWS=["freeMinted()","freeClaimed()","freeCount()","freeRemaining()","freeLeft()","freeSupply()","FREE_SUPPLY()","FREE_CAP()","totalMinted()","totalSupply()","claimed()","claimedFree()","mintedFree()"]
ADDRS={"Agentic":"0x7BcC29c5405286b4Dd8b5b23FE7097F9EE65e4e5",
 "BAHUANG3":"0x2CCb3fA957E69AbD46A6651CC1444EF2Ea9bd591",
 "Lenx":"0x6E252E3a3584BD6a64C103e4eDFa761f6335980F",
 "TIME_CARDS":"0xc5624B61beE1971E6Aa3AB5f403236Ab32C2B6cd"}
out={}
for name,a in ADDRS.items():
    out[name]={v: call(a,v) for v in VIEWS}
    print(name, json.dumps(out[name]))
json.dump(out,open("run-2026-11-09-2031-freecounter.json","w"),indent=1)
