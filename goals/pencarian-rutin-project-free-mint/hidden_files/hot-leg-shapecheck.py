#!/usr/bin/env python3
"""Hot-leg Sourcify shape-check (S1/S2), read-only. First run 2026-11-01 23:09 WIB."""
import json, sys, urllib.request, concurrent.futures
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
FEED = ["0xf7dF61f4e75D38085487A69cB8687b771CE2F004","0xDF0AAD437eB45bB3b47ac93514e04c3893279Ea1",
"0x178Fae448b2E1F370041B2d8258724c54B0b154E","0xF583841811F05E92473A71F69A490A4Ccbe4fa66",
"0xd77E3AD745D98922c4dB989fB9b07E841a1f90f8","0x6C01A53077eF1BE10c71d7B067a6608f6ADC1882",
"0x8eaDeeA8d28021D240802Da59F7Fd89c44c216B1","0x398d480932b5b8755285C8f732812731120431F1",
"0xd7a4DCca73094B1065e39F251a283EC61d049Aab","0x6B7D2A0f05CaBe1c6818f82bF27EE3e866E79eA4",
"0xBe532cdd09683645499d4fd6205B78b124F02abE","0xa33698457fe05F88F69FDB20c099F9ecadFe47BF",
"0x64ADD1bc8972c0D64574d5ee365eBFc632D95b8f","0x9231a519609848d2f84f15f3606847edD9868441",
"0xd92431A20c34f308E0253b35f8FaDB3917aEa8fa","0xF76c840cEE20f6F78677022F4B1A7Edf8EF02Ec2",
"0xEd99445d72787Adb627cD8588586984DF548CD2F","0x3EE9aF0D9290F2D352f77fD550C1bD79cC03B66F",
"0x2e2002d707cdA33Ac2Be6A49Def062f04cbA3d96","0x19147255e7FE00D3e3f3A64fB2348eb389526794"]
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
def fetch(addr):
    for kind in ("v2abi",):
        url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
        try:
            req = urllib.request.Request(url, headers={"User-Agent":"hot-leg/1.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                meta = json.loads(r.read().decode())
            abi = meta.get("abi", [])
            fns = {}
            for e in abi:
                if e.get("type") == "function":
                    fns.setdefault(e["name"], []).append(e)
            names = set(fns)
            has_mint = any(n.lower().startswith("mint") for n in names)
            has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
            free_views = sorted(names & set(FREE_VIEWS))
            agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
            s1 = has_mint and has_quote and bool(free_views) and agent_ref
            is_token = bool(names & {"name","symbol","decimals","totalSupply"})
            mintfree = "mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
            s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
            return {"address": addr, "match": kind, "functions": sorted(names),
                    "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                    "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token}
        except Exception as ex:
            last = f"{type(ex).__name__}: {str(ex)[:120]}"
    return {"address": addr, "match": None, "error": last}
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    out = list(ex.map(fetch, FEED))
for o in out:
    print(json.dumps(o))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-01-2309-sourcify.json","w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
