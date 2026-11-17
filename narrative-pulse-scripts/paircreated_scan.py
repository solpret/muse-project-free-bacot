#!/usr/bin/env python3
"""Pioneer scan: recent PancakeSwap V2 PairCreated events via Ankr getLogs (read-only).
Decodes token0 (topic1), token1 (topic2), pair (data word 0).
State: ~/workspace/narrative-pulse/paircreated_state.json (seen pair addresses).
Usage: paircreated_scan.py [lookback_blocks]  (default 5000, ~4h)
Prints JSON: {latest_block, new_pairs: [{pair, token0, token1, block, tx}]}.
WBNB pairs are the memecoin-relevant subset; non-WBNB pairs are listed too."""
import json, os, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import race
from ankr import get_logs  # module call: CLI truncates output at 4000 chars
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c"
STATE = "/home/hatch/workspace/narrative-pulse/paircreated_state.json"

def main():
    lookback = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    latest = int(race("eth_blockNumber", []), 16)
    frm = max(0, latest - lookback)
    data = get_logs(FACTORY, frm, latest)
    seen = set()
    if os.path.exists(STATE):
        seen = set(json.load(open(STATE)).get("pairs", []))
    new = []
    for log in (data.get("result") or {}).get("logs", []):
        topics = log.get("topics", [])
        if len(topics) < 3:
            continue
        token0 = "0x" + topics[1][-40:]
        token1 = "0x" + topics[2][-40:]
        pair = "0x" + (log.get("data", "")[2:66])[-40:]
        if pair not in seen:
            seen.add(pair)
            new.append({"pair": pair, "token0": token0, "token1": token1,
                        "wbnb_pair": token0.lower() == WBNB or token1.lower() == WBNB,
                        "block": int(log.get("blockNumber", "0x0"), 16),
                        "tx": log.get("transactionHash")})
    json.dump({"pairs": sorted(seen), "latest_block": latest}, open(STATE, "w"), indent=1)
    print(json.dumps({"latest_block": latest, "from_block": frm,
                      "new_pairs": new, "new_wbnb_pairs": sum(1 for p in new if p["wbnb_pair"])}, indent=1))

if __name__ == "__main__":
    main()
