#!/usr/bin/env python3
import json, subprocess
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
cands = json.load(open(BASE + "run-2026-11-03-0301-trackc-5c-cands.json"))
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeSharesGiven","freeClaimedBy","freeMinted"]
out = {}
for c in cands:
    a = c["address"]
    try:
        raw = subprocess.run(["curl","-sL","--max-time","20",f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"], capture_output=True, text=True).stdout
        d = json.loads(raw)
        abi = d.get("abi")
        if not abi:
            out[a] = {"status": "abi-empty-inconclusive", "mint_count": c["mint_count"]}; print(a, "ABI-EMPTY"); continue
        fns = [f["name"] for f in abi if f.get("type") == "function"]
        has_mint = any(f in ("mint","mintFree","claimFree","claimFreeShare","claim") for f in fns)
        has_quote = any("quote" in f or "cost" in f.lower() for f in fns)
        has_free = any(f in FREE_VIEWS for f in fns)
        has_reg = any("regist" in f.lower() or "agent" in f.lower() for f in fns)
        s1 = has_mint and has_quote and has_free and has_reg
        is_token = all(x in fns for x in ("name","symbol","decimals","totalSupply"))
        s2 = is_token and ("mintFree" in fns or "claimFree" in fns) and has_free and has_reg
        out[a] = {"status": "PASS" if (s1 or s2) else "fail", "S1": s1, "S2": s2, "mint_count": c["mint_count"],
                  "fns_sample": [f for f in fns if f in ("mint","mintFree","claimFree","quote","costFor","freeClaimed","freeMinted","agentRegistry","registry","agentId")]}
        print(a, "PASS" if (s1 or s2) else "fail", "S1", s1, "S2", s2, out[a]["fns_sample"])
    except Exception as e:
        out[a] = {"status": "error", "err": str(e)[:100]}; print(a, "ERR", str(e)[:100])
json.dump(out, open(BASE + "run-2026-11-03-0301-trackc-5c.json", "w"), indent=1)
print("passes:", [k for k,v in out.items() if v.get("status")=="PASS"])
