#!/usr/bin/env python3
import json, urllib.request
B="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
scan=json.load(open(B+"onchain-scan-2026-11-02-1301.json"))
checked=json.load(open(B+"track-c-scan-checked.json"))
done=set(a.lower() for a in checked.get("checked",[]))
cands=sorted(scan["erc20_mint_contracts_list"], key=lambda x: x.get("mint_count",0), reverse=True)
todo=[]
for c in cands:
    if c["mint_count"]>=10 and c["address"].lower() not in done:
        todo.append(c)
    if len(todo)>=20: break
print("todo:", len(todo))
FREE=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
out=[]
for c in todo:
    addr=c["address"]
    try:
        with urllib.request.urlopen(f"https://sourcify.dev/server/v2/contracts/56/{addr}", timeout=15) as r:
            d=json.load(r)
        std=d.get("stdJson",{}) if isinstance(d,dict) else {}
        abi=std.get("output",{}).get("abi",[]) if std else []
        names=[f.get("name","") for f in abi if f.get("type")=="function"]
        src=json.dumps(abi)
        has_mint=any(n in ("mint","mintFree") for n in names)
        has_quote=any(n in ("quote","cost","costFor","getCost") for n in names)
        has_free=any(f in names for f in FREE)
        has_agent=("0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F" in src) or any(n in ("agentRegistry","AGENT_ID","AgentGate","registry") for n in names)
        s1=has_mint and has_quote and has_free and has_agent
        is_token=any(n in names for n in ("name","symbol","decimals","totalSupply"))
        s2=is_token and ("mintFree" in names) and has_free and has_agent
        out.append({"address":addr,"mint_count":c["mint_count"],"distinct_minters":c["distinct_minters"],"sourcify":"verified","S1":s1,"S2":s2,"has_mint":has_mint,"has_quote":has_quote,"has_free":has_free,"has_agent":has_agent,"names_sample":names[:40]})
        print(addr, "mints", c["mint_count"], "S1", s1, "S2", s2, "mint", has_mint, "quote", has_quote, "free", has_free, "agent", has_agent)
    except Exception as e:
        out.append({"address":addr,"mint_count":c["mint_count"],"sourcify":"ERROR","error":f"{type(e).__name__}: {str(e)[:120]}"})
        print(addr, "ERR", e)
    checked["checked"].append(addr)
checked["note"]="Run 13:01 WIB: +20 checked (batch from scan 131187511-131189510, mint_count>=10 sorted desc); 0 strict S1/S2 passes in this batch (see run log)."
json.dump(checked, open(B+"track-c-scan-checked.json","w"), indent=1)
json.dump(out, open(B+"run-2026-11-02-1301-trackc5c.json","w"), indent=1)
