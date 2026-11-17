#!/usr/bin/env python3
"""MOODENG probe 2 — read-only extra views."""
import json, subprocess
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SALE="0xbb45668788a08ceceea6b1a0d0f25c1b667e1668"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def ti(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def batch(addr,views):
    calls=[];keys=[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig and "(uint256)" not in sig: data=sel(sig)+enc(USER); key=base+"_user"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    for ep in EPS:
        try:
            res=post(ep,calls)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {k:(None if isinstance(it,dict) and "error" in it else ti(it.get("result")) if isinstance(it,dict) else None) for it,k in zip(res,keys)}
        except Exception: continue
    return None
VIEWS=["agentRegistry()","registry()","pricePerShare()","tokensPerShare()","freeShares()","freeLeft()","freeRemaining()","freeSupply()","freePool()","owner()","saleToken()","tokenAddress()","isAgent(address)","hasAgent(address)","maxFreePerWallet()","FREE_SHARES()","TOTAL_SHARES()","TOKENS_PER_SHARE()","PRICE_PER_SHARE()","paidMinted()","totalMinted()","mintPrice()","cost(uint256)"]
print(json.dumps(batch(SALE,VIEWS),indent=1))
# raw code selectors present?
for ep in EPS:
    try:
        r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[SALE,"latest"]},timeout=25)
        code=(r.get("result") or "").lower()
        for s in ["e84f43b7","0d1cfcae","7b103999","94bf804d","61c0b6a0","9a5f5d31","8f79306e"]:
            print("selector", s, "in code:", s in code)
        break
    except Exception: continue
print("DONE")
