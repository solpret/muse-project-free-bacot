#!/usr/bin/env python3
"""First-mint search via public-RPC eth_getLogs (Transfer from zero) for ALIEN + PXIO. Read-only, bounded."""
import json, subprocess, time
EP = "https://bsc-dataseed.binance.org/"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
def rpc(method, params, timeout=30):
    payload = {"jsonrpc":"2.0","id":1,"method":method,"params":params}
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps(payload)], capture_output=True, text=True, timeout=timeout+10).stdout
    try: return json.loads(out)
    except Exception: return {"error": out[:120]}
def get_logs(addr, frm, to):
    r = rpc("eth_getLogs", [{"fromBlock": hex(frm), "toBlock": hex(to), "address": addr, "topics": [TRANSFER, ZERO]}])
    if "error" in r: return None, r["error"]
    return r.get("result", []), None
def block_ts(b):
    r = rpc("eth_getBlockByNumber", [hex(b), False])
    if r.get("result"): return int(r["result"]["timestamp"], 16)
    return None
import datetime
def fmt(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB") if ts else None
targets = [
    ("ALIEN", "0xE4D2c58A8F7b4E6d3c1A5f2B8d9C0e1F2a3B4c5D", None),  # placeholder fixed below
]
# real addresses from snapshot
snap = json.load(open("onchain-snapshot.json"))
addrs = {}
for k,v in snap.get("contracts", {}).items():
    if isinstance(v, dict) and v.get("address"):
        addrs[k.upper()] = v["address"]
print("ALIEN addr:", addrs.get("ALIEN"))
print("PXIO addr: 0x58e8f1b34B60687B36BCdc78e02a2fd443De71Ab")
jobs = [
    ("ALIEN", addrs.get("ALIEN"), 133920769, 133924439),
    ("PXIO", "0x58e8f1b34B60687B36BCdc78e02a2fd443De71Ab", 133925000, 133940166),
]
for name, addr, frm, to in jobs:
    if not addr:
        print(name, "NO ADDRESS"); continue
    first = None
    chunk = 1000
    b = frm
    err = None
    while b <= to:
        e = min(b+chunk-1, to)
        logs, err = get_logs(addr, b, e)
        if err:
            print(name, f"chunk {b}-{e} ERROR:", str(err)[:100]); break
        if logs:
            first = logs[0]
            print(name, f"first mint in window: block {int(first['blockNumber'],16)} tx {first['transactionHash'][:18]}...")
            break
        b = e+1
    if first:
        blk = int(first["blockNumber"], 16)
        ts = block_ts(blk)
        print(name, "first-mint block:", blk, "time:", fmt(ts), f"(ts {ts})")
    elif err:
        print(name, "first-mint search FAILED at chunk; age stays UNVERIFIED")
    else:
        print(name, "no mint in window", frm, "-", to, "(first mint outside window or window empty)")
print("DONE")
