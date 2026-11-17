#!/usr/bin/env python3
"""Verify new S1 contract 0x61F35C9E... (feed 1319) — leg 3 fast on-chain check."""
import json, subprocess, time
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR="0x61F35C9E546ED5CC4989Ff29740bc8F9E6d963Be"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0=time.time()
def curl(url, timeout=12):
    try:
        r=subprocess.run(["curl","-s","-m",str(timeout),"-A","Mozilla/5.0",url],capture_output=True,timeout=timeout+5)
        return r.stdout
    except Exception: return b""
def curl_json(url, timeout=12):
    try: return json.loads(curl(url,timeout).decode(errors="replace"))
    except Exception: return None
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def post_rpc(ep,payload,timeout=15):
    outb=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(outb)
def batch(addr, views):
    calls,keys=[],[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        elif "(uint256)" in sig: data=sel(sig)+"0"*64; key=base+"_0"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    for ep in EPS:
        try:
            res=post_rpc(ep,calls,timeout=15)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {key:(None if (isinstance(it,dict) and "error" in it) else (it.get("result") if isinstance(it,dict) else None)) for it,key in zip(res,keys)}
        except Exception: continue
    return None
abi_j=curl_json(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi",12)
abi=None
if isinstance(abi_j,dict): abi=abi_j.get("abi") or (abi_j.get("stdJson") or {}).get("abi")
out={"addr":ADDR,"verifiedAt_feed":None}
if abi:
    fns=[(f.get("name"),",".join((i.get("type") or "") for i in f.get("inputs",[]))) for f in abi if isinstance(f,dict) and f.get("type")=="function"]
    out["fns"]=fns
    out["n_fns"]=len(fns)
    names=[n for n,_ in fns]
    out["name_guess"]=[n for n in names if "name" in n.lower() or "symbol" in n.lower()]
    # string reads
    def read_str(sig):
        r=batch(ADDR,[sig])
        if not r: return None
        raw=r.get(sig.split("(")[0])
        if not raw or raw=="0x": return None
        try:
            b=bytes.fromhex(raw[2:])
            ln=int.from_bytes(b[64:96],"big")
            return b[96:96+ln].decode(errors="replace")
        except Exception: return None
    out["name"]=read_str("name()")
    out["symbol"]=read_str("symbol()")
    # numeric views: try every no-arg uint view plausibly relevant + address views
    views=["totalSupply()","totalMinted()","freeSupply()","freeMinted()","freeRemaining()","free_start_id()","max_free_per_wallet()","FREE_SUPPLY()","FREE_SHARES()","mintStart()","saleStart()","mintOpen()","launched()","currentState()","finalized()","refunding()","freeMintedBy(address)","freeClaimed(address)","balanceOf(address)","mintedBy(address)"]
    raw=batch(ADDR,views)
    vals={}
    if raw:
        for k,v in raw.items():
            vals[k]=to_int(v)
    out["views"]=vals
    # quote(user,1): find quote-like fn
    qnames=[n for n,_ in fns if "quote" in n.lower()]
    out["quote_fns"]=qnames
    for qn in qnames:
        sigs=[f"{qn}({ins})" for nm,ins in fns if nm==qn]
        for sig in sigs:
            if sig.count(",")==1 and "address" in sig:
                data=sel(sig)+enc(USER)+"0"*63+"1"
                for ep in EPS:
                    try:
                        res=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":ADDR,"data":data},"latest"]},timeout=15)
                        out["quote_user_1_raw"]=res.get("result")
                        out["quote_user_1_words"]=[to_int("0x"+res["result"][2+i*64:2+(i+1)*64]) for i in range((len(res["result"])-2)//64)] if res.get("result") else None
                        break
                    except Exception: continue
                break
    # mint function signatures
    out["mint_fns"]=[f"{n}({ins})" for n,ins in fns if "mint" in n.lower()]
else:
    out["abi_error"]="unfetchable"
now=datetime.now(timezone(timedelta(hours=7)))
out["checked_wib"]=now.strftime("%Y-%m-%dT%H:%M:%S+07:00")
out["elapsed_s"]=round(time.time()-T0,1)
json.dump(out,open(BASE+"hot-leg-2026-11-12-1319-verify-61f3.json","w"),indent=1)
print(json.dumps(out,indent=1))
