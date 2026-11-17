#!/usr/bin/env python3
"""Run 1601 (2026-11-05 ~16:01 WIB): route-1 watchlist re-read + track-C re-read. Read-only.
Views: totalSupply (fallback totalMinted), freeClaimed/freeMinted, FREE_SUPPLY,
balanceOf(user); slot views only for promotion candidates. No preview/mint."""
import json, urllib.request, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-05-1601"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc-dataseed2.bnbchain.org",
        "https://bsc-dataseed3.bnbchain.org", "https://bsc.publicnode.com"]
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
            with urllib.request.urlopen(req, timeout=8) as r: out = json.load(r)
            if "error" in out: return {"error": str(out["error"])[:60]}
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return {"error": "rpc-fail"}

def call(to, sig, args=""): return raw(to, sel(sig) + args)
def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: return int(json.load(r)["result"], 16)
        except Exception:
            continue
    return None

def block_ts(n):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                               "params": [hex(n), False]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r:
                return int(json.load(r)["result"]["timestamp"], 16)
        except Exception:
            continue
    return None

# (name, address, extra slot views?)
NFT = [
 ("HIVE Agents", "0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77", False),
 ("Tigora-E8c4", "0xE8c46E7c734259FEc1A78Fc846DcFaD94Ecb70E5", False),
 ("BNBRunnerz-2674", "0x8AAA14b24e71cC93672939ba3e3C3e9DE2674d27", False),
 ("Shroomies-2AE7", "0x2AE712138a74202daBB8FFC93117AA53754F54D0", True),
 ("Blobbies-a7fB", "0xa7fBAB4a96d6900122Dc51FDC839CFE5C89B23b3", False),
 ("Jolly", "0xdc11764a5664e333c8d303eb465e89a1caadb85b", False),
 ("HACKED", "0xCD355D1191Ce9849B3A935C821A66d9DF37cFE77", False),
 ("SoulAgent", "0x8fdB9411753c58476A41F7B88a44989F8D687d63", False),
 ("PERSONA-A930", "0xA930C4466431B0331C911846f297D7D4e063249D", False),
 ("RigOrb-539e", "0x72D977237f7b3931A08434cEBD0D3814fE13539e", False),
 ("AFROG", "0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31", False),
 ("Swarmcentaur", "0x87B805eCDDaB0b376531cAf6d5aD9A52E641B100", False),
 ("Agentyyds", "0x8463abFC06173BdCaEDe96c4331C30A958789629", False),
 ("Pilotneon", "0x01D0f3b16C89615c924007ae85779B55A22552D0", False),
 ("Mummyhive", "0xf45fE22B3a9A748c59A7099e2E7B69f41216b1cd", False),
 ("Saturnode", "0x6124b3ae64adA7b73581CcD01fEF89e583E8742c", True),
 ("Agent Coffee", "0x53A3D78FF23d9c9cb14Ae8B2fd168A44391b2010", True),
 ("Driftnauts", "0x6a926234D3767F2EEb3DB12c1B4C9e2912C5589b", True),
 ("Thronemind", "0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90", True),
 ("Hashseers", "0x7E634ED532a7b7b781262A0d4220ac3c3Ba6B688", True),
 ("Cachejack", "0x18042D2E0bFd11fc2cc8ee1E59a6601e530C3dF5", True),
 ("AgentMiner", "0x8670e99062ead2cE5402754aeDE769602FDf38b8", True),
 ("Smeltbots", "0xdC0004F3Efcc2aEA6052e138d3f1e680ca5D9b8e", True),
 ("Roguefall", "0x5fe03829a2f94a8bA3906459258b1305F0e68934", True),
 ("Agent Goats", "0x0E9E0a3B46dC0d36A1Ab64f553Dd8A0693E6aAa6", True),
 ("Agent Owls", "0x50B4bD215c409C975c940d5CF23B56D8F3ecfd3b", True),
 ("Hirelings-A", "0xff61A6e13776B0823E18d960b3f9ee2C78685601", True),
 ("Hirelings-B", "0xcbE18caA6d2A8BEaC563972d7457E8Afbb0E7C4a", True),
 ("Forklings", "0xD7B3FD33e0b465B0e374906F60567D317b758FD8", True),
 ("Auspibots", "0x3E56Ace6760ba03F3Ff669C51bcCa662bB96f955", True),
 ("Neurolucha", "0x56eBED63452Bb02B975ceE02949DA3C02466725b", True),
 ("Layerloom", "0x1B72ceC52A74537b06F713FCebA0e491f53679aE", True),
 ("Tumblebots", "0x02f10432EAf9CbF72e1aC9b9208af601aADd6b17", True),
 ("Agent Frogs", "0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31", True),
 ("PassAgentX", "0x08b1A979Dd997492EEcc010fe986eA2e2925e620", True),
 ("Bathybots", "0x9610195ac5304B697080ea1252C70613a098E388", True),
 ("Pulsekeep", "0x65c89bD01A03B9B9B73eD29d3B3aF8D2eb034DFc", True),
 ("Tensortug", "0xDdD2b5501B32e0C58C7deB7401765d711553b702", True),
 ("DYOR-8695", "0x86956Bc830EB62110820Ae79164BeF61c7E31936", True),
 ("PixelLaptop-273f", "0x273fc2c7705b23eb129e35ac8da26348e6fc4980", True),
 ("AgentLattice-5b9e", "0x5b9fe53468F1Aa4EDbe2b96a4387910D335e2eDB", True),
 ("Lucky Charm Atlas II-5812", "0x58126241BAA73B0b234e9B7F299D06eF44cCaFe9", True),
 ("MoonCat", "0x045425004b622733ced4139e930c622187ea6c73", True),
 ("PCAT-9b9e", "0x9b9e0a4358449eebf4437877a9b36e26c24ce703", True),
 ("KOAI-6dFE", "0x6dFE0D2E3Ab6f2bD5F3875557eb0e5c5Fe4B05c7", True),
 ("LIMITLESS-c7aa", "0xc7aa008c2369ff00322c49d526f33529bb692a86", True),
 ("SEAT-f11e", "0xf11e9405b23ca0f53e6135162a85545d780a3737", True),
 ("Cogito-COG-A", "0x5ae2be6BbA1BD4f561Dc13158c7f5B95992e045B", True),
 ("LIKHIN", "0x8166e67c35ff12a03564530f01f583f0A15De30c", True),
 ("StarAgent-7d39", "0x7d390e37Ed41A359f276D8764ca15432704B99b7", True),
 ("WAGagent", "0x06a6f51D30556f4262e38485C09556fE81e6A984", True),
 ("PACTURE", "0x10b80088fdaf9363d83671be66b64f231f9e92f6", True),
]

