#!/usr/bin/env python3
"""Deep-check follow-up for triage-backfill-131897549-131899548.
Read-only. No preview/mint/claim/approve/sign/swap.
"""
import json, sys, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EPS = ["https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed3.bnbchain.org/"]
USER_PAD = USER[2:].lower().rjust(64, "0")
ONE_PAD = "0000000000000000000000000000000000000000000000000000000000000001"

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def eth_call(to, data, timeout=10):
    last = None
    for ep in EPS:
        try:
            return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], timeout, retries=0)
        except Exception as e:
            last = e
    raise last

def call_ok(to, data):
    try:
        r = eth_call(to, data)
        if isinstance(r, str) and r.startswith("0x") and len(r) >= 66:
            return r
        return None
    except Exception:
        return None

def u256(h):
    try:
        return int(h[-64:], 16)
    except Exception:
        return None

def addr_of(h):
    try:
        return "0x" + h[-40:]
    except Exception:
        return None

def abi_curl(a):
    url = f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"
    p = subprocess.run(["curl", "-s", "--max-time", "15", "-H", "User-Agent: curl", url],
                       capture_output=True, text=True, timeout=20)
    return json.loads(p.stdout).get("abi")

def sig_of(fn):
    ins = ",".join(i["type"] for i in fn.get("inputs", []))
    return f"{fn['name']}({ins})"

def main():
    out = {}
    # ---- FOD Agent ----
    fod = "0xA3d24EE16b6b912192724598Da55C7909bBB97e8"
    abi = abi_curl(fod)
    fns = {f["name"]: f for f in abi if f.get("type") == "function"}
    print("FOD functions with inputs:")
    for n, f in sorted(fns.items()):
        print("  ", sig_of(f), "->", [o["type"] for o in f.get("outputs", [])])
    r = {}
    for name in ["freeQuota", "costOf", "paidPrice", "mintOpen", "agentGateOn", "maxPerWallet", "remainingFree"]:
        f = fns.get(name)
        if not f:
            continue
        sig = sig_of(f)
        n_in = len(f.get("inputs", []))
        data = None
        if n_in == 0:
            data = sel(sig)
        elif n_in == 1 and f["inputs"][0]["type"] == "address":
            data = sel(sig) + USER_PAD
        elif n_in == 2 and f["inputs"][0]["type"] == "address":
            data = sel(sig) + USER_PAD + ONE_PAD
        elif n_in == 1 and f["inputs"][0]["type"] == "uint256":
            data = sel(sig) + ONE_PAD
        if data:
            rr = call_ok(fod, data)
            r[name] = u256(rr) if rr is not None else None
            print(f"FOD {name}: {r[name]}")
    # mintedBy(user) -> uint256 count?
    f = fns.get("mintedBy")
    if f:
        rr = call_ok(fod, sel(sig_of(f)) + USER_PAD)
        r["mintedBy(user)"] = u256(rr) if rr is not None else None
        print("FOD mintedBy(user):", r["mintedBy(user)"])
    out["FOD"] = r
    # ---- template agents x3 ----
    for label, a in [("Nebula Ape", "0x79720611065DF9Fc810399DC1eeE870b3A8AD3fC"),
                     ("Digital Soul", "0x0b9EBce92bF2b549DF960205637cE1f7dee83495"),
                     ("Shadow Yeti", "0xA193Ea677a39D4F04bB770555fe6954e0e00C02C")]:
        abi = abi_curl(a)
        fns = {f["name"]: f for f in abi if f.get("type") == "function"}
        rr = {}
        print(f"{label} functions: quote sig =", sig_of(fns["quote"]) if "quote" in fns else None,
              "| AGENT_REGISTRY:", "AGENT_REGISTRY" in fns, "| spotsLeft:", "spotsLeft" in fns)
        for name in ["AGENT_REGISTRY", "spotsLeft", "PRICE", "MAX_SUPPLY", "MAX_PER_WALLET"]:
            f = fns.get(name)
            if not f:
                continue
            d = sel(sig_of(f))
            v = call_ok(a, d)
            rr[name] = addr_of(v) if name == "AGENT_REGISTRY" and v else (u256(v) if v else None)
            print(f"  {label} {name}: {rr[name]}")
        # quote with its real signature
        f = fns.get("quote")
        if f:
            sig = sig_of(f)
            n_in = len(f.get("inputs", []))
            data = None
            if n_in == 1 and f["inputs"][0]["type"] == "address":
                data = sel(sig) + USER_PAD
            elif n_in == 2 and f["inputs"][0]["type"] == "address":
                data = sel(sig) + USER_PAD + ONE_PAD
            elif n_in == 1 and f["inputs"][0]["type"] == "uint256":
                data = sel(sig) + ONE_PAD
            elif n_in == 0:
                data = sel(sig)
            if data:
                v = call_ok(a, data)
                rr["quote"] = u256(v) if v is not None else None
                print(f"  {label} quote: {rr['quote']}")
        f = fns.get("mintedBy")
        if f:
            v = call_ok(a, sel(sig_of(f)) + USER_PAD)
            rr["mintedBy(user)"] = u256(v) if v is not None else None
            print(f"  {label} mintedBy(user): {rr['mintedBy(user)']}")
        out[label] = rr
    json.dump(out, open(f"{BASE}/triage-deepcheck-131897549-131899548.json", "w"), indent=1)
    print("DEEPCHECK_DONE")

if __name__ == "__main__":
    main()
