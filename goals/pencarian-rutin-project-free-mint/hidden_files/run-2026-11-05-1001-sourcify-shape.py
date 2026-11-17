import json, urllib.request
FEED=["0xf03d62A10a5Cd72321D2cE48421471aA0C0238C1","0x609828f537e6AAB7b193106F8249Cc45eE82a6F4","0x49150574b740c5a75FaC272446f9cBB7c27b02C2","0x63074E383845bCc3715D4761c1BbEf5E9e7be861","0x98b388D1c246F70770887194763d55dFCaaba615","0x49d057C403611F0A19D3DF7a825e813648D73197","0x6973E7c7f2d53894418Bef46b72D9E0A143cFf44","0x86CA531ffB29A0B7bc17A5f3973F7B431a9263A4","0xeEB4E27bCf62e257920cB573eb8ca14392C62637","0x133d4544b4BE8efb49d6245655d16C8632C52885","0x62EC413381B74387b57F1E2734cdd2E5b96a57B7","0x320eaFF5D69Af30696FbDb179f70EFe9C511361c","0xcdbdB027BBcbEc8217859f4f244A0629Fa27Ddb2","0xF136482BE355d431BA02D657a50691621C78d9B0","0x5DDC00FE4A43FAA59d22cD9DF291dAA53fdbf172","0xa650d6d58C91aE9a2674dfC60D99ed24D97Bd571","0x12167D06c9CecC0b5EAFD166892CFbf8240fd971","0xE9bF181aEDb61c320787cd707a36aB0C6524aA6b","0x37336d3E8faE51ddA4Ce0f213c72631A87119ED4","0xc3e4029b0cfdcaFaF91fC0e33ff0deC597736207"]
FREE_VIEWS=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeMint"]
res={}
for a in FEED:
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",headers={"Accept":"application/json"})
        with urllib.request.urlopen(req,timeout=25) as r: d=json.load(r)
        abi=d.get("abi") or d.get("stdJson",{}).get("abi") or []
        names=[e.get("name","") for e in abi if isinstance(e,dict)]
        has_mint=any(n.startswith("mint") for n in names)
        has_quote=any("quote" in n.lower() or "cost" in n.lower() or "price" in n.lower() for n in names)
        free=[n for n in names if any(f.lower() in n.lower() for f in FREE_VIEWS)]
        gate=any("agent" in n.lower() or "registry" in n.lower() for n in names)
        is_token=any(n in names for n in ["name","symbol","decimals","totalSupply"])
        res[a]={"abi_funcs":len(names),"mint":has_mint,"quote_or_cost":has_quote,"free_views":free,"agent_gate":gate,"is_token_shape":is_token,
               "funcs_sample":[n for n in names if any(k in n.lower() for k in ["mint","free","agent","quote","claim","registry","price"])][:20]}
    except Exception as e:
        res[a]={"error":str(e)[:120]}
    print(a, json.dumps(res[a]), flush=True)
json.dump(res,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-1001-sourcify-shape.json","w"),indent=1)
