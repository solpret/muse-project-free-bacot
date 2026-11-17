#!/usr/bin/env python3
"""Probe2: bead62 freeAvailable(user)/freeUsed(user)/tokenURI(1); ORYN freeRound(1) via ABI types."""
import json, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def call(addr,data):
    for ep in EPS:
        try:
            res=post(ep,[{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}],timeout=25)
            if isinstance(res,list) and res and isinstance(res[0],dict) and "result" in res[0]:
                return res[0]["result"]
        except Exception: continue
    return None
def dec_str(r):
    try:
        b=bytes.fromhex(r[2:])
        ln=int.from_bytes(b[64:96],"big")
        return b[96:96+ln].decode(errors="replace")
    except Exception: return None
B="0xbead62a6c6b9a43ece68645f2328e0ebd015dbf2"
out={}
for fn in ["freeAvailable","freeUsed"]:
    r=call(B, sel(f"{fn}(address)")+enc(USER))
    out[fn+"_user"]= (int(r,16) if r else None)
out["tokenURI_1"]=dec_str(call(B, sel("tokenURI(uint256)")+"0"*63+"1"))
out["name_raw"]=call(B, sel("name()"))
out["symbol_raw"]=call(B, sel("symbol()"))
# ORYN freeRound(1): struct likely (uint256 startTime, uint256 endTime, ...) — decode all words
O="0x96135a41FA155752dc7154CDcaA480f2fBEC1493"
r=call(O, sel("freeRound(uint256)")+"0"*63+"1")
if r:
    b=bytes.fromhex(r[2:])
    out["oryn_freeRound1_words"]=[int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
else:
    out["oryn_freeRound1_words"]=None
r=call(O, sel("paidRound(uint256)")+"0"*63+"1")
if r:
    b=bytes.fromhex(r[2:])
    out["oryn_paidRound1_words"]=[int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
print(json.dumps(out,indent=1))
json.dump(out,open(f"{BASE}/run-2026-11-11-0331-probe2.json","w"),indent=1)
