#!/usr/bin/env python3
"""Hot-leg 11:34 leg-3 verify: two new S1 sale-shape contracts. Read-only, bounded ~75s."""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/",
       "https://rpc.ankr.com/bsc"]
CONTRACTS = ["0xc4695f19dE428EA37169bBD058463588D511554a",
             "0x05debe4445232205ae7e79d02cb5de5aa0641eff"]
t0 = time.time()
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def call(to, data, timeout=8):
    last = None
    for ep in EPS:
        if time.time() - t0 > 75: return "deadline", ep
        try:
            v = _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], timeout, retries=0)
            return v, ep
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:80]}"
    return None, last
def call_int(to, sig, args=""):
    v, ep = call(to, sel(sig) + args)
    if v in (None, "deadline"): return v
    try: return int(v, 16)
    except Exception: return v
def call_addr(to, sig):
    v = call_int(to, sig)
    if isinstance(v, int) and v: return "0x" + format(v, "040x")
    return v
def call_str(to, sig):
    v, ep = call(to, sel(sig))
    if v in (None, "deadline") or not isinstance(v, str) or len(v) < 130: return v
    try:
        ln = int(v[130:194], 16)
        raw = bytes.fromhex(v[194:194+ln*2])
        return raw.decode("utf-8", "replace")
    except Exception: return v
out = {"block": None}
for ep in EPS:
    try: out["block"] = int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16); break
    except Exception: pass
U = enc_addr(USER)
for c in CONTRACTS:
    d = {}
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{c}?fields=abi",
                                     headers={"User-Agent": "hot-leg/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r: meta = json.load(r)
        abi = meta.get("abi", [])
        fns = sorted({e["name"] for e in abi if e.get("type") == "function"})
        d["abi_functions"] = fns
        d["name"] = call_str(c, "name()")
        d["symbol"] = call_str(c, "symbol()")
        d["token"] = call_addr(c, "token()")
        for view in ["freeSharesRemaining()", "freeClaimed()", "freeMinted()", "totalMinted()",
                     "totalSupply()", "mintOpen()", "mintingOpen()", "poolOpen()", "paused()",
                     "FREE_SUPPLY()", "FREE_SLOTS()", "FREE_AMOUNT()", "tokensPerShare()",
                     "TOKENS_PER_SHARE()", "totalCards()", "cardsSold()", "freeCardsRemaining()",
                     "agentRegistry()", "registry()"]:
            if view.split("(")[0] in fns:
                d[view] = call_int(c, view)
        for view in ["freeLeft(address)", "freeFor(address)", "freeClaimed(address)",
                     "freeUsed(address)", "mintedBy(address)", "freeAvailable(address)",
                     "quotaLeft(address)", "balanceOf(address)"]:
            if view.split("(")[0] in fns:
                d[view + "_user"] = call_int(c, view, U)
        for q in ["quote(address,uint256)", "quote(uint256)", "quoteForCaller(uint256)"]:
            if q.split("(")[0] in fns:
                args = (U + enc_uint(1)) if q.startswith("quote(address") else enc_uint(1)
                d[q + "_1"] = call_int(c, q, args)
        if isinstance(d.get("token"), str) and d["token"].startswith("0x"):
            tok = d["token"]
            d["token_name"] = call_str(tok, "name()")
            d["token_symbol"] = call_str(tok, "symbol()")
            d["token_balance_user"] = call_int(tok, "balanceOf(address)", U)
    except Exception as e:
        d["error"] = f"{type(e).__name__}: {str(e)[:150]}"
    out[c] = d
out["duration_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "hot-leg-2026-11-07-1134-verify.json", "w"), indent=1)
print(json.dumps(out, indent=1))
