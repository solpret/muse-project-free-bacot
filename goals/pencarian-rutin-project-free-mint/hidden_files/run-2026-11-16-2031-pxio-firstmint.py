#!/usr/bin/env python3
"""Binary-search first block with totalSupply>0 for PXIO, then block timestamp. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
ADDR = "0x58e8f1b34B60687B36BCdc78e02a2fd443De71Ab"
EP = "https://bsc-dataseed.binance.org/"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
DATA = sel("totalSupply()")
def rpc(method, params):
    payload = {"jsonrpc":"2.0","id":1,"method":method,"params":params}
    out = subprocess.run(["curl","-sL","--max-time","30","-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps(payload)], capture_output=True, text=True, timeout=40).stdout
    return json.loads(out).get("result")
head = int(rpc("eth_blockNumber", []), 16)
print("head:", head, flush=True)
def ts_at(b):
    r = rpc("eth_call", [{"to":ADDR,"data":DATA}, hex(b)])
    if r is None: return None
    return int(r,16)
lo = head - 200000  # ~25h back
hi = head
print("totalSupply at lo:", ts_at(lo), "at head:", ts_at(hi), flush=True)
# binary search first block with supply>0
while hi - lo > 1:
    mid = (lo+hi)//2
    v = ts_at(mid)
    if v is None:
        print("read fail at", mid); break
    if v > 0: hi = mid
    else: lo = mid
print("first block supply>0:", hi, "supply:", ts_at(hi), flush=True)
blk = rpc("eth_getBlockByNumber", [hex(hi), False])
print("block ts:", int(blk["timestamp"],16), "UTC:", __import__('datetime').datetime.fromtimestamp(int(blk["timestamp"],16), __import__('datetime').timezone.utc).isoformat())
print("DONE")
