#!/usr/bin/env python3
"""Retry only the null-field single calls from the 1429 leg4 re-read (transient RPC failures)."""
import json, re, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
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
    except Exception:
        return None
reread = json.load(open(BASE+"hot-leg-2026-11-08-1429-reread.json"))
prev = json.load(open(BASE+"hot-leg-2026-11-08-1424-reread.json"))
retried, fixed, still_null = 0, 0, []
for name, cur in reread["items"].items():
    addr, keys = ITEMS[name]
    for k in keys:
        if cur.get(k) is None:
            retried += 1
            sig, arg = V[k]
            v = single(addr, sig, arg)
            if v is not None:
                cur[k] = v; fixed += 1
            else:
                still_null.append((name, k))
json.dump(reread, open(BASE+"hot-leg-2026-11-08-1429-reread.json","w"), indent=1)
diffs = []
for name, cur in reread["items"].items():
    old = prev["items"].get(name, {})
    for k, v in cur.items():
        if k == "address": continue
        if v != old.get(k):
            diffs.append({"item": name, "field": k, "old": old.get(k), "new": v})
print(json.dumps({"retried": retried, "fixed": fixed, "still_null": still_null,
                  "diffs_vs_1424": diffs, "block": reread["block"]}, indent=1))
