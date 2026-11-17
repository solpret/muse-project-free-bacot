#!/usr/bin/env python3
import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
scan=json.load(open(BASE+"onchain-scan-2026-11-02-1831.json"))
checked=json.load(open(BASE+"track-c-scan-checked.json"))
ck=set(checked["checked"]) if isinstance(checked,dict) else set(checked)
lst=scan.get("erc20_mint_contracts_list",[])
print("erc20 list entries:", len(lst))
cands=[]
for e in lst:
    if isinstance(e,dict):
        addr=e.get("address") or e.get("contract"); mc=e.get("mint_count",0)
    else: continue
    if mc>=10 and addr and addr.lower() not in {c.lower() for c in ck}:
        cands.append((mc,addr))
cands.sort(reverse=True)
print(">=10 and unchecked:", len(cands))
for mc,a in cands[:20]: print(mc,a)
json.dump([{"mint_count":mc,"address":a} for mc,a in cands[:20]], open(BASE+"run-2026-11-02-1831-trackc-erc20-todo.json","w"), indent=1)
print("scan keys:", list(scan.keys())[:20])
print("nft contracts:", len(scan.get("nft_contracts_list",[])) if "nft_contracts_list" in scan else scan.get("nft_contracts"))
