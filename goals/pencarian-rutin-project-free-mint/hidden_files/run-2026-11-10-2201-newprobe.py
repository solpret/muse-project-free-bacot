#!/usr/bin/env python3
"""Run 2201 new-item probes: ORBITJANITOR (early?) + sale 0x6B39 (track-C shape?). Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_uint(n): return format(n,"064x")
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def call(addr,sig,args=""):
    data=sel(sig)+args
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]},timeout=25)
            res=r.get("result")
            if res not in (None,"0x"): return res
        except Exception: continue
    return None
def words(h):
    if h is None: return None
    b=bytes.fromhex(h[2:])
    return [int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
def wi(h):
    w=words(h); return w[0] if w and len(w)==1 else w
def addr_of(h):
    w=words(h)
    if not w: return None
    return "0x"+w[-1].to_bytes(32,'big')[-20:].hex()
def probe(addr, views):
    out={}
    for v in views:
        if v.endswith("(address)"): r=call(addr,v,enc(USER))
        elif v=="previewMint(address,uint256)": r=call(addr,v,enc(USER)+enc_uint(1))
        elif v=="remainingQuota(uint256)": r=call(addr,v,enc_uint(0))
        elif v=="remainingFor(address)": r=call(addr,v,enc(USER))
        else: r=call(addr,v)
        out[v]=words(r)
    return out
OJ="0x8d5a0555446d37afaba75e36da318646a4b32420"
SALE="0x6B39c561b187F8Bc2aA05323A5E74Fd60BE64d7b"
OJ_VIEWS=["name()","symbol()","totalSupply()","totalMinted()","freeMinted()","freeClaimed()","FREE_SUPPLY()","MAX_SUPPLY()","AGENT_FREE_CAP()","agentFreeUsed()","agentFreeByWallet(address)","mintOpen()","mintStart()","saleStart()","freeLeft()","balanceOf(address)","mintPrice()","PRICE()","owner()","agentRegistry()","REGISTRY()","registry()","contractURI()"]
SALE_VIEWS=["name()","symbol()","totalSupply()","token()","pair()","opened()","totalMinted()","totalRaised()","MAX_SHARES()","PRICE()","TOKENS_PER_SHARE()","BASE_QUOTA()","bonusQuota()","registry()","agentIdOf(address)","previewMint(address,uint256)","remainingQuota(uint256)","remainingFor(address)","mintOpen()","saleStart()"]
res={}
for label,addr,views in [("ORBITJANITOR",OJ,OJ_VIEWS),("SALE-6B39",SALE,SALE_VIEWS)]:
    t=time.time(); d=probe(addr,views); d["_secs"]=round(time.time()-t,1)
    res[label]=d
    print(label, json.dumps(d), flush=True)
json.dump(res, open("run-2026-11-10-2201-newprobe.json","w"), indent=1)
print("NEWPROBE DONE")
