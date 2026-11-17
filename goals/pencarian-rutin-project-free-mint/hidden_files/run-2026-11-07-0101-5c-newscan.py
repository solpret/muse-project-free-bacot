#!/usr/bin/env python3
"""Route 5c for run 2026-11-07 01:01 WIB — shape-check ERC-20 backlog from the
new scan (recover.json, window 132053652-132054651). Read-only.
mint_count >= 10, sorted desc, at most 20 NEW (not in track-c-scan-checked.json).
Sourcify endpoint (corrected run 0031): /v2/contract/56/{addr}?fields=abi.
Transport failure is recorded as transport-failed, NEVER as not-sale-shape.
Writes run-2026-11-07-0101-5c-newscan.json only; does NOT edit the checked file
(parent finalize appends)."""
import json, time, urllib.request, urllib.error

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
              "freeused", "freeavailable", "freesharepoolexhausted",
              "freesharesclaimed", "freeminted", "free_slots", "free_supply",
              "freeslots", "freesupply"]
QUOTE_WORDS = ["quote", "cost", "price", "getprice", "mintprice", "mintcost"]

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    last = None
    for attempt in (1, 2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "free-bacot-5c/1.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode()), None
        except urllib.error.HTTPError as e:
            # Sourcify 404 = contract NOT verified (definitive, not a transport failure)
            if e.code == 404:
                return {"__not_verified__": True}, None
            last = f"attempt{attempt}:{type(e).__name__}:{e}"
            time.sleep(2)
        except Exception as e:  # noqa: BLE001
            last = f"attempt{attempt}:{type(e).__name__}:{e}"
            time.sleep(2)
    return None, last

def shape(abi_list):
    if not isinstance(abi_list, list):
        return {"error": "abi-not-list"}
    fns = [e for e in abi_list if isinstance(e, dict) and e.get("type") == "function"]
    names = [f.get("name", "").lower() for f in fns]
    name_set = set(names)
    raw = json.dumps(abi_list).lower()
    mint_fns = [n for n in names if n.startswith("mint") or n in ("claim", "claimfree")]
    quote_fns = [n for n in names if any(w in n for w in QUOTE_WORDS)]
    free_views = [n for n in names if n in FREE_VIEWS]
    has_registry = REGISTRY in raw or "agentregistry" in name_set or "agentgate" in name_set
    is_token = {"name", "symbol", "decimals", "totalsupply"} <= name_set
    noarg_free = any(
        f.get("name", "").lower() in ("mintfree", "claimfree", "freemint")
        and len(f.get("inputs", [])) == 0 for f in fns)
    s1 = bool(mint_fns and quote_fns and free_views and has_registry)
    s2 = bool(is_token and noarg_free and free_views and has_registry)
    return {"mint_fns": mint_fns, "quote_fns": quote_fns, "free_views": free_views,
            "agent_gate": has_registry, "is_token": is_token,
            "noarg_free": noarg_free, "S1": s1, "S2": s2,
            "fn_count": len(fns)}

def main():
    scan = json.load(open(f"{BASE}/onchain-scan-2026-11-07-0101-recover.json"))
    checked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
    checked_set = {a.lower() for a in checked.get("checked", [])}
    cands = [e for e in scan["erc20_mint_contracts_list"] if e.get("mint_count", 0) >= 10]
    cands.sort(key=lambda e: -e["mint_count"])
    new = [e for e in cands if e["address"].lower() not in checked_set][:20]
    print(f"erc20 mint_count>=10: {len(cands)}; already checked: {len(cands)-len(new)}; to check: {len(new)}")
    results, transport_failed = [], []
    for e in new:
        addr = e["address"]
        data, err = fetch_abi(addr)
        if data is None:
            results.append({"address": addr, "mint_count": e["mint_count"],
                            "distinct_minters": e.get("distinct_minters"),
                            "verdict": "transport-failed", "error": err})
            transport_failed.append(addr)
            print(f"  {addr} mint_count={e['mint_count']} TRANSPORT-FAILED {err}")
            continue
        std = data.get("stdJson") if isinstance(data, dict) else None
        abi = None
        if isinstance(data, dict):
            abi = data.get("abi")
            if abi is None and isinstance(std, dict):
                abi = std.get("abi")
        if abi is None:
            results.append({"address": addr, "mint_count": e["mint_count"],
                            "distinct_minters": e.get("distinct_minters"),
                            "verdict": "not_verified",
                            "sourcify": data if isinstance(data, dict) else str(data)[:200]})
            print(f"  {addr} mint_count={e['mint_count']} NOT_VERIFIED")
            continue
        sh = shape(abi)
        verdict = "SALE-SHAPE" if (sh["S1"] or sh["S2"]) else "not-sale-shape"
        results.append({"address": addr, "mint_count": e["mint_count"],
                        "distinct_minters": e.get("distinct_minters"),
                        "verdict": verdict, "sourcify": "verified", **sh})
        print(f"  {addr} mint_count={e['mint_count']} {verdict} S1={sh['S1']} S2={sh['S2']}")
        time.sleep(0.5)
    out = {"run": "2026-11-07-0101", "source": "onchain-scan-2026-11-07-0101-recover.json",
           "window": [scan.get("from_block"), scan.get("to_block")],
           "candidates_ge10": len(cands), "checked_this_run": len(results),
           "sale_shape_hits": [r["address"] for r in results if r["verdict"] == "SALE-SHAPE"],
           "transport_failed": transport_failed, "results": results}
    json.dump(out, open(f"{BASE}/run-2026-11-07-0101-5c-newscan.json", "w"), indent=1)
    print(f"done: {len(results)} checked, {len(out['sale_shape_hits'])} sale-shape, "
          f"{len(transport_failed)} transport-failed")

if __name__ == "__main__":
    main()
