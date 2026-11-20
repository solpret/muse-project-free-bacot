#!/usr/bin/env python3
"""grove-watch check (read-only): freeOpen() + freeClaimed(user) on Agent Grove.

Calldata is built programmatically from function signatures via keccak
(eth_hash) — never hand-typed hex. Reads via fast_rpc.batch_race.
"""
import json
import sys
import time

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
from fast_rpc import batch_race

GROVE = "0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"


def selector(sig: str) -> str:
    return "0x" + keccak(sig.encode()).hex()[:8]


def main():
    t0 = time.time()
    free_open_data = selector("freeOpen()")
    claimed_data = selector("freeClaimed(address)") + USER[2:].lower().rjust(64, "0")
    calls = [("eth_call", [{"to": GROVE, "data": free_open_data}, "latest"]),
             ("eth_call", [{"to": GROVE, "data": claimed_data}, "latest"])]
    results = batch_race(calls)
    elapsed = time.time() - t0
    free_open = int(results[0], 16)
    claimed = int(results[1], 16)
    print(json.dumps({
        "freeOpen": free_open,
        "freeClaimed_user": bool(claimed),
        "freeClaimed_raw": results[1],
        "freeOpen_raw": results[0],
        "elapsed_s": round(elapsed, 2),
    }))


if __name__ == "__main__":
    main()
