#!/usr/bin/env python3
"""Fallback direct-urllib read for BOBBIE #4023 listing watch (read-only).
Used when fast_rpc race fails; tries dataseed endpoints one by one."""
import json, urllib.request

NFT = "0x3BF121dC4c5a1Ba567F3eE801d0e447601726207"
MARKET = "0xfA239D919Db60E1b497E9E8CA26CA79689a180AF"
TOKEN_ID = 4023

ENDPOINTS = [
    "https://bsc-dataseed3.bnbchain.org/",
    "https://bsc-dataseed1.bnbchain.org/",
    "https://bsc-dataseed.binance.org/",
    "https://bsc-dataseed2.bnbchain.org/",
    "https://bsc-dataseed4.bnbchain.org/",
]

from Crypto.Hash import keccak

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def u256(v):
    return format(v, "064x")

def eth_call(ep, to, data):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": to, "data": data}, "latest"]}).encode()
    req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

def eth_block(ep):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
    req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

CALLS = {
    "saleFinalized": (NFT, sel("saleFinalized()")),
    "cancelled": (NFT, sel("cancelled()")),
    "ownerOf4023": (NFT, sel("ownerOf(uint256)") + u256(TOKEN_ID)),
    "marketPaused": (MARKET, sel("paused()")),
    "listings4023": (MARKET, sel("listings(uint256)") + u256(TOKEN_ID)),
}

out, used = {}, None
for ep in ENDPOINTS:
    try:
        blk = eth_block(ep)
        if "result" not in blk:
            continue
        used = ep
        out["blockNumber"] = int(blk["result"], 16)
        for name, (to, data) in CALLS.items():
            res = eth_call(ep, to, data)
            out[name] = res.get("result") if "result" in res else ("ERR", res)
        break
    except Exception as e:
        print(f"{ep} failed: {e}", flush=True)
        continue

if not used:
    print("ALL_ENDPOINTS_FAILED")
    raise SystemExit(1)

def parse_bool(v):
    if isinstance(v, str) and v.startswith("0x") and len(v) >= 66:
        return int(v, 16) != 0
    return v

def parse_addr(v):
    if isinstance(v, str) and v.startswith("0x") and len(v) >= 66:
        return "0x" + v[-40:]
    return v

summary = {
    "endpoint": used,
    "saleFinalized": parse_bool(out["saleFinalized"]),
    "cancelled": parse_bool(out["cancelled"]),
    "ownerOf4023": parse_addr(out["ownerOf4023"]),
    "marketPaused": parse_bool(out["marketPaused"]),
    "blockNumber": out["blockNumber"],
}
raw = out["listings4023"]
if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 2 + 64 * 5:
    w = [raw[2 + i * 64: 2 + (i + 1) * 64] for i in range(5)]
    summary["listings4023"] = {
        "seller": "0x" + w[0][-40:],
        "price": int(w[1], 16),
        "version": int(w[2], 16),
        "benefits": int(w[3], 16),
        "ownershipVersion": int(w[4], 16),
    }
else:
    summary["listings4023"] = None
print(json.dumps(summary, indent=2))
