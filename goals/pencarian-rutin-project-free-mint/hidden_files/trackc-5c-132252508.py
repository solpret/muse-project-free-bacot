#!/usr/bin/env python3
"""Track-C 5c shape-check, backfill run 132252508-132254477 (read-only).
Sourcify ABI via curl (urllib often fails IncompleteRead/RemoteDisconnected).
S1 = mint + quote/cost + free-share view + registry/AgentGate (all required).
S2 = single-contract token+sale: name/symbol/decimals/totalSupply same
contract; mintFree() no-arg; free views freeClaimed/freeMinted +
FREE_SLOTS/FREE_SUPPLY; agentRegistry; paid mintPaid with PRICE (USDT).
Records newly checked into track-c-scan-checked.json (list + per-address)."""
import json, subprocess, sys

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
CHUNK = "132252508-132254477"
NEW = [
    ("0x7d87480845ABbaeB7cDC7554eC1AB9F758556a86", 100),
    ("0x946E07bdb603717e00EEeC0C6A525394EBb464Ce", 35),
    ("0x34796Cf3d5C3d08e4635472D476e64959a42203B", 25),
    ("0xf1C9f59b2012E669D017926e1f3991a4B5cFE64C", 25),
    ("0xfD8eE0a8C7d0A5222481D274336Cb106267cBeFD", 23),
    ("0xCaE7B3fA7Fbdb96E81A685062DAE114603B6c22d", 22),
    ("0x6078E25d5F27E4c5D8798797b94cEACcB6ebB976", 14),
    ("0x64f4F7eF675F48c488110873439Cb5665bD79681", 12),
]

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        p = subprocess.run(["curl", "-s", "--max-time", "30", url],
                           capture_output=True, text=True, timeout=40)
        d = json.loads(p.stdout)
        if "abi" in d:
            return ("verified", d.get("match"), d.get("abi", []))
        return ("sourcify_error", str(d)[:150], [])
    except Exception as e:
        return ("curl_error", f"{type(e).__name__}:{str(e)[:100]}", [])

def fn_names(abi):
    out = []
    for e in abi:
        if e.get("type") == "function":
            sig = e["name"] + "(" + ",".join(i.get("type", "") for i in e.get("inputs", [])) + ")"
            out.append(sig)
    return out

def shape(abi):
    names = fn_names(abi)
    low = [n.lower() for n in names]
    has = lambda *subs: any(all(s in n for s in subs) for n in low)
    registry = has("agentregistry") or has("agent_id_registry") or has("agentidregistry") or has("agentgate")
    mint_fn = any(n.startswith("mint") for n in low)
    quote_fn = has("quote") or has("costof") or has("pricefor") or has("cost(") or has("getprice") or has("price(")
    free_view = (has("freeclaimed") or has("freeminted") or has("freeleft") or
                 has("freesupply") or has("free_slots") or has("free_supply") or
                 has("freepool") or has("freeshares") or has("freeshare"))
    s1 = mint_fn and quote_fn and free_view and registry
    # S2
    token_self = has("name()") and has("symbol()") and has("decimals()") and has("totalsupply()")
    mintfree = has("mintfree()")
    free_views2 = (has("freeclaimed") or has("freeminted")) and (has("free_slots") or has("free_supply"))
    paid = has("mintpaid") and has("price")
    s2 = token_self and mintfree and free_views2 and registry and paid
    return {
        "registry": registry, "mint_fn": mint_fn, "quote_fn": quote_fn,
        "free_view": free_view, "S1": s1,
        "token_self": token_self, "mintFree": mintfree,
        "free_views2": free_views2, "paid_mintPaid_PRICE": paid, "S2": s2,
        "fn_count": len(names),
        "fn_names": names[:60],
    }

results = []
for addr, mc in NEW:
    status, match, abi = fetch_abi(addr)
    if status == "verified":
        sh = shape(abi)
        note = f"S1={sh['S1']} S2={sh['S2']} (registry={sh['registry']}, mint={sh['mint_fn']}, quote={sh['quote_fn']}, free={sh['free_view']}, fns={sh['fn_count']})"
        rec = {"address": addr, "mint_count": mc, "sourcify": "verified",
               "match": match, "shape": sh, "note": note}
    else:
        rec = {"address": addr, "mint_count": mc, "sourcify": status,
               "match": match, "shape": None,
               "note": f"{status}: {match}"}
    results.append(rec)
    print(addr, "mc=", mc, "|", rec["sourcify"], "|", rec["note"][:160])

hits = [r for r in results if r.get("shape") and (r["shape"]["S1"] or r["shape"]["S2"])]
print("HITS S1/S2:", len(hits))

# record into track-c-scan-checked.json
chk = json.load(open(BASE + "/track-c-scan-checked.json"))
before_list = len(chk.get("checked", []))
for r in results:
    a = r["address"]
    if a not in chk.get("checked", []):
        chk.setdefault("checked", []).append(a)
    chk[a] = {
        "source": f"backfill-{CHUNK}-5c",
        "status": "checked-sale-shape-hit" if (r.get("shape") and (r["shape"]["S1"] or r["shape"]["S2"])) else "checked-not-sale-shape",
        "mint_count": r["mint_count"],
        "note": r["note"],
    }
json.dump(chk, open(BASE + "/track-c-scan-checked.json", "w"), indent=1)
print(f"track-c-scan-checked.json checked list: {before_list} -> {len(chk['checked'])}")

out = {"chunk": CHUNK, "checked_new": len(results), "hits": len(hits),
       "results": results}
json.dump(out, open(BASE + f"/backfill-5c-{CHUNK}.json", "w"), indent=1)
print("wrote backfill-5c-" + CHUNK + ".json")
