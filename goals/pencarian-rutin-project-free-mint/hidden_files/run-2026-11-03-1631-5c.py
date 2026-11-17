import json, subprocess, concurrent.futures
H="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
d=json.load(open(H+'onchain-scan-2026-11-03-1631.json'))
checked=json.load(open(H+'track-c-scan-checked.json'))['checked']
chk={k.lower() for k in checked.keys()}
lst=sorted(d['erc20_mint_contracts_list'], key=lambda x: x.get('mint_count',0), reverse=True)
ge10=[c for c in lst if c.get('mint_count',0)>=10]
new=[c for c in ge10 if c['address'].lower() not in chk]
print('ge10',len(ge10),'unchecked',len(new),'todo20',len(new[:20]))
FREE_VIEWS={"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
def shape(addr):
    try:
        out=subprocess.run(["curl","-sL","--max-time","20",f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],capture_output=True,text=True).stdout
        meta=json.loads(out); abi=meta.get("abi",[])
        fns={}
        for e in abi:
            if e.get("type")=="function": fns.setdefault(e["name"],[]).append(e)
        names=set(fns)
        has_mint=any(n.lower().startswith("mint") for n in names)
        has_quote=bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views=sorted(names & FREE_VIEWS)
        agent_ref=bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate","AGENT_ID","AGENT_ID_REGISTRY","agentIdOf","hasAgentId"})
        is_token=bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree="mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
        s1=has_mint and has_quote and bool(free_views) and agent_ref
        s2=is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address":addr,"functions":sorted(names),"S1":s1,"S2":s2,"has_mint":has_mint,"has_quote":has_quote,"free_views":free_views,"agent_ref":agent_ref,"is_token":is_token}
    except Exception as ex:
        return {"address":addr,"error":f"{type(ex).__name__}: {str(ex)[:120]}"}
todo=[c['address'] for c in new[:20]]
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    shapes=list(ex.map(shape,todo))
json.dump({"todo":todo,"shapes":shapes,"ge10":len(ge10),"unchecked":len(new),"dropped":len(new)-len(todo)},open(H+'run-2026-11-03-1631-5c.json','w'),indent=1)
for s in shapes: print(s)
print('PASS', [s['address'] for s in shapes if s.get('S1') or s.get('S2')])
