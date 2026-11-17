#!/usr/bin/env python3
"""Agent Grove fase 2 watch — run 2026-11-09 01:01 WIB. Read-only.

Reads freeOpen() + freeClaimed(user) via fast_rpc (batched eth_call),
with direct-curl fallback to bsc-dataseed.binance.org if fast_rpc fails
(quirk seen 22:31 run: fast_rpc TimeoutError, direct curl succeeded).
Selectors computed with keccak at runtime — no hand-typed calldata.
"""
import json
import subprocess
import sys
import time

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from Crypto.Hash import keccak  # noqa: E402

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
GROVE = "0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPC = "https://bsc-dataseed.binance.org"


def sel(sig):
    k = keccak.new(digest_bits=256)
    k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]


def enc(addr):
    return addr[2:].lower().rjust(64, "0")


def curl_call(method, params):
    payload = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1})
    r = subprocess.run(
        ["curl", "-s", "-m", "20", "-X", "POST", RPC,
         "-H", "Content-Type: application/json", "-d", payload],
        capture_output=True, text=True, timeout=30,
    )
    data = json.loads(r.stdout)
    if "error" in data:
        raise RuntimeError(data["error"])
    return data["result"]


def curl_eth_call(data_hex):
    return curl_call("eth_call", [{"to": GROVE, "data": data_hex}, "latest"])


t0 = time.time()
method_used = "fast_rpc"
try:
    from fast_rpc import call_many, race  # noqa: E402
    block_hex = race("eth_blockNumber", [])
    block = int(block_hex, 16)
    free_open_hex, free_claimed_hex = call_many([
        (GROVE, sel("freeOpen()")),
        (GROVE, sel("freeClaimed(address)") + enc(USER)),
    ])
except Exception as e:
    method_used = f"curl-fallback ({type(e).__name__}: {e})"
    block = int(curl_call("eth_blockNumber", []), 16)
    free_open_hex = curl_eth_call(sel("freeOpen()"))
    free_claimed_hex = curl_eth_call(sel("freeClaimed(address)") + enc(USER))

out = {
    "block": block,
    "freeOpen": int(free_open_hex, 16),
    "freeClaimed_user": bool(int(free_claimed_hex, 16)),
    "elapsed_s": round(time.time() - t0, 2),
    "method": method_used,
}
print(json.dumps(out, indent=1))
json.dump(out, open(f"{BASE}/run-2026-11-09-0101-grove-check.json", "w"), indent=1)
