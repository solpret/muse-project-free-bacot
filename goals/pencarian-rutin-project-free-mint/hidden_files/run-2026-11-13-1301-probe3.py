#!/usr/bin/env python3
"""Probe 3 genuinely-new Sourcify feed contracts (run 1301 retry)."""
import json, subprocess
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return k.hexdigest()[:8]
def curl(url,timeout=20):
    try: return subprocess.run(["curl","-sL","--max-time",str(timeout),url],capture_output=True,text=True,timeout=timeout+5).stdout
    except Exception: return ""
def rpc(ep,payload,timeout=20):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
MINT=["mint(uint256)","mint(address,uint256)","mint()","mintFree()","claimFree()","claimFreeAgent(uint256)","buyShares(uint256)","mintShares(uint256)","mint(address)"]
QUOTE=["quote(address,uint256)","quote(uint256)","costOf(address,uint256)","getQuote(uint256)","price()"]
FREE=["freeClaimed()","freeLeft()","freeSharesRemaining()","freeAvailable(address)","freeClaimed(address)","freeFor(address)","freeUsed()","freeMinted()","freeSupply()","freeSharePoolExhausted()","freeSharesClaimed()","freeClaimedByAgent(uint256)"]
AGENT=["agentIdRegistry()","registry()","agentRegistry()","holdsAgentId(address)","agentIdOf(address)"]
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
out={}
for a in ["0xbFe7C3eDc07CDC7065a605Ae949D3A01A14c147d","0x3cD033589040954aa1a62791Ff967289fa37A3B2","0xf597ab8E004AD3f494B4Ccb95A399240B9E3FA8b"]:
    rec={}
    try:
        mj=json.loads(curl(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",20))
        abi=mj.get("abi") or []
        fns=[f.get("name") for f in abi if f.get("type")=="function"]
        rec["sourcify_fns"]=len(fns)
        if fns:
            src=json.dumps(mj).lower()
            rec["fns"]=fns
            rec["S1"]=bool(any(n in fns for n in ("mint","claimFree","mintFree","claimFreeAgent")) and any("quote" in n.lower() or "cost" in n.lower() for n in fns) and [n for n in fns if "free" in n.lower()] and ("0x60b9262456de011f7d15a54cdd8c48baaa8b022f" in src or "agent" in " ".join(fns).lower()))
    except Exception as e: rec["sourcify_error"]=str(e)[:100]
    if rec.get("sourcify_fns",0)==0:
        for ep in EPS:
            try:
                r=rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[a,"latest"]})
                code=(r.get("result") or "")[2:]
                cb=bytes.fromhex(code)
                def has(sigs): return [s for s in sigs if bytes.fromhex(sel(s)) in cb]
                pr={"code_len":len(cb),"mint":has(MINT),"quote":has(QUOTE),"free":has(FREE),"agent":has(AGENT)}
                rec["probe"]=pr
                rec["S1_probe"]=bool(pr["mint"] and pr["quote"] and pr["free"] and pr["agent"])
                rec["S2_probe"]=bool(pr["mint"] and pr["free"] and pr["agent"])
                break
            except Exception: continue
    out[a]=rec
print(json.dumps(out,indent=1))
json.dump(out,open("run-2026-11-13-1301-probe3.json","w"),indent=1)
