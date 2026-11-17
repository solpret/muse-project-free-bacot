#!/usr/bin/env python3
"""Zephyra 0x00a9791b one-off verification, run 0931. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR="0x00a9791be6317d6e3a6c60f75a706c870d882048"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-rpc.publicnode.com/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def build(sig,args):
    d=sel(sig)
    for a in args:
        d+=enc_addr(a) if isinstance(a,str) and a.startswith("0x") and len(a)==42 else enc_u(int(a))
    return d
VIEWS=[("name","name()",[]),("symbol","symbol()",[]),("totalMinted","totalMinted()",[]),
("MAX_SUPPLY","MAX_SUPPLY()",[]),("MAX_PER_WALLET","MAX_PER_WALLET()",[]),
("mintOpen","mintOpen()",[]),("priceFor_user","priceFor(address)",[USER]),
("mintedBy_user","mintedBy(address)",[USER]),("hasAgentId_user","hasAgentId(address)",[USER]),
("balanceOf_user","balanceOf(address)",[USER]),
("DAWN_END","DAWN_END()",[]),("CLOUD_END","CLOUD_END()",[]),("STORM_END","STORM_END()",[]),
("NEXT_PRICE","NEXT_PRICE()",[]),("AGENT_ID_REGISTRY","AGENT_ID_REGISTRY()",[]),
("tokenURI_841","tokenURI(uint256)",[841]),("CREATOR","CREATOR()",[])]
calls=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":ADDR,"data":build(s,a)},"latest"]} for i,(k,s,a) in enumerate(VIEWS)]
out={}
for ep in EPS:
    try:
        r=subprocess.run(["curl","-sL","--max-time","120","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(calls)],capture_output=True,text=True,timeout=130)
        res=json.loads(r.stdout)
        if not isinstance(res,list) or len(res)!=len(calls): print("bad shape",ep,str(res)[:150]); continue
        for (k,s,a),it in zip(VIEWS,res):
            if not isinstance(it,dict) or "error" in it or it.get("result") in (None,"0x"): out[k]=None
            else:
                raw=it["result"]
                if k.startswith("tokenURI") or k=="AGENT_ID_REGISTRY":
                    out[k]=raw
                elif k in ("name","symbol"):
                    try:
                        hx=bytes.fromhex(raw[2:]); ln=int(hx[64:128].hex(),16); out[k]=hx[128:128+ln].decode(errors="ignore")
                    except Exception: out[k]=raw
                else: out[k]=to_int(raw[:66]) if len(raw)>=66 else raw
        print("OK via",ep); break
    except Exception as e: print("ep fail",ep,str(e)[:120])
# decode tokenURI if present
tu=out.get("tokenURI_841")
if isinstance(tu,str) and tu.startswith("0x"):
    try:
        hx=bytes.fromhex(tu[2:]); ln=int(hx[64:128].hex(),16); out["tokenURI_841_decoded"]=hx[128:128+ln].decode(errors="ignore")[:600]
    except Exception as e: out["tokenURI_841_decoded"]="decode-fail "+str(e)[:80]
# block number
blk=None
for ep in EPS:
    try:
        r=subprocess.run(["curl","-sL","--max-time","60","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})],capture_output=True,text=True,timeout=70)
        j=json.loads(r.stdout)
        if j.get("result"): blk=int(j["result"],16); break
    except Exception: continue
out["_block"]=blk
json.dump(out,open(BASE+"run-2026-11-14-0931-zephyra.json","w"),indent=1)
print(json.dumps(out,indent=1))
