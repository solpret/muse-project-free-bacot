"""Route 5c shape-check for run 08:01: top-20 unchecked ERC-20 (mint_count>=10, desc).
S1: mint fn + quote/cost fn + free-share view + registry ref/gate.
S2: token fns + no-arg free-mint fn + free views + registry ref/gate.
Sourcify ABI fetch; unverified -> FAIL (unknown shape, never a pass).
"""
import json, urllib.request, time
B = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted",
              "freeSharesMinted", "freeClaimedShares"]
QUOTE_FNS = ["quote", "costFor", "cost", "getQuote", "priceFor"]

def abi_of(a):
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",
                                     headers={"User-Agent": "free-mint-search/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode())["abi"], None
    except Exception as e:
        return None, str(e)[:120]

todo = json.load(open(B + "run-2026-11-02-0801-5c-todo.json"))
out = []
for e in todo:
    a = e["address"]
    abi, err = abi_of(a)
    if abi is None:
        out.append({"address": a, "mint_count": e["mint_count"], "shape": "FAIL",
                    "reason": f"Sourcify ABI unavailable ({err}); unknown shape, never a pass"})
        print(a, "FAIL sourcify-unavailable"); time.sleep(0.5); continue
    fns = {x["name"] for x in abi if x.get("type") == "function"}
    src = json.dumps(abi).lower()
    has_mint = "mint" in fns or "mintFree" in fns or "claim" in fns or "claimFree" in fns
    has_quote = bool(fns & set(QUOTE_FNS))
    free = sorted(fns & set(FREE_VIEWS))
    has_reg = REG in src or "agentRegistry" in fns or "registry" in fns or "AGENT_ID" in fns or "agentId" in " ".join(fns).lower()
    has_token = {"name", "symbol", "decimals", "totalSupply"} <= fns
    noarg_free = any(x.get("name") in ("mintFree", "claimFree", "freeMint") and len(x.get("inputs", [])) == 0
                     for x in abi if x.get("type") == "function")
    s1 = has_mint and has_quote and bool(free) and has_reg
    s2 = has_token and noarg_free and bool(free) and has_reg
    if s1 or s2:
        verdict = "PASS-S1" if s1 else "PASS-S2"
        out.append({"address": a, "mint_count": e["mint_count"], "shape": verdict,
                    "fns": sorted(fns), "free_views": free})
        print(a, verdict, "free:", free)
    else:
        out.append({"address": a, "mint_count": e["mint_count"], "shape": "FAIL",
                    "reason": f"mint={has_mint} quote={has_quote} free={free} registry={has_reg} token={has_token} noarg_free={noarg_free}"})
        print(a, "FAIL", f"mint={has_mint} quote={has_quote} free={free} reg={has_reg}")
    time.sleep(0.5)
json.dump(out, open(B + "run-2026-11-02-0801-5c.json", "w"), indent=1)
print("passes:", [o for o in out if o["shape"].startswith("PASS")])
