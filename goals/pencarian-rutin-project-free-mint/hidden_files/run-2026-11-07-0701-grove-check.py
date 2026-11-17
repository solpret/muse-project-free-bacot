#!/usr/bin/env python3
"""Grove watch run 2026-11-07 07:01 WIB — read-only: freeOpen() + freeClaimed(user)."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import call_many, race

GROVE = "0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
t0 = time.time()
calls = [
    (GROVE, "0x71f195b9"),  # freeOpen()
    (GROVE, "0x61c0b6a0" + USER[2:].lower().rjust(64, "0")),  # freeClaimed(user)
]
res = call_many(calls)
block = race("eth_blockNumber", [])
elapsed = time.time() - t0
out = {
    "block": int(block, 16) if block else None,
    "freeOpen": int(res[0], 16) if res and res[0] else None,
    "freeClaimed_user": (int(res[1], 16) != 0) if res and len(res) > 1 and res[1] else None,
    "raw": res,
    "elapsed_s": round(elapsed, 2),
}
print(json.dumps(out, indent=1))
with open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-07-0701-grove-check.json", "w") as f:
    json.dump(out, f, indent=1)
