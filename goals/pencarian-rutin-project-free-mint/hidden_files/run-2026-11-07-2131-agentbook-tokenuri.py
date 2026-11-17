#!/usr/bin/env python3
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
ADDR = "0xEECaCBE6eAC6D6F2a38e8daA9049C7AA08aD43b0"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def dec_str(v):
    try:
        b = bytes.fromhex(v[2:]); ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception: return None
ep = "https://bsc-dataseed1.bnbchain.org/"
for tid in (1, 0):
    data = sel("tokenURI(uint256)") + ("%064x" % tid)
    try:
        r = batch([("eth_call", [{"to": ADDR, "data": data}, "latest"])], endpoint=ep, timeout=10)
        print("tokenURI(%d):" % tid, (dec_str(r[0]) or "")[:600])
    except Exception as e:
        print("tokenURI(%d) ERR:" % tid, str(e)[:150])
