#!/usr/bin/env python3
"""Follow-up for S1-Ff65 (run 2331): FREE_CAP / mintOpensAt / freeCountBy(user) / FREE_PER_WALLET."""
import json, subprocess
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def post(ep, payload, timeout=25):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
ADDR = "0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96"
VIEWS = ["FREE_CAP()","FREE_PER_WALLET()","MAX_PER_WALLET()","mintOpensAt()","freeCountBy(address)","mintsBy(address)","nextTokenId()","holdsAgentId(address)"]
calls, keys = [], []
for i, sig in enumerate(VIEWS):
    base = sig.split("(")[0]
    if "(address)" in sig: data, key = sel(sig)+enc(USER), base+"_user"
    else: data, key = sel(sig), base
    calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":ADDR,"data":data},"latest"]})
    keys.append(key)
res = None
for ep in EPS:
    try:
        r = post(ep, calls)
        if isinstance(r, list) and len(r) == len(calls): res = r; break
    except Exception: continue
out = {} if res is None else {k: (None if isinstance(it, dict) and "error" in it else (to_int(it.get("result")) if isinstance(it, dict) else None)) for it, k in zip(res, keys)}
print(json.dumps(out, indent=1))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-11-2331-verify-ff65b.json","w"), indent=1)
