#!/usr/bin/env python3
"""NJAR fresh probe run 1901. Read-only."""
import json, urllib.request
from Crypto.Hash import keccak
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SALE = "0x816458b734d17d59058762deaadd9b952bad6985"
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
def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None
blk = block()
out = {"block": blk}
out["giftsClaimed"] = call(SALE, "giftsClaimed()")
out["GIFT_SHARES"] = call(SALE, "GIFT_SHARES()")
out["live"] = call(SALE, "live()")
out["poolOpen"] = call(SALE, "poolOpen()")
out["saleStart"] = call(SALE, "saleStart()")
out["fillDeadline"] = call(SALE, "fillDeadline()")
out["paidSharesSold"] = call(SALE, "paidSharesSold()")
out["TOKENS_PER_SHARE"] = call(SALE, "TOKENS_PER_SHARE()")
# agentIdOf(address) returns tuple (uint256,bool) -> raw hex
raw_agent = raw(SALE, sel("agentIdOf(address)") + enc(USER))
out["agentIdOf_raw"] = raw_agent
if raw_agent and len(raw_agent) >= 130:
    agent_id = int(raw_agent[2:66], 16)
    out["agentId"] = agent_id
    out["hasAgent"] = int(raw_agent[66:130], 16)
    out["giftTaken_agentId"] = call(SALE, "giftTaken(uint256)", enc_uint(agent_id))
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-05-1901-njar-probe.json", "w"), indent=1)
