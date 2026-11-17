import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
scan=json.load(open(f"{BASE}/onchain-scan-2026-11-07-1801.json"))
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
seen=json.load(open(f"{BASE}/onchain-scan-seen.json"))
snap_addrs={v.get("address","").lower() for v in snap["contracts"].values()}
seen_addrs=set()
if isinstance(seen,dict):
    seen_addrs={a.lower() for a in seen.get("contracts",{}).keys()}
    if not seen_addrs and "addresses" in seen: seen_addrs={a.lower() for a in seen["addresses"]}
REG="0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
first_seen=[]
known=[]
for c in scan["contracts"]:
    a=c.get("address","").lower()
    if a==REG.lower(): continue
    if a not in snap_addrs and a not in seen_addrs:
        first_seen.append(c)
    else:
        known.append(c)
print(f"enriched={len(scan['contracts'])} first_seen_new={len(first_seen)} known={len(known)}")
for c in first_seen:
    print("FIRST-SEEN:", c.get("address"), c.get("name"), c.get("symbol"), "registry=", c.get("registry"), "sourcify=", c.get("sourcify"), "mint_count=", c.get("mint_count"))
# ERC20 5c triage: mint_count>=10, sort desc, skip already checked
checked=json.load(open(f"{BASE}/track-c-scan-checked.json"))
checked_set={a.lower() for a in (checked if isinstance(checked,list) else checked.get("checked",[]))}
erc20=scan.get("erc20_mint_contracts_list",[])
cand=[e for e in erc20 if (e.get("mint_count",0)>=10 and e.get("address","").lower() not in checked_set)]
cand.sort(key=lambda e: e.get("mint_count",0), reverse=True)
print(f"erc20 total={len(erc20)} mint>=10 new-to-check={len(cand)} (cap 20)")
for e in cand[:20]:
    print("ERC20-CAND:", e.get("address"), "mint_count=", e.get("mint_count"))
json.dump({"first_seen":first_seen,"erc20_candidates":cand[:20],"enriched":len(scan["contracts"]),"window":[scan["from_block"],scan["to_block"]],"partial":True},
          open(f"{BASE}/run-2026-11-07-1801-triage-scan.json","w"), indent=1)
