#!/usr/bin/env python3
"""Hot-leg Sourcify shape-check (S1/S2), read-only. First run 2026-11-01 23:09 WIB."""
import json, sys, urllib.request, concurrent.futures
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
FEED = ['0x79B5D86089a29a65faC3278572f00C8FADc361fb', '0xaE3eb0525BF6CCFf4A914Ec65537CE6E7F2CDc79', '0xa7b012332a6dc244Ac7195241023042092929314', '0x3CF77C2DCB0dD4Be465add021B773A63024CF37a', '0x0634c6793530f928E1D4DB45DCab3fB5aeBa0A15', '0x3C720836b1A9b7053D6171b058cDeFf7dF5F1B47', '0x44660A280A87037ABE12D3D42758370e3Bac46EA', '0xB67FE0553386B73Cb6fcCE04DaF07bD164503782', '0x60cFc77B7D41171672bC985639f759C891e8dC06', '0x2197ce9C2Ff890436d497dE817d1B552ffEB7AFe', '0x40e730B47E5d4883E14B77C0D7f762e8cf57790f', '0x2C215262635E66c798c5a1Ba4411fA9F06852bDD', '0x672c1dF4F7121DaCBD3504995441C47d2fAbCdDC', '0x11fa2C4b71EcE40f242992a08C4ACC6C23c99Ca0', '0x787b522d48084A83b8B1b0C206aA4A12B1FD1cc2', '0x0AC5591d1B980C7bE16861d722E59E21E2624868', '0xA74bEF84304D8838db798faE96fb873dd46fB4C1', '0xF54E80a86FCF71Fa2F86Eb9bC2f21f36B94961b7', '0x754bFf286120eCFc5c63273C264edBa5C05102F2', '0xC16E0e5e060d253D34c81AA6606c37B9317f6909', '0x8DF15F3043E71A76A31DAE0a18B7146820A42EF8', '0xf281623B4f2CEA04F67ffAfB3bbC77D1b4BbebB5', '0x84Df1048626c942D930aA0Fb7ab3a4724B45eB82', '0x206902bc6e14051DFa01319257d29220Ea665bc4', '0x221B327c30949b859F65b1d734B96fFe1daFcDba', '0x54360f5a8626109BFcce7F7911f41604423DAF18', '0x1ed3BF35e4DA25b1289C27ddbD82f0A38DDCee8b', '0x8362e6a5F38427d8d719EA47f08890784F6023DC', '0x2Df4Ef534cbBe1a8F647e24D0f8C75ECe74D8288', '0xf7dF61f4e75D38085487A69cB8687b771CE2F004']
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
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-01-2331-sourcify-shape.json","w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
