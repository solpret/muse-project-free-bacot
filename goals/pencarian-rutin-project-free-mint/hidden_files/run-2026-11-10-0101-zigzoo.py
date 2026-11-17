#!/usr/bin/env python3
"""Zigzoo 0x09ada5... probe run 0101. Read-only."""
import json, urllib.request
from Crypto.Hash import keccak
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org","https://bsc-dataseed.binance.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR="0x09ada5a12293c30d75b97c56e34967e8a4326a3c"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def rpc(method,params):
    for u in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
            req=urllib.request.Request(u,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=20) as r: out=json.load(r)
            if "error" in out: continue
            return out["result"]
        except Exception: continue
    return None
def call(sig,args=""):
    v=rpc("eth_call",[{"to":ADDR,"data":sel(sig)+args},"latest"])
    if v is None or v=="0x": return None
    try: return int(v,16)
    except Exception: return v
def call_str(sig,args=""):
    v=rpc("eth_call",[{"to":ADDR,"data":sel(sig)+args},"latest"])
    return v
blk=rpc("eth_blockNumber",[])
out={"block":int(blk,16) if blk else None}
for sig in ["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","FREE_CAP()","MAX_SUPPLY()","mintOpen()","mintPrice()","mintStart()","START_TIME()","startTime()","paused()","totalPaidMints()","freePerWallet()","FREE_PER_WALLET()","maxFreePerWallet()"]:
    out[sig.split("(")[0]]=call(sig)
out["balanceOf_user"]=call("balanceOf(address)",enc(USER))
out["freeClaimed_user"]=call("freeClaimed(address)",enc(USER))
out["freeMintedBy_user"]=call("freeMintedBy(address)",enc(USER))
out["name"]=call_str("name()")
out["symbol"]=call_str("symbol()")
out["agentId"]=call_str("agentId()")
out["agentRegistry"]=call_str("agentRegistry()")
out["contractURI"]=call_str("contractURI()")
print(json.dumps(out,indent=1))
json.dump(out,open("run-2026-11-10-0101-zigzoo.json","w"),indent=1)
