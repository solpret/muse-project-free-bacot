#!/usr/bin/env python3
"""Hot-leg 0534 leg-4 retry: parallel RPC re-read, fixed urllib import."""
import json, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-07-0534"
T0 = time.time()
DEADLINE = 90
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc-dataseed.binance.org",
        "https://bsc-dataseed1.defibit.io", "https://bsc-dataseed2.bnbchain.org"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]

def call(to, data, timeout=5):
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call",
                       "params":[{"to":to,"data":data},"latest"]}).encode()
    last = None
    for rpc in RPCS:
        try:
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                o = json.load(r)
            v = o.get("result")
            if not v or v == "0x" or "error" in o: return None
            try: return int(v, 16)
            except Exception: return v
        except Exception as e:
            last = f"err:{type(e).__name__}"
    return last

def block_number():
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
    for rpc in RPCS:
        try:
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=5) as r:
                return int(json.load(r)["result"], 16)
        except Exception: pass
    return None

ITEMS = {
 "KING Agent": ("0x2A2463d243E5c4dF850e48f350392AD23B494132", ["totalMinted()","remainingFree()","freeQuota()","mintOpen()"]),
 "MERGEBORN": ("0x348455be18b700cae8aa425bd84e456e47f16e8b", ["freeMinted()","FREE_CAP()","totalSupply()","freeClaimed()"]),
 "DeY": ("0xDB062c12bF0a14227e7Fe896a988950b050B51C1", ["totalSupply()","freeMinted()","FREE_SLOTS()","freeClaimed()"]),
 "FANBEIMAO-824d": ("0x824d1e5c1395ed7543854fCd9e4da6D3F358De16", ["totalSupply()","freeClaimed()","freeSharesRemaining()","freeAvailable()"]),
 "LuckyBox-LUCK": ("0xd08ef372B52C29255fEd7004f59bF41571451894", ["totalSupply()","freeMinted()","FREE_SUPPLY()","freeClaimed()"]),
 "NJAR": ("0x816458b734d17d59058762deaadd9b952bad6985", ["totalSupply()","freeClaimed()","freeSharesRemaining()","freeAvailable()"]),
 "Predictagent-PRDICT": ("0x8fF4bd65584882324c44Ee794a23E7791820189b", ["totalSupply()","freeMinted()","FREE_SLOTS()","freeClaimed()"]),
 "CLEPSYDRA": ("0x9e2738B3DD3773c6c71cA24Fbc92660B501C0B6b", ["totalSupply()","freeMinted()","FREE_SLOTS()","freeClaimed()"]),
 "Wuyuhive": ("0x250e800025a9a7861970e253bab6975a57f80567", ["totalSupply()","freeClaimed()","freeMinted()","FREE_SUPPLY()"]),
 "Orchidia": ("0x09bcdd97186f6f37521bd1b281d329e48ac54b89", ["totalSupply()","freeClaimed()","freeMinted()","FREE_SUPPLY()"]),
 "DigitalBomb-C3f8": ("0xC3f847430D660e5AAbE8D4b2B5792d6Fcbb171F9", ["totalSupply()","freeClaimed()","freeMinted()","FREE_SUPPLY()"]),
}
USER_PAD = "0x" + "0"*24 + USER[2:].lower()
blk = block_number()
print("block:", blk)

def read_one(args):
    name, (addr, views) = args
    d = {}
    for sig in views:
        if time.time() - T0 > DEADLINE:
            d[sig.split("(")[0]] = "deadline"; continue
        try: d[sig.split("(")[0]] = call(addr, sel(sig))
        except Exception as e: d[sig.split("(")[0]] = f"err:{type(e).__name__}"
    if time.time() - T0 <= DEADLINE:
        try: d["freeClaimed_user"] = call(addr, sel("freeClaimed(address)") + USER_PAD[2:])
        except Exception as e: d["freeClaimed_user"] = f"err:{type(e).__name__}"
    return name, d

reread = {}
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(read_one, it): it[0] for it in ITEMS.items()}
    for f in as_completed(futs):
        try:
            n, d = f.result(); reread[n] = d
        except Exception as e:
            reread[futs[f]] = {"error": str(e)}
out = {"block": blk, "leg4": reread, "duration_s": round(time.time()-T0, 1)}
for n, d in reread.items(): print(n, d)
json.dump(out, open(f"{BASE}/hot-leg-{TS}-reread-retry.json","w"), indent=1)
print("DONE", out["duration_s"])
