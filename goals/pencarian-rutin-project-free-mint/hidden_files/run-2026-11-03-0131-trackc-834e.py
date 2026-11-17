#!/usr/bin/env python3
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return ("%064x" % n)
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
    return None
def iv(v):
    try: return int(v, 16) if v else None
    except Exception: return None
def av(v):
    try: return "0x" + v[-40:] if v else None
    except Exception: return None
SALE = "0x834e5BC43Aa91bEbEB31B97eaFA1bCb2F4286d97"
out = {}
for ep in EPS:
    try: out["block"] = int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16); break
    except Exception: pass
tests = [("AGENT_REGISTRY()", ""), ("MAX_SHARES_PER_WALLET()", ""), ("PRICE()", ""), ("TOKENS_PER_SHARE()", ""),
         ("TOTAL_SHARES()", ""), ("deadline()", ""), ("freeClaimed()", ""), ("freeSharesGiven()", ""),
         ("mintOpen()", ""), ("token()", ""), ("totalSharesSold()", ""), ("owner()", "")]
for fn, arg in tests:
    v = call(SALE, sel(fn) + arg)
    out[fn] = av(v) if fn in ("AGENT_REGISTRY()", "token()", "owner()") else iv(v)
    print(fn, out[fn])
out["hasAgentId(user)"] = iv(call(SALE, sel("hasAgentId(address)") + enc_addr(USER)))
out["freeClaimedBy(user)"] = iv(call(SALE, sel("freeClaimedBy(address)") + enc_addr(USER)))
out["sharesOf(user)"] = iv(call(SALE, sel("sharesOf(address)") + enc_addr(USER)))
out["quote(0)"] = iv(call(SALE, sel("quote(uint256)") + enc_u(0)))
out["quote(1)"] = iv(call(SALE, sel("quote(uint256)") + enc_u(1)))
print("hasAgentId(user)", out["hasAgentId(user)"], "freeClaimedBy(user)", out["freeClaimedBy(user)"], "sharesOf(user)", out["sharesOf(user)"], "quote0", out["quote(0)"], "quote1", out["quote(1)"])
tok = out.get("token()")
if tok:
    for fn in ["name()", "symbol()", "decimals()", "totalSupply()"]:
        v = call(tok, sel(fn))
        if fn in ("name()", "symbol()"):
            try:
                raw = bytes.fromhex(v[2:]) if v else b""
                # abi string: offset, len, data
                ln = int.from_bytes(raw[64:96], "big") if len(raw) >= 96 else 0
                out["token_" + fn] = raw[96:96+ln].decode("utf-8", "ignore") if ln else None
            except Exception as e: out["token_" + fn] = f"ERR {e}"
        else: out["token_" + fn] = iv(v)
        print("token", fn, out["token_" + fn])
json.dump(out, open(BASE + "run-2026-11-03-0131-trackc-834e.json", "w"), indent=1)
print("BLOCK", out["block"])
