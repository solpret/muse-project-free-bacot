#!/usr/bin/env python3
"""Hot-leg leg-4 priority re-read, run 2026-11-08 00:04 WIB. Single-call reads only
(LEAN; fast_rpc.batch whole-batch-revert quirk). Read-only; never writes snapshot."""
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def single(addr, sig, args=None):
    data = sel(sig)
    if args:
        for a in args:
            data += enc_addr(a) if isinstance(a, str) and a.startswith("0x") else enc_u(a)
    for ep in EPS:
        try:
            res = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=8)
            return to_int(res[0])
        except Exception:
            continue
    return None
ITEMS = {
 "Tri333": ("0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f", ["freeMinted()","FREE_CAP()","freeCount(address)","mintOpen()","balanceOf(address)"]),
 "WAR3": ("0x1Aa9797cC762b838388566Daa45A56b1709F4Bbe", ["freeMinted()","totalSupply()","balanceOf(address)"]),
 "HUNT PASS": ("0x885128Cf234c768F1353e2C1432D55873C6b67dD", ["totalMinted()","FREE_SUPPLY()","freeMinted()","balanceOf(address)","mintedBy(address)"]),
 "fab7-variant": ("0xfab7dd20e8816e10227C1222bd4Bd446FecF1B72", ["freeMinted()","FREE_SHARES()","totalMinted()","finalized()"]),
 "DinoAgent": ("0xcE19D6A5FF15e088D4bf23614242927139084895", ["freeMinted()","FREE_SUPPLY()","freeClaimed(address)"]),
 "LOCKSMITH": ("0x05e8738290be6639fD0f7236ebF444E5466D3164", ["totalMinted()","freeMintedTotal()","FREE_CAP()","mintActive()"]),
 "HOG ORBIT": ("0x7bc0b487febcbb1caa781148bf05a8cd72d02ec5", ["freeLeft()","totalSupply()","balanceOf(address)"]),
 "AgentBook": ("0xEECaCBE6eAC6D6F2a38e8daA9049C7AA08aD43b0", ["FREE_QUOTA()","remainingFree()"]),
 "Night Bandits Club": ("0xa849aEd9dC19FBA823CcEf1FA01BdA72Fbb8fcDf", ["freeUsed()","freeTakenBy(address)"]),
 "Ink Koi": ("0xbd4B4e7189ae9356514664146b0eD683601200A9", ["freeMinted()","freeClaimed(address)"]),
 "AURISLE": ("0xC52a979C20C5a43e5Be4Ffa6d1A4DD50069D5E2D", ["freeMinted()","FREE_SUPPLY()","freeClaimed(address)"]),
 "CipherAgent": ("0x158b5e25015758a94703A27c152889451E5d52E5", ["totalMints()","mintOpen()","balanceOf(address)"]),
 "MarsAgent": ("0x2231FdAe405c33dc4993f8C577c453802FF1AcE9", ["totalMints()","mintOpen()","balanceOf(address)"]),
 "OnlyAI": ("0x156482ad3f0eebd8e3f70d494ebd1da3f738f5ba", ["totalSupply()","balanceOf(address)"]),
 "Gloops": ("0x183CBb52B3C7BCB2433d50dE0Add99B59f4DE4fE", ["totalMinted()","mintOpen()"]),
 "Saturnagent": ("0xef870a9b4a529373fb2e174b59ca7a66eb018074", ["freeClaimed()","quote(address,uint256)"]),
 "Lumenhold": ("0x9701980b0afd825134390ee46fb3bd675a2f356f", ["freeClaimed()","quote(address,uint256)"]),
}
def read_item(item):
    name, (addr, views) = item
    d = {"address": addr}
    for sig in views:
        base = sig.split("(")[0]
        if "(address)" in sig:
            key = base + "_user"; v = single(addr, sig, [USER])
        elif sig == "quote(address,uint256)":
            key = "quote_user1"; v = single(addr, sig, [USER, 1])
        else:
            key = base; v = single(addr, sig)
        d[key] = v
    return name, d
try:
    b = batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=8)
    block = int(b[0], 16)
except Exception as e:
    block = None
    print("BLOCK-FAIL", e, flush=True)
out = {"block": block, "items": {}}
t0 = time.time()
with ThreadPoolExecutor(max_workers=8) as ex:
    for name, d in ex.map(read_item, ITEMS.items()):
        out["items"][name] = d
out["duration_sec"] = round(time.time() - t0, 1)
json.dump(out, open(f"{BASE}/hot-leg-2026-11-08-0004-reread.json", "w"), indent=1)
print("BLOCK", block, "DUR", out["duration_sec"])
print(json.dumps(out["items"], indent=1))
