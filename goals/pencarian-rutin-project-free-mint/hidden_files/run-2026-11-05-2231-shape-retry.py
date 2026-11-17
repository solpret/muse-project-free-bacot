import json, subprocess
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeSupply"]
out=json.load(open(f"{BASE}/run-2026-11-05-2231-sourcify-shape.json"))
failed=[a for a,v in out.items() if "error" in v]
print("retrying", len(failed))
for a in failed:
    ok=False
    for attempt in range(3):
        r=subprocess.run(["curl","-s","--max-time","30",f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"],capture_output=True,text=True)
        try:
            d=json.loads(r.stdout)
            abi=d.get("abi",[])
            if not abi and "error" not in str(d)[:50] and not d.get("abi"): raise ValueError("empty abi")
            fns=sorted({f.get("name") for f in abi if isinstance(f,dict) and f.get("name")})
            src=json.dumps(d).lower()
            mint=any(n in fns for n in ["mint","mintFree","mintShare","buyShare","claimFree"])
            quote=any(n in fns for n in ["quote","cost","getQuote","price"])
            free=[n for n in FREE_VIEWS if n in fns]
            agent=(REG in src) or any(n in fns for n in ["AGENT_REGISTRY","agentRegistry","AgentGate","agentGate"])
            token=any(n in fns for n in ["name","symbol","decimals","totalSupply"]) and "transfer" in fns
            nft=any(n in fns for n in ["tokenURI","ownerOf","totalSupply"]) and "transferFrom" in fns
            s1=mint and quote and bool(free) and agent
            s2=token and ("mintFree" in fns) and bool(free) and agent
            out[a]={"verifiedAt":out[a]["verifiedAt"],"abi_functions":fns,"S1":s1,"S2":s2,"mint":mint,"quote":quote,"free":free,"agent":agent,"token":token,"nft":nft}
            print(a,"S1",s1,"S2",s2,"mint",mint,"quote",quote,"free",free,"agent",agent,"fns",len(fns))
            ok=True; break
        except Exception as e:
            print(a,"attempt",attempt+1,"fail",str(e)[:100])
    if not ok:
        out[a]["error_retry"]="3 attempts failed via curl"
        print(a,"STILL FAILED")
json.dump(out, open(f"{BASE}/run-2026-11-05-2231-sourcify-shape.json","w"), indent=1)
print("saved")
