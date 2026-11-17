#!/usr/bin/env python3
"""Probe2 run 1131: 0x8653 ABI fn names; CAP7 tokenURI(0) (method I);
Odaily newsflash + PANews front page (route 6). Read-only."""
import json, urllib.request, subprocess, re
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
out={}
def get(url,timeout=25):
    req=urllib.request.Request(url,headers={"User-Agent":"free-bacot/1.0"})
    with urllib.request.urlopen(req,timeout=timeout) as r: return r.read().decode(errors="replace")
try:
    meta=json.loads(get("https://sourcify.dev/server/v2/contract/56/0x8653B09bDaD22c99915910962167F132E514331F?fields=abi"))
    abi=meta.get("abi",[])
    fns=sorted({e.get("name") for e in abi if e.get("type")=="function"})
    out["a8653_abi"]={"verified":True,"match":meta.get("match"),"verifiedAt":meta.get("verifiedAt"),"fns":fns}
except Exception as e:
    out["a8653_abi"]={"verified":False,"error":f"{type(e).__name__}: {str(e)[:150]}"}
print("8653-ABI",json.dumps(out["a8653_abi"])[:800],flush=True)
# CAP7 tokenURI(0) via eth_call
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
payload={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":"0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd","data":sel("tokenURI(uint256)")+"00"*32},"latest"]}
for ep in ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]:
    try:
        r=subprocess.run(["curl","-sL","--max-time","25","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=30)
        res=json.loads(r.stdout)
        out["cap7_tokenURI0"]=res
        print("CAP7-tokenURI0",str(res)[:300],flush=True)
        break
    except Exception as e:
        out["cap7_tokenURI0"]={"error":str(e)[:150]}
# route 6
for name,url in (("odaily","https://www.odaily.news/en/newsflash"),("panews","https://panews.io")):
    try:
        html=get(url,timeout=30)
        hits=[m for m in re.findall(r"(?i)(agent.{0,20}id|free.{0,20}mint|free.{0,20}share|agentic.{0,20}wallet)",html)]
        out[name]={"bytes":len(html),"keyword_hits":len(hits)}
    except Exception as e:
        out[name]={"error":f"{type(e).__name__}: {str(e)[:120]}"}
    print(name.upper(),out[name],flush=True)
json.dump(out,open(BASE+"run-2026-11-11-1131-probe2.json","w"),indent=1)
print("PROBE2 DONE",flush=True)
