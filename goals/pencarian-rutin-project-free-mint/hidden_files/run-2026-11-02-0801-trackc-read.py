#!/usr/bin/env python3
"""Free-mint-search run 2026-11-02 08:01 WIB: fresh track-C lead reads before direct-mint execution. Read-only."""
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
            err = f"{type(e).__name__}: {str(e)[:160]}"
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
BABY = "0xbb7ed59ca41ea03cf20084a8c9de94244b7b2637"
result["BNBbaby"] = collect(BABY, [("sharesMinted()", ""), ("freeMinted()", ""), ("paidShares()", ""), ("MAX_SHARES()", ""), ("mintingOpen()", ""), ("poolOpen()", ""), ("freeAvailable(address)", enc_addr(USER)[2:]), ("freeClaimed(address)", enc_addr(USER)[2:]), ("mintedBy(address)", enc_addr(USER)[2:]), ("hasAgentId(address)", enc_addr(USER)[2:]), ("TOKENS_PER_SHARE()", ""), ("PRICE()", ""), ("token()", "")])
DOGSALE = "0xA74bEF84304D8838db798faE96fb873dd46fB4C1"
result["DOG"] = collect(DOGSALE, [("sharesMinted()", ""), ("FREE_SHARES()", ""), ("MAX_SHARES()", ""), ("saleFailed()", ""), ("sharesByWallet(address)", enc_addr(USER)[2:]), ("deadline()", "")])
aid, err = call(DOGSALE, sel("agentIdOf(address)") + enc_addr(USER)[2:])
result["DOG_agentId"] = {"raw": aid, "error": err}
if aid:
    fc, e2 = call(DOGSALE, sel("freeClaimed(bytes32)") + aid[2:])
    result["DOG_freeClaimed_user"] = {"words": words(fc), "raw": fc, "error": e2}
    v, e = call(DOGSALE, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(1)[2:])
    result["DOG_quote_user_1"] = {"words": words(v), "raw": v, "error": e}
SAM = "0xe15e68C9198ee0A5780fba96016e1780204aF3B4"
result["SAMBARIO"] = collect(SAM, [("totalCards()", ""), ("cardsSold()", ""), ("cardsRemaining()", ""), ("freeCardCap()", ""), ("freeCardsRemaining()", ""), ("freeGiven()", ""), ("gateOn()", ""), ("paused()", ""), ("freeClaimed(address)", enc_addr(USER)[2:]), ("quotaLeft(address)", enc_addr(USER)[2:]), ("tokensPerShare()", "")])
v, e = call(SAM, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(1)[2:])
result["SAMBARIO_quote_user_1"] = {"words": words(v), "raw": v, "error": e}
A7 = "0xa7Bef74f9327daacEe49fEa9Db9C34253900936A"
result["a7Be"] = collect(A7, [("sharesMinted()", ""), ("freeSharesMinted()", ""), ("FREE_SHARES()", ""), ("MAX_SHARES()", ""), ("saleFailed()", ""), ("sharesByWallet(address)", enc_addr(USER)[2:]), ("deadline()", "")])
aid2, err2 = call(A7, sel("agentIdOf(address)") + enc_addr(USER)[2:])
result["a7Be_agentId"] = {"raw": aid2, "error": err2}
if aid2:
    fc, e2 = call(A7, sel("freeClaimed(bytes32)") + aid2[2:])
    result["a7Be_freeClaimed_agentId"] = {"words": words(fc), "raw": fc, "error": e2}
    v, e = call(A7, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(1)[2:])
    result["a7Be_quote_user_1"] = {"words": words(v), "raw": v, "error": e}
ZERO = "0xc180b8bffdd65531f4bae6ac7586cfb192164a9b"
result["ZeroYuanGou"] = collect(ZERO, [("FREE_TOTAL()", ""), ("soldFree()", ""), ("soldPaid()", ""), ("totalSold()", ""), ("TOKENS_PER_SHARE()", ""), ("launched()", ""), ("startTime()", ""), ("balanceOf(address)", enc_addr(USER)[2:])])
def _label_bytes32(txt): return txt.encode().ljust(32, b"\x00").hex()
def _label_keccak(txt):
    kk = keccak.new(digest_bits=256); kk.update(txt.encode()); return kk.hexdigest()
