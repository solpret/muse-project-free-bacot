#!/usr/bin/env python3
"""Triage backfill run 132254478-132257813: 1 first-seen HokiFrog/HFROG.
READ-ONLY. Uses fast_rpc (dataseed race) for eth_call + block timestamp.
Sourcify ABI already fetched via curl -> /tmp/hokifrog-abi.json."""
import json, sys
from eth_hash.auto import keccak
from eth_abi import decode

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import call_many, race

ADDR = "0xeb3ede3893ca798f30648194eCC03119A7071b40"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

CALLS = [
    ("agentIdRegistry", "agentIdRegistry()", "address", None),
    ("FREE_CAP", "FREE_CAP()", "uint256", None),
    ("FREE_PER_WALLET", "FREE_PER_WALLET()", "uint256", None),
    ("freeMinted", "freeMinted()", "uint256", None),
    ("freeCount_user", "freeCount(address)", "uint256", USER),
    ("totalMinted", "totalMinted()", "uint256", None),
    ("MAX_SUPPLY", "MAX_SUPPLY()", "uint256", None),
    ("PRICE", "PRICE()", "uint256", None),
    ("mintOpen", "mintOpen()", "bool", None),
    ("paidMintedCount", "paidMintedCount()", "uint256", None),
    ("paidUnlocked", "paidUnlocked()", "bool", None),
    ("owner", "owner()", "address", None),
    ("treasury", "treasury()", "address", None),
    ("balanceOf_user", "balanceOf(address)", "uint256", USER),
]

items = []
for name, sig, typ, arg in CALLS:
    data = sel(sig) + (enc_addr(arg) if arg else "")
    items.append((ADDR, data))

results = call_many(items)
out = {}
for (name, sig, typ, arg), res in zip(CALLS, results):
    if res is None or res == "0x":
        out[name] = {"error": "empty/revert"}
        continue
    try:
        v = decode([typ], bytes.fromhex(res[2:]))[0]
        out[name] = {"value": v.hex() if isinstance(v, bytes) else v}
    except Exception as e:
        out[name] = {"error": f"decode: {e}", "raw": res}

# first-mint block timestamp via dataseed (NOT Ankr)
blk = race("eth_getBlockByNumber", [hex(132254774), False])
ts = None
if blk:
    ts = int(blk["timestamp"], 16)
    out["first_block_ts"] = {"value": ts}
else:
    out["first_block_ts"] = {"error": "eth_getBlockByNumber failed all endpoints"}

# owner vs same-owner-discards
disc = json.load(open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/same-owner-discards.json"))
owners = {d["owner"].lower() for d in disc}
contracts = {d["contract"].lower() for d in disc}
owner = out.get("owner", {}).get("value", "")
out["owner_in_discards"] = {"value": owner.lower() in owners if owner else None}
out["contract_in_discards"] = {"value": ADDR.lower() in contracts}

print(json.dumps(out, indent=2, default=str))
