#!/usr/bin/env python3
"""Free-mint-search run 2026-11-01 21:01 WIB: HIVE + Bubblebruin + TrackB re-reads. Read-only."""
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
HIVE = "0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77"
BUB = "0xc205F8c74733D914776D66cBc4Cf10BF701D96Aa"
MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN = "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
PAIR = "0x903ACC22B9BABCD427bfb9AF2C27a27a5aC7c698"

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

hive_tests = [("totalSupply()", ""), ("START_TIME()", ""), ("FREE_SUPPLY()", ""),
    ("FREE_PER_WALLET()", ""), ("totalPaid()", ""), ("freeMintedBy(address)", enc_addr(USER)[2:]),
    ("balanceOf(address)", enc_addr(USER)[2:]), ("quote(uint256)", enc_uint(1)[2:]),
    ("currentPrice()", ""), ("name()", ""), ("symbol()", "")]
bub_tests = [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""), ("MAX_SUPPLY()", ""),
    ("mintOpen()", ""), ("mintedBy(address)", enc_addr(USER)[2:]), ("freeFor(address)", enc_addr(USER)[2:]),
    ("freeUsed(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])]
tb_tests = [("launched()", ""), ("tokenClaimed(address)", enc_addr(USER)[2:]), ("totalShares()", ""),
    ("isRefundPhase()", ""), ("failed()", ""), ("FREE_SHARES()", "")]
tok_tests = [("balanceOf(address)", enc_addr(MINT)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])]
pair_tests = [("getReserves()", ""), ("token0()", ""), ("token1()", "")]

result = {"block": block(),
  "HIVE": collect(HIVE, hive_tests),
  "Bubblebruin": collect(BUB, bub_tests),
  "TrackB_MINT": collect(MINT, tb_tests),
  "TrackB_TOKEN_bal_MINT": collect(TOKEN, [("balanceOf(address)", enc_addr(MINT)[2:])]),
  "TrackB_TOKEN_bal_USER": collect(TOKEN, [("balanceOf(address)", enc_addr(USER)[2:])]),
  "TrackB_PAIR": collect(PAIR, pair_tests)}
print(json.dumps(result, indent=1))
json.dump(result, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-01-2101-read.json", "w"), indent=1)
