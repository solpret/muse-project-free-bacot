#!/usr/bin/env python3
"""5c shape-check run 1201: 4 new ERC20 candidates from partial scan 1201. Read-only."""
import json, sys, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REG = "0x60b9262456dE011F7d15a54CdD8c48bAaa8B022F"
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeSupply","freeShares","freeCap","freeSold","freeRemaining","freeClaimedByKey","freeClaimedById","freeTokens","freeMintedBy"}
cands = json.load(open(f"{BASE}/run-2026-11-08-1201-5c-candidates.json"))
def sourcify_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return ("verified", json.loads(r.read().decode()).get("abi"))
    except urllib.error.HTTPError as e:
        return ("not_verified" if e.code == 404 else f"http_{e.code}", None)
    except Exception as e:
        return (f"error:{type(e).__name__}", None)
def fn_names(abi):
    return {f.get("name") for f in (abi or []) if f.get("type") == "function"}
out = {}
for c in cands:
    addr = c["address"]
    st, abi = sourcify_abi(addr)
    fns = fn_names(abi) if abi else set()
    has_mint = any(n in fns for n in ("mint","mintFree","claimFree","freeMint","mintWithBnb","claim"))
    has_quote = any(n in fns for n in ("quote","quoteFor","costFor","mintCost","cost","priceAt","mintPrice","currentPrice","bnbQuote","costOf"))
    free_hits = sorted(fns & FREE_VIEWS)
    reg_fn = any(n in fns for n in ("agentId","registry","AGENT_ID","AGENT_ID_REGISTRY","AGENT_REGISTRY","agentRegistry","identity","agentIdOf","hasAgentId","requireAgentId","isAgent"))
    # bytecode registry bytes check via eth_getCode
    code = None
    try:
        code = batch([("eth_getCode", [addr, "latest"])], endpoint="https://bsc-dataseed.binance.org/", timeout=15)[0]
    except Exception as e:
        code = f"error:{e}"
    reg_bytes = isinstance(code, str) and "60b9262456de011f7d15a54cdd8c48baaa8b022f" in code.lower()
    is_token = bool({"name","symbol","decimals","totalSupply"} & fns)
    s1 = bool(has_mint and has_quote and free_hits and (reg_fn or reg_bytes))
    s2 = bool(is_token and ("mintFree" in fns or "claimFree" in fns) and free_hits and (reg_fn or reg_bytes))
    out[addr] = {"mint_count": c["mint_count"], "distinct_minters": c["distinct_minters"],
                 "first_block": c["first_block"], "sourcify": st,
                 "fns": sorted(fns)[:60], "has_mint": has_mint, "has_quote": has_quote,
                 "free_views": free_hits, "registry_fn": reg_fn, "registry_bytes": reg_bytes,
                 "is_token": is_token, "S1": s1, "S2": s2,
                 "verdict": ("S1" if s1 else "S2" if s2 else "NOT-SALE-SHAPE")}
    print(addr, out[addr]["verdict"], "sourcify=", st, "fns=", len(fns), "free=", free_hits, "regfn=", reg_fn, "regbytes=", reg_bytes, flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-08-1201-5c.json", "w"), indent=1)
# record as checked
p = f"{BASE}/track-c-scan-checked.json"
chk = json.load(open(p))
if isinstance(chk, dict):
    for a, r in out.items():
        chk[a] = {"run": "2026-11-08-1201", "verdict": r["verdict"], "sourcify": r["sourcify"], "mint_count": r["mint_count"]}
else:
    for a in out: chk.append(a)
json.dump(chk, open(p, "w"), indent=1)
print("5c DONE:", len(out), "checked, 0 sale-shape" if not any(r["S1"] or r["S2"] for r in out.values()) else "HIT!")
