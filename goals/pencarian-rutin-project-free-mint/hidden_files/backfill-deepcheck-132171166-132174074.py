#!/usr/bin/env python3
"""Deep check run 2026-11-07 ~16:3x WIB for the 2 registry-bytes first-seen
contracts without Sourcify ABI (Hakuna Agent 0x75f9E01a, 0xECd0aE8A) plus
retries of transient-failed timestamps/owner() calls.
Read-only. Direct selector calls (no ABI needed); transport failures
recorded as such, never as reverts.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
ONE = "0000000000000000000000000000000000000000000000000000000000000001"

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def call(to, data, tries=3):
    last = None
    for _ in range(tries):
        try:
            r = race("eth_call", [{"to": to, "data": data}, "latest"])
            return r, None
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:160]}"
            time.sleep(2)
    return None, last

def block_ts(blk, tries=3):
    last = None
    for _ in range(tries):
        try:
            b = race("eth_getBlockByNumber", [hex(blk), False])
            ts = int(b["timestamp"], 16)
            return ts, time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7*3600)), None
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:160]}"
            time.sleep(2)
    return None, None, last

def dec_addr(raw):
    if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 66:
        return "0x" + raw[-40:]
    return None

def dec_uint(raw):
    if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 2:
        try:
            return int(raw, 16)
        except Exception:
            return None
    return None

# zero-arg views
ZERO_ARG = ["agentRegistry()", "AGENT_REGISTRY()", "AGENT_ID_REGISTRY()",
            "REGISTRY()", "freeLeft()", "freeUsed()", "FREE_SUPPLY()",
            "FREE_SLOTS()", "freeMinted()", "freeSharesRemaining()",
            "PRICE()", "price()", "mintPrice()", "MINT_PRICE()",
            "PUBLIC_PRICE()", "totalSupply()", "MAX_SUPPLY()", "maxSupply()",
            "totalMinted()", "minted()", "freeSupply()", "freeCap()",
            "freeWalletCap()", "freeToken()", "spotsLeft()", "remaining()",
            "mintOpen()", "isLive()", "launched()"]
# (address) views
ADDR_ARG = ["freeClaimed(address)", "freeFor(address)", "freeSharesClaimed(address)",
            "freeSharesClaimedBy(address)", "mintedBy(address)", "balanceOf(address)",
            "eligible(address)", "canMint(address)", "allowance(address)"]
# (uint256) views
UINT_ARG = ["quote(uint256)", "cost(uint256)", "getPrice(uint256)", "priceFor(uint256)"]
# (address,uint256) views
ADDR_UINT_ARG = ["quote(address,uint256)", "cost(address,uint256)"]

discards = json.load(open(f"{BASE}/same-owner-discards.json"))
discard_owners = {r.get("owner", "").lower() for r in discards if isinstance(r, dict)}

targets = {
    "0x75f9E01aF66A6B3B5f169d1d9C88e6f356a01e2F": {"name": "Hakuna Agent/HAKUNA", "first_block": 132172876},
    "0xECd0aE8AE79c1e580898480467DfC210143f9FEF": {"name": "unknown (1 mint)", "first_block": 132173698},
}

out = {}
for addr, meta in targets.items():
    row = {"address": addr, "name": meta["name"], "first_block": meta["first_block"]}
    ts, wib, err = block_ts(meta["first_block"])
    row["first_block_timestamp"] = ts
    row["first_block_wib"] = wib
    row["first_block_ts_error"] = err
    calls = {}
    for sig in ZERO_ARG:
        raw, e = call(addr, sel(sig))
        calls[sig] = {"raw": (raw or "")[:130], "uint": dec_uint(raw) if raw else None,
                      "addr": dec_addr(raw) if raw else None, "error": e}
    for sig in ADDR_ARG:
        raw, e = call(addr, sel(sig) + USER_PAD)
        calls[sig] = {"raw": (raw or "")[:130], "uint": dec_uint(raw) if raw else None,
                      "addr": dec_addr(raw) if raw else None, "error": e}
    for sig in UINT_ARG:
        raw, e = call(addr, sel(sig) + ONE)
        calls[sig] = {"raw": (raw or "")[:130], "uint": dec_uint(raw) if raw else None,
                      "addr": dec_addr(raw) if raw else None, "error": e}
    for sig in ADDR_UINT_ARG:
        raw, e = call(addr, sel(sig) + USER_PAD + ONE)
        calls[sig] = {"raw": (raw or "")[:130], "uint": dec_uint(raw) if raw else None,
                      "addr": dec_addr(raw) if raw else None, "error": e}
    row["calls"] = calls
    # registry exact?
    reg_vals = [calls[s].get("addr") for s in ("agentRegistry()", "AGENT_REGISTRY()", "AGENT_ID_REGISTRY()", "REGISTRY()") if calls.get(s)]
    row["registry_exact"] = any(a and a.lower() == REGISTRY.lower() for a in reg_vals)
    row["registry_returned"] = [a for a in reg_vals if a]
    # owner()
    raw, e = call(addr, "0x8da5cb5b")
    owner = dec_addr(raw) if raw else None
    row["owner"] = owner
    row["owner_error"] = e
    row["owner_in_discards"] = bool(owner and owner.lower() in discard_owners)
    out[addr] = row
    print(json.dumps(row, indent=1))

# retry failed timestamps / owner() for the other first-seen
retries = {}
for blk in (132171308, 132173750):
    ts, wib, err = block_ts(blk)
    retries[f"block_{blk}"] = {"timestamp": ts, "wib": wib, "error": err}
for addr in ("0xd14c87C753960edF036d10579186A1b2596E95D4",
             "0x5B837a9a9361A418541F4A6D39e5F43765E7ef60"):
    raw, e = call(addr, "0x8da5cb5b")
    owner = dec_addr(raw) if raw else None
    retries[addr] = {"owner": owner, "error": e,
                     "owner_in_discards": bool(owner and owner.lower() in discard_owners)}
print(json.dumps({"retries": retries}, indent=1))
out["_retries"] = retries
json.dump(out, open(f"{BASE}/backfill-triage-132171166-132174074-deepcheck.json", "w"), indent=1)
print("WROTE backfill-triage-132171166-132174074-deepcheck.json")
