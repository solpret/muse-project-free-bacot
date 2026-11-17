#!/usr/bin/env python3
"""Track-C 5c shape-check, backfill run 132508815-132514814 (2026-11-09 ~13:0x WIB).
Read-only: Sourcify ABI via curl for the 20 NEW mc>=10 ERC20 candidates
(1711 unique, 158 mc>=10, 131 already checked, 27 new, cap 20/run; 7 deferred).
S1/S2 logic identical to hot-leg-shapecheck.py. Writes
backfill-trackc-132508815-132514814.json; caller records checked addresses
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
CANDS = [['0x02e83468be1a98444f0c2a86c0e762be7063f9df', 168], ['0x80d20a4658a4ed114ac2c30b8751f8397679c209', 142], ['0xaba61515e3e42b08337f555113a3946e1f89960b', 94], ['0x26b5f1ab2efe3c814ef628c89935113970cea355', 73], ['0x601a2ceb3a534e1c304e4c4e45b6da37aca4da72', 31], ['0x0cf7c268277217723e3b584e21c45c49edcd5903', 27], ['0xabc6f60870afb9093b14cfc009344040754eed43', 23], ['0xeeb2835296e16b614980949d9773ffe175d3011d', 23], ['0x112b29e7e31c005076761048aca2dd4054f5577a', 21], ['0x3662a16de4cecbeb71dc29126a37838c32c0ee07', 21], ['0x1b18d63803482fa5b9c84ac02deff9b473e38c91', 20], ['0x5ed1d2725279d5587191e6d90f6e63c0a0ff9768', 20], ['0xa3c3a9c94081b83f679fe0f0df7ad5fa81e3ccbd', 19], ['0x0df0f72ecada0d77527eb1f4093270b99a70cddb', 19], ['0x7a9e886b5ca32ea6f47518a910c1276de5445ea5', 17], ['0xb6b876eaf47bdf37ba61acd7f6592922ac51ce2c', 17], ['0xc9b228388a5de027d9706d7135886fea28b88efc', 17], ['0xbb911015f518ed16e7dde945711c6330e355a6f9', 17], ['0x1498bc28a1a5d14a1b6b08404c4f8f5b12013dcd', 16], ['0x6145e1aa2caf338fc11709c03a6b61c19aa24373', 16]]

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
json.dump(out, open(f"{base}/backfill-trackc-132508815-132514814.json", "w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
