#!/usr/bin/env python3
"""Re-probe the 8 null fields from the 1539 leg4 reread on a fallback endpoint.
Null = eth_call exception in batch, not on-chain state. Verify + correct own reread file."""
import json, re, sys, time, concurrent.futures
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
src = open(BASE+"hot-leg-2026-11-08-1129.py").read()
def extract(var):
    m = re.search(re.escape(var)+r"\s*=\s*(\{.*?^\})", src, re.S|re.M)
    return eval(m.group(1))
V = extract("V"); ITEMS = extract("ITEMS")
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
NULLS = [("Tri333","freeMinted"),("WAR3","freeMinted"),("HUNT PASS","totalMinted"),
         ("fab7-variant","freeMinted"),("DinoAgent","freeMinted"),("LOCKSMITH","totalMinted"),
         ("HOG ORBIT","freeLeft"),("AgentBook","FREE_QUOTA")]
def probe(ep, item, field):
    addr, keys = ITEMS[item]
    sig, arg = V[field]
    data = sel(sig)
    if arg == "USER": data += enc_addr(USER)
    elif arg == "USER1": data += enc_addr(USER) + format(1, "064x")
    try:
        res = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=20)
        return to_int(res[0])
    except Exception:
        return None
reread = json.load(open(BASE+"hot-leg-2026-11-08-1539-reread.json"))
out = {}
for ep in ("https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"):
    for item, field in NULLS:
        if out.get((item, field)) is not None: continue
        v = probe(ep, item, field)
        if v is not None: out[(item, field)] = v
    if len(out) == len(NULLS): break
fixed, still_null = [], []
for item, field in NULLS:
    v = out.get((item, field))
    if v is not None:
        reread["items"][item][field] = v
        fixed.append({"item": item, "field": field, "value": v})
    else:
        still_null.append({"item": item, "field": field})
json.dump(reread, open(BASE+"hot-leg-2026-11-08-1539-reread.json","w"), indent=1)
print(json.dumps({"fixed": fixed, "still_null": still_null, "block": reread["block"]}, indent=1))
