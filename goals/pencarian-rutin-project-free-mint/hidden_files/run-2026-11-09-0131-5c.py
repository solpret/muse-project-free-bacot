#!/usr/bin/env python3
"""Run 0131 stage 5c: track-C shape-check of ERC-20 mint_count>=10 from scan.
Read-only except writing run-2026-11-09-0131-5c.json and updating
track-c-scan-checked.json with newly checked addresses."""
import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
import onchain_nft_scan as scan

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
out = {}

# (b) 5c shape-check
scan_out = json.load(open(f"{BASE}/run-2026-11-09-0131-scan.json"))
e20 = scan_out.get("erc20_mint_contracts_list", [])
checked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
checked_list = checked.get("checked", [])
checked_set = set(checked_list) | {k for k in checked if k.startswith("0x")}
cands = sorted([e for e in e20 if e.get("mint_count", 0) >= 10],
               key=lambda x: -x.get("mint_count", 0))
new = [e for e in cands if e["address"] not in checked_set][:20]
print(f"5c: {len(cands)} mint_count>=10, {len(new)} new to check", flush=True)

def sourcify(a):
    url = f"https://sourcify.dev/server/v2/contracts/56/{a}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except Exception as e:
        return {"_error": str(e)}

shapes = {}
for e in new:
    a = e["address"]
    sc = sourcify(a)
    abi = None
    try:
        abi = sc.get("stdJson", {}).get("output", {}).get("abi") or sc.get("abi")
    except Exception:
        pass
    if abi:
        fns = [f.get("name") for f in abi if f.get("type") == "function"]
        free = [f for f in fns if "free" in f.lower()]
        mint = any("mint" in f.lower() for f in fns)
        quote = any("quote" in f.lower() or "cost" in f.lower() for f in fns)
        agent = any("agent" in f.lower() or "registry" in f.lower() for f in fns)
        token = all(x in fns for x in ["name", "symbol", "decimals", "totalSupply"])
        shapes[a] = {"mint_count": e["mint_count"],
                     "S1": bool(mint and quote and free and agent),
                     "S2": bool(token and any(f.lower() == "mintfree" for f in fns) and free and agent),
                     "mint": mint, "quote": quote, "free": free, "agent": agent,
                     "token": token, "registry_bytes": REG in json.dumps(sc).lower()}
    else:
        shapes[a] = {"mint_count": e["mint_count"], "error": sc.get("_error"),
                     "S1": False, "S2": False}
    print("  5c", a, shapes[a], flush=True)
out["5c"] = shapes
out["5c_targets"] = [e["address"] for e in new]
out["5c_dropped"] = len(cands) - len(new)
json.dump(out, open(f"{BASE}/run-2026-11-09-0131-5c.json", "w"), indent=1)
# record newly checked addresses (append to checked list, keep file shape)
for a in shapes:
    if a not in checked_set:
        checked_list.append(a)
checked["checked"] = checked_list
with open(f"{BASE}/track-c-scan-checked.json", "w") as f:
    json.dump(checked, f, indent=1)
print("5C DONE", flush=True)
