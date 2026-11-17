#!/usr/bin/env python3
import json, subprocess, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
import fast_rpc
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def call(to, sig, arg=None):
    d = "0x" + sel(sig)
    if arg == "user": d += enc_addr(USER)
    return (to, d)
PLAN = [
 ("BNBG", "0x1595013dfc8c6b3f4b172254bf09bdaf1421002b", [("totalMinted", "totalMinted()", None)]),
 ("SPARKS", "0xd52fd117c4b47d03e4e16e778871f09faa5a024b", [("totalSupply", "totalSupply()", None)]),
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
def one_batch(chunk, ep):
    payload = [{"jsonrpc":"2.0","id":j+1,"method":"eth_call",
                "params":[{"to":to,"data":data},"latest"]} for j,(to,data) in enumerate(chunk)]
    req = urllib.request.Request(ep, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())
out = {}
errs = []
for i in range(0, len(calls), 5):
    chunk = calls[i:i+5]
    got = None
    for ep in fast_rpc.healthy_endpoints() or fast_rpc.ENDPOINTS:
        try:
            resp = one_batch(chunk, ep)
            if isinstance(resp, list): got = resp; break
        except Exception as e:
            errs.append(f"{ep}: {type(e).__name__}")
            continue
    if got is None:
        # last resort: direct curl once more
        r = subprocess.run(["curl","-s","--max-time","20","https://bsc-dataseed.binance.org/",
                            "-H","Content-Type: application/json","-d",json.dumps(
                             [{"jsonrpc":"2.0","id":j+1,"method":"eth_call",
                               "params":[{"to":to,"data":data},"latest"]} for j,(to,data) in enumerate(chunk)])],
                           capture_output=True, timeout=25)
        try:
            got = json.loads(r.stdout.decode())
        except Exception as e:
            errs.append(f"curl: {type(e).__name__}: {r.stdout[:100]!r}")
            got = []
    by_id = {it["id"]: it for it in got if isinstance(it, dict)}
    for j in range(len(chunk)):
        it = by_id.get(j+1, {})
        name, addr, label = meta[i+j]
        val = None
        if "result" in it and it["result"] not in (None, "0x"):
            try: val = int(it["result"], 16)
            except Exception: val = it["result"]
        out.setdefault(name, {"address": addr, "views": {}})["views"][label] = val
print(json.dumps({"reprobe": out, "errors": errs}, indent=1))
json.dump(out, open("hot-leg-2026-11-16-1409-reprobe.json","w"), indent=1)
