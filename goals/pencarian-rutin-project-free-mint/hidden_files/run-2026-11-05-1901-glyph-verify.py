#!/usr/bin/env python3
"""AgentGlyph fresh verification run 1901 (parent). Read-only."""
import json, urllib.request, datetime
from Crypto.Hash import keccak
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
G = "0x3ef2A97Abf2E43182eACAe323B82d2CAC2132C6A"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
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
def call_addr(to, sig, args=""):
    v = raw(to, sel(sig) + args)
    if v is None: return None
    try: return "0x" + v[-40:]
    except Exception: return v
def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None
blk = block()
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
out = {"block": blk, "now_wib": now.strftime("%Y-%m-%d %H:%M:%S")}
out["AGENT_ID"] = call_addr(G, "AGENT_ID()")
out["FREE_SUPPLY"] = call(G, "FREE_SUPPLY()")
out["freeClaimed"] = call(G, "freeClaimed()")
out["totalSupply"] = call(G, "totalSupply()")
out["MAX_SUPPLY"] = call(G, "MAX_SUPPLY()")
out["PRICE"] = call(G, "PRICE()")
out["mintOpen"] = call(G, "mintOpen()")
out["mintedBy_user"] = call(G, "mintedBy(address)", enc(USER))
out["freeUsed_user"] = call(G, "freeUsed(address)", enc(USER))
out["quote_user_1"] = call(G, "quote(address,uint256)", enc(USER) + enc_uint(1))
out["freeLeft_user"] = call(G, "freeLeft(address)", enc(USER))
out["freeFor_user_1"] = call(G, "freeFor(address,uint256)", enc(USER) + enc_uint(1))
out["balanceOf_user"] = call(G, "balanceOf(address)", enc(USER))
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-05-1901-glyph-verify.json", "w"), indent=1)
