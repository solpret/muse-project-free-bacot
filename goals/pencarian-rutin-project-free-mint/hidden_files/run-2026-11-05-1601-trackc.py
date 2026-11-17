#!/usr/bin/env python3
"""Run 1601 route 5c: ERC-20 backlog shape-check (S1/S2), max 20, mint_count >= 10.
Reads onchain-scan-2026-11-05-1601.json + track-c-scan-checked.json (checked dict),
writes run-2026-11-05-1601-trackc-shape.json and UPDATES track-c-scan-checked.json
with newly checked addresses only. No preview/mint/transaction."""
import json, sys, urllib.request

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS = {"freesharesremaining", "freeclaimed", "freefor", "freeleft",
              "freeused", "freeavailable", "freesharepoolexhausted",
              "freesharesclaimed", "freeminted", "freemint", "freebalance"}
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

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

def get_code(addr):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                       "params": [addr, "latest"]}).encode()
    for rpc in ("https://bsc-dataseed1.bnbchain.org", "https://bsc-dataseed2.bnbchain.org"):
        try:
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=12) as r:
                return json.load(r)["result"]
        except Exception:
            continue
    return None

scan = json.load(open(f"{BASE}/onchain-scan-2026-11-05-1601.json"))
checked_doc = json.load(open(f"{BASE}/track-c-scan-checked.json"))
checked = checked_doc.setdefault("checked", {})
checked_l = {k.lower() for k in checked.keys()}

cands = [e for e in scan.get("erc20_mint_contracts_list", []) if e["mint_count"] >= 10]
cands.sort(key=lambda e: -e["mint_count"])
print(f"ERC-20 window mint_count>=10: {len(cands)}; already checked (cumulative): {sum(1 for e in cands if e['address'].lower() in checked_l)}")

results = []
new_checked = 0
for e in cands:
    if len(results) >= 20:
        break
    addr = e["address"]
    if addr.lower() in checked_l:
        continue
    status, abi = sourcify_abi(addr)
    fns = {}
    if isinstance(abi, list):
        for it in abi:
            if it.get("type") == "function":
                fns[it.get("name", "")] = it
    names = list(fns.keys())
    lower = {n.lower(): n for n in names}
    has_mint = any("mint" in n.lower() for n in names)
    has_quote = any(("quote" in n.lower() or "cost" in n.lower() or "price" in n.lower()) for n in names)
    free_views = [n for n in names if n.lower() in FREE_VIEWS or ("free" in n.lower() and not n.lower().startswith("freeze"))]
    code = get_code(addr)
    reg_hit = bool(code and REGISTRY_BYTES in code[2:].lower())
    has_gate = any(("agentgate" in n.lower() or "registry" in n.lower() or "agentregistry" in n.lower()) for n in names)
    is_token = all(k in lower for k in ("name", "symbol", "decimals", "totalsupply"))
    no_arg_free = any(n.lower() in ("mintfree", "freemint", "claimfree") for n in names)
    s1 = bool(has_mint and has_quote and free_views and (reg_hit or has_gate))
    s2 = bool(is_token and no_arg_free and free_views and (reg_hit or has_gate))
    verdict = "S1" if s1 else ("S2" if s2 else "fail")
    results.append({
        "address": addr, "mint_count": e["mint_count"], "distinct_minters": e["distinct_minters"],
        "first_block": e["first_block"], "last_block": e["last_block"],
        "sourcify": status, "registry_bytes_hit": reg_hit, "agent_gate": has_gate,
        "is_token": is_token, "has_mint": has_mint, "has_quote_or_cost": has_quote,
        "free_views": free_views, "no_arg_free_mint": no_arg_free,
        "shape": verdict,
    })
    checked[addr] = {"source": "run-2026-11-05-1601-5c", "shape": verdict,
                     "mint_count": e["mint_count"]}
    checked_l.add(addr.lower())
    new_checked += 1
    print(f"  {verdict} {addr} mints={e['mint_count']} sourcify={status} reg={reg_hit} gate={has_gate} token={is_token} free={free_views}", flush=True)

remaining = len([e for e in cands if e["address"].lower() not in checked_l])
out = {
    "run": "1601",
    "window": [scan["from_block"], scan["to_block"]],
    "erc20_window_total": len(scan.get("erc20_mint_contracts_list", [])),
    "erc20_mint_count_ge_10": len(cands),
    "checked_this_run": len(results),
    "newly_checked": new_checked,
    "passed_shape": [r for r in results if r["shape"] in ("S1", "S2")],
    "failed_shape": [r["address"] for r in results if r["shape"] == "fail"],
    "results": results,
    "remaining_unchecked_this_window_sampling_limit": remaining,
    "note": "Sampling limit: max 20/run; remainder dropped for this window, stated not full coverage.",
}
json.dump(out, open(f"{BASE}/run-2026-11-05-1601-trackc-shape.json", "w"), indent=1)
json.dump(checked_doc, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)
print(f"checked this run: {len(results)}, passed: {len(out['passed_shape'])}, remaining unchecked: {remaining}")
print("DONE")
