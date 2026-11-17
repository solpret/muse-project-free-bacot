#!/usr/bin/env python3
"""Run 2001 MERGEBORN first-mint walk v2: walk BACK until first EMPTY chunk;
the earliest log in the last non-empty chunk is the first mint. Read-only."""
import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
M = "0x348455be18b700cae8aa425bd84e456e47f16e8b"
EPS = ["https://bsc-dataseed2.bnbchain.org", "https://bsc-dataseed1.bnbchain.org",
       "https://bsc.publicnode.com", "https://bsc-dataseed3.bnbchain.org"]

def block_ts(blk):
    for rpc in EPS:
        try:
            b = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                            "params": [hex(blk), False]}).encode()
            req = urllib.request.Request(rpc, data=b, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r: return int(json.load(r)["result"]["timestamp"], 16)
        except Exception: continue
    return None

head = None
for rpc in EPS:
    try:
        b = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
        req = urllib.request.Request(rpc, data=b, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as r: head = int(json.load(r)["result"], 16); break
    except Exception: continue
print("HEAD", head, flush=True)
topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
zero = "0x" + "00" * 32
end = head
oldest = None
chunks = 0
for i in range(120):
    frm = max(0, end - 999)
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(frm),
            "toBlock": hex(end), "address": M, "pageSize": 1000, "decodeLogs": False,
            "topics": [topic, zero]}, timeout=30)
        logs = body.get("result", {}).get("logs", [])
    except Exception as e:
        print(f"  chunk {frm}-{end} ERR {e}", flush=True)
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
    import datetime
    if oldest["first_ts"]:
        oldest["first_wib"] = datetime.datetime.fromtimestamp(
            oldest["first_ts"], datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
print("RESULT", json.dumps(oldest), f"chunks_walked={chunks}", flush=True)
json.dump({"head": head, "chunks_walked": chunks, "first_mint": oldest},
          open(f"{BASE}/run-2026-11-06-2001-merge-firstmint.json", "w"), indent=1)
print("DONE", flush=True)
