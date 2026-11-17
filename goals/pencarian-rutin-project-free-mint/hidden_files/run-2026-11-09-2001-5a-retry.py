import json, subprocess
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
FREE_VIEWS=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","FREE_SLOTS","FREE_SUPPLY"]
def fetch_abi(addr):
    url=f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        out=subprocess.run(["curl","-sL","--max-time","30",url],capture_output=True,text=True,timeout=35).stdout
        d=json.loads(out)
        return d.get("abi")
    except Exception as e:
        return {"_error":repr(e)}
def shape(addr):
    abi=fetch_abi(addr)
    if not isinstance(abi,list):
        return {"address":addr,"error":str(abi)[:200]}
    fns={}
    for f in abi:
        if f.get("type")=="function": fns.setdefault(f.get("name"),[]).append(f)
    names=set(fns)
    has_mint=any(n.lower().startswith("mint") for n in names)
    has_quote=any("quote" in n.lower() or n in ("cost","price","getPrice","mintPrice") for n in names)
    free=[n for n in FREE_VIEWS if n in names]
    src=json.dumps(abi).lower()
    agent=("60b9262456de011f7d15a54cdd8c48baaa8b022f" in src or "agentid" in src or "agentgate" in src or "agentregistry" in src or "registry" in names)
    tokenish=bool({"name","symbol","decimals","totalSupply"} <= names)
    s1=has_mint and has_quote and bool(free) and agent
    s2=tokenish and ("mintFree" in names or "mintfree" in [n.lower() for n in names]) and bool(free) and agent
    return {"address":addr,"S1":s1,"S2":s2,"mint":has_mint,"quote":has_quote,"free":free,"agent":agent,"token":tokenish}
todo=["0x7C2C3BCe712B138bDFf3832CEfCc9fa1F5a2226c","0x7609A4d0Bd6b576ADcCeD6a7F5AB77071431c3d0",
"0x47bE6B8b6345f22B56B44008020ef0543FcBb90D","0x0Fe8d8Fb871F6d949ffe4C3f13D351e1b1ab2E94",
"0xFB5a559886fCCbA6400cC52905ba3AA4658ba0CC","0x9b1559aDc9B9c2Dce8A32957f3024F3393AE5bf3",
"0xDB3B3544d95Cf445E869bF3Bb9a2d1Dfb1d7007F","0x25DB4bdd4d8f2F8A3df7863332A0e0f9cA4786d1",
"0xfd9D6B38fbbED9262cE4537F822a38bF0440ed30","0xf9A710fA71E97b7EfAe4b92c40C57292D8548993",
"0x5dc5148196Ce0563A6aA3A916ca471f73A9C5cc5","0x728095ab0bd71636db5da4e2a6d7f5cc73729fc0",
"0x7a3cd992e6aea95c684d71d1f33511ff1206d9e6","0xec1c5898da3f8ffc5d147a27d5c7d63dcc9f268d"]
out={}
for a in todo:
    s=shape(a); out[a]=s
    print(a,"S1",s.get("S1"),"S2",s.get("S2"),"mint",s.get("mint"),"quote",s.get("quote"),"free",s.get("free"),"agent",s.get("agent"), s.get("error",""), flush=True)
json.dump(out,open(f"{BASE}/run-2026-11-09-2001-5a-retry.json","w"),indent=1)
print("RETRY DONE")
