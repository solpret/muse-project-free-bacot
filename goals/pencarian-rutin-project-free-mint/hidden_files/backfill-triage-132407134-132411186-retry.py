#!/usr/bin/env python3
"""Backfill triage RETRY run 2026-11-08 ~22:0x WIB, window 132407134-132411186.
OUPE Cards 0x7cd1C2a0EE1DB8Bb3CE82270ec2610Be74A1285d only: agentRegistry()
transport-failed in the first pass; retry it + free-path views.
Read-only eth_call / Sourcify already done; writes only
backfill-triage-132407134-132411186-retry.json. No preview/mint/sign.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0x7cd1C2a0EE1DB8Bb3CE82270ec2610Be74A1285d"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a.lower()[2:]

def enc_uint(n):
    return format(int(n), "064x")

def eth_call(to, data):
    try:
        r = race("eth_call", [{"to": to, "data": data}, "latest"])
        if isinstance(r, dict) and "error" in r:
            return {"error": str(r["error"])[:300]}
        return {"result": r}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:300]}"}

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

def dec_str(h):
    if not h or h == "0x" or len(h) < 130:
        return None
    try:
        ln = int(h[66:130], 16)
        return bytes.fromhex(h[130:130 + ln * 2]).decode("utf-8", "replace")
    except Exception:
        return None

def vcall(sig, args=None, decode="uint"):
    data = "0x" + sel(sig)
    for a in (args or []):
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            data += enc_addr(a)
        else:
            data += enc_uint(a)
    r = eth_call(ADDR, data)
    if "error" in r:
        return {"fn": sig, "error": r["error"]}
    h = r["result"]
    if decode == "uint":
        v = dec_uint(h)
    elif decode == "bool":
        v = dec_uint(h)
        v = None if v is None else bool(v)
    elif decode == "addr":
        v = dec_addr(h)
        v = v.lower() if v else None
    elif decode == "str":
        v = dec_str(h)
    else:
        v = h
    if v is None and h not in (None, "0x"):
        return {"fn": sig, "value": None, "raw": str(h)[:200], "note": "decode-null (revert?)"}
    return {"fn": sig, "value": v}

out = {"address": ADDR, "retry": "agentRegistry + free-path views"}
# agentRegistry() 3 attempts (transport flakiness vs genuine revert)
for i in (1, 2, 3):
    r = vcall("agentRegistry()", None, "addr")
    out[f"agentRegistry_attempt{i}"] = r
    if "error" not in r:
        break
    time.sleep(3)
out["agentRegistry_exact_match"] = any(
    out.get(f"agentRegistry_attempt{i}", {}).get("value") == REGISTRY.lower()
    for i in (1, 2, 3))
for sig, args, dec in [
    ("agentIds()", None, "addr"),
    ("isAgent(address)", [USER], "bool"),
    ("FREE_CLAIM()", None, "uint"),
    ("FREE_BASE()", None, "uint"),
    ("FREE_MAX()", None, "uint"),
    ("freeClaimed()", None, "uint"),
    ("remainingFor(address)", [USER], "uint"),
    ("phase()", None, "uint"),
    ("startTime()", None, "uint"),
    ("marketOpen()", None, "bool"),
    ("priceOf(uint256)", [1], "uint"),
    ("quote(uint256)", [1], "uint"),
    ("quote(uint256)", [0], "uint"),
    ("website()", None, "str"),
    ("stats()", None, "raw"),
]:
    out[sig] = vcall(sig, args, dec)
    time.sleep(0.5)
# first-mint block timestamp re-check + current freeClaimed re-read
try:
    b = race("eth_getBlockByNumber", [hex(132410796), False])
    ts = int(b["timestamp"], 16)
    out["first_block_ts"] = ts
    out["first_block_wib"] = time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7 * 3600))
except Exception as e:
    out["first_block_ts_error"] = f"{type(e).__name__}: {e}"
print(json.dumps(out, indent=1))
json.dump(out, open(f"{BASE}/backfill-triage-132407134-132411186-retry.json", "w"), indent=1)
print("WROTE backfill-triage-132407134-132411186-retry.json")
