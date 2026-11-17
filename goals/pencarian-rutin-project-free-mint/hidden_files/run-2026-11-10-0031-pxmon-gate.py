#!/usr/bin/env python3
"""PIXEL MONSTERS gate methods C/H/J + D probes. Read-only."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR="0x3f508d8826517123Fdd39c776e55F85Fa188E5fD"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
out={}
# (H) contractURI
for ep in EPS:
    try:
        r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":ADDR,"data":sel("contractURI()")},"latest"]})
        out["contractURI_raw"]=r.get("result") if isinstance(r,dict) else r
        break
    except Exception as e:
        out["contractURI_err"]=repr(e)
print("contractURI:",str(out.get("contractURI_raw"))[:300])
# (C) Sourcify metadata
try:
    req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=stdJson,metadata",headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=25) as resp:
        d=json.loads(resp.read().decode())
    s=json.dumps(d)
    import re
    out["sourcify_urls"]=sorted(set(re.findall(r'https?://[A-Za-z0-9._\-/~?=&%#]+',s)))[:20]
    print("sourcify urls:",out["sourcify_urls"])
    json.dump(d,open(f"{BASE}/run-2026-11-10-0031-pxmon-sources.json","w"))
except Exception as e:
    out["sourcify_err"]=repr(e); print("sourcify err:",e)
# (D) same-family probes (HEAD only; a hit counts ONLY if site prints exact contract)
for host in ["pixelmonsters.pages.dev","pixelmonsters.vercel.app","pxmon.pages.dev","pixel-monsters.pages.dev"]:
    try:
        req=urllib.request.Request(f"https://{host}",headers={"User-Agent":"Mozilla/5.0"},method="HEAD")
        with urllib.request.urlopen(req,timeout=15) as resp:
            print(host,"->",resp.status)
    except Exception as e:
        print(host,"->",getattr(e,'code',repr(e)))
json.dump(out,open(f"{BASE}/run-2026-11-10-0031-pxmon-gate.json","w"),indent=1)
