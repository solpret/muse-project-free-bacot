#!/usr/bin/env python3
"""Retry read-only verification for backfill window 132401212-132404141 triage.
Only re-calls eth_calls that failed on TRANSPORT in the first triage pass
(fast_rpc race 'all endpoints failed'), using a second transport (urllib
direct to public BSC dataseeds). No chunk re-scan, no preview/mint/sign.
Targets:
- MiChan 0x669c...: agentRegistry() exact check + generic free-view probes
- Pressure 0xD61a...: agentRegistry(), FREE_POOL(), freeRemaining(),
  freeOf(user,1), quote(user,1), MAX_SUPPLY()
- Aiuki 0xEd93...: agentRegistry(), remaining(), quoteBNB/nextPrice (ABI arity),
  agentTokenOf(user), slotOf(user)
- Delveria Gear 0xFD63... + 0x9421...: owner() retry (returned decode-null)
Writes backfill-triage-132401212-132404141-retry.json
"""
import json, subprocess, time, urllib.request
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = [
    "https://bsc-dataseed.binance.org",
    "https://bsc-dataseed1.bnbchain.org",
    "https://bsc-dataseed2.bnbchain.org",
    "https://bsc-dataseed1.defibit.io",
    "https://1rpc.io/bnb",
]
MICHAN = "0x669cb75f51b5D23F4B42fC1522b653d7B88e608d"
PRESSURE = "0xD61aF26aD1D8D9903436455e665d38167AcCCbEc"
AIUKI = "0xEd934652815f98CB9FAcc6Ce0511f01A25694741"
DELVERIA = "0xFD63eB16714e1A1c45cF467243131D89Bb8e0B70"
C9421 = "0x9421A58DFc41C4f5E7942B8B4777837d641106E3"

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a.lower()[2:]

def enc_uint(n):
    return format(int(n), "064x")

