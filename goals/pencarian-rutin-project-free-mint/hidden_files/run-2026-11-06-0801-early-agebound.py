#!/usr/bin/env python3
"""Run 0801: 48h age-bound check for the 10 leads whose first mint predates the
watermark (totals far exceed gap+window Transfer-from-zero counts).
Bound block ~131534000 ~= 2026-11-04 08:11 WIB (48h before scan window).
One existence query per contract over [130000000, 131534000], pageSize 1:
any mint there => first mint older than 48h (age-excluded if not sold out).
If hits, binary-search the exact earliest mint block."""
import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0801"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
BOUND = 131534000

LEADS = {
 "Tacotron": "0x05deBE4445232205AE7E79d02cb5DE5AA0641efF",
 "AgentPad Pass": "0x01c106835091c09D5c69737631Af133530093C89",
 "Cloudpuff": "0xe09131bBb48E653C5b2D64099324f14000d67De5",
 "Thalvorix Hero": "0x6D862c8B847323961FCD349ffFbee0133F6B929A",
 "Binance Agent Oracle": "0xcBe2DBBFF4264Dc67Bf557c64e29997B82439354",
 "Agent Creatures": "0xF7245511A890a42F911c776824c665E2da3cedb3",
 "Crown Race Pass": "0x924B1c9203EBC3EE3D4Fd2Af758B2DBDD3856e0c",
 "CodexCrew": "0xA5921507449eB36eB16BE3ffedBEEe5439C9bDef",
 "Diamondo": "0x58C96735342e5c2e8Ba542E4aAc2a1500Cc769C6",
 "GOAT": "0xE7a548606eECB32a93B227411b6343B0399DC7C0",
}

def exists_mint(addr, frm, to):
    params = {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(to),
              "pageSize": 1, "decodeLogs": False, "address": addr,
              "topics": [TRANSFER, ZERO_TOPIC]}
    body = ankr_post("ankr_getLogs", params, timeout=30)
    result = body.get("result", {}) if isinstance(body, dict) else {}
    logs = result.get("logs", [])
    return len(logs), (int(logs[0]["blockNumber"], 16) if logs else None)

def earliest_mint(addr, lo, hi):
    """Binary search earliest Transfer-from-zero block in [lo, hi]; assumes >=1 exists."""
    while lo < hi:
        mid = (lo + hi) // 2
        n, _ = exists_mint(addr, lo, mid)
        if n > 0:
            hi = mid
        else:
            lo = mid + 1
        time.sleep(1.0)
    return lo

out = {}
for name, addr in LEADS.items():
    t0 = time.time()
    try:
        n, first_in_range = exists_mint(addr, 130000000, BOUND)
        rec = {"address": addr, "bound_block": BOUND, "mints_before_bound": n}
        if n > 0:
            rec["earliest_block"] = earliest_mint(addr, 130000000, BOUND)
            rec["age_le_48h"] = False
        else:
            rec["earliest_block"] = None
            rec["age_le_48h"] = True
        rec["elapsed_s"] = round(time.time() - t0, 1)
    except Exception as e:
        rec = {"address": addr, "bound_block": BOUND, "error": repr(e), "age_le_48h": None}
    out[name] = rec
    print(name, addr, "before_bound=", rec.get("mints_before_bound"),
          "earliest=", rec.get("earliest_block"), "age<=48h=", rec.get("age_le_48h"),
          "err=", rec.get("error"), flush=True)
    json.dump(out, open(f"{BASE}/run-{TS}-early-agebound.json", "w"), indent=1)
print("DONE", flush=True)
