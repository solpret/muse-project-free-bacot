#!/usr/bin/env python3
"""Hot-leg 0644 recovery: shape-check the 6 feed-new contracts only.
Bounded: 60s total. Writes run-2026-11-12-0644-shapes.json."""
import json, subprocess, time
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
addrs = json.load(open(BASE + "run-2026-11-12-0644-feed-new.json"))
t0 = time.time()
out = {}
for a in addrs:
    if time.time() - t0 > 55:
        out[a] = {"error": "deadline-skip"}
        continue
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "12",
                            f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"],
                           capture_output=True, text=True, timeout=15)
        meta = json.loads(r.stdout)
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        lnames = {n.lower() for n in names}
        has_quote = bool(lnames & {"quote", "cost", "getquote", "mintcost", "price", "getprice", "mintprice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(lnames & {"agentid", "agentregistry", "registry", "getagentid", "agentgate", "agentidregistry"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply", "balanceOf"}) and "totalSupply" in names
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        is_nft = bool(names & {"tokenURI", "ownerOf", "safeTransferFrom"}) or "uri" in names
        free_mint_fn = bool(names & {"freeMint", "mintFree", "claimFree", "mint"}) or any(n.lower().startswith("freemint") for n in names)
        early_shape = is_nft and (agent_ref or free_mint_fn)
        out[a] = {"S1": s1, "S2": s2, "early_shape": early_shape, "has_mint": has_mint,
                  "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref,
                  "is_token": is_token, "is_nft": is_nft, "fn_count": len(names)}
    except Exception as ex:
        out[a] = {"error": f"{type(ex).__name__}: {str(ex)[:120]}"}
    print(a, out[a], f"({time.time()-t0:.1f}s)", flush=True)
json.dump(out, open(BASE + "run-2026-11-12-0644-shapes.json", "w"), indent=1)
print("SHAPES DONE in", round(time.time() - t0, 1), "s", flush=True)
