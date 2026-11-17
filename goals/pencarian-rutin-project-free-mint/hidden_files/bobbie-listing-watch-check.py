#!/usr/bin/env python3
"""BOBBIE listing watch — fresh on-chain reads (read-only)."""
import json, urllib.request
from eth_hash.auto import keccak

NFT = "0x3BF121dC4c5a1Ba567F3eE801d0e447601726207"
MARKET = "0xfA239D919Db60E1b497E9E8CA26CA79689a180AF"
AGENT = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TOKEN = 4023

ENDPOINTS = [
    "https://bsc-dataseed.bnbchain.org/",
    "https://bsc.publicnode.com/",
    "https://bsc-dataseed3.bnbchain.org/",
    "https://bsc-dataseed1.bnbchain.org/",
    "https://bsc-dataseed2.bnbchain.org/",
    "https://bsc-dataseed4.bnbchain.org/",
    "https://bsc-dataseed.binance.org/",
    "https://bsc-mainnet.public.blastapi.io",
    "https://rpc.ankr.com/bsc",
]

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def enc_uint(n):
    return n.to_bytes(32, "big").hex()

def rpc(endpoint, method, params, rid):
    body = json.dumps({"jsonrpc": "2.0", "id": rid, "method": method, "params": params}).encode()
    req = urllib.request.Request(endpoint, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())

def eth_call(endpoint, to, data, rid):
    res = rpc(endpoint, "eth_call", [{"to": to, "data": data}, "latest"], rid)
    if "error" in res:
        raise RuntimeError(res["error"])
    return res["result"]

def main():
    calls = [
        ("saleFinalized", NFT, sel("saleFinalized()")),
        ("cancelled", NFT, sel("cancelled()")),
        ("ownerOf4023", NFT, sel("ownerOf(uint256)") + enc_uint(TOKEN)),
        ("marketPaused", MARKET, sel("paused()")),
        ("listings4023", MARKET, sel("listings(uint256)") + enc_uint(TOKEN)),
    ]
    last_err = None
    for ep in ENDPOINTS:
        try:
            out = {}
            for i, (name, to, data) in enumerate(calls):
                out[name] = eth_call(ep, to, data, i + 1)
            block = rpc(ep, "eth_blockNumber", [], 99)["result"]
            out["block_number"] = int(block, 16)
            out["endpoint_used"] = ep
            print(json.dumps(out, indent=2))
            return
        except Exception as e:
            last_err = e
            print(f"endpoint {ep} failed: {e}", flush=True)
    raise SystemExit(f"ALL endpoints failed, last: {last_err}")

if __name__ == "__main__":
    main()