for tag, hx in (("masgayut_padded", _label_bytes32("masgayut")), ("masgayut_keccak", _label_keccak("masgayut")), ("masgayut_ai_keccak", _label_keccak("masgayut.ai"))):
    v, e = call(ZERO, sel("freeById(bytes32)") + hx)
    result["ZeroYuanGou"]["freeById_"+tag] = {"words": words(v), "raw": v, "error": e}
# Registry label probes: what bytes32 does the Agent ID registry return for the user?
for fn in ("agentIdOf(address)", "identityOf(address)", "getAgentId(address)", "agentOf(address)"):
    v, e = call(REG, sel(fn) + enc_addr(USER)[2:])
    result["REGISTRY_"+fn] = {"raw": v, "error": e}
for nm, addr in (("JUBAO", "0x1ed3BF35e4DA25b1289C27ddbD82f0A38DDCee8b"),
                ("ZCMAO", "0x8362e6a5F38427d8d719EA47f08890784F6023DC"),
                ("JINLONG", "0x2Df4Ef534cbBe1a8F647e24D0f8C75ECe74D8288")):
    d = collect(addr, [("freeClaimed()", ""), ("FREE_SHARES()", ""), ("phase()", ""), ("startedAt()", ""), ("launched()", ""), ("sold()", ""), ("balanceOf(address)", enc_addr(USER)[2:])])
    idraw, _ = call(addr, sel("identity()"))
    d["identity_raw"] = idraw
    idaddr = "0x" + idraw[-40:] if idraw else None
    d["identity_addr"] = idaddr
    if idaddr:
        reg, _ = call(idaddr, sel("REGISTRY()"))
        d["identity_REGISTRY"] = reg
        aidv, _ = call(idaddr, sel("identityOf(address)") + enc_addr(USER)[2:])
        d["identityOf_user"] = aidv
        if aidv:
            fc, _ = call(addr, sel("freeClaimedById(bytes32)") + aidv[2:])
            d["freeClaimedById_agentId"] = {"words": words(fc), "raw": fc}
            mb, _ = call(addr, sel("mintedById(bytes32)") + aidv[2:])
            d["mintedById_agentId"] = {"words": words(mb), "raw": mb}
    result[nm] = d
BIAO = "0x16469C174cd827A5e21f4bf3eE3711f2bB42e275"
result["BIAO"] = collect(BIAO, [("freeClaimed()", ""), ("FREE_SHARES()", ""), ("MAX_PAID()", ""), ("phase()", ""), ("sold()", ""), ("totalPaidBNB()", ""), ("startedAt()", ""), ("balanceOf(address)", enc_addr(USER)[2:])])
SI = "0x071f76c1868039e2f042Dca1890EcB0364D8494a"
result["SI"] = collect(SI, [("FREE_POOL()", ""), ("soldFree()", ""), ("soldPaid()", ""), ("TOTAL_CAP()", ""), ("startTime()", ""), ("balanceOf(address)", enc_addr(USER)[2:])])
for tag, hx in (("masgayut_padded", _label_bytes32("masgayut")), ("masgayut_keccak", _label_keccak("masgayut")), ("masgayut_ai_keccak", _label_keccak("masgayut.ai"))):
    v, e = call(SI, sel("freeQuotaOf(bytes32)") + hx)
    result["SI"]["freeQuotaOf_"+tag] = {"words": words(v), "raw": v, "error": e}
    v2, e2 = call(SI, sel("hasMintedById(bytes32)") + hx)
    result["SI"]["hasMintedById_"+tag] = {"words": words(v2), "raw": v2, "error": e2}
VELM = "0x538Bd9f178eEf2CFB564d2FAD1D5B0702d8B3818"
result["Velmora"] = collect(VELM, [("FREE_SHARES()", ""), ("freeClaimedShares()", ""), ("totalClaimedShares()", ""), ("claimOpen()", ""), ("paused()", ""), ("claimedBy(address)", enc_addr(USER)[2:]), ("freeTaken(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:])])
v, e = call(VELM, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(1)[2:])
result["Velmora_quote_user_1"] = {"words": words(v), "raw": v, "error": e}
print(json.dumps(result, indent=1))
json.dump(result, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0801-trackc-read.json", "w"), indent=1)
