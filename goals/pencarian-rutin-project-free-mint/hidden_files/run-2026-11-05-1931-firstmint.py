import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00"*32
addr = sys.argv[1].lower()
hi = int(sys.argv[2])   # search backwards from hi
out = {"address": addr, "logs": [], "errors": [], "ankr_calls": 0}
b = hi
while b > hi - 40000:
    lo = max(b - 1999, hi - 40000)
    try:
        r = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(lo), "toBlock": hex(b),
            "address": addr, "topics": [TRANSFER, ZERO_TOPIC]})
        out["ankr_calls"] += 1
        logs = r.get("result", {}).get("logs", []) if isinstance(r, dict) else []
        print(f"chunk {lo}-{b}: {len(logs)} mint logs")
        out["logs"].extend(logs)
        if not logs and b < hi:
            # empty chunk below the top: keep going a bit to be sure? stop after 2 consecutive empties
            pass
    except Exception as ex:
        out["errors"].append(str(ex)); print("ERR", lo, ex)
    b = lo - 1
    time.sleep(0.3)
    # stop once we've found logs and the earliest chunk is empty (first mint found)
    if out["logs"] and lo <= int(out["logs"][0]["blockNumber"], 16):
        pass
# sort by block
out["logs"].sort(key=lambda l: (int(l["blockNumber"], 16), int(l["logIndex"], 16)))
mints = out["logs"]
out["mint_count"] = len(mints)
out["distinct_minters"] = len({l["topics"][2].lower() for l in mints}) if mints else 0
if mints:
    out["first_mint_block"] = int(mints[0]["blockNumber"], 16)
    out["first_mint_tx"] = mints[0]["transactionHash"]
    out["first_mint_timestamp"] = int(mints[0]["timestamp"], 16)
    out["last_mint_block"] = int(mints[-1]["blockNumber"], 16)
with open(sys.argv[3], "w") as f:
    json.dump(out, f, indent=1)
print("mint_count:", out["mint_count"], "distinct:", out["distinct_minters"], "first block:", out.get("first_mint_block"), "first ts:", out.get("first_mint_timestamp"))
