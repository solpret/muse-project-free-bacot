#!/usr/bin/env python3
"""Free-mint-search run 2026-11-02 08:01 WIB: track-A watchlist + track-B pending re-read. Read-only."""
import json, sys
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
def call(to, data):
    for ep in EPS:
        try:
            return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0), None
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:160]}"
    return None, err
def collect(to, tests):
    out = {}
    for name, arg in tests:
        val, err = call(to, sel(name) + arg)
        try: iv = int(val, 16) if val else None
        except Exception: iv = None
        out[name] = {"int": iv, "raw": val, "error": err if val is None else None}
    return out
def block():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
    return None
def words(val):
    if not val: return None
    b = bytes.fromhex(val[2:])
    return [int.from_bytes(b[i:i+32], "big") for i in range(0, len(b), 32)]

B = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(B + "onchain-snapshot.json"))
result = {"block": block()}
std_tests = [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""), ("MAX_SUPPLY()", ""),
    ("mintOpen()", ""), ("mintedBy(address)", enc_addr(USER)[2:]), ("freeUsed(address)", enc_addr(USER)[2:]),
    ("balanceOf(address)", enc_addr(USER)[2:])]
SPECIAL = {
 "HIVE Agents": [("totalSupply()", ""), ("FREE_SUPPLY()", ""), ("totalPaid()", ""), ("freeMintedBy(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])],
 "Slimelings": [("totalSupply()", ""), ("mintedCount()", ""), ("freeCount()", ""), ("maxSupply()", ""), ("mintedBy(address)", enc_addr(USER)[2:]), ("freeClaimed(address)", enc_addr(USER)[2:]), ("remainingForWallet(address)", enc_addr(USER)[2:]), ("hasAgentId(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])],
 "Vorpry": [("totalSupply()", ""), ("totalMinted()", ""), ("openLeft()", ""), ("saleActive()", ""), ("tookFree(address)", enc_addr(USER)[2:]), ("isAgentHolder(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])],
 "Mirror Pair": [("mintedPairs()", ""), ("totalBonds()", ""), ("MAX_PAIRS()", ""), ("pairingPaused()", ""), ("hasAgentId(address)", enc_addr(USER)[2:]), ("hasPaired(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])],
 "Cilok Cats: White Paw Genesis": [("totalMinted()", ""), ("freeMinted()", ""), ("FREE_SUPPLY()", ""), ("freeClaimed(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])],
 "Agents NormiePunks": [("totalSupply()", ""), ("totalMinted()", ""), ("freePerWallet()", ""), ("mintedBy(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])],
 "NULLSECTOR": [("totalSupply()", ""), ("MAX_SUPPLY()", ""), ("mintOpen()", ""), ("freeClaimed(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])],
 "Onimaru": [("totalMinted()", ""), ("freeMinted()", ""), ("FREE_CAP()", ""), ("freeClaimed(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])],
 "Rootlinks": [("totalMinted()", ""), ("freeMinted()", ""), ("FREE_CAP()", ""), ("balanceOf(address)", enc_addr(USER)[2:])],
 "PIXEL FROGS": [("totalSupply()", ""), ("freeClaimed(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])],
 "Orchard Agent": [("totalMinted()", ""), ("FREE_SUPPLY()", ""), ("currentPrice()", ""), ("mintedBy(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])],
 "Hachiko": [("totalSupply()", ""), ("freeClaimed()", ""), ("freeCap()", ""), ("balanceOf(address)", enc_addr(USER)[2:])],
 "Critter Agent": [("totalSupply()", ""), ("freeMinted()", ""), ("freeSupply()", ""), ("mintedBy(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])],
 "Glacier Agent": [("totalMinted()", ""), ("FREE_SUPPLY()", ""), ("costFor(uint256)", enc_uint(1)[2:]), ("mintedBy(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])],
}
for name, entry in snap["contracts"].items():
    addr = entry.get("address")
    if not addr:
        continue
    tests = SPECIAL.get(name, std_tests)
    d = collect(addr, tests)
    if name not in SPECIAL:
        v, e = call(addr, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(1)[2:])
        d["quote_user_1"] = {"words": words(v), "raw": v, "error": e}
    if name == "PIXEL FROGS":
        v, e = call(addr, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(1)[2:])
        d["quote_user_1"] = {"words": words(v), "raw": v, "error": e}
    if name == "Slimelings":
        v, e = call(addr, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(1)[2:])
        d["quote_user_1"] = {"words": words(v), "raw": v, "error": e}
    result[name] = d
MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
result["TrackB_MINT"] = collect(MINT, [("launched()", ""), ("tokenClaimed(address)", enc_addr(USER)[2:]), ("totalShares()", ""), ("isRefundPhase()", ""), ("failed()", "")])
POLLEN = "0x3E9B4F58e2bC9b064F002cF89531e12FC5CfA00f"
result["Pollen_MINT"] = collect(POLLEN, [("launched()", ""), ("phase()", ""), ("startAt()", ""), ("endAt()", ""),
    ("pollenAgents()", ""), ("pollenSlice()", ""), ("paidSold()", ""), ("PAID_SHARES()", "")])
print(json.dumps(result, indent=1))
json.dump(result, open(B + "run-2026-11-02-1031-read.json", "w"), indent=1)

# Track-C blocked/watchlist re-check (no preview)
BIAO="0x16469C174cd827A5e21f4bf3eE3711f2bB42e275"
BABY="0xbb7ed59ca41ea03cf20084a8c9de94244b7b2637"
DROID="0xFcF6388DD3bcC674c095273aB479C7e54dd5E177"
NIUBI="0x094DA228770A141bB2aCaE22608A08D66a8f789a"
QILIN="0xbb77f247e6b57f4dcd09c5900b2ffc4250b6b88f"
result["TrackC_BIAO"]=collect(BIAO,[("freeClaimed()",""),("FREE_SHARES()",""),("phase()",""),("sold()",""),("tradingOpen()",""),("poolCreated()","")])
result["TrackC_BNBbaby"]=collect(BABY,[("sharesMinted()",""),("freeMinted()",""),("paidShares()",""),("MAX_SHARES()",""),("mintingOpen()",""),("freeAvailable(address)",enc_addr(USER)[2:]),("freeClaimed(address)",enc_addr(USER)[2:]),("mintedBy(address)",enc_addr(USER)[2:])])
result["TrackC_DROID"]=collect(DROID,[("FREE_SHARES()",""),("freeMinted()",""),("paused()",""),("freeUsed(address)",enc_addr(USER)[2:])])
result["TrackC_NIUBI"]=collect(NIUBI,[("sharesMinted()",""),("freeMinted()",""),("freeAvailable(address)",enc_addr(USER)[2:]),("freeClaimed(address)",enc_addr(USER)[2:])])
result["TrackC_QILIN"]=collect(QILIN,[("totalCards()",""),("cardsSold()",""),("cardsRemaining()",""),("freeCardCap()",""),("freeCardsRemaining()",""),("freeGiven()",""),("gateOn()",""),("paused()",""),("freeClaimed(address)",enc_addr(USER)[2:]),("quotaLeft(address)",enc_addr(USER)[2:])])
print(json.dumps({k:result[k] for k in ["TrackC_BIAO","TrackC_BNBbaby","TrackC_DROID","TrackC_NIUBI","TrackC_QILIN"]},indent=1))
json.dump(result, open(B + "run-2026-11-02-1031-read.json", "w"), indent=1)
