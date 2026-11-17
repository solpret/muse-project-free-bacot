#!/usr/bin/env python3
"""WOJAK sale probe run 0231 — read-only. S1+S2 shape check."""
import json, subprocess, datetime
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SALE="0x70ab28d6d1569d35b6dcb58d0b2da0363303c9f5"
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
        elif "(address,uint256)" in sig: data=sel(sig)+enc(USER)+format(1,'064x'); key=base+"_user_1"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    for ep in EPS:
        try:
            res=post(ep,calls)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {k:(None if isinstance(it,dict) and "error" in it else ti(it.get("result")) if isinstance(it,dict) else None) for it,k in zip(res,keys)}
        except Exception: continue
    return None
VIEWS=["freeMinted()","FREE_SLOTS()","FREE_SUPPLY()","FREE_AMOUNT()","freeClaimed(address)","mintedBy(address)","agentRegistry()","agentId()","totalSupply()","decimals()","startTime()","deadline()","FREE_SHARES()","TOTAL_SHARES()","TOKENS_PER_SHARE()","PRICE_PER_SHARE()","ESCROW_BPS()","REFERRAL_BPS()","totalMinted()","sharesMinted()","quote(address,uint256)","freeAvailable(address)","mintingOpen()","token()"]
out=batch(SALE,VIEWS)
print(json.dumps(out,indent=1))
for ep in EPS:
    try:
        r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[SALE,"latest"]},timeout=25)
        code=(r.get("result") or "").lower()
        print("code len:", len(code), "registry-bytes:", "60b9262456de011f7d15a54cdd8c48baa8b022f" in code)
        break
    except Exception: continue
for ep in EPS:
    try:
        r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(132820917),False]},timeout=25)
        ts=int(r["result"]["timestamp"],16)
        print("mint block ts:", datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB"))
        break
    except Exception: continue
json.dump({"sale_views":out}, open("wojak-0231-probe.json","w"), indent=1)
print("DONE")
