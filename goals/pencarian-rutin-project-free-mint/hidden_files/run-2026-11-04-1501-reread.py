#!/usr/bin/env python3
"""Run 1501 re-read: subset aktif snapshot + track-B + track-C watchlist. Read-only."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def call(to, data):
    try: return race("eth_call", [{"to": to, "data": data}, "latest"])
    except Exception as e: return None
def iv(v):
    try: return int(v, 16) if v else None
    except Exception: return None
def collect(to, tests):
    out = {}
    for name, arg in tests:
        out[name] = iv(call(to, sel(name)+arg))
    return out
def block():
    try: return int(race("eth_blockNumber", []), 16)
    except Exception: return None

snap = json.load(open(BASE+"onchain-snapshot.json"))
contracts = snap["contracts"]
# subset: reread keys 1431 + 4 baru 1431
NAMES = ['Pyrevane','Robogent','Vesperfang','Krakenbo','Mothfarm','Swarmcentaur','Noctagent','Botsaturn','LunaBirds','PixelTrump','WDNFT','Mummyhive','Glitchdroid','Agentyyds','Pilotneon','Pilotphoenix','Agentzhenxiang','Pumpkinmind','Chipagent','Spookdroidling','Saturndroid','Agentvolt','Jolly','Vampirko','Neijuan','Agentarot','Cybermoth','Unnamed-E6BA-1401','Unnamed-miner-E246-1401']
tests = [("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("freeMinted()",""),("mintedBy(address)",enc_addr(USER)),("freeUsed(address)",enc_addr(USER)),("balanceOf(address)",enc_addr(USER))]
result = {"block": block()}
for n in NAMES:
    v = contracts.get(n)
    if not v: result[n] = {"error": "not-in-snapshot"}; continue
    addr = v.get("address")
    result[n] = collect(addr, tests)
    # E246 miner: nextId
    if n == 'Unnamed-miner-E246-1401':
        result[n]["nextId()"] = iv(call(addr, sel("nextId()")))
        result[n]["freeMinedCount()"] = iv(call(addr, sel("freeMinedCount()")))
# Track-B pending (binanceai.fun) + FABE launched
MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN = "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
result["TrackB_MINT"] = collect(MINT, [("launched()",""),("tokenClaimed(address)",enc_addr(USER)),("totalShares()",""),("isRefundPhase()",""),("failed()","")])
result["TrackB_TOKEN_bal_USER"] = collect(TOKEN, [("balanceOf(address)", enc_addr(USER))])
FABE = "0xFabE022a5943462fee1Bd221791945DA57510BE8"
result["FABE"] = collect(FABE, [("launched()",""),("freeSharesClaimed(address)",enc_addr(USER)),("sharesMinted(address)",enc_addr(USER)),("freeSharesRemaining()",""),("FREE_SHARES()","")])
# Track-C watchlist: DROID, OSK, IMARS, NIULAI, KillZero (generic views; null = revert/unknown, never zero)
TC = {
 "DROID": "0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",
 "OSK": "0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37",
 "IMARS": "0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f",
 "NIULAI": "0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF",
 "KillZero": "0x87ad9c1617ceb65f1b56f2ee06FE193F60aACF97",
}
tc_tests = [("launched()",""),("opened()",""),("freeMinted()",""),("totalMinted()",""),("FREE_SHARES()",""),("freeClaimed()",""),("totalMintCount()","")]
for n, a in TC.items():
    result[n] = collect(a, tc_tests)
json.dump({"reread": result}, open(BASE+"run-2026-11-04-1501-reread.json","w"), indent=1)
print("block:", result["block"])
for n in NAMES + ["TrackB_MINT","FABE","DROID","OSK","IMARS","NIULAI","KillZero"]:
    print(n, result.get(n))
