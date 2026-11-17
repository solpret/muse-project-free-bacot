#!/usr/bin/env python3
"""Track-C 5c shape-check, backfill run 132512515-132518514 (2026-11-09 ~13:0x WIB).
Read-only: Sourcify ABI via curl for the 20 NEW mc>=10 ERC20 candidates
(1711 unique, 158 mc>=10, 131 already checked, 27 new, cap 20/run; 7 deferred).
S1/S2 logic identical to hot-leg-shapecheck.py. Writes
backfill-trackc-132512515-132518514.json; caller records checked addresses
in track-c-scan-checked.json. No preview/mint/sign.
NOTE: driver exit 2 PARSIAL (chunk 2 rc=2, 1 failed sub-chunk Transfer
132512515-132512564, 50 blok hole, retry otomatis run berikut); watermark
132508814 -> 132512514 (prefix kontigu). ERC20 lists complete for the 3
chunks as scanned (chunk 2 partial at enrichment level only in the sense
of the failed 50-block sub-chunk).
"""
import json, subprocess

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
CANDS = [['0x539d40b2cbd4f69bae891882fdc791fa91ed6324', 84], ['0x3e7cacf68d9c3044ff44a239515a2550d47e0418', 80], ['0x8b0ea7f6049c957b2d81ea3c6f0dde3c019ef21b', 69], ['0xe206825345a44b32700526f627d64f8db2b4fb86', 69], ['0xceecf1f6b0d747981c3db974cbcfd536b4b0a8fc', 63], ['0xd86846fcd0d71777ec161fb58b39a175b356648d', 56], ['0x318a47d4003377cc032ef9ce9e420c4ee9862403', 28], ['0x1403e36374366a93b19c5efd6cee5a527480e8cb', 28], ['0xb35131148f5e19e8ef2e327a4a9f1c69716a73bc', 27], ['0x5b1cb0a976479a00b048c9606ab1ca80ab44c8bb', 25], ['0x55c49ab66ee97f30a8dcbe6c47f6af0a2a3f7bc1', 22], ['0xa2286250e505004d5881c67615b80774e31213b2', 21], ['0x255e98f1f3e5f4b461c2313937b9c2b7c52a7f8e', 20], ['0x3182a85030a012f6690e5f0cbb7a39d3e859d716', 20], ['0xdc7575276962e2c221908c8ff840133a68f22f79', 19], ['0xf69279591d583ce7b3ab5bbf4e60923560474b24', 19], ['0x7c5519df0b15b55c126c5de00de4a82b22e668ab', 18], ['0x12995a2bf53c1ea96a5a5a37bbf530baf2da6a62', 18], ['0xf3820ab4c85583a3cee4a92944cc1641135b3be3', 18], ['0xefc6c710ab5fc3fbeecf237c6e2c28695ecc5a39', 17]]

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
json.dump(out, open(f"{base}/backfill-trackc-132512515-132518514.json", "w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
