#!/usr/bin/env python3
"""Lean triage run 1331 first-seen (read-only). Fields: name/symbol/registry
views/PRICE/MAX_SUPPLY/totalSupply/totalMinted/free views/owner/quote(1) +
first-block timestamp + Sourcify ABI fn list."""
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
        except Exception as e:
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


def enc_addr(a):
    return "0x" + "00" * 12 + a[2:].lower()


def enc_u256(n):
    return "0x" + format(n, "064x")


TARGETS = [
    ("0xB8740E3Ab25fE0ea7e4d48106519EeadB35721b1", 132347079, 66, 5),
    ("0xC92bEc9160506065E515b225721a749Fad7664E9", 132346345, 16, 16),
    ("0x7Af71d3B2B3df7A7E9B13CaDB96003B967b7499B", 132347220, 1, 1),
]

FIELDS = [
    ("name", "name()", dec_str),
    ("symbol", "symbol()", dec_str),
    ("AGENT_REGISTRY", "AGENT_REGISTRY()", addr_of),
    ("AGENT_ID_REGISTRY", "AGENT_ID_REGISTRY()", addr_of),
    ("agentRegistry", "agentRegistry()", addr_of),
    ("PRICE", "PRICE()", u256),
    ("MAX_SUPPLY", "MAX_SUPPLY()", u256),
    ("FREE_SUPPLY", "FREE_SUPPLY()", u256),
    ("FREE_SLOTS", "FREE_SLOTS()", u256),
    ("totalSupply", "totalSupply()", u256),
    ("totalMinted", "totalMinted()", u256),
    ("freeClaimed", "freeClaimed()", u256),
    ("freeMinted", "freeMinted()", u256),
    ("freeLeft", "freeLeft()", u256),
    ("mintOpen", "mintOpen()", u256),
    ("OWNER", "OWNER()", addr_of),
    ("owner", "owner()", addr_of),
]


def main():
    discards = json.load(open(f"{BASE}/same-owner-discards.json"))
    d_owners = {r.get("owner", "").lower() for r in discards if isinstance(r, dict)}
    out = {}
    for addr, fblk, mints, minters in TARGETS:
        r = {"first_block": fblk, "scan_mints": mints, "scan_minters": minters}
        try:
            blk = rpc("eth_getBlockByNumber", [hex(fblk), False], timeout=8)
            ts = int(blk["timestamp"], 16)
            r["first_block_ts"] = ts
            r["first_block_wib"] = datetime.datetime.fromtimestamp(
                ts, datetime.timezone(datetime.timedelta(hours=7))
            ).strftime("%Y-%m-%d %H:%M:%S WIB")
        except Exception as e:
            r["first_block_ts_error"] = str(e)
        print(f"\n== {addr} first={r.get('first_block_wib')}", flush=True)
        for name, sig, dec in FIELDS:
            try:
                v = dec(call(addr, sel(sig)))
                r[name] = v
                print(f"  {name}: {v}", flush=True)
            except Exception as e:
                r[name + "_error"] = str(e)[:80]
                print(f"  {name}: ERROR {str(e)[:80]}", flush=True)
        # user-slot probes
        for name, sig in [
            ("freeClaimed_user", "freeClaimed(address)"),
            ("freeMintedBy_user", "freeMintedBy(address)"),
            ("freeUsed_user", "freeUsed(address)"),
            ("mintedBy_user", "mintedBy(address)"),
        ]:
            try:
                v = u256(call(addr, sel(sig) + enc_addr(USER)[2:]))
                r[name] = v
                print(f"  {name}: {v}", flush=True)
            except Exception as e:
                r[name + "_error"] = str(e)[:80]
                print(f"  {name}: ERROR {str(e)[:80]}", flush=True)
        for name, sig in [("quote_1", "quote(uint256)"), ("costFor_1", "costFor(uint256)")]:
            try:
                q = u256(call(addr, sel(sig) + enc_u256(1)[2:]))
                r[name] = q
                print(f"  {name}: {q} wei = {q / 1e18 if q is not None else None} BNB", flush=True)
            except Exception as e:
                r[name + "_error"] = str(e)[:80]
                print(f"  {name}: ERROR {str(e)[:80]}", flush=True)
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
        except Exception as e:
            r["sourcify"] = f"error:{type(e).__name__}"
            print(f"  sourcify: ERROR {e}", flush=True)
        owner = (r.get("OWNER") or r.get("owner") or "").lower()
        r["owner_in_discards"] = owner in d_owners if owner else None
        reg = (r.get("AGENT_REGISTRY") or r.get("AGENT_ID_REGISTRY") or r.get("agentRegistry") or "")
        r["registry_view_match"] = reg.lower() == REGISTRY_EXPECTED.lower() if reg else None
        print(f"  owner in discards: {r['owner_in_discards']}; registry view match: {r['registry_view_match']}", flush=True)
        out[addr] = r
    json.dump(out, open(f"{BASE}/run-2026-11-08-1331-triage.json", "w"), indent=1)
    print("\nsaved run-2026-11-08-1331-triage.json", flush=True)


if __name__ == "__main__":
    main()
