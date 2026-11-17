#!/usr/bin/env python3
"""Retry on-chain views for 0xbaC6 (backfill 132126342-132129578 triage).
Read-only; writes backfill-triage-132126342-132129578-retry.json.
Transport failure recorded as such, never as a value."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0xbaC6B6De36a54b2815c02aD3cC5e6551E306Aa90"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_NOPREFIX = USER[2:].lower()

def sel(sig):
    k = keccak.new(digest_bits=256)
    k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def call(data):
    try:
        return race("eth_call", [{"to": ADDR, "data": data}, "latest"])
    except Exception as e:
        return f"ERROR {type(e).__name__}: {e}"

def view(name, sig, arg=None):
    data = sel(sig) + (arg or "")
    r = call(data)
    if isinstance(r, str) and r.startswith("0x") and len(r) >= 66:
        return {"ok": True, "raw": r, "int": int(r, 16), "addr": "0x" + r[-40:]}
    return {"ok": False, "raw": str(r)[:300]}

def view_str(name, sig):
    r = call(sel(sig))
    if isinstance(r, str) and r.startswith("0x") and len(r) >= 130:
        try:
            ln = int(r[130:194], 16)
            s = bytes.fromhex(r[194:194 + ln * 2]).decode("utf-8", "replace")
            return {"ok": True, "value": s}
        except Exception as e:
            return {"ok": False, "raw": str(r)[:200], "err": str(e)}
    return {"ok": False, "raw": str(r)[:200]}

out = {}
out["agentRegistry()"] = view("agentRegistry", "agentRegistry()")
reg = out["agentRegistry()"]
out["agentRegistry_exact"] = bool(reg.get("ok") and reg["addr"].lower() == REGISTRY.lower())
out["agent_registry()"] = view("agent_registry", "agent_registry()")
out["name()"] = view_str("name", "name()")
out["symbol()"] = view_str("symbol", "symbol()")
out["price()"] = view("price", "price()")
out["FREE_SUPPLY"] = view("FREE_SUPPLY", "FREE_SUPPLY()")
out["freeMinted()"] = view("freeMinted", "freeMinted()")
out["paidMinted()"] = view("paidMinted", "paidMinted()")
out["totalMinted()"] = view("totalMinted", "totalMinted()")
out["maxSupply()"] = view("maxSupply", "maxSupply()")
out["maxPerWallet()"] = view("maxPerWallet", "maxPerWallet()")
out["mintedBy(user)"] = view("mintedBy", "mintedBy(address)", USER_NOPREFIX)
out["paused()"] = view("paused", "paused()")
out["passSigner()"] = view("passSigner", "passSigner()")
out["usedPassNonce(user)"] = view("usedPassNonce", "usedPassNonce(address)", USER_NOPREFIX)
# mintFree signature: try no-arg first
out["mintFree_noarg_probe"] = view("mintFree", "mintFree()")
print(json.dumps(out, indent=1))
json.dump(out, open(f"{BASE}/backfill-triage-132126342-132129578-retry.json", "w"), indent=1)
print("WROTE backfill-triage-132126342-132129578-retry.json")
