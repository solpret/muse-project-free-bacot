#!/usr/bin/env python3
"""Run 0301 owner() checks for new first-read items. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def owner(addr):
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":sel("owner()")},"latest"]})
            res=r.get("result")
            if res and res!="0x" and "error" not in r:
                return "0x"+res[-40:]
        except Exception: continue
    return None
d=json.load(open('same-owner-discards.json'))
disc={e.get('owner','').lower() for e in d}
for name,addr in [("SAKURA","0xF2705A84602369069782624279837A08bdbBf6D6"),
                  ("MOODENG-sale","0xbb45668788a08ceceea6b1a0d0f25c1b667e1668"),
                  ("FEED88D7","0x88D7624Ecec5D327920C49F9Fe295885740Effe1"),
                  ("ACORE","0xf4bacf30fb8f69373f63d99c657f53dd7774af1d")]:
    o=owner(addr)
    print(name, "owner:", o, "in_discards:", (o or "").lower() in disc, flush=True)
print("DONE")
