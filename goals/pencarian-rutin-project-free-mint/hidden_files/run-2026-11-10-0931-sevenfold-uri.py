#!/usr/bin/env python3
"""SEVENFOLD methods H/I/C: contractURI + tokenURI(1) + Sourcify metadata. Read-only."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak
ADDR="0x4ca724a354db4f743607ecc1a5f117b2e617c8ae"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(data):
    for ep in EPS:
        try:
            out=subprocess.run(["curl","-sL","--max-time","25","-X","POST",ep,"-H","Content-Type: application/json",
                "-d",json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":ADDR,"data":data},"latest"]})],
                capture_output=True,text=True,timeout=30).stdout
            r=json.loads(out)
            if "result" in r: return r["result"]
        except Exception as e: print("call err", e)
    return None
def decode_str(h):
    try:
        b=bytes.fromhex(h[2:])
        if len(b)<64: return None
        off=int.from_bytes(b[0:32],"big"); ln=int.from_bytes(b[off:off+32],"big")
        return b[off+32:off+32+ln].decode(errors="replace")
    except Exception as e: return f"decode-err {e}"
res={}
res["contractURI"]=decode_str(call(sel("contractURI()"))) 
# tokenURI(1)
d=sel("tokenURI(uint256)")+"0000000000000000000000000000000000000000000000000000000000000001"
res["tokenURI_1"]=decode_str(call(d))
print(json.dumps(res, indent=1))
json.dump(res, open("run-2026-11-10-0931-sevenfold-uri.json","w"), indent=1)
# Sourcify metadata (C)
try:
    req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{ADDR}", headers={"User-Agent":"free-bacot/0931"})
    with urllib.request.urlopen(req, timeout=30) as r:
        meta=json.loads(r.read().decode())
    print("sourcify match:", meta.get("match"), "verifiedAt:", meta.get("verifiedAt"))
    std=meta.get("stdJson",{})
    srcs=list(std.get("sources",{}).keys()) if isinstance(std,dict) else []
    print("sources:", srcs)
    json.dump(meta, open("run-2026-11-10-0931-sevenfold-sourcify.json","w"), indent=1)
except Exception as e:
    print("sourcify meta FAIL:", type(e).__name__, str(e)[:200])
