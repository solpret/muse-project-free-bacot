#!/usr/bin/env python3
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
HK = "0x74055b4Afe2d8c7347e8D4c0fc23e704405F7A36"
HP = "0x4b61A7767dA68f18266907b2Eb7C9A1EE3d24517"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_u(n): return str(n).rjust(64, "0")
def call(addr, sig, args=None):
    data = sel(sig)
    if args:
        for a in args: data += a
    for ep in ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/"]:
        try:
            r = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=10)
            return r[0]
        except Exception: continue
    return None
def call_str(addr, sig, args=None):
    raw = call(addr, sig, args)
    if not raw or raw == "0x": return None
    try:
        h = raw[2:]; ln = int(h[64:128], 16)
        return bytes.fromhex(h[128:128+ln*2]).decode("utf-8", "replace")
    except Exception: return raw
out = {
 "hokikoi_tokenURI_1": call_str(HK, "tokenURI(uint256)", [enc_u(1)]),
 "hokikoi_contractURI": call_str(HK, "contractURI()"),
 "hokipanda_contractURI": call_str(HP, "contractURI()"),
 "hokikoi_name": call_str(HK, "name()"),
}
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-08-0801-hokikoi-tokenuri.json", "w"), indent=1)
