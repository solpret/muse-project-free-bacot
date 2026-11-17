#!/usr/bin/env python3
"""Run 2229 LEAN re-read (retry after full re-read died on RPC slowness).
Threaded, 5s timeout, 2 RPCs, minimal views, incremental JSON writes. Read-only."""
import json, urllib.request, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-05-2304"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]
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
            with urllib.request.urlopen(req, timeout=5) as r: out = json.load(r)
            if "error" in out: return None
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

NFT = [
 ("HIVE Agents", "0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77"),
 ("Mummyhive", "0xf45fE22B3a9A748c59A7099e2E7B69f41216b1cd"),
 ("Thronemind", "0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90"),
 ("Hashseers", "0x7E634ED532a7b7b781262A0d4220ac3c3Ba6B688"),
 ("Smeltbots", "0xdC0004F3Efcc2aEA6052e138d3f1e680ca5D9b8e"),
 ("Forklings", "0xD7B3FD33e0b465B0e374906F60567D317b758FD8"),
 ("Agent Frogs", "0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31"),
 ("PassAgentX", "0x08b1A979Dd997492EEcc010fe986eA2e2925e620"),
 ("SEAT-f11e", "0xf11e9405b23ca0f53e6135162a85545d780a3737"),
 ("StarAgent-7d39", "0x7d390e37Ed41A359f276D8764ca15432704B99b7"),
 ("WAGagent", "0x06a6f51D30556f4262e38485C09556fE81e6A984"),
 ("LuckyBox-d08e", "0xd08ef372B52C29255fEd7004f59bF41571451894"),
 ("SnailMail", "0xb773e52fE45196c840F8e59c3B4bB944633Ae03a"),
 ("wheelz", "0x5aCC0Ec4449Edb788f43803cDb1A11f1f6b7E64d"),
 ("Layerloom", "0x1B72ceC52A74537b06F713FCebA0e491f53679aE"),
 ("Tumblebots", "0x02f10432EAf9CbF72e1aC9b9208af601aADd6b17"),
]
COSTOF = {"DumpsterRoyalty","SIDEWAYS","Hoard","SlowSteady","MonkeBusiness","VeryGoodBoys","DoNotDisturb","MothClub","SnailMail","wheelz","Forklings"}
SLOT = {"Saturnode", "Thronemind", "Hashseers", "Smeltbots", "PassAgentX",
        "Agent Frogs", "Neurolucha", "Shroomies-2AE7", "DinoEra-b7ae", "LuckyBox-d08e"}

TC = [
 ("OSK", "0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37"),
 ("NIULAI", "0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF"),
 ("KillZero-K0-sale", "0x87ad9c1617ceb65f1b56f2ee06FE193F60aACF97"),
 ("DROID", "0xFcF6388DD3bcC674c095273aB479C7e54dd5E177"),
 ("IMARS", "0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f"),
 ("ASOC-43cE", "0x43cEef9313CB8c4ca3757bA841C44DF40A223205"),
 ("SENBAZURU-b215", "0xb21583A08581278BcF925351a99C61A4562C62f0"),
 ("FABE", "0xB44AC34F6089B7c5c99CBc1643E22838e67C9D4d"),
 ("QAGENT-2", "0xE3a4f3099a2136e0e66202A665815caB8FFA2704"),
 ("ShibAgent-R2", "0x016a148e728b8d61b2440ed311946ac06d4b5648"),
 ("DeY", "0xDB062c12bF0a14227e7Fe896a988950b050B51C1"),
 ("BoxBigem-3Ee9", "0x3Ee92296D663378D42521273aAA4779BDa8e25dD"),
 ("FANBEIMAO-824d", "0x824d1e5c1395ed7543854fCd9e4da6D3F358De16"),
 ("Ikigai-Ihigi", "0x3611455bE1FC2c6987FE9d016971b7E40B341684"),
 ("Hongbao-HONGBAO", "0x834e5BC43Aa91bEbEB31B97eaFA1bCb2F4286d97"),
 ("Nvagent-NVGT-28Fe", "0x28Fe0daD54dbfc84D29Cd48E88c27a82E76fF1c2"),
 ("Soarm-SOARM", "0x4a02e3824b301a1bf6a8230e56b44b526174ca97"),
 ("SAFUAI", "0xbd6087fc30f2395344020cb190255c56cbc517bd"),
]

def read_nft(item):
    name, addr = item
    d = {"address": addr}
    d["totalSupply"] = call(addr, "totalSupply()")
    if not isinstance(d["totalSupply"], int):
        d["totalMinted"] = call(addr, "totalMinted()")
    d["freeClaimed"] = call(addr, "freeClaimed()")
    d["freeMinted"] = call(addr, "freeMinted()")
    d["balanceOf_user"] = call(addr, "balanceOf(address)", enc(USER))
    if name in COSTOF:
        d["costOf_user_1"] = call(addr, "costOf(address,uint256)", enc(USER) + enc_uint(1))
        d["mintsLeft_user"] = call(addr, "mintsLeft(address)", enc(USER))
        d["mintOpen"] = call(addr, "mintOpen()")
        d["mintedBy_user"] = call(addr, "mintedBy(address)", enc(USER))
        d["price"] = call(addr, "price()")
    if name in SLOT:
        d["mintedBy_user"] = call(addr, "mintedBy(address)", enc(USER))
        d["freeUsed_user"] = call(addr, "freeUsed(address)", enc(USER))
        d["canFreeMint_user"] = call(addr, "canFreeMint(address)", enc(USER))
        d["claimedFree_user"] = call(addr, "claimedFree(address)", enc(USER))
        d["quote_user_1"] = call(addr, "quote(address,uint256)", enc(USER) + enc_uint(1))
    print(name, d, flush=True)
    return name, d

def read_tc(item):
    key, sale = item
    d = {"sale": sale}
    d["opened"] = call(sale, "opened()")
    d["launched"] = call(sale, "launched()")
    d["freeMinted"] = call(sale, "freeMinted()")
    d["freeSharesRemaining"] = call(sale, "freeSharesRemaining()")
    d["freeSharesClaimed_user"] = call(sale, "freeSharesClaimed(address)", enc(USER))
    d["freeClaimed_user"] = call(sale, "freeClaimed(address)", enc(USER))
    d["hasFreeShare_user"] = call(sale, "hasFreeShare(address)", enc(USER))
    d["totalMinted"] = call(sale, "totalMinted()")
    d["sharesMinted"] = call(sale, "sharesMinted()")
    d["saleEnded"] = call(sale, "saleEnded()")
    d["phase"] = call(sale, "phase()")
    print("TC", key, d, flush=True)
    return key, d

blk = block()
print("BLOCK", blk, flush=True)
out = {"block": blk, "reread": {}, "track_c": {}}
t0 = time.time()
with ThreadPoolExecutor(max_workers=8) as ex:
    for name, d in ex.map(read_nft, NFT):
        out["reread"][name] = d
        json.dump(out, open(f"{BASE}/run-{TS}-reread-lean.json", "w"), indent=1)
    for key, d in ex.map(read_tc, TC):
        out["track_c"][key] = d
        json.dump(out, open(f"{BASE}/run-{TS}-reread-lean.json", "w"), indent=1)
print("DONE in %.1fs, block %s" % (time.time() - t0, blk), flush=True)
json.dump(out, open(f"{BASE}/run-{TS}-reread-lean.json", "w"), indent=1)
