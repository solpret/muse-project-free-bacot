#!/usr/bin/env python3
"""Run 2031 Hourglas first-mint walk: exponential probe bracket, then walk back
in 1000-block chunks until the first EMPTY chunk. Read-only."""
import json, sys, urllib.request, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
M = "0xc2027F9407eA355eeD5845Bb5e653aeed671f212"
EPS = ["https://bsc-dataseed2.bnbchain.org", "https://bsc-dataseed1.bnbchain.org",
       "https://bsc.publicnode.com", "https://bsc-dataseed3.bnbchain.org"]
TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32

def block_ts(blk):
    for rpc in EPS:
        try:
            b = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                            "params": [hex(blk), False]}).encode()
            req = urllib.request.Request(rpc, data=b, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r: return int(json.load(r)["result"]["timestamp"], 16)
        except Exception: continue
    return None

def probe(frm, to):
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(frm),
            "toBlock": hex(to), "address": M, "pageSize": 1000, "decodeLogs": False,
            "topics": [TOPIC, ZERO]}, timeout=30)
        return body.get("result", {}).get("logs", [])
    except Exception as e:
        print(f"  probe {frm}-{to} ERR {e}", flush=True)
        return None

import sys as _sys
_sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as _single_head
head = None
for _ep in ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
            "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]:
    try:
        head = int(_single_head(_ep, "eth_blockNumber", [], 8, retries=0), 16)
        break
    except Exception:
        continue
if head is None:
    head = 132022233  # scan latest block ~21:09 WIB; walk starts slightly behind head, safe
    print("HEAD fallback = scan latest 132022233", flush=True)
print("HEAD", head, flush=True)

# Exponential probes: chunk [head-off-999, head-off]
last_nonempty_off = 0
empty_off = None
for off in [0, 10000, 30000, 100000, 200000, 400000, 800000]:
    frm, to = head - off - 999, head - off
    logs = probe(frm, to)
    if logs is None:
        print(f"  probe off={off} ERROR, abort bracket", flush=True)
        break
    print(f"  probe off={off} [{frm}-{to}]: {len(logs)} logs", flush=True)
    if logs:
        last_nonempty_off = off
    else:
        empty_off = off
        break
if empty_off is None:
    print("  no empty probe within 800k blocks (~4.5 days); first mint older than bracket", flush=True)
    result = {"head": head, "bracket": "older-than-800k", "first_mint": None}
    json.dump(result, open(f"{BASE}/run-2026-11-06-2031-hourglas-firstmint.json", "w"), indent=1)
    print("DONE older-than-bracket", flush=True)
    raise SystemExit(0)

# Walk back 1000-block chunks from the last non-empty probe end until empty
end = head - last_nonempty_off
oldest = None
chunks = 0
for i in range(400):
    frm = max(0, end - 999)
    logs = probe(frm, end)
    if logs is None:
        print(f"  walk chunk {frm}-{end} ERR, abort", flush=True)
        break
    chunks += 1
    if not logs:
        print(f"  empty chunk {frm}-{end}; stop", flush=True)
        break
    first = min(logs, key=lambda l: int(l["blockNumber"], 16))
    oldest = {"first_block": int(first["blockNumber"], 16), "n_logs_in_chunk": len(logs),
              "chunk_from": frm, "chunk_to": end}
    print(f"  chunk {frm}-{end}: {len(logs)} logs, earliest {oldest['first_block']}", flush=True)
    end = frm - 1
    if end <= 0:
        break
if oldest:
    oldest["first_ts"] = block_ts(oldest["first_block"])
    if oldest["first_ts"]:
        oldest["first_wib"] = datetime.datetime.fromtimestamp(
            oldest["first_ts"], datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
print("RESULT", json.dumps(oldest), f"chunks_walked={chunks}", flush=True)
json.dump({"head": head, "bracket_offsets": [last_nonempty_off, empty_off],
           "chunks_walked": chunks, "first_mint": oldest},
          open(f"{BASE}/run-2026-11-06-2031-hourglas-firstmint.json", "w"), indent=1)
print("DONE", flush=True)
