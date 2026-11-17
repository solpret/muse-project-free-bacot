#!/usr/bin/env python3
"""Orchidia first-mint probe: Transfer-from-zero logs, 5000-block windows walking back."""
import json, urllib.request, datetime
from Crypto.Hash import keccak
ADDR = "0x09bcdd97186f6f37521bd1b281d329e48ac54b89"
RPCS = ["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
topic0 = "0x" + keccak.new(digest_bits=256, data=b"Transfer(address,address,uint256)").hexdigest()
zero = "0x0000000000000000000000000000000000000000000000000000000000000000"
def rpc(method, params, timeout=10):
    for r in RPCS:
        try:
            body = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
            req = urllib.request.Request(r, data=body, headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as resp: out = json.load(resp)
            if "error" in out: continue
            return out["result"]
        except Exception: continue
    return None
_b = rpc("eth_blockNumber", [])
blk = int(_b, 16) if _b else 132078747
print("current block", blk)
W = 5000
found = None
for start in range(blk, blk - 100000, -W):
    lo, hi = start - W + 1, start
    logs = rpc("eth_getLogs", [{"fromBlock": hex(lo), "toBlock": hex(hi), "address": ADDR,
                                "topics": [topic0, zero]}])
    if logs is None:
        print(f"window {lo}-{hi}: RPC fail"); continue
    print(f"window {lo}-{hi}: {len(logs)} mint logs")
    if logs:
        found = logs[0]; break
if found:
    fb = int(found["blockNumber"], 16)
    print("earliest mint in window block:", fb, "tx:", found["transactionHash"])
    b = rpc("eth_getBlockByNumber", [hex(fb), False])
    if b:
        ts = int(b["timestamp"], 16)
        print("first mint time WIB:", datetime.datetime.utcfromtimestamp(ts + 7*3600).isoformat())
        print("age hours:", (blk - fb) * 3 / 3600)
else:
    print("no mint logs in last 100k blocks")
print("DONE")
