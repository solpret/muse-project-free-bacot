#!/usr/bin/env python3
"""Run 0701 FCAT verify: on-chain reads + owner vs discards + Sourcify ABI. Read-only."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
FCAT="0x349d8fbed5de52a4e5065e143797d7b92846be0e"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def toint(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def batch(addr, views):
    calls=[]; keys=[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        elif "(uint256)" in sig: data=sel(sig)+"0"*63+"1"; key=base+"_1"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    for ep in EPS:
        try:
            res=post(ep,calls)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {k:(None if (isinstance(it,dict) and "error" in it) else (toint(it.get("result")) if isinstance(it,dict) else None)) for it,k in zip(res,keys)}
        except Exception: continue
    return None
def call_raw(addr, data):
    for ep in EPS:
        try:
            res=post(ep,[{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}])
            v=res[0].get("result") if isinstance(res,list) else None
            return v
        except Exception: continue
    return None
out={"block":None}
for ep in EPS:
    try:
        r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})
        out["block"]=int(r["result"],16); break
    except Exception: continue
out["fcat"]=batch(FCAT,["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","freeClaimed(address)","balanceOf(address)","mintPrice()","MAX_PER_WALLET()","owner()","name()","symbol()"])
# string views: name/symbol raw decode
def dec_str(hexv):
    try:
        b=bytes.fromhex(hexv[2:])
        off=int.from_bytes(b[32:64],"big"); ln=int.from_bytes(b[64:96],"big")
        return b[96:96+ln].decode(errors="ignore")
    except Exception: return None
for fn in ("name()","symbol()","contractURI()","baseURI()"):
    v=call_raw(FCAT, sel(fn))
    out["fcat_"+fn.split("(")[0]]=dec_str(v) if v and len(v)>130 else v
out["fcat_tokenURI_1"]=call_raw(FCAT, sel("tokenURI(uint256)")+"0"*63+"1")
# owner vs discards
owner_int=out["fcat"].get("owner")
disc=json.load(open("same-owner-discards.json")) if __import__("os").path.exists("same-owner-discards.json") else {}
out["discards_file_keys"]=len(disc) if isinstance(disc,dict) else disc
owner_hex=None
if owner_int is not None:
    owner_hex="0x"+format(owner_int,"040x")
out["owner_hex"]=owner_hex
if isinstance(disc,dict):
    out["owner_in_discards"]= owner_hex.lower() in {str(k).lower() for k in disc.keys()} if owner_hex else None
    # also check values
    if owner_hex:
        hit=[k for k,v in disc.items() if owner_hex.lower() in str(v).lower() or owner_hex.lower()==str(k).lower()]
        out["owner_discard_hits"]=hit
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-10-0701-fcat-verify.json","w"), indent=1)
