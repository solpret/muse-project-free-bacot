import json, re, datetime
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-05-1501"
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
now=datetime.datetime(2026,11,5,15,30,tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
cands={}
for k,v in snap.get("contracts",{}).items():
    st=str(v.get("status",""))
    if "minted-by-user" in st: continue
    if "promotion-discarded" in st: continue
    if "sold-out" in st: continue
    if st.startswith("excluded"): continue
    ln=(v.get("launchNote","") or "")
    fm=None; src=None; snippet=None
    pats=[
        (r'first Transfer-from-zero at block \d+, (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) WIB', "first-mint-WIB"),
        (r'first Transfer-from-zero at block \d+, (\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})\+07:00', "first-mint-T"),
        (r'first mint.*?(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) WIB', "first-mint-WIB"),
        (r'first mint.*?(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})', "first-mint-T"),
        (r'sole Transfer-from-zero at block \d+, (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) WIB', "sole-mint-WIB"),
    ]
    for pat,s in pats:
        m=re.search(pat, ln, re.IGNORECASE)
        if m:
            fm=f"{m.group(1)} {m.group(2)}"; src=s
            snippet=ln[max(0,m.start()-40):m.end()+10]
            break
    if not fm and v.get("startTimeWib"):
        fm=v["startTimeWib"][:19].replace("T"," "); src="startTimeWib"
    if not fm: continue
    try: fmdt=datetime.datetime.strptime(fm, '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
    except Exception: continue
    age=(now-fmdt).total_seconds()/3600
    if age>48:
        cands[k]={"address":v.get("address"),"status":st,"firstMintWib":fm,"src":src,"age_h":round(age,1),
                  "snippet":snippet,
                  "lastFree":v.get("freeClaimed"),"lastCap":v.get("FREE_SUPPLY") or v.get("FREE_CAP"),
                  "lastSupply":v.get("totalSupply")}
print("CANDIDATES:", len(cands))
for k,v in cands.items():
    print(" ", k, v["address"], "age", v["age_h"], "src", v["src"], "lastFree", v["lastFree"], "/", v["lastCap"], "supply", v["lastSupply"])
    print("    snippet:", (v.get("snippet") or "")[:160])
json.dump(cands, open(f"{BASE}/run-{TS}-age-candidates.json","w"), indent=1)
