#!/usr/bin/env python3
"""Verify Boltbook-new leads run 2131: Nova Agent + Aero Agents A2. Read-only."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP="https://bsc-dataseed.binance.org/"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def data(sig,args):
    d=sel(sig)
    for a in args:
        if isinstance(a,str) and a.startswith("0x") and len(a)==42: d+=enc_addr(a)
        elif isinstance(a,str) and a.startswith("0x"): d+=enc_u(int(a,16))
        else: d+=enc_u(int(a))
    return d
def batch(addr, views):
    calls=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data(sig,args)},"latest"]} for i,(k,sig,args) in enumerate(views)]
    out=subprocess.run(["curl","-sL","--max-time","120","-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps(calls)],capture_output=True,text=True,timeout=130).stdout
    res=json.loads(out)
    def ti(v):
        try: return int(v,16) if v and v!="0x" else None
        except Exception: return None
    outd={}
    for (k,sig,args),r in zip(views,res):
        v=r.get("result")
        if v is None or v=="0x": outd[k]=None; continue
        if k in ("name","symbol"):
            try:
                raw=bytes.fromhex(v[2:])
                # string: offset 64, len, data
                ln=int.from_bytes(raw[64:96],'big')
                outd[k]=raw[96:96+ln].decode(errors='replace')
            except Exception: outd[k]="decode-fail"
        else: outd[k]=ti(v)
    return outd
def sourcify(addr):
    try:
        with urllib.request.urlopen(f"https://sourcify.dev/server/v2/contract/56/{addr}", timeout=45) as r:
            d=json.load(r)
        m=d.get("match") or d.get("stdJson") and {}
        return {"status": d.get("match") or d.get("status"), "verifiedAt": (d.get("match") or {}).get("verifiedAt")}
    except Exception as e:
        return {"status": f"err:{str(e)[:60]}"}
U=[USER]
COMMON=[("name","name()",[]),("symbol","symbol()",[]),("totalSupply","totalSupply()",[]),
 ("totalMinted","totalMinted()",[]),("freeMinted","freeMinted()",[]),("freeClaimed","freeClaimed()",[]),
 ("FREE_SUPPLY","FREE_SUPPLY()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
 ("PRE_MINT","PRE_MINT()",[]),("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U),
 ("hasAgentId_user","hasAgentId(address)",U),("paused","paused()",[])]
result={}
for label,addr in [("NovaAgent","0xe471c0e3e61837d3aa4b19bc6c2ac402f91e9b6f"),
                   ("AeroA2","0xe0a32f2658fe46eff4755fdc4c8c67933e847c93")]:
    # eth_getCode first
    code=subprocess.run(["curl","-sL","--max-time","30","-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]})],capture_output=True,text=True,timeout=40).stdout
    c=json.loads(code).get("result","")
    result[label]={"address":addr,"code_len":len(c),"sourcify":sourcify(addr)}
    if len(c)>10:
        result[label]["views"]=batch(addr,COMMON)
        # quote(user,1) + mintPriceFor if present
        result[label]["views"].update(batch(addr,[("quote_user_1","quote(address,uint256)",[USER,1]),("cost_user_1","cost(address,uint256)",[USER,1]),("mintPriceFor_user_1","mintPriceFor(address,uint256)",[USER,1]),("canMint_user","canMint(address)",U),("freeLeft","freeLeft()",[]),("freeSupply","freeSupply()",[])]))
    print(label, json.dumps(result[label])[:1200], flush=True)
json.dump(result, open(BASE+"run-2026-11-16-2131-verify-nova-aero.json","w"), indent=1)
print("DONE")
