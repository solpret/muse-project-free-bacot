#!/usr/bin/env python3
"""Main run 2026-11-03 08:31 WIB targeted re-read. Read-only."""
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
  "SoarmSale": "0x7ba14e1119d31E876Cc4aa52a0bcB9E43C841799",
  "SoarmToken": "0x4a02e3824b301a1bf6a8230e56b44b526174ca97",
  "Nvagent4951": "0x4951c7b9a1a0f8b1c9e3b8c7e0a1f2d3e4a5b6c7d8",
}
# fix Nvagent address placeholder: read from snapshot instead
snap = json.load(open(BASE + "onchain-snapshot.json"))
nv = None
for k, v in snap.get("track_c", {}).items():
    if "Nvagent" in k and v.get("address", "").startswith("0x4951"):
        nv = v["address"]
if nv: TARGETS["Nvagent4951"] = nv
else: del TARGETS["Nvagent4951"]
EXTRA = {
  "WildDuck": [("freeMintCount(address)", enc_addr(USER)[2:]), ("hasAgentId(address)", enc_addr(USER)[2:])],
  "LuckyKoi": [("mintStart()", ""), ("mintEnd()", ""), ("remaining()", ""), ("freeClaimed(address)", enc_addr(USER)[2:])],
  "SoarmSale": [("freeSharesLeft()", ""), ("sharesSold()", ""), ("sharesOf(address)", enc_addr(USER)[2:]), ("freeClaimed(address)", enc_addr(USER)[2:])],
  "Kigae": [("freeLeft()", ""), ("hasAgentId(address)", enc_addr(USER)[2:])],
  "Sentrix": [("freeFor(address)", enc_addr(USER)[2:]), ("freeLeft()", ""), ("AGENT_ID()", "")],
  "Dragonito": [("freeFor(address)", enc_addr(USER)[2:]), ("freeLeft()", ""), ("AGENT_ID()", "")],
}
def work(item):
    n, a = item
    tests = STD + EXTRA.get(n, [])
    return n, collect(a, tests)
result = {"block": block()}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    for n, out in ex.map(work, TARGETS.items()):
        result[n] = out
json.dump(result, open(BASE + "run-2026-11-03-0901-reread.json", "w"), indent=1)
print("block", result["block"])
for k, v in result.items():
    if k == "block": continue
    print(k, {kk: vv.get("int") for kk, vv in v.items()})
# owner() raw -> address
for k, v in result.items():
    if isinstance(v, dict) and "owner()" in v:
        raw = v["owner()"].get("raw") or ""
        print(k, "owner_addr", "0x" + raw[-40:] if len(raw) >= 42 else raw)
