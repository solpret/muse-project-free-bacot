#!/usr/bin/env python3
"""Agent Grove fase 2 watch — run 2026-11-07 21:31 WIB. Read-only.

Reads freeOpen() + freeClaimed(user) via fast_rpc (batched eth_call).
Selectors computed with keccak at runtime — no hand-typed calldata.
"""
import json
import sys
import time

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from Crypto.Hash import keccak  # noqa: E402
from fast_rpc import call_many, race  # noqa: E402

GROVE = "0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"


def sel(sig):
    k = keccak.new(digest_bits=256)
    k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]


def enc(addr):
    return addr[2:].lower().rjust(64, "0")


t0 = time.time()
block_hex = race("eth_blockNumber", [])
block = int(block_hex, 16)
free_open_hex, free_claimed_hex = call_many([
    (GROVE, sel("freeOpen()")),
    (GROVE, sel("freeClaimed(address)") + enc(USER)),
])
out = {
    "block": block,
    "freeOpen": int(free_open_hex, 16),
    "freeClaimed_user": bool(int(free_claimed_hex, 16)),
    "elapsed_s": round(time.time() - t0, 2),
}
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-07-2131-grove-check.json", "w"), indent=1)
