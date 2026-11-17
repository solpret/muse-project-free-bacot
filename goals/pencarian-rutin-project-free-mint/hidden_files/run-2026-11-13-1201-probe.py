#!/usr/bin/env python3
"""Probe for free-mint-search run 2026-11-13 12:01 WIB.
- Boltbook-new 0x68e42f... : totalSupply/free views/registry/Sourcify ABI
- Hot-leg registry-hit 0xce18f9DE... : same
- 5x 37-fn Sourcify template contracts: totalSupply only (mint-count check)
Read-only; writes run-2026-11-13-1201-probe.json."""
import json, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def curl(url,timeout=20):
    try: return subprocess.run(["curl","-sL","--max-time",str(timeout),url],capture_output=True,text=True,timeout=timeout+5).stdout
    except Exception: return ""
def rpc(ep,payload,timeout=20):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def words(h):
    try:
        b=bytes.fromhex(h[2:]); return [int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
    except Exception: return None
VIEWS=[("totalSupply","totalSupply()"),("totalMinted","totalMinted()"),("freeMinted","freeMinted()"),("freeClaimed","freeClaimed()"),("FREE_SUPPLY","FREE_SUPPLY()"),("FREE_CAP","FREE_CAP()"),("MAX_SUPPLY","MAX_SUPPLY()"),("mintOpen","mintOpen()"),("name","name()"),("symbol","symbol()"),("agentIdRegistry","agentIdRegistry()"),("registry","registry()")]
def read(addr):
    calls=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":sel(s)},"latest"]} for i,(k,s) in enumerate(VIEWS)]
    for ep in EPS:
        try:
            r=rpc(ep,calls)
            if not isinstance(r,list) or len(r)!=len(calls): continue
            out={}
            for it,(k,s) in zip(r,VIEWS):
                if not isinstance(it,dict) or "error" in it or not it.get("result") or it["result"]=="0x": out[k]=None; continue
                w=words(it["result"]); out[k]=w[0] if w is not None and len(w)==1 else w
            return out
        except Exception: continue
    return {"error":"all-endpoints-failed"}
TARGETS={
 "Boltbook-new-68e42f":"0x68e42fef5962443a74ccd80a7b44014f2b751d78",
 "Hotleg-registry-hit-ce18":"0xce18f9DE452c63D806A9C273EFa09eD1f80b3BA3",
 "Sourcify-37fn-3fF78B":"0x3fF78B7965A4DDa4d870Bd0cf1b30947bE49CD23",
 "Sourcify-37fn-2Fa60c":"0x2Fa60cf65Ca989728204B43aB0D9DEA13E6bf169",
 "Sourcify-37fn-F12257":"0xF1225751101f7ACa3f539f74a63f6A396D58F938",
 "Sourcify-37fn-4DCB21":"0x4DCB214c08b25e52e1ad479F8cA60C3DB3E03C7D",
 "Sourcify-37fn-189314":"0x1893143e7d3E1340e0Df456402296511FC185862",
}
out={"started_wib":"2026-11-13T12:01+07:00","reads":{}}
for n,a in TARGETS.items():
    out["reads"][n]={"address":a,"views":read(a)}
    try:
        meta=curl(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",20)
        mj=json.loads(meta); abi=mj.get("abi") or []
        fns=[f.get("name") for f in abi if f.get("type")=="function"]
        out["reads"][n]["sourcify_fns"]=len(fns)
        out["reads"][n]["sourcify_fn_names"]=fns[:80]
    except Exception as e:
        out["reads"][n]["sourcify_error"]=str(e)[:120]
print(json.dumps(out,indent=1))
json.dump(out,open(BASE+"run-2026-11-13-1201-probe.json","w"),indent=1)
