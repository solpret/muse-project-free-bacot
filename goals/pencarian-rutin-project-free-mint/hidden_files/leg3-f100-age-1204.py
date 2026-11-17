#!/usr/bin/env python3
"""Launch-age check for Pathwyrm 0xf100c608... via Ankr eth_getLogs: first Transfer from zero (mint) + Launched event. Read-only."""
import json, urllib.request, time
from datetime import datetime, timezone

ADDR = "0xf100c608913dC07ed268bEA865Fca10004f04657"
ANKR = "https://rpc.ankr.com/bsc"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
LAUNCHED = "0x"  # compute below
from Crypto.Hash import keccak
k = keccak.new(digest_bits=256); k.update(b"Launched()"); LAUNCHED = "0x" + k.hexdigest()
ZERO_PAD = "0x" + "0"*64

def rpc(method, params, timeout=20, url=None):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(url or ANKR, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        o = json.load(r)
    if "error" in o:
        raise RuntimeError(o["error"])
    return o.get("result")

# current block
blk = int(rpc("eth_blockNumber", [], url="https://bsc-dataseed.binance.org/"), 16)
print("head block:", blk)
# search window: last 60k blocks (~50h)
from_block = blk - 20000
params = [{"fromBlock": hex(from_block), "toBlock": "latest", "address": ADDR,
           "topics": [TRANSFER, ZERO_PAD]}]
logs = rpc("eth_getLogs", params)
print("mint Transfer logs in window:", len(logs) if logs else 0)
if logs:
    first = min(logs, key=lambda l: int(l["blockNumber"], 16))
    fb = int(first["blockNumber"], 16)
    print("first mint block:", fb, "tx:", first["transactionHash"])
    b = rpc("eth_getBlockByNumber", [hex(fb), False])
    ts = int(b["timestamp"], 16)
    dt = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(timezone.utc)
    print("first mint time UTC:", dt.isoformat(), "| WIB:", datetime.fromtimestamp(ts, tz=__import__("zoneinfo").ZoneInfo("Asia/Jakarta")).isoformat())
    print("age hours:", round((time.time() - ts) / 3600, 2))
    print("first mint tokenId:", int(first["topics"][3], 16))
else:
    print("NO mint in last 60k blocks - launch age NOT verified in this window")
# Launched events
params2 = [{"fromBlock": hex(from_block), "toBlock": "latest", "address": ADDR, "topics": [LAUNCHED]}]
logs2 = rpc("eth_getLogs", params2)
print("Launched events:", len(logs2) if logs2 else 0)
if logs2:
    fb2 = int(logs2[0]["blockNumber"], 16)
    b2 = rpc("eth_getBlockByNumber", [hex(fb2), False])
    ts2 = int(b2["timestamp"], 16)
    print("first Launched block:", fb2, "time WIB:", datetime.fromtimestamp(ts2, tz=__import__("zoneinfo").ZoneInfo("Asia/Jakarta")).isoformat())
