#!/usr/bin/env python3
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def ci(addr, sig, args=None):
    data = sel(sig)
    if args:
        for a in args: data += a
    for ep in ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/"]:
        try:
            r = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=10)
            return int(r[0], 16)
        except Exception: continue
    return None
out = {"wib": "2026-11-08 ~08:35 WIB"}
try:
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint="https://bsc-dataseed1.bnbchain.org/", timeout=10)[0], 16)
except Exception: out["block"] = None
for name, addr in [("hokipanda","0x4b61A7767dA68f18266907b2Eb7C9A1EE3d24517"),("hokikoi","0x74055b4Afe2d8c7347e8D4c0fc23e704405F7A36"),("dafeiyu","0xD8DE64ACB25A87D98F1E170BF082a01427772511")]:
    out[name] = {
        "totalMinted": ci(addr, "totalMinted()"),
        "totalSupply": ci(addr, "totalSupply()"),
        "freeMinted": ci(addr, "freeMinted()"),
        "mintOpen": ci(addr, "mintOpen()"),
        "freeCount_user": ci(addr, "freeCount(address)", [enc(USER)]),
        "balanceOf_user": ci(addr, "balanceOf(address)", [enc(USER)]),
    }
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-08-0801-hoki-final.json","w"), indent=1)
