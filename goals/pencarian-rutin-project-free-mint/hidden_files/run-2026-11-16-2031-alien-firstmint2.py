#!/usr/bin/env python3
"""ALIEN first-mint: eth_getLogs 200-block chunks, window 133920769-133924439. Bounded, read-only."""
import json, subprocess, datetime
EP = "https://bsc-dataseed.binance.org/"
ADDR = "0xf5767ac3beb8bbfaf4596dfc1925fc5aca779dcb"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
def rpc(method, params, timeout=30):
    payload = {"jsonrpc":"2.0","id":1,"method":method,"params":params}
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps(payload)], capture_output=True, text=True, timeout=timeout+10).stdout
    try: return json.loads(out)
    except Exception: return {"error": out[:100]}
b = 133920769; to = 133924439; found = None; err = None
while b <= to and not found:
    e = min(b+199, to)
    r = rpc("eth_getLogs", [{"fromBlock": hex(b), "toBlock": hex(e), "address": ADDR, "topics": [TRANSFER, ZERO]}])
    if "error" in r:
        err = r["error"]; print(f"chunk {b}-{e} ERROR:", str(err)[:100]); break
    logs = r.get("result", [])
    if logs:
        found = logs[0]; print(f"first mint: block {int(found['blockNumber'],16)} tx {found['transactionHash'][:18]}")
        break
    b = e+1
if found:
    blk = int(found["blockNumber"], 16)
    r = rpc("eth_getBlockByNumber", [hex(blk), False])
    ts = int(r["result"]["timestamp"], 16) if r.get("result") else None
    wib = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB") if ts else None
    print("ALIEN first-mint block:", blk, "time:", wib)
elif err:
    print("ALIEN first-mint search FAILED (public RPC limit); age stays UNVERIFIED")
else:
    print("ALIEN: no mint in window 133920769-133924439 (first mint earlier than window start?)")
print("DONE")
