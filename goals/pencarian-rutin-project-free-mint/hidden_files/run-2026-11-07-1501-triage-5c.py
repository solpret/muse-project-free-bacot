#!/usr/bin/env python3
"""5c triage run 1501: ERC-20 backlog from scan window, mint_count>=10, max 20,
skip already-checked in track-c-scan-checked.json. Read-only on-chain except
recording newly checked addresses. Writes run-2026-11-07-1501-triage-5c.json."""
import json, time, urllib.request, urllib.error
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
              "freeused", "freeavailable", "freesharepoolexhausted",
              "freesharesclaimed", "freeminted", "free_slots", "free_supply",
              "freeslots", "freesupply"]
QUOTE_WORDS = ["quote", "cost", "price", "getprice", "mintprice", "mintcost"]

scan = json.load(open(f"{BASE}/onchain-scan-2026-11-07-1501.json"))
lst = scan.get("erc20_mint_contracts_list", [])
cands = sorted([e for e in lst if e.get("mint_count", 0) >= 10],
               key=lambda e: -e.get("mint_count", 0))
checked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
seen = {a.lower() for a in checked.get("checked", [])}
seen |= {k.lower() for k in checked.keys() if k != "checked"}
todo = [e for e in cands if e["address"].lower() not in seen][:20]
print(f"5c: window erc20={len(lst)} >=10={len(cands)} already-checked="
      f"{len(cands) - len(todo)} to-check={len(todo)}", flush=True)

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "free-bacot-sourcify/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode()).get("abi"), None
    except urllib.error.HTTPError as e:
        return ("__not_verified__" if e.code == 404 else None), f"HTTP{e.code}"
    except Exception as e:
        return None, f"{type(e).__name__}:{e}"

out = {"checked": [], "hits": [], "window": scan.get("from_block"),
       "window_to": scan.get("to_block")}
for e in todo:
    addr = e["address"]
    abi, err = fetch_abi(addr)
    row = {"address": addr, "mint_count": e.get("mint_count"),
           "distinct_minters": e.get("distinct_minters"), "error": err}
    if abi == "__not_verified__" or not isinstance(abi, list):
        row["shape"] = "not_verified" if abi == "__not_verified__" else "abi-unavailable"
        out["checked"].append(row)
        print(addr, "mints=", e.get("mint_count"), row["shape"], flush=True)
    else:
        fns = [f for f in abi if isinstance(f, dict) and f.get("type") == "function"]
        names = [f.get("name", "").lower() for f in fns]
        name_set = set(names)
        raw = json.dumps(abi).lower()
        mint = [n for n in names if n.startswith("mint") or n in ("claim", "claimfree")]
        quote = [n for n in names if any(w in n for w in QUOTE_WORDS)]
        freev = [n for n in names if n in FREE_VIEWS]
        has_reg = REGISTRY in raw or "agentregistry" in name_set or "agentgate" in name_set
        is_token = all(x in name_set for x in ("name", "symbol", "decimals", "totalsupply"))
        noarg_free = any(f.get("name", "").lower() in ("mintfree", "claimfree")
                         and len(f.get("inputs", [])) == 0 for f in fns)
        s1 = bool(mint) and bool(quote) and bool(freev) and has_reg
        s2 = is_token and noarg_free and bool(freev) and has_reg
        row.update({"fns": len(fns), "mint": mint[:4], "quote": quote[:4],
                    "free_views": freev[:6], "registry": has_reg,
                    "is_token": is_token, "noarg_free": noarg_free,
                    "S1": s1, "S2": s2})
        out["checked"].append(row)
        tag = "HIT S1" if s1 else ("HIT S2" if s2 else "no-shape")
        print(addr, "mints=", e.get("mint_count"), tag, "mint=", mint[:3],
              "free=", freev[:4], "reg=", has_reg, flush=True)
        if s1 or s2:
            out["hits"].append(row)
    checked.setdefault("checked", []).append(addr)
    time.sleep(0.3)

json.dump(out, open(f"{BASE}/run-2026-11-07-1501-triage-5c.json", "w"), indent=1)
json.dump(checked, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)
print(f"5c DONE checked={len(out['checked'])} hits={len(out['hits'])}", flush=True)
