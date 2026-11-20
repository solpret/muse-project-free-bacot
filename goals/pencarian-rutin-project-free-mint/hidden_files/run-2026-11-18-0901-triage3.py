#!/usr/bin/env python3
"""Triage SHENLONG (new) + ORE + ClafEye (live re-read) run 0901. Read-only."""
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
def post(payload,timeout=25):
    r=subprocess.run(["curl","-s","-L","--max-time",str(timeout),RPC,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,timeout=timeout+5)
    return json.loads(r.stdout.decode())
PLAN=[
 ("SHENLONG","0xd823a14507af2507a670fac4ed08316db7dca553",
  ["totalSupply()","totalMinted()","MAX_SUPPLY()","FREE_SUPPLY()","freeMinted()","freeClaimed()","freeLeft()","freeRemaining()","freeMintsLeft()","mintOpen()","mintedBy(address)","balanceOf(address)","cost(address,uint256)","quote(address,uint256)","freeMintedByWallet(address)","agentRegistry()","name()","symbol()"]),
 ("ORE","0x4142045F58D319F133AC33BB7922Fb211595B67c",
  ["totalSupply()","totalMinted()","MAX_SUPPLY()","FREE_SUPPLY()","freeMinted()","freeClaimed()","mintOpen()","balanceOf(address)","agentRegistry()"]),
 ("ClafEye","0x1c759C4e075103b5B250DB5114B832b17B99C456",
  ["totalSupply()","MAX_SUPPLY()","mintOpen()","balanceOf(address)","mintedBy(address)","costFor(address,uint256)"]),
]
calls,meta=[],[]
for name,addr,sigs in PLAN:
    for sig in sigs:
        arg="user" if "(address)" in sig and sig not in ("agentRegistry()",) else None
        if sig=="cost(address,uint256)": arg="user1"
        if sig=="quote(address,uint256)": arg="user1"
        if sig=="costFor(address,uint256)": arg="user1"
        calls.append((addr,encode(sig,arg))); meta.append((name,addr,sig))
payload=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":t,"data":d},"latest"]} for i,(t,d) in enumerate(calls)]
resp=post(payload)
by={it["id"]:it for it in resp if isinstance(it,dict)}
out={}
for i,(name,addr,sig) in enumerate(meta):
    it=by.get(i+1,{})
    if "result" in it and it["result"] not in (None,"0x"):
        v=it["result"]
        if sig in ("name()","symbol()"):
            try:
                b=bytes.fromhex(v[2:]); ln=int.from_bytes(b[64:96],"big"); val=b[96:96+ln].decode(errors="replace")
            except Exception: val=v
        else:
            try: val=int(v,16)
            except Exception: val=v
    elif "error" in it: val="err"
    else: val=None
    out.setdefault(name,{"address":addr,"views":{}})[ "views"][sig]=val
blk=post([{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}])
out["block"]=int(blk[0]["result"],16)
print(json.dumps(out,indent=1))
# Sourcify ABI for SHENLONG
try:
    r=subprocess.run(["curl","-s","-L","--max-time","25","https://sourcify.dev/server/v2/contract/56/0xd823a14507af2507a670fac4ed08316db7dca553?fields=abi"],capture_output=True,timeout=30)
    m=json.loads(r.stdout.decode())
    abi=m.get("abi",[])
    fns=sorted({e["name"] for e in abi if e.get("type")=="function"})
    print("SHENLONG sourcify verifiedAt:",m.get("verifiedAt"),"match:",m.get("match"),"n_fns:",len(fns))
    print("SHENLONG FNS:",fns)
    out["shenlong_sourcify"]={"verifiedAt":m.get("verifiedAt"),"match":m.get("match"),"fns":fns}
except Exception as e:
    print("SHENLONG sourcify FAIL:",e)
    out["shenlong_sourcify"]={"error":str(e)[:150]}
# registry bytes for SHENLONG
code=post([{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":["0xd823a14507af2507a670fac4ed08316db7dca553","latest"]}])[0].get("result","")
print("SHENLONG codelen:",len(code),"registry-bytes:","60b9262456de011f7d15a54cdd8c48baa8b022f" in code.lower())
out["shenlong_codelen"]=len(code)
json.dump(out,open(f"{HF}/run-2026-11-18-0901-triage3.json","w"),indent=1)
