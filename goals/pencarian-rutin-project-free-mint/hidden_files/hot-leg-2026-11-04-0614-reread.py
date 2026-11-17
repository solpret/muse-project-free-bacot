#!/usr/bin/env python3
"""Hot-leg 2026-11-04 05:59 WIB: read-only re-read of snapshot watchlist items."""
import json, urllib.request
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def call(to, data):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": to, "data": data}, "latest"]}).encode()
    for ep in EPS:
        try:
            req = urllib.request.Request(ep, data=payload, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=8) as r:
                v = json.load(r)["result"]
            return int(v, 16) if v and v != "0x" else None
        except Exception:
            continue
    return None
def block():
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
    for ep in EPS:
        try:
            req = urllib.request.Request(ep, data=payload, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=8) as r:
                return int(json.load(r)["result"], 16)
        except Exception:
            continue
    return None
def collect(to, tests):
    return {name: call(to, sel(name) + arg) for name, arg in tests}
u = USER[2:].lower().rjust(64, "0")
early = [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""),
         ("mintedBy(address)", u), ("freeUsed(address)", u), ("balanceOf(address)", u)]
items = {
 "Malabao": "0x2C215262635E66c798c5a1Ba4411fA9F06852bDD",
 "Mothwraith": "0x11fa2C4b71EcE40f242992a08C4ACC6C23c99Ca0",
 "Pyrevane": "0xFb8b2865727D7e7b8F8761cDC0cA0DE4e7f4e551",
 "Robogent": "0x5eA7E757dfc4654f7478841BD30175bd7F186e24",
 "Crtdroid": "0xDe67dc24C9B37af22bC6C995cA99e86809b01286",
 "Fangcount": "0x75A2D4f6f158240CB5Fd4B4f866cEA85b143D165",
 "Vesperfang": "0x2a91b304eE74162007730CF1da24C1d8C137c627",
 "Krakenbo": "0x46c1815082ccf1273e3c07548ef2004046Bb7Fc0",
 "Mothfarm": "0x74E64b8B2941F61Bb67801C7668a4307bC34D9E0",
 "Swarmcentaur": "0x87B805eCDDaB0b376531cAf6d5aD9A52E641B100",
 "Noctagent": "0x9c60E147f10fF790A293889DDee1e2C4063e096d",
 "Botsaturn": "0xd1E75De8e6B46E09a90126A122373Fac79578300",
 "LunaBirds": "0xd514eb87c957514979360d9913e1bebcdd90129d",
 "PixelTrump": "0x3054a5530f1852c33bd2749bfaf7155f162a581b",
 "WDNFT": "0xac7c0e1f36e15dba7ed32bf6e72d83095ff8fd10",
}
res = {"block": block()}
for n, a in items.items():
    res[n] = collect(a, early)
res["TrackB_MINT"] = collect("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
    [("launched()", ""), ("tokenClaimed(address)", u), ("isRefundPhase()", ""), ("failed()", "")])
res["DROID"] = collect("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",
    [("FREE_SHARES()", ""), ("freeMinted()", ""), ("freeUsed(address)", u)])
res["QAGENT2"] = collect("0xE3a4f3099a2136e0e66202A665815caB8FFA2704",
    [("freeMinted()", ""), ("MAX_FREE()", ""), ("poolOpen()", ""), ("freeClaimed(address)", u)])
json.dump(res, open(BASE + "hot-leg-2026-11-04-0614-reread.json", "w"), indent=1)
print("block", res["block"])
for k, v in res.items():
    if k != "block":
        print(k, v)
