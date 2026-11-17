#!/usr/bin/env python3
"""Hot-leg 0424 leg4 retry: deadline-hit items only, single fast RPC, minimal views."""
import json, time, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-07-0424"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed.binance.org", "https://bsc.publicnode.com", "https://bsc-dataseed1.bnbchain.org"]

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
            with urllib.request.urlopen(req, timeout=4) as r:
                o = json.load(r)
            if "error" in o:
                continue
            v = o.get("result")
            if not v or v == "0x":
                return None
            try:
                return int(v, 16)
            except Exception:
                return v
        except Exception:
            continue
    return "rpc-fail"

def call(to, sig, args=""): return raw(to, sel(sig) + args)

NFT = ["totalSupply()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
       "balanceOf(address)", "mintedBy(address)", "freeUsed(address)", "mintOpen()"]
SALE = ["freeLeft(address)", "quote(address,uint256)", "mintedBy(address)",
        "totalSupply()", "freeClaimed()", "freeSharesRemaining()", "mintOpen()"]
ITEMS = {
 "Wuyuhive": ("0x250e800025a9a7861970e253bab6975a57f80567", NFT),
 "Orchidia": ("0x09bcdd97186f6f37521bd1b281d329e48ac54b89", NFT),
 "KING Agent": ("0x2A2463d243E5c4dF850e48f350392AD23B494132", NFT),
 "MERGEBORN": ("0x348455be18b700cae8aa425bd84e456e47f16e8b", NFT),
 "BNB CACHE Server": ("0x1989058Da9eb7F36E69779fCda0EA04578528570", NFT),
 "Hashseers": ("0x7E634ED532a7b7b781262A0d4220ac3c3Ba6B688", NFT),
 "Layerloom": ("0x1B72ceC52A74537b06F713FCebA0e491f53679aE", NFT),
 "Smeltbots": ("0xdC0004F3Efcc2aEA6052e138d3f1e680ca5D9b8e", NFT),
 "Driftnauts": ("0x6a926234D3767F2EEb3DB12c1B4C9e2912C5589b", NFT),
 "DeY": ("0xDB062c12bF0a14227e7Fe896a988950b050B51C1", SALE),
 "FANBEIMAO-824d": ("0x824d1e5c1395ed7543854fCd9e4da6D3F358De16", SALE),
 "LuckyBox-LUCK": ("0xd08ef372B52C29255fEd7004f59bF41571451894", SALE),
 "NJAR": ("0x816458b734d17d59058762deaadd9b952bad6985", SALE),
 "Predictagent-PRDICT": ("0x8fF4bd65584882324c44Ee794a23E7791820189b", SALE),
 "CLEPSYDRA": ("0x9e2738B3DD3773c6c71cA24Fbc92660B501C0B6b", SALE),
 "BOMB-sale": ("0xC3f847430D660e5AAbE8D4b2B5792d6Fcbb171F9", SALE),
}
blk = None
for rpc in RPCS:
    try:
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
        req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=4) as r:
            blk = int(json.load(r)["result"], 16)
        break
    except Exception:
        continue
t0 = time.time()
out = {"block": blk, "retry": {}}
for name, (addr, views) in ITEMS.items():
    d = {"address": addr}
    for sig in views:
        key = sig.split("(")[0]
        if sig.startswith("quote("):
            v = call(addr, sig, enc(USER) + enc_uint(1)); key += "_user1"
        elif "address" in sig:
            v = call(addr, sig, enc(USER)); key += "_user"
        else:
            v = call(addr, sig)
        d[key] = v
    out["retry"][name] = d
    print(name, d, flush=True)
out["duration_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{BASE}/hot-leg-{TS}-reread-retry.json", "w"), indent=1)
print("DONE block", blk, "in %.1fs" % out["duration_s"])
