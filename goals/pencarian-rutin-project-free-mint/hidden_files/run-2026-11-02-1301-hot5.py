#!/usr/bin/env python3
import json, sys
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from ankr import ankr_post
from fast_rpc import _single
ZERO = "0x" + "0"*64
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
EPS = ["https://bsc-dataseed.binance.org/"]
def decode_str(val):
    try:
        b = bytes.fromhex(val[2:])
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception as e: return f"ERR {e}"
adds = ["0x3203D93cE535c2ec88c99d1967324Fe556A4e8f6","0xa1bC72EcEC9f1F73Be9ED0c21b5cB880f42dA1A3","0xAB23259Cac7D87d8cfE0ADaba80827d3e3AcC99F","0x553484EC13486cAec4cdB884B9953e381dd1d66B","0x693777E674fa13a8318821919296d52E90898191"]
# name/symbol via selector 0x06fdde03 / 0x95d89b41
out = {}
for a in adds:
    nm = _single(EPS[0], "eth_call", [{"to": a, "data": "0x06fdde03"}, "latest"], 8, retries=0)
    sy = _single(EPS[0], "eth_call", [{"to": a, "data": "0x95d89b41"}, "latest"], 8, retries=0)
    out[a] = {"name": decode_str(nm), "symbol": decode_str(sy)}
    # first mint: ankr_getLogs address-filtered, from 131150000
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": "131150000", "toBlock": "latest", "address": [a.lower()], "topics": [TRANSFER, ZERO, None]}, timeout=30)
        logs = body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
        blocks = sorted(int(l["blockNumber"], 16) if isinstance(l.get("blockNumber"), str) else l["blockNumber"] for l in logs)
        out[a]["logs_from_131150000"] = len(logs)
        out[a]["first_mint_block_in_range"] = blocks[0] if blocks else None
    except Exception as e:
        out[a]["logs_error"] = f"{type(e).__name__}: {str(e)[:160]}"
    print(a, out[a])
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-1301-hot5.json", "w"), indent=1)
