#!/usr/bin/env python3
"""5a Sourcify shape-check run 2301 via curl (urllib RemoteDisconnected tonight).
Reads sourcify-feed-2301.json (fetched by curl). Read-only except own output.
"""
import json, subprocess, time
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
              "freeused", "freeavailable", "freesharepoolexhausted",
              "freesharesclaimed", "isfreemintavailable", "freeminted",
              "free_slots", "free_supply", "freeslots", "freesupply"]
QUOTE_WORDS = ["quote", "cost", "price", "getprice", "mintprice", "mintcost"]

def curl_json(url):
    r = subprocess.run(["curl", "-s", "-m", "30", url], capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return None, f"curl rc={r.returncode}"
    try:
        return json.loads(r.stdout), None
    except Exception as e:
        return None, f"parse:{e}"

feed = json.load(open(f"{BASE}/sourcify-feed-2301.json"))
results = feed.get("results", [])
print("feed:", len(results), "contracts", flush=True)
checked_file = json.load(open(f"{BASE}/track-c-scan-checked.json"))
checked_set = {a.lower() for a in checked_file.get("checked", [])}
checked_set |= {k.lower() for k in checked_file.keys() if k != "checked"}
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
snap_addrs = {v.get("address", "").lower() for v in snap.get("contracts", {}).values()}
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
seen_addrs = set()
if isinstance(seen, dict):
    seen_addrs = {a.lower() for a in seen.get("contracts", {}).keys()}
    for a in seen.keys():
        if a.startswith("0x"):
            seen_addrs.add(a.lower())

def shape(abi):
    fns = [e for e in abi if isinstance(e, dict) and e.get("type") == "function"]
    names = [f.get("name", "").lower() for f in fns]
    name_set = set(names)
    raw = json.dumps(abi).lower()
    mint = [n for n in names if n.startswith("mint") or n in ("claim", "claimfree")]
    quote = [n for n in names if any(w in n for w in QUOTE_WORDS)]
    freev = [n for n in names if n in FREE_VIEWS]
    has_reg = REGISTRY in raw or "agentregistry" in name_set or "agentgate" in name_set
    is_token = ({"name", "symbol", "decimals", "totalSupply"} <= name_set)
    noarg_free = any(f.get("name", "").lower() in ("mintfree", "claimfree")
                     and len(f.get("inputs", [])) == 0 for f in fns)
    s1 = bool(mint) and bool(quote) and bool(freev) and has_reg
    s2 = is_token and noarg_free and bool(freev) and has_reg
    return {"fns": len(fns), "mint": mint[:4], "quote": quote[:4],
            "free_views": freev[:6], "registry": has_reg,
            "is_token": is_token, "noarg_free": noarg_free,
            "S1": s1, "S2": s2,
            "agent_mint_shape": bool(mint) and bool(freev) and has_reg}

out = {"feed_url": "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc",
       "transport": "curl (urllib RemoteDisconnected x2 on feed fetch)",
       "checked": [], "hits": [], "additions": [], "skipped_already_checked": []}
for it in results:
    addr = it["address"]; va = it.get("verifiedAt")
    if addr.lower() in checked_set:
        out["skipped_already_checked"].append(addr)
        print(addr, va, "SKIP already-checked", flush=True); continue
    d, err = curl_json(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi")
    row = {"address": addr, "verifiedAt": va,
           "in_snapshot": addr.lower() in snap_addrs,
           "in_seen": addr.lower() in seen_addrs, "error": err}
    abi = d.get("abi") if isinstance(d, dict) else None
    if not isinstance(abi, list):
        row["shape"] = "abi-unavailable"
        out["checked"].append(row)
        print(addr, va, "abi-unavailable", err, flush=True)
    else:
        row.update(shape(abi))
        out["checked"].append(row)
        tag = "HIT S1" if row["S1"] else ("HIT S2" if row["S2"]
              else ("agent-mint" if row["agent_mint_shape"] else "no-shape"))
        print(addr, va, tag, "mint=", row["mint"][:3], "free=", row["free_views"][:4],
              "reg=", row["registry"], "in_snap=", row["in_snapshot"], flush=True)
        if row["S1"] or row["S2"] or row["agent_mint_shape"]:
            out["hits"].append(row)
    out["additions"].append(addr)
    time.sleep(0.3)
json.dump(out, open(f"{BASE}/run-2026-11-07-2301-sourcify.json", "w"), indent=1)
print(f"SOURCIFY DONE checked={len(out['checked'])} hits={len(out['hits'])} "
      f"additions={len(out['additions'])} skipped={len(out['skipped_already_checked'])}", flush=True)
