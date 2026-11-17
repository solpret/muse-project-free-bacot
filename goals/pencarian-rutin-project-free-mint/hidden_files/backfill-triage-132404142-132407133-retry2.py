#!/usr/bin/env python3
"""Final focused retry: SHACHO agentRegistry/owner/mintOpen/price (5 attempts,
longer backoff). Read-only; writes backfill-triage-132404142-132407133-retry2.json.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
SHACHO = "0x26E009350Ef80cb542785d57c27c686a582bf605"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a.lower()[2:]

def call(to, sig, args=None, decode="uint", attempts=5):
    data = "0x" + sel(sig)
    for a in (args or []):
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            data += enc_addr(a)
        else:
            data += format(int(a), "064x")
    last = None
    for i in range(attempts):
        try:
            r = race("eth_call", [{"to": to, "data": data}, "latest"])
            if isinstance(r, dict) and "error" in r:
                return {"fn": sig, "error": str(r["error"])[:150]}
            h = r
            if decode == "uint":
                v = int(h, 16) if h and h != "0x" else None
            elif decode == "bool":
                v = int(h, 16) if h and h != "0x" else None
                v = None if v is None else bool(v)
            elif decode == "addr":
                v = ("0x" + h[-40:]).lower() if h and len(h) >= 66 else None
            else:
                v = h
            return {"fn": sig, "value": v, "attempt": i + 1}
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:120]}"
            time.sleep(5)
    return {"fn": sig, "error": last, "attempts": attempts}

def main():
    out = {}
    out["agentRegistry"] = call(SHACHO, "agentRegistry()", None, "addr")
    out["agentRegistry_exact_match"] = out["agentRegistry"].get("value") == REGISTRY.lower()
    out["owner"] = call(SHACHO, "owner()", None, "addr")
    out["mintOpen"] = call(SHACHO, "mintOpen()", None, "bool")
    out["price"] = call(SHACHO, "price()", None, "uint")
    discards = json.load(open(f"{BASE}/same-owner-discards.json"))
    owners = {r.get("owner", "").lower() for r in discards if isinstance(r, dict)}
    out["owner_in_discards"] = (out["owner"].get("value") in owners) if out["owner"].get("value") else None
    print(json.dumps(out, indent=1))
    json.dump(out, open(f"{BASE}/backfill-triage-132404142-132407133-retry2.json", "w"), indent=1)
    print("WROTE backfill-triage-132404142-132407133-retry2.json")

if __name__ == "__main__":
    main()
