#!/usr/bin/env python3
"""Run 1631 gate attempts for Skunk Hollow (strong-lead gate block): (D) same-family pattern hosts,
(I) tokenURI external_url, (J) ABI site-function grep. Read-only. Also Marbleworks tokenURI(1)."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
SK="0x88E4b613609af6C479F11D78e5a696d84B78993B"
MW="0xCc844748C64b9b8e45aC4504553C9757c7CDB7E0"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def call(addr,data):
    for ep in ["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
            if isinstance(r,dict) and "result" in r: return r["result"]
        except Exception: continue
    return None
def dec_str(h):
    try:
        if not h or h=="0x": return None
        b=bytes.fromhex(h[2:])
        ln=int.from_bytes(b[32:64],"big")
        return b[64:64+ln].decode(errors="ignore")
    except Exception: return None
out={}
# (I) tokenURI
for label,addr,tid in [("Skunk",SK,1),("Skunk0",SK,0),("Marbleworks",MW,1)]:
    data=sel("tokenURI(uint256)")+str(tid).rjust(64,"0")
    uri=dec_str(call(addr,data))
    out[f"tokenURI_{label}"]=uri
    print(f"tokenURI {label}({tid}):", uri, flush=True)
    if uri:
        try:
            req=urllib.request.Request(uri,headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req,timeout=15) as r: body=r.read().decode(errors="ignore")[:2000]
            print(f"  fetched {len(body)} chars:", body[:300], flush=True)
            out[f"tokenURI_{label}_body"]=body[:1000]
        except Exception as e:
            print(f"  fetch ERR {e}", flush=True); out[f"tokenURI_{label}_fetch_err"]=str(e)
# (J) Skunk ABI grep
try:
    req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{SK}?fields=abi",headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=20) as r: data=json.load(r)
    abi=data.get("abi") or []
    fns=[f.get("name") for f in abi if f.get("type")=="function"]
    site_fns=[f for f in fns if any(k in f.lower() for k in ("website","site","url","domain","external","link"))]
    out["skunk_abi_fns"]=fns; out["skunk_site_fns"]=site_fns
    print("Skunk ABI fns:", len(fns), "site-ish:", site_fns, flush=True)
except Exception as e:
    print("Skunk ABI ERR", e, flush=True); out["skunk_abi_err"]=str(e)
# (D) pattern hosts
for host in ["https://skunkhollow.pages.dev/","https://skunk-hollow.pages.dev/","https://skunkhollow.vercel.app/","https://skunkhollow.fun/"]:
    try:
        req=urllib.request.Request(host,headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req,timeout=12) as r:
            body=r.read().decode(errors="ignore")
            hit = SK.lower() in body.lower() or "88E4b613" in body
            print(f"(D) {host} -> HTTP {r.status}, {len(body)} bytes, prints-contract={hit}", flush=True)
            out[f"D_{host}"]={"status":r.status,"bytes":len(body),"prints_contract":hit}
    except Exception as e:
        print(f"(D) {host} -> ERR {e}", flush=True); out[f"D_{host}"]={"error":str(e)}
with open(f"{BASE}/run-2026-11-09-1631-gate-skunk.json","w") as f: json.dump(out,f,indent=1)
print("GATE ATTEMPTS DONE", flush=True)
