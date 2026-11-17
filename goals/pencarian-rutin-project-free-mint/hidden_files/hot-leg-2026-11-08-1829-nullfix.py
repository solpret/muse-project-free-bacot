#!/usr/bin/env python3
"""Re-read leg4 null fields one-by-one (single eth_call each) — fast_rpc.batch
kills a whole batch on one revert, so nulls are read artifacts until proven."""
import json, sys, time, re
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-1829"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc-dataseed1.bnbchain.org/"
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
def single(addr, sig, arg=""):
    data = sel(sig)
    if arg == "USER": data += enc_addr(USER)
    elif arg == "USER1": data += enc_addr(USER) + format(1, "064x")
    try:
        res = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=EP, timeout=30)
        return to_int(res[0])
    except Exception as ex:
        return f"ERR {str(ex)[:100]}"
reread = json.load(open(BASE+TAG+"-reread.json"))
prev = json.load(open(BASE+"hot-leg-2026-11-08-1824-reread.json"))
fixed = {}
for name, cur in reread["items"].items():
    addr, keys = ITEMS[name]
    for k, v in list(cur.items()):
        if k == "address": continue
        if v is None:
            sig, arg = V[k]
            nv = single(addr, sig, arg)
            fixed[f"{name}.{k}"] = {"old_1824": prev["items"].get(name, {}).get(k), "reread_single": nv}
            cur[k] = nv if isinstance(nv, int) else v
json.dump(reread, open(BASE+TAG+"-reread.json","w"), indent=1)
json.dump(fixed, open(BASE+TAG+"-nullfix.json","w"), indent=1)
print(json.dumps(fixed, indent=1))
