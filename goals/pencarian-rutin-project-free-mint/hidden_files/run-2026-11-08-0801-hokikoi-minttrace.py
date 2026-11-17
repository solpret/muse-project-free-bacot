#!/usr/bin/env python3
import sys, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from ankr import ankr_post
from fast_rpc import batch
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
HK = "0x74055b4Afe2d8c7347e8D4c0fc23e704405F7A36"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
TO = "0x000000000000000000000000" + USER[2:].lower()
head = int(batch([("eth_blockNumber", [])], endpoint="https://bsc-dataseed1.bnbchain.org/", timeout=10)[0], 16)
print("head", head, flush=True)
# chunked: 132297000 -> head, 1000-block chunks; topic0 Transfer, topic2 = to user
out = []
fb = 132297000
while fb <= head:
    tb = min(fb + 999, head)
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(fb), "toBlock": hex(tb),
            "address": HK, "topics": [TRANSFER, None, TO]})
        logs = body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
        for l in logs:
            out.append({"block": int(l["blockNumber"], 16), "tx": l["transactionHash"],
                        "from": "0x"+l["topics"][1][-40:], "tokenId": int(l["topics"][3], 16)})
        print(f"chunk {fb}-{tb}: {len(logs)} logs", flush=True)
    except Exception as e:
        print(f"chunk {fb}-{tb} FAIL {e}", flush=True)
    fb = tb + 1
print(json.dumps({"head": head, "mints_to_user": out}, indent=1))
json.dump({"head": head, "mints_to_user": out}, open("run-2026-11-08-0801-hokikoi-minttrace.json", "w"), indent=1)
