import sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import race
from ankr import ankr_post
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
head_n = int(race("eth_blockNumber", [], timeout=10), 16)
print("head:", head_n, flush=True)
for name, addr in [("NeoGods", "0x2746bb6c6ec8fc968b8f0159618af1bb30ab593d"),
                   ("Orin", "0xa04513d85e02e1a1623a985269b3ebd46fa76b98")]:
    try:
        params = {"blockchain": "bsc", "fromBlock": hex(head_n-20000), "toBlock": hex(head_n),
                  "address": [addr], "topics": [TRANSFER, ZERO], "pageSize": 5, "descOrder": True}
        body = ankr_post("ankr_getLogs", params, timeout=30)
        logs = (body.get("result", {}) or {}).get("logs", []) or []
        print(name, "mints last 20000 blocks:", len(logs), [int(l['blockNumber'],16) for l in logs], flush=True)
    except Exception as e:
        print(name, "ERR", type(e).__name__, str(e)[:200], flush=True)
print("DONE", flush=True)
