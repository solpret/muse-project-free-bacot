#!/usr/bin/env python3
"""Fresh on-chain verification for BNB Chick free mint (user order 2026-11-06 ~14:40 WIB).
Reads free pool, user slot, supply, balance + latest block for age check.
Writes chick-verify-20261106.json in the same dir. Read-only."""
import json
import os
import sys
import time

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

BASE = os.path.dirname(os.path.abspath(__file__))
SALE = "0xA9481429169C883c7FD5f5EAdFD08737ad688337"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = [
    "https://bsc-dataseed1.defibit.io/",
    "https://bsc.publicnode.com/",
    "https://bsc-dataseed1.bnbchain.org/",
    "https://bsc-dataseed2.defibit.io/",
    "https://bsc-dataseed1.ninicoin.io/",
]
FIRST_MINT_BLOCK = 131933567
FIRST_MINT_TS = 1793934260  # 2026-11-06 10:04:20 WIB


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


def call(data):
    return rpc("eth_call", [{"to": SALE, "data": data}, "latest"])


def u256(v):
    if isinstance(v, str) and v.startswith("0x"):
        try:
            return int(v, 16)
        except Exception:
            return v
    return v


def addr_arg(a: str) -> str:
    return "00" * 12 + a[2:].lower()


def main():
    out = {"sale": SALE, "user": USER, "checked_wib": time.strftime("%Y-%m-%d %H:%M:%S")}
    views = [
        ("freeSharesRemaining", sel("freeSharesRemaining()"), "uint"),
        ("freeSharesClaimed", sel("freeSharesClaimed()"), "uint"),
        ("freeShareClaimedBy(user)", sel("freeShareClaimedBy(address)") + addr_arg(USER), "bool"),
        ("sharesMintedBy(user)", sel("sharesMintedBy(address)") + addr_arg(USER), "uint"),
        ("paidSharesRemaining", sel("paidSharesRemaining()"), "uint"),
        ("paidSharesSold", sel("paidSharesSold()"), "uint"),
        ("totalSupply", sel("totalSupply()"), "uint"),
        ("balanceOf(user)", sel("balanceOf(address)") + addr_arg(USER), "uint"),
        ("SHARE_PRICE", sel("SHARE_PRICE()"), "uint"),
        ("TOKENS_PER_SHARE", sel("TOKENS_PER_SHARE()"), "uint"),
    ]
    for name, data, kind in views:
        raw = call(data)
        if isinstance(raw, str) and raw.startswith("ERROR"):
            out[name] = raw
            continue
        v = u256(raw)
        out[name] = bool(v) if kind == "bool" and isinstance(v, int) else v
    blk = rpc("eth_blockNumber", [])
    out["latest_block"] = u256(blk) if isinstance(blk, str) else blk
    if isinstance(out["latest_block"], int):
        b = rpc("eth_getBlockByNumber", [hex(out["latest_block"]), False])
        if isinstance(b, dict):
            ts = int(b.get("timestamp", "0x0"), 16)
            out["latest_block_ts"] = ts
            out["age_hours_since_first_mint"] = round((ts - FIRST_MINT_TS) / 3600, 2)
            out["first_mint_block"] = FIRST_MINT_BLOCK
            out["first_mint_wib"] = "2026-11-06 10:04:20 WIB"
    with open(os.path.join(BASE, "chick-verify-20261106.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
