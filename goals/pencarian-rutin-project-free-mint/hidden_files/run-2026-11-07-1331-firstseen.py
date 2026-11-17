import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
d=json.load(open(f"{BASE}/onchain-scan-2026-11-07-1331.json"))
seen=json.load(open(f"{BASE}/onchain-scan-seen.json"))
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
print("seen top keys:", list(seen.keys()) if isinstance(seen,dict) else type(seen))
seen_addrs=set()
if isinstance(seen,dict):
    for k,v in seen.items():
        if isinstance(v,dict): seen_addrs|={a.lower() for a in v.keys()}
        elif isinstance(v,list): seen_addrs|={a.lower() for a in v}
print("seen_addrs:", len(seen_addrs))
snap_addrs={v.get("address","").lower() for v in snap["contracts"].values()}
for _v in snap.get("track_c",{}).values():
    if isinstance(_v,dict):
        for _k in ("sale","token","address"):
            if _v.get(_k): snap_addrs.add(_v[_k].lower())
print("snap_addrs:", len(snap_addrs))
REG="0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
fs=[]
for c in d.get("contracts",[]):
    a=c["address"].lower()
    if a not in seen_addrs and a not in snap_addrs:
        fs.append(c)
print("FIRST-SEEN:", len(fs))
for c in fs:
    print(json.dumps(c))
json.dump({"first_seen": fs, "window": [d["from_block"], d["to_block"]]}, open(f"{BASE}/run-2026-11-07-1331-firstseen.json","w"), indent=1)
# agent-shaped among first-seen
for c in fs:
    shaped = c.get("registry_bytes_hit") or bool(c.get("free_shaped")) or bool(c.get("mint_funcs"))
    print("SHAPED?" , c["address"], c.get("name"), "registry=", c.get("registry_bytes_hit"), "free=", c.get("free_shaped"), "mint_funcs=", c.get("mint_funcs"), "sourcify=", c.get("sourcify"))
