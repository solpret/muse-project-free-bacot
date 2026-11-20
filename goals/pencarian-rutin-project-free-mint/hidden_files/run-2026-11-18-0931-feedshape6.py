#!/usr/bin/env python3
"""Shape-check 6 new Sourcify contracts since hot-leg 0924 (verifiedAt 02:26:25Z -> 02:34:38Z). Read-only."""
import json, subprocess
FREE_VIEWS={"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
ADDRS=["0x55B467b8023fA6D6e64534Db6e2e3Ca2c896E0bA","0xF18F337Ea12Af5D7BA8d8BA9600535ea652c4F1B","0xf6C0775E1E82E7F227Ae1a683D5494820EB4E2c1","0xf37d229eb2E78EC98acf51F92c1525C8bb02AFeb","0x3797CFFF0F00E1b07121EfF67dE3A732507aD861","0x49dF5277A1677613281C01caBf9795d2507faee4"]
def get(url,timeout=25):
    r=subprocess.run(["curl","-s","-L","--max-time",str(timeout),url],capture_output=True,timeout=timeout+5)
    return json.loads(r.stdout.decode())
out={}
for ADDR in ADDRS:
    try:
        meta=get(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi")
        abi=meta.get("abi") or []
        names={e["name"] for e in abi if e.get("type")=="function"}
        has_mint=any(n.lower().startswith("mint") for n in names)
        has_quote=bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views=sorted(names & FREE_VIEWS)
        agent_ref=bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        is_token=bool(names & {"name","symbol","decimals","totalSupply"})
        s1=has_mint and has_quote and bool(free_views) and agent_ref
        mintfree="mintFree" in names
        s2=is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        out[ADDR]={"verifiedAt":meta.get("verifiedAt"),"match":meta.get("match"),"n_fns":len(names),"S1":s1,"S2":s2,"has_mint":has_mint,"has_quote":has_quote,"free_views":free_views,"agent_ref":agent_ref,"is_token":is_token,"fns":sorted(names)}
        print(ADDR, "S1",s1,"S2",s2,"fns",len(names),"free",free_views,"agent",agent_ref,"mint",has_mint,"quote",has_quote)
    except Exception as e:
        out[ADDR]={"error":f"{type(e).__name__}: {str(e)[:150]}"}
        print(ADDR,"ERROR",e)
json.dump(out,open("run-2026-11-18-0931-feedshape.json","w"),indent=1)
