#!/usr/bin/env python3
"""Kicks first-mint retry: eth_getLogs Transfer-from-zero, 100-block chunks,
publicnode first, dataseed fallback. Run 2026-11-14 05:31 WIB. Read-only."""
import json, subprocess, time

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0x5726100e0D9ACB20cFB13e80e0fe42DF146730A8"
EPS = ["https://bsc-rpc.publicnode.com/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
t0 = time.time()

def post_rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)

def get_logs(frm, to):
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
               "params": [{"fromBlock": hex(frm), "toBlock": hex(to), "address": ADDR,
                           "topics": [TRANSFER, ZERO_TOPIC]}]}
    for ep in EPS:
        try:
            res = post_rpc(ep, payload, timeout=60)
            if isinstance(res, dict) and "result" in res:
                return res["result"], ep
        except Exception as e:
            print(f"  {frm}-{to} ep {ep} exc {str(e)[:60]}", flush=True)
    return None, None

first_block = first_tx = None
# search 133425359-133426358 in 100-block chunks, newest first
chunks = [(lo, min(lo + 99, 133426358)) for lo in range(133425359, 133426359, 100)][::-1]
for lo, hi in chunks:
    logs, ep = get_logs(lo, hi)
    print(f"chunk {lo}-{hi}: {None if logs is None else len(logs)} logs via {ep} ({time.time()-t0:.0f}s)", flush=True)
    if logs:
        f = min(logs, key=lambda l: int(l["blockNumber"], 16))
        first_block = int(f["blockNumber"], 16); first_tx = f["transactionHash"]
        break
ts = None
if first_block is not None:
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                                "params": [hex(first_block), False]}, timeout=60)
            if isinstance(res, dict) and isinstance(res.get("result"), dict):
                ts = int(res["result"]["timestamp"], 16); break
        except Exception: continue
out = {"first_mint_block": first_block, "first_mint_tx": first_tx, "first_mint_ts": ts,
       "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open(BASE + "run-2026-11-14-0531-kicks-firstmint3.json", "w"), indent=1)
print(json.dumps(out, indent=1))
