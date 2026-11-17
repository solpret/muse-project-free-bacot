#!/usr/bin/env python3
"""Main run 2026-11-02 15:31 WIB route 1 + track B/C + Sevaris fresh reads."""
import json, sys, concurrent.futures
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0), None
        except Exception as e: err = f"{type(e).__name__}: {str(e)[:120]}"
    return None, err
def collect(to, tests):
    out = {}
    for name, arg in tests:
        val, err = call(to, sel(name) + arg)
        try: iv = int(val, 16) if val else None
        except Exception: iv = None
        out[name] = iv
    return out
def block():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
    return None

snap = json.load(open(BASE + "onchain-snapshot.json"))
GEN = [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""), ("freeMinted()", ""),
       ("freeLeft()", ""), ("mintedBy(address)", enc_addr(USER)), ("freeUsed(address)", enc_addr(USER)),
       ("balanceOf(address)", enc_addr(USER)), ("owner()", "")]
targets = {}
for name, v in snap["contracts"].items():
    if not str(v.get("status", "")).startswith("minted-by-user"):
        targets[name] = v["address"]
extra = {
 "TrackB_MINT": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
   [("launched()", ""), ("tokenClaimed(address)", enc_addr(USER)), ("totalShares()", ""), ("isRefundPhase()", ""), ("failed()", "")]),
 "TrackB_TOKEN_bal": ("0x209173F09aFbCA053C0de9e9763f503e9fb54a3c", [("balanceOf(address)", enc_addr(USER))]),
 "Pollen_MINT": ("0x3E9B4F58e2bC9b064F002cF89531e12FC5CfA00f",
   [("launched()", ""), ("phase()", ""), ("pollenAgents()", ""), ("paidSold()", "")]),
 "QAGENT": ("0x93eAbc3f8496A304eb0CDC3F1AD00CCCdb877877",
   [("sharesMinted()", ""), ("freeMinted()", ""), ("MAX_FREE()", ""), ("mintingOpen()", ""), ("freeAvailable(address)", enc_addr(USER)), ("freeClaimed(address)", enc_addr(USER))]),
 "NIUBI": ("0x094DA228770A141bB2aCaE22608A08D66a8f789a",
   [("sharesMinted()", ""), ("freeMinted()", ""), ("MAX_FREE()", ""), ("mintingOpen()", ""), ("freeAvailable(address)", enc_addr(USER)), ("freeClaimed(address)", enc_addr(USER))]),
 "DROID": ("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",
   [("FREE_SHARES()", ""), ("freeMinted()", ""), ("paused()", ""), ("freeUsed(address)", enc_addr(USER))]),
 "B749": ("0xb7496DAA943cc136a3f6c2C42147Bb1849A6B1F3",
   [("totalCards()", ""), ("cardsSold()", ""), ("freeCardsRemaining()", ""), ("freeClaimed(address)", enc_addr(USER)), ("quotaLeft(address)", enc_addr(USER))]),
 "PrelaunchSale": ("0x9807a084dcCfFed3F9e530Ab08635ae08c35BF14",
   [("launched()", ""), ("soldFree()", ""), ("FREE_TOTAL()", ""), ("totalSold()", ""), ("soldPaid()", "")]),
 "FABE_sale": ("0xFabE022a5943462fee1Bd221791945DA57510BE8",
   [("freeSharesRemaining()", ""), ("FREE_SHARES()", ""), ("totalShares()", "")]),
 "UPONLY": ("0x1ddBcbA032bc0D80A69B58D91C292aB83119cbc3",
   [("launched()", ""), ("soldFree()", ""), ("FREE_TOTAL()", ""), ("totalSold()", ""), ("soldPaid()", "")]),
 "QAGENT2": ("0xE3a4f3099a2136e0e66202A665815caB8FFA2704",
   [("sharesMinted()", ""), ("freeMinted()", ""), ("mintingOpen()", ""), ("freeAvailable(address)", enc_addr(USER)), ("freeClaimed(address)", enc_addr(USER))]),
 "S723": ("0x723BA73f3480628DD909798367fd47D763C8B5c8",
   [("freeMinted()", ""), ("mintingOpen()", ""), ("freeAvailable(address)", enc_addr(USER)), ("freeClaimed(address)", enc_addr(USER))]),
 "Sevaris_extra": ("0x73085868F57C46E09C7b70AdFda6E6b806222Af0",
   [("saleOpen()", ""), ("freeAvailable(address)", enc_addr(USER)), ("freeClaimed(address)", enc_addr(USER)), ("hasAgentId(address)", enc_addr(USER))]),
}
result = {"block": block()}
def work(item):
    name, addr = item
    return name, collect(addr, GEN)
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
    for name, vals in ex.map(work, targets.items()):
        result[name] = vals
for name, (addr, tests) in extra.items():
    result[name] = collect(addr, tests)
json.dump(result, open(BASE + "run-2026-11-02-1701-read.json", "w"), indent=1)
print("BLOCK", result["block"])
for name in targets:
    v = result[name]
    fc = v.get("freeClaimed()"); fs = v.get("FREE_SUPPLY()"); fm = v.get("freeMinted()"); fl = v.get("freeLeft()")
    pct = None
    if fc is not None and fs: pct = round(100 * fc / fs, 2)
    elif fm is not None and fl is not None and (fm + fl): pct = round(100 * fm / (fm + fl), 2)
    print(f"{name}: ts={v.get('totalSupply()')} fc={fc} fs={fs} fm={fm} fl={fl} pct={pct} mintedBy={v.get('mintedBy(address)')} freeUsed={v.get('freeUsed(address)')} bal={v.get('balanceOf(address)')} owner={v.get('owner()')}")
for name in extra:
    print(name, result[name])
