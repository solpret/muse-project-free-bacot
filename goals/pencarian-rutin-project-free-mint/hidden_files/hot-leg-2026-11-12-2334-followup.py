#!/usr/bin/env python3
"""Hot-leg 2334 followup: shape-check the 10 feed contracts deferred by deadline + 2 still-404.
Tight: 5s Sourcify timeout each, no sleep. Updates hot-leg-seen.json notes only."""
import json, subprocess, time
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS = {"freesharesremaining", "freeclaimed", "freefor", "freeleft", "freeused",
              "freeavailable", "freesharepoolexhausted", "freesharesclaimed",
              "freeamount", "free_supply", "freeslots", "free_slots",
              "freeminted", "freemint", "freesupply"}
TARGETS = ["0xf9f931FFd3EF62dd616eA3eFe306A289512ab28F",
           "0x1e311022fEe30A395291eA21e5f339D3016a0Ed4",
           "0xad64BA5fe5Ff8d5929F79A61ce7841831C47d25e",
           "0x0504146B29416e8ec0262616c5520c20bFAB7fD8",
           "0x177B6B8761eF67520c42edEBD63CECe15A0c5829",
           "0x869DDC46b778462FEF834d60bc6dF1537Fb64124",
           "0x045E657A1EB160E9aC9625b54aC4Ba61bC04cAdF",
           "0x0D83163CB11b7959aaAc7A65f8f62082653E8577",
           "0x43405D834868d14bfF44Fe492A5091F367b98e77",
           "0xF408Bfe87b62be13c633b6277903EFB8426538dF",
           "0x98741B00d8F07A35Bd3347a6f03906343e839B76",
           "0x98a05953D68168Bf3216fF55750fd487f76486F0",
           "0xCF68C5dD64ef5ed92F6FdFa4366801C9D5Bda69b",
           "0xcb15aE4d71fDE657B1c9AbD3fe6F6EfA5A3bB2FA"]

def shape_check(a):
    try:
        r = subprocess.run(["curl", "-sL", "-m", "5", "-A", "Mozilla/5.0",
                            f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"],
                           capture_output=True, timeout=8)
        abi_j = json.loads(r.stdout.decode(errors="replace"))
    except Exception:
        return {"status": "shape-check-failed", "note": "fetch error/timeout"}
    abi = None
    if isinstance(abi_j, dict):
        abi = abi_j.get("abi") or (abi_j.get("stdJson") or {}).get("abi")
    if not abi:
        return {"status": "shape-check-failed", "note": "ABI unfetchable (404 or error)"}
    names = set()
    for fn in abi:
        if isinstance(fn, dict) and fn.get("type") in ("function", None):
            names.add((fn.get("name") or "").lower())
    has_mint = any("mint" in n for n in names)
    has_quote = any(("quote" in n or n in ("cost", "price", "mintprice", "getprice")) for n in names)
    free_views = sorted(n for n in names if n in FREE_VIEWS or "free" in n)
    agent = any(("agent" in n and ("registry" in n or "gate" in n or "id" in n)) or n in
                ("agentregistry", "agentgate", "agent_id_registry", "registry") for n in names)
    src = json.dumps(abi).lower()
    agent = agent or ("agent_id_registry" in src) or ("agentgate" in src) or (REGISTRY[2:].lower() in src)
    is_token = any(n in names for n in ("name", "symbol", "decimals", "totalsupply"))
    has_mintfree = "mintfree" in names
    s1 = has_mint and has_quote and bool(free_views) and agent
    s2 = is_token and has_mintfree and bool(free_views) and agent
    return {"status": "checked", "S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote,
            "free": free_views, "agent": agent, "n_fns": len(names)}

seen = json.load(open(BASE + "hot-leg-seen.json"))
out = {}
t0 = time.time()
for a in TARGETS:
    s = shape_check(a)
    out[a] = {k: s.get(k) for k in ("S1", "S2", "mint", "quote", "free", "agent", "status")}
    if isinstance(seen.get(a), dict):
        if s.get("status") == "checked":
            seen[a]["status"] = "checked"
            seen[a]["note"] = (f"FOLLOWUP-2334 {now_wib}: S1={s.get('S1')} S2={s.get('S2')} "
                               f"mint={s.get('mint')} quote={s.get('quote')} free={s.get('free')} agent={s.get('agent')}")
        else:
            seen[a]["note"] = (seen[a].get("note", "") + f" | followup {now_wib}: still 404").strip()[:400]
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "hot-leg-2026-11-12-2334-followup.json", "w"), indent=1)
print(json.dumps(out, indent=1))
