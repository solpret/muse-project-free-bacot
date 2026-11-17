#!/usr/bin/env python3
"""Raw owner()/contractURI() reads for the 4 agent-shaped hits, run 2026-11-14 0231.
Read-only. Prints raw hex; caller decodes strings."""
import json, subprocess, time
from Crypto.Hash import keccak
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
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
                return r["result"], ep
            if isinstance(r, dict) and "error" in r:
                return "ERR:"+str(r["error"].get("message","?")), ep
        except Exception as e:
            continue
    return None, None
ITEMS = {
 "AngelEye-77D9": "0x77D98247BA3dDAfa9ffBceA1F13d3e4cFe3f2d4C",
 "AbsurdAgentNFT-72C1": "0x72c14121681F1133545947B0735563835CC07B67",
 "NovaRemnants-38C1": "0x38C1695eb72B7522c8d6452a4CE27122532A0d69",
 "AngelEye-07bD": "0x07bD6DbbEf508ad83BA2C557ED979732488894A1",
}
for name, addr in ITEMS.items():
    o, ep1 = call(addr, "owner()")
    c, ep2 = call(addr, "contractURI()")
    print(name, "| owner:", o, "| contractURI:", (c[:400] if c else c), "| eps:", ep1, ep2)
