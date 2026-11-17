#!/usr/bin/env python3
"""Run 1801 reread v2: single-endpoint JSON-RPC batch (per-item errors tolerated). Read-only."""
import json, subprocess, sys
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
PAD = "0" * 24 + USER[2:].lower()
EP = "https://bsc-dataseed.binance.org/"

def sel(sig):
    return keccak.new(digest_bits=256, data=sig.encode()).hexdigest()[:8]

def batch_call(calls):
    """calls: list of (key, to, data). Returns dict key -> {int, raw, error}."""
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]} for i, (_, to, data) in enumerate(calls)]
    out = subprocess.run(["curl", "-sL", "--max-time", "60", "-X", "POST",
                          "-H", "Content-Type: application/json", "--data", json.dumps(payload), EP],
                         capture_output=True, text=True).stdout
    resp = json.loads(out)
    by_id = {item["id"]: item for item in resp}
    res = {}
    for i, (key, to, data) in enumerate(calls):
        item = by_id.get(i + 1, {})
        if "error" in item:
            res[key] = {"int": None, "raw": None, "error": str(item["error"])[:160]}
        else:
            r = item.get("result")
            if r in (None, "0x", ""):
                res[key] = {"int": None, "raw": r, "error": None}
            else:
                try:
                    res[key] = {"int": int(r, 16), "raw": r, "error": None}
                except Exception:
                    res[key] = {"int": None, "raw": r, "error": None}
    return res

def block_number():
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []})
    out = subprocess.run(["curl", "-sL", "--max-time", "20", "-X", "POST",
                          "-H", "Content-Type: application/json", "--data", payload, EP],
                         capture_output=True, text=True).stdout
    return json.loads(out).get("result")

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
 "Ghoulfarm": "0x99B26bf54De6eb30c7f412aBE33e1C5523ffbD2F",
 "Phoenixgent": "0x1db6fA45EC462C23CdC4b67D6301c3d5bcc3107a",
 "Nbgent": "0x1785F9a47B8A537aAB5DABA768f36DdF4E578D03",
 "Weldagent": "0x30F3626Dc29a4d8F7A6Fe873Ad3e61cFE69BfbED",
 "Frostagent": "0x419209baA03e6A3547330ec5BC86B61FcA069EA1",
 "Nivimine": "0x4b178cB11fBF417803b6ABf525f14Bd7f8719C51",
 "NEWNFT2092": "0x20921b2B97090412a39c14B3A10C1E43b5d4aAAb",
 "E438": "0xe43818C2C6080E9d2bef53DB14092806B51711D2",
 "VAR9295": "0x9295ba269e51F920cFD7be6FAA9Ce2a12084A665",
 "Merith": "0x3dF52d687a7a5F79Fc1BE45fECD1B2Ec1Df622A7",
 "Glitchpilotfox": "0xda552a0b709d09a2532689c6E39D981f527817B6",
 "Monke": "0xD06518eA638cab567328ccD7b67e43A119C275E0",
 "Cogentbyte": "0xde94d86FDd2EEb66AaEF837e43134a5D505DC39D",
 "Argonode": "0x390a8C1322647De9F55520Fe761f4E4945813B6d",
 "bridge-Orzo-39f6": "0x39f61c0a379f132d66fb8c2adab293e6a7595b0a",
 "bridge-ZENT-751f": "0x751f8124304405154b67b9571723c23386c6b3db",
 "bridge-AgentFish-4c54": "0x4c54c3d3cc77f2c9ece2452d5670a6cc2805534d",
 "bridge-PEPE404-563a": "0x563a23b9b3bd563220cab13d028a6904ef3fa7e7",
 "bridge-QDRAW-94b7": "0x94b7e6eadf5182c824b160166aaba6fb0a1b134a",
 "bridge-AgentVOLT-2b8a": "0x2b8ae9ef424e0791c1ad526a052bd8f18d6b3625",
 "bridge-SailPixels-42bd": "0x42bdfff914afcf12047922ae58be397c1f351a27",
 "bridge-AnthroBitNFT-c7b7": "0xc7b7593aa572701d26301d9707e93b0c511e636a",
}
VIEWS = ["totalSupply()", "freeClaimed()", "freeMinted()", "freeLeft()", "FREE_SUPPLY()"]
USERVIEWS = ["mintedBy(address)", "freeUsed(address)", "balanceOf(address)"]
out = {}
blk = block_number()
out["block"] = blk
print("BLOCK", blk, int(blk, 16) if blk else None)
calls, keys = [], []
for name, addr in NFT.items():
    for v in VIEWS:
        calls.append((f"{name}||{v}", addr, "0x" + sel(v)))
    for v in USERVIEWS:
        calls.append((f"{name}||{v}", addr, "0x" + sel(v) + PAD))
    calls.append((f"{name}||owner()", addr, "0x" + sel("owner()")))
res = {}
for i in range(0, len(calls), 30):
    res.update(batch_call(calls[i:i+30]))
    print("chunk", i, "done")
for name in NFT:
    d = {v: res[f"{name}||{v}"] for v in VIEWS + USERVIEWS + ["owner()"]}
    out[name] = d
    ts, fc, fs = d["totalSupply()"]["int"], d["freeClaimed()"]["int"], d["FREE_SUPPLY()"]["int"]
    print(name, "TS", ts, "free", fc, "FREE_SUPPLY", fs,
          "pct", (round(fc / fs * 100, 1) if fc is not None and fs else None),
          "mintedBy", d["mintedBy(address)"]["int"], "freeUsed", d["freeUsed(address)"]["int"],
          "bal", d["balanceOf(address)"]["int"])
MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN = "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
tb_calls = []
for v in ["launched()", "totalShares()", "isRefundPhase()", "failed()"]:
    tb_calls.append((f"TB||{v}", MINT, "0x" + sel(v)))
tb_calls.append(("TB||tokenClaimed(address)", MINT, "0x" + sel("tokenClaimed(address)") + PAD))
tb_calls.append(("TBbal||balanceOf(address)", TOKEN, "0x" + sel("balanceOf(address)") + PAD))
tb = batch_call(tb_calls)
out["TrackB_MINT"] = {k.split("||", 1)[1]: v for k, v in tb.items() if k.startswith("TB||")}
out["TrackB_TOKEN_bal_USER"] = {"balanceOf(address)": tb["TBbal||balanceOf(address)"]}
print("TrackB", {k: v["int"] for k, v in out["TrackB_MINT"].items()},
      "TOKENbal", out["TrackB_TOKEN_bal_USER"]["balanceOf(address)"]["int"])
IMARS = "0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f"
im_calls = [(f"IM||{v}", IMARS, "0x" + sel(v)) for v in ["freeMinted()", "totalMinted()", "FREE_SHARES()", "opened()"]]
im = batch_call(im_calls)
out["IMARS"] = {k.split("||", 1)[1]: v for k, v in im.items()}
print("IMARS", {k: v["int"] for k, v in out["IMARS"].items()})
json.dump(out, open(BASE + "run-2026-11-03-1931-reread.json", "w"), indent=1)
print("WROTE run-2026-11-03-1931-reread.json")
