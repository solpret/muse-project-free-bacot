#!/usr/bin/env python3
"""Backfill triage RETRY run 2026-11-09 ~00:0x WIB, window 132422006-132427337.
Retry failed reads for 0x4AB41152EdB3E2853b19828e51927db36508cd64 only
(first run: fast_rpc all-endpoints TimeoutError/OSError on agentRegistry(),
owner(); Sourcify not_verified, no ABI; agent-shaped ONLY via bytecode
registry-bytes hit). Probe agentRegistry()/agentIdRegistry() exact value,
owner(), name/symbol, free-pool views by selector, user slot; plus
first-block timestamp for Backdoor Pass 0x9c6A008f73a1d1941f4763b88C6eE8c8E4ef8B0a
(block 132426579, failed in first run).
Read-only; writes only backfill-triage-132422006-132427337-retry.json.
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
BDPASS_FIRST_BLOCK = 132426579

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

def dec_str(h):
    if not h or h == "0x" or len(h) < 130:
        return None
    try:
        ln = int(h[66:130], 16)
        return bytes.fromhex(h[130:130 + ln * 2]).decode("utf-8", "replace")
    except Exception:
        return None

def vcall(to, sig, args=None, decode="uint", tries=3):
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
    v = {"uint": dec_uint, "bool": dec_bool, "addr": dec_addr, "str": dec_str}.get(decode, dec_uint)(h)
    if v is None and h not in (None, "0x"):
        return {"fn": sig, "value": None, "raw": str(h)[:100], "note": "decode-null (revert?)"}
    return {"fn": sig, "value": v}

def block_ts(blk, tries=3):
    last = None
    for i in range(tries):
        try:
            b = race("eth_getBlockByNumber", [hex(blk), False])
            ts = int(b["timestamp"], 16)
            return ts, time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7 * 3600))
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:200]}"
            time.sleep(3)
    return None, last

def main():
    out = {"address": ADDR, "retry_wib": time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(time.time() + 7 * 3600))}
    out["agentRegistry"] = vcall(ADDR, "agentRegistry()", None, "addr")
    out["agentRegistry_exact_match"] = (out["agentRegistry"].get("value") == REGISTRY.lower())
    out["agentIdRegistry"] = vcall(ADDR, "agentIdRegistry()", None, "addr")
    out["agentIdRegistry_exact_match"] = (out["agentIdRegistry"].get("value") == REGISTRY.lower())
    out["owner"] = vcall(ADDR, "owner()", None, "addr")
    out["name"] = vcall(ADDR, "name()", None, "str")
    out["symbol"] = vcall(ADDR, "symbol()", None, "str")
    for sig, dec in [("totalSupply()", "uint"), ("totalMinted()", "uint"),
                     ("mintOpen()", "bool"), ("FREE_CAP()", "uint"),
                     ("FREE_POOL()", "uint"), ("FREE_SLOTS()", "uint"),
                     ("FREE_SUPPLY()", "uint"), ("freeMinted()", "uint"),
                     ("MAX_SUPPLY()", "uint"), ("PRICE()", "uint"),
                     ("mintPrice()", "uint"), ("price()", "uint")]:
        out[sig] = vcall(ADDR, sig, None, dec)
    out["freeClaimed(user)"] = vcall(ADDR, "freeClaimed(address)", [USER], "uint")
    out["freeCount(user)"] = vcall(ADDR, "freeCount(address)", [USER], "uint")
    out["balanceOf(user)"] = vcall(ADDR, "balanceOf(address)", [USER], "uint")
    ts, ts_wib = block_ts(BDPASS_FIRST_BLOCK)
    out["bdpass_first_block_timestamp"] = ts
    out["bdpass_first_block_wib"] = ts_wib
    # same-owner check for the retried owner()
    try:
        discards = json.load(open(f"{BASE}/same-owner-discards.json"))
        owners = {r.get("owner", "").lower() for r in discards if isinstance(r, dict)}
        ov = out["owner"].get("value")
        out["owner_in_discards"] = (ov.lower() in owners) if ov else None
    except Exception as e:
        out["owner_in_discards"] = f"discards-read-error: {e}"
    json.dump(out, open(f"{BASE}/backfill-triage-132422006-132427337-retry.json", "w"), indent=1)
    print(json.dumps(out, indent=1))
    print("WROTE backfill-triage-132422006-132427337-retry.json")

if __name__ == "__main__":
    main()
