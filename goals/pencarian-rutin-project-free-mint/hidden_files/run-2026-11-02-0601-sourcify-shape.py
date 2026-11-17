import urllib.request, json
FREE = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCount"]
REG = ["registry","agentRegistry","AGENT_ID","agentId","agentGate","AgentGate","isAgent","hasAgentId","requireAgentId"]
new = ["0x8103162b878eD7158D54825fcd1305b4D5D6D3dC","0x072154bD66Ac9D65Fd29fabCEe1ca1dD52342c5c","0xBaE532f8dd506706907b1Fb4eE9A0532b86b7777","0x455Af58Ff30690244cFF9e670e733470B30E908c","0x840Ec126bc401bC09482F4A9667da6BD43b60f7F","0x2C92207D1949D3Ed0cFB55C3Bc9e9F543064a656","0xc87e521Ec78cf6cE0373b45eb9B449AbcB6c30D2","0x09deCa240b1e6b69C0D13c1f286ece922521DFA6","0xb822d4e11480d3c6d3a750298504A8a82Fb0ea80","0x0B2cFfEAc8Fd6a29Eeb1636a151F5C90b12cB70E","0x7dD18E2B8eD92a1A039e0B20caD40d0a8be7F88a","0x2b0de6cf7b9Cec56bcab24fEfCE46D14217b1262","0x0b32Ab148B57043fBc6F37d762449112387Fa662","0x42a045b454dAA7cCEaDf9e13763503ACFbF3b200","0x282DDb7C556cb361454062E4dE548751FFCa81D4","0xE994F4C0A2ACb99Bb363DBA01639feD7998B4502","0x7BE77828f913EB61AE6BFef2660F9CEB92248A66","0xA849792ED89A309831df3D0279118E7F98460680","0x7D33Aee186c972239d3D8e98cafa925EF76dAfdf","0x8e0A36dC5E60Fd8f618853EC9cad4153a43344C8","0xAEF612B5517D0A4C8140c9Fb54453F9956ad99bC","0x3E09117A69Cccc7986e05194E41067Dc73bAbc30","0xcDB8A67575a7154199ec836C5f4e15a0fF26d41b","0xbe4470e0A26980aeB69A62e16B4FcB9dAA3cF6ea","0xEd3CD63bb9dBe4C0E9D82FBEC4Cb4728082579d8","0xC1AdDeBab730c28E7Aa980eE11037023d6881327"]
out={}
for a in new:
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r: d=json.load(r)
        abi=d.get("stdJson",{}).get("abi") or d.get("abi") or []
        fns=[f.get("name") for f in abi if f.get("type")=="function"]
        has_mint=any(n in fns for n in ("mint","mintFree","mintPaid","freeMint","claimFree","mintWithVoucher","freeMintWithVoucher")) or any("mint" in (n or "").lower() for n in fns)
        fv=[n for n in fns if n in FREE]
        rg=[n for n in fns if n in REG]
        has_quote="quote" in fns or "costFor" in fns
        is_token=("name" in fns and "symbol" in fns and "decimals" in fns and "totalSupply" in fns)
        out[a]={"verified":True,"functions":fns,"has_mint":has_mint,"free_views":fv,"registry_refs":rg,"has_quote":has_quote,"is_token":is_token,
                "agent_shape":bool(has_mint and fv and rg),"sale_S1":bool(has_mint and has_quote and fv and rg),
                "sale_S2":bool(is_token and ("mintFree" in fns) and fv and rg)}
        print(a, "agent" if out[a]["agent_shape"] else "-", "S1" if out[a]["sale_S1"] else "", "S2" if out[a]["sale_S2"] else "", fns[:40])
    except Exception as e:
        out[a]={"verified":False,"error":f"{type(e).__name__}: {str(e)[:120]}"}
        print(a, "UNVERIFIED", out[a]["error"])
json.dump(out, open("run-2026-11-02-0601-sourcify-shape.json","w"), indent=1)
