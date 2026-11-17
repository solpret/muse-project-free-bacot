#!/usr/bin/env python3
"""Run 0901 special2: binanceai track-B + Grove freeOpen + age-watch
(MONOLITH, Night Bandits Club, King's Game, Lenx) + track-C specific
(BOME-50CD, NUSA, FOUNT, PACTA). Read-only; writes only
run-2026-11-10-0901-special2.json. Curl transport, --max-time 25."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
T0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            return {k: (None if (isinstance(it, dict) and "error" in it)
                        else (to_int(it.get("result")) if isinstance(it, dict) else None))
                    for it, k in zip(res, keys)}
        except Exception:
            continue
    return None

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

out = {"block": None, "started_wib": "2026-11-10 09:01 WIB",
       "binanceai": {}, "grove": {}, "age_watch": {}, "track_c_specific": {}}
out["block"] = get_block()
print("BLOCK", out["block"], flush=True)

BIN_MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
BIN_TOKEN = "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
GROVE = "0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c"

def do(label, addr, views):
    got = batch(addr, views)
    d = {"address": addr}
    if got is None:
        for v in views:
            d[v.split("(")[0] + ("_user" if "(address)" in v else "")] = None
        d["_batch_fail"] = True
    else:
        d.update(got)
    print(label, json.dumps(d), flush=True)
    return d

# 1. Track B — binanceai
out["binanceai"]["mint"] = do("binanceai_mint", BIN_MINT,
    ["launched()", "failed()", "isRefundPhase()", "totalShares()", "tokenClaimed(address)"])
out["binanceai"]["token_balance"] = do("binanceai_token", BIN_TOKEN, ["balanceOf(address)"])

# Grove freeOpen
out["grove"] = do("grove", GROVE,
    ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
     "FREE_SUPPLY()", "MAX_SUPPLY()", "freeOpen()", "mintOpen()",
     "freeClaimed(address)", "balanceOf(address)"])

# 2. Age-watch
LEAN = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
        "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "freeOpen()",
        "balanceOf(address)", "freeClaimed(address)"]
out["age_watch"]["MONOLITH"] = do("MONOLITH", "0xcdA4A0EF9C0a626b2450168fd8F90f62C51A569b", LEAN)
out["age_watch"]["Night Bandits Club"] = do("NightBandits", "0xa849aEd9dC19FBA823CcEf1FA01BdA72Fbb8fcDf",
    LEAN + ["freeTotal()", "freeUsed()", "freeTakenBy(address)", "opensAt()", "closesAt()"])
out["age_watch"]["King's Game"] = do("KingsGame", "0x9eA27f3F0919DaF6a4401CFd09563162d395061D", LEAN)
out["age_watch"]["Lenx Agent Pass"] = do("Lenx", "0x6E252E3a3584BD6a64C103e4eDFa761f6335980F",
    LEAN + ["FREE_CAP()", "freeRemaining()"])

# 3. Track C specific
out["track_c_specific"]["BOME-50CD"] = do("BOME", "0x50CDd91b31cED977D2776825BBaD72e99FF0830E",
    ["mintOpen()", "opened()", "FREE_CAP()", "freeLotsMinted()", "freeSharesRemaining()",
     "totalSupply()", "freeUsed(address)", "balanceOf(address)"])
out["track_c_specific"]["NUSA"] = do("NUSA_sale", "0x7D08289E962f5aEc00d56D67322eb2FD056B687c",
    ["freeMinted()", "sharesMinted()", "freeSharesRemaining()", "soldOut()", "closed()",
     "freeClaimed(address)", "freeAvailable(address)"])
out["track_c_specific"]["NUSA_token_balance"] = do("NUSA_token", "0x6f91Fc7160Dc873b98a0B21Bdd974AE546FCC19a",
    ["balanceOf(address)"])
out["track_c_specific"]["FOUNT"] = do("FOUNT", "0x4d146a58cB2D38ce91961358Dc090282e6ec7396",
    ["totalSupply()", "freeMinted()", "FREE_SUPPLY()", "FREE_SLOTS()", "FREE_AMOUNT()",
     "freeClaimed(address)", "balanceOf(address)"])
out["track_c_specific"]["PACTA"] = do("PACTA_sale", "0x6Cbf2E389AfBEb8fCC45d790E21D66F71A2b78Ca",
    ["freeMinted()", "sharesMinted()", "freeSharesRemaining()", "soldOut()",
     "freeClaimed(address)", "balanceOf(address)"])
out["track_c_specific"]["PACTA_token_balance"] = do("PACTA_token", "0x8372f2e05ba2b186511f28b3d5d80d66e7278631",
    ["balanceOf(address)"])

out["elapsed_s"] = round(time.time() - T0, 1)
with open(f"{BASE}/run-2026-11-10-0901-special2.json", "w") as f:
    json.dump(out, f, indent=1)
print(f"DONE in {out['elapsed_s']}s", flush=True)
print(json.dumps(out, indent=1))
