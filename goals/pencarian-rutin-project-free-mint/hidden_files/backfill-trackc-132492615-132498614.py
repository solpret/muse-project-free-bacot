#!/usr/bin/env python3
"""Track-C 5c shape-check, backfill run 132492615-132498614 (2026-11-09 ~11:00 WIB).
Read-only: Sourcify ABI via curl for the 20 NEW mc>=10 ERC20 candidates
(985 unique, 235 mc>=10, 201 already checked, 34 new, cap 20/run; 14 deferred).
S1/S2 logic identical to hot-leg-shapecheck.py. Writes
backfill-trackc-132492615-132498614.json; caller records checked addresses
in track-c-scan-checked.json. No preview/mint/sign.
"""
import json, subprocess

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
CANDS = [['0x91fc7371d6dE682A1e8CFcB4EB7dA693312A03a4', 39], ['0xAb176F8DefdC1B1B894eF7fFEF2Fb93A35506d76', 34], ['0x44c4B9315aFD9A2648207dD812848C3FcB0434bD', 27], ['0x7451024504D3a3C78b2a4879eE8017036EeA92D1', 27], ['0x50856f04bd5829051af46bf2ce4F332165C3A582', 26], ['0xAc7ABC6dc224Efb018DC256f020504b435f4Ff07', 26], ['0x2590048D0f8c17164eDeA68582CACDb81fd6A866', 26], ['0xe3AE3df52085f8eC47B7F5695B727cF1aec2B8fC', 26], ['0x6e532F4Bbe5c13cdEF36640d8DcD9596Bf9f0786', 25], ['0xE4C3aD5155991682445d68a04a5F7831cfA50093', 22], ['0x95CDA1eB5CA1c9c40A9ba53397622CBB98bCDb8A', 21], ['0x0636830B22c5e234FDb4e6b6A52B71b5e3d5fB48', 20], ['0xfd3390F4DC5E5DE95aC7889Db9EA918d8e9a2FAa', 20], ['0xA9dAc2d091E9cD6Cd15775e8b79BFE0692DF12b7', 20], ['0x991A36744D81421ac3624C960c1fABc90e77325B', 19], ['0x8e71eb7F1d81eEfa5D27B49be94fD8B77e590f53', 18], ['0x3111cF1DDB484717BAf9a126566139a16C7ED0F4', 18], ['0xEB8Ab13B5d7A231B3fF4249C3a87e49Cfc59b0d1', 18], ['0xEb738dC6E381345b7d681364E71e622eFB312930', 18], ['0xDb17592a49b6B2b0965deaD56226eBc816f42492', 18]]

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
json.dump(out, open(f"{base}/backfill-trackc-132492615-132498614.json", "w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
