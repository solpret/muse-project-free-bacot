#!/usr/bin/env python3
"""Find HOG ORBIT first mint via Ankr ankr_getLogs (registered API).
Prints only a summary (no full log dump)."""
import json, sys, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import get_logs

CA = "0x7bc0b487febcbb1caa781148bf05a8cd72d02ec5"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
res = get_logs(CA, 132190000, 132228700, topics=[TRANSFER, ZERO])
logs = res.get("result", {}).get("logs", [])
print("logs:", len(logs), "nextPageToken:", res.get("result", {}).get("nextPageToken"))
if logs:
    first = min(logs, key=lambda l: int(l["blockNumber"], 16))
    ts = int(first["timestamp"], 16)
    wib = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7)))
    print("first_mint_block:", int(first["blockNumber"], 16))
    print("first_mint_wib:", wib.strftime("%Y-%m-%d %H:%M:%S WIB"))
    print("first_mint_tokenId:", int(first["topics"][3], 16))
    print("first_mint_minter:", "0x" + first["topics"][2][-40:])
    print("first_mint_tx:", first["transactionHash"])
    last = max(logs, key=lambda l: int(l["blockNumber"], 16))
    print("last_mint_block_in_window:", int(last["blockNumber"], 16))
