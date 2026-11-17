#!/usr/bin/env python3
"""Track-C 5c shape-check, backfill run 132474915-132480914 (2026-11-09 ~08:3x WIB).
Read-only: Sourcify ABI via curl for the 10 NEW mc>=10 ERC20 candidates.
S1/S2 logic identical to hot-leg-shapecheck.py. Writes
backfill-trackc-132474915-132480914.json; caller records checked addresses
in track-c-scan-checked.json. No preview/mint/sign.
"""
import json, subprocess

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
CANDS = [
    ("0xD90b4fFfd3d461B9D88BdcF35d9A270a5c2B2C42", 205),
    ("0xDEEDEB7D54A1a0b842Ac3dd9B6e8e197c7F90d25", 64),
    ("0xffB8c30b293ef9fd45D8c65Ac47579d5e1668415", 46),
    ("0x148E78E762501b44f0ecdc1B95bf94fb4Bbe9845", 42),
    ("0xB60686862c6957dAC64C0E715998Af2065999a2d", 40),
    ("0x55470c36D2D936f7E746409Bac076e7DAC7f88bc", 40),
    ("0x629FD71126f3D1a9cD1804270DF00950458ae8CF", 38),
    ("0x2Fb73906e7D1c6f13741C7802e57E0169a09c641", 38),
    ("0xF28f22559AD2f768519219f2EC5dC40a7D1Fe371", 37),
    ("0x1298c354b9c0fc84aF2E96a53F0898ba568Bb7b4", 37),
    ("0x7678A40D7E390b1600d6cb783B90C6B4aeCC9ED3", 37),
    ("0x4BdbC85D040E7B80B5aA8ACF78d60bFf3a54FE7c", 37),
    ("0xd6334021d021A5F78F0f0EBbeE43BF788F15b2DE", 36),
    ("0x99A5744db33964612E7377676d6e96c12b8BC059", 32),
    ("0xDaebB1080aF839e8f30E4dAB83Df67aF9930c39E", 31),
    ("0x7F7eF70fcc6036815B89Ee0b6Bf12EC5b326834c", 30),
    ("0xFb65b8cEB78Ef369b37764505BC3Dd2004515Fe8", 29),
    ("0x13eBfe3a4F9d2D279aB48b0563ae9D66A36Ee628", 27),
    ("0x5b2F8232129A5a7D2993535E4E861E7172E72842", 26),
    ("0x8CEB0391e0D709Cb39182b3aafFaF8F2Ef7EaaE0", 24),
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
json.dump(out, open(f"{base}/backfill-trackc-132474915-132480914.json", "w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
