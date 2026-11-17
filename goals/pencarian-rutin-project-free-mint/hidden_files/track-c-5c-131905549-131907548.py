#!/usr/bin/env python3
"""Track-C 5c shape-check for backfill chunk 131905549-131907548 (read-only).
Checks the 3 new ERC20 mint_count>=10 addresses not yet in track-c-scan-checked.json.
S1 = mint + quote/cost + free-share view + registry/AgentGate.
S2 = single-contract token+sale: name/symbol/decimals/totalSupply + mintFree() + free views + agentRegistry.
"""
import json, subprocess, sys

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TARGETS = [
    ("0x2B30618F7dfbFf759145a158eb4F4E2a956f6C89", 116, 116, 131907150),
    ("0x98A2C738d8C76aF8A90127ec312b3A4C4947C600", 15, 2, 131907026),
    ("0xBB7c5c37aE8DEF9a92C53da4Ba66D8F379E71378", 10, 1, 131907336),
]

def abi_curl(a):
    url = f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"
    p = subprocess.run(["curl", "-s", "--max-time", "15", "-H", "User-Agent: curl", url],
                       capture_output=True, text=True, timeout=20)
    try:
        return json.loads(p.stdout).get("abi")
    except Exception:
        return None

def main():
    out = {}
    for addr, mc, dm, fb in TARGETS:
        abi = abi_curl(addr)
        if not isinstance(abi, list):
            print(f"{addr} mint_count={mc}: sourcify NO-ABI (not verified / 404)")
            out[addr] = {"mint_count": mc, "sourcify": "no-abi", "shape": "none"}
            continue
        fns = sorted({f.get("name", "") for f in abi if f.get("type") == "function"})
        has = lambda n: n in fns
        free_views = [f for f in fns if "free" in f.lower() and not f.lower().startswith("freeze")]
        s1 = (has("mint") and (has("quote") or has("cost") or has("costOf"))
              and bool(free_views) and (has("agentRegistry") or has("AGENT_REGISTRY") or has("agentGate") or has("AgentGate")))
        s2 = (has("mintFree") and bool(free_views) and (has("agentRegistry") or has("AGENT_REGISTRY"))
              and has("name") and has("symbol") and has("decimals") and has("totalSupply"))
        shape = "S1" if s1 else ("S2" if s2 else "none")
        print(f"{addr} mint_count={mc} minters={dm} first_block={fb}: sourcify verified, {len(fns)} fns, shape={shape}")
        print(f"  fns: {fns}")
        print(f"  free-ish: {free_views}")
        out[addr] = {"mint_count": mc, "distinct_minters": dm, "first_block": fb,
                     "sourcify": "verified", "functions": fns, "free_views": free_views, "shape": shape}
    json.dump(out, open(f"{BASE}/track-c-5c-131905549-131907548.json", "w"), indent=1)
    print("saved track-c-5c-131905549-131907548.json")

if __name__ == "__main__":
    main()
