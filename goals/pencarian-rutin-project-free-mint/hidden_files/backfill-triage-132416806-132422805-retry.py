#!/usr/bin/env python3
"""Backfill triage RETRY run 2026-11-08 ~23:3x WIB, window 132416806-132422805.
Retry failed reads for DRAGON 0x7F00b3Aa3A3e41dc145180C4ED8a24eE568eaED4 only
(first run: fast_rpc all-endpoints TimeoutError/OSError on agentRegistry(),
FREE_CAP(), mintOpen(), totalMinted(), freeMint()).
DRAGON ABI has agentIdRegistry() (not agentRegistry()) - verify its value
against 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, plus free pool state.
Read-only; writes only backfill-triage-132416806-132422805-retry.json.
No preview/mint/sign/approve/swap.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x7F00b3Aa3A3e41dc145180C4ED8a24eE568eaED4"

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a.lower()[2:]

def enc_uint(n):
    return format(int(n), "064x")

def eth_call(to, data, tries=3):
    last = None
    for i in range(tries):
        try:
            r = race("eth_call", [{"to": to, "data": data}, "latest"])
            if isinstance(r, dict) and "error" in r:
                return {"error": str(r["error"])[:200]}
            return {"result": r}
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:200]}"
            time.sleep(3)
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

def dec_bool(h):
    v = dec_uint(h)
    return None if v is None else bool(v)

def vcall(sig, args=None, decode="uint", tries=3):
    data = "0x" + sel(sig)
    for a in (args or []):
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            data += enc_addr(a)
        else:
            data += enc_uint(a)
    r = eth_call(ADDR, data, tries)
    if "error" in r:
        return {"fn": sig, "error": r["error"]}
    h = r["result"]
    v = {"uint": dec_uint, "bool": dec_bool, "addr": dec_addr}.get(decode, dec_uint)(h)
    if v is None and h not in (None, "0x"):
        return {"fn": sig, "value": None, "raw": str(h)[:100], "note": "decode-null (revert?)"}
    return {"fn": sig, "value": v}

def main():
    out = {"address": ADDR, "retry_wib": time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(time.time() + 7 * 3600))}
    out["agentIdRegistry"] = vcall("agentIdRegistry()", None, "addr")
    out["agentIdRegistry_exact_match"] = (out["agentIdRegistry"].get("value") == REGISTRY.lower())
    out["agentRegistry_selector"] = vcall("agentRegistry()", None, "addr")
    out["agentRegistry_selector_exact_match"] = (out["agentRegistry_selector"].get("value") == REGISTRY.lower())
    for sig, dec in [("FREE_CAP()", "uint"), ("FREE_PER_WALLET()", "uint"),
                     ("freeMinted()", "uint"), ("totalMinted()", "uint"),
                     ("mintOpen()", "bool"), ("PRICE()", "uint"),
                     ("paidMintedCount()", "uint"), ("paidUnlocked()", "bool"),
                     ("tierRemaining()", "uint"), ("MAX_SUPPLY()", "uint"),
                     ("BRONZE_CAP()", "uint"), ("SILVER_CAP()", "uint"),
                     ("GOLD_CAP()", "uint"), ("LEGENDARY_CAP()", "uint"),
                     ("TIER_COUNT()", "uint")]:
        out[sig] = vcall(sig, None, dec)
    out["freeCount(user)"] = vcall("freeCount(address)", [USER], "uint")
    out["balanceOf(user)"] = vcall("balanceOf(address)", [USER], "uint")
    fc = out.get("FREE_CAP()", {}).get("value")
    fm = out.get("freeMinted()", {}).get("value")
    if isinstance(fc, int) and isinstance(fm, int) and fc > 0:
        out["free_pct"] = round(100.0 * fm / fc, 2)
        out["free_left"] = fc - fm
    json.dump(out, open(f"{BASE}/backfill-triage-132416806-132422805-retry.json", "w"), indent=1)
    print(json.dumps(out, indent=1))
    print("WROTE backfill-triage-132416806-132422805-retry.json")

if __name__ == "__main__":
    main()
