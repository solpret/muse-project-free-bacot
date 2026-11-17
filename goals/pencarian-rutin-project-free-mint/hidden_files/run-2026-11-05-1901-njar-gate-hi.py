#!/usr/bin/env python3
"""NJAR gate methods (H) contractURI + (I) tokenURI, run 1901. Read-only."""
import json, urllib.request, base64
from Crypto.Hash import keccak
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]
SALE = "0x816458b734d17d59058762deaadd9b952bad6985"
TOKEN = "0x0b0b8df4d7df0b2cdd00877b476a447a8a1824ee"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def raw(to, data):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: out = json.load(r)
            if "error" in out: return None
            v = out["result"]
            if not v or v == "0x": return None
            return v
        except Exception:
            continue
    return None
def decode_str(v):
    """Decode ABI-encoded string return."""
    if not v or len(v) < 130: return None
    try:
        off = int(v[2:66], 16)
        ln = int(v[2+off*2:2+off*2+64], 16)
        data = bytes.fromhex(v[2+off*2+64:2+off*2+64+ln*2])
        return data.decode("utf-8", "replace")
    except Exception as e:
        return f"<decode-fail {e}>"
out = {}
for label, addr in [("sale", SALE), ("token", TOKEN)]:
    out[label+"_contractURI"] = decode_str(raw(addr, sel("contractURI()")))
    out[label+"_tokenURI_1"] = decode_str(raw(addr, sel("tokenURI(uint256)") + format(1, "064x")))
    out[label+"_uri"] = decode_str(raw(addr, sel("uri(uint256)") + format(1, "064x")))
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-05-1901-njar-gate-hi.json", "w"), indent=1)
