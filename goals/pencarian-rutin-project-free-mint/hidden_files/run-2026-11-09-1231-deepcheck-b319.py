#!/usr/bin/env python3
"""Deep-check run 1231 first-seen 0xB31947A80AC2e72390B84e3d503d9148f4A9d1ca (11 mints/11 minters). Read-only."""
import json, subprocess, datetime
from Crypto.Hash import keccak
ADDR="0xB31947A80AC2e72390B84e3d503d9148f4A9d1ca"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
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
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    for ep in EPS:
        try:
            res=post(ep,calls)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {k:(None if (isinstance(it,dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,k in zip(res,keys)}
        except Exception: continue
    return None
def call_str(addr,sig):
    for ep in EPS:
        try:
            res=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":sel(sig)},"latest"]})
            r=res.get("result")
            if isinstance(r,str) and len(r)>130:
                ln=int(r[66:130],16); raw=bytes.fromhex(r[130:130+ln*2])
                return raw.decode(errors="replace")
        except Exception: continue
    return None
def block_ts(blk):
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(blk),False]})
            ts=r.get("result",{}).get("timestamp")
            if ts:
                dt=datetime.datetime.fromtimestamp(int(ts,16),datetime.timezone(datetime.timedelta(hours=7)))
                return dt.strftime("%Y-%m-%d %H:%M:%S WIB")
        except Exception: continue
    return None
views=["totalSupply()","totalMinted()","freeMinted()","freeClaimed()","FREE_SUPPLY()","FREE_CAP()","MAX_SUPPLY()","mintOpen()","freeLeft()","freeSupply()","balanceOf(address)","freeClaimed(address)","mintedBy(address)","freeCount(address)"]
out={"address":ADDR}
out["views"]=batch(ADDR,views)
out["name"]=call_str(ADDR,"name()")
out["symbol"]=call_str(ADDR,"symbol()")
out["contractURI"]=call_str(ADDR,"contractURI()")
out["owner"]=batch(ADDR,["owner()"])
out["first_block"]=132531650
out["first_mint_wib"]=block_ts(132531650)
try:
    s=subprocess.run(["curl","-sL","--max-time","20","https://sourcify.dev/server/v2/contract/56/"+ADDR+"?fields=abi"],capture_output=True,text=True,timeout=25).stdout
    d=json.loads(s); abi=d.get("abi") or []
    out["sourcify_match"]=d.get("match")
    out["sourcify_fns"]=sorted({e.get("name") for e in abi if isinstance(e,dict) and e.get("type")=="function"})
except Exception as e:
    out["sourcify_match"]=f"error:{type(e).__name__}"
    out["sourcify_fns"]=[]
json.dump(out,open("run-2026-11-09-1231-deepcheck-b319.json","w"),indent=1)
print(json.dumps(out,indent=1))
