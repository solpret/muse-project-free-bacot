#!/usr/bin/env python3
"""Main run 2026-11-03 10:31 WIB: first-mint walk for Animora group. Read-only."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from ankr import ankr_post
from fast_rpc import _single
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
TARGETS = {
    "Animora": "0x150699b44B36b542B9F954272bDD0aC3fDD9519b",
    "Golemar": "0x4e06728894F3f31CbB32B97d6905639FfE2a147B",
    "Homunqul": "0x5539dD54c00094Cbd186f08AA2d8fF3A8c098ddE",
    "Praxion": "0xEA1e4AA5ecD147035eB005aDc8013959bA852799",
    "Eidolyn": "0x94c4834B186938F95EDC67FF0536Ac17F3102523",
}
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]

def block_ts(b):
    for ep in EPS:
        try:
            blk = _single(ep, "eth_getBlockByNumber", [hex(b), False], 8, retries=0)
            return int(blk["timestamp"], 16)
        except Exception:
            continue
    return None

out = {}
for name, addr in TARGETS.items():
    end = 131349240  # chunk below the known pre-window chunk 131349241-131351240
    earliest = None
    chunks = []
    for _ in range(12):
        frm = end - 2000 + 1
        to = end
        try:
            body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(frm),
                "toBlock": hex(to), "address": addr, "pageSize": 1000,
                "decodeLogs": False, "topics": [TRANSFER, ZERO]}, timeout=30)
            res = body.get("result", body) if isinstance(body, dict) else body
            logs = res.get("logs", []) if isinstance(res, dict) else []
        except Exception as e:
            chunks.append((frm, to, f"ERROR {type(e).__name__}: {str(e)[:120]}"))
            break
        blks = sorted(int(l["blockNumber"], 16) for l in logs if l.get("blockNumber"))
        chunks.append((frm, to, len(logs), blks[0] if blks else None, blks[-1] if blks else None))
        print(name, chunks[-1], flush=True)
        if not blks:
            break  # chunk below is empty: earliest in previous chunk is first mint
        earliest = blks[0]
        end = frm - 1
    ts = block_ts(earliest) if earliest else None
    out[name] = {"address": addr, "firstMintBlock": earliest, "firstMintTs": ts, "chunks": chunks}
    print(name, "FIRST", earliest, ts, flush=True)
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-03-1031-animora-walk.json", "w"), indent=1)
