#!/usr/bin/env python3
"""Fetch full contractURI for both AngelEye forges, decode base64 JSON. Read-only."""
import json, subprocess, base64
from Crypto.Hash import keccak
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def call(addr, sig):
    data = sel(sig)
    for ep in EPS:
        try:
            out = subprocess.run(["curl", "-sL", "--max-time", "45", "-X", "POST", ep,
                "-H", "Content-Type: application/json",
                "-d", json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call",
                    "params":[{"to":addr,"data":data},"latest"]})],
                capture_output=True, text=True, timeout=50).stdout
            r = json.loads(out)
            if isinstance(r, dict) and r.get("result") not in (None, "0x"):
                return r["result"]
        except Exception:
            continue
    return None
def decode_str(raw):
    # ABI string: offset(32B) + len(32B) + data
    b = bytes.fromhex(raw[2:])
    ln = int.from_bytes(b[32:64], "big")
    s = b[64:64+ln].decode("utf-8", "replace")
    return s
for name, addr in [("AngelEye-77D9","0x77D98247BA3dDAfa9ffBceA1F13d3e4cFe3f2d4C"),
                   ("AngelEye-07bD","0x07bD6DbbEf508ad83BA2C557ED979732488894A1")]:
    raw = call(addr, "contractURI()")
    if not raw:
        print(name, "contractURI: NO RESULT"); continue
    s = decode_str(raw)
    print(name, "contractURI raw:", s[:200])
    if s.startswith("data:application/json;base64,"):
        j = json.loads(base64.b64decode(s.split(",",1)[1]))
        print(name, "DECODED JSON:", json.dumps(j, indent=1))
    else:
        print(name, "NOT base64-json")
