#!/usr/bin/env python3
"""Hot-leg run 2026-11-06 04:49 WIB. Leg 4: lean re-read snapshot (read-only) + leg 3 extras.
Same item set as run 2359 lean + Mossminds/Jolly/AgentGlyph/Pacture. Never writes snapshot."""
import json, urllib.request, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0509"
RPCS = ["https://bsc.publicnode.com", "https://bsc-dataseed.binance.org",
        "https://bsc-dataseed1.bnbchain.org"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

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
            with urllib.request.urlopen(req, timeout=3) as r: out = json.load(r)
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
            with urllib.request.urlopen(req, timeout=3) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None

NFT = {
 "HIVE Agents": ("0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "Mummyhive": ("0xf45fE22B3a9A748c59A7099e2E7B69f41216b1cd", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "Thronemind": ("0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "mintedBy(address)", "freeUsed(address)", "canFreeMint(address)", "claimedFree(address)", "quote(address,uint256)"]),
 "Hashseers": ("0x7E634ED532a7b7b781262A0d4220ac3c3Ba6B688", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "mintedBy(address)", "freeUsed(address)", "canFreeMint(address)", "claimedFree(address)", "quote(address,uint256)"]),
 "Smeltbots": ("0xdC0004F3Efcc2aEA6052e138d3f1e680ca5D9b8e", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "mintedBy(address)", "freeUsed(address)", "canFreeMint(address)", "claimedFree(address)", "quote(address,uint256)"]),
 "Forklings": ("0xD7B3FD33e0b465B0e374906F60567D317b758FD8", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "costOf(address,uint256)", "mintsLeft(address)", "mintOpen()", "mintedBy(address)", "price()"]),
 "Agent Frogs": ("0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "mintedBy(address)", "freeUsed(address)", "canFreeMint(address)", "claimedFree(address)", "quote(address,uint256)"]),
 "PassAgentX": ("0x08b1A979Dd997492EEcc010fe986eA2e2925e620", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "mintedBy(address)", "freeUsed(address)", "canFreeMint(address)", "claimedFree(address)", "quote(address,uint256)"]),
 "SEAT-f11e": ("0xf11e9405b23ca0f53e6135162a85545d780a3737", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "StarAgent-7d39": ("0x7d390e37Ed41A359f276D8764ca15432704B99b7", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "WAGagent": ("0x06a6f51D30556f4262e38485C09556fE81e6A984", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "LuckyBox-d08e": ("0xd08ef372B52C29255fEd7004f59bF41571451894", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "mintedBy(address)", "freeUsed(address)", "canFreeMint(address)", "claimedFree(address)", "quote(address,uint256)"]),
 "SnailMail": ("0xb773e52fE45196c840F8e59c3B4bB944633Ae03a", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "costOf(address,uint256)", "mintsLeft(address)", "mintOpen()", "mintedBy(address)", "price()"]),
 "wheelz": ("0x5aCC0Ec4449Edb788f43803cDb1A11f1f6b7E64d", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "costOf(address,uint256)", "mintsLeft(address)", "mintOpen()", "mintedBy(address)", "price()"]),
 "Layerloom": ("0x1B72ceC52A74537b06F713FCebA0e491f53679aE", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "Tumblebots": ("0x02f10432EAf9CbF72e1aC9b9208af601aADd6b17", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "Mossminds": ("0x5b49B06a2E25FcE0BCa865Be70F3C62b6319367a", ["totalSupply()", "freeMinted()", "canFreeMint(address)", "claimedFree(address)", "balanceOf(address)"]),
 "Jolly": ("0xdc11764a5664e333c8d303eb465e89a1caadb85b", ["totalSupply()", "totalMinted()", "freeMinted()", "balanceOf(address)"]),
 "AgentGlyph": ("0x3ef2a97abf2e43182eacae323b82d2cac2132c6a", ["freeClaimed()", "totalSupply()", "FREE_SUPPLY()"]),
 "Pacture": ("0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9", ["freeClaimed(address)", "totalMinted()", "freeMinted()", "balanceOf(address)"]),
}

TC = {
 "OSK": "0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37",
 "NIULAI": "0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF",
 "KillZero-K0-sale": "0x87ad9c1617ceb65f1b56f2ee06FE193F60aACF97",
 "DROID": "0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",
 "IMARS": "0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f",
 "ASOC-43cE": "0x43cEef9313CB8c4ca3757bA841C44DF40A223205",
 "SENBAZURU-b215": "0xb21583A08581278BcF925351a99C61A4562C62f0",
 "FABE": "0xB44AC34F6089B7c5c99CBc1643E22838e67C9D4d",
 "QAGENT-2": "0xE3a4f3099a2136e0e66202A665815caB8FFA2704",
 "ShibAgent-R2": "0x016a148e728b8d61b2440ed311946ac06d4b5648",
 "DeY": "0xDB062c12bF0a14227e7Fe896a988950b050B51C1",
 "BoxBigem-3Ee9": "0x3Ee92296D663378D42521273aAA4779BDa8e25dD",
 "FANBEIMAO-824d": "0x824d1e5c1395ed7543854fCd9e4da6D3F358De16",
 "SAFUAI": "0xbd6087fc30f2395344020cb190255c56cbc517bd",
}
TC_VIEWS = ["opened()", "launched()", "freeMinted()", "freeSharesRemaining()",
            "freeSharesClaimed(address)", "freeClaimed(address)", "hasFreeShare(address)",
            "totalMinted()", "sharesMinted()", "saleEnded()", "phase()"]

def read_item(args):
    name, addr, views = args
    d = {"address": addr}
    for sig in views:
        key = sig.split("(")[0]
        if "address" in sig and "uint256" in sig:
            v = call(addr, sig, enc(USER) + enc_uint(1))
            key += "_user_1"
        elif "address" in sig:
            v = call(addr, sig, enc(USER))
            key += "_user"
        else:
            v = call(addr, sig)
        d[key] = v
    print(name, d, flush=True)
    return name, d

jobs = []
for name, (addr, views) in NFT.items():
    jobs.append((name, addr, views))
for name, addr in TC.items():
    jobs.append((name, addr, TC_VIEWS))

blk = block()
print("BLOCK", blk, flush=True)
t0 = time.time()
out = {"block": blk, "reread": {}, "track_c": {}}
with ThreadPoolExecutor(max_workers=16) as ex:
    for name, d in ex.map(read_item, jobs):
        if name in NFT:
            out["reread"][name] = d
        else:
            out["track_c"][name] = d
        json.dump(out, open(f"{BASE}/run-{TS}-reread-lean.json", "w"), indent=1)
print("DONE in %.1fs block %s" % (time.time() - t0, blk), flush=True)

# Bridge (read-only)
try:
    br = json.load(open(f"{BASE}/scan-bridge.json"))
    cons = br.get("contracts", {})
    snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
    snap_text = json.dumps(snap)
    not_in_snap = [c for c in cons if c.lower() not in snap_text.lower()]
    discarded = [c for c, v in cons.items() if v.get("same_owner_discarded")]
    print("BRIDGE", len(cons), "discarded", len(discarded), "not_in_snapshot", len(not_in_snap), flush=True)
    json.dump({"total": len(cons), "discarded": len(discarded), "not_in_snapshot": len(not_in_snap),
               "not_in_snapshot_list": not_in_snap},
              open(f"{BASE}/hot-leg-{TS}-bridge.json", "w"), indent=1)
except Exception as e:
    print("BRIDGE-ERROR", e, flush=True)
