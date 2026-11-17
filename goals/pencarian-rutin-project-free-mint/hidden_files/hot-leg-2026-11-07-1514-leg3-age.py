#!/usr/bin/env python3
"""First-mint (Transfer-from-zero) lookup for Neonshogun 0x0015... via Ankr Advanced API getLogs.
Uses ankr.py's get_logs directly (its CLI truncates output to 4000 chars).
Read-only. Block timestamp via dataseed (Ankr timestamps not trusted)."""
import json, sys, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
import ankr as ankr_mod
from fast_rpc import _single as _fast_single

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0x001502c9ee19908f36db306da4dca7976db95bc4"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "0" * 64

out = {}
# window 1: 132000000 -> latest
r1 = ankr_mod.get_logs(ADDR, 132000000, "latest")
logs1 = r1.get("result", {}).get("logs", []) if isinstance(r1, dict) else []
out["window_132000000_latest_count"] = len(logs1)
# window 2: earliest -> 131999999 (confirm nothing earlier)
r2 = ankr_mod.get_logs(ADDR, "earliest", 131999999)
logs2 = r2.get("result", {}).get("logs", []) if isinstance(r2, dict) else []
out["window_earliest_131999999_count"] = len(logs2)
json.dump({"logs": logs1}, open(f"{BASE}/hot-leg-2026-11-07-1514-neonshogun-logs.json", "w"))
json.dump({"logs": logs2}, open(f"{BASE}/hot-leg-2026-11-07-1514-neonshogun-logs-early.json", "w"))

mints = [l for l in logs1 if l["topics"][0].lower() == TRANSFER and l["topics"][1].lower() == ZERO]
mints.sort(key=lambda l: (int(l["blockNumber"], 16), int(l["logIndex"], 16)))
out["transfer_from_zero_count"] = len(mints)
if mints:
    f = mints[0]
    blk = int(f["blockNumber"], 16)
    out["first_mint"] = {"block": blk, "tx": f["transactionHash"],
                         "to": "0x" + f["topics"][2][-40:],
                         "tokenId": int(f["topics"][3], 16),
                         "logIndex": int(f["logIndex"], 16)}
    # block timestamp via dataseed (Ankr timestamps are fake per AGENTS.md)
    ts = None
    for ep in ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]:
        try:
            v = _fast_single(ep, "eth_getBlockByNumber", [hex(blk), False], 8, retries=0)
            if v and v.get("timestamp"):
                ts = int(v["timestamp"], 16)
                break
        except Exception:
            continue
    out["first_mint"]["block_timestamp"] = ts
    if ts:
        dt = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7)))
        out["first_mint"]["wib"] = dt.strftime("%Y-%m-%d %H:%M:%S WIB")
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
        out["first_mint"]["age_minutes_at_check"] = round((now.timestamp() - ts) / 60, 1)
        out["first_mint"]["age_le_48h"] = (now.timestamp() - ts) <= 48 * 3600
    # sanity: Launched event block
    launched = [l for l in logs1 if l["topics"][0].lower() != TRANSFER]
    out["other_events_count"] = len(launched)
    if launched:
        launched.sort(key=lambda l: (int(l["blockNumber"], 16), int(l["logIndex"], 16)))
        out["first_other_event"] = {"block": int(launched[0]["blockNumber"], 16),
                                    "topic0": launched[0]["topics"][0], "tx": launched[0]["transactionHash"]}
json.dump(out, open(f"{BASE}/hot-leg-2026-11-07-1514-leg3-age.json", "w"), indent=1)
print(json.dumps(out, indent=1))
