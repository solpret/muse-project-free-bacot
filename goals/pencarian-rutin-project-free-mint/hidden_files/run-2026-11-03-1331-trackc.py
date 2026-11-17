import json, subprocess
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
d = json.load(open(HF + "onchain-scan-2026-11-03-1331.json"))
checked = json.load(open(HF + "track-c-scan-checked.json"))
if isinstance(checked, dict): checked_set = set(checked.keys())
else: checked_set = set(checked)
lst = d["erc20_mint_contracts_list"]
def mc(e): return e.get("window_mint_count", e.get("mint_count", 0))
cands = [e for e in sorted(lst, key=mc, reverse=True) if mc(e) >= 10 and e["address"].lower() not in {a.lower() for a in checked_set}]
print("unchecked >=10:", len(cands), "total >=10:", sum(1 for e in lst if mc(e) >= 10), flush=True)
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted"}
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
results = []
for e in cands[:20]:
    addr = e["address"]
    try:
        raw = subprocess.run(["curl", "-sL", "--max-time", "25", f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,metadata"], capture_output=True, text=True).stdout
        dd = json.loads(raw); abi = dd.get("abi", [])
        fns = {f["name"] for f in abi if f.get("type") == "function"}
        has_mint = any("mint" in f.lower() for f in fns)
        has_quote = any("quote" in f.lower() or "cost" in f.lower() for f in fns)
        free_views = sorted(fns & FREE_VIEWS)
        src = json.dumps(dd.get("metadata", {}))
        has_reg = REG.lower() in src.lower() or "agentRegistry" in fns or "AgentGate" in src
        s1 = has_mint and has_quote and bool(free_views) and has_reg
        is_token = {"name","symbol","decimals","totalSupply"} <= fns
        s2 = is_token and ("mintFree" in fns or "freeMint" in fns) and bool(free_views) and has_reg
        print(addr, "mint_count", mc(e), "S1" if s1 else "-", "S2" if s2 else "-", "fns", len(fns), "mint", has_mint, "quote", has_quote, "free", free_views, "reg", has_reg, "token", is_token, flush=True)
        results.append({"address": addr, "mint_count": mc(e), "s1": s1, "s2": s2, "fns": len(fns)})
    except Exception as ex:
        print(addr, "ERR", type(ex).__name__, str(ex)[:120], flush=True)
        results.append({"address": addr, "mint_count": mc(e), "error": str(ex)[:120]})
json.dump(results, open(HF + "run-2026-11-03-1331-trackc.json", "w"), indent=1)
print("DONE", len(results))
