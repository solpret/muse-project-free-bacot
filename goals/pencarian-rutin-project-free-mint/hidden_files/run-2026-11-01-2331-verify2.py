#!/usr/bin/env python3
"""2331 run verify part 2: correct string decode + sale quote/freeClaimed. Read-only."""
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
        except Exception as e: err = f"{type(e).__name__}: {str(e)[:120]}"
    return None, err
def sstr(to, fn):
    val, err = call(to, sel(fn))
    if not val: return {"error": err}
    try:
        b = bytes.fromhex(val[2:])
        ln = int.from_bytes(b[32:64], "big")
        return {"str": b[64:64+ln].decode(errors="ignore")}
    except Exception as e: return {"error": str(e)[:120], "raw": val[:160]}
def words(val):
    if not val: return None
    b = bytes.fromhex(val[2:])
    return [int.from_bytes(b[i:i+32], "big") for i in range(0, len(b), 32)]
res = {}
for a in ["0x672c1dF4F7121DaCBD3504995441C47d2fAbCdDC","0x11fa2C4b71EcE40f242992a08C4ACC6C23c99Ca0",
          "0x787b522d48084A83b8B1b0C206aA4A12B1FD1cc2","0x0AC5591d1B980C7bE16861d722E59E21E2624868","0x2C215262635E66c798c5a1Ba4411fA9F06852bDD",
          "0xF54E80a86FCF71Fa2F86Eb9bC2f21f36B94961b7",
          "0x1ed3BF35e4DA25b1289C27ddbD82f0A38DDCee8b","0x8362e6a5F38427d8d719EA47f08890784F6023DC","0x2Df4Ef534cbBe1a8F647e24D0f8C75ECe74D8288"]:
    res[a] = {"name": sstr(a, "name()"), "symbol": sstr(a, "symbol()")}
SALE = "0xA74bEF84304D8838db798faE96fb873dd46fB4C1"
aid, err = call(SALE, sel("agentIdOf(address)") + enc_addr(USER)[2:])
res["SALE_agentId"] = {"raw": aid, "error": err}
if aid:
    fc, err2 = call(SALE, sel("freeClaimed(bytes32)") + aid[2:])
    res["SALE_freeClaimed_user"] = {"words": words(fc), "raw": fc, "error": err2}
    for q in (0, 1):
        v, e = call(SALE, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(q)[2:])
        res[f"SALE_quote_user_{q}"] = {"words": words(v), "raw": v, "error": e}
    sb, e = call(SALE, sel("sharesByWallet(address)") + enc_addr(USER)[2:])
    res["SALE_sharesByWallet"] = {"words": words(sb), "error": e}
print(json.dumps(res, indent=1))
json.dump(res, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-01-2331-verify2.json", "w"), indent=1)
