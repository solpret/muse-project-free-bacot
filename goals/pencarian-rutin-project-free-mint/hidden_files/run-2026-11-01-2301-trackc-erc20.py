#!/usr/bin/env python3
"""Track-C ERC-20 backlog shape-check, run 2026-11-01 23:01 WIB. Read-only.
Mirrors the 22:31 WIB check, plus S2 (single-contract token+sale) test.
S1: mint fn + quote/cost fn + free-share view + registry/AgentGate.
S2: token fns (name/symbol/decimals/totalSupply) + no-arg free-mint fn
     (mintFree or equivalent) + free views (freeClaimed/freeMinted +
     FREE_SLOTS/FREE_SUPPLY) + registry/AgentGate."""
import json, urllib.request, urllib.error

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
scan = json.load(open(BASE + "onchain-scan-2026-11-01-2301.json"))
checked = json.load(open(BASE + "track-c-scan-checked.json"))
done = {a.lower() for a in checked.get("checked", {})}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted"]
QUOTE_FNS = ["quote", "cost", "price", "getQuote", "mintCost", "pricePerShare"]
FREE_MINT_FNS = ["mintFree", "freeMint", "claimFree", "freeClaim"]
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"

erc20 = scan.get("erc20_mint_contracts_list", scan.get("erc20_mint_contracts", []))
print(f"erc20 backlog entries: {len(erc20)}")
cands = [c for c in erc20 if c.get("mint_count", 0) >= 10]
cands.sort(key=lambda c: c["mint_count"], reverse=True)
print(f"with mint_count >= 10: {len(cands)}")
todo = [c for c in cands if c["address"].lower() not in done][:20]
print(f"top 20 new to shape-check: {len(todo)} (remaining dropped as sampling limit)")

def sourcify(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode()).get("abi", [])
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP Error {e.code}: {e.reason}")
    except Exception as e:
        raise RuntimeError(f"{type(e).__name__}: {str(e)[:120]}")

out = {}
for c in todo:
    addr = c["address"]
    try:
        abi = sourcify(addr)
    except Exception as e:
        out[addr] = {"mint_count": c["mint_count"], "distinct_minters": c.get("distinct_minters"),
                     "error": str(e)}
        continue
    fns = sorted(set(f.get("name") for f in abi if f.get("type") == "function"))
    fnset = set(fns)
    blob = json.dumps(abi).lower()
    has_mint = "mint" in fnset
    has_quote = bool(fnset & set(QUOTE_FNS))
    free_views = [f for f in FREE_VIEWS if f in fnset]
    has_gate = (REG in blob) or bool(fnset & {"agentId", "agentRegistry", "registry", "agentGate"})
    s1 = has_mint and has_quote and bool(free_views) and has_gate
    is_token = bool({"name", "symbol", "decimals", "totalSupply"} <= fnset)
    has_free_mint = bool(fnset & set(FREE_MINT_FNS))
    s2_free = ("freeClaimed" in fnset or "freeMinted" in fnset) and bool(fnset & {"FREE_SLOTS", "FREE_SUPPLY"})
    s2 = is_token and has_free_mint and s2_free and has_gate
    out[addr] = {"mint_count": c["mint_count"], "distinct_minters": c.get("distinct_minters"),
                 "mint": has_mint, "quote_cost": has_quote, "free_views": free_views,
                 "agent_reg_gate": has_gate, "shape_pass_S1": s1,
                 "shape_pass_S2": s2, "is_token": is_token, "free_mint_fn": has_free_mint,
                 "shape_pass": s1 or s2, "fns_sample": fns[:40]}
    print(addr, "S1" if s1 else "-", "S2" if s2 else "-", "mints", c["mint_count"])

json.dump(out, open(BASE + "run-2026-11-01-2301-trackc-erc20.json", "w"), indent=1)
checked.setdefault("checked", {}).update(out)
json.dump(checked, open(BASE + "track-c-scan-checked.json", "w"), indent=1)
print("checked file updated; total checked:", len(checked["checked"]))
