#!/usr/bin/env python3
"""Main run 0101 reread part 2 - read-only, missing tail from part 1 (timeout-killed dump)."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0), None
        except Exception as e: err = f"{type(e).__name__}: {str(e)[:160]}"
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
def dec_str(raw):
    try:
        if not raw or len(raw) < 130: return None
        ln = int(raw[66:130], 16)
        return bytes.fromhex(raw[130:130 + ln * 2]).decode(errors="replace")
    except Exception: return None
def str_call(to, name):
    val, err = call(to, sel(name))
    return {"int": None, "str": dec_str(val), "raw": val, "error": err if val is None else None}

snap = json.load(open(BASE + "onchain-snapshot.json"))
c = snap["contracts"]
names = ["Agentdragon","Wuyuhive","Rimeagent","Pandadroid","SYNTHIA","Ghost Frog","Ghostpilotcat",
 "Droidneon","Osiris Guardians","LanternLords","Brinedroid","Plutofarm","Chiphiveowl","Swarmdrake",
 "Agentjiayou","Mintmind","Icepilot","OK AGENT","Kairos","Kelpiare","Borealux","Owlgent",
 "Pixel Trump","CaptainWagmi","Flyingsquirrelai"]
tests = [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""),
         ("mintedBy(address)", enc_addr(USER)[2:]), ("freeUsed(address)", enc_addr(USER)[2:]),
         ("balanceOf(address)", enc_addr(USER)[2:]), ("mintOpen()", ""), ("totalMinted()", "")]
out = {"block": block()}
for n in names:
    if n not in c: out[n] = {"error": "not in snapshot"}; continue
    a = c[n]["address"]
    out[n] = collect(a, tests)
for label, addr in [("NEW0E42","0x0e42D40fF176aE2156b0dA3668F9a5EB0565Ffd6"),
                    ("BB050A","0x050a11c2bfcf881b546983a20550a0e409bf69da"),
                    ("BB149B","0x149b6F713a1e544ED6Dc9905Afc22F03EEf94887"),
                    ("BB2D70","0x2D7097E0f28Ea0fEB0b3b44c7d0ee0227d513103")]:
    out[label] = collect(addr, tests)
    out[label+"_str"] = {"name": str_call(addr, "name()"), "symbol": str_call(addr, "symbol()")}
    out[label+"_extra"] = collect(addr, [("owner()", ""), ("contractURI()", ""), ("freeLeft()", ""),
        ("freeMinted()", ""), ("MAX_SUPPLY()", ""), ("AGENT_ID()", "")])
    out[label+"_quote"] = collect(addr, [("quote(address,uint256)", enc_addr(USER)[2:]+"01".rjust(64,"0")),
        ("freeFor(address,uint256)", enc_addr(USER)[2:]+"01".rjust(64,"0"))])
out["IMARS"] = collect("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f",
    [("opened()", ""), ("freeMinted()", ""), ("FREE_SHARES()", ""), ("totalMinted()", ""),
     ("freeClaimed(address)", enc_addr(USER)[2:])])
out["NIULAI"] = collect("0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF",
    [("launched()", ""), ("phase()", ""), ("freeClaimed()", ""), ("totalMinted()", ""),
     ("mintedBy(address)", enc_addr(USER)[2:])])
out["NIULAI_str"] = {"name": str_call("0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF", "name()"),
                     "symbol": str_call("0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF", "symbol()")}
out["BINANCEAI"] = collect("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
    [("launched()", ""), ("totalShares()", ""), ("isRefundPhase()", ""), ("failed()", ""),
     ("tokenClaimed(address)", enc_addr(USER)[2:])])
json.dump(out, open(BASE + "run-2026-11-04-0101-reread2.json", "w"), indent=1)
print("block", out["block"], "done")
