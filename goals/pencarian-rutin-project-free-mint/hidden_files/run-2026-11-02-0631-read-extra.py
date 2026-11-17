#!/usr/bin/env python3
"""Run 0631 extra reads: wave early leads + Lighthouse + new track-C leads. Read-only."""
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
AGENTID = "0x934122e8fc4fe823a60d9dde4b2b716dd6bdcff35db0ad4ec90f97a1b0b7d310"
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0), None
        except Exception as e: err = f"{type(e).__name__}: {str(e)[:120]}"
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
NFTS = {
 "Agents NormiePunks": "0xa233C45f881A6982647b63c61D7a5f9a3F90C5f4",
 "Medusine": "0x8E878C801b9F37cc0Cb6FF3C4597Af8FC057988b",
 "Hotpotsage": "0xEbAdb5Be9692b0BF25E8A5F3351C35DdC58f195d",
 "Mummyrelic": "0xB330e582f45c0243e5Eb1B56958b56273f26a9eB",
 "Ravenhex": "0xB44050254A25dAA8077C14BbB20d0a595e6CECE2",
 "Orbitmarshal": "0x74C2214fDCc10c303302592151c50965903aa7a9",
}
nft_tests = [("totalSupply()", ""), ("totalMinted()", ""), ("freeClaimed()", ""), ("freeLeft()", ""),
    ("freePerWallet()", ""), ("FREE_SUPPLY()", ""), ("MAX_SUPPLY()", ""), ("mintOpen()", ""),
    ("mintedBy(address)", enc_addr(USER)[2:]), ("freeFor(address)", enc_addr(USER)[2:]),
    ("freeUsed(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:]),
    ("costFor(uint256)", enc_uint(1)[2:]), ("currentPrice()", "")]
for nm, addr in NFTS.items():
    result[nm] = collect(addr, nft_tests)
    v, e = call(addr, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(1)[2:])
    result[nm]["quote_user_1"] = {"words": words(v), "raw": v, "error": e}
# JINLI (identity-delegation S2 variant)
J = "0xd7a2567929da32cab052cf287522cd6e3d3ecfa2"
d = collect(J, [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SHARES()", ""), ("PAID_SHARES()", ""),
    ("phase()", ""), ("sold()", ""), ("perShare()", ""), ("launched()", ""), ("pair()", ""),
    ("startedAt()", ""), ("freeClaimedById(address)", enc_addr(USER)[2:]),
    ("mintedById(address)", enc_addr(USER)[2:]), ("remainingFor(address)", enc_addr(USER)[2:]),
    ("balanceOf(address)", enc_addr(USER)[2:])])
idraw, _ = call(J, sel("identity()")); d["identity_raw"] = idraw
idaddr = "0x" + idraw[-40:] if idraw else None; d["identity_addr"] = idaddr
if idaddr:
    reg, _ = call(idaddr, sel("REGISTRY()")); d["identity_REGISTRY"] = reg
    aidv, _ = call(idaddr, sel("identityOf(address)") + enc_addr(USER)[2:]); d["identityOf_user"] = aidv
    if aidv:
        fc, _ = call(J, sel("freeClaimedById(bytes32)") + aidv[2:]); d["freeClaimedById_agentId"] = {"words": words(fc), "raw": fc}
        mb, _ = call(J, sel("mintedById(bytes32)") + aidv[2:]); d["mintedById_agentId"] = {"words": words(mb), "raw": mb}
        rq, _ = call(J, sel("remainingQuota(bytes32)") + aidv[2:]); d["remainingQuota_agentId"] = {"words": words(rq), "raw": rq}
result["JINLI"] = d
# BIAO
B = "0x16469C174cd827A5e21f4bf3eE3711f2bB42e275"
d = collect(B, [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SHARES()", ""), ("MAX_PAID()", ""),
    ("phase()", ""), ("startedAt()", ""), ("sold()", ""), ("launched()", ""), ("pair()", ""),
    ("PRICE()", ""), ("totalPaidBNB()", ""), ("balanceOf(address)", enc_addr(USER)[2:])])
reg, _ = call(B, sel("REGISTRY()")); d["REGISTRY_raw"] = reg
fc, _ = call(B, sel("freeClaimedById(bytes32)") + AGENTID[2:]); d["freeClaimedById_agentId"] = {"words": words(fc), "raw": fc}
result["BIAO"] = d
# 兕 (0x071f...)
S = "0x071f76c1868039e2f042Dca1890EcB0364D8494a"
d = collect(S, [("totalSupply()", ""), ("FREE_POOL()", ""), ("soldFree()", ""), ("soldPaid()", ""),
    ("TOTAL_CAP()", ""), ("currentPrice()", ""), ("pair()", ""), ("launched()", ""),
    ("startTime()", ""), ("deadline()", ""), ("balanceOf(address)", enc_addr(USER)[2:])])
reg, _ = call(S, sel("REGISTRY()")); d["REGISTRY_raw"] = reg
def lbl(txt): return txt.encode().ljust(32, b"\x00").hex()
def kk(txt):
    k = keccak.new(digest_bits=256); k.update(txt.encode()); return k.hexdigest()
for tag, hx in (("masgayut_padded", lbl("masgayut")), ("masgayut_keccak", kk("masgayut")),
                ("masgayut_ai_keccak", kk("masgayut.ai")), ("agentid", AGENTID[2:])):
    for fn in ("freeQuotaOf(bytes32)", "freeUsedById(bytes32)", "freeUsedOf(bytes32)", "hasMintedById(bytes32)", "freeById(bytes32)"):
        v, e = call(S, sel(fn) + hx)
        d[f"{fn}_{tag}"] = {"words": words(v), "raw": v, "error": e}
result["XI"] = d
print(json.dumps(result, indent=1))
json.dump(result, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0631-read-extra.json", "w"), indent=1)
