#!/usr/bin/env python3
import sys, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def topic(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()
SALE = "0x834e5BC43Aa91bEbEB31B97eaFA1bCb2F4286d97"
t0 = topic("Claimed(address,uint256,bool,uint256,uint256)")
print("Claimed topic:", t0)
logs = []
frm = 131200000
for ep in ["https://bsc-dataseed.binance.org/"]:
    try: head = int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
    except Exception: head = 131290500
print("head", head)
params = {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(head),
          "address": [SALE], "topics": [[t0]], "pageSize": 100}
try:
    body = ankr_post("ankr_getLogs", params, timeout=60)
    logs = body.get("logs", body) if isinstance(body, dict) else body
    print("logs type", type(logs), "count", len(logs) if hasattr(logs, "__len__") else logs)
    if isinstance(logs, list) and logs:
        first = min(logs, key=lambda l: int(l["blockNumber"], 16))
        print("earliest Claimed:", first["blockNumber"], int(first["blockNumber"], 16), first.get("transactionHash"))
        blk = int(first["blockNumber"], 16)
        for ep in ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]:
            try:
                b = _single(ep, "eth_getBlockByNumber", [hex(blk), False], 8, retries=0)
                import datetime
                ts = int(b["timestamp"], 16)
                print("block ts WIB:", datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat())
                break
            except Exception as e: print("block err", str(e)[:100])
        json.dump(logs, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-03-0131-hongbao-claimed.json", "w"), indent=1)
    else:
        print("RAW:", str(body)[:500])
except Exception as e:
    print("ERR", type(e).__name__, str(e)[:300])
