#!/usr/bin/env python3
"""Probe 0x26Eb899cb65b8cd5A885C358abA9332F36fd84f8 (Sourcify ABI fetch failed
retry-exhausted): on-chain selector probe for S1/S2 sale-shape signals.
Read-only, 25s deadline."""
import json, urllib.request, time
from Crypto.Hash import keccak
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com", "https://bsc-dataseed2.bnbchain.org"]
ADDR = "0x26Eb899cb65b8cd5A885C358abA9332F36fd84f8"
DL = time.time() + 25
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def raw(data):
    for rpc in RPCS:
        if time.time() > DL: return "deadline"
        try:
            body = json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":ADDR,"data":data},"latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            return v
        except Exception: continue
    return None
SIGS = ["name()","symbol()","decimals()","totalSupply()","mintFree()","freeClaimed()","freeMinted()","freeClaimed(address)","FREE_SLOTS()","FREE_SUPPLY()","freeSharesRemaining()","freeLeft()","agentRegistry()","registry()","quote(address,uint256)","freeAvailable()"]
res = {}
for s in SIGS:
    v = raw(sel(s))
    res[s] = ("CALL-OK" if v not in (None,"deadline") else v)
    print(s, res[s], flush=True)
print(json.dumps(res))
