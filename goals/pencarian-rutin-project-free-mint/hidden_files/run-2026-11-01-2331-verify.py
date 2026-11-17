#!/usr/bin/env python3
"""2331 run: verify Sourcify shape hits. Read-only."""
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
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
def call(to, data):
    for ep in EPS:
        try:
            return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0), None
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:120]}"
    return None, err
def code(to):
    for ep in EPS:
        try:
            return _single(ep, "eth_getCode", [to, "latest"], 8, retries=0), None
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:120]}"
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
        try: iv = int(val, 16) if val and len(val) <= 66 else None
        except Exception: iv = None
        out[name] = {"int": iv, "raw": (val[:200] if val else None), "error": err if val is None else None}
    return out
def strval(to, name):
    # decode string return: offset/len/data
    val, err = call(to, sel(name))
    if not val: return {"error": err}
    try:
        b = bytes.fromhex(val[2:])
        ln = int.from_bytes(b[64:96], "big")
        return {"str": b[96:96+ln].decode(errors="ignore")}
    except Exception as e:
        return {"error": str(e)[:120], "raw": val[:200]}
res = {"block": block()}
SALE = "0xA74bEF84304D8838db798faE96fb873dd46fB4C1"
sale_tests = [("sharesMinted()", ""), ("freeClaimed()", ""), ("FREE_SHARES()", ""), ("MAX_SHARES()", ""),
    ("poolOpen()", ""), ("saleFailed()", ""), ("poolOpenFailed()", ""), ("deadline()", ""),
    ("paidShares()", ""), ("token()", ""), ("registry()", ""), ("agentIdOf(address)", enc_addr(USER)[2:]),
    ("sharesByWallet(address)", enc_addr(USER)[2:]), ("quote(uint256)", enc_uint(1)[2:]), ("quote(uint256)", enc_uint(0)[2:])]
res["SALE_A74b"] = collect(SALE, sale_tests)
tok, _ = call(SALE, sel("token()"))
if tok:
    taddr = "0x" + tok[-40:]
    res["SALE_A74b_token"] = taddr
    res["SALE_A74b_token_info"] = {"name": strval(taddr, "name()"), "symbol": strval(taddr, "symbol()")}
NFTS = ["0x672c1dF4F7121DaCBD3504995441C47d2fAbCdDC","0x11fa2C4b71EcE40f242992a08C4ACC6C23c99Ca0",
        "0x787b522d48084A83b8B1b0C206aA4A12B1FD1cc2","0x0AC5591d1B980C7bE16861d722E59E21E2624868",
        "0x2C215262635E66c798c5a1Ba4411fA9F06852bDD"]
nft_tests = [("totalSupply()", ""), ("freeClaimed()", ""), ("freeLeft()", ""), ("FREE_SUPPLY()", ""),
    ("MAX_SUPPLY()", ""), ("mintOpen()", ""), ("mintedBy(address)", enc_addr(USER)[2:]),
    ("freeUsed(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:]),
    ("AGENT_ID()", ""), ("PRICE()", ""), ("quote(uint256)", enc_uint(1)[2:])]
for a in NFTS:
    res["NFT_"+a] = collect(a, nft_tests)
    res["NFT_"+a+"_info"] = {"name": strval(a, "name()"), "symbol": strval(a, "symbol()")}
IDENT = ["0x1ed3BF35e4DA25b1289C27ddbD82f0A38DDCee8b","0x8362e6a5F38427d8d719EA47f08890784F6023DC","0x2Df4Ef534cbBe1a8F647e24D0f8C75ECe74D8288"]
id_tests = [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SHARES()", ""), ("PAID_SHARES()", ""),
    ("sold()", ""), ("launched()", ""), ("phase()", ""), ("startedAt()", ""), ("start()", ""),
    ("freeClaimedById(address)", enc_addr(USER)[2:]), ("mintedById(address)", enc_addr(USER)[2:]),
    ("remainingQuota(address)", enc_addr(USER)[2:]), ("identity(address)", enc_addr(USER)[2:]),
    ("quote(uint256)", enc_uint(1)[2:]), ("pair()", "")]
for a in IDENT:
    res["IDENT_"+a] = collect(a, id_tests)
    res["IDENT_"+a+"_info"] = {"name": strval(a, "name()"), "symbol": strval(a, "symbol()")}
    c, cerr = code(a)
    res["IDENT_"+a+"_code_has_registry"] = (REG[2:].lower() in (c or "").lower()) if c else {"error": cerr}
    c2, _ = code(SALE)
    res["SALE_code_has_registry"] = (REG[2:].lower() in (c2 or "").lower()) if c2 else False
print(json.dumps(res, indent=1))
json.dump(res, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-01-2331-verify.json", "w"), indent=1)
