#!/usr/bin/env python3
"""Run 2026-11-06 2201 WIB: Sourcify feed shape-check (S1/S2 sale + agent-mint).
Read-only. Writes run-2026-11-06-2201-sourcify-shape.json."""
import json, urllib.request, urllib.error, time

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-2301"
feed = json.load(open(f"{BASE}/run-{TS}-sourcify-feed.json"))
addrs = [(r["address"], r.get("verifiedAt")) for r in feed.get("results", [])]

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
known = set()
for v in snap.get("contracts", {}).values():
    if v.get("address"): known.add(v["address"].lower())
for v in snap.get("track_c", {}).values():
    for k in ("sale", "address", "token"):
        if isinstance(v, dict) and v.get(k): known.add(v[k].lower())
for v in snap.get("excluded", {}).values():
    for k in ("address", "sale", "token"):
        if isinstance(v, dict) and v.get(k): known.add(v[k].lower())
try:
    seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
    seen_keys = {k.lower() for k in seen.keys()} if isinstance(seen, dict) else set()
except Exception:
    seen_keys = set()
try:
    hl = json.load(open(f"{BASE}/hot-leg-seen.json"))
    hl_keys = {k.lower() for k in hl.keys()} if isinstance(hl, dict) else set()
except Exception:
    hl_keys = set()

MINT = ["mint", "mintfree", "claimfree", "claim", "mintagent", "buyshare", "buyshares", "purchase"]
QUOTE = ["quote", "quotefor", "cost", "costfor", "getcost", "price", "mintprice", "feefor"]
FREE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft", "freeused",
              "freeavailable", "freesharepoolexhausted", "freesharesclaimed",
              "freeminted", "freeremaining", "free_slots", "free_supply", "free_amount",
              "freetokens", "freeperwallet"]
GATE = ["agentid", "agent_id", "agentregistry", "agent_registry", "agentgate",
        "agent_gate", "hasagentid", "isagent"]

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.load(r)
        return d.get("abi") or (d.get("stdJson", {}).get("abi")) or None
    except Exception as e:
        return {"_error": str(e)}

def names(abi):
    out = []
    for e in abi or []:
        if isinstance(e, dict) and e.get("name"):
            out.append(e["name"].lower())
    return out

out = []
for addr, va in addrs:
    low = addr.lower()
    status = "known-snapshot" if low in known else ("known-scan-seen" if low in seen_keys else ("known-hotleg-seen" if low in hl_keys else "NEW"))
    rec = {"address": addr, "verifiedAt": va, "status": status}
    if status == "NEW":
        abi = fetch_abi(addr)
        if isinstance(abi, dict) and "_error" in abi:
            rec["abi_error"] = abi["_error"]
        else:
            ns = names(abi)
            has_mint = any(any(m in n for m in MINT) for n in ns)
            has_quote = any(any(q in n for q in QUOTE) for n in ns)
            has_free = any(any(fv in n for fv in FREE_VIEWS) for n in ns)
            has_gate = any(any(g in n for g in GATE) for n in ns)
            has_token = all(any(t in n for n in ns) for t in ["name", "symbol", "decimals", "totalsupply"])
            rec.update({"abi_len": len(abi or []), "mint": has_mint, "quote": has_quote,
                        "free_view": has_free, "agent_gate": has_gate, "is_token": has_token,
                        "S1": bool(has_mint and has_quote and has_free and has_gate),
                        "S2": bool(has_token and has_mint and has_free and has_gate),
                        "fn_names": ns[:60]})
        time.sleep(0.3)
    out.append(rec)

json.dump({"run": TS, "checked_wib": "2026-11-06T23:01:00+07:00", "feed_count": len(addrs),
           "new": [r for r in out if r["status"] == "NEW"],
           "all": out}, open(f"{BASE}/run-{TS}-sourcify-shape.json", "w"), indent=1)
for r in out:
    print(r["address"], r["verifiedAt"], r["status"],
          ("S1=%s S2=%s" % (r.get("S1"), r.get("S2")) if r["status"] == "NEW" else ""))
print("NEW:", sum(1 for r in out if r["status"] == "NEW"),
      "S1:", sum(1 for r in out if r.get("S1")), "S2:", sum(1 for r in out if r.get("S2")))
