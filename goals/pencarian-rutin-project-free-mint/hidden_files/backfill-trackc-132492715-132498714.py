#!/usr/bin/env python3
"""Track-C 5c shape-check, backfill run 132492715-132498714 (2026-11-09 ~12:00 WIB).
Read-only: Sourcify ABI via curl for the 20 NEW mc>=10 ERC20 candidates
(989 unique, 235 mc>=10, 208 already checked, 27 new, cap 20/run; 7 deferred).
S1/S2 logic identical to hot-leg-shapecheck.py. Writes
backfill-trackc-132492715-132498714.json; caller records checked addresses
in track-c-scan-checked.json. No preview/mint/sign.
NOTE: run itself SUCCEEDED (driver exit 0, 3/3 chunks, watermark 132498714);
ERC20 lists are complete (3/3 chunks, 0 failed sub-chunks).
"""
import json, subprocess

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
CANDS = [['0xe77835f548D6c5eCe1fA5D0c73beb3bD81b06217', 123], ['0xB5eF0Da58adA22B5534126143487A448d206E7B3', 102], ['0x66517A13946795349108196e268Ef7f606DAa3F2', 93], ['0xa84EA20a667B3b1859aB9a9984FF5F03D8688aE2', 36], ['0x3d7393b4541F726d5f93DE3c995E8f0B55a5128A', 26], ['0xDa0e9E9ee52A8a78b661def121Be9e2c94BCfAc7', 23], ['0xB0e3F58424a099d1DD48B161bA94882A892F2Cf7', 20], ['0x7C7958a7a2186D8ebb54f934fc26Ebf612a372F7', 20], ['0xAC926978d363483C709865786E74C57F6690A2D1', 18], ['0xF061D52f6D429fC43769969779F64aE36d21C5E3', 18], ['0x6beEd6E6797D6B7f997B0E46CdDc6c04Ad368E80', 17], ['0x1b1358B2005A0C3ed8f3F3C5296E9eBE41E69F83', 17], ['0xE40B0DCF7A211CD020D3E43BaEF9314018941181', 16], ['0x581482109C23c6ba17Bf71B4BCd7608C8FeCA1AE', 16], ['0x689F6158466d9d40CC0CBb469c06B2686A101FA3', 14], ['0x71553938630a079a22eAA63ADF7FB014Da026F93', 14], ['0x4dEf7655E1b097E3D6417Ec71e0D320e1485D2cF', 14], ['0x963c6b28C7c50EB4b10441439f56AB2340D3f30C', 13], ['0xd354bb09E83a0949F0FDB1D660f1B364EFeAC3Db', 12], ['0x04f93E2EAE707CBdea686Dfe50e2d9d7CDdB892B', 12]]

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
json.dump(out, open(f"{base}/backfill-trackc-132492715-132498714.json", "w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
