#!/usr/bin/env python3
"""Post-mint verification for 6 strong-lead direct mints, run 2026-11-02 09:01 WIB."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def rpc(method, params):
    for ep in EPS:
        try: return _single(ep, method, params, 8, retries=0)
        except Exception as e: err = str(e)[:160]
    return None
def call(to, data):
    v = rpc("eth_call", [{"to": to, "data": data}, "latest"])
    try: return int(v, 16) if v else None, v
    except Exception: return None, v
TARGETS = {
 "Lensorb": ("0x1edfd1e6c6b132e88f5b09b1dbe025037b5b0539", "0xf12fc0668575cd3c8f0bdff8b11b4e6d17cd6c55844da82b8de6905d0f631c16", 392),
 "Hotpotsage": ("0xEbAdb5Be9692b0BF25E8A5F3351C35DdC58f195d", "0xfc616ac93769d5af2e03682f8990f9eeae778d6913d171c72aee910542eb1fa8", 398),
 "Plutopop": ("0xE4cA7AaA82253717C0d897C10d58D59821631509", "0x29ce300d774d3b3cf883e96cc2b245a8740799948392116753d83865dcc27acc", 516),
 "Ghoulipop": ("0xb2d236EC0473792eC6727e5bf41084Df3eA0137F", "0xe07caf6101faf4e253b5191016f95580320882ba87a9101256f168350c2f976d", 537),
 "Servobun": ("0xbd297cb5158F4DcA02C336A59556FDBfa6609A70", "0x9a0d81f9f34aef7c03146625f7422d89414bc74c0dfa6128977451a1dca33483", 516),
 "Xianyulo": ("0x5bF46eF8E5e09fFFfd928e30077b4d4674CBA4b0", "0xbb26fc50eb20f4cf9816da860aa12f253e549eeb4e7d798145bbd59fe5ed0e64", 507),
}
out = {}
for name, (addr, tx, sim) in TARGETS.items():
    receipt = None
    for _ in range(24):
        receipt = rpc("eth_getTransactionReceipt", [tx])
        if receipt: break
        time.sleep(5)
    d = {"tx": tx, "receipt": receipt}
    if receipt:
        logs = receipt.get("logs", [])
        d["receipt_status"] = receipt.get("status")
        d["blockNumber"] = int(receipt["blockNumber"], 16) if receipt.get("blockNumber") else None
        d["gasUsed"] = int(receipt["gasUsed"], 16) if receipt.get("gasUsed") else None
        # Transfer log tokenId
        for lg in logs:
            if len(lg.get("topics", [])) >= 4:
                try: d["receipt_tokenId"] = int(lg["topics"][3], 16)
                except Exception: pass
    owner, _ = call(addr, sel("ownerOf(uint256)") + enc_uint(sim)[2:])
    # ownerOf returns address in last 40 hex chars
    v = rpc("eth_call", [{"to": addr, "data": sel("ownerOf(uint256)") + enc_uint(sim)[2:]}, "latest"])
    d["ownerOf_sim"] = ("0x" + v[-40:]) if v else None
    for fn, arg in [("totalSupply()", ""), ("freeClaimed()", ""), ("mintedBy(address)", enc_addr(USER)[2:]),
                    ("freeUsed(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])]:
        iv, _ = call(addr, sel(fn) + arg); d[fn] = iv
    uri = rpc("eth_call", [{"to": addr, "data": sel("tokenURI(uint256)") + enc_uint(sim)[2:]}, "latest"])
    d["tokenURI_raw"] = uri
    out[name] = d
    print(name, json.dumps({k: v for k, v in d.items() if k != "receipt"}, indent=1)[:1500])
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0901-verify.json", "w"), indent=1)
