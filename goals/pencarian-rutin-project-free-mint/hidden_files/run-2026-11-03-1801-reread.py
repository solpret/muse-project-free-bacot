#!/usr/bin/env python3
"""Run 1801 reread: active watchlist + bridge watchlist-only + TrackB + IMARS. Read-only."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
PAD = "0" * 24 + USER[2:].lower()

def sel(sig):
    return keccak.new(digest_bits=256, data=sig.encode()).hexdigest()[:8]

def call(to, sig, arg=None):
    data = "0x" + sel(sig) + (PAD if arg == "user" else "")
    try:
        r = race("eth_call", [{"to": to, "data": data}, "latest"])
        if r in (None, "0x", ""):
            return {"int": None, "raw": r, "error": None}
        try:
            return {"int": int(r, 16), "raw": r, "error": None}
        except Exception:
            return {"int": None, "raw": r, "error": None}
    except Exception as e:
        return {"int": None, "raw": None, "error": f"{type(e).__name__}: {str(e)[:120]}"}

NFT = {
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
 "Ronagent": "0xc22d29A0411B2B76D723E5f9fDEb5B7cc509AF48",
 "bridge-AgentVOLT-2b8a": "0x2b8ae9ef424e0791c1ad526a052bd8f18d6b3625",
 "bridge-SailPixels-42bd": "0x42bdfff914afcf12047922ae58be397c1f351a27",
 "bridge-AnthroBitNFT-c7b7": "0xc7b7593aa572701d26301d9707e93b0c511e636a",
}
VIEWS = ["totalSupply()", "freeClaimed()", "freeMinted()", "freeLeft()", "FREE_SUPPLY()"]
USERVIEWS = ["mintedBy(address)", "freeUsed(address)", "balanceOf(address)"]
out = {}
try:
    out["block"] = race("eth_blockNumber", [])
    print("BLOCK", out["block"], int(out["block"], 16))
except Exception as e:
    out["block"] = None
    print("BLOCK_FAIL", e)
for name, addr in NFT.items():
    d = {}
    for v in VIEWS:
        d[v] = call(addr, v)
    for v in USERVIEWS:
        d[v] = call(addr, v, arg="user")
    d["owner()"] = call(addr, "owner()")
    out[name] = d
    ts = d["totalSupply()"]["int"]; fc = d["freeClaimed()"]["int"]; fs = d["FREE_SUPPLY()"]["int"]
    print(name, "TS", ts, "free", fc, "FREE_SUPPLY", fs,
          "pct", (round(fc / fs * 100, 1) if fc is not None and fs else None),
          "mintedBy", d["mintedBy(address)"]["int"], "freeUsed", d["freeUsed(address)"]["int"],
          "bal", d["balanceOf(address)"]["int"])
# Track B: binanceai.fun
MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN = "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
tb = {}
for v in ["launched()", "tokenClaimed(address)", "totalShares()", "isRefundPhase()", "failed()"]:
    tb[v] = call(MINT, v, arg="user" if "address" in v else None)
out["TrackB_MINT"] = tb
out["TrackB_TOKEN_bal_USER"] = {"balanceOf(address)": call(TOKEN, "balanceOf(address)", arg="user")}
print("TrackB", {k: v["int"] for k, v in tb.items()}, "TOKENbal", out["TrackB_TOKEN_bal_USER"]["balanceOf(address)"]["int"])
# IMARS track C
IMARS = "0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f"
im = {}
for v in ["freeMinted()", "totalMinted()", "FREE_SHARES()", "opened()"]:
    im[v] = call(IMARS, v)
out["IMARS"] = im
print("IMARS", {k: v["int"] for k, v in im.items()})
json.dump(out, open(BASE + "run-2026-11-03-1801-reread.json", "w"), indent=1)
print("WROTE run-2026-11-03-1801-reread.json")