# track-C sales: (key, sale address)
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

blk = block()
ts = block_ts(blk) if blk else None
print("BLOCK", blk, "TS", ts)
out = {"block": blk, "block_ts": ts, "reread": {}, "track_c": {}}

for name, addr, slot in NFT:
    d = {}
    d["totalSupply"] = call(addr, "totalSupply()")
    if not isinstance(d["totalSupply"], int):
        d["totalMinted"] = call(addr, "totalMinted()")
    d["freeClaimed"] = call(addr, "freeClaimed()")
    d["freeMinted"] = call(addr, "freeMinted()")
    d["FREE_SUPPLY"] = call(addr, "FREE_SUPPLY()")
    d["balanceOf_user"] = call(addr, "balanceOf(address)", enc(USER))
    if slot:
        d["mintedBy_user"] = call(addr, "mintedBy(address)", enc(USER))
        d["freeUsed_user"] = call(addr, "freeUsed(address)", enc(USER))
        d["freeLeft_user"] = call(addr, "freeLeft(address)", enc(USER))
        d["canFreeMint_user"] = call(addr, "canFreeMint(address)", enc(USER))
        d["claimedFree_user"] = call(addr, "claimedFree(address)", enc(USER))
        d["quote_user_1"] = call(addr, "quote(address,uint256)", enc(USER) + enc_uint(1))
        d["mintOpen"] = call(addr, "mintOpen()")
    out["reread"][name] = {"address": addr, **d}
    print(name, d)
    time.sleep(0.05)

for key, sale in TC:
    d = {}
    d["opened"] = call(sale, "opened()")
    d["launched"] = call(sale, "launched()")
    d["freeMinted"] = call(sale, "freeMinted()")
    d["freeSharesRemaining"] = call(sale, "freeSharesRemaining()")
    d["freeSharesClaimed_user"] = call(sale, "freeSharesClaimed(address)", enc(USER))
    d["freeClaimed_user"] = call(sale, "freeClaimed(address)", enc(USER))
    d["hasFreeShare_user"] = call(sale, "hasFreeShare(address)", enc(USER))
    d["totalMinted"] = call(sale, "totalMinted()")
    d["sharesMinted"] = call(sale, "sharesMinted()")
    d["paidShares"] = call(sale, "paidShares()")
    d["saleEnded"] = call(sale, "saleEnded()")
    d["phase"] = call(sale, "phase()")
    d["isRefundPhase"] = call(sale, "isRefundPhase()")
    d["failed"] = call(sale, "failed()")
    out["track_c"][key] = {"sale": sale, **d}
    print("TC", key, d)
    time.sleep(0.05)

json.dump(out, open(f"{BASE}/run-{TS}-reread.json", "w"), indent=1)
print("SAVED run-%s-reread.json" % TS)
