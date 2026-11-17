#!/usr/bin/env python3
"""SEVEN gate reads: tokenURI(1), owner(), name(), symbol(). Read-only."""
import json, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
SEVEN="0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def post_rpc(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def call(data):
    payload={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":SEVEN,"data":data},"latest"]}
    for ep in EPS:
        try:
            r=post_rpc(ep,payload,timeout=25)
            if "result" in r: return r["result"]
        except Exception: continue
    return None
def decode_str(hexstr):
    try:
        b=bytes.fromhex(hexstr[2:])
        off=int.from_bytes(b[:32],"big"); ln=int.from_bytes(b[32+off:64+off],"big") if False else int.from_bytes(b[32:64],"big")
        ln=int.from_bytes(b[32:64],"big")
        return b[64:64+ln].decode(errors="replace")
    except Exception as e: return f"<decode fail {e}>"
out={}
out["tokenURI_1_raw"]=call(sel("tokenURI(uint256)")+"0000000000000000000000000000000000000000000000000000000000000001")
out["tokenURI_1"]=decode_str(out["tokenURI_1_raw"]) if out["tokenURI_1_raw"] else None
out["owner_raw"]=call(sel("owner()"))
out["owner"]="0x"+out["owner_raw"][-40:] if out["owner_raw"] else None
out["name_raw"]=call(sel("name()"))
out["name"]=decode_str(out["name_raw"]) if out["name_raw"] else None
out["symbol_raw"]=call(sel("symbol()"))
out["symbol"]=decode_str(out["symbol_raw"]) if out["symbol_raw"] else None
print(json.dumps(out,indent=1))
json.dump(out,open(BASE+"run-2026-11-12-0231-seven-gate.json","w"),indent=1)
