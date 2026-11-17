#!/usr/bin/env python3
"""Re-probe leg-4 entries that returned all-None in the 14:09 run (BNBG, SPARKS,
Ledgera, BoldLeonidas) via direct curl batches, to distinguish RPC read failure
from real state change."""
import json, subprocess, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def call(to, sig, arg=None):
    d = "0x" + sel(sig)
    if arg == "user": d += enc_addr(USER)
    return (to, d)
PLAN = [
 ("BNBG", "0x1595013dfc8c6b3f4b172254bf09bdaf1421002b",
  [("totalMinted", "totalMinted()", None)]),
 ("SPARKS", "0xd52fd117c4b47d03e4e16e778871f09faa5a024b",
  [("totalSupply", "totalSupply()", None)]),
 ("Ledgera", "0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d",
  [("freeClaimed", "freeClaimed()", None), ("totalSupply", "totalSupply()", None),
   ("mintOpen", "mintOpen()", None), ("freeUsed_user", "freeUsed(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("BoldLeonidas", "0x84bcb8c16566e81ce902530c9da1e3de291f9941",
  [("totalSupply", "totalSupply()", None), ("mintOpen", "mintOpen()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
]
calls, meta = [], []
for name, addr, views in PLAN:
    for label, sig, arg in views:
        calls.append(call(addr, sig, arg)); meta.append((name, addr, label))
out = {}
for i in range(0, len(calls), 5):
    chunk = calls[i:i+5]
    payload = [{"jsonrpc":"2.0","id":j+1,"method":"eth_call",
                "params":[{"to":to,"data":data},"latest"]}
               for j,(to,data) in enumerate(chunk)]
    r = subprocess.run(["curl","-s","--max-time","20","https://bsc-dataseed.binance.org/",
                        "-H","Content-Type: application/json","-d",json.dumps(payload)],
                       capture_output=True, timeout=25)
    resp = json.loads(r.stdout.decode())
    by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
    for j in range(len(chunk)):
        it = by_id.get(j+1, {})
        name, addr, label = meta[i+j]
        val = None
        if "result" in it and it["result"] not in (None, "0x"):
            try: val = int(it["result"], 16)
            except Exception: val = it["result"]
        out.setdefault(name, {"address": addr, "views": {}})["views"][label] = val
print(json.dumps(out, indent=1))
json.dump(out, open("hot-leg-2026-11-16-1409-reprobe.json","w"), indent=1)
