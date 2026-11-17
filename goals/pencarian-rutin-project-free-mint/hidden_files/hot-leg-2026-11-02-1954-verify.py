#!/usr/bin/env python3
"""Hot-leg 19:54 lean verify: ORBIT + e45b + track-B pending + compact reread (concurrent). Read-only."""
import json, re, sys, urllib.request, concurrent.futures
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0), None
        except Exception as e: err = f"{type(e).__name__}: {str(e)[:120]}"
    return None, err
def collect(to, tests):
    out = {}
    for name, arg in tests:
        v, err = call(to, sel(name) + arg)
        try: iv = int(v, 16) if v else None
        except Exception: iv = None
        out[name] = iv
    return out
def block():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
    return None

U = enc_addr(USER)[2:]
ORBIT = "0x6e0c18185f584781592fa972ff2b7566c5532e12"
ORBIT_TOK = "0xc09eea8ecc744e0adf299c849ccc9fb897a545d8"
E45B = "0xe45b4a6755e29EaDbc3fF90CB15207F56B7B43B1"
out = {"block": block()}
out["ORBIT"] = collect(ORBIT, [("totalCards()", ""), ("cardsSold()", ""), ("freeCardsRemaining()", ""),
    ("freeGiven()", ""), ("gateOn()", ""), ("paused()", ""), ("freeClaimed(address)", U),
    ("quotaLeft(address)", U), ("mintedBy(address)", U), ("owner()", ""), ("token()", ""), ("tokensPerShare()", "")])
out["ORBIT_quote_user1"] = collect(ORBIT, [("quote(address,uint256)", U + enc_uint(1)[2:])])
out["ORBIT_quoteForCaller1"] = collect(ORBIT, [("quoteForCaller(uint256)", enc_uint(1)[2:])])
out["ORBIT_token_bal_USER"] = collect(ORBIT_TOK, [("balanceOf(address)", U)])
out["E45B"] = collect(E45B, [("token()", ""), ("pair()", ""), ("MAX_FREE()", ""), ("MAX_SHARES()", ""),
    ("sharesMinted()", ""), ("freeMinted()", ""), ("paidShares()", ""), ("mintingOpen()", ""),
    ("poolOpen()", ""), ("freeAvailable(address)", U), ("freeClaimed(address)", U),
    ("mintedBy(address)", U), ("hasAgentId(address)", U), ("TOKENS_PER_SHARE()", ""), ("PRICE()", ""), ("deadline()", "")])
out["E45B_quote"] = collect(E45B, [("quote(uint256)", enc_uint(0)[2:]), ("quote(uint256)", enc_uint(1)[2:])])
tok_raw = out["E45B"].get("token()")
if isinstance(tok_raw, int) and tok_raw:
    tok = "0x" + format(tok_raw, "040x")
    out["E45B_token_addr"] = tok
    out["E45B_token_bal_USER"] = collect(tok, [("balanceOf(address)", U)])
    out["E45B_token_name"] = collect(tok, [("name()", ""), ("symbol()", "")])
else:
    out["E45B_token_addr"] = None
# Track-B pending
out["TrackB_MINT"] = collect("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
    [("launched()", ""), ("tokenClaimed(address)", U), ("totalShares()", ""), ("isRefundPhase()", ""), ("failed()", "")])
out["Pollen_MINT"] = collect("0x3E9B4F58e2bC9b064F002cF89531e12FC5CfA00f",
    [("launched()", ""), ("phase()", ""), ("pollenAgents()", ""), ("paidSold()", "")])

# Compact reread: addresses parsed from 1949 script dicts
py1949 = open(BASE + "hot-leg-2026-11-02-1949.py").read()
pairs = re.findall(r'"([A-Za-z0-9_]+)"\s*:\s*"(0x[0-9a-fA-F]{40})"', py1949)
addr_map = {}
for n, a in pairs:
    addr_map.setdefault(n, a)
# plus explicit singles
for n, a in [("SEVARIS", "0x73085868F57C46E09C7b70AdFda6E6b806222Af0"),
             ("QAG", "0x93eAbc3f8496A304eb0CDC3F1AD00CCCdb877877"),
             ("NIUBI", "0x094DA228770A141bB2aCaE22608A08D66a8f789a"),
             ("DROID", "0xFcF6388DD3bcC674c095273aB479C7e54dd5E177"),
             ("B749", "0xb7496DAA943cc136a3f6c2C42147Bb1854A6B1F3"),
             ("PREL", "0x9807a084dcCfFed3F9e530Ab08635ae08c35BF14"),
             ("FABES", "0xFabE022a5943462fee1Bd221791945DA57510BE8"),
             ("UPONLY", "0x1ddBcbA032bc0D80A69B58D91C292aB83119cbc3"),
             ("S723", "0x723BA73f3480628DD909798367fd47D763C8B5c8"),
             ("QAGENT2", "0xE3a4f3099a2136e0e66202A665815caB8FFA2704"),
             ("WAG", "0x5091F75CdFEf44883a5b24ff453322De8ef24aFd")]:
    addr_map.setdefault(n, a)
print("REREAD_TARGETS", len(addr_map))
early = [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""),
         ("mintedBy(address)", U), ("freeUsed(address)", U), ("balanceOf(address)", U)]
def do(item):
    n, a = item
    return n, collect(a, early)
reread = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=16) as ex:
    for n, v in ex.map(do, sorted(addr_map.items())):
        reread[n] = v
out["reread_block"] = block()
out["reread"] = reread
json.dump(out, open(BASE + "hot-leg-2026-11-02-1954-verify.json", "w"), indent=1)
for k, v in out.items():
    if k in ("reread",): continue
    print(k, v)
for n, v in reread.items():
    print("REREAD", n, v)
