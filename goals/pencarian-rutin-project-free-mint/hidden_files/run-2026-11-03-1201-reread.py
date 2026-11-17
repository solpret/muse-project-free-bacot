#!/usr/bin/env python3
"""Main run 2026-11-03 11:01 WIB targeted re-read. Read-only."""
import json, concurrent.futures, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0), None
        except Exception as e: err = f"{type(e).__name__}: {str(e)[:160]}"
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
STD = [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""), ("freeMinted()", ""),
       ("mintedBy(address)", enc_addr(USER)[2:]), ("freeUsed(address)", enc_addr(USER)[2:]),
       ("balanceOf(address)", enc_addr(USER)[2:]), ("owner()", ""), ("mintOpen()", "")]
TARGETS = {
  "Sentrix": "0xb7dce0412BB89dE075413855875D1DB31AC89E8f",
  "Dragonito": "0x56E2604A33F1ccBc00376046a767cCE45B50F592",
  "Kigae": "0x33fd00aF8bfF3db611D3222D394da33eaaa6a566",
  "WildDuck": "0xac7C0e1f36E15DBa7ED32Bf6e72D83095Ff8fd10",
  "LuckyKoi": "0x30bDb65093081317F64cfe95921D5c855B699aC8",
  "Animora": "0x150699b44B36b542B9F954272bDD0aC3fDD9519b",
  "Golemar": "0x4e06728894F3f31CbB32B97d6905639FfE2a147B",
  "Homunqul": "0x5539dD54c00094Cbd186f08AA2d8fF3A8c098ddE",
  "Praxion": "0xEA1e4AA5ecD147035eB005aDc8013959bA852799",
  "Eidolyn": "0x94c4834B186938F95EDC67FF0536Ac17F3102523",
  "Aura": "0xacc6e2F1aaE42B2E5FF2758Ff078E4B1bfAc7DB1",
  "DigDown": "0xF464550f1d744793893C0ce09b89269Ed726d796",
  "Deepvane": "0xDd682169A6699eA7feF7E6E15C727Cf970C98d97",
  "Neuroveil": "0x7BCA844AD4cD95b5B30ecC3885dfBab45F38e99b",
  "AgentisVox": "0xe7b329fC7F8294f75bAa40dD438940Ba83b6168c",
  "Autonym": "0x7Fa142C23805387c94fbc4AdEbf1168A7145f528",
  "Noesyn": "0x69e2B3df4ecedBf7FC89085707a8cb9163F5e1BC",
  "Synaptik": "0xE5523bf6AA0F92aCC7d2898F65596a0A088a8f0F",
  "Logiphon": "0x14Fb2182311dEBfA3fa6EdbE17278cd4ddBDB619",
  "SoarmSale": "0x7ba14e1119d31E876Cc4aa52a0bcB9E43C841799",
  "HivePollen": "0x3E9B4F58e2bC9b064F002cF89531e12FC5CfA00f",
      }
EXTRA = {
  "WildDuck": [("freeMintCount(address)", enc_addr(USER)[2:]), ("hasAgentId(address)", enc_addr(USER)[2:])],
  "LuckyKoi": [("remaining()", ""), ("freeClaimed(address)", enc_addr(USER)[2:])],
  "Deepvane": "0xDd682169A6699eA7feF7E6E15C727Cf970C98d97",
  "Neuroveil": "0x7BCA844AD4cD95b5B30ecC3885dfBab45F38e99b",
  "AgentisVox": "0xe7b329fC7F8294f75bAa40dD438940Ba83b6168c",
  "Autonym": "0x7Fa142C23805387c94fbc4AdEbf1168A7145f528",
  "Noesyn": "0x69e2B3df4ecedBf7FC89085707a8cb9163F5e1BC",
  "Synaptik": "0xE5523bf6AA0F92aCC7d2898F65596a0A088a8f0F",
  "Logiphon": "0x14Fb2182311dEBfA3fa6EdbE17278cd4ddBDB619",
  "SoarmSale": [("freeSharesLeft()", ""), ("sharesSold()", ""), ("sharesOf(address)", enc_addr(USER)[2:]), ("freeClaimed(address)", enc_addr(USER)[2:])],
  "Kigae": [("freeLeft()", ""), ("hasAgentId(address)", enc_addr(USER)[2:])],
  "Sentrix": [("freeFor(address)", enc_addr(USER)[2:]), ("freeLeft()", "")],
  "Dragonito": [("freeFor(address)", enc_addr(USER)[2:]), ("freeLeft()", "")],
  "Aura": [("freeRemaining()", ""), ("freeMinted()", "")],
  "Deepvane": [("freeLeft()", ""), ("freeFor(address)", enc_addr(USER)[2:])],
  "Neuroveil": [("freeLeft()", ""), ("freeFor(address)", enc_addr(USER)[2:])],
  "AgentisVox": [("freeLeft()", ""), ("freeFor(address)", enc_addr(USER)[2:])],
  "Autonym": [("freeLeft()", ""), ("freeFor(address)", enc_addr(USER)[2:])],
  "Noesyn": [("freeLeft()", ""), ("freeFor(address)", enc_addr(USER)[2:])],
  "Synaptik": [("freeLeft()", ""), ("freeFor(address)", enc_addr(USER)[2:])],
  "Logiphon": [("freeLeft()", ""), ("freeFor(address)", enc_addr(USER)[2:])],
  "HivePollen": [("launched()", ""), ("phase()", ""), ("pollenAgents()", ""), ("paidSold()", ""), ("claimed(address)", enc_addr(USER)[2:])],
}
def work(item):
    n, a = item
    return n, collect(a, STD + EXTRA.get(n, []))
result = {"block": block()}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    for n, out in ex.map(work, TARGETS.items()):
        result[n] = out
json.dump(result, open(BASE + "run-2026-11-03-1201-reread.json", "w"), indent=1)
print("block", result["block"])
for k, v in result.items():
    if k == "block": continue
    print(k, {kk: vv.get("int") for kk, vv in v.items()})
    raw = v.get("owner()", {}).get("raw") or ""
    if len(raw) >= 42: print(k, "owner_addr", "0x" + raw[-40:])
