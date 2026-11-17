#!/usr/bin/env python3
"""Agent Muse slot probe run 0601. Proper ABI decode for tuple returns."""
import json, subprocess
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
C = "0x779fa133848d23052B7345F63B3b2E5309cd13ed"
EPS = ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
VIEWS=[("freeClaimed","freeClaimed()"),("FREE_SHARES","FREE_SHARES()"),("bookedTotal","bookedTotal()"),
 ("openedAt","openedAt()"),("DOORS_OPEN","DOORS_OPEN()"),("OSK_PER_SHARE","OSK_PER_SHARE()"),
 ("SHARE_PRICE","SHARE_PRICE()"),("FREE_OSK","FREE_OSK()"),("afterSold","afterSold()"),("paidSold","paidSold()"),
 ("bookedOf_user","bookedOf(address)",enc_addr(USER)),
 ("canBook_user","canBook(address)",enc_addr(USER)),
 ("agentIdOf_user","agentIdOf(address)",enc_addr(USER)),
 ("progress","progress()")]
calls=[]
for i,(key,sig,*rest) in enumerate(VIEWS):
    calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":C,"data":sel(sig)+(rest[0] if rest else "")},"latest"]})
def words(hexv):
    b=bytes.fromhex(hexv[2:]) if hexv.startswith("0x") else b""
    return [int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
out={"contract":C,"reads":{}}
for ep in EPS:
    try:
        res=post(ep,calls)
        if not isinstance(res,list) or len(res)!=len(calls): continue
        for it,(key,sig,*rest) in zip(res,VIEWS):
            if not isinstance(it,dict) or "error" in it or not it.get("result") or it["result"]=="0x":
                out["reads"][key]=None; continue
            w=words(it["result"])
            out["reads"][key]=w
        out["endpoint"]=ep; break
    except Exception as e:
        out.setdefault("errors",[]).append(str(e)[:100])
try:
    r=post(EPS[0],{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=15)
    out["block"]=int(r.get("result"),16)
except Exception as e:
    out["block_error"]=str(e)[:100]
print(json.dumps(out,indent=1))
json.dump(out,open("run-2026-11-13-0601-agentmuse.json","w"),indent=1)
