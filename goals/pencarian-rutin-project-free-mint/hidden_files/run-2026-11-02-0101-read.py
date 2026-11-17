#!/usr/bin/env python3
"""Free-mint-search run 2026-11-02 01:01 WIB: re-reads. Read-only."""
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
        sig = name.replace("quote1(", "quote(").replace("quote0(", "quote(")
        val, err = call(to, sel(sig) + arg)
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
def gi(d, name):
    v = d.get(name, {})
    return v.get("int") if isinstance(v, dict) else v

result = {"block": block()}
HIVE = "0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77"
result["HIVE"] = collect(HIVE, [("totalSupply()", ""), ("START_TIME()", ""), ("FREE_SUPPLY()", ""),
    ("totalPaid()", ""), ("freeMintedBy(address)", enc_addr(USER)[2:]),
    ("balanceOf(address)", enc_addr(USER)[2:]), ("quote(uint256)", enc_uint(1)[2:]), ("currentPrice()", "")])
NFTS = {
 "Bubblebruin": "0xc205F8c74733D914776D66cBc4Cf10BF701D96Aa",
 "Zapcourier": "0x672c1dF4F7121DaCBD3504995441C47d2fAbCdDC",
 "Mothwraith": "0x11fa2C4b71EcE40f242992a08C4ACC6C23c99Ca0",
 "Cryonyx": "0x787b522d48084A83b8B1b0C206aA4A12B1FD1cc2",
 "Cathodex": "0x0AC5591d1B980C7bE16861d722E59E21E2624868",
 "Malabao": "0x2C215262635E66c798c5a1Ba4411fA9F06852bDD",
 "Voltabyte": "0xBbbBf437CE6275e21728bc6a9aa99d1bda9cE989",
 "Saturnin": "0xb257b3A30A795cAd46ee4D25D0c730b10cAd6b1E",
 "Kirinova": "0x68a971C9D2b54Ae86dAF59CD665E40f3E087fb7F",
 "Ghostbloom": "0xd987945d1df5FcD111155bF9C494fAAde3f91E3e",
 "Junepup": "0x7Fbedd1E2EF6e4765e8F72b2668E9f4A964600f7",
}
nft_tests = [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""), ("MAX_SUPPLY()", ""),
    ("mintOpen()", ""), ("mintedBy(address)", enc_addr(USER)[2:]), ("freeFor(address)", enc_addr(USER)[2:]),
    ("freeUsed(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])]
for nm, addr in NFTS.items():
    result[nm] = collect(addr, nft_tests)
    v, e = call(addr, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(1)[2:])
    result[nm]["quote_user_1"] = {"words": words(v), "raw": v, "error": e}
MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN = "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
PAIR = "0x903ACC22B9BABCD427bfb9AF2C27a27a5aC7c698"
POLLEN = "0x3E9B4F58e2bC9b064F002cF89531e12FC5CfA00f"
POLLEN_TOK = "0x2d91628eeed28f5442C8903cfF8bB85bCf38FF9B"
result["TrackB_MINT"] = collect(MINT, [("launched()", ""), ("tokenClaimed(address)", enc_addr(USER)[2:]), ("totalShares()", ""), ("isRefundPhase()", ""), ("failed()", "")])
result["Pollen_MINT"] = collect(POLLEN, [("launched()", ""), ("phase()", ""), ("startAt()", ""), ("endAt()", ""),
    ("pollenAgents()", ""), ("pollenSlice()", ""), ("paidSold()", ""), ("PAID_SHARES()", ""),
    ("accounts(address)", enc_addr(USER)[2:]), ("agentInfo(address)", enc_addr(USER)[2:]),
    ("claimable(address)", enc_addr(USER)[2:])])
# accounts/agentInfo are multi-word; capture raw via collect? collect int-parse fails, so re-read raw:
for fn in ("accounts(address)", "agentInfo(address)"):
    v, e = call(POLLEN, sel(fn) + enc_addr(USER)[2:])
    result["Pollen_MINT"][fn + "_raw"] = {"words": words(v), "raw": v, "error": e}
BABY = "0xbb7ed59ca41ea03cf20084a8c9de94244b7b2637"
result["BNBbaby"] = collect(BABY, [("sharesMinted()", ""), ("freeMinted()", ""), ("paidShares()", ""), ("totalShares()", ""),
    ("MAX_SHARES()", ""), ("mintingOpen()", ""), ("poolOpen()", ""),
    ("freeAvailable(address)", enc_addr(USER)[2:]), ("freeClaimed(address)", enc_addr(USER)[2:]),
    ("mintedBy(address)", enc_addr(USER)[2:]), ("hasAgentId(address)", enc_addr(USER)[2:])])
DOGSALE = "0xA74bEF84304D8838db798faE96fb873dd46fB4C1"
result["DOG"] = collect(DOGSALE, [("sharesMinted()", ""), ("FREE_SHARES()", ""), ("MAX_SHARES()", ""),
    ("poolOpen()", ""), ("saleFailed()", ""), ("sharesByWallet(address)", enc_addr(USER)[2:]), ("deadline()", "")])
aid, err = call(DOGSALE, sel("agentIdOf(address)") + enc_addr(USER)[2:])
result["DOG_agentId"] = {"raw": aid, "error": err}
if aid:
    fc, e2 = call(DOGSALE, sel("freeClaimed(bytes32)") + aid[2:])
    result["DOG_freeClaimed_user"] = {"words": words(fc), "raw": fc, "error": e2}
    for q in (0, 1):
        v, e = call(DOGSALE, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(q)[2:])
        result[f"DOG_quote_user_{q}"] = {"words": words(v), "raw": v, "error": e}
result["SAFU"] = collect("0x56b06B4BF22dd02D0375916907f19D37846c9d91", [("freeClaimed()", ""), ("paused()", ""), ("totalSupply()", ""), ("MAX_SUPPLY()", ""), ("balanceOf(address)", enc_addr(USER)[2:])])
result["QILIN"] = collect("0xbb77f247e6b57f4dcd09c5900b2ffc4250b6b88f", [("totalCards()", ""), ("cardsSold()", ""), ("cardsRemaining()", ""), ("freeCardCap()", ""),
    ("freeCardsRemaining()", ""), ("freeGiven()", ""), ("gateOn()", ""), ("paused()", ""),
    ("freeClaimed(address)", enc_addr(USER)[2:]), ("quotaLeft(address)", enc_addr(USER)[2:])])
SLIME = "0x3815A26a6981BAAd0b850f7522B7a8BDDdB6B70C"
result["Slimelings"] = collect(SLIME, [("totalSupply()", ""), ("mintedCount()", ""), ("freeCount()", ""), ("maxSupply()", ""), ("paused()", ""), ("gatingEnabled()", ""), ("mintedBy(address)", enc_addr(USER)[2:]), ("freeClaimed(address)", enc_addr(USER)[2:]), ("remainingForWallet(address)", enc_addr(USER)[2:]), ("hasAgentId(address)", enc_addr(USER)[2:]), ("isEligible(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])])
v, e = call(SLIME, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(1)[2:])
result["Slimelings_quote_user_1"] = {"words": words(v), "raw": v, "error": e}
PIG = "0xfd3d4e0d7a81534addd11f96fdd8008f942097f9"
result["BNBPIG"] = collect(PIG, [("sharesMinted()", ""), ("freeMinted()", ""), ("paidShares()", ""), ("MAX_SHARES()", ""), ("MAX_FREE()", ""), ("mintingOpen()", ""), ("freeAvailable(address)", enc_addr(USER)[2:]), ("freeClaimed(address)", enc_addr(USER)[2:]), ("mintedBy(address)", enc_addr(USER)[2:]), ("hasAgentId(address)", enc_addr(USER)[2:])])
SAM = "0xe15e68C9198ee0A5780fba96016e1780204aF3B4"
result["SAMBARIO"] = collect(SAM, [("totalCards()", ""), ("cardsSold()", ""), ("cardsRemaining()", ""), ("freeCardCap()", ""), ("freeCardsRemaining()", ""), ("freeGiven()", ""), ("gateOn()", ""), ("paused()", ""), ("freeClaimed(address)", enc_addr(USER)[2:]), ("quotaLeft(address)", enc_addr(USER)[2:]), ("quote(address,uint256)", enc_addr(USER)[2:] + enc_uint(1)[2:])])
FOUNT = "0x81Fc58bD054b95de96ea4Bf37A4bD45E9B6e1f4e"
result["Fountain"] = collect(FOUNT, [("totalMinted()", ""), ("FREE_SUPPLY()", ""), ("MAX_SUPPLY()", ""), ("currentPrice()", ""), ("mintedBy(address)", enc_addr(USER)[2:]), ("costFor(uint256)", enc_uint(1)[2:])])
VOR = "0xDEc97178bFA4692A6CB60901C628C8e7437b5A83"
result["Vorpry"] = collect(VOR, [("totalSupply()", ""), ("totalMinted()", ""), ("mintPrice()", ""), ("saleActive()", ""), ("openSupply()", ""), ("openLeft()", ""), ("tookFree(address)", enc_addr(USER)[2:]), ("isAgentHolder(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])])
MIR = "0x27cD34C8A5cc9376030f44d5fEc1a3DCCEeCa2a3"
result["MirrorPair"] = collect(MIR, [("mintedPairs()", ""), ("totalBonds()", ""), ("MAX_PAIRS()", ""), ("GENESIS_LIMIT()", ""), ("pairingPaused()", ""), ("poolSize()", ""), ("hasAgentId(address)", enc_addr(USER)[2:]), ("hasPaired(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])])
A7 = "0xa7Bef74f9327daacEe49fEa9Db9C34253900936A"
result["a7Be"] = collect(A7, [("sharesMinted()", ""), ("freeSharesMinted()", ""), ("FREE_SHARES()", ""), ("MAX_SHARES()", ""), ("paidSharesMinted()", ""), ("poolOpen()", ""), ("saleFailed()", ""), ("deadline()", ""), ("sharesByWallet(address)", enc_addr(USER)[2:])])
aid2, err2 = call(A7, sel("agentIdOf(address)") + enc_addr(USER)[2:])
result["a7Be_agentId"] = {"raw": aid2, "error": err2}
if aid2:
    fc, e2 = call(A7, sel("freeClaimed(bytes32)") + aid2[2:])
    result["a7Be_freeClaimed_agentId"] = {"words": words(fc), "raw": fc, "error": e2}
    v, e = call(A7, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(1)[2:])
    result["a7Be_quote_user_1"] = {"words": words(v), "raw": v, "error": e}
NIU = "0x094DA228770A141bB2aCaE22608A08D66a8f789a"
result["NIUBI"] = collect(NIU, [("sharesMinted()", ""), ("freeMinted()", ""), ("MAX_FREE()", ""), ("MAX_SHARES()", ""), ("poolOpen()", ""), ("deadline()", ""), ("freeAvailable(address)", enc_addr(USER)[2:]), ("freeClaimed(address)", enc_addr(USER)[2:]), ("mintedBy(address)", enc_addr(USER)[2:])])
print(json.dumps(result, indent=1))
json.dump(result, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0101-read.json", "w"), indent=1)
