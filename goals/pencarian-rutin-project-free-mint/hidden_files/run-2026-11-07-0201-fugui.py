#!/usr/bin/env python3
"""FUGUI second-set sale contract on-chain verification, run 2026-11-07 0201 WIB.
Read-only eth_call via fast_rpc. No signing."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak

SALE = "0xa0b30b8ff77826e2288a28d2c560ecf3476828f6"
TOKEN = "0x098efa9227ee4cbb4f9c25da812d6d61a0310230"
TOKEN1 = "0xebcc9431cce0d00143b641ec2650a11a970a2366"  # FUGUI first set ("991"), per 1328.ai post
MAIN = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
W2 = "0xcf3c6fc1bf670a8d3f03436395286f86dbee7418"
W3 = "0x71bcee31054137448e78f2e28dbe3160aae3e235"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def enc_addr(a):
    return a.lower().replace("0x", "").rjust(64, "0")

def call(addr, sig, args_hex=""):
    data = sel(sig) + args_hex
    last = None
    for ep in EPS:
        try:
            r = _single(ep, "eth_call", [{"to": addr, "data": data}, "latest"], 10, retries=0)
            if isinstance(r, str) and r.startswith("0x"):
                return r
            last = r
        except Exception as e:
            last = str(e)
    return {"error": str(last)}

def u256(r):
    if isinstance(r, dict):
        return r
    return int(r, 16)

def s256(r):
    if isinstance(r, dict):
        return r
    n = int(r, 16)
    # decode string: offset 32, len 32, data
    b = bytes.fromhex(r[2:])
    ln = int.from_bytes(b[32:64], "big")
    return b[64:64+ln].decode("utf-8", "replace")

def b256(r):
    if isinstance(r, dict):
        return r
    return int(r, 16) != 0

def addr256(r):
    if isinstance(r, dict):
        return r
    return "0x" + r[-40:]

out = {"run": "2026-11-07-0201", "sale": SALE, "token": TOKEN, "token_first_set": TOKEN1}
sale_views = {}
for fn in ["FREE_SHARES()", "TOTAL_SHARES()", "TOKENS_PER_SHARE()", "PRICE_PER_SHARE()",
           "MAX_PER_WALLET()", "LP_RESERVE()", "deadline()", "freeMinted()", "totalMinted()",
           "paidMinted()", "usdtRaised()"]:
    sale_views[fn] = u256(call(SALE, fn))
for fn in ["finalized()", "tradingOpen()"]:
    pass
sale_views["finalized"] = b256(call(SALE, "finalized()"))
sale_views["deadline_raw"] = sale_views.pop("deadline()")
for fn, dec in [("token()", addr256), ("treasury()", addr256), ("USDT()", addr256),
                ("AGENT_ID_REGISTRY()", addr256), ("owner()", addr256)]:
    sale_views[fn] = dec(call(SALE, fn))
out["sale_views"] = sale_views

wallets = {}
for name, w in [("main", MAIN), ("w2", W2), ("w3", W3)]:
    d = {}
    d["freeClaimed"] = b256(call(SALE, "freeClaimed(address)", enc_addr(w)))
    d["sharesOf"] = u256(call(SALE, "sharesOf(address)", enc_addr(w)))
    d["hasAgentId"] = b256(call(SALE, "hasAgentId(address)", enc_addr(w)))
    ui = call(SALE, "userInfo(address)", enc_addr(w))
    if isinstance(ui, str) and len(ui) >= 130:
        d["userInfo_claimed"] = int(ui[2:66], 16) != 0
        d["userInfo_shares"] = int(ui[66:130], 16)
    else:
        d["userInfo"] = ui
    d["token_balance"] = u256(call(TOKEN, "balanceOf(address)", enc_addr(w)))
    d["token1_balance"] = u256(call(TOKEN1, "balanceOf(address)", enc_addr(w)))
    wallets[name] = d
out["wallets"] = wallets

tok = {}
for fn, dec in [("name()", s256), ("symbol()", s256), ("decimals()", u256),
                ("totalSupply()", u256), ("TOTAL_SUPPLY()", u256),
                ("saleContract()", addr256)]:
    tok[fn] = dec(call(TOKEN, fn))
tok["tradingOpen"] = b256(call(TOKEN, "tradingOpen()"))
out["token_views"] = tok

tok1 = {}
for fn, dec in [("name()", s256), ("symbol()", s256), ("decimals()", u256),
                ("totalSupply()", u256)]:
    tok1[fn] = dec(call(TOKEN1, fn))
tok1["tradingOpen"] = b256(call(TOKEN1, "tradingOpen()"))
out["token_first_set_views"] = tok1

# block number for timestamp context
blk = _single(EPS[0], "eth_blockNumber", [], 10, retries=0)
out["blockNumber"] = int(blk, 16) if isinstance(blk, str) else blk

json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-07-0201-fugui-onchain.json", "w"), indent=1)
print(json.dumps(out, indent=1))
