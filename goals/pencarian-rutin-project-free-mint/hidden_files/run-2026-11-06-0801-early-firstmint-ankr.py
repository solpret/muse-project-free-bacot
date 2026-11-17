#!/usr/bin/env python3
"""Run 0801: Ankr-based first-mint verification for the 12 genuine agent-shaped
first-seen leads (triage dataseed eth_getLogs failed for all).
Range: [131899549 (watermark), first_block-1] per contract, address-filtered
ankr_getLogs, paging pageSize 1000. Records earlier-mint count + earliest block.
Limitation stated in output: pre-watermark existence excluded only by absence
from onchain-scan-seen.json + snapshot (which have known coverage gaps)."""
import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0801"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
FROM = 131899549

LEADS = {
 "Tacotron": ("0x05deBE4445232205AE7E79d02cb5DE5AA0641efF", 131918254),
 "AgentPad Pass": ("0x01c106835091c09D5c69737631Af133530093C89", 131918338),
 "Cloudpuff": ("0xe09131bBb48E653C5b2D64099324f14000d67De5", 131918590),
 "Thalvorix Hero": ("0x6D862c8B847323961FCD349ffFbee0133F6B929A", 131918521),
 "Binance Agent Oracle": ("0xcBe2DBBFF4264Dc67Bf557c64e29997B82439354", 131918261),
 "Agent Creatures": ("0xF7245511A890a42F911c776824c665E2da3cedb3", 131919026),
 "Data Synth": ("0x7Bd19ee3c72b4544787EbA0ebD655e1376FE3642", 131918469),
 "Crown Race Pass": ("0x924B1c9203EBC3EE3D4Fd2Af758B2DBDD3856e0c", 131918569),
 "CodexCrew": ("0xA5921507449eB36eB16BE3ffedBEEe5439C9bDef", 131918736),
 "Diamondo": ("0x58C96735342e5c2e8Ba542E4aAc2a1500Cc769C6", 131918980),
 "GOAT": ("0xE7a548606eECB32a93B227411b6343B0399DC7C0", 131919124),
 "Zero Genesis": ("0x7807202FBE09f4AAC9ac312ed593ba16806F6b34", 131919173),
}

def earlier_mints(addr, frm, to):
    """Count + earliest Transfer-from-zero logs for addr in [frm, to]."""
    total = 0
    earliest = None
    token = None
    pages = 0
    while True:
        params = {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(to),
                  "pageSize": 1000, "decodeLogs": False, "address": addr,
                  "topics": [TRANSFER, ZERO_TOPIC]}
        if token:
            params["pageToken"] = token
        body = ankr_post("ankr_getLogs", params, timeout=30)
        result = body.get("result", {}) if isinstance(body, dict) else {}
        logs = result.get("logs", [])
        for lg in logs:
            total += 1
            b = int(lg.get("blockNumber", "0x0"), 16)
            earliest = b if earliest is None else min(earliest, b)
        token = result.get("nextPageToken")
        pages += 1
        if not token or pages >= 15:
            break
        time.sleep(2.2)
    return total, earliest, pages

out = {}
for name, (addr, fb) in LEADS.items():
    t0 = time.time()
    try:
        total, earliest, pages = earlier_mints(addr, FROM, fb - 1)
        rec = {"address": addr, "first_block_window": fb, "range_checked": [FROM, fb - 1],
               "earlier_mints": total, "earliest_block": earliest,
               "first_mint_verified": total == 0, "pages": pages,
               "elapsed_s": round(time.time() - t0, 1)}
    except Exception as e:
        rec = {"address": addr, "first_block_window": fb, "range_checked": [FROM, fb - 1],
               "earlier_mints": None, "earliest_block": None,
               "first_mint_verified": False, "error": repr(e),
               "elapsed_s": round(time.time() - t0, 1)}
    out[name] = rec
    print(name, addr, "earlier=", rec["earlier_mints"], "earliest_block=", rec.get("earliest_block"),
          "verified=", rec["first_mint_verified"], "err=", rec.get("error"), flush=True)
    json.dump(out, open(f"{BASE}/run-{TS}-early-firstmint-ankr.json", "w"), indent=1)
print("DONE", flush=True)
