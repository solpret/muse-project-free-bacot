#!/usr/bin/env python3
"""First-mint walk for Sentrix (read-only). Descending eth_getLogs, address-filtered,
Transfer topic, from == zero address, 2000-block chunks, until an empty chunk is
found below the mint range. Earliest mint block timestamp -> WIB launch time."""
import json, sys, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
ADDR = "0xb7dce0412BB89dE075413855875D1DB31AC89E8f"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
HEAD = int(race("eth_blockNumber", []), 16)
print("head", HEAD, flush=True)
earliest = None
chunk_to = HEAD
empty_below = None
while chunk_to > 131280000:
    chunk_from = max(131280000, chunk_to - 1999)
    try:
        logs = race("eth_getLogs", [{"address": ADDR, "fromBlock": hex(chunk_from),
                                     "toBlock": hex(chunk_to),
                                     "topics": [TRANSFER, ZERO]}])
    except Exception as e:
        print("chunk failed", chunk_from, chunk_to, type(e).__name__, str(e)[:160], flush=True)
        break
    logs = logs or []
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
    blk = race("eth_getBlockByNumber", [hex(earliest[0]), False])
    ts = int(blk["timestamp"], 16)
    wib = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7)))
    print("earliest_block", earliest[0], "tx", earliest[1], "timestamp", ts, "wib", wib.isoformat(), flush=True)
    json.dump({"earliest_block": earliest[0], "tx": earliest[1], "timestamp": ts,
               "wib": wib.isoformat(), "empty_below": empty_below, "head": HEAD},
              open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-03-0831-sentrix-firstmint.json", "w"), indent=1)
