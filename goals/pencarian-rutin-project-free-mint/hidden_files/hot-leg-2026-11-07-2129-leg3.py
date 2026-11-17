#!/usr/bin/env python3
"""Hot-leg 2026-11-07 21:29 leg-3: on-chain verify S1 NFT sale 0xEECaCBE6,
probe share-sale variant 0xfab7dd20, probe 2 Boltbook shape-failed addrs.
Read-only. Single calls only (batch revert quirk)."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak

USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def raw(addr, sig, arg=""):
    data = sel(sig) + arg
    for ep in EPS:
        try:
            r = _single(ep, "eth_call", [{"to": addr, "data": data}, "latest"], 8, retries=0)
            return r
        except Exception:
            continue
    return None
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def to_str(v):
    try:
        b = bytes.fromhex(v[2:])
        if len(b) < 96: return None
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode("utf-8", "replace")
    except Exception:
        return None
def u(addr, sig, arg=""):
    return to_int(raw(addr, sig, arg))
def s(addr, sig, arg=""):
    return to_str(raw(addr, sig, arg))

out = {}
# --- 0xEECaCBE6 NFT sale ---
a = "0xEECaCBE6eAC6D6F2a38e8daA9049C7AA08aD43b0"
d = {"address": a}
d["name"] = s(a, "name()"); d["symbol"] = s(a, "symbol()")
for v in ["totalSupply()", "FREE_QUOTA()", "freeUsed()", "remainingFree()", "MAX_SUPPLY()", "mintOpen()", "soldOut()", "MAX_PER_WALLET()", "PAID_PRICE()"]:
    d[v.split("(")[0]] = u(a, v)
d["freeClaimed_user"] = u(a, "freeClaimed(address)", enc(USER))
d["mintedBy_user"] = u(a, "mintedBy(address)", enc(USER))
d["balanceOf_user"] = u(a, "balanceOf(address)", enc(USER))
d["costOf_1"] = u(a, "costOf(uint256)", enc_uint(1))
d["costOf_user1"] = u(a, "costOf(address,uint256)", enc(USER) + enc_uint(1))
d["freeFor_user1"] = u(a, "freeFor(address,uint256)", enc(USER) + enc_uint(1))
d["contractURI"] = s(a, "contractURI()")
out["EECaCBE6"] = d

# --- 0xfab7dd20 share-sale variant (no quote -> fails literal S1) ---
a = "0xfab7dd20e8816e10227C1222bd4Bd446FecF1B72"
d = {"address": a}
d["token"] = raw(a, "token()")
d["FREE_SHARES"] = u(a, "FREE_SHARES()")
d["freeMinted"] = u(a, "freeMinted()")
d["totalMinted"] = u(a, "totalMinted()")
d["freeClaimed_user"] = u(a, "freeClaimed(address)", enc(USER))
d["startTime"] = u(a, "startTime()")
d["deadline"] = u(a, "deadline()")
d["finalized"] = u(a, "finalized()")
d["TOKENS_PER_SHARE"] = u(a, "TOKENS_PER_SHARE()")
d["TOTAL_SHARES"] = u(a, "TOTAL_SHARES()")
out["fab7dd20"] = d

# --- Boltbook shape-failed probes ---
for a in ["0x5aaa9dcae9d548cf7118b1d2c21be27313f1ae1d", "0x907e53f41139a534230fb997ea3e553d8815bf30"]:
    d = {"address": a}
    d["name"] = s(a, "name()"); d["symbol"] = s(a, "symbol()")
    d["totalSupply"] = u(a, "totalSupply()")
    d["decimals"] = u(a, "decimals()")
    d["freeClaimed_user"] = u(a, "freeClaimed(address)", enc(USER))
    d["owner"] = raw(a, "owner()")
    out[a] = d

print(json.dumps(out, indent=1))
json.dump(out, open("hot-leg-2026-11-07-2129-leg3.json", "w"), indent=1)
