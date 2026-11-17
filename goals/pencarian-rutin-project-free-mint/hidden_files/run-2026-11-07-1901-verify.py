#!/usr/bin/env python3
"""Lean re-verify run 1901 first-seen (5 contracts, same template):
Sourcify ABI via curl fallback (urllib IncompleteRead flaky), then
on-chain free/quote/registry/owner views with exact signatures from ABI.
Read-only. Writes run-2026-11-07-1901-verify.json."""
import json, subprocess, sys, hashlib, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/", "https://bsc.publicnode.com/"]
ADDRS = ["0x3C7D328027Ca0068e7CD8709D64D9161Bc35de93",
         "0x7bc0B487feBCBB1caA781148bf05A8Cd72D02Ec5",
         "0x69Dc6eB49E4cA2508C09778a211F8D6DFECE0049",
         "0xB4B5320e22B187d8C3dFFF0c03AF1675B4a76519",
         "0x6D318F9e4147b7A9B1eC8196BA1799592e5ae44a"]
NAMES = {ADDRS[0]: "BRAINROT ZOO/ROT", ADDRS[1]: "HOG ORBIT/HOG",
         ADDRS[2]: "RESET 2016/R2016", ADDRS[3]: "NO NUT NOV/NNN",
         ADDRS[4]: "LUCKY LIFE/LUCKY"}

def sel(sig):
    return "0x" + hashlib.sha3_256(sig.encode()).hexdigest()[:8]

def call(to, data):
    for ep in EPS:
        try:
            return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 10, retries=0)
        except Exception as e:
            last = str(e)[:80]
    return {"error": last}

def abi_via_curl(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        out = subprocess.run(["curl", "-sS", "--max-time", "25", url],
                             capture_output=True, text=True, timeout=30)
        d = json.loads(out.stdout)
        abi = d.get("abi") or []
        return abi
    except Exception as e:
        return {"error": str(e)[:120]}

out = {}
for a in ADDRS:
    v = {"name": NAMES[a]}
    abi = abi_via_curl(a)
    if isinstance(abi, dict):
        v["abi_error"] = abi.get("error")
        abi = []
    fns = {}
    for f in abi:
        if isinstance(f, dict) and f.get("type") == "function":
            sig = f["name"] + "(" + ",".join(i.get("type", "") for i in f.get("inputs", [])) + ")"
            fns[f["name"]] = sig
    v["fn_count"] = len(fns)
    v["fns"] = sorted(fns.values())
    # registry views
    for name in ("AGENT_REGISTRY", "AGENT_ID_REGISTRY", "agentRegistry", "AGENT_ID", "registry"):
        if name in fns:
            r = call(a, sel(fns[name]))
            if isinstance(r, str) and len(r) >= 66:
                val = "0x" + r[-40:]
                v["registry_view"] = {"fn": name, "value": val, "match": val.lower() == REG.lower()}
            else:
                v["registry_view"] = {"fn": name, "raw": str(r)[:100]}
            break
    # free views with correct arity
    free = {}
    for name, sig in fns.items():
        if name.lower().startswith("free") or name in ("PRICE", "price", "MAX_SUPPLY", "maxSupply", "totalMinted", "mintOpen", "spotsLeft"):
            data = sel(sig)
            if "(address)" in sig:
                data += USER[2:].lower().rjust(64, "0")
            elif "(uint256)" in sig:
                data += "01".rjust(64, "0")
            r = call(a, data)
            if isinstance(r, str):
                try:
                    free[name] = int(r, 16)
                except Exception:
                    free[name] = r[:66]
            else:
                free[name] = str(r)[:100]
    v["free_views"] = free
    # quote variants
    for name, sig in fns.items():
        if name == "quote":
            for args in ([USER], [1], [USER, 1]):
                data = sel(sig)
                for x in args:
                    if isinstance(x, str):
                        data += x[2:].lower().rjust(64, "0")
                    else:
                        data += format(x, "064x")
                r = call(a, data)
                free[f"quote({','.join(str(x)[:6] for x in args)})"] = (int(r, 16) if isinstance(r, str) else str(r)[:100])
    # owner
    if "owner" in fns:
        r = call(a, sel(fns["owner"]))
        v["owner"] = ("0x" + r[-40:]) if isinstance(r, str) and len(r) >= 66 else str(r)[:100]
    out[a] = v
    print(a, NAMES[a], "fns:", v["fn_count"], "registry:", v.get("registry_view"), "free:", json.dumps(free), "owner:", v.get("owner"), flush=True)

json.dump(out, open(f"{BASE}/run-2026-11-07-1901-verify.json", "w"), indent=1)
print("VERIFY DONE", flush=True)
