#!/usr/bin/env python3
"""Deep-verify MOLT AGENT 0x4B8150f1a258cD3CE2300fAf682432c52ca48Fc1 (backfill run 132082252-132084331).
READ-ONLY eth_call / eth_getCode / eth_getBlockByNumber. Writes only its own JSON.
"""
import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single

try:
    from Crypto.Hash import keccak

    def _keccak(b: bytes) -> bytes:
        k = keccak.new(digest_bits=256)
        k.update(b)
        return k.digest()
except Exception:
    from eth_hash.auto import keccak as _keccak  # type: ignore

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x4B8150f1a258cD3CE2300fAf682432c52ca48Fc1"
EPS = ["https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed3.bnbchain.org/"]
WIB = timezone(timedelta(hours=7))


def sel(sig: str) -> str:
    return "0x" + _keccak(sig.encode()).hex()[:8]


def rpc(method, params, timeout=10):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:  # noqa: BLE001
            last = e
    return f"ERROR:{last}"


def call(addr, data, block="latest"):
    r = rpc("eth_call", [{"to": addr, "data": data}, block])
    if isinstance(r, str) and r.startswith("0x") and len(r) > 2:
        return r
    return None


def u256(v):
    if isinstance(v, str) and v.startswith("0x"):
        try:
            return int(v, 16)
        except Exception:
            return None
    return None


def addr_arg(a: str) -> str:
    return "00" * 12 + a[2:].lower()


def wib(ts):
    return datetime.fromtimestamp(ts, WIB).strftime("%Y-%m-%d %H:%M:%S")


out = {"address": ADDR, "checked_wib": datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S")}

# seen first_block
seen = json.load(open(os.path.join(BASE, "onchain-scan-seen.json")))
out["seen_first_block"] = seen.get("contracts", {}).get(ADDR)

# code existence around first mint: block before first seen block
for blk in (132084230, 132084231, 132084287):
    code = rpc("eth_getCode", [ADDR, hex(blk)])
    out[f"code_len_at_{blk}"] = len(code) - 2 if isinstance(code, str) else f"ERROR:{code}"

# counters
for fn in ["totalMinted", "freeMinted", "paidMinted", "freeAllocation",
           "freeRemaining", "paidRemaining", "maxSupply", "mintPrice",
           "maxFreePerWallet", "maxPaidPerWallet", "rewardPerMint"]:
    out[fn] = u256(call(ADDR, sel(f"{fn}()")))
out["mintOpen"] = call(ADDR, sel("mintOpen()"))
out["agentId"] = call(ADDR, sel("agentId()"))
out["canClaimFree_user"] = call(ADDR, sel("canClaimFree(address)") + addr_arg(USER))
out["hasAgentId_user"] = call(ADDR, sel("hasAgentId(address)") + addr_arg(USER))
out["freeMintedBy_user"] = u256(call(ADDR, sel("freeMintedBy(address)") + addr_arg(USER)))
out["paidMintedBy_user"] = u256(call(ADDR, sel("paidMintedBy(address)") + addr_arg(USER)))
out["balanceOf_user"] = u256(call(ADDR, sel("balanceOf(address)") + addr_arg(USER)))
out["moltaToken"] = call(ADDR, sel("moltaToken()"))
out["molta"] = call(ADDR, sel("molta()"))
out["renderer"] = call(ADDR, sel("renderer()"))
# walletInfo(user) raw
out["walletInfo_user_raw"] = call(ADDR, sel("walletInfo(address)") + addr_arg(USER))
# owner
r = call(ADDR, sel("owner()"))
out["owner"] = ("0x" + r[-40:]) if isinstance(r, str) and len(r) >= 42 else r
# agentRegistry() raw (expect revert / empty since not in ABI)
out["agentRegistry_raw"] = call(ADDR, sel("agentRegistry()"))
# first-mint block timestamp
for blk in (132084231, 132084287):
    b = rpc("eth_getBlockByNumber", [hex(blk), False])
    ts = u256(b.get("timestamp")) if isinstance(b, dict) else None
    out[f"block_{blk}_ts"] = ts
    out[f"block_{blk}_wib"] = wib(ts) if ts else None
out["age_hours_now"] = round((time.time() - 1794002092) / 3600, 2) if out.get("block_132084231_ts") else None

with open(os.path.join(BASE, "backfill-triage-132082252-132084331-molt-verify.json"), "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out, indent=1))
