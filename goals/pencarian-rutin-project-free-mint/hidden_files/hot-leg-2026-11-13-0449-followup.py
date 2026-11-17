#!/usr/bin/env python3
"""Hot-leg 0449 follow-up: leg3 verify 0x5306 (S1=True found via retry-404 AFTER leg3_targets built - retry_404 results are not fed into leg3_targets; verify it now so it is not lost)."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
A="0x530695a8e3eb9a1253cafc9239811f4ca88791f9"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def _post_one(ep,payload,timeout=12):
    r=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5)
    return json.loads(r.stdout)
def post_rpc_race(payload,timeout=12):
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs={ex.submit(_post_one,ep,payload,timeout):ep for ep in EPS}
        for fut in as_completed(futs):
            try:
                res=fut.result()
                if isinstance(res,list) and len(res)==len(payload): return res
            except Exception: continue
    return None
def raw_batch(addr,views):
    calls,keys=[],[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    res=post_rpc_race(calls,timeout=12)
    if res is None: return None
    return {key:(None if (isinstance(it,dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,key in zip(res,keys)}
def chunked(addr,views,chunk=8):
    m={}
    for i in range(0,len(views),chunk):
        c=raw_batch(addr,views[i:i+chunk])
        if c: m.update(c)
    return m if m else None
VIEWS=["name()","symbol()","totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","FREE_CAP()","FREE_SHARES()","MAX_SUPPLY()","mintOpen()","balanceOf(address)","freeClaimed(address)","freeUsed(address)","mintedBy(address)","mintStart()","freeLeft()","freeAvailable(address)","saleStart()","saleEnd()","PRICE()","price()","launched()","freeSharesLeft()","freeSharesRemaining()","freeClaimedByWallet(address)","currentState()","finalized()","refunding()","totalFreeMinted()","openedAt()","token()","saleToken()","agentRegistry()","freePerWallet()","freeFor(address)"]
out={"address":A,"run":"hot-leg-2026-11-13-0449-followup"}
r=None
for att in range(3):
    r=chunked(A,VIEWS)
    if r and any(v is not None for v in r.values()): break
    time.sleep(2)
out["views"]=r
out["summary"]={k:v for k,v in r.items() if v is not None} if r else None
# quote(user,1)
data=sel("quote(address,uint256)")+enc(USER)+format(1,"064x")
res=post_rpc_race([{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":A,"data":data},"latest"]}],timeout=12)
out["quote_raw"]=res
if isinstance(res,list) and res and isinstance(res[0],dict) and res[0].get("result"):
    try:
        b=bytes.fromhex(res[0]["result"][2:])
        words=[int.from_bytes(b[i:i+32],"big") for i in range(0,min(len(b),160),32)]
        tail=None
        if len(words)>=5 and words[4]<len(b):
            off=words[4]; ln=int.from_bytes(b[off:off+32],"big")
            tail=b[off+32:off+32+ln].decode(errors="replace")
        out["quote_user_1"]={"words":words,"tail_string":tail}
    except Exception as e: out["quote_user_1"]={"decode_error":str(e)[:100]}
# token name/symbol raw decode
for fn in ("name()","symbol()"):
    d=sel(fn)
    res=post_rpc_race([{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":A,"data":d},"latest"]}],timeout=12)
    if isinstance(res,list) and res and isinstance(res[0],dict) and res[0].get("result"):
        hx=res[0]["result"][2:]
        try:
            b=bytes.fromhex(hx)
            if len(b)>=64:
                off=int.from_bytes(b[:32],"big"); ln=int.from_bytes(b[off:off+32],"big")
                out[fn[:-2]+"_str"]=b[off+32:off+32+ln].decode(errors="replace")
        except Exception: pass
# contractURI for gate pointer
d=sel("contractURI()")
res=post_rpc_race([{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":A,"data":d},"latest"]}],timeout=12)
out["contractURI_raw"]=res[0].get("result") if isinstance(res,list) and res and isinstance(res[0],dict) else res
json.dump(out,open(BASE+"hot-leg-2026-11-13-0449-followup.json","w"),indent=1)
print(json.dumps(out,indent=1))
