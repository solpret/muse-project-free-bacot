#!/usr/bin/env python3
"""Sentrix first-mint walk via Ankr getLogs, address-filtered (read-only).
Descending 2000-block chunks from head to 131300000; stops at the first empty
chunk below the mint range. Earliest mint block timestamp -> WIB."""
import json, sys, time, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
ADDR = "0xb7dce0412BB89dE075413855875D1DB31AC89E8f"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def ankr_logs(cf, ct):
    logs, token, pages = [], None, 0
    while True:
        params = {"blockchain": "bsc", "fromBlock": hex(cf), "toBlock": hex(ct),
                  "address": ADDR, "pageSize": 1000, "decodeLogs": False,
                  "topics": [TRANSFER, ZERO]}
        if token: params["pageToken"] = token
        body = ankr_post("ankr_getLogs", params, timeout=30)
        res = body.get("result", body) if isinstance(body, dict) else body
        logs += res.get("logs", []) if isinstance(res, dict) else []
        token = res.get("nextPageToken") if isinstance(res, dict) else None
        pages += 1
        if not token or pages >= 10: break
    return logs
def block_ts(b):
    for ep in EPS:
        try:
            blk = _single(ep, "eth_getBlockByNumber", [hex(b), False], 10, retries=0)
            return int(blk["timestamp"], 16)
        except Exception:
            continue
    return None
HEAD = int(_single(EPS[0], "eth_blockNumber", [], 10, retries=0), 16)
print("head", HEAD, flush=True)
earliest, empty_below = None, None
chunk_to = HEAD
while chunk_to > 131300000:
    cf = max(131300000, chunk_to - 1999)
    try:
        logs = ankr_logs(cf, chunk_to)
    except Exception as e:
        print("chunk FAILED", cf, chunk_to, type(e).__name__, str(e)[:160], flush=True)
        break
    print(f"chunk {cf}-{chunk_to}: {len(logs)} from-zero mints", flush=True)
    if logs:
        for lg in logs:
            b = int(lg["blockNumber"], 16)
            if earliest is None or b < earliest[0]:
                earliest = (b, lg.get("transactionHash"))
        chunk_to = cf - 1
    else:
        if earliest is not None:
            empty_below = (cf, chunk_to); break
        chunk_to = cf - 1
print("earliest", earliest, "empty_below", empty_below, flush=True)
if earliest:
    ts = block_ts(earliest[0])
    wib = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat() if ts else None
    print("earliest_block", earliest[0], "tx", earliest[1], "wib", wib, flush=True)
    json.dump({"earliest_block": earliest[0], "tx": earliest[1], "timestamp": ts,
               "wib": wib, "empty_below": empty_below, "head": HEAD},
              open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-03-0831-sentrix-firstmint3.json", "w"), indent=1)
