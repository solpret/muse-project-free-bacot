#!/usr/bin/env python3
"""Probe run 0831: SOLDERCATS strong-lead legs + 3 new feed early-shape contracts. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def dec_str(v):
    try:
        if not v or v=="0x": return None
        b=bytes.fromhex(v[2:])
        ln=int.from_bytes(b[64:96],"big")
        return b[96:96+ln].decode(errors="replace")
    except Exception: return None
def dec_addr(v):
    try:
        if not v or v=="0x": return None
        return "0x"+v[-40:]
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def batch(addr, views):
    calls=[]; keys=[]
    for i,(sig,arg) in enumerate(views):
        data=sel(sig)+(enc(arg) if arg else "")
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        keys.append(sig.split("(")[0])
    for ep in EPS:
        try:
            r=post(ep,calls,timeout=25)
            if isinstance(r,list) and len(r)==len(calls):
                return {k:(it.get("result") if isinstance(it,dict) and "error" not in it else None) for k,it in zip(keys,r)}
        except Exception: continue
    return {k:None for k in keys}
def block():
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=25)
            return int(r["result"],16)
        except Exception: continue
    return None
out={"block":block(),"started_wib":"2026-11-11 08:31 WIB"}
# SOLDERCATS
sc="0x3D972EBbF7488f21b95250B867e2406c723C9DDC"
v=batch(sc,[("agentFreeUsed()",None),("paidMinted()",None),("agentFreeByWallet(address)",USER),("balanceOf(address)",USER),("freeLeft()",None),("mintStart()",None),("mintEnd()",None),("mintOpen()",None),("name()",None),("symbol()",None),("totalSupply()",None),("REGISTRY()",None)])
out["SOLDERCATS"]={"address":sc,
  "agentFreeUsed":to_int(v["agentFreeUsed"]),"paidMinted":to_int(v["paidMinted"]),
  "agentFreeByWallet_user":to_int(v["agentFreeByWallet"]),"balanceOf_user":to_int(v["balanceOf"]),
  "freeLeft":to_int(v["freeLeft"]),"mintStart":to_int(v["mintStart"]),"mintEnd":to_int(v["mintEnd"]),
  "mintOpen":to_int(v["mintOpen"]),"name":dec_str(v["name"]),"symbol":dec_str(v["symbol"]),
  "totalSupply":to_int(v["totalSupply"]),"REGISTRY":dec_addr(v["REGISTRY"])}
print("SOLDERCATS",json.dumps(out["SOLDERCATS"]),flush=True)
# FEED-4676
f1="0x467696af8c2206B977B24081445104632dc1D459"
v=batch(f1,[("name()",None),("symbol()",None),("totalMinted()",None),("freeAvailable()",None),("freeMinted()",None),("FREE_SUPPLY()",None),("MAX_SUPPLY()",None),("mintStart()",None),("mintEnd()",None),("mintOpen()",None),("REGISTRY()",None),("balanceOf(address)",USER)])
out["FEED-4676"]={"address":f1,"name":dec_str(v["name"]),"symbol":dec_str(v["symbol"]),
  "totalMinted":to_int(v["totalMinted"]),"freeAvailable":to_int(v["freeAvailable"]),
  "freeMinted":to_int(v["freeMinted"]),"FREE_SUPPLY":to_int(v["FREE_SUPPLY"]),
  "MAX_SUPPLY":to_int(v["MAX_SUPPLY"]),"mintStart":to_int(v["mintStart"]),"mintEnd":to_int(v["mintEnd"]),
  "mintOpen":to_int(v["mintOpen"]),"REGISTRY":dec_addr(v["REGISTRY"]),"balanceOf_user":to_int(v["balanceOf"])}
print("FEED-4676",json.dumps(out["FEED-4676"]),flush=True)
# FEED-08E3 / FEED-0BF3 (23-fn claimFreeShare template)
for key,addr in [("FEED-08E3","0x08E3e40829718913fb627c818Cb334B1E3d5B699"),("FEED-0BF3","0x0BF38aFe23070C79f693DBDA4ce1866Ff11C4bF7")]:
    v=batch(addr,[("name()",None),("symbol()",None),("totalMinted()",None),("MAX_SHARES()",None),("registry()",None),("agentIdRequired()",None),("mintStart()",None),("mintEnd()",None),("hasClaimed(address)",USER),("balanceOf(address)",USER)])
    out[key]={"address":addr,"name":dec_str(v["name"]),"symbol":dec_str(v["symbol"]),
      "totalMinted":to_int(v["totalMinted"]),"MAX_SHARES":to_int(v["MAX_SHARES"]),
      "registry":dec_addr(v["registry"]),"agentIdRequired":to_int(v["agentIdRequired"]),
      "mintStart":to_int(v["mintStart"]),"mintEnd":to_int(v["mintEnd"]),
      "hasClaimed_user":to_int(v["hasClaimed"]),"balanceOf_user":to_int(v["balanceOf"])}
    print(key,json.dumps(out[key]),flush=True)
json.dump(out,open("run-2026-11-11-0831-probe.json","w"),indent=1)
print("PROBE DONE block",out["block"],flush=True)
