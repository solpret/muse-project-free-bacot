#!/usr/bin/env python3
"""BOBBIE listing watch — read-only fresh on-chain check (run 2026-11-09 22:33 WIB)."""
import json, urllib.request, sys

NFT = "0x3BF121dC4c5a1Ba567F3eE801d0e447601726207"
MARKET = "0xfA239D919Db60E1b497E9E8CA26CA79689a180AF"
AGENT = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TOKEN_ID = 4023

ENDPOINTS = [
    "https://bsc-dataseed1.bnbchain.org/",
    "https://bsc-dataseed2.bnbchain.org/",
    "https://bsc-dataseed3.bnbchain.org/",
    "https://bsc-dataseed4.bnbchain.org/",
    "https://bsc-dataseed.bnbchain.org/",
]

def rpc(endpoint, method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(endpoint, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)

def eth_call(endpoint, to, data):
    res = rpc(endpoint, "eth_call", [{"to": to, "data": data}, "latest"])
    if "error" in res:
        raise RuntimeError(res["error"])
    return res["result"]

def pad_uint(n):
    return n.to_bytes(32, "big").hex()

def parse_bool(hexstr):
    return int(hexstr, 16) != 0

def parse_addr(hexstr):
    return "0x" + hexstr[-40:]

def main():
    calls = [
        ("saleFinalized", NFT, "0xa5f0dea2"),
        ("cancelled", NFT, "0x9a82a09a"),
        ("ownerOf4023", NFT, "0x6352211e" + pad_uint(TOKEN_ID)),
        ("marketPaused", MARKET, "0x5c975abb"),
        ("listings4023", MARKET, "0xde74e57b" + pad_uint(TOKEN_ID)),
    ]
    last_err = None
    for ep in ENDPOINTS:
        try:
            block = int(rpc(ep, "eth_blockNumber", [])["result"], 16)
            out = {}
            for name, to, data in calls:
                out[name] = eth_call(ep, to, data)
            sf = parse_bool(out["saleFinalized"])
            cx = parse_bool(out["cancelled"])
            owner = parse_addr(out["ownerOf4023"])
            paused = parse_bool(out["marketPaused"])
            raw = out["listings4023"][2:]
            words = [raw[i:i+64] for i in range(0, len(raw), 64)]
            seller = "0x" + words[0][-40:]
            price = int(words[1], 16)
            version = int(words[2], 16)
            benefits = int(words[3], 16)
            own_ver = int(words[4], 16)
            result = {
                "agent_wallet": AGENT,
                "block_number": block,
                "cancelled": cx,
                "endpoint_used": f"urllib {ep}",
                "last_checked_wib": "2026-11-09 22:33 WIB",
                "listing_active": seller.lower() == AGENT.lower() and price == 7500000000000000,
                "listing_price_wei": 7500000000000000,
                "listings4023": {"benefits": benefits, "ownershipVersion": own_ver,
                                 "price": price, "seller": seller, "version": version},
                "market": MARKET,
                "marketPaused": paused,
                "nft": NFT,
                "notes": "",
                "ownerOf4023": owner,
                "owner_is_agent": owner.lower() == AGENT.lower(),
                "saleFinalized": sf,
                "token_id": TOKEN_ID,
            }
            print(json.dumps(result, indent=2))
            return result
        except Exception as e:
            last_err = e
            continue
    print(f"ALL ENDPOINTS FAILED: {last_err}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
