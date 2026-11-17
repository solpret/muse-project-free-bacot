import json, subprocess
ADDRS=["0x4d416f0D7F0710A5B5BBDB9C9346b60914FeE3AE","0x06ec6a80F8C6924f6cc5b916072528fb58A5a8BF","0xD2bf897B50661f4961ECB049cb875a368d5e3fE5","0x3f964c8ca60A87ab874c5D3aDe87D229093c11CB","0x9537D87889DB55592bA5956a009e960857310e77","0x96c39A5aC2666AAD758C67f79c752752ee571dF2","0x9f9ae311a61a045d0E04794e26aa068DfB16522F","0x32c8920F1803BA368060B6BB0EF65F17370366D6","0x0bC3894CDCE47AbBC3B34E0816C15B195E0AAdbE","0x19993B3Cf15c1055063468EB932F5e335A7526ea","0x46AcB035b5efa87bFC99aF605b85b8d45c4D1F85","0x11AfDc2d736d646421E8df53E9cA6080783B5A5e","0x0E35f73fE749bfE28755D9acbf950b60548d816F","0x04C39B491bb4342fd05822b4C939Fb7d9427B793","0x1BCAA6E08c4e68E8fc9D468152339aB931Ad6cEC","0x47b58721A0e1E0265FAcaEA9Ab79Ba7A6D1aFaD6","0x8D14B3CED5ca9c6272b9e80D93a524da528D79E3","0x625354460BC39aA0a039DA8620a629C6726E4010","0xe17f31D735916854963B272635047dc75D5C6826","0xab3bA230A727897F4A19c1561485ab2660B83b88"]
VERIFIED_AT={"0x4d416f0D7F0710A5B5BBDB9C9346b60914FeE3AE":"2026-11-08T03:53:36Z","0x06ec6a80F8C6924f6cc5b916072528fb58A5a8BF":"2026-11-08T03:53:24Z","0xD2bf897B50661f4961ECB049cb875a368d5e3fE5":"2026-11-08T03:53:09Z","0x3f964c8ca60A87ab874c5D3aDe87D229093c11CB":"2026-11-08T03:52:44Z","0x9537D87889DB55592bA5956a009e960857310e77":"2026-11-08T03:51:12Z","0x96c39A5aC2666AAD758C67f79c752752ee571dF2":"2026-11-08T03:50:38Z","0x9f9ae311a61a045d0E04794e26aa068DfB16522F":"2026-11-08T03:49:45Z","0x32c8920F1803BA368060B6BB0EF65F17370366D6":"2026-11-08T03:48:13Z","0x0bC3894CDCE47AbBC3B34E0816C15B195E0AAdbE":"2026-11-08T03:48:10Z","0x19993B3Cf15c1055063468EB932F5e335A7526ea":"2026-11-08T03:48:03Z","0x46AcB035b5efa87bFC99aF605b85b8d45c4D1F85":"2026-11-08T03:47:58Z","0x11AfDc2d736d646421E8df53E9cA6080783B5A5e":"2026-11-08T03:45:45Z","0x0E35f73fE749bfE28755D9acbf950b60548d816F":"2026-11-08T03:44:44Z","0x04C39B491bb4342fd05822b4C939Fb7d9427B793":"2026-11-08T03:43:43Z","0x1BCAA6E08c4e68E8fc9D468152339aB931Ad6cEC":"2026-11-08T03:43:42Z","0x47b58721A0e1E0265FAcaEA9Ab79Ba7A6D1aFaD6":"2026-11-08T03:42:50Z","0x8D14B3CED5ca9c6272b9e80D93a524da528D79E3":"2026-11-08T03:42:12Z","0x625354460BC39aA0a039DA8620a629C6726E4010":"2026-11-08T03:42:04Z","0xe17f31D735916854963B272635047dc75D5C6826":"2026-11-08T03:38:14Z","0xab3bA230A727897F4A19c1561485ab2660B83b88":"2026-11-08T03:37:49Z"}
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE=["freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","freesupply","free_slots","free_supply","freeslots"]
def get_abi(a):
    r=subprocess.run(["curl","-s","--max-time","30","-H","User-Agent: Mozilla/5.0",
        f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"],capture_output=True,text=True)
    try:
        d=json.loads(r.stdout)
    except Exception:
        return {"_err":(r.stdout[:100] or r.stderr[:100])}
    if isinstance(d,dict) and "abi" in d: return d["abi"]
    return d
out={}
for a in ADDRS:
    abi=get_abi(a)
    if not isinstance(abi,list):
        out[a]={"status":str(abi)[:200],"verifiedAt":VERIFIED_AT[a]}
        print(a,"SOURCIFY_FAIL",str(abi)[:120]); continue
    fns=[x.get("name","") for x in abi if x.get("type")=="function"]
    low=[f.lower() for f in fns]
    has_mint=any(f.startswith("mint") for f in low)
    has_quote=any("quote" in f or f.startswith("cost") for f in low)
    free=[f for f in low if any(k in f for k in FREE)]
    has_token=any(x in low for x in ("name","symbol","decimals","totalsupply"))
    raw=json.dumps(abi).lower()
    reg = REG in raw or "agentregistry" in raw or "agent_id_registry" in raw or "agentidregistry" in raw
    s1 = has_mint and has_quote and bool(free) and reg
    noarg_free = any(f in ("mintfree","claimfree","freemint") for f in low)
    s2 = has_token and noarg_free and bool(free) and reg
    mint_shaped = has_mint and bool(free)
    out[a]={"verifiedAt":VERIFIED_AT[a],"fns":len(fns),"mint":has_mint,"quote":has_quote,"free":free,"token":has_token,"registry":reg,"S1":s1,"S2":s2,"mint_shaped":mint_shaped,"fn_sample":fns[:40]}
    print(a,"fns",len(fns),"mint",has_mint,"quote",has_quote,"free",free,"token",has_token,"reg",reg,"S1",s1,"S2",s2,"mint_shaped",mint_shaped)
json.dump(out,open("run-2026-11-08-1031-feed-shape.json","w"),indent=1)
print("HITS S1/S2/mint-shaped:",[a for a,v in out.items() if isinstance(v,dict) and (v.get("S1") or v.get("S2") or v.get("mint_shaped"))])
