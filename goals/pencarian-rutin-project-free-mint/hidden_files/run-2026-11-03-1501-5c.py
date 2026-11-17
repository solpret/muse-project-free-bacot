import json, urllib.request, time
H = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
addrs = json.load(open("/tmp/scan1501-5c-top20.json"))
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeSupply"]
def fetch(addr):
    req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", headers={"User-Agent":"free-mint-search/1501"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except Exception as e:
        return {"_err": str(e)[:120]}
out = {}
for addr in addrs:
    d = fetch(addr)
    if "_err" in d:
        out[addr] = {"sourcify": "error", "err": d["_err"]}
        print(addr, "ERROR", d["_err"], flush=True); continue
    abi = d.get("abi") or []
    fns = [f.get("name") for f in abi if f.get("type") == "function"]
    fnset = set(fns)
    has_mint = "mint" in fnset
    has_quote = bool(fnset & {"quote","cost","getCost","mintCost","price"})
    has_free = bool(fnset & set(FREE_VIEWS))
    abi_txt = json.dumps(abi).lower()
    has_reg = REG in abi_txt or "agentregistry" in abi_txt or "agentgate" in abi_txt
    s1 = has_mint and has_quote and has_free and has_reg
    is_token = bool(fnset & {"name","symbol","decimals","totalSupply"})
    has_free_mint_noarg = any(f.get("name") in ("mintFree","freeMint","claimFree") and len(f.get("inputs",[]))==0 for f in abi if f.get("type")=="function")
    s2 = is_token and has_free_mint_noarg and has_free and has_reg
    out[addr] = {"sourcify":"verified","functions":sorted(fnset),"S1":s1,"S2":s2,
                 "legs":{"mint":has_mint,"quote":has_quote,"free_view":has_free,"registry":has_reg,"token":is_token,"free_mint_noarg":has_free_mint_noarg}}
    print(addr, "S1" if s1 else "", "S2" if s2 else "", "fns:", len(fns), flush=True)
    time.sleep(0.5)
json.dump(out, open(f"{H}/run-2026-11-03-1501-5c.json","w"), indent=1)
print("DONE", len(out))
