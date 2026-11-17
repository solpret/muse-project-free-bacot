#!/usr/bin/env python3
"""Single-call retry for SolNFT + AgcNFT (batch failed in verify-2131).
One eth_call per view, endpoint race via curl, 15s timeout each."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def call(addr, sig, timeout=15):
    base = sig.split("(")[0]
    data = sel(sig) + enc(USER) if "(address)" in sig else sel(sig)
    payload = {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}
    for ep in EPS:
        try:
            out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
                "-H","Content-Type: application/json","-d",json.dumps(payload)],
                capture_output=True, text=True, timeout=timeout+5).stdout
            r = json.loads(out)
            if isinstance(r, dict) and "result" in r and r["result"] not in (None, "0x"):
                return to_int(r["result"])
            if isinstance(r, dict) and r.get("result") == "0x":
                return 0
        except Exception:
            continue
    return None
VIEWS = ["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_CAP()","FREE_SUPPLY()",
         "MAX_SUPPLY()","mintOpen()","mintOpensAt()","price()","PRICE()","balanceOf(address)",
         "freeClaimed(address)","mintsBy(address)","holdsAgentId(address)","agentIdRegistry()"]
out = {"started_wib": "2026-11-12 21:31 WIB retry", "reads": {}}
t0 = time.time()
for name, addr in [("SolNFT","0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606"),
                   ("AgcNFT","0xdAc222886b887fC5b6262889B189B8eb57e99794")]:
    res = {}
    for v in VIEWS:
        res[v.split("(")[0] + ("_user" if "(address)" in v else "")] = call(addr, v)
    out["reads"][name] = {"address": addr, "views": res}
    print(name, {k:val for k,val in res.items() if val is not None}, flush=True)
out["elapsed_s"] = round(time.time()-t0, 1)
json.dump(out, open(BASE+"run-2026-11-12-2131-retry-new.json","w"), indent=1)
print("ELAPSED", out["elapsed_s"])
