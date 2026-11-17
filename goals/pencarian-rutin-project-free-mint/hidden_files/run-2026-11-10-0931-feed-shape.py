#!/usr/bin/env python3
"""Run 0931 Sourcify feed shape-check (S1/S2), read-only. Adapted from hot-leg-shapecheck.py; timeout 30s, 5 workers."""
import json, urllib.request, concurrent.futures
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
FEED = ["0x94F8F6F4Da3Dfd0549DE5c3422A4FfB41Aba673e","0x136AC70EE85529ef961ccC7076de77e4e929D6dF","0x09e664F447D854b0C413f63E4D6e78070B411AeB","0x4F8cbCD1F336D873CAEC5e479ecc689624107037","0xC828186ea59599048c27B23D564eCb6A3e5Bf142","0xD35ca43DBEC645226466d7b37B275394e9c67F19","0x67C60B78eEa11a96ECD6215498547BA771Ff4fe8","0x32Ef9524771fAc05585Af142702e4D7a6b5F7AD9","0x144876A2Fbf5438339AFFD699bCBE16b611C63DA","0x31E0A9Df03bC0EE4aB42a44dB3f7D5f64c4A04D4","0xd9e364D3055827E0077bD7375224C0E2E5fD8746","0x485be9daA4620FcEE4e2bAEd7cc85Ea57Acb44b0","0x07683F749e1e6ddA9059456109c2D161ce3c0f41","0x5FEF88E9E7eb0899f3F70EF16d50A08E0fd8bd09","0x3479bfA6e0f681A3763961b95759f477DE7Cc9a9","0x94792e859ffeDbAa0b789E438Ed27FF1b92601A2","0x43B2Ede2217ACd3de6542F7C4baFEb488cbbC7a2","0x6b149377b0d68c7cF09DDa6B6467861D997C9646","0xA2Be5520ef3FE334fCB68E649787636b3ff84A65","0xe3f83002413c029BA7F194a878b8C36B03d3d8a0"]
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
def fetch(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"free-bacot/0931"})
        with urllib.request.urlopen(req, timeout=30) as r:
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
        return {"address": addr, "functions": sorted(names), "S1": s1, "S2": s2,
                "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:150]}"}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    out = list(ex.map(fetch, FEED))
for o in out:
    print(json.dumps(o), flush=True)
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-10-0931-feed-shape.json","w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
print("ERRORS:", [(o["address"], o.get("error")) for o in out if o.get("error")])
