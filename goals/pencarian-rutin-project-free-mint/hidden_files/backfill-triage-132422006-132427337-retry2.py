#!/usr/bin/env python3
"""Backfill triage RETRY-2 run 2026-11-09 ~00:1x WIB, window 132422006-132427337.
Second targeted retry for PanduAGENT 0x4AB41152EdB3E2853b19828e51927db36508cd64
only: agentRegistry()/agentIdRegistry() exact + user free slot + FREE_CAP.
Retry-1 (~00:05 WIB) still hit all-endpoints-failed on those calls while
other calls (owner/name/totalSupply/freeMinted/balanceOf) succeeded, so the
outage is intermittent per-call; one more targeted attempt is warranted.
If these still fail, legs stay UNVERIFIED and no lead is reported.
Read-only; writes only backfill-triage-132422006-132427337-retry2.json.
No preview/mint/sign/approve/swap.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x4AB41152EdB3E2853b19828e51927db36508cd64"

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a.lower()[2:]

def enc_uint(n):
    return format(int(n), "064x")

def eth_call(to, data, tries=4):
    last = None
    for i in range(tries):
        try:
            r = race("eth_call", [{"to": to, "data": data}, "latest"])
            if isinstance(r, dict) and "error" in r:
                return {"error": str(r["error"])[:200]}
            return {"result": r}
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:200]}"
            time.sleep(5)
    return {"error": last}

def dec_addr(h):
    if not h or h == "0x" or len(h) < 66:
        return None
    return "0x" + h[-40:]

def dec_uint(h):
    if not h or h == "0x":
        return None
    try:
        return int(h, 16)
    except Exception:
        return None

def vcall(to, sig, args=None, decode="uint", tries=4):
    data = "0x" + sel(sig)
    for a in (args or []):
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            data += enc_addr(a)
        else:
            data += enc_uint(a)
    r = eth_call(to, data, tries)
    if "error" in r:
        return {"fn": sig, "error": r["error"]}
    h = r["result"]
    v = {"uint": dec_uint, "addr": dec_addr}.get(decode, dec_uint)(h)
    if v is None and h not in (None, "0x"):
        return {"fn": sig, "value": None, "raw": str(h)[:100], "note": "decode-null (revert?)"}
    return {"fn": sig, "value": v}

def main():
    out = {"address": ADDR, "retry2_wib": time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(time.time() + 7 * 3600))}
    out["agentRegistry"] = vcall(ADDR, "agentRegistry()", None, "addr")
    out["agentRegistry_exact_match"] = (out["agentRegistry"].get("value") == REGISTRY.lower())
    out["agentIdRegistry"] = vcall(ADDR, "agentIdRegistry()", None, "addr")
    out["agentIdRegistry_exact_match"] = (out["agentIdRegistry"].get("value") == REGISTRY.lower())
    out["FREE_CAP"] = vcall(ADDR, "FREE_CAP()", None, "uint")
    out["freeMinted"] = vcall(ADDR, "freeMinted()", None, "uint")
    out["freeClaimed(user)"] = vcall(ADDR, "freeClaimed(address)", [USER], "uint")
    out["freeCount(user)"] = vcall(ADDR, "freeCount(address)", [USER], "uint")
    out["totalMinted"] = vcall(ADDR, "totalMinted()", None, "uint")
    out["mintOpen"] = vcall(ADDR, "mintOpen()", None, "uint")
    json.dump(out, open(f"{BASE}/backfill-triage-132422006-132427337-retry2.json", "w"), indent=1)
    print(json.dumps(out, indent=1))
    print("WROTE backfill-triage-132422006-132427337-retry2.json")

if __name__ == "__main__":
    main()
