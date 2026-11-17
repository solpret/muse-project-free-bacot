#!/usr/bin/env python3
"""bobbie-listing-watch read — fresh on-chain state for BOBBIE #4023 listing watch.
Read-only: NFT saleFinalized/cancelled/ownerOf(4023); market paused/listings(4023).
Single calls (no batch) to avoid the fast_rpc.batch revert quirk."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from Crypto.Hash import keccak

NFT = "0x3BF121dC4c5a1Ba567F3eE801d0e447601726207"
MARKET = "0xfA239D919Db60E1b497E9E8CA26CA79689a180AF"
AGENT = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TOKEN_ID = 4023

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def call(to, data):
    return race("eth_call", [{"to": to, "data": data}, "latest"])

def u256(v):
    return "0x" + format(v, "064x")

def read(name, to, data):
    try:
        res = call(to, data)
        if isinstance(res, str) and res.startswith("0x"):
            return res
        return ("ERR", res)
    except Exception as e:
        return ("EXC", str(e))

out = {}
out["saleFinalized"] = read("saleFinalized", NFT, sel("saleFinalized()"))
out["cancelled"] = read("cancelled", NFT, sel("cancelled()"))
out["ownerOf4023"] = read("ownerOf", NFT, sel("ownerOf(uint256)") + u256(TOKEN_ID)[2:])
out["marketPaused"] = read("paused", MARKET, sel("paused()"))
out["listings4023"] = read("listings", MARKET, sel("listings(uint256)") + u256(TOKEN_ID)[2:])
out["blockNumber"] = race("eth_blockNumber", [])

def parse_bool(v):
    if isinstance(v, str) and v.startswith("0x") and len(v) >= 66:
        return int(v, 16) != 0
    return v

def parse_addr(v):
    if isinstance(v, str) and v.startswith("0x") and len(v) >= 66:
        return "0x" + v[-40:]
    return v

summary = {
    "saleFinalized": parse_bool(out["saleFinalized"]),
    "cancelled": parse_bool(out["cancelled"]),
    "ownerOf4023": parse_addr(out["ownerOf4023"]),
    "marketPaused": parse_bool(out["marketPaused"]),
    "listings4023_raw": out["listings4023"],
    "blockNumber": int(out["blockNumber"], 16) if isinstance(out["blockNumber"], str) and out["blockNumber"].startswith("0x") else out["blockNumber"],
}
# listings returns (seller, price, version, benefits, ownershipVersion) = 5 x 32 bytes
raw = out["listings4023"]
if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 2 + 64 * 5:
    words = [raw[2 + i * 64: 2 + (i + 1) * 64] for i in range(5)]
    summary["listings4023"] = {
        "seller": "0x" + words[0][-40:],
        "price": int(words[1], 16),
        "version": int(words[2], 16),
        "benefits": int(words[3], 16),
        "ownershipVersion": int(words[4], 16),
    }
else:
    summary["listings4023"] = None

print(json.dumps(summary, indent=2))
