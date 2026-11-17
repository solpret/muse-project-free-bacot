import json, time, urllib.request
def sourcify_abi(addr):
    url=f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r: d=json.load(r)
        abi=d.get("abi")
        if isinstance(abi,list) and abi:
            return {"verified":True,"fns":sorted({f.get("name") for f in abi if isinstance(f,dict) and f.get("type")=="function" and f.get("name")})}
        return {"verified":False,"note":str(d)[:200]}
    except Exception as e:
        return {"verified":False,"error":str(e)}
FREE=["freeClaimed","freeMinted","freeLeft","freeSupply","freeFor","freeUsed","freeAvailable","freeSharesRemaining","freeSharePoolExhausted","freeSharesClaimed","freeOf","freeCount","freeRemaining"]
AGENT=["agentRegistry","AGENT_ID_REGISTRY","AGENT_REGISTRY","registry","agentIds","agentTokenIdOf"]
out={}
for a in ["0xac05a1CdB85157da5e92E73865446a302340ceb6","0xB0b84D294e0C75A6abe60171b70edEb2EFd14A1B"]:
    s=sourcify_abi(a); fns=s.get("fns",[])
    shape={"address":a,"verified":s.get("verified"),
      "free":[f for f in fns if any(x.lower() in f.lower() for x in FREE)],
      "mint":[f for f in fns if "mint" in f.lower() or "claim" in f.lower()],
      "quote":[f for f in fns if f.lower() in ("quote","costof","priceof","price","cost")],
      "agent":[f for f in fns if any(x.lower() in f.lower() for x in AGENT)],
      "token":[f for f in fns if f.lower() in ("name","symbol","decimals","totalsupply")],
      "all_fns":fns}
    shape["S1"]=bool(shape["mint"] and shape["quote"] and shape["free"] and shape["agent"])
    shape["S2"]=bool(shape["token"] and len(shape["token"])>=4 and shape["mint"] and shape["free"] and shape["agent"])
    out[a]=shape
    print(a, "verified:", s.get("verified"), "S1:", shape["S1"], "S2:", shape["S2"], "free:", shape["free"], "mint:", shape["mint"][:6], "quote:", shape["quote"], "agent:", shape["agent"], "err:", s.get("error",""), flush=True)
    time.sleep(1)
json.dump(out, open("run-2026-11-09-0231-5c.json","w"), indent=1)
# record into checked file
chk=json.load(open("track-c-scan-checked.json"))
for a,v in out.items():
    chk[a]={"checked_wib":"2026-11-09 02:31 run","run":"2026-11-09-0231","S1":v["S1"],"S2":v["S2"],"verdict":"checked-not-sale-shape" if not (v["S1"] or v["S2"]) else "SALE-SHAPE-HIT"}
json.dump(chk, open("track-c-scan-checked.json","w"), indent=1)
print("checked total now:", len(chk))
print("DONE")
