#!/usr/bin/env python3
"""Retry triage backfill run 132266113-132268175 after batch 429.
READ-ONLY. Single _single eth_calls, 3s pause between selectors, 20s wait on 429.
Writes backfill-triage-132266113-132268175.json."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak
from eth_abi import decode

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
OUT = f"{BASE}/backfill-triage-132266113-132268175.json"
ADDR = "0x4C9da74aa08Ed26EDC163a2A7531430f6F5651c2"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
FIRST_BLOCK = 132266809
EPS = ["https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed3.bnbchain.org/",
       "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed.binance.org/",
       "https://bsc-rpc.publicnode.com/"]

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

def enc_uint(n):
    return format(n, "064x")

def rpc(method, params, timeout=10):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0), None
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:120]}"
    return None, last

CALLS = [
    ("agentRegistry", "agentRegistry()", "address", None),
    ("agentIdRegistry", "agentIdRegistry()", "address", None),
    ("AGENT_ID_REGISTRY", "AGENT_ID_REGISTRY()", "address", None),
    ("AGENT_REGISTRY", "AGENT_REGISTRY()", "address", None),
    ("REGISTRY", "REGISTRY()", "address", None),
    ("name", "name()", "string", None),
    ("symbol", "symbol()", "string", None),
    ("totalSupply", "totalSupply()", "uint256", None),
    ("owner", "owner()", "address", None),
    ("FREE_CAP", "FREE_CAP()", "uint256", None),
    ("FREE_SUPPLY", "FREE_SUPPLY()", "uint256", None),
    ("FREE_SLOTS", "FREE_SLOTS()", "uint256", None),
    ("FREE_AMOUNT", "FREE_AMOUNT()", "uint256", None),
    ("FREE_PER_WALLET", "FREE_PER_WALLET()", "uint256", None),
    ("freeMinted", "freeMinted()", "uint256", None),
    ("freeSupply", "freeSupply()", "uint256", None),
    ("freeClaimed_user", "freeClaimed(address)", "bool", USER),
    ("freeClaimed_noarg", "freeClaimed()", "bool", None),
    ("freeCount_user", "freeCount(address)", "uint256", USER),
    ("MAX_SUPPLY", "MAX_SUPPLY()", "uint256", None),
    ("maxSupply", "maxSupply()", "uint256", None),
    ("PRICE", "PRICE()", "uint256", None),
    ("mintOpen", "mintOpen()", "bool", None),
    ("paidMintedCount", "paidMintedCount()", "uint256", None),
    ("paidUnlocked", "paidUnlocked()", "bool", None),
    ("balanceOf_user", "balanceOf(address)", "uint256", USER),
    ("quote_user_1", "quote(address,uint256)", "uint256", ("addr_uint", USER, 1)),
]

out = {"address": ADDR, "sourcify": "not_verified (HTTP 404 via curl)", "calls": {}}
for i, (name, sig, typ, arg) in enumerate(CALLS):
    data = sel(sig)
    if arg is None:
        pass
    elif isinstance(arg, tuple) and arg[0] == "addr_uint":
        data += enc_addr(arg[1]) + enc_uint(arg[2])
    else:
        data += enc_addr(arg)
    raw, e = None, None
    for attempt in (1, 2, 3):
        raw, e = rpc("eth_call", [{"to": ADDR, "data": data}, "latest"])
        if raw or (e and "429" not in str(e)):
            break
        print(f"{name} attempt {attempt}: 429, waiting 20s...", flush=True)
        time.sleep(20)
    if raw is None or raw == "0x":
        out["calls"][name] = {"error": e or "empty/revert"}
    else:
        try:
            v = decode([typ], bytes.fromhex(raw[2:]))[0]
            out["calls"][name] = {"value": v.hex() if isinstance(v, bytes) else v}
        except Exception as ex:
            out["calls"][name] = {"error": f"decode: {ex}", "raw": raw[:130]}
    print(f"{name}: {out['calls'][name]}", flush=True)
    if i < len(CALLS) - 1:
        time.sleep(3)

# first-mint block timestamp via dataseed (NOT Ankr)
blk, e = rpc("eth_getBlockByNumber", [hex(FIRST_BLOCK), False])
if blk:
    out["first_block_ts"] = {"value": int(blk["timestamp"], 16)}
else:
    out["first_block_ts"] = {"error": e or "eth_getBlockByNumber failed all endpoints"}

disc = json.load(open(f"{BASE}/same-owner-discards.json"))
owners = {d["owner"].lower() for d in disc}
contracts = {d["contract"].lower() for d in disc}
owner = out["calls"].get("owner", {}).get("value", "")
out["owner_in_discards"] = {"value": owner.lower() in owners if owner else None}
out["contract_in_discards"] = {"value": ADDR.lower() in contracts}
out["registry_exact_match"] = {
    "value": any(
        out["calls"].get(k, {}).get("value", "").lower() == REGISTRY.lower()
        for k in ("agentRegistry", "agentIdRegistry", "AGENT_ID_REGISTRY", "AGENT_REGISTRY", "REGISTRY")
    )
}

with open(OUT, "w") as f:
    json.dump(out, f, indent=2, default=str)
print("WROTE", OUT)
