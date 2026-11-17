#!/usr/bin/env python3
"""Run 2026-11-08 0231 WIB: lean re-check track_c not-open / active items.
READ-ONLY. Single eth_calls via fast_rpc _single (dataseed), so one revert
never kills the batch. None = unreadable, NOT zero.
Writes run-2026-11-08-0231-trackc-recheck.json"""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

VIEWS = ["opened()", "launched()", "freeMinted()", "freeClaimed()",
         "freeSharesRemaining()", "totalMinted()", "totalSupply()",
         "FREE_SHARES()", "FREE_SUPPLY()", "freeLeft()", "mintOpen()",
         "spotsLeft()", "remainingFree()", "freeSupply()"]
# mapping(address) views, called with USER
MAPVIEWS = ["freeClaimed(address)", "freeUsed(address)", "mintedBy(address)",
            "freeFor(address)", "freeLeft(address)", "claimed(address)"]

TARGETS = {
 "NIUBI": "0x094DA228770A141bB2aCaE22608A08D66a8f789a",
 "DROID": "0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",
 "960E-sale": "0x960E7e4126b97679053B8416fA59f13508be88bf",
 "IMARS": "0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f",
 "NIULAI": "0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF",
 "OSK": "0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37",
 "CHTCI": "0x050a11c2bfcf881b546983a20550a0e409bf69da",
 "KillZero-K0-sale": "0x87ad9c1617ceb65f1b56f2ee06FE193F60aACF97",
 "DeY": "0xDB062c12bF0a14227e7Fe896a988950b050B51C1",
 "BoxBigem-3Ee9": "0x3Ee92296D663378D42521273aAA4779BDa8e25dD",
 "FANBEIMAO-824d": "0x824d1e5c1395ed7543854fCd9e4da6D3F358De16",
 "ShibAgent-R2": "0x016a148e728b8d61b2440ed311946ac06d4b5648",
 "BelieveBNB": "0x2d15595d2e6EfB1c1EBf938Cd7Fd0f57d11C6b86",
 "Pubzz-9f10": "0x9f10c0D8b8E5eFB8706243b1E9336A19E924CCeF",
 "FUGUI-set1-991": "0x4d6bbbc3129beb54450427dc12011f178c7fb630",
 "FUGUI-set2": "0xa0b30b8ff77826e2288a28d2c560ecf3476828f6",
 "MizzlewickAgent": "0x892E438425b3A41BC75b25C22Fd878b3fa2e308d",
 "MoonAgent-MOAGT": "0xc4695f19dE428EA37169bBD058463588D511554a",
 "JupiterAgent-JAGT": "0xa900873E65B5F391B6E37d80a98A6b26D07613B8",
 "PLNK": "0xec266bdd979b19d8a2f1266ef0610b4791dbd24b",
 "QuonkersAgent": "0xe8b5E3ca9f4F51366f9f4860ed70b8e929e80470",
 "HobnorbAgent": "0xab3F2dA0b63F5A823510095263789E9e6F26329a",
 "WibblezapAgent": "0x8717fc8751b8Ebd6832EA145974AA77D86bE9EaD",
 "DribblonAgent": "0x16A8aFdc97F8Cf48617bF15E47b4dA2217ea04A5",
 "YammerjackAgent": "0x2a71CEF7101B8b19c4ab18BeD40C3ec5EC87B9b7",
 "Draco Coin": "0x2e1927798462397a88e3c1015Dc8168e798DF6D3",
 "PHNX": "0x28a4F0BbdC1bE886f9e5a290e6598A83F248B224",
 "Agentidbsc": "0x716BFaB3B7b0301D17Af0fF4c50a880C7721F39C",
 "CLEPSYDRA": "0x9e2738B3DD3773c6c71cA24Fbc92660B501C0B6b",
 "ChimpAgent": "0x57D41Ff4895A19f518a0Ec3A2Fa56284a85f5689",
 "NJAR": "0x816458b734d17d59058762deaadd9b952bad6985",
 "Predictagent-PRDICT": "0x8fF4bd65584882324c44Ee794a23E7791820189b",
}

def call(addr, data):
    for ep in EPS:
        try:
            r = _single(ep, "eth_call", [{"to": addr, "data": data}, "latest"], 8, retries=0)
            if isinstance(r, str) and r.startswith("0x") and len(r) >= 66:
                return int(r, 16)
            if isinstance(r, str) and r.startswith("0x") and len(r) > 2:
                return r
            return None
        except Exception:
            continue
    return None

out = {}
block = None
try:
    block = int(_single(EPS[0], "eth_blockNumber", [], 8, retries=0), 16)
except Exception as e:
    block = f"ERR {e}"
out["block"] = block
for name, addr in TARGETS.items():
    row = {"address": addr}
    for v in VIEWS:
        row[v] = call(addr, sel(v))
    for v in MAPVIEWS:
        data = sel(v) + USER[2:].lower().rjust(64, "0")
        row[v] = call(addr, data)
    out[name] = row
    print(name, {k: val for k, val in row.items() if val is not None and k != "address"}, flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-08-0231-trackc-recheck.json", "w"), indent=1)
print("BLOCK", block, "done", flush=True)
