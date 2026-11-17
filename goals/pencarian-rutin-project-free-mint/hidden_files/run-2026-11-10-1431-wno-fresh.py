#!/usr/bin/env python3
"""WNO fresh pre-execution reads, run 1431. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
WNO="0x8C969a4CD49E4774908e667702C3d7C3ece164D0"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def post_rpc(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def call(to,data):
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]},timeout=25)
            if "error" in r: continue
            v=r.get("result")
            if not v or v=="0x": return None
            return v
        except Exception: continue
    return None
def u1(sig,args=""):
    v=call(WNO,sel(sig)+args)
    return int(v,16) if v is not None else None
q=call(WNO,sel("quote(address,uint256)")+enc(USER)+"%064x"%1)
qv=[int(q[2+i*64:2+(i+1)*64],16) for i in range(3)] if q else None
ov=call(WNO,sel("overview()"))
ovv=[int(ov[2+i*64:2+(i+1)*64],16) for i in range(7)] if ov else None
out={"quote_user_1_cost_free_paid":qv,"overview_sharesSold_freeSold_paidSold_freeRemaining_sharesRemaining_price_tps":ovv,
     "freeUsed_user":u1("freeUsed(address)",enc(USER)),"sharesOf_user":u1("sharesOf(address)",enc(USER)),
     "balanceOf_user":u1("balanceOf(address)",enc(USER)),"isAgent_user":u1("isAgent(address)",enc(USER)),
     "totalFreeShares":u1("totalFreeShares()"),"FREE_SHARES":u1("FREE_SHARES()")}
print(json.dumps(out,indent=1))
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-10-1431-wno-fresh.json","w"),indent=1)
