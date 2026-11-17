"""Run 2201 first-seen dedupe — CORRECT dedupe (lesson run 2131):
seen file has sub-dict `contracts` (11.5k) + top-level 0x keys + known_older_leads.
A contract is first-seen ONLY if absent from ALL of: seen['contracts'],
seen top-level 0x keys, seen['known_older_leads'], snapshot contracts addresses,
snapshot track_c addresses. Read-only; never writes seen/snapshot."""
import json, sys
B="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
scan=json.load(open(B+"onchain-scan-2026-11-08-2301.json"))
snap=json.load(open(B+"onchain-snapshot.json"))
seen=json.load(open(B+"onchain-scan-seen.json"))
known=set()
for k in seen.keys():
    if isinstance(k,str) and k.startswith("0x"): known.add(k.lower())
if isinstance(seen.get("contracts"),dict):
    known |= {k.lower() for k in seen["contracts"].keys()}
if isinstance(seen.get("known_older_leads"),dict):
    known |= {k.lower() for k in seen["known_older_leads"].keys()}
elif isinstance(seen.get("known_older_leads"),list):
    known |= {str(x).lower() for x in seen["known_older_leads"]}
for v in snap.get("contracts",{}).values():
    if isinstance(v,dict) and v.get("address"): known.add(v["address"].lower())
for v in snap.get("track_c",{}).values():
    if isinstance(v,dict):
        for f in ("address","sale","token"):
            if v.get(f): known.add(str(v[f]).lower())
print(f"known set size: {len(known)} (seen contracts sub-dict {len(seen.get('contracts',{}))}, top-level 0x {sum(1 for k in seen if isinstance(k,str) and k.startswith('0x'))}, known_older_leads {len(seen.get('known_older_leads',{})) if isinstance(seen.get('known_older_leads'),dict) else len(seen.get('known_older_leads',[]))})")
print(f"scan window {scan.get('from_block')}-{scan.get('to_block')} head {scan.get('latest_block')} ankr_calls={scan.get('ankr_calls')} errors={scan.get('errors')} partial={scan.get('partial')}")
print(f"scan: {len(scan.get('contracts',[]))} NFT contracts, {scan.get('erc20_mint_contracts')} ERC20-mint")
first=[]
for c in scan.get("contracts",[]):
    a=c.get("address","")
    if a.lower() not in known:
        first.append(c)
print(f"FIRST-SEEN (correct dedupe): {len(first)}")
for c in first:
    print(json.dumps(c))
json.dump({"window":[scan.get("from_block"),scan.get("to_block")],"head":scan.get("latest_block"),
           "ankr_calls":scan.get("ankr_calls"),"errors":scan.get("errors"),
           "nft_contracts":len(scan.get("contracts",[])),"erc20_mint":scan.get("erc20_mint_contracts"),
           "known_set_size":len(known),"first_seen":first},
          open(B+"run-2026-11-08-2301-firstseen.json","w"),indent=1)
print("written run-2026-11-08-2301-firstseen.json")
