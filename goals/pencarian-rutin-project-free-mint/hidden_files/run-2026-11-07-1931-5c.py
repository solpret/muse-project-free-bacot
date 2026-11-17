#!/usr/bin/env python3
"""5c triage run 1931: shape-check NEW ERC-20 from scan 1931
(mint_count>=10, none checked yet), Sourcify ABI sale-shape test S1/S2.
Correct endpoint /v2/contract/56/{addr}?fields=abi.
Read-only except writing run-2026-11-07-1931-5c.json; newly checked
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
TARGETS = [('0x7d4a66144A53221303281934b868D7CAf5E7c82E', 124), ('0x8c524d7a9D4F6fca8D7aaF0a529595c2d1b9a2c6', 31), ('0x912A5aC3e5483e28CeF91794693b1e7f83a12F67', 26), ('0xcA0F6cc2A6BC620157c962036316710C12306f23', 26), ('0x9715E0048C21dAD6061Cb088F8a939f4bCB3C4a1', 24), ('0x1a8C1d1FadC18a7a3d942676886F120cfdEebf79', 22), ('0x8176E3953F4F1D26E6e7f2CaE814F10bCa6240Ff', 20), ('0x9f6f3d84f36c03DCb3566f41623D85b8c72f5d53', 17), ('0x40Aec18c5aE4fd49970758023C15fd05598FE70c', 16), ('0xD8074277641f8bE95b96CDeea2D4C742fd6C699c', 13), ('0xD6366A6ff402310EdCa1146Cda7cD9A1a514612c', 11), ('0x6f710A128cabc76efB9EbEe06A2a7c65cb83FCFa', 10), ('0xeeB5840F698a6d90Cc29C2Ca80F0B9347dB1a8b6', 10)]
scan = json.load(open(f"{BASE}/onchain-scan-2026-11-07-1931.json"))
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
       "scan_source": "onchain-scan-2026-11-07-1931.json",
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

json.dump(out, open(f"{BASE}/run-2026-11-07-1931-5c.json", "w"), indent=1)
print(f"5c DONE checked={len(out['checked'])} hits={len(out['hits'])} "
      f"additions={len(out['additions'])}", flush=True)
