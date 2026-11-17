#!/usr/bin/env python3
"""Verify HOG ORBIT mint tx on-chain: receipt + ownership + free quota used."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
TX = "0x28f650d774144ce817d672a8fc377935e0f7d602b4134dd1b0669cc5e0d59b38"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x7bc0b487febcbb1caa781148bf05a8cd72d02ec5"
EP = "https://bsc-dataseed1.bnbchain.org/"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_int(n): return "%064x" % n
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
out = {"tx": TX}
for attempt in range(12):
    try:
        r = batch([("eth_getTransactionReceipt", [TX])], endpoint=EP, timeout=10)[0]
        if r:
            out["receipt"] = r
            break
    except Exception as e:
        out.setdefault("receipt_errors", []).append(str(e)[:100])
    time.sleep(10)
rec = out.get("receipt") or {}
print("status:", rec.get("status"), "block:", int(rec.get("blockNumber","0x0"),16) if rec.get("blockNumber") else None, "gasUsed:", int(rec.get("gasUsed","0x0"),16) if rec.get("gasUsed") else None)
def call(data):
    return batch([("eth_call", [{"to": ADDR, "data": data}, "latest"])], endpoint=EP, timeout=10)[0]
out["block_now"] = int(batch([("eth_blockNumber", [])], endpoint=EP, timeout=10)[0], 16)
out["totalSupply"] = to_int(call(sel("totalSupply()")))
out["freeLeft"] = to_int(call(sel("freeLeft()")))
out["balanceOf_user"] = to_int(call(sel("balanceOf(address)")+enc(USER)))
out["mintedBy_user"] = to_int(call(sel("mintedBy(address)")+enc(USER)))
out["ownerOf_421"] = "0x"+call(sel("ownerOf(uint256)")+enc_int(421))[-40:]
out["tokenURI_421"] = None
try:
    raw = call(sel("tokenURI(uint256)")+enc_int(421))
    b = bytes.fromhex(raw[2:]); ln = int.from_bytes(b[32:64], "big")
    out["tokenURI_421"] = b[64:64+ln].decode("utf-8", "replace")
except Exception as e:
    out["tokenURI_421_err"] = str(e)[:100]
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-08-0031-hog-verify.json", "w"), indent=1)
