#!/usr/bin/env python3
"""Punch Card fresh read run 2031. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
ADDR = "0x1d4ef0587dd3ff3875a141d4711c60bca40587c4"
EP = "https://bsc-dataseed.binance.org/"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def call(data):
    payload = {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":ADDR,"data":data},"latest"]}
    out = subprocess.run(["curl","-sL","--max-time","30","-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps(payload)], capture_output=True, text=True, timeout=40).stdout
    try: return json.loads(out).get("result")
    except Exception: return None
def u(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
res = {}
for name, sig in [("totalSupply","totalSupply()"),("freeMinted","freeMinted()"),("totalMinted","totalMinted()")]:
    res[name] = u(call(sel(sig)))
print(json.dumps(res))
blk = subprocess.run(["curl","-sL","--max-time","30","-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})], capture_output=True, text=True, timeout=40).stdout
print("block:", int(json.loads(blk)["result"],16))
json.dump(res, open("run-2026-11-16-2031-verify-punch.json","w"), indent=1)
