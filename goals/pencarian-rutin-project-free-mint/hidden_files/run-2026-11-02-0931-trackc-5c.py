import json, urllib.request
B="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
todo=json.load(open(B+"run-2026-11-02-0931-trackc-erc20-todo.json"))[:20]
def get(url):
    return urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=20).read()
out=[]
for c in todo:
    addr=c["address"]
    try:
        d=json.loads(get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"))
        abi=d.get("abi",[])
        names=[f.get("name","") for f in abi if f.get("type")=="function"]
        mint=any("mint" in n.lower() for n in names); quote=any("quote" in n.lower() or "cost" in n.lower() for n in names)
        free=[n for n in names if "free" in n.lower()]
        agent=any("agent" in n.lower() or "registry" in n.lower() for n in names)
        token=any(n.lower() in ("name","symbol","decimals","totalSupply") for n in names)
        s1=mint and quote and bool(free) and agent
        print(addr, c["mint_count"], "S1",s1,"mint",mint,"quote",quote,"free",free,"agent",agent,"token",token,"match",d.get("match"))
        out.append({"address":addr,"mint_count":c["mint_count"],"s1":s1,"mint":mint,"quote":quote,"free":free,"agent":agent,"token":token,"match":d.get("match"),"names":names})
    except Exception as e:
        print(addr, c["mint_count"], "ERR", type(e).__name__, e)
        out.append({"address":addr,"mint_count":c["mint_count"],"error":f"{type(e).__name__}: {e}"})
json.dump(out, open(B+"run-2026-11-02-0931-trackc-5c.json","w"), indent=1)
# record checked
tc=json.load(open(B+"track-c-scan-checked.json"))
checked=tc["checked"]
for o in out:
    if o["address"] not in checked: checked.append(o["address"])
tc["checked"]=checked
json.dump(tc, open(B+"track-c-scan-checked.json","w"), indent=1)
print("checked total now", len(checked))
