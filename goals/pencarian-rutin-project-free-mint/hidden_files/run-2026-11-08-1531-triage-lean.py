#!/usr/bin/env python3
"""Lean triage run 1531 first-seen (genuinely-new only; 22 re-finds excluded) (read-only). Fields: name/symbol/registry
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
    ("0xd80D0095746999c93AE837B1DE1569d5814405dC", 132361002, 28, 28),
    ("0x8b8427c7d11103125FE9d1bC45EBA072Fc61d947", 132361205, 10, 10),
    ("0xc5C6153e1ff3D05F5424091856F31Bab857DE68c", 132361545, 5, 4),
    ("0x3f26450491C0819Cf16C1e710b3DDa7B8209Ef76", 132361139, 4, 1),
    ("0xE1a438A132659Fea25AFD7712Ed7F203e62cC420", 132361319, 3, 1),
    ("0x38850dA344c7674470943A9091dF1679F7E2A6D5", 132361601, 3, 1),
    ("0x16E33821066A6e3FFEb670924A321526e3170a72", 132361270, 2, 2),
    ("0x65994Ec1e9c2518d06Ad3E4c063efF1f517003cF", 132361569, 2, 2),
    ("0xB0Fe5643e5840239F5F2269f92c42B69a8B34C3B", 132361074, 1, 1),
    ("0x2E7Aa64BAc710082bb0E84F4BEb7C0cF668CfC29", 132361132, 1, 1),
    ("0x0d09eF40DF44bb1820E8b293198bbfef61d06893", 132361239, 1, 1),
    ("0xf7527a3727B48052fbC5E1fF1ED62F6D349843A3", 132361259, 1, 1),
    ("0x5977CF8C65F392247c030eE7867eF3D32879E939", 132361347, 1, 1),
    ("0xBC3C55a7b69C7c75b44bfEF11302E9f64bD3Cf0d", 132361474, 1, 1),
    ("0x05e8738290be6639fD0f7236ebF444E5466D3164", 132361473, 1, 1),
    ("0x82Cf5049146D8656d1d4877546110C29B4a1c71a", 132361533, 1, 1),
    ("0x5aCC0Ec4449Edb788f43803cDb1A11f1f6b7E64d", 132361581, 1, 1),
    ("0xd08ef372B52C29255fEd7004f59bF41571451894", 132361734, 1, 1),
    ("0xA889711a46bA370dA1e068F02762A065fC3D06e7", 132361804, 1, 1),
    ("0xA3D48855EdAb6394F217Bc0F30991Ea13CFeA86f", 132361847, 1, 1),
    ("0xF58cebE35bfb159EFA897BB33191e67B3C1b4B83", 132361900, 1, 1),
    ("0xD09052d690151702759481Bbcb0eB5Dbdc5f1eAA", 132361900, 1, 1),
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
    json.dump(out, open(f"{BASE}/run-2026-11-08-1531-triage.json", "w"), indent=1)
    print("\nsaved run-2026-11-08-1531-triage.json", flush=True)


if __name__ == "__main__":
    main()
