#!/usr/bin/env python3
"""VISION 0x5f76cab7... probe run 0101. Read-only."""
import json, urllib.request
from Crypto.Hash import keccak
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org","https://bsc-dataseed.binance.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR="0x5f76cab7b054e088563d5098e17bd0dc430e61ae"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return hex(n)[2:].rjust(64,"0")
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
blk=rpc("eth_blockNumber",[])
out={"block":int(blk,16) if blk else None}
for sig in ["MAX_SHARES()","TOTAL_SHARES()","totalShares()","totalFreeShares()","totalPaidShares()","totalSupply()","TOKENS_PER_SHARE()","LIQ_TOKENS_PER_SHARE()","PRICE()","BASE_QUOTA()","MAX_PER_TX()","totalRaised()"]:
    out[sig.split("(")[0]]=call(sig)
out["agentIdRegistry"]=rpc("eth_call",[{"to":ADDR,"data":sel("agentIdRegistry()")},"latest"])
out["isAgent_user"]=call("isAgent(address)",enc(USER))
out["freeUsed_user"]=call("freeUsed(address)",enc(USER))
out["sharesOf_user"]=call("sharesOf(address)",enc(USER))
out["quotaOf_user"]=call("quotaOf(address)",enc(USER))
out["balanceOf_user"]=call("balanceOf(address)",enc(USER))
# quote(user,1): quote(address,uint256) guess; also try quote(uint256)
q=rpc("eth_call",[{"to":ADDR,"data":sel("quote(address,uint256)")+enc(USER)+enc_u(1)},"latest"])
out["quote_user_1_raw"]=q
try: out["quote_user_1"]=int(q,16) if q else None
except Exception: out["quote_user_1"]=q
print(json.dumps(out,indent=1))
json.dump(out,open("run-2026-11-10-0101-vision.json","w"),indent=1)
