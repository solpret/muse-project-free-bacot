#!/usr/bin/env python3
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
    return None
def iv(v):
    try: return int(v, 16) if v else None
    except Exception: return None
def block():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
    return None
targets = {
 "Kelp Agent": "0xf76F0BB04EbC0866E8FDdf24e1eC5320fAD0c9Fb",
 "Jelly Agent": "0xE20638C26Fd7EAC342a4164b4F026754375AEbfE",
 "Flora Agent": "0x1C89AcaB7A497F537f988b5f20055fd11B062f50",
 "Caravan Agent": "0x7112010027394f0d9146885fa242e117F18D4BD8",
 "Silk Agent": "0xF888787f39dD5a5adCEC1b0d9833cF40a655c60e",
 "Peony Agent": "0x58bA07CEd2803f40DE2d00b411580Eea7CC2D2FC",
 "Yunjin Agent": "0x6F726D4cF7263f1F7562d5868EC09806d7ef70f8",
 "Deco Agent": "0xfe8D985cB19380805B01cf7FCFc65c3819e030C8",
 "Opera Agent": "0x32ddd7d98bB711976cCfE19548Df52D0cdeC197c",
}
tests = [("totalMinted()", ""), ("totalSupply()", ""), ("costFor(uint256)", "0"*63+"1"),
         ("quote(address,uint256)", enc(USER)+"0"*63+"1"),
         ("mintedBy(address)", enc(USER)), ("freeUsed(address)", enc(USER))]
out = {"block": block()}
for name, addr in targets.items():
    d = {}
    for sig, arg in tests:
        d[sig] = iv(call(addr, sel(sig)+arg))
    out[name] = d
    tm = d["totalMinted()"] or d["totalSupply()"]
    print(name, d, "=> minted~", tm)
json.dump(out, open(BASE+"run-2026-11-03-0401-extra2.json","w"), indent=1)
print("BLOCK", out["block"])
