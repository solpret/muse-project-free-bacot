#!/usr/bin/env python3
"""Sourcify feed new-3 shape probe run 0231 — read-only."""
import json, subprocess
ADDS=["0x9599fD07ad1de244EDe8E11680102D96988702F8","0xc0A5E51e91b3f2bD3d878c7e67BE327fb249BA9F","0xeAb49dcf2fe0145eA2Bb9205bd068c48c7EAD3CA"]
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
for a in ADDS:
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[a,"latest"]},timeout=25)
            code=(r.get("result") or "").lower()
            print(a, "codelen:", len(code), "registry-bytes:", "60b9262456de011f7d15a54cdd8c48baa8b022f" in code)
            break
        except Exception: continue
    # totalSupply() selector 0x18160ddd
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":a,"data":"0x18160ddd"},"latest"]},timeout=25)
            res=r.get("result")
            print("  totalSupply:", int(res,16) if res and res!="0x" else None)
            break
        except Exception as e: print("  ts fail", e); continue
print("DONE")
