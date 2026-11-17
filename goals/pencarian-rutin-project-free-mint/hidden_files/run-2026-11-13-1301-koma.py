#!/usr/bin/env python3
"""Re-triage KOMA 0xef48 (run 1301): fresh Sourcify ABI + broad sale views."""
import json, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR="0xef4882e029b8d58F81960c433D852a5b0A352965"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
AGENT_ID=107187496765866644729837695198686237165740365523485558112864918211974996443404
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return k.hexdigest()[:8]
def curl(url,timeout=20):
    try: return subprocess.run(["curl","-sL","--max-time",str(timeout),url],capture_output=True,text=True,timeout=timeout+5).stdout
    except Exception: return ""
def rpc(ep,payload,timeout=20):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return hex(n)[2:].rjust(64,"0")
def words(h):
    try:
        b=bytes.fromhex(h[2:]); return [int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
    except Exception: return None
out={"address":ADDR}
try:
    mj=json.loads(curl(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi",25))
    abi=mj.get("abi") or []
    fns=[f.get("name") for f in abi if f.get("type")=="function"]
    src=json.dumps(mj).lower()
    out["sourcify"]={"verified":bool(fns),"n_fns":len(fns),"fns":fns,
      "has_registry_addr":"0x60b9262456de011f7d15a54cdd8c48baaa8b022f" in src,
      "verifiedAt":mj.get("match",{}).get("verifiedAt") if isinstance(mj.get("match"),dict) else None}
except Exception as e: out["sourcify"]={"error":str(e)[:120]}
VIEWS=[("name","name()"),("symbol","symbol()"),("totalSupply","totalSupply()"),
 ("totalShares","totalShares()"),("totalMinted","totalMinted()"),
 ("freeClaimed","freeClaimed()"),("freeLeft","freeLeft()"),("freeSharesRemaining","freeSharesRemaining()"),
 ("freeAvailable_user","freeAvailable(address)",enc_addr(USER)),
 ("freeClaimed_user","freeClaimed(address)",enc_addr(USER)),
 ("freeFor_user","freeFor(address)",enc_addr(USER)),
 ("quote_user_1","quote(address,uint256)",enc_addr(USER)+enc_u(1)),
 ("costOf_user_1","costOf(address,uint256)",enc_addr(USER)+enc_u(1)),
 ("saleStart","saleStart()"),("startTime","startTime()"),("mintStart","mintStart()"),
 ("saleEnd","saleEnd()"),("endTime","endTime()"),("opened","opened()"),("saleOpen","saleOpen()"),
 ("agentRegistry","agentRegistry()"),("registry","registry()"),
 ("freeClaimedByAgent_user","freeClaimedByAgent(uint256)",enc_u(AGENT_ID)),
 ("balanceOf_user","balanceOf(address)",enc_addr(USER)),
 ("sharesOf_user","sharesOf(address)",enc_addr(USER)),
 ("decimals","decimals()"),("PRICE","PRICE()"),("price","price()")]
calls=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":ADDR,"data":"0x"+sel(sig)+(rest[0] if rest else "")},"latest"]} for i,(k,sig,*rest) in enumerate(VIEWS)]
views={}
for ep in EPS:
    try:
        r=rpc(ep,calls)
        if isinstance(r,list) and len(r)==len(calls):
            for it,(k,sig,*rest) in zip(r,VIEWS):
                if isinstance(it,dict) and it.get("result") and it["result"]!="0x":
                    w=words(it["result"])
                    if k in ("name","symbol"):
                        try:
                            b=bytes.fromhex(it["result"][2:])
                            views[k]=b[64:].split(b"\x00")[0].decode("utf-8","ignore")[:80] if len(b)>64 else it["result"]
                        except Exception: views[k]=it["result"][:80]
                    else: views[k]=w[0] if w and len(w)==1 else w
                else: views[k]=None
            break
    except Exception: continue
out["views"]=views
print(json.dumps(out,indent=1))
json.dump(out,open(BASE+"run-2026-11-13-1301-koma.json","w"),indent=1)
