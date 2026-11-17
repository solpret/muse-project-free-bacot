#!/usr/bin/env python3
"""Final probe for free-mint-search run 2026-11-13 22:31 WIB.
Ponke 0x0c222b11 (hot-leg S2, first seen 12 Nov 18:44) + PIXELPHARAOH 0xBb90Cc15
(Boltbook front page 23:25, 897/5555). Read-only; writes run-2026-11-13-2231-probe2.json."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
t0=time.time()
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def post_rpc(ep,payload,timeout=20):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def build_data(sig,args):
    d=sel(sig)
    for a in args:
        if isinstance(a,str) and a.startswith("0x") and len(a)==42: d+=enc_addr(a)
        else: d+=enc_u(int(a))
    return d
def raw_batch(addr,views):
    calls,keys=[],[]
    for i,(key,sig,args) in enumerate(views):
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":build_data(sig,args)},"latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res=post_rpc(ep,calls,timeout=20)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            out={}
            for it,key in zip(res,keys):
                if not isinstance(it,dict) or "error" in it or it.get("result") in (None,"0x"): out[key]=None
                else:
                    r=it["result"]; out[key]=to_int(r[:66]) if len(r)>=66 else r
            return out
        except Exception: continue
    return None
U=[USER]
ITEMS={
 "Ponke": ("0x0c222b11A380DF4F68ceE7CAcB162357E60c7215", [("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),("freeMinted","freeMinted()",[]),("FREE_SLOTS","FREE_SLOTS()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintStart","mintStart()",[]),("freeClaimed_user","freeClaimed(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "PIXELPHARAOH": ("0xBb90Cc15F7302Bbb7e114a5329d41dBb104F5350", [("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U)]),
}
reads={}
for name,(addr,views) in ITEMS.items():
    r=raw_batch(addr,views)
    reads[name]={"address":addr,"views":r}
    print(name,"OK" if r is not None else "FAIL",json.dumps(r)[:240],flush=True)
json.dump({"reads":reads,"elapsed_s":round(time.time()-t0,1)},open(BASE+"run-2026-11-13-2231-probe2.json","w"),indent=1)
print("DONE")
