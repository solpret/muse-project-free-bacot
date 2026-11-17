#!/usr/bin/env python3
"""Run 2331 targeted retries: BA sellout confirm, Mossminds freeMinted,
Snail Mail price(), Jolly supply. Read-only, 3 RPCs, retries."""
import json, urllib.request, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed2.bnbchain.org"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(to, data, tries=3):
    for _ in range(tries):
        for rpc in RPCS:
            try:
                body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                   "params": [{"to": to, "data": data}, "latest"]}).encode()
                req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=8) as r: out = json.load(r)
                if "error" in out: continue
                v = out["result"]
                if not v or v == "0x": continue
                try: return int(v, 16)
                except Exception: return v
            except Exception:
                continue
    return None

def call(to, sig, args=""): return raw(to, sel(sig) + args)

BA = "0xE3a382B8e577A58A5540420C11ABa287C62e49f4"
MOSS = "0x5b49B06a2E25FcE0BCa865Be70F3C62b6319367a"
SNAIL = "0xb773e52fE45196c840F8e59c3B4bB944633Ae03a"
JOLLY = "0xdc11764a5664e333c8d303eb465e89a1caadb85b"

out = {}
out["Binance Agent"] = {
    "freeMinted": call(BA, "freeMinted()"),
    "totalMinted": call(BA, "totalMinted()"),
    "totalSupply": call(BA, "totalSupply()"),
    "paidMinted": call(BA, "paidMinted()"),
    "PRICE": call(BA, "PRICE()"),
    "mintOpen": call(BA, "mintOpen()"),
    "FREE_SUPPLY": call(BA, "FREE_SUPPLY()"),
}
out["Mossminds"] = {
    "freeMinted": call(MOSS, "freeMinted()"),
    "totalSupply": call(MOSS, "totalSupply()"),
    "canFreeMint_user": call(MOSS, "canFreeMint(address)", enc(USER)),
    "claimedFree_user": call(MOSS, "claimedFree(address)", enc(USER)),
    "mintedBy_user": call(MOSS, "mintedBy(address)", enc(USER)),
    "freeUsed_user": call(MOSS, "freeUsed(address)", enc(USER)),
    "quote_user_1": call(MOSS, "quote(address,uint256)", enc(USER) + enc_uint(1)),
}
out["Snail Mail"] = {
    "price": call(SNAIL, "price()"),
    "costOf_user_1": call(SNAIL, "costOf(address,uint256)", enc(USER) + enc_uint(1)),
    "totalSupply": call(SNAIL, "totalSupply()"),
    "mintOpen": call(SNAIL, "mintOpen()"),
}
out["Jolly"] = {
    "totalSupply": call(JOLLY, "totalSupply()"),
    "totalMinted": call(JOLLY, "totalMinted()"),
    "freeMinted": call(JOLLY, "freeMinted()"),
}
print(json.dumps(out, indent=1))
json.dump(out, open(f"{BASE}/run-2026-11-05-2331-retries.json", "w"), indent=1)
