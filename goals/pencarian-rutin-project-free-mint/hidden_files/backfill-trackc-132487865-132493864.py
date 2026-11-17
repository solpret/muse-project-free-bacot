#!/usr/bin/env python3
"""Track-C 5c shape-check, backfill run 132487865-132493864 (2026-11-09 ~10:1x WIB).
Read-only: Sourcify ABI via curl for the 20 NEW mc>=10 ERC20 candidates
(157 unique mc>=10 this run, 127 already checked, 30 new, cap 20/run).
S1/S2 logic identical to hot-leg-shapecheck.py. Writes
backfill-trackc-132487865-132493864.json; caller records checked addresses
in track-c-scan-checked.json. No preview/mint/sign.
"""
import json, subprocess

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
CANDS = [
    ("0x7bbf060fdc5734f55442f8abc25460da0beb001d", 94),
    ("0x5e24810732a06008d4f756673920847643b10fa8", 33),
    ("0xb615d61e6c951dba3a895afe493f0d3dbfbb5a8a", 26),
    ("0xd259cbf8c028412c337336db8bef8cd49dfa403d", 25),
    ("0x5d16c4c20d7c7e3c0de5b405e16ae4fbb6b451e6", 25),
    ("0x643d58cf4af8f5fa32139981d85b8629802bcd5e", 25),
    ("0x83e444f7fb386e7ac1a8eedf0a305d8630a8b7ce", 24),
    ("0x5f06e539e022273e8f6d5d5823813af8c37bac52", 22),
    ("0x1130e0910502792f4714db4a5055c16b7296257b", 22),
    ("0x097ff90fce52f4f0e1f41d6f8c799db9cd67099f", 22),
    ("0xc7bc4798d9e6f052d0daec99708bde75e996b485", 22),
    ("0xe6113aadf04940e8d024c9e81b4cccdd4666e8b2", 21),
    ("0x95ce07ae742206e5ccdfa15b1465e45703347940", 20),
    ("0xa4401e5b69e637c1034cab3c7258c1ccbcf55d5f", 19),
    ("0x146dd38cc31ea6f499921e06b753c76c615867d6", 19),
    ("0xa74696ce4d2877ca4d7e7fe02d8f027e350c2c0d", 18),
    ("0xdd2945ca349925d12a75fa8095a4503abc4368b2", 18),
    ("0x8c6aa8459b7fc5def1bf03643f5aa602120a8e57", 16),
    ("0x9d3419ea0154a532df44fc9e60aa71452cd45648", 16),
    ("0xc9eade786d5f69a9b1b0079c5a7380d073e58c79", 16),
]

def fetch(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        r = subprocess.run(["curl", "-s", "-m", "30", url],
                           capture_output=True, text=True, timeout=40)
        meta = json.loads(r.stdout)
        abi = meta.get("abi") or []
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "match": meta.get("match"), "functions": sorted(names),
                "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token}
    except Exception as ex:
        return {"address": addr, "match": None, "error": f"{type(ex).__name__}: {str(ex)[:150]}"}

out = []
for addr, mc in CANDS:
    o = fetch(addr)
    o["mint_count"] = mc
    out.append(o)
    print(json.dumps(o))

base = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
json.dump(out, open(f"{base}/backfill-trackc-132487865-132493864.json", "w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
