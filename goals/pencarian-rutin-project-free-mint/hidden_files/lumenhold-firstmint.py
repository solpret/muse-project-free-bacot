#!/usr/bin/env python3
"""Find Lumenhold first Transfer-from-zero via Ankr getLogs (chunked, <1000/page)."""
import json, urllib.request
from Crypto.Hash import keccak
ADDR = "0x9701980b0afd825134390ee46fb3bd675a2f356f"
TRANSFER = "0x" + keccak.new(digest_bits=256, data=b"Transfer(address,address,uint256)").hexdigest()
ZERO = "0x" + "0"*64
def logs(frm, to):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                       "params": [{"fromBlock": hex(frm), "toBlock": hex(to), "address": ADDR,
                                   "topics": [TRANSFER, ZERO]}]}).encode()
    req = urllib.request.Request("https://rpc.ankr.com/bsc", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=25) as r:
        o = json.load(r)
    if "error" in o: return f"ERR {o['error']}"
    return o.get("result", [])
# scan from before first-seen (131559780) in 20k-block chunks up to 132101090
first = None; total = 0; chunks = []
b = 131540000
while b <= 132101090:
    e = min(b + 19999, 132101090)
    try:
        r = logs(b, e)
    except Exception as ex:
        r = f"ERR {ex}"
    if isinstance(r, str):
        chunks.append((b, e, r)); b = e + 1; continue
    chunks.append((b, e, len(r)))
    total += len(r)
    if r and first is None:
        first = int(r[0]["blockNumber"], 16)
        break
    b = e + 1
print(json.dumps({"first_mint_block_before_132101090": first, "mints_before_window": total if first else None, "chunks": chunks}, indent=1))
# timestamp of first mint block via dataseed
if first:
    import sys; sys.path.insert(0, "/home/hatch/workspace/fast_exec")
    from fast_rpc import _single as single
    for ep in ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]:
        try:
            r = single(ep, "eth_getBlockByNumber", [hex(first), False], 8, retries=0)
            if r and r.get("timestamp"):
                print("first_mint_ts:", int(r["timestamp"], 16)); break
        except Exception as ex:
            print("ts err", ep, ex)
