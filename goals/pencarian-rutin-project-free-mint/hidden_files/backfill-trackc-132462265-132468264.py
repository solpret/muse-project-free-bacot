#!/usr/bin/env python3
"""Track-C 5c for backfill run 2026-11-09 ~06:30 WIB, window 132462265-132468264 (driver exit 2, partial - chunk 1 rc=2, chunk 2-3 rc=0).
Read-only. Combines erc20_mint_contracts_list from ALL chunk JSONs, mint_count>=10,
sorted desc, shape-checks max 20 NEW (total) via Sourcify ABI (curl fallback),
skips addresses already in track-c-scan-checked.json (union of top-level keys
+ 'checked' list). Records newly checked as top-level keys. No preview/mint.
S1 = mint + quote/cost + free-share view + registry/AgentGate (all required).
S2 = single-contract token+sale: name/symbol/decimals/totalSupply + mintFree()
no-arg + freeClaimed/freeMinted + FREE_SLOTS/FREE_SUPPLY + agentRegistry +
mintPaid with PRICE (USDT).
"""
import json, subprocess, sys
from datetime import datetime, timezone

CHUNKS = ["backfill-132462265-132464264.json", "backfill-132464265-132466264.json", "backfill-132466265-132468264.json"]
CHECKED_FILE = "track-c-scan-checked.json"
OUT = "backfill-trackc-132462265-132468264.json"
RUN = "backfill-132462265-132468264-5c"
NOW_WIB = datetime.now(timezone.utc).astimezone(
    timezone(__import__("datetime").timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")

def sourcify_abi(addr):
    try:
        r = subprocess.run(
            ["curl", "-s", "-m", "30",
             f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
            capture_output=True, text=True, timeout=40)
        d = json.loads(r.stdout)
        if isinstance(d.get("abi"), list):
            return {"match": d.get("match"), "fns": sorted({
                e["name"] for e in d["abi"] if e.get("type") == "function"})}
        return {"match": d.get("match"), "fns": []}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:100]}"}

def classify(fns):
    s = set(fns)
    has_mint = bool(s & {"mint", "mintFree", "claimFreeShare", "mintPaid", "mintWithAgentTokenId"})
    has_quote = bool(s & {"quote", "costOf", "mintCost", "price", "PRICE", "currentPrice", "getQuote"})
    has_free = bool(s & {"freeShares", "freeShareClaimedBy", "freeSharesRemaining",
                         "FREE_SHARES_TOTAL", "freeClaimed", "freeMinted", "freeLeft",
                         "freeOf", "freeUsed", "freeCount", "FREE_CAP", "FREE_SLOTS",
                         "FREE_SUPPLY", "freeFor", "claimFreeShare"})
    has_reg = bool(s & {"agentRegistry", "agentIdRegistry", "AGENT_REGISTRY",
                        "AGENT_ID", "REGISTRY", "agentIds", "AgentGate"})
    s1 = has_mint and has_quote and has_free and has_reg
    s2 = ("mintFree" in s and has_free and
          bool(s & {"FREE_SLOTS", "FREE_SUPPLY"}) and has_reg and
          "mintPaid" in s)
    return s1, s2, {"mint": has_mint, "quote": has_quote, "free": has_free, "registry": has_reg}

def main():
    combined = {}
    for f in CHUNKS:
        d = json.load(open(f))
        for e in d.get("erc20_mint_contracts_list", []):
            a = e.get("address", "")
            if not a:
                continue
            combined[a] = combined.get(a, 0) + int(e.get("mint_count", 0))
    cands = sorted(((a, c) for a, c in combined.items() if c >= 10),
                   key=lambda x: -x[1])
    checked = json.load(open(CHECKED_FILE))
    already = {k.lower() for k in checked if isinstance(k, str) and k.startswith("0x")}
    cl = checked.get("checked", [])
    if isinstance(cl, list):
        for it in cl:
            if isinstance(it, str) and it.startswith("0x"):
                already.add(it.lower())
            elif isinstance(it, dict) and it.get("address"):
                already.add(it["address"].lower())
    elif isinstance(cl, dict):
        already |= {k.lower() for k in cl}
    new = [(a, c) for a, c in cands if a.lower() not in already][:20]
    skipped_already = sum(1 for a, c in cands if a.lower() in already)
    dropped = max(0, len([1 for a, c in cands if a.lower() not in already]) - 20)
    results = {}
    hits = []
    for addr, mc in new:
        info = sourcify_abi(addr)
        if "error" in info:
            results[addr] = {"error": info["error"], "mint_count": mc}
            note = "Sourcify fetch error"
            status = "checked-error"
        else:
            fns = info["fns"]
            s1, s2, parts = classify(fns)
            results[addr] = {"match": info["match"], "fns": sorted(fns),
                             "S1": s1, "S2": s2, "parts": parts, "mint_count": mc}
            note = f"S1={s1} S2={s2} (mint={parts['mint']} quote={parts['quote']} free={parts['free']} registry={parts['registry']})"
            status = "checked-sale-shape-HIT" if (s1 or s2) else "checked-not-sale-shape"
            if s1 or s2:
                hits.append(addr)
        checked[addr] = {"source": RUN, "status": status, "mint_count": mc,
                         "note": note, "checked_wib": NOW_WIB}
    json.dump(checked, open(CHECKED_FILE, "w"), indent=1)
    summary = {"run": RUN, "window": "132462265-132468264", "checked_wib": NOW_WIB,
               "erc20_unique_combined": len(combined),
               "candidates_mint_count_ge10": len(cands),
               "already_checked_skipped": skipped_already,
               "new_checked": len(new), "sampling_dropped": dropped,
               "sale_shape_hits": hits, "results": results}
    json.dump(summary, open(OUT, "w"), indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k != "results"}, indent=1))
    for addr, r in results.items():
        print(addr, "mc=", r.get("mint_count"), r.get("match"),
              "S1=", r.get("S1"), "S2=", r.get("S2"),
              r.get("error", ""), (r.get("parts") or ""))

if __name__ == "__main__":
    main()
