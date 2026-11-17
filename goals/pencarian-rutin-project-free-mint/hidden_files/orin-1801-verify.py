"""Orin Agent 0xa04513d85e02e1a1623a985269b3ebd46fa76b98 — read-only verify (leg 2, run 1801)."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post

ADDR = "0xa04513d85e02e1a1623a985269b3ebd46fa76b98"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]

def rpc_call(method, params, timeout=8):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:
            last = e
    raise last

out = {}
for name, sel in [('totalSupply()', '0x18160ddd'), ('name()', '0x06fdde03'), ('symbol()', '0x95d89b41')]:
    try:
        r = rpc_call("eth_call", [{"to": ADDR, "data": sel}, "latest"])
        out[name] = r
    except Exception as e:
        out[name] = f"ERR {e}"
print("CALLS:", json.dumps(out, indent=1))
head_n = int(rpc_call("eth_blockNumber", []), 16)
print("head:", head_n)

found = None
end = head_n
tries = 0
while end > head_n - 200000 and tries < 200:
    start = end - 1000 + 1
    params = {"blockchain": "bsc", "fromBlock": hex(start), "toBlock": hex(end),
              "address": [ADDR], "topics": [TRANSFER, ZERO], "pageSize": 1, "descOrder": False}
    try:
        body = ankr_post("ankr_getLogs", params, timeout=30)
        logs = body.get("result", {}).get("logs", []) or []
    except Exception as e:
        print("ankr err", start, end, e); break
    if logs:
        found = logs[0]
        print("FIRST MINT LOG chunk", start, end, "block", int(found["blockNumber"], 16), "tx", found.get("transactionHash"))
        break
    end = start - 1
    tries += 1
if found:
    blk = int(found["blockNumber"], 16)
    b = rpc_call("eth_getBlockByNumber", [hex(blk), False])
    print("first mint block:", blk, "timestamp:", int(b["timestamp"], 16))
else:
    print("NO first-mint log found in last 200k blocks")
json.dump({"calls": out, "head": head_n, "first_mint": found}, open("orin-1801-verify.json", "w"), indent=1)
