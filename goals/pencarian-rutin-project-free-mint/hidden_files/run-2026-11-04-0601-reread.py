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
tests = [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""), ("freeMinted()", ""), ("freeLeft()", ""), ("freeRemaining()", ""), ("mintOpen()", ""), ("mintedBy(address)", enc_addr(USER)[2:]), ("freeUsed(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:]), ("MAX_SUPPLY()", ""), ("totalMinted()", ""), ("mintedPerWallet(address)", enc_addr(USER)[2:]), ("hasAgentId(address)", enc_addr(USER)[2:])]
items = {
 "Mummyhive":"0xf45fE22B3a9A748c59A7099e2E7B69f41216b1cd",
 "Glitchdroid":"0xe3F0085fd94D4Fb2AE9ACb4B49f6c0504E3546A0",
 "Kittynode":"0xb625B5ddA0a2EbB4b062c358d955685B71AabB51",
 "Krillfarm":"0x0aA11F327313682CDF072AFFfF26D0dffC804483",
 "Agentvolt":"0xB04af24bBFA0EF441091178E61A724163e2828Cc",
 "Agentyyds":"0x8463abFC06173BdCaEDe96c4331C30A958789629",
 "Spookdroidling":"0x7e20f345435130Af72733Ce5742A6704b19cc574",
 "Saturndroid":"0xb884dc59bBB4f66797F533e449546640b17549C8",
 "Pilotphoenix":"0xc1A54df271a455E236169F8Ff65b084eBfB00E15",
 "Jolly":"0xdc11764a5664e333c8d303eb465e89a1caadb85b",
 "Astrogent":"0x483CEf46ec23D5656896526408221074597b6ed6",
 "Duneswarm":"0xBCACC3a237b11CFAe2b59D3E5E6D2B7f2c3EfF96",
 "Kabutomind":"0x3b3C00d4616a4A48C115B8E321aa6B983A2BEb10",
 "Cosmopilot":"0x3e68AbD88885979188b97b19e8986552F10265D2",
 "OKAGENT":"0xb081550d7b38f17bf93df8f20db82903c59d6f40",
 "LunaBirds":"0xd514eb87c957514979360d9913e1bebcdd90129d",
 "Chipagent":"0xc3D831dB5f018ab9977724352ec773bA0AC3AE4a",
 "Botsaturn":"0xd1E75De8e6B46E09a90126A122373Fac79578300",
 "Noctagent":"0x9c60E147f10fF790A293889DDee1e2C4063e096d",
 "Mothfarm":"0x74E64b8B2941F61Bb67801C7668a4307bC34D9E0",
 "Swarmcentaur":"0x87B805eCDDaB0b376531cAf6d5aD9A52E641B100",
 "WDNFT":"0xac7c0e1f36e15dba7ed32bf6e72d83095ff8fd10",
}
out = {"block": block()}
for n,a in items.items():
    out[n] = collect(a, tests)
    out[n+"_str"] = {"name": str_call(a, "name()"), "symbol": str_call(a, "symbol()")}
    out[n+"_extra"] = collect(a, [("owner()", ""), ("AGENT_ID()", ""), ("agentIdRegistry()", "")])
    out[n+"_quote"] = collect(a, [("quote(address,uint256)", enc_addr(USER)[2:]+"01".rjust(64,"0")), ("freeFor(address,uint256)", enc_addr(USER)[2:]+"01".rjust(64,"0"))])
out["OSKsale_extra2"] = collect("0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37", [("opened()", ""), ("FREE_SHARES()", ""), ("TOTAL_SHARES()", "")])
out["IMARS"] = collect("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f", [("opened()", ""), ("freeMinted()", ""), ("FREE_SHARES()", ""), ("totalMinted()", "")])
out["NIULAI"] = collect("0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF", [("launched()", ""), ("phase()", ""), ("freeClaimed()", "")])
out["BINANCEAI"] = collect("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [("launched()", ""), ("totalShares()", ""), ("isRefundPhase()", ""), ("failed()", ""), ("tokenClaimed(address)", enc_addr(USER)[2:])])
json.dump(out, open(BASE + "run-2026-11-04-0601-reread.json", "w"), indent=1)
print("block", out["block"])
for k in items: print(k, json.dumps(out[k]), out[k+"_quote"], out[k+"_str"])
print("OSK", out["OSKsale_extra2"]); print("IMARS", out["IMARS"]); print("NIULAI", out["NIULAI"]); print("BINANCEAI", out["BINANCEAI"])

out["OKAGENT_extra"] = collect("0xb081550d7b38f17bf93df8f20db82903c59d6f40", [("freeRemaining()", ""), ("freeSupply()", "")])
print("OKAGENT_extra", out["OKAGENT_extra"])