def call(to, data):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": to, "data": data}, "latest"]}).encode()
    last_err = None
    for url in RPCS:
        try:
            req = urllib.request.Request(url, data=payload,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as r:
                j = json.load(r)
            if "error" in j:
                return {"error": str(j["error"])[:150]}
            return {"result": j["result"]}
        except Exception as e:
            last_err = f"{type(e).__name__}: {str(e)[:100]}"
    return {"error": f"all endpoints failed; last: {last_err}"}

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

def vcall(to, sig, args=None, decode="uint"):
    data = "0x" + sel(sig)
    for a in (args or []):
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            data += enc_addr(a)
        else:
            data += enc_uint(a)
    r = call(to, data)
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

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        r = subprocess.run(["curl", "-s", "-m", "25", "-A",
                            "free-bacot-backfill-triage/1.0", url],
                           capture_output=True, text=True, timeout=40)
        d = json.loads(r.stdout)
        abi = d.get("abi")
        if abi is None and isinstance(d.get("stdJson"), dict):
            abi = d["stdJson"].get("abi")
        return abi
    except Exception as e:
        return None

def main():
    out = {}
    # MiChan: agentRegistry exact + generic probes (no ABI: not_verified)
    m = {}
    m["agentRegistry"] = vcall(MICHAN, "agentRegistry()", None, "addr")
    m["agentRegistry_exact_match"] = (m["agentRegistry"].get("value") == REGISTRY.lower())
    for sig, dec in [("name()", "str"), ("symbol()", "str"), ("totalSupply()", "uint"),
                     ("mintOpen()", "bool"), ("price()", "uint"), ("freeLeft()", "uint"),
                     ("freeMinted()", "uint"), ("freeSupply()", "uint"),
                     ("FREE_SLOTS()", "uint"), ("FREE_SUPPLY()", "uint"),
                     ("MAX_SUPPLY()", "uint")]:
        fn = sig.split("(")[0]
        r = vcall(MICHAN, sig, None, dec)
        m[fn] = r
    m["freeClaimed(user)"] = vcall(MICHAN, "freeClaimed(address)", [USER], "uint")
    m["freeOf(user,1)"] = vcall(MICHAN, "freeOf(address,uint256)", [USER, 1], "uint")
    m["costOf(user,1)"] = vcall(MICHAN, "costOf(address,uint256)", [USER, 1], "uint")
    m["quote(user,1)"] = vcall(MICHAN, "quote(address,uint256)", [USER, 1], "uint")
    out["MiChan"] = m
    # Pressure
    p = {}
    p["agentRegistry"] = vcall(PRESSURE, "agentRegistry()", None, "addr")
    p["agentRegistry_exact_match"] = (p["agentRegistry"].get("value") == REGISTRY.lower())
    for sig, dec in [("FREE_POOL()", "uint"), ("freeRemaining()", "uint"),
                     ("MAX_SUPPLY()", "uint"), ("freeMintCount()", "uint"),
                     ("paidMinted()", "uint"), ("tierPrice(uint256)", "uint")]:
        fn = sig.split("(")[0]
        args = [1] if "tierPrice" in sig else None
        p[fn] = vcall(PRESSURE, sig, args, dec)
    p["freeOf(user,1)"] = vcall(PRESSURE, "freeOf(address,uint256)", [USER, 1], "uint")
    p["costOf(user,1)"] = vcall(PRESSURE, "costOf(address,uint256)", [USER, 1], "uint")
    p["quote(user,1)"] = vcall(PRESSURE, "quote(address,uint256)", [USER, 1], "uint")
    out["Pressure"] = p
    # Aiuki: inspect ABI for quoteBNB/nextPrice arity first
    a = {}
    abi = fetch_abi(AIUKI)
    fns = {}
    if abi:
        for e in abi:
            if isinstance(e, dict) and e.get("type") == "function":
                fns[e["name"]] = e
    a["agentRegistry"] = vcall(AIUKI, "agentRegistry()", None, "addr")
    a["agentRegistry_exact_match"] = (a["agentRegistry"].get("value") == REGISTRY.lower())
    a["remaining"] = vcall(AIUKI, "remaining()", None, "uint")
    a["TOTAL_SLOTS"] = vcall(AIUKI, "TOTAL_SLOTS()", None, "uint")
    a["totalMinted"] = vcall(AIUKI, "totalMinted()", None, "uint")
    a["mintedBy(user)"] = vcall(AIUKI, "mintedBy(address)", [USER], "uint")
    if "agentTokenOf" in fns:
        n_in = len(fns["agentTokenOf"].get("inputs", []))
        a["agentTokenOf(user)"] = vcall(AIUKI, "agentTokenOf(address)", [USER], "uint") if n_in == 1 else {"fn": "agentTokenOf", "note": f"arity {n_in}, skipped"}
    if "slotOf" in fns:
        n_in = len(fns["slotOf"].get("inputs", []))
        a["slotOf(user)"] = vcall(AIUKI, "slotOf(address)", [USER], "uint") if n_in == 1 else {"fn": "slotOf", "note": f"arity {n_in}, skipped"}
    if "quoteBNB" in fns:
        n_in = len(fns["quoteBNB"].get("inputs", []))
        if n_in == 0:
            a["quoteBNB()"] = vcall(AIUKI, "quoteBNB()", None, "uint")
        elif n_in == 1:
            a["quoteBNB(user)"] = vcall(AIUKI, "quoteBNB(address)", [USER], "uint")
        else:
            a["quoteBNB"] = {"fn": "quoteBNB", "note": f"arity {n_in}, skipped"}
    if "nextPrice" in fns:
        n_in = len(fns["nextPrice"].get("inputs", []))
        a["nextPrice()"] = vcall(AIUKI, "nextPrice()", None, "uint") if n_in == 0 else {"fn": "nextPrice", "note": f"arity {n_in}, skipped"}
    out["Aiuki"] = a
    # owner() retry for the two decode-null contracts
    out["Delveria_owner_retry"] = vcall(DELVERIA, "owner()", None, "addr")
    out["C9421_owner_retry"] = vcall(C9421, "owner()", None, "addr")
    json.dump(out, open(f"{BASE}/backfill-triage-132401212-132404141-retry.json", "w"), indent=1)
    print(json.dumps(out, indent=1))
    print("WROTE backfill-triage-132401212-132404141-retry.json")

if __name__ == "__main__":
    main()
