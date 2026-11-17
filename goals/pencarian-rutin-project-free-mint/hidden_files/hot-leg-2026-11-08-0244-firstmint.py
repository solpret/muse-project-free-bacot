#!/usr/bin/env python3
"""Ninetailix first-mint: narrow getLogs windows (Ankr public now needs API key; dataseed limit)."""
import json, urllib.request, datetime, subprocess
ADDR = "0x809215729bcbff2ef31dea5efd6c12a6b788ba9a"
def post(rpc, method, params, timeout=25):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r: return json.load(r)
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
blk = int(post(EPS[0], "eth_blockNumber", [], 10)["result"], 16)
print("current block:", blk)
TOPIC0 = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
found = None
for width in (5000, 20000):
    from_blk = hex(blk - width)
    for rpc in EPS:
        try:
            o = post(rpc, "eth_getLogs", [{"fromBlock": from_blk, "toBlock": "latest", "address": ADDR, "topics": [TOPIC0, ZERO]}], 30)
            if "error" in o:
                print(f"w={width} {rpc} error:", o["error"].get("message")); continue
            logs = o.get("result", [])
            print(f"w={width} {rpc} logs:", len(logs))
            if logs:
                first = logs[0]
                fblk = int(first["blockNumber"], 16)
                ts = int(post(EPS[0], "eth_getBlockByNumber", [first["blockNumber"], False], 10)["result"]["timestamp"], 16)
                wib = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
                found = {"first_mint_block": fblk, "first_mint_ts": ts, "first_mint_wib": wib,
                         "first_mint_tx": first["transactionHash"], "first_tokenId": int(first["topics"][3], 16),
                         "logs_total": len(logs), "logs_via": rpc, "window_blocks": width,
                         "from_block": from_blk, "current_block": blk}
                print(json.dumps(found, indent=1))
                break
        except Exception as e:
            print(f"w={width} {rpc} EXC:", type(e).__name__, e)
    if found: break
json.dump(found or {"error": "first mint not found in 20000-block window", "current_block": blk},
          open("hot-leg-2026-11-08-0244-firstmint.json", "w"), indent=1)
# Boltbook post EN full read
html = subprocess.run(["curl","-sS","-L","--max-time","20","-A","Mozilla/5.0","https://boltbook.fun/p/pFdD0MdrJSat?lang=en"],
                      capture_output=True, text=True, timeout=25).stdout
open("hot-leg-2026-11-08-0244-boltbook-post-en.html","w").write(html)
print("post html bytes:", len(html))
