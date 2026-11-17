#!/usr/bin/env python3
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0), None
        except Exception as e: err = f"{type(e).__name__}: {str(e)[:160]}"
    return None, err
def safe_int(val):
    try:
        if val and len(val) <= 130: return int(val, 16)
    except Exception: pass
    return None
def collect(to, tests):
    out = {}
    for name, arg in tests:
        val, err = call(to, sel(name) + arg)
        out[name] = {"int": safe_int(val), "raw": (val[:200] if val else val), "error": err if val is None else None}
    return out
def block():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
    return None
def dec_str(raw):
    try:
        if not raw or len(raw) < 130: return None
        off = int(raw[2:66], 16); ln = int(raw[66:130], 16)
        hx = raw[130:130 + ln * 2]
        return bytes.fromhex(hx).decode(errors="replace")
    except Exception: return None
def str_call(to, name):
    val, err = call(to, sel(name))
    return {"str": dec_str(val), "raw": (val[:200] if val else val), "error": err if val is None else None}
tests = [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""), ("freeMinted()", ""), ("freeLeft()", ""), ("freeRemaining()", ""), ("freeMintedCount()", ""), ("mintOpen()", ""), ("freeOpen()", ""), ("mintedBy(address)", enc_addr(USER)[2:]), ("freeUsed(address)", enc_addr(USER)[2:]), ("freeMinted(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:]), ("MAX_SUPPLY()", ""), ("totalMinted()", "")]
items = {
 "Pearlpilot":"0x78F377952bD84383dd226148Ab8093fc0F7eCdFd",
 "Swarmganbei":"0xEEa8A6d433850b3121e059f9F86aCAeF47cFDA90",
 "NovaWraiths":"0x27e6ecE26dc93094978E794Cc47D33EA26F10bc2",
 "Beatmind":"0xC22ea04ff39c2471aBEcf51D5D2553713EB396Dd",
 "Dragonmind":"0x84Ce3C8662C081232ae505195f3c3a7F1a9F4ac0",
 "Hootfarm":"0xd82eD99905416a4860D9ae46d39A862E30DAEBAC",
 "Sourcify10e4":"0x10e46d53411f2EC60715718ce2E259182901709f",
 "Cryptlichor":"0xb792Bf600DF37EB7638fb16434E813FC0c90C3C8",
 "CilokCats":"0x01E3E2FE09cB34AD4C6f8090Cb2BD7E098484C9b",
 "WildDuck":"0xac7C0e1f36E15DBa7ED32Bf6e72D83095Ff8fd10",
}
out = {"block": block()}
for n,a in items.items():
    out[n] = collect(a, tests)
    out[n+"_str"] = {"name": str_call(a, "name()"), "symbol": str_call(a, "symbol()")}
    out[n+"_extra"] = collect(a, [("owner()", ""), ("AGENT_ID()", ""), ("agentIdRegistry()", ""), ("contractURI()", "")])
    out[n+"_quote"] = collect(a, [("quote(address,uint256)", enc_addr(USER)[2:]+"01".rjust(64,"0")), ("freeFor(address,uint256)", enc_addr(USER)[2:]+"01".rjust(64,"0"))])
out["OSKsale_extra2"] = collect("0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37", [("opened()", ""), ("FREE_SHARES()", ""), ("TOTAL_SHARES()", ""), ("saleStart()", ""), ("saleEnd()", "")])
out["IMARS"] = collect("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f", [("opened()", ""), ("freeMinted()", ""), ("FREE_SHARES()", ""), ("totalMinted()", "")])
out["NIULAI"] = collect("0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF", [("launched()", ""), ("phase()", ""), ("freeClaimed()", "")])
out["BINANCEAI"] = collect("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [("launched()", ""), ("totalShares()", ""), ("isRefundPhase()", ""), ("failed()", ""), ("tokenClaimed(address)", enc_addr(USER)[2:])])
json.dump(out, open(BASE + "run-2026-11-04-0201-verify.json", "w"), indent=1)
print("block", out["block"])
for k in items: print(k, json.dumps(out[k]), out[k+"_quote"])
print("OSKextra2", out["OSKsale_extra2"]); print("IMARS", out["IMARS"]); print("NIULAI", out["NIULAI"]); print("BINANCEAI", out["BINANCEAI"])
