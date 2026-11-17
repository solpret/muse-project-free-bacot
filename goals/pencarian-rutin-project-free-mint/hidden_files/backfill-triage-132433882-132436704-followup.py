#!/usr/bin/env python3
"""Follow-up probe Dragon Agent 0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6.
Resolves the triage ambiguities: REGISTRY() exact value (ABI has REGISTRY, not
agentRegistry), agentGate(), canMint(user), maxSupply(), MAX_PER_WALLET(),
priceOf(user,1); retry agentRegistry() via fast_rpc AND direct curl to tell
revert apart from transport failure. Read-only; writes only
backfill-triage-132433882-132436704-followup.json.
"""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6"
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
            return {"error": str(r["error"])[:200]}
        return {"result": r}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:200]}"}

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
    else:
        v = h
    if v is None and h not in (None, "0x"):
        return {"fn": sig, "value": None, "raw": str(h)[:100], "note": "decode-null (revert?)"}
    return {"fn": sig, "value": v}

def direct_curl_call(to, data):
    """One eth_call via direct curl to bsc-dataseed (bypasses fast_rpc race)."""
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": to, "data": data}, "latest"]})
    for url in ["https://bsc-dataseed.binance.org/",
                "https://bsc-dataseed1.bnbchain.org/",
                "https://bsc-dataseed2.bnbchain.org/"]:
        try:
            r = subprocess.run(["curl", "-s", "-m", "20", "-X", "POST",
                                "-H", "Content-Type: application/json",
                                "-d", payload, url],
                               capture_output=True, text=True, timeout=30)
            d = json.loads(r.stdout)
            if "result" in d:
                return {"via": url, "result": d["result"]}
            if "error" in d:
                return {"via": url, "error": str(d["error"])[:200]}
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
    return {"error": f"all direct-curl failed: {last}"}

def main():
    out = {"address": ADDR}
    out["REGISTRY"] = vcall("REGISTRY()", None, "addr")
    out["REGISTRY_exact_match"] = (out["REGISTRY"].get("value") == REGISTRY.lower())
    out["agentGate"] = vcall("agentGate()", None, "bool")
    out["canMint(user)"] = vcall("canMint(address)", [USER], "bool")
    out["maxSupply"] = vcall("maxSupply()", None, "uint")
    out["MAX_PER_WALLET"] = vcall("MAX_PER_WALLET()", None, "uint")
    out["priceOf(user,1)"] = vcall("priceOf(address,uint256)", [USER, 1], "uint")
    out["price"] = vcall("price()", None, "uint")
    out["FREE_COUNT"] = vcall("FREE_COUNT()", None, "uint")
    out["totalSupply"] = vcall("totalSupply()", None, "uint")
    out["balanceOf(user)"] = vcall("balanceOf(address)", [USER], "uint")
    # agentRegistry() retry via fast_rpc race
    out["agentRegistry_retry_race"] = vcall("agentRegistry()", None, "addr")
    # agentRegistry() via direct curl (distinguish revert from transport failure)
    data = "0x" + sel("agentRegistry()")
    dc = direct_curl_call(ADDR, data)
    if "result" in dc:
        dc["decoded"] = dec_addr(dc["result"])
        dc["exact_match"] = (dc["decoded"] or "").lower() == REGISTRY.lower()
        # a 0x result (empty) means the call returned nothing -> function absent/revert
        dc["empty_return"] = dc["result"] in ("0x", "0x" + "0" * 64)
    out["agentRegistry_direct_curl"] = dc
    # REGISTRY() via direct curl as cross-check
    data2 = "0x" + sel("REGISTRY()")
    dc2 = direct_curl_call(ADDR, data2)
    if "result" in dc2:
        dc2["decoded"] = dec_addr(dc2["result"])
        dc2["exact_match"] = (dc2["decoded"] or "").lower() == REGISTRY.lower()
    out["REGISTRY_direct_curl"] = dc2
    json.dump(out, open(f"{BASE}/backfill-triage-132433882-132436704-followup.json", "w"), indent=1)
    print(json.dumps(out, indent=1))
    print("WROTE backfill-triage-132433882-132436704-followup.json")

if __name__ == "__main__":
    main()
