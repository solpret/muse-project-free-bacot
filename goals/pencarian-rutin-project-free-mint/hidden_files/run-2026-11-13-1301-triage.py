#!/usr/bin/env python3
"""Triage new Boltbook address 0x14d8b77e27d478ece7e6344b59744526b8526fac (run 1301).
Selector probe + Sourcify ABI + generic on-chain views. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR="0x14d8b77e27d478ece7e6344b59744526b8526fac"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return k.hexdigest()[:8]
def curl(url,timeout=20):
    try:
        return subprocess.run(["curl","-sL","--max-time",str(timeout),url],capture_output=True,text=True,timeout=timeout+5).stdout
    except Exception: return ""
def rpc(ep,payload,timeout=20):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def words(h):
    try:
        b=bytes.fromhex(h[2:]); return [int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
    except Exception: return None
out={"address":ADDR}
# Sourcify ABI
try:
    mj=json.loads(curl(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi",20))
    abi=mj.get("abi") or []
    fns=[f.get("name") for f in abi if f.get("type")=="function"]
    out["sourcify"]={"verified":bool(fns),"n_fns":len(fns),"fns":fns,
                     "src_has_registry":"0x60b9262456de011f7d15a54cdd8c48baaa8b022f" in json.dumps(mj).lower()}
except Exception as e:
    out["sourcify"]={"error":str(e)[:120]}
# selector probe
MINT=["mint(uint256)","mint(address,uint256)","mint()","mintFree()","claimFree()","claimFreeAgent(uint256)","buyShares(uint256)","mintShares(uint256)","mint(address)"]
QUOTE=["quote(address,uint256)","quote(uint256)","costOf(address,uint256)","getQuote(uint256)","price()"]
FREE=["freeClaimed()","freeLeft()","freeSharesRemaining()","freeAvailable(address)","freeClaimed(address)","freeFor(address)","freeUsed()","freeMinted()","freeSupply()","freeSharePoolExhausted()","freeSharesClaimed()","freeClaimedByAgent(uint256)"]
AGENT=["agentIdRegistry()","registry()","agentRegistry()","holdsAgentId(address)","agentIdOf(address)"]
for ep in EPS:
    try:
        r=rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[ADDR,"latest"]})
        code=(r.get("result") or "")[2:]
        cb=bytes.fromhex(code)
        def has(sigs): return [s for s in sigs if bytes.fromhex(sel(s)) in cb]
        out["probe"]={"code_len":len(cb),"mint":has(MINT),"quote":has(QUOTE),"free":has(FREE),"agent":has(AGENT)}
        break
    except Exception as e:
        out["probe_error"]=str(e)[:80]
# generic views
VIEWS=[("totalSupply","totalSupply()"),("totalMinted","totalMinted()"),("freeMinted","freeMinted()"),
 ("freeClaimed","freeClaimed()"),("FREE_SUPPLY","FREE_SUPPLY()"),("FREE_CAP","FREE_CAP()"),
 ("MAX_SUPPLY","MAX_SUPPLY()"),("mintOpen","mintOpen()"),("mintStart","mintStart()"),
 ("mintOpensAt","mintOpensAt()"),("name","name()"),("symbol","symbol()"),
 ("balanceOf_user","balanceOf(address)",enc_addr(USER)),
 ("freeClaimed_user","freeClaimed(address)",enc_addr(USER)),
 ("contractURI","contractURI()"),("agentIdRegistry","agentIdRegistry()"),("registry","registry()")]
calls=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":ADDR,"data":"0x"+sel(sig)+(rest[0] if rest else "")},"latest"]} for i,(k,sig,*rest) in enumerate(VIEWS)]
views={}
for ep in EPS:
    try:
        r=rpc(ep,calls)
        if isinstance(r,list) and len(r)==len(calls):
            for it,(k,sig,*rest) in zip(r,VIEWS):
                if isinstance(it,dict) and it.get("result") and it["result"]!="0x":
                    w=words(it["result"])
                    if k in ("name","symbol","contractURI"):
                        try:
                            b=bytes.fromhex(it["result"][2:])
                            s=b[64:].split(b"\x00")[0].decode("utf-8","ignore") if len(b)>64 else it["result"]
                            views[k]=s[:200]
                        except Exception: views[k]=it["result"][:80]
                    else:
                        views[k]=w[0] if w and len(w)==1 else w
                else: views[k]=None
            break
    except Exception: continue
out["views"]=views
print(json.dumps(out,indent=1))
json.dump(out,open(BASE+"run-2026-11-13-1301-triage.json","w"),indent=1)
