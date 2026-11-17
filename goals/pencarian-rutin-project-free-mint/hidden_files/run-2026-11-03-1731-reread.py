#!/usr/bin/env python3
"""Main run 1731 (executed ~17:50 WIB). Read-only re-read of promotion-relevant watchlist + bridge-5 + track-B/C."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
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
early = [("totalSupply()", ""), ("freeClaimed()", ""), ("freeMinted()", ""), ("freeLeft()", ""),
         ("FREE_SUPPLY()", ""), ("mintedBy(address)", enc_addr(USER)[2:]),
         ("freeUsed(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:]),
         ("owner()", "")]
ITEMS = {
 "Syntaxia": "0xA9b060551764f3213a64a449fD3D06db3b8CbCff",
 "Noesyn": "0x69e2B3df4ecedBf7FC89085707a8cb9163F5e1BC",
 "Lumenhold": "0x9701980b0afd825134390ee46fb3bd675a2f356f",
 "Vertexa": "0x7e00856e5bbc2795ad545592ba547336133fd244",
 "Omegrid": "0x4095f575f1aec7068ec0e542aaf20e44cd62e5d1",
 "Auditrix": "0x13eEa6a99720e2C9dDEda9B28d7eF5306B7322F4",
 "Robogent": "0x5eA7E757dfc4654f7478841BD30175bd7F186e24",
 "Synaptik": "0xE5523bf6AA0F92aCC7d2898F65596a0A088a8f0F",
 "Yydsgent": "0x38CB2dF1D6Fdac4115883E6EC7d2Ff39e20C1e61",
 "Mechfarm-1FAb": "0x1FAb92b937572C79550aEEe51Cee77d3aDD20367",
 "Saturnagent-ef87": "0xef870A9B4A529373fB2E174b59Ca7A66EB018074",
 "bridge-AgentVOLT-2b8a": "0x2b8ae9ef424e0791c1ad526a052bd8f18d6b3625",
 "bridge-SailPixels-42bd": "0x42bdfff914afcf12047922ae58be397c1f351a27",
 "bridge-AnthroBitNFT-c7b7": "0xc7b7593aa572701d26301d9707e93b0c511e636a",
}
result = {"block": block()}
for n, a in ITEMS.items():
    result[n] = collect(a, early)
MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN = "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
result["TrackB_MINT"] = collect(MINT, [("launched()", ""), ("tokenClaimed(address)", enc_addr(USER)[2:]),
    ("totalShares()", ""), ("isRefundPhase()", ""), ("failed()", "")])
result["TrackB_TOKEN_bal_USER"] = collect(TOKEN, [("balanceOf(address)", enc_addr(USER)[2:])])
IMARS = "0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f"
result["IMARS"] = collect(IMARS, [("freeMinted()", ""), ("totalMinted()", ""), ("FREE_SHARES()", ""),
    ("opened()", ""), ("openPool()", ""), ("mintingOpen()", "")])
json.dump(result, open(BASE + "run-2026-11-03-1731-reread.json", "w"), indent=1)
print("BLOCK", result["block"])
for k, v in result.items():
    if k == "block": continue
    if isinstance(v, dict):
        print(k, {kk: (vv.get("int") if isinstance(vv, dict) else vv) for kk, vv in v.items()})
    else: print(k, v)
