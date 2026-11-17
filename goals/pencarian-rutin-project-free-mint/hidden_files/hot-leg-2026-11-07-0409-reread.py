#!/usr/bin/env python3
"""Hot-leg run 2026-11-07 04:09 WIB. Leg 4 targeted fresh probe (read-only).
Re-reads change-sensitive snapshot items only. Never writes snapshot."""
import json, urllib.request, time, subprocess
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-07-0409"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed2.bnbchain.org"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
DEADLINE = time.time() + 90

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(to, data):
    for rpc in RPCS:
        if time.time() > DEADLINE:
            return "deadline"
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None

def call(to, sig, args=""): return raw(to, sel(sig) + args)

def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None

NFT_VIEWS = ["totalSupply()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
             "balanceOf(address)", "mintedBy(address)", "freeUsed(address)",
             "claimedFree(address)", "mintOpen()"]
SALE_VIEWS = ["freeClaimed()", "freeSharesRemaining()", "freeLeft(address)",
              "quote(address,uint256)", "mintedBy(address)", "mintOpen()",
              "totalMinted()", "freeMinted()", "totalSupply()"]

ITEMS = {
 "Agent Frogs": ("0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31", NFT_VIEWS),
 "Thronemind": ("0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90", NFT_VIEWS),
 "Hashseers": ("0x7E634ED532a7b7b781262A0d4220ac3c3Ba6B688", NFT_VIEWS),
 "Layerloom": ("0x1B72ceC52A74537b06F713FCebA0e491f53679aE", NFT_VIEWS),
 "Smeltbots": ("0xdC0004F3Efcc2aEA6052e138d3f1e680ca5D9b8e", NFT_VIEWS),
 "Tumblebots": ("0x02f10432EAf9CbF72e1aC9b9208af601aADd6b17", NFT_VIEWS),
 "Forklings": ("0xD7B3FD33e0b465B0e374906F60567D317b758FD8", NFT_VIEWS),
 "Neurolucha": ("0x56eBED63452Bb02B975ceE02949DA3C02466725b", NFT_VIEWS),
 "Driftnauts": ("0x6a926234D3767F2EEb3DB12c1B4C9e2912C5589b", NFT_VIEWS),
 "BNB CACHE Server": ("0x1989058Da9eb7F36E69779fCda0EA04578528570", NFT_VIEWS),
 "KING Agent": ("0x2A2463d243E5c4dF850e48f350392AD23B494132", NFT_VIEWS),
 "MERGEBORN": ("0x348455be18b700cae8aa425bd84e456e47f16e8b", NFT_VIEWS),
 "DeY": ("0xDB062c12bF0a14227e7Fe896a988950b050B51C1", SALE_VIEWS),
 "FANBEIMAO-824d": ("0x824d1e5c1395ed7543854fCd9e4da6D3F358De16", SALE_VIEWS),
 "LuckyBox-LUCK": ("0xd08ef372B52C29255fEd7004f59bF41571451894", SALE_VIEWS),
 "NJAR": ("0x816458b734d17d59058762deaadd9b952bad6985", SALE_VIEWS),
 "Predictagent-PRDICT": ("0x8fF4bd65584882324c44Ee794a23E7791820189b", SALE_VIEWS),
 "CLEPSYDRA": ("0x9e2738B3DD3773c6c71cA24Fbc92660B501C0B6b", SALE_VIEWS),
 "BOMB-sale": ("0xC3f847430D660e5AAbE8D4b2B5792d6Fcbb171F9", SALE_VIEWS),
 "Wuyuhive": ("0x250e800025a9a7861970e253bab6975a57f80567", NFT_VIEWS),
 "Orchidia": ("0x09bcdd97186f6f37521bd1b281d329e48ac54b89", NFT_VIEWS),
}

def read_item(args):
    name, (addr, views) = args
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
    print(name, d, flush=True)
    return name, d

blk = block()
print("BLOCK", blk, flush=True)
t0 = time.time()
out = {"block": blk, "reread": {}}
with ThreadPoolExecutor(max_workers=10) as ex:
    for name, d in ex.map(read_item, list(ITEMS.items())):
        out["reread"][name] = d
        json.dump(out, open(f"{BASE}/hot-leg-{TS}-reread.json", "w"), indent=1)
print("DONE in %.1fs block %s" % (time.time() - t0, blk), flush=True)
