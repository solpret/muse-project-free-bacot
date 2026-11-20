#!/usr/bin/env python3
"""Retry triage probe with chunked batches of 20 (same pattern as main re-read)."""
import json, subprocess
from eth_hash.auto import keccak
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPC="https://bsc-dataseed.binance.org/"
def sel(s): return keccak(s.encode())[:4].hex()
def enc(a): return "0"*24+a[2:].lower()
def encode(sig,arg=None):
    d="0x"+sel(sig)
    if arg=="user": d+=enc(USER)
    elif arg=="one": d+="%064x"%1
    elif arg=="user1": d+=enc(USER)+"%064x"%1
    return d
def curl_json(payload,timeout=25):
    r=subprocess.run(["curl","-s","-L","--max-time",str(timeout),RPC,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,timeout=timeout+5)
    return json.loads(r.stdout.decode())
def rpc_batch(calls,timeout=25):
    payload=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":t,"data":d},"latest"]} for i,(t,d) in enumerate(calls)]
    resp=curl_json(payload,timeout=timeout)
    if not isinstance(resp,list): raise IOError(f"non-list: {str(resp)[:200]}")
    by={it["id"]:it for it in resp if isinstance(it,dict)}
    res=[]
    for i in range(len(calls)):
        it=by.get(i+1,{})
        if "result" in it and it["result"] not in (None,"0x"):
            try: res.append(int(it["result"],16))
            except Exception: res.append(it["result"])
        elif "error" in it: res.append("err")
        else: res.append(None)
    return res
PLAN=[
 ("SHENLONG","0xd823a14507af2507a670fac4ed08316db7dca553",
  [("totalSupply","totalSupply()",None),("totalMinted","totalMinted()",None),("MAX_SUPPLY","MAX_SUPPLY()",None),
   ("FREE_MINTS","FREE_MINTS()",None),("freeMintsLeft","freeMintsLeft()",None),("mintOpen","mintOpen()",None),
   ("mintedCount_user","mintedCount(address)","user"),("balanceOf_user","balanceOf(address)","user"),
   ("mintPrice","mintPrice()",None),("MINT_PRICE","MINT_PRICE()",None),
   ("agentRegistry","agentRegistry()",None),("name","name()",None),("symbol","symbol()",None)]),
 ("ORE","0x4142045F58D319F133AC33BB7922Fb211595B67c",
  [("totalSupply","totalSupply()",None),("totalMinted","totalMinted()",None),("MAX_SUPPLY","MAX_SUPPLY()",None),
   ("FREE_SUPPLY","FREE_SUPPLY()",None),("freeMinted","freeMinted()",None),("freeClaimed","freeClaimed()",None),
   ("mintOpen","mintOpen()",None),("balanceOf_user","balanceOf(address)","user")]),
 ("ClafEye","0x1c759C4e075103b5B250DB5114B832b17B99C456",
  [("totalSupply","totalSupply()",None),("MAX_SUPPLY","MAX_SUPPLY()",None),("mintOpen","mintOpen()",None),
   ("balanceOf_user","balanceOf(address)","user"),("mintedBy_user","mintedBy(address)","user"),
   ("costFor_user_1","costFor(address,uint256)","user1")]),
]
calls,meta=[],[]
for name,addr,views in PLAN:
    for label,sig,arg in views:
        calls.append((addr,encode(sig,arg))); meta.append((name,addr,label))
res=[]
for i in range(0,len(calls),20):
    res+=rpc_batch(calls[i:i+20])
out={}
for (name,addr,label),val in zip(meta,res):
    if label in ("name","symbol") and isinstance(val,str):
        try:
            b=bytes.fromhex(val[2:]); ln=int.from_bytes(b[64:96],"big"); val=b[96:96+ln].decode(errors="replace")
        except Exception: pass
    out.setdefault(name,{"address":addr,"views":{}})[ "views"][label]=val
blk=curl_json([{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}])
out["block"]=int(blk[0]["result"],16)
print(json.dumps(out,indent=1))
json.dump(out,open(f"{HF}/run-2026-11-18-0901-triage3.json","w"),indent=1)
