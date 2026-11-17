import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import race, _single
from ankr import ankr_post
ADDR = "0xa04513d85e02e1a1623a985269b3ebd46fa76b98"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
# totalSupply retry via single dataseed endpoint directly
for ep in ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]:
    try:
        r = _single(ep, "eth_call", [{"to": ADDR, "data": "0x18160ddd"}, "latest"], 10, retries=0)
        print("totalSupply via", ep, "=", r, int(r, 16) if r.startswith("0x") else r, flush=True)
        break
    except Exception as e:
        print("totalSupply ERR", ep, type(e).__name__, str(e)[:120], flush=True)
head_n = int(race("eth_blockNumber", [], timeout=10), 16)
print("head:", head_n, flush=True)
for window in (100000, 20000):
    try:
        params = {"blockchain": "bsc", "fromBlock": hex(head_n-window), "toBlock": hex(head_n),
                  "address": [ADDR], "topics": [TRANSFER, ZERO], "pageSize": 5, "descOrder": True}
        body = ankr_post("ankr_getLogs", params, timeout=30)
        logs = (body.get("result", {}) or {}).get("logs", []) or []
        print(f"mints last {window} blocks:", len(logs), [int(l['blockNumber'],16) for l in logs], flush=True)
    except Exception as e:
        print(f"window {window} ERR", type(e).__name__, str(e)[:200], flush=True)
print("DONE", flush=True)
