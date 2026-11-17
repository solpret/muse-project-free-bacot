#!/usr/bin/env python3
"""Track-C 5c shape-check, backfill run 132489815-132495814 (2026-11-09 ~10:16 WIB).
Read-only: Sourcify ABI via curl for the 20 NEW mc>=10 ERC20 candidates
(187 unique mc>=10 this run, 158 already checked, 29 new, cap 20/run; 9 deferred).
S1/S2 logic identical to hot-leg-shapecheck.py. Writes
backfill-trackc-132489815-132495814.json; caller records checked addresses
in track-c-scan-checked.json. No preview/mint/sign.
"""
import json, subprocess

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
CANDS = [
    ("0xFE6CfCB9FFb6Ce9177b743cf0441C69841e7B93C", 31),
    ("0xCAd83216725E1629C9BE55002B12FA0Bf936F0Af", 28),
    ("0xD9b64A3efDe3eBB8C5B919a6638963759C98c7b2", 23),
    ("0xAeF687360C0021Bc1e0B5BdB6CAba0161894B5c4", 21),
    ("0x8E0D7E3DeEef2d54A684d4D16818D5027D1863B7", 20),
    ("0x285074B480260d5138CC57d3f282BFdc7831d830", 19),
    ("0xF2401de2fc6f626385443aF2bfB84BFc65b21313", 17),
    ("0xD8c280642cD88f8a2a89f6a230D266fbCF0bBE3F", 17),
    ("0x51c26EC12Db0437b195764ce1E15f6A84db2a674", 17),
    ("0x551779CA72B40f021B4Ff4FDdFb096d111EB0365", 16),
    ("0x103d1aAB760FC116F43Dd48690Dc73F6cb5a5542", 16),
    ("0x60220BE6b82F9f8724D723babcB268B607Eba3b3", 16),
    ("0x88C93ecAe195094a28B06b22B8ECBbeeC595EdF4", 16),
    ("0xdEb1ea07C3196EE00e4D6f7A1D4003bf450c2DE7", 16),
    ("0x0fe4fEc9B39dca945Fc9A8F2080Ec74Dcea3BCCa", 16),
    ("0x87CcAD3aAC3BD06a405c97Eda87f50ff60071859", 16),
    ("0xb83fB1c35843b223A3DD1242990f8a325d8b1D5e", 16),
    ("0x05DFa3dc0baE116FCCDac395be375e0B9867f336", 16),
    ("0x62E794d08E5d71E594863Cd3960C52c527a55B78", 16),
    ("0x9074880a4549ffd92778A9ed42c323E908620165", 16),
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
json.dump(out, open(f"{base}/backfill-trackc-132489815-132495814.json", "w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
