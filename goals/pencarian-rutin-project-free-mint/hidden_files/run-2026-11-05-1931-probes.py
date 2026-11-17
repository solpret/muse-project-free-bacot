#!/usr/bin/env python3
"""Run 1931 extra probes (read-only): AgentGlyph owner() [gate method E],
BINANCEAI launched/refund/failed [track-B terminal confirm]."""
import json, urllib.request
from Crypto.Hash import keccak
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
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
def call(to, sig, args=""):
    v = raw(to, sel(sig) + args)
    if v is None: return None
    try: return int(v, 16)
    except Exception: return v
def addr_of(v):
    if v and len(v) >= 42: return "0x" + v[-40:]
    return v
out = {}
out["AgentGlyph_owner"] = addr_of(raw("0x3ef2A97Abf2E43182eACAe323B82d2CAC2132C6A", sel("owner()")))
out["AgentGlyph_deployer_note"] = "owner() read for gate method E (deployer-group check)"
B = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
out["BINANCEAI_launched"] = call(B, "launched()")
out["BINANCEAI_isRefundPhase"] = call(B, "isRefundPhase()")
out["BINANCEAI_failed"] = call(B, "failed()")
out["BINANCEAI_tokenClaimed_user"] = call(B, "tokenClaimed(address)", enc(USER))
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-05-1931-probes.json", "w"), indent=1)
