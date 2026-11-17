#!/usr/bin/env python3
"""Triage backfill run 132266113-132268175: 1 first-seen ERC721 0x4C9da74a...
READ-ONLY. Uses fast_rpc (dataseed race) for eth_call + block timestamp.
Sourcify ABI already fetched via curl -> /tmp/abi-4c9d.json (HTTP 404, not_verified)."""
import json, sys
from eth_hash.auto import keccak
from eth_abi import decode

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import call_many, race

ADDR = "0x4C9da74aa08Ed26EDC163a2A7531430f6F5651c2"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
FIRST_BLOCK = 132266809

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

def enc_uint(n):
    return format(n, "064x")

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

items = []
for name, sig, typ, arg in CALLS:
    data = sel(sig)
    if arg is None:
        pass
    elif isinstance(arg, tuple) and arg[0] == "addr_uint":
        data += enc_addr(arg[1]) + enc_uint(arg[2])
    else:
        data += enc_addr(arg)
    items.append((ADDR, data))

results = call_many(items)
out = {"address": ADDR, "sourcify": "not_verified (HTTP 404 via curl)", "calls": {}}
for (name, sig, typ, arg), res in zip(CALLS, results):
    if res is None or res == "0x":
        out["calls"][name] = {"error": "empty/revert"}
        continue
    try:
        v = decode([typ], bytes.fromhex(res[2:]))[0]
        out["calls"][name] = {"value": v.hex() if isinstance(v, bytes) else v}
    except Exception as e:
        out["calls"][name] = {"error": f"decode: {e}", "raw": res}

# first-mint block timestamp via dataseed (NOT Ankr)
blk = race("eth_getBlockByNumber", [hex(FIRST_BLOCK), False])
if blk:
    out["first_block_ts"] = {"value": int(blk["timestamp"], 16)}
else:
    out["first_block_ts"] = {"error": "eth_getBlockByNumber failed all endpoints"}

# owner vs same-owner-discards
disc = json.load(open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/same-owner-discards.json"))
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

print(json.dumps(out, indent=2, default=str))
with open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/backfill-triage-132266113-132268175.json", "w") as f:
    json.dump(out, f, indent=2, default=str)
