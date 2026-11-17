#!/usr/bin/env python3
"""BOBBIE listing watch — fresh on-chain reads (read-only).
Reads: NFT saleFinalized(), cancelled(), ownerOf(4023);
       Market paused(), listings(4023).
Method: fast_rpc batch race first; fallback direct curl to bsc-dataseed.
Usage: python3 bobbie-check.py
Output: JSON on stdout.
"""
import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from Crypto.Hash import keccak

NFT = "0x3BF121dC4c5a1Ba567F3eE801d0e447601726207"
MKT = "0xfA239D919Db60E1b497E9E8CA26CA79689a180AF"
AGENT = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TOKEN_ID = 4023

def sel(sig):
    k = keccak.new(digest_bits=256)
    k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def enc_uint(n):
    return format(n, "064x")

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

CALLS = [
    ("saleFinalized", NFT, sel("saleFinalized()")),
    ("cancelled", NFT, sel("cancelled()")),
    ("ownerOf4023", NFT, sel("ownerOf(uint256)") + enc_uint(TOKEN_ID)),
    ("marketPaused", MKT, sel("paused()")),
    ("listings4023", MKT, sel("listings(uint256)") + enc_uint(TOKEN_ID)),
]

def decode_bool(hexdata):
    return int(hexdata[-64:], 16) != 0

def decode_addr(hexdata):
    return "0x" + hexdata[-40:]

def decode_listings(hexdata):
    h = hexdata[2:] if hexdata.startswith("0x") else hexdata
    words = [h[i:i+64] for i in range(0, min(len(h), 320), 64)]
    seller = "0x" + words[0][-40:] if len(words) > 0 else None
    price = int(words[1], 16) if len(words) > 1 else None
    version = int(words[2], 16) if len(words) > 2 else None
    return {"seller": seller, "price": price, "version": version,
            "raw_words": len(words)}

def read_via_fast_rpc():
    from fast_rpc import call_many, race
    items = [(to, data) for _, to, data in CALLS]
    res = call_many(items)
    block = race("eth_blockNumber", [])
    out = {"method": "fast_rpc", "block_number": int(block, 16)}
    for (name, _, _), r in zip(CALLS, res):
        out[name] = r
    return out

def read_via_curl():
    import subprocess
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (_, to, data) in enumerate(CALLS)]
    payload.append({"jsonrpc": "2.0", "id": 99, "method": "eth_blockNumber",
                    "params": []})
    req = urllib.request.Request(
        "https://bsc-dataseed.binance.org/",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = json.loads(resp.read())
    by_id = {r["id"]: r.get("result") for r in raw if "result" in r}
    out = {"method": "curl-dataseed", "block_number": int(by_id[99], 16)}
    for i, (name, _, _) in enumerate(CALLS):
        out[name] = by_id[i + 1]
    return out

def main():
    try:
        raw = read_via_fast_rpc()
    except Exception as e:
        print(f"fast_rpc failed ({e}), falling back to direct curl",
              file=sys.stderr)
        raw = read_via_curl()
    result = {
        "method": raw["method"],
        "block_number": raw["block_number"],
        "saleFinalized": decode_bool(raw["saleFinalized"]),
        "cancelled": decode_bool(raw["cancelled"]),
        "ownerOf4023": decode_addr(raw["ownerOf4023"]),
        "marketPaused": decode_bool(raw["marketPaused"]),
        "listings4023": decode_listings(raw["listings4023"]),
        "owner_is_agent": decode_addr(raw["ownerOf4023"]).lower() == AGENT.lower(),
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
