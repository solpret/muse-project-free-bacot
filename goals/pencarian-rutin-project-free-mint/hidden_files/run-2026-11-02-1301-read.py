#!/usr/bin/env python3
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0), None
        except Exception as e: err = f"{type(e).__name__}: {str(e)[:120]}"
    return None, err
def block():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
    return None
def collect(to, tests):
    out = {}
    for name, arg in tests:
        val, err = call(to, sel(name) + arg)
        try: iv = int(val, 16) if val else None
        except Exception: iv = None
        out[name] = iv
    return out
B = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(B + "onchain-snapshot.json"))
res = {"block": block()}
std = [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""), ("MAX_SUPPLY()", ""), ("mintOpen()", ""), ("mintedBy(address)", enc_addr(USER)[2:]), ("freeUsed(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:]), ("quote(address,uint256)", enc_addr(USER)[2:] + format(1, "064x"))]
watch = {}
for k, v in snap["contracts"].items():
    if v.get("address") and "minted-by-user" not in str(v.get("status")):
        watch[k] = v["address"]
res["watchlist"] = {k: collect(a, std) for k, a in watch.items()}
new5 = {"HOT-0x3203": "0x3203D93cE535c2ec88c99d1967324Fe556A4e8f6", "HOT-0xa1bC": "0xa1bC72EcEC9f1F73Be9ED0c21b5cB880f42dA1A3", "HOT-0xAB23": "0xAB23259Cac7D87d8cfE0ADaba80827d3e3AcC99F", "HOT-0x5534": "0x553484EC13486cAec4cdB884B9953e381dd1d66B", "HOT-0x6937": "0x693777E674fa13a8318821919296d52E90898191"}
res["hot5"] = {k: collect(a, std + [("name()", ""), ("symbol()", "")]) for k, a in new5.items()}
# pending claims
res["binanceai"] = collect("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [("launched()", ""), ("tokenClaimed(address)", enc_addr(USER)[2:]), ("isRefundPhase()", ""), ("failed()", ""), ("totalShares()", "")])
res["pollen"] = collect("0x3E9B4F58e2bC9b064F002cF89531e12FC5CfA00f", [("launched()", ""), ("phase()", ""), ("pollenAgents()", ""), ("paidSold()", ""), ("accounts(address)", enc_addr(USER)[2:])])
# track-C watchlist: QILIN sale, NIUBI sale, DROID sale, 9807 sale
res["trackc"] = {
 "QILIN": collect("0xbb77f247e6b57f4dcd09c5900b2ffc4250b6b88f", [("freeCardsRemaining()", ""), ("freeClaimed(address)", enc_addr(USER)[2:]), ("cardsSold()", "")]),
 "NIUBI": collect("0x094DA228770A141bB2aCaE22608A08D66a8f789a", [("freeClaimed(address)", enc_addr(USER)[2:]), ("mintedBy(address)", enc_addr(USER)[2:])]),
 "DROID": collect("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177", [("freeMinted()", ""), ("FREE_SUPPLY()", ""), ("freeUsed(address)", enc_addr(USER)[2:])]),
 "PRE9807": collect("0x9807a084dcCfFed3F9e530Ab08635ae08c35BF14", [("soldFree()", ""), ("FREE_TOTAL()", "")]),
}
json.dump(res, open(B + "run-2026-11-02-1301-read.json", "w"), indent=1)
print("block", res["block"], "watch", len(res["watchlist"]))
for k, v in res["watchlist"].items():
    ts, fc, fs = v.get("totalSupply()"), v.get("freeClaimed()"), v.get("FREE_SUPPLY()")
    pct = f"{fc/fs*100:.2f}%" if fc is not None and fs else "-"
    print(f"{k}: ts={ts} free={fc}/{fs} {pct} userMinted={v.get('mintedBy(address)')} freeUsed={v.get('freeUsed(address)')} bal={v.get('balanceOf(address)')} quote={v.get('quote(address,uint256)')}")
print("HOT5:")
for k, v in res["hot5"].items(): print(k, v)
print("binanceai", res["binanceai"]); print("pollen", res["pollen"]); print("trackc", res["trackc"])
