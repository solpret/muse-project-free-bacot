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
    ("0xc36FD9884ac52eB406B80D4E91328B39251F54Ab", 132355679, 3, 2),
    ("0x3B016fC92eF08bDe512065F2Ab5658d524744230", 132356212, 2, 2),
    ("0x6810056D235c949f425b394dE590835096dd6AdC", 132356507, 2, 1),
    ("0x09BcDD97186F6F37521bD1b281D329E48ac54B89", 132356265, 1, 1),
    ("0x1f974998031c6DD8137E8D7aC6c2287357A2ddeb", 132356319, 1, 1),
    ("0x9A67E1FD6409B91BD9751206c81fDf37Fc467aE6", 132356308, 1, 1),
    ("0xF10C1E17ae65e88e34253b951dD8EC274fa3AfEB", 132356297, 1, 1),
    ("0x4c895E2eC1FB615d6bd28584644f5e778f64BC36", 132356372, 1, 1),
    ("0x7b601C3D2050B021B3bd9d650D421f3F98436ab3", 132356362, 1, 1),
    ("0xd9D4466342c993b43f02AE2e21D6F125a1Bd937F", 132356351, 1, 1),
    ("0xc2027F9407eA355eeD5845Bb5e653aeed671f212", 132356340, 1, 1),
    ("0x6551529eC146020ee59B41265614b7a00A166A3f", 132356329, 1, 1),
    ("0x273fc2C7705B23eb129E35aC8Da26348E6Fc4980", 132356394, 1, 1),
    ("0x7998Dd32bE1c7bf98d3075C1D0f12De2F0e1d6eC", 132355627, 2, 2),
    ("0x3fc442342a5289d10773aE585C6CB3Dc4A37254e", 132356013, 2, 2),
    ("0x8F1246Dc5556035a4921658d81A0E06427414aFF", 132355637, 1, 1),
    ("0xa422fbf16E0e2f81A38f74B1be8b770B97575529", 132355760, 1, 1),
    ("0x4f1bE6E4c73138D706853584BA0Fa4cB923Dcd95", 132355790, 1, 1),
    ("0xbd0e97f1a2b8b192382935A7B69c9514d75A479A", 132355951, 1, 1),
    ("0xECd0aE8AE79c1e580898480467DfC210143f9FEF", 132356023, 1, 1),
    ("0xED33074b1E7728D8F38d28Bb00E71708c59160F1", 132356011, 1, 1),
    ("0x72D977237f7b3931A08434cEBD0D3814fE13539e", 132356002, 1, 1),
    ("0x85dF79AD6df9BCa9292E73f973ECF49205E62dB8", 132356275, 1, 1),
    ("0xbC2C4A71791fb86d14a2A859B0253aa3BBaEB34c", 132356367, 1, 1),
    ("0x2ED9E0a6992BA22B48c2fc2def6bB2365301A0D0", 132356349, 1, 1),
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
    json.dump(out, open(f"{BASE}/run-2026-11-08-1431-triage.json", "w"), indent=1)
    print("\nsaved run-2026-11-08-1431-triage.json", flush=True)


if __name__ == "__main__":
    main()
