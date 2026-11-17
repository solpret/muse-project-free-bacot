#!/usr/bin/env python3
"""5c triage run 1901: shape-check 8 NEW ERC-20 from scan 1901
(mint_count>=10, none checked yet), Sourcify ABI sale-shape test S1/S2.
Correct endpoint /v2/contract/56/{addr}?fields=abi.
Read-only except writing run-2026-11-07-1901-5c.json; newly checked
addresses listed in output 'additions' for appending to
track-c-scan-checked.json.
"""
import json, time, urllib.request, urllib.error
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
              "freeused", "freeavailable", "freesharepoolexhausted",
              "freesharesclaimed", "isfreemintavailable", "freeminted",
              "free_slots", "free_supply", "freeslots", "freesupply"]
QUOTE_WORDS = ["quote", "cost", "price", "getprice", "mintprice", "mintcost"]
TARGETS = [
    ("0x44C2F8258164A178109e8402848A35b079A4e790", 92),
    ("0x3D3ab521e50017672918109058F024DCD93E80bb", 48),
    ("0x4A167498A824466cf3f013181baB4C5c4802C1eC", 25),
    ("0x2DD4D75C1793eCd87FB2CAc02d0972Ca0c9Bf2ED", 23),
    ("0xB20a0219F8DFA6b8a097A279D36E55F325d2BABD", 19),
    ("0x10894c3Bd3e6A7ac3331bC66322e93a17D332d31", 18),
    ("0x15eb9812fB0CD71A327C21a9f480734E50e612b3", 14),
    ("0xFC18C76a1BFbd0Db829fB65fE382FCDFee45b340", 13),
]
scan = json.load(open(f"{BASE}/onchain-scan-2026-11-07-1901.json"))
scan_map = {e["address"].lower(): e for e in scan.get("erc20_mint_contracts_list", [])}
checked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
seen = {a.lower() for a in checked.get("checked", [])}
seen |= {k.lower() for k in checked.keys() if k != "checked"}

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

out = {"checked": [], "hits": [], "additions": [],
       "scan_source": "onchain-scan-2026-11-07-1901.json",
       "window": scan.get("from_block"), "window_to": scan.get("to_block")}
for addr, mc in TARGETS:
    e = scan_map.get(addr.lower(), {})
    if addr.lower() in seen:
        print(addr, "SKIP already-checked", flush=True)
        continue
    abi, err = fetch_abi(addr)
    row = {"address": addr, "mint_count": e.get("mint_count", mc),
           "distinct_minters": e.get("distinct_minters"),
           "first_block": e.get("first_block"), "last_block": e.get("last_block"),
           "error": err}
    if abi == "__not_verified__" or not isinstance(abi, list):
        row["shape"] = "not_verified" if abi == "__not_verified__" else "abi-unavailable"
        print(addr, "mints=", row["mint_count"], row["shape"], flush=True)
    else:
        row.update(shape(abi))
        tag = "HIT S1" if row["S1"] else ("HIT S2" if row["S2"]
              else ("agent-mint" if row["agent_mint_shape"] else "no-shape"))
        print(addr, "mints=", row["mint_count"], tag, "mint=", row["mint"][:3],
              "free=", row["free_views"][:4], "reg=", row["registry"], flush=True)
        if row["S1"] or row["S2"]:
            out["hits"].append(row)
    out["checked"].append(row)
    out["additions"].append(addr)
    time.sleep(0.3)

json.dump(out, open(f"{BASE}/run-2026-11-07-1901-5c.json", "w"), indent=1)
print(f"5c DONE checked={len(out['checked'])} hits={len(out['hits'])} "
      f"additions={len(out['additions'])}", flush=True)
