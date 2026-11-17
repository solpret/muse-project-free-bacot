#!/usr/bin/env python3
"""Run 105 pair retry (read-only): token0/token1 for persistently unreadable pairs."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
import fast_rpc
import ankr as ankr_mod
from Crypto.Hash import keccak
def sel4(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def read_addr(addr, sig):
    try:
        r = fast_rpc.race("eth_call", [{"to": addr, "data": sel4(sig)}, "latest"])
    except Exception as e:
        return f"fast_rpc ERROR:{e}"
    if not isinstance(r, str):
        return f"raw:{r}"
    try:
        return "0x" + r[-40:]
    except Exception:
        return f"raw:{r[:80]}"
PAIRS = {
 "a6e6 0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da": "0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da",
 "887c 0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97": "0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97",
 "2bfb 0x782671f637bf1a01de482824c4b2520bc58a5a4b": "0x782671f637bf1a01de482824c4b2520bc58a5a4b",
 "c459 0xeca06856c88fcdf1506886431a079d3f2565ca82": "0xeca06856c88fcdf1506886431a079d3f2565ca82",
 "43c8 0xaafebb5244e2e546f7cd18a2c89f85bbee03f1e0": "0xaafebb5244e2e546f7cd18a2c89f85bbee03f1e0",
 "cfdb 0x1e04925db4eabab2917ef73a8cdf232bcc69b5ba": "0x1e04925db4eabab2917ef73a8cdf232bcc69b5ba",
 "0cf8 0xf6800c4a1ecdffbd64f9047c606bdb32dee0127f": "0xf6800c4a1ecdffbd64f9047c606bdb32dee0127f",
 "e68b 0xfab7cb4979c9e4738afc61e4974177cf72c50896": "0xfab7cb4979c9e4738afc61e4974177cf72c50896",
 "7809 0xfaba06b92f8e425055417fac8388dedf1cd58a72": "0xfaba06b92f8e425055417fac8388dedf1cd58a72",
 "7f0a 0x25a1bf1d836ba5865d9ba1dfaea33c33ad06c754": "0x25a1bf1d836ba5865d9ba1dfaea33c33ad06c754",
 "f3bd 0xbf243f454ac1463f2b596d9843026299e0ea5e31": "0xbf243f454ac1463f2b596d9843026299e0ea5e31",
 "8b19 0xf7a2396852111ed1480d4ffca583696369c87eab": "0xf7a2396852111ed1480d4ffca583696369c87eab",
 "d826 0x2315f44831bcac27bd7308e2d50943b4f115f4bd": "0x2315f44831bcac27bd7308e2d50943b4f115f4bd",
 "07b2 0x39f0227ba7aa712db15bdb51046647e8f0939b54": "0x39f0227ba7aa712db15bdb51046647e8f0939b54",
 "4263 0x70b31f93bff68d87ccd7b11c4458af5a7deb8d44": "0x70b31f93bff68d87ccd7b11c4458af5a7deb8d44",
}
out = {}
for label, pair in PAIRS.items():
    t0 = read_addr(pair, "token0()")
    t1 = read_addr(pair, "token1()")
    out[label] = {"token0": t0, "token1": t1}
    print(label, "token0", t0, "token1", t1, flush=True)
json.dump(out, open("/home/hatch/workspace/narrative-pulse/scan-runs/run105-pair-retry.json", "w"), indent=1)
print("saved run105-pair-retry.json")
