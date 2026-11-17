#!/usr/bin/env python3
"""Hot-leg 0524 supplementary: shape-check the 4 feed contracts the main script missed
because its curl Sourcify-feed fetch returned empty (leg1_feed n=0) while browser.open
had returned 20 contracts at 05:27 WIB. Only the 2 newest + the 2 transport-failed
retries from 0519 are new vs seen; the rest were already in seen per the 0519 run.
Transport-failed checks are NOT recorded in seen (established rule)."""
import json, subprocess, datetime
from concurrent.futures import ThreadPoolExecutor
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted"]
def wib_now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds")
def curl_get(url, timeout=12):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), url], capture_output=True, text=True, timeout=timeout + 5)
    return r.stdout
def shape_check(addr):
    try:
        d = json.loads(curl_get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=12))
        abi = d.get("abi") or []
        fns = [e.get("name") for e in abi if isinstance(e, dict) and e.get("type") == "function"]
    except Exception as e:
        return {"address": addr, "error": f"{type(e).__name__}: {e}"}
    names = set(fns)
    has_mint = bool(names & {"mint", "mintFree", "mintWithInviter", "claimMint", "mintShare", "buyShare"})
    has_quote = bool(names & {"quote", "cost", "price", "priceFor", "getPrice", "mintPrice"})
    free = sorted([f for f in FREE_VIEWS if f in names])
    agent = bool(names & {"identityRegistry", "agentRegistry", "AgentGate", "agentId", "agentID"}) or any("agent" in (f or "").lower() or "registry" in (f or "").lower() for f in fns)
    token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = token and ("mintFree" in names) and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY", "FREE_AMOUNT"})
    return {"address": addr, "S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote,
            "free": free, "agent": agent, "token": token,
            "note": f"S1={s1} S2={s2} mint={has_mint} quote={has_quote} free={free} agent={agent} token={token}"}
addrs = ["0xb5443C9b29Ee3FBe917171C059fFB5a23F916Ea5",
         "0xF3091151FC40f5f12a7B0BB7d9679C9fCE133E16",
         "0x546aDbF244fbaA70fDe81f550a7EdA38612A1c07",
         "0x53aA0c94b9f670866a5EDbc42A66bf5cAB59c92a"]
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
results = {}
with ThreadPoolExecutor(max_workers=4) as ex:
    for res in ex.map(shape_check, addrs):
        results[res["address"]] = res
        if "error" not in res:
            seen[res["address"]] = {"first_seen_wib": wib_now(), "note": res.get("note", ""), "source": "sourcify-feed", "status": "checked-not-sale-shape" if not (res.get("S1") or res.get("S2")) else "sale-shape"}
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
json.dump(list(results.values()), open(f"{BASE}/hot-leg-2026-11-09-0524-sourcify-shape.json", "w"), indent=1)
print(json.dumps(list(results.values()), indent=1))
