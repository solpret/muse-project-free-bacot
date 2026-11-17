import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0), None
        except Exception as ex: err = f"{type(ex).__name__}: {str(ex)[:120]}"
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
def words(val):
    if not val: return None
    b = bytes.fromhex(val[2:])
    return [int.from_bytes(b[i:i+32], "big") for i in range(0, len(b), 32)]
result = {"block": block()}
CILOK = "0x01E3E2FE09cB34AD4C6f8090Cb2BD7E098484C9b"
result["Cilok"] = collect(CILOK, [("totalMinted()", ""), ("freeMinted()", ""), ("FREE_SUPPLY()", ""), ("MAX_SUPPLY()", ""), ("freeOpen()", ""), ("freeClosedForever()", ""), ("paidMinted()", ""), ("agentGateEnabled()", ""), ("freeClaimed(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])])
NFTS = {"Gearpixel": "0x9560703c474Ed34df8415Aa715991D15B9b3c47e", "Skelebop": "0xaB5183443e2B82333A4b173e55bb38cCe7c46b01"}
tests = [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""), ("MAX_SUPPLY()", ""), ("mintOpen()", ""), ("mintedBy(address)", enc_addr(USER)[2:]), ("freeFor(address)", enc_addr(USER)[2:]), ("freeUsed(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])]
for nm, addr in NFTS.items():
    result[nm] = collect(addr, tests)
    v, e = call(addr, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(1)[2:])
    result[nm]["quote_user_1"] = {"words": words(v), "raw": v, "error": e}
print(json.dumps(result, indent=1))
json.dump(result, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0401-cilok.json", "w"), indent=1)
