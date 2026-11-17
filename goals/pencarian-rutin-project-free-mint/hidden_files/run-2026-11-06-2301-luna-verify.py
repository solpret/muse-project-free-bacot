#!/usr/bin/env python3
"""Run 2301: Luna Phase Agents (0x5c04392641c81F1b69826E13d8f3F78c58464970) targeted verification.
Read-only eth_calls via fast_rpc race (multi-endpoint, retries). None = read failed, NOT zero."""
import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from Crypto.Hash import keccak
from fast_rpc import call_many, race
CA = "0x5c04392641c81F1b69826E13d8f3F78c58464970"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
calls = [
    ("totalSupply", sel("totalSupply()")),
    ("totalMinted", sel("totalMinted()")),
    ("freeMinted", sel("freeMinted()")),
    ("freeClaimed", sel("freeClaimed()")),
    ("FREE_SUPPLY", sel("FREE_SUPPLY()")),
    ("MAX_SUPPLY", sel("MAX_SUPPLY()")),
    ("freeRemaining", sel("freeRemaining()")),
    ("freeOpen", sel("freeOpen()")),
    ("mintOpen", sel("mintOpen()")),
    ("freeMintedCount", sel("freeMintedCount()")),
    ("paidMinted", sel("paidMinted()")),
    ("quote_user_1", sel("quote(address,uint256)") + enc(USER) + enc_uint(1)),
    ("quoteMint_user_1", sel("quoteMint(address,uint256)") + enc(USER) + enc_uint(1)),
    ("mintedBy_user", sel("mintedBy(address)") + enc(USER)),
    ("mintedCount_user", sel("mintedCount(address)") + enc(USER)),
    ("freeUsed_user", sel("freeUsed(address)") + enc(USER)),
    ("canFreeMint_user", sel("canFreeMint(address)") + enc(USER)),
    ("claimedFree_user", sel("claimedFree(address)") + enc(USER)),
    ("balanceOf_user", sel("balanceOf(address)") + enc(USER)),
]
t0 = time.time()
try:
    blk = race("eth_blockNumber", [])
    block = int(blk, 16)
except Exception as e:
    block = None
    print("block FAIL", e, flush=True)
vals = {}
try:
    res = call_many([(CA, data) for _, data in calls])
    for (name, _), v in zip(calls, res):
        try: vals[name] = int(v, 16) if isinstance(v, str) and v.startswith("0x") else v
        except Exception: vals[name] = v
except Exception as e:
    print("call_many FAIL", e, flush=True)
    vals = {name: None for name, _ in calls}
# block timestamp for first-mint block 132037074 (age verification)
ts = None
try:
    b = race("eth_getBlockByNumber", [hex(132037074), False])
    ts = int(b.get("timestamp", "0x0"), 16) if isinstance(b, dict) else None
except Exception as e:
    print("block ts FAIL", e, flush=True)
out = {"block": block, "reads": vals, "firstMintBlock": 132037074, "firstMintTimestamp": ts, "elapsed_s": round(time.time()-t0, 1)}
print(json.dumps(out, indent=1), flush=True)
json.dump(out, open("run-2026-11-06-2301-luna-verify.json", "w"), indent=1)
