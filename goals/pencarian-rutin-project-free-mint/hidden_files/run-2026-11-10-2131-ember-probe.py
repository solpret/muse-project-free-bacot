#!/usr/bin/env python3
"""Run 2131 targeted probe: EMBERANVIL + NIGHTFORGE (SMITH template) - status/free views + contractURI + quote decode. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def call(addr,sig,args=""):
    data=sel(sig)+args
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]},timeout=25)
            res=r.get("result")
            if res is None or res=="0x": return None
            return res
        except Exception: continue
    return None
def ui(h):
    if h is None: return None
    try: return int(h,16)
    except Exception: return h
def tup(h):
    if h is None: return None
    try:
        b=bytes.fromhex(h[2:])
        return [int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
    except Exception: return h
def astr(h):
    if h is None: return None
    try:
        b=bytes.fromhex(h[2:])
        ln=int.from_bytes(b[32:64],"big")
        return b[64:64+ln].decode(errors="ignore")
    except Exception: return h
res={}
for label,addr in [("EMBERANVIL","0x7673c596a6702d32f844266dc2ca7b1fd6d7df21"),("NIGHTFORGE","0x22f43ba09fd4beb9417d4484c60370354b220186")]:
    d={}
    d["status_tuple"]=tup(call(addr,"status()"))
    d["totalSupply"]=ui(call(addr,"totalSupply()"))
    d["totalMinted"]=ui(call(addr,"totalMinted()"))
    d["freeMinted"]=ui(call(addr,"freeMinted()"))
    d["freeClaimed"]=ui(call(addr,"freeClaimed()"))
    d["FREE_SUPPLY"]=ui(call(addr,"FREE_SUPPLY()"))
    d["freeLeft"]=tup(call(addr,"freeLeft()"))
    d["mintOpen"]=ui(call(addr,"mintOpen()"))
    d["mintStart"]=ui(call(addr,"mintStart()"))
    d["owner"]="0x"+call(addr,"owner()")[-40:] if call(addr,"owner()") else None
    d["contractURI"]=astr(call(addr,"contractURI()"))
    d["balanceOf_user"]=ui(call(addr,"balanceOf(address)",enc(USER)))
    q=call(addr,"quote(address,uint256)",enc(USER)+format(1,"064x"))
    d["quote_raw"]=q
    if q:
        w=tup(q)
        d["quote"]={"freeUnits":w[0],"paidUnits":w[1],"valueWei":w[2],"ok":w[3]} if w and len(w)>=4 else None
    res[label]=d
    print(label, json.dumps(d), flush=True)
json.dump(res, open("run-2026-11-10-2131-ember-probe.json","w"), indent=1)
print("EMBER PROBE DONE")
