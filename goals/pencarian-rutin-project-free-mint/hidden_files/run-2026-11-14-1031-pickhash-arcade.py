#!/usr/bin/env python3
"""Deep check Pickhash + ARCADEWARDEN (run 1031): registry bytes in code,
AGENT_ID() value, basic views. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
REG="60b9262456de011f7d15a54cdd8c48baa8b022f"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-rpc.publicnode.com/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def rpc(ep,payload,timeout=60):
    o=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+10).stdout
    return json.loads(o)
def call(addr,data):
    p={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}
    for ep in EPS:
        try:
            r=rpc(ep,p)
            if isinstance(r,dict) and isinstance(r.get("result"),str) and r["result"] not in (None,"0x"): return r["result"]
        except Exception: continue
    return None
def code(addr):
    p={"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]}
    for ep in EPS:
        try:
            r=rpc(ep,p)
            if isinstance(r,dict) and isinstance(r.get("result"),str): return r["result"]
        except Exception: continue
    return None
def ti(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
out={}
for name,addr in [("Pickhash","0x2296367f74b2ec266cf4667d98501ae7110f5a58"),
                  ("ARCADEWARDEN","0xdb7257dbf18ca1539159c64534ffd68ef14c2f32")]:
    c=code(addr)
    aid=call(addr,sel("AGENT_ID()"))
    res={"code_len":len(c)-2 if c else None,"registry_bytes_in_code":(REG in c.lower()) if c else None,
         "AGENT_ID_value":("0x"+aid[-40:]) if aid and len(aid)>=66 else None,
         "name":call(addr,sel("name()")),"symbol":call(addr,sel("symbol()")),
         "totalSupply":ti(call(addr,sel("totalSupply()"))),
         "totalMinted":ti(call(addr,sel("totalMinted()"))),
         "mintOpen":ti(call(addr,sel("mintOpen()"))),
         "freeClaimed":ti(call(addr,sel("freeClaimed()"))),
         "freeMinted":ti(call(addr,sel("freeMinted()"))),
         "freeLeft":ti(call(addr,sel("freeLeft()"))),
         "MAX_SUPPLY":ti(call(addr,sel("MAX_SUPPLY()")))}
    out[name]=res
    print(name, json.dumps(res), flush=True)
json.dump(out,open("run-2026-11-14-1031-pickhash-arcade.json","w"),indent=1)
