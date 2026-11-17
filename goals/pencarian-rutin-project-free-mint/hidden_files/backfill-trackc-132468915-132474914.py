#!/usr/bin/env python3
"""Track-C 5c shape-check, backfill run 132468915-132474914 (2026-11-09 ~08:3x WIB).
Read-only: Sourcify ABI via curl for the 10 NEW mc>=10 ERC20 candidates.
S1/S2 logic identical to hot-leg-shapecheck.py. Writes
backfill-trackc-132468915-132474914.json; caller records checked addresses
in track-c-scan-checked.json. No preview/mint/sign.
"""
import json, subprocess

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
CANDS = [
    ("0xfa410665b9c1d3b3215ca8c18bca0164866a4a88", 35),
    ("0x5f0bb0ce23f08029fb47c58141a8fcfe3dbec600", 33),
    ("0xe98ed499fd3d85c3e73f08dc85b2ce0e521b8a0e", 33),
    ("0xef7611b5fedf882ec75a7dba0ebbfa56aaae26aa", 31),
    ("0x834748748dec8bc212175de1e4c2a67469cc68fe", 30),
    ("0x70542d4f513d60faee422c385c0974f970cbaf04", 23),
    ("0x93bf08d2936aefe0cd2ceba8f76cb566fdf9e1c9", 21),
    ("0x860c42405627906601384f729a99e022c271b74d", 16),
    ("0x0555e30da8f98308edb960aa94c0db47230d2b9c", 12),
    ("0x56a7ddc4e848ebf43845854205ad71d5d5f72d3d", 11),
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
json.dump(out, open(f"{base}/backfill-trackc-132468915-132474914.json", "w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
