#!/usr/bin/env python3
"""Run 0401 track-C ERC20 backlog shape-check (max 20, here 14). Read-only."""
import json, urllib.request
todo=json.load(open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0401-trackc-erc20-todo.json'))
FREE_VIEWS=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCount"]
out={}
for e in todo:
    C=e['address']
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{C}?fields=abi", headers={"User-Agent":"free-mint-search/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r: meta=json.loads(r.read().decode())
        fns=sorted({x["name"] for x in meta.get("abi",[]) if x.get("type")=="function"})
        has_mint=any(f in fns for f in ["mint","mintFree","freeMint","claimFree"])
        has_quote=any(f in fns for f in ["quote","costFor","cost"])
        fv=[f for f in FREE_VIEWS if f in fns]
        has_reg=any(f in fns for f in ["agentRegistry","registry","AGENT_ID","agentId","agentIdRegistry"])
        is_token=all(f in fns for f in ["name","symbol","decimals","totalSupply"])
        s1=bool(has_mint and has_quote and fv and has_reg)
        s2=bool(is_token and "mintFree" in fns and fv and has_reg)
        out[C]={"functions":fns,"S1":s1,"S2":s2,"has_mint":has_mint,"has_quote":has_quote,"free_views":fv,"has_reg":has_reg,"window":e}
        print(C, "S1", s1, "S2", s2, "mint", has_mint, "quote", has_quote, "fv", fv, "reg", has_reg, "mints", e['mint_count'])
    except Exception as ex:
        out[C]={"abi_error":f"{type(ex).__name__}: {str(ex)[:120]}", "window":e}
        print(C, "ABI FAIL", out[C]["abi_error"])
json.dump(out, open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0401-trackc-erc20.json','w'), indent=1)
