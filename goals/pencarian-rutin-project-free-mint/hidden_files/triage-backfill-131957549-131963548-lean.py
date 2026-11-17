#!/usr/bin/env python3
"""Lean verify for backfill 131957549-131963548 first-seen (read-only).
Adapted from triage-backfill-131939549-131945548-lean.py.
Fields: name/symbol/registry/PRICE/MAX_SUPPLY/minted/spotsLeft/
OWNER/owner/quote(1) + ABI fn list via curl (spots free views).
"""
import json
import subprocess
import sys
import datetime
from eth_hash.auto import keccak

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
EPS = ["https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed3.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY_EXPECTED = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"


def rpc(method, params, timeout=8):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:  # noqa: BLE001
            last = e
    raise last


def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]


def call(addr, data, timeout=8):
    return rpc("eth_call", [{"to": addr, "data": data}, "latest"], timeout)


def u256(h):
    if not isinstance(h, str) or not h.startswith("0x") or len(h) < 66:
        return None
    return int(h[-64:], 16)


def addr_of(h):
    if not isinstance(h, str) or not h.startswith("0x") or len(h) < 66:
        return None
    return "0x" + h[-40:]


def dec_str(h):
    if not isinstance(h, str) or not h.startswith("0x"):
        return None
    raw = bytes.fromhex(h[2:])
    if len(raw) >= 64:
        try:
            ln = int.from_bytes(raw[32:64], "big")
            if 0 < ln <= len(raw) - 64:
                return raw[64:64 + ln].decode("utf-8", "replace")
        except Exception:
            pass
    if len(raw) == 32:
        return raw.rstrip(b"\x00").decode("utf-8", "replace") or None
    return None


def enc_u256(n):
    return "0x" + format(n, "064x")


TARGETS = [
    ("0x50A994E71615474b55559fF4F500928fbc339DD9", 131960796),
    ("0x5bc200922C2fb96a3a83F4298E952707058ce638", 131960182),
    ("0x35207983355C90A259E8261b7b41F998C6A8f424", 131960239),
    ("0x92f415aB3a243f992429db3e568A8C6C341FDD83", 131961416),
]

FIELDS = [
    ("name", "name()", dec_str),
    ("symbol", "symbol()", dec_str),
    ("AGENT_REGISTRY", "AGENT_REGISTRY()", addr_of),
    ("PRICE", "PRICE()", u256),
    ("MAX_SUPPLY", "MAX_SUPPLY()", u256),
    ("minted", "minted()", u256),
    ("spotsLeft", "spotsLeft()", u256),
    ("AGENT_ID_REGISTRY", "AGENT_ID_REGISTRY()", addr_of),
    ("OWNER", "OWNER()", addr_of),
    ("owner", "owner()", addr_of),
]


def main():
    discards = json.load(open(f"{BASE}/same-owner-discards.json"))
    d_owners = {r.get("owner", "").lower() for r in discards if isinstance(r, dict)}
    out = {}
    for addr, fblk in TARGETS:
        r = {"first_block": fblk}
        try:
            blk = rpc("eth_getBlockByNumber", [hex(fblk), False], timeout=8)
            ts = int(blk["timestamp"], 16)
            r["first_block_ts"] = ts
            r["first_block_wib"] = datetime.datetime.fromtimestamp(
                ts, datetime.timezone(datetime.timedelta(hours=7))
            ).strftime("%Y-%m-%d %H:%M:%S WIB")
        except Exception as e:  # noqa: BLE001
            r["first_block_ts_error"] = str(e)
        print(f"\n== {addr} first={r.get('first_block_wib')}", flush=True)
        for name, sig, dec in FIELDS:
            try:
                v = dec(call(addr, sel(sig)))
                r[name] = v
                print(f"  {name}: {v}", flush=True)
            except Exception as e:  # noqa: BLE001
                r[name + "_error"] = str(e)
                print(f"  {name}: ERROR {e}", flush=True)
        try:
            q = u256(call(addr, sel("quote(uint256)") + enc_u256(1)[2:]))
            r["quote_1"] = q
            print(f"  quote(1): {q} wei = {q / 1e18 if q is not None else None} BNB", flush=True)
        except Exception as e:  # noqa: BLE001
            r["quote_error"] = str(e)
            print(f"  quote(1): ERROR {e}", flush=True)
        try:
            p = subprocess.run(
                ["curl", "-s", "-m", "20", "-A", "Mozilla/5.0",
                 f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                capture_output=True, text=True, timeout=30)
            d = json.loads(p.stdout)
            abi = d.get("abi")
            if isinstance(abi, list):
                fns = sorted({it.get("name", "") for it in abi if it.get("type") == "function"})
                r["sourcify"] = "verified"
                r["abi_functions"] = fns
                print(f"  sourcify: verified, {len(fns)} fns: {fns}", flush=True)
            else:
                r["sourcify"] = "no-abi"
                print("  sourcify: no-abi", flush=True)
        except Exception as e:  # noqa: BLE001
            r["sourcify"] = f"error:{type(e).__name__}"
            print(f"  sourcify: ERROR {e}", flush=True)
        owner = (r.get("OWNER") or r.get("owner") or "").lower()
        r["owner_in_discards"] = owner in d_owners if owner else None
        r["registry_match"] = (r.get("AGENT_REGISTRY") or "").lower() == REGISTRY_EXPECTED.lower()
        print(f"  owner in discards: {r['owner_in_discards']}; registry match: {r['registry_match']}", flush=True)
        out[addr] = r
    json.dump(out, open(f"{BASE}/triage-backfill-131957549-131963548-lean.json", "w"), indent=1)
    print("\nsaved triage-backfill-131957549-131963548-lean.json", flush=True)


if __name__ == "__main__":
    main()
