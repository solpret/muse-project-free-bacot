#!/usr/bin/env python3
"""Run 85: retry the single failed contract from the run-84 window inbound retry.
Topic-filtered (Transfer/TransferSingle from zero -> tracked) + full-range fallback.
Read-only."""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
import ankr as ankr_mod
from Crypto.Hash import keccak
def topic(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()
T_TRANSFER = topic("Transfer(address,address,uint256)")
T_SINGLE = topic("TransferSingle(address,address,address,uint256,uint256)")
ZERO_PAD = "0x" + "0" * 64
HOME = Path.home()
tier = json.load(open(HOME / "workspace/narrative-pulse/tier-ab-watch-state.json"))
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903","0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc","0xda91cefe240175e6fab56271110427a4195ab71f"]
uniq = []
for w in list(tier["wallets"].keys()) + feed:
    if w.lower() not in uniq: uniq.append(w.lower())
tracked_padded = {"0x" + "0" * 24 + w[2:] for w in uniq}
C = "0x4b9b8fd6361a9e1baa0705fa77252f14dc54c10a"
FROM, TO = 132031247, 132041619
out = {"contract": C, "from": FROM, "to": TO, "verified": False, "hits": []}
for attempt in (1, 2, 3):
    try:
        data = ankr_mod.get_logs(C, FROM, TO, topics=[T_TRANSFER, ZERO_PAD, sorted(tracked_padded)])
        logs = ((data.get("result") or {}).get("logs") or [])
        print(f"attempt {attempt}: topic-filtered Transfer logs={len(logs)}", flush=True)
        out["topic_filtered_logs"] = len(logs)
        out["verified"] = True
        for lg in logs:
            t = lg.get("topics") or []
            if t and t[0] == T_TRANSFER and len(t) >= 3 and t[1] == ZERO_PAD and t[2] in tracked_padded:
                out["hits"].append({"tx": lg.get("transactionHash"), "block": lg.get("blockNumber")})
        break
    except Exception as e:
        print(f"attempt {attempt} ERROR {e}", flush=True)
        out.setdefault("errors", []).append(str(e)[:200])
        time.sleep(5)
if not out["verified"]:
    # full-range fallback (no topics) - may hit 1000 cap; only counts if it returns
    try:
        data = ankr_mod.get_logs(C, FROM, TO)
        logs = ((data.get("result") or {}).get("logs") or [])
        print(f"fallback full-range logs={len(logs)}", flush=True)
        out["full_range_logs"] = len(logs)
        out["verified"] = len(logs) < 1000
    except Exception as e:
        print("fallback ERROR", e, flush=True)
        out.setdefault("errors", []).append(str(e)[:200])
print("hits:", out["hits"], "verified:", out["verified"], flush=True)
json.dump(out, open("/home/hatch/workspace/narrative-pulse/scan-runs/run85-inbound84-4b9b-retry.json", "w"), indent=1)
print("saved run85-inbound84-4b9b-retry.json", flush=True)
