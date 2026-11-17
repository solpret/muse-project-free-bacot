#!/usr/bin/env python3
"""Probe NEW S1 sale 0x1f82 (LumenMintV2) - leg 3 on-chain verify, run 1449.
Read-only eth_calls via fast_rpc. No preview, no mint."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
SALE = "0x1f82539520a8b3d4eB7C3145f7E1EaFe4B52c4e1"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = "0" * 24 + USER[2:].lower()
AGENTID = "12411464190637771618140538948436718430879438309640658942350393382867700450815750101755948145101197728078227495339265465644916641821446368465628375122182145"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

def call(to, data, timeout=12):
    last = None
    for ep in EPS:
        try:
            return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], timeout, retries=0)
        except Exception as e:
            last = str(e)[:150]
    return {"error": last}

def u(h):
    if isinstance(h, dict) or not h or h == "0x" or len(h) < 66: return None
    try: return int(h[2:66], 16)
    except Exception: return None

def b(h):
    if isinstance(h, dict) or not h or len(h) < 66: return None
    try: return int(h[2:66], 16) != 0
    except Exception: return None

out = {"sale": SALE, "read_wib": time.strftime("%Y-%m-%d %H:%M:%S WIB", time.localtime(time.time() + 7*3600))}
V = {}
V["opened"] = b(call(SALE, sel("opened()")))
V["paused"] = b(call(SALE, sel("paused()")))
V["saleEnd"] = u(call(SALE, sel("saleEnd()")))
V["FREE_MAX"] = u(call(SALE, sel("FREE_MAX()")))
V["freeMinted"] = u(call(SALE, sel("freeMinted()")))
V["totalMinted"] = u(call(SALE, sel("totalMinted()")))
V["MAX_SHARES"] = u(call(SALE, sel("MAX_SHARES()")))
V["BASE_PRICE"] = u(call(SALE, sel("BASE_PRICE()")))
V["TOKENS_PER_SHARE"] = u(call(SALE, sel("TOKENS_PER_SHARE()")))
V["BASE_QUOTA"] = u(call(SALE, sel("BASE_QUOTA()")))
V["agentRegistry"] = call(SALE, sel("agentRegistry()"))
V["token"] = call(SALE, sel("token()"))
V["factory"] = call(SALE, sel("factory()"))
V["pair"] = call(SALE, sel("pair()"))
V["owner"] = call(SALE, sel("owner()"))
ident = call(SALE, sel("identityOf(address)") + USER_PAD)
V["identityOf_user_raw"] = ident
ident_hex = ident[2:66] if isinstance(ident, str) and len(ident) >= 66 else None
V["identityOf_user"] = ident_hex
if ident_hex:
    V["freeClaimed_identity"] = b(call(SALE, sel("freeClaimed(bytes32)") + ident_hex))
    V["quotaOf_identity"] = u(call(SALE, sel("quotaOf(bytes32)") + ident_hex))
    V["quotaBonusOf_identity"] = u(call(SALE, sel("quotaBonusOf(bytes32)") + ident_hex))
    V["identityRegistered"] = b(call(SALE, sel("identityRegistered(bytes32)") + ident_hex))
V["claimable_user"] = u(call(SALE, sel("claimable(address)") + USER_PAD))
V["mintedById_user"] = u(call(SALE, sel("mintedById(bytes32)") + ident_hex)) if ident_hex else None
# quoteFor(1, true) = free path; quoteFor(1, false) = paid path
for use_free in (True, False):
    data = sel("quoteFor(uint8,bool)") + "01".rjust(64, "0") + ("01" if use_free else "00").rjust(64, "0")
    r = call(SALE, data)
    if isinstance(r, dict):
        V[f"quoteFor_1_free={use_free}"] = r
    else:
        words = [r[2+i*64:2+(i+1)*64] for i in range(10)]
        vals = [int(w, 16) for w in words]
        V[f"quoteFor_1_free={use_free}"] = {
            "freeShare": vals[0], "paidShare": vals[1], "startIndex": vals[2],
            "endIndex": vals[3], "pricePerShare": vals[4], "totalBnb": vals[5],
            "tokenAmount": vals[6], "deadline": vals[7], "quotaLeft": vals[8],
            "remainingShares": vals[9]}
# token identity (name/symbol) from token()
tok = V["token"]
if isinstance(tok, str) and len(tok) >= 66:
    taddr = "0x" + tok[26:66]
    V["token_addr"] = taddr
    for fn, lab in (("name()", "name"), ("symbol()", "symbol")):
        rr = call(taddr, sel(fn))
        if isinstance(rr, str) and len(rr) > 130:
            try:
                ln = int(rr[130:194], 16)
                V["token_" + lab] = bytes.fromhex(rr[194:194+ln*2]).decode("utf-8", "ignore")
            except Exception as e:
                V["token_" + lab] = {"error": str(e)[:80]}
        else:
            V["token_" + lab] = rr
    V["token_totalSupply"] = u(call(taddr, sel("totalSupply()")))
    V["token_decimals"] = u(call(taddr, sel("decimals()")))
out["values"] = V
# block
blk = None
for ep in EPS:
    try:
        blk = _single(ep, "eth_blockNumber", [], 12, retries=0); break
    except Exception as e:
        blk = {"error": str(e)[:120]}
out["block"] = blk
with open(HF + "hot-leg-2026-11-11-1449-1f82-probe.json", "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out, indent=1))
