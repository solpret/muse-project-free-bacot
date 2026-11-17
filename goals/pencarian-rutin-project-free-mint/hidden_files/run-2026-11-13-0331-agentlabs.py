#!/usr/bin/env python3
"""AgentLabs SPEC contract read for run 2026-11-13 01:31 WIB. Read-only."""
import json, subprocess, time
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SPEC = "0x639329f5dc4317c44D9Fed961a1217ba845012F7"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")
VIEWS = {
  "genesisOpen": "0x14349d0c",
  "currentExperiment": "0xf85ffaa3",
  "totalSpecimens": "0xfc00816d",
  "specimensInExperiment(1)": "0xefb14faf" + enc_u(1),
  "participantsOf(1)": "0xe200c857" + enc_u(1),
  "experimentEnd(1)": "0x37e46fcd" + enc_u(1),
  "specimensOf(1,user)": "0xa59e6ead" + enc_u(1) + enc_addr(USER),
  "priceFor(user)": "0xf12a7add" + enc_addr(USER),
  "holdsAgentId(user)": "0x11213086" + enc_addr(USER),
  "balanceOf(user)": "0x70a08231" + enc_addr(USER),
  "isSealed(1)": "0x2c1758c1" + enc_u(1),
  "totalSupply": "0x18160ddd",
}
calls = [{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":SPEC,"data":d},"latest"]}
         for i,d in enumerate(VIEWS.values())]
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
out = {"contract": SPEC, "views": {}}
for ep in EPS:
    try:
        r = subprocess.run(["curl","-sL","--max-time","25","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(calls)],
                           capture_output=True, text=True, timeout=30)
        res = json.loads(r.stdout)
        if isinstance(res, list) and len(res)==len(calls):
            out["views"] = {k: (None if (isinstance(it,dict) and "error" in it) else to_int(it.get("result")) if isinstance(it,dict) else None)
                            for it,k in zip(res, VIEWS.keys())}
            out["endpoint"] = ep
            break
    except Exception as e:
        out.setdefault("errors", []).append(str(e)[:100])
try:
    r = subprocess.run(["curl","-sL","--max-time","15","-X","POST",EPS[0],"-H","Content-Type: application/json",
                        "-d", json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})],
                       capture_output=True, text=True, timeout=20)
    out["block"] = int(json.loads(r.stdout).get("result"),16)
except Exception as e:
    out["block_error"] = str(e)[:100]
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-13-0331-agentlabs.json","w"), indent=1)
