import json, subprocess, time
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
ADDRS = ["0x23fFE8CBe0aFb410e5F312E27f8af8382dcc96Eb",  # Boltbook EN new
         "0x96d095CF44a2C4b458e3EAa6fecadc86885CA5C3",
         "0xBB8eb154F4fa5cF72B7733a4093d5cA9F8fEc2Dc",
         "0x2437dF59913c1471C927A27E8312090632d8705A",
         "0x0Cd189974655659CD69b2d8D7AEd81ca3ab32C88"]
def fetch(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        r = subprocess.run(["curl","-sL","--max-time","30",url],capture_output=True,text=True,timeout=35)
        meta = json.loads(r.stdout)
        abi = meta.get("abi",[])
        fns={}
        for e in abi:
            if e.get("type")=="function": fns.setdefault(e["name"],[]).append(e)
        names=set(fns); lnames={n.lower() for n in names}
        has_mint=any(n.lower().startswith("mint") for n in names)
        has_quote=bool(lnames & {"quote","cost","getquote","mintcost","price","getprice","mintprice"})
        free_views=sorted(names & set(FREE_VIEWS))
        agent_ref=bool(lnames & {"agentid","agentregistry","registry","getagentid","agentgate","agentidregistry"})
        is_token=bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree="mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
        s1=has_mint and has_quote and bool(free_views) and agent_ref
        s2=is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        is_nft=bool(names & {"tokenURI","ownerOf","safeTransferFrom"}) or "uri" in names
        early=is_nft and (agent_ref or bool(names & {"freeMint","mintFree","claimFree","mint"}))
        return {"address":addr,"S1":s1,"S2":s2,"early_shape":early,"has_mint":has_mint,"has_quote":has_quote,
                "free_views":free_views,"agent_ref":agent_ref,"is_token":is_token,"is_nft":is_nft,"fn_count":len(names)}
    except Exception as ex:
        return {"address":addr,"error":f"{type(ex).__name__}: {str(ex)[:120]}"}
out=[fetch(a) for a in ADDRS]
print(json.dumps(out,indent=1))
json.dump(out,open("run-2026-11-11-2349-shape-retry.json","w"),indent=1)
