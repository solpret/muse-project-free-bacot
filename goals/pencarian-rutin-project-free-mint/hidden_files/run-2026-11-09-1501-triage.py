#!/usr/bin/env python3
"""Triage run 1501 — on-chain verification of 3 discovery items (read-only, dataseed curl).
BMT (track A), 0x29666B (track C S1), BURN (track C). No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def to_int(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def batch(addr,views):
    calls=[];keys=[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        elif "(uint256)" in sig and sig.startswith(("quoteCost","quotaOf","freeClaimed","claimed","agentShares","pendingTokens","bonusShares")):
            continue
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    for ep in EPS:
        try:
            res=post(ep,calls)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {k:(None if (isinstance(it,dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,k in zip(res,keys)}
        except Exception: continue
    return None
def call1(addr,data,block="latest"):
    for ep in EPS:
        try:
            res=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},block]})
            if isinstance(res,dict) and "result" in res: return res["result"]
        except Exception: continue
    return None
def block():
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})
            return int(r["result"],16)
        except Exception: continue
    return None
def txt(addr,sig):
    r=call1(addr,sel(sig))
    if not r or r=="0x": return None
    try:
        b=bytes.fromhex(r[2:])
        off=int.from_bytes(b[32:64],"big"); ln=int.from_bytes(b[64:96],"big")
        return b[96:96+ln].decode(errors="replace")
    except Exception: return None
out={"block":block(),"triage":{}}
BMT="0x7d6e8528cc918afbd0ba5b0998c8a57860d2ded6"
out["triage"]["BMT"]={
 "name":txt(BMT,"name()"),"symbol":txt(BMT,"symbol()"),
 "views":batch(BMT,["totalSupply()","totalMinted()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","PRICE()","agentId()","freeClaimed(address)","publicMintedBy(address)","balanceOf(address)","PUBLIC_PER_WALLET()"]),
 "agentId_addr":None}
# agentId() returns address (20 bytes) - decode separately
r=call1(BMT,sel("agentId()"))
if r and len(r)>=66: out["triage"]["BMT"]["agentId_addr"]="0x"+r[-40:]
SALE="0x29666Bc0004824dc2B282c82aAC206b8b1711839"
sv=batch(SALE,["totalSupply()","FREE_SHARES()","soldShares()","TOTAL_SHARES()","TOKENS_PER_SHARE()","registry()","startTime()","saleEnd()","opened()","openedAt()","isSaleEnded()","pair()","pricePerShare()","balanceOf(address)","hasBought(address)","TOTAL_SUPPLY()","baseQuota()"])
out["triage"]["SALE-29666B"]={"name":txt(SALE,"name()"),"symbol":txt(SALE,"symbol()"),"views":sv}
r=call1(SALE,sel("registry()"))
if r and len(r)>=66: out["triage"]["SALE-29666B"]["registry_addr"]="0x"+r[-40:]
r=call1(SALE,sel("pair()"))
if r and len(r)>=66: out["triage"]["SALE-29666B"]["pair_addr"]="0x"+r[-40:]
# walletAgent(user) -> agent id (uint)
r=call1(SALE,sel("walletAgent(address)")+enc(USER))
out["triage"]["SALE-29666B"]["walletAgent_user"]=to_int(r)
BURN="0x7de1606230aa70802caecf1a3e90039a6265b1c4"
bv=batch(BURN,["totalSupply()","totalMinted()","FREE_SHARES()","freeMinted()","BASE_QUOTA()","OPEN_AT()","opened()","pair()","balanceOf(address)","MAX_SHARES()"])
out["triage"]["BURN"]={"name":txt(BURN,"name()"),"symbol":txt(BURN,"symbol()"),"views":bv}
r=call1(BURN,sel("pair()"))
if r and len(r)>=66: out["triage"]["BURN"]["pair_addr"]="0x"+r[-40:]
print(json.dumps(out,indent=1))
json.dump(out,open("run-2026-11-09-1501-triage.json","w"),indent=1)
