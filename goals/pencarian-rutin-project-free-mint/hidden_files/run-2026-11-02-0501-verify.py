import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
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
res = {"block": block()}
NULL = "0x9395e207F9928657237DE96ffB12340094c073cd"
res["NULLSECTOR"] = collect(NULL, [("totalSupply()", ""), ("MAX_SUPPLY()", ""), ("mintOpen()", ""), ("freeClaimed(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])])
ROOT = "0x900a89FA78b64D6C26B76A314FEd1d6caE9e7a74"
res["Root"] = collect(ROOT, [("totalMinted()", ""), ("FREE_SUPPLY()", ""), ("MAX_SUPPLY()", ""), ("mintedBy(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:]), ("costFor(uint256)", enc_uint(1)[2:]), ("currentPrice()", "")])
print(json.dumps(res, indent=1))
json.dump(res, open("run-2026-11-02-0501-verify.json", "w"), indent=1)
