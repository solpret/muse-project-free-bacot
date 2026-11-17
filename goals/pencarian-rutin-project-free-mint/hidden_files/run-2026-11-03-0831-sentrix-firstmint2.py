#!/usr/bin/env python3
"""Retry Sentrix first-mint walk from chunk 131348019 downward (read-only).
Sequential _single over dataseeds with retries, 2000-block chunks."""
import json, sys, time, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
ADDR = "0xb7dce0412BB89dE075413855875D1DB31AC89E8f"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def logs_for(cf, ct):
    last = None
    for attempt in range(3):
        for ep in EPS:
            try:
                return _single(ep, "eth_getLogs", [{"address": ADDR, "fromBlock": hex(cf),
                                                    "toBlock": hex(ct),
                                                    "topics": [TRANSFER, ZERO]}], 10, retries=0)
            except Exception as e:
                last = e
        time.sleep(3)
    raise last
def block_ts(b):
    for ep in EPS:
        try:
            blk = _single(ep, "eth_getBlockByNumber", [hex(b), False], 10, retries=0)
            return int(blk["timestamp"], 16)
        except Exception:
            continue
    return None
earliest = None
chunk_to = 131350018
empty_below = None
while chunk_to > 131300000:
    chunk_from = max(131300000, chunk_to - 249)
    try:
        logs = logs_for(chunk_from, chunk_to) or []
    except Exception as e:
        print("chunk FAILED after retries", chunk_from, chunk_to, type(e).__name__, str(e)[:120], flush=True)
        break
    print(f"chunk {chunk_from}-{chunk_to}: {len(logs)} from-zero mints", flush=True)
    if logs:
        for lg in logs:
            b = int(lg["blockNumber"], 16)
            if earliest is None or b < earliest[0]:
                earliest = (b, lg.get("transactionHash"))
        chunk_to = chunk_from - 1
    else:
        if earliest is not None:
            empty_below = (chunk_from, chunk_to)
            break
        chunk_to = chunk_from - 1
print("earliest", earliest, "empty_below", empty_below, flush=True)
if earliest:
    ts = block_ts(earliest[0])
    wib = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat() if ts else None
    print("earliest_block", earliest[0], "tx", earliest[1], "wib", wib, flush=True)
    json.dump({"earliest_block": earliest[0], "tx": earliest[1], "timestamp": ts,
               "wib": wib, "empty_below": empty_below},
              open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-03-0831-sentrix-firstmint2.json", "w"), indent=1)
