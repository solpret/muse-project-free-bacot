#!/usr/bin/env python3
"""Lean triage run backfill 132213366-132219365 (2026-11-07 ~23:4x WIB).
Read-only. Sourcify ABI dulu (curl); eth_call HANYA untuk fungsi yang ADA
di ABI; proxy ERC1967 -> resolve implementation slot lalu cek ABI impl.
Block timestamp via dataseed eth_getBlockByNumber (fast_rpc._single).
owner() single eth_call; revert = unverified.
"""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
OUT = f"{BASE}/backfill-triage-132213366-132219365.json"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed3.bnbchain.org/",
       "https://bsc-rpc.publicnode.com/"]
IMPL_SLOT = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"

FIRST_SEEN = [
    ("0x3f8eDBc2C414cCf7454152ae8f72f43657Ede95C", "ERC721", 5, 1, 132215484),
    ("0xB9BC4DCc063d2eE749845C2a308CC56c908b3F45", "ERC1155", 1, 1, 132218891),
]
FREE_VIEWS = {"freeClaimed", "freeMinted", "freeLeft", "freeSupply", "freeSharesRemaining",
              "freeFor", "freeAvailable", "freeUsed", "freeSharesClaimed"}

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def rpc(method, params, timeout=12):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0), None
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:120]}"
    return None, last

def sourcify_abi(address):
    try:
        p = subprocess.run(["curl", "-s", "-m", "25",
            f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"],
            capture_output=True, text=True, timeout=30)
        if p.returncode != 0 or not p.stdout.strip():
            return ("curl_error", None, None)
        d = json.loads(p.stdout)
        if d.get("match") is None and d.get("abi") is None:
            return ("not_verified", None, d.get("verifiedAt"))
        return ("verified", d.get("abi"), d.get("verifiedAt"))
    except Exception as e:
        return (f"error:{type(e).__name__}", None, None)

def fns_of(abi):
    fns = {}
    if isinstance(abi, list):
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
    return fns

discards = set()
try:
    dj = json.load(open(f"{BASE}/same-owner-discards.json"))
    recs = dj if isinstance(dj, list) else dj.get("records", dj.get("discards", []))
    for r in recs:
        if isinstance(r, dict):
            discards.add(str(r.get("owner", "")).lower())
except Exception as e:
    print("discards read error:", e)

results = []
for addr, kind, mc, dm, fb in FIRST_SEEN:
    status, abi, verified_at = sourcify_abi(addr)
    fns = fns_of(abi)
    names = set(fns)
    impl = None
    impl_status = None
    impl_fns = {}
    if status == "verified" and not names and "implementation" not in str(abi).lower():
        # proxy with no functions in ABI -> resolve ERC1967 implementation
        r, e = rpc("eth_getStorageAt", [addr, IMPL_SLOT, "latest"])
        if r:
            impl = "0x" + r[-40:]
            if int(impl, 16) != 0:
                impl_status, impl_abi, _ = sourcify_abi(impl)
                impl_fns = fns_of(impl_abi)
    all_names = names | set(impl_fns)
    has_reg = "agentRegistry" in all_names
    free_views = sorted(all_names & FREE_VIEWS)
    agent_shaped = has_reg and bool(free_views)
    # agentRegistry() value check only if present
    reg_val = None
    reg_err = None
    if has_reg:
        data = sel("agentRegistry()")
        target = impl if impl else addr
        r, e = rpc("eth_call", [{"to": target, "data": data}, "latest"])
        if r and len(r) >= 66:
            reg_val = "0x" + r[-40:]
        else:
            reg_err = e or f"short:{r}"
    # owner() single call
    owner = None
    owner_err = None
    r, e = rpc("eth_call", [{"to": addr, "data": sel("owner()")}, "latest"])
    if r and len(r) >= 66:
        owner = "0x" + r[-40:]
    else:
        owner_err = e or f"revert/short:{r}"
    # first-mint block timestamp
    ts = None
    ts_err = None
    r, e = rpc("eth_getBlockByNumber", [hex(fb), False])
    if r and r.get("timestamp"):
        ts = int(r["timestamp"], 16)
    else:
        ts_err = e or "no timestamp"
    row = {"address": addr, "kind": kind, "first_block": fb, "mint_count": mc,
           "distinct_minters": dm, "sourcify": status, "verified_at": verified_at,
           "abi_functions": sorted(names), "proxy_implementation": impl,
           "implementation_sourcify": impl_status,
           "implementation_functions": sorted(set(impl_fns)),
           "abi_has_agentRegistry": has_reg, "abi_has_free_view": bool(free_views),
           "free_views": free_views, "agentRegistry_value": reg_val,
           "agentRegistry_matches": (reg_val or "").lower() == REGISTRY.lower() if reg_val else False,
           "agentRegistry_error": reg_err, "agent_shaped": agent_shaped,
           "owner": owner, "owner_error": owner_err,
           "same_owner_discard": bool(owner) and owner.lower() in discards,
           "first_mint_timestamp": ts, "block_error": ts_err}
    results.append(row)
    print(addr, status, "impl", impl, impl_status, "agent_shaped", agent_shaped,
          "owner", owner, "ts", ts, flush=True)
    time.sleep(2)

json.dump({"run": "backfill-132213366-132219365", "results": results}, open(OUT, "w"), indent=1)
print("saved", OUT)
print("AGENT_SHAPED:", [r["address"] for r in results if r["agent_shaped"]])
print("SAME_OWNER_DISCARD:", [r["address"] for r in results if r["same_owner_discard"]])
