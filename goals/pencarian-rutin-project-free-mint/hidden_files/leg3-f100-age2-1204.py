#!/usr/bin/env python3
"""First-mint lookup for Pathwyrm via authenticated Ankr ankr_getLogs (module, no CLI truncation). Read-only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from datetime import datetime
from zoneinfo import ZoneInfo

ADDR = "0xf100c608913dC07ed268bEA865Fca10004f04657"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
HEAD = 132142796

def ankr_logs(from_block, to_block, topics, address=None, max_pages=10):
    logs, page_token, pages = [], None, 0
    while True:
        params = {"blockchain": "bsc", "fromBlock": hex(from_block), "toBlock": hex(to_block),
                  "pageSize": 1000, "decodeLogs": False, "topics": topics}
        if address:
            params["address"] = address
        if page_token:
            params["pageToken"] = page_token
        body = ankr_post("ankr_getLogs", params, timeout=30)
        result = body.get("result", {}) if isinstance(body, dict) else {}
        logs.extend(result.get("logs", []))
        page_token = result.get("nextPageToken")
        pages += 1
        if not page_token or pages >= max_pages:
            break
        time.sleep(2.2)
    return logs, pages

# Window: last 60k blocks (~50h). Narrow to this contract + Transfer-from-zero.
logs, pages = ankr_logs(HEAD - 60000, HEAD, [TRANSFER, ZERO], address=ADDR)
print("pages:", pages, "mint logs:", len(logs))
out = {"pages": pages, "n_mints_window": len(logs)}
if logs:
    first = min(logs, key=lambda l: (int(l["blockNumber"], 16), int(l["logIndex"], 16)))
    ts = int(first["timestamp"], 16)
    out["first_mint_block"] = int(first["blockNumber"], 16)
    out["first_mint_tx"] = first["transactionHash"]
    out["first_mint_token"] = int(first["topics"][3], 16)
    out["first_mint_minter"] = "0x" + first["topics"][2][-40:]
    out["first_mint_wib"] = datetime.fromtimestamp(ts, tz=ZoneInfo("Asia/Jakarta")).isoformat()
    out["age_hours"] = round((time.time() - ts) / 3600, 2)
    out["age_le_48h"] = (time.time() - ts) <= 48 * 3600
    last = max(logs, key=lambda l: (int(l["blockNumber"], 16), int(l["logIndex"], 16)))
    out["last_mint_block"] = int(last["blockNumber"], 16)
    out["last_mint_wib"] = datetime.fromtimestamp(int(last["timestamp"], 16), tz=ZoneInfo("Asia/Jakarta")).isoformat()
    now = time.time()
    out["mints_last_1h"] = sum(1 for l in logs if now - int(l["timestamp"], 16) <= 3600)
    out["mints_prev_1h"] = sum(1 for l in logs if 3600 < now - int(l["timestamp"], 16) <= 7200)
    out["unique_minters_window"] = len(set("0x" + l["topics"][2][-40:].lower() for l in logs))
print(json.dumps(out, indent=1))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/leg3-f100-age-1204.json", "w"), indent=1)
