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
 "Marsagentis":"0x6908fb5FB6AE2F62FF2672005b1eD60150C0EBd9",
 "Chipdroidling":"0x9ADca6B0777FD8CD5B4795f885c7D5C5f98EEa6b",
 "Neonmind":"0x0e42D40fF176aE2156b0dA3668F9a5EB0565Ffd6",
 "Batbot":"0xD3908F017424967BeC6aC5E8055FBa91f31E5585",
 "SevenSins":"0xEce8031bCE4d350733e6E5baE1e509be1cCfa702",
 "VelmoraNFT":"0x0502b9A7B173dF12251157C72Cb5971D7F00F010",
 "Plutofarm":"0xdB101245A380C54E9CE5508359B1350F5fc31289",
 "Chiphiveowl":"0xc36FD9884ac52eB406B80D4E91328B39251F54Ab",
 "Swarmdrake":"0x3807470b75f332461D8aae40501E83A7E1Fe1819",
 "Agentjiayou":"0x33A8Db53339a0C37246216b45394e7E56B3c7D1E",
 "PixelTrump":"0x3054a5530F1852C33bD2749BFAF7155F162A581b",
 "Pumpkinagent":"0xC9BF67564043573A06685205C4c5296D7D37Bc74",
 "Agentdragon":"0x2Df7435f5BCE0577bEE213e13Da68313c74d7d0b",
 "LanternLords":"0xC9c0De69ea301cA9479149554bf325aE3342584B",
 "Owlagent":"0x2252ee71d079ab2e4527edf8ab3b93e20d2222f4",
 "Octagent":"0x3364aa233254873107b015926b337f32c50d17f4",
 "Bridge396c":"0x396ce471230c0c30a7e52bbccbbf87bec1f52492",
 "Bridge9d78":"0x9d78b216ae96060895837c60df84893cd5ac34f2",
 "Ikigai":"0x76437a85b768bb5612e8a466e492d89d8ef634b1",
 "LunaBirds":"0xd514eb87c957514979360d9913e1bebcdd90129d",
 "PACTURE":"0x10b80088fdaf9363d83671be66b64f231f9e92f6",
 "CzAgent":"0xa8e36d374de1cb2664d4631e7035481ad3b4a877",
 "PoPAgent":"0x26e374c049a898d01120c5003adfc9f250e7a8aa",
 "PopAgent":"0x53a8bfef643bcaee7407ae25de35f169d66c8b59",
 "OSKsale":"0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37",
 "CHTCI":"0x050a11c2bfcf881b546983a20550a0e409bf69da",
}
out = {"block": block()}
for n,a in items.items():
    out[n] = collect(a, tests)
    out[n+"_str"] = {"name": str_call(a, "name()"), "symbol": str_call(a, "symbol()")}
    out[n+"_extra"] = collect(a, [("owner()", ""), ("AGENT_ID()", ""), ("agentIdRegistry()", "")])
    out[n+"_quote"] = collect(a, [("quote(address,uint256)", enc_addr(USER)[2:]+"01".rjust(64,"0")), ("freeFor(address,uint256)", enc_addr(USER)[2:]+"01".rjust(64,"0"))])
out["OSKsale_extra2"] = collect("0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37", [("opened()", ""), ("FREE_SHARES()", ""), ("TOTAL_SHARES()", ""), ("saleStart()", ""), ("saleEnd()", "")])
out["IMARS"] = collect("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f", [("opened()", ""), ("freeMinted()", ""), ("FREE_SHARES()", ""), ("totalMinted()", "")])
out["NIULAI"] = collect("0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF", [("launched()", ""), ("phase()", ""), ("freeClaimed()", "")])
out["BINANCEAI"] = collect("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [("launched()", ""), ("totalShares()", ""), ("isRefundPhase()", ""), ("failed()", ""), ("tokenClaimed(address)", enc_addr(USER)[2:])])
json.dump(out, open(BASE + "run-2026-11-04-0201-reread.json", "w"), indent=1)
print("block", out["block"])
for k in items: print(k, json.dumps(out[k]), out[k+"_quote"])
print("OSKextra2", out["OSKsale_extra2"]); print("IMARS", out["IMARS"]); print("NIULAI", out["NIULAI"]); print("BINANCEAI", out["BINANCEAI"])
