#!/usr/bin/env python3
"""5a Sourcify feed shape-check run 2131: sale shapes S1/S2.
Read-only except writing run-2026-11-07-2131-sourcify.json and
sourcify-feed-2131.json. Correct endpoint /v2/contract/56/{addr}?fields=abi.
Keccak selectors via pycryptodome (never hashlib.sha3_256).
Skips addresses already in track-c-scan-checked.json; newly checked
addresses are listed in output 'additions' for appending to the file.
"""
import json, time, urllib.request, urllib.error
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
              "freeused", "freeavailable", "freesharepoolexhausted",
              "freesharesclaimed", "isfreemintavailable", "freeminted",
              "free_slots", "free_supply", "freeslots", "freesupply"]
QUOTE_WORDS = ["quote", "cost", "price", "getprice", "mintprice", "mintcost"]

def get_json(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "free-bacot-sourcify/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

feed_url = "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"
feed = get_json(feed_url)
json.dump(feed, open(f"{BASE}/sourcify-feed-2131.json", "w"), indent=1)
results = feed.get("results", [])
print(f"feed: {len(results)} contracts", flush=True)

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

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        return get_json(url).get("abi"), None
    except urllib.error.HTTPError as e:
        return ("__not_verified__" if e.code == 404 else None), f"HTTP{e.code}"
    except Exception as e:
        return None, f"{type(e).__name__}:{e}"

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

out = {"feed_url": feed_url, "checked": [], "hits": [], "additions": [],
       "skipped_already_checked": []}
for it in results:
    addr = it["address"]
    va = it.get("verifiedAt")
    if addr.lower() in checked_set:
        out["skipped_already_checked"].append(addr)
        print(addr, va, "SKIP already-checked", flush=True)
        continue
    abi, err = fetch_abi(addr)
    row = {"address": addr, "verifiedAt": va,
           "in_snapshot": addr.lower() in snap_addrs,
           "in_seen": addr.lower() in seen_addrs, "error": err}
    if abi == "__not_verified__" or not isinstance(abi, list):
        row["shape"] = "not_verified" if abi == "__not_verified__" else "abi-unavailable"
        out["checked"].append(row)
        print(addr, va, row["shape"], flush=True)
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

json.dump(out, open(f"{BASE}/run-2026-11-07-2131-sourcify.json", "w"), indent=1)
print(f"SOURCIFY DONE checked={len(out['checked'])} hits={len(out['hits'])} "
      f"additions={len(out['additions'])} skipped={len(out['skipped_already_checked'])}", flush=True)
