#!/usr/bin/env python3
"""Update snapshot after run 2026-11-01 ~20:01 WIB (HIVE Agents re-read)."""
import json
P = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(P))
h = snap["contracts"]["HIVE Agents"]
# Baseline 19:40 WIB: totalSupply 564. Fresh read 20:01 WIB (block 131053652): 571.
# Interval ~21 min, minted 7 -> rate ~0.33/min. No previous rate existed, so
# velocity does NOT pass (also 7 < 20 tokens in interval).
h["totalSupply"] = 571
h["previousTotalSupply"] = 564
h["mintedInInterval"] = 7
h["intervalMinutes"] = 21
h["currentRatePerMin"] = round(7 / 21, 2)
h["previousRatePerMin"] = None
h["velocityVerified"] = False
h["velocityNote"] = "First computable rate 20:01 WIB: 7 tokens / ~21 min = 0.33/min; does NOT pass increasing test (no prior rate, and 7 < 20 tokens in interval). Stored as baseline for next run."
h["freePctInference"] = 57.1
h["freePctNote"] = "Inference only: totalSupply 571 + totalPaid 0 -> 571/1000 FREE_SUPPLY = 57.1%; no freeClaimed view on contract."
h["lastReadBlock"] = 131053652
h["lastReadWib"] = "2026-11-01T20:01:00+07:00"
h["baselineNote"] = ("Deep-sweep lead; % is inference from totalSupply + totalPaid=0, not a freeClaimed view; "
    "START_TIME 2026-11-01 16:00 WIB; free slot open for user wallet; X unverified; velocity first rate recorded 20:01 WIB (0.33/min, NOT passing); "
    "already reported to main chat as watchlist lead 2026-11-01 ~19:36 WIB, do not re-report as new, only changes")
snap["timestamp_wib"] = "2026-11-01T20:01:00+07:00"
json.dump(snap, open(P, "w"), indent=1)
print(json.dumps(snap, indent=1))
