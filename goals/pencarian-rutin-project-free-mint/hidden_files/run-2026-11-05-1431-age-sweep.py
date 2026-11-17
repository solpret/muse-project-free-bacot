import json, re, datetime, urllib.request
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-05-1431"
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
now=datetime.datetime(2026,11,5,15,15,tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
cands={}
for k,v in snap.get("contracts",{}).items():
    st=str(v.get("status",""))
    if "minted-by-user" in st: continue
    if "promotion-discarded" in st: continue
    if "sold-out" in st: continue
    if st.startswith("excluded"): continue
    ln=(v.get("launchNote","") or "")
    fm=None; src=None
    m=re.search(r'first Transfer-from-zero at block \d+, (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) WIB', ln)
    if m: fm=m.group(1); src="first-mint"
    if not fm:
        m2=re.search(r'first mint.*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) WIB', ln)
        if m2: fm=m2.group(1); src="first-mint"
    if not fm and v.get("startTimeWib"):
        fm=v["startTimeWib"][:19].replace("T"," "); src="startTimeWib"
    if not fm: continue
    try: fmdt=datetime.datetime.strptime(fm, '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
    except Exception: continue
    age=(now-fmdt).total_seconds()/3600
    if age>48:
        cands[k]={"address":v.get("address"),"status":st,"firstMintWib":fm,"src":src,"age_h":round(age,1),
                  "lastFree":v.get("freeClaimed"),"lastCap":v.get("FREE_SUPPLY") or v.get("FREE_CAP"),
                  "lastSupply":v.get("totalSupply")}
print("CANDIDATES:", len(cands))
for k,v in cands.items(): print(" ", k, v["address"], "age", v["age_h"], "lastFree", v["lastFree"], "/", v["lastCap"], "supply", v["lastSupply"])
json.dump(cands, open(f"{BASE}/run-{TS}-age-candidates.json","w"), indent=1)

# fresh reads: totalSupply, freeMinted, freeClaimed(no-arg), FREE_SUPPLY, FREE_CAP, MAX_SUPPLY, balanceOf(user)
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def raw(to,data):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=12) as r: out=json.load(r)
            if "error" in out: return {"error":str(out["error"])[:60]}
            v=out["result"]
            if not v or v=="0x": return None
            try: return int(v,16)
            except Exception: return v
        except Exception: continue
    return {"error":"rpc-fail"}
def block():
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r: return int(json.load(r)["result"],16)
        except Exception: continue
    return None
res={"block":block()}
for k,v in cands.items():
    a=v["address"]; d={}
    for fn in ["totalSupply()","totalMinted()","freeMinted()","freeClaimed()","FREE_SUPPLY()","FREE_CAP()","MAX_SUPPLY()"]:
        d[fn]=raw(a,sel(fn))
    d["balanceOf(user)"]=raw(a,sel("balanceOf(address)")+enc(USER))
    res[k]=d
    print(k, d)
json.dump(res, open(f"{BASE}/run-{TS}-age-reads.json","w"), indent=1)
print("DONE block", res["block"])
