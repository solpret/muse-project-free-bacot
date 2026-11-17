#!/usr/bin/env python3
"""Run 0301 NIGHTFORGE gate recheck (H+I+J+G light). Read-only."""
import subprocess, json
ADDR="0x22f43ba09fd4beb9417d4484c60370354b220186"
def fetch(url, timeout=20):
    try:
        r=subprocess.run(["curl","-sL","--max-time",str(timeout),url],capture_output=True,text=True,timeout=timeout+5)
        return r.stdout
    except Exception as e:
        return ""
for path in ["", "/llms.txt", "/skill.md", "/launch.json", "/agent.json", "/meta/collection.json"]:
    url="https://nightforge.pages.dev"+path
    body=fetch(url)
    print(f"NF-GATE {path or '/'} {len(body)} prints_contract={ADDR.lower() in body.lower()}", flush=True)
# contractURI + tokenURI via eth_call (contractURI selector 0xe8a3d485, tokenURI(uint256) 0xc87b56dd)
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
for label,data in [("contractURI",sel("contractURI()")),("tokenURI(1)",sel("tokenURI(uint256)")+"0"*63+"1")]:
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":ADDR,"data":data},"latest"]})
            print(label, str(r.get("result"))[:120] if isinstance(r,dict) else r, flush=True)
            break
        except Exception as e:
            print(label,"ERR",e,flush=True); continue
print("DONE")
