#!/usr/bin/env python3
"""One bounded retry of leg 2 (Boltbook EN+ZH) for hot-leg run 2026-11-18 14:14 WIB.
Leg 2 failed inside the main run (curl timeout, no html files written); direct
curl now returns 200. Single retry only; no loop. Updates hot-leg-seen.json for
any genuinely new contract found, and writes the retry supplement JSON."""
import json, re, subprocess, time
from datetime import datetime, timezone, timedelta
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
T0 = time.time()
out = {"run": "free-mint-hot-leg 2026-11-18 14:14 WIB - leg2 single retry", "started_wib": now_wib}
seen = json.load(open(f"{HF}/hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted",
              "freeCardsRemaining"}
def fetch(lang):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    path = f"{HF}/hot-leg-2026-11-18-1414-boltbook-{lang}.html"
    r = subprocess.run(["curl", "-s", "-L", "-A",
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
                        "--max-time", "25", url, "-o", path, "-w", "%{http_code}"],
                       capture_output=True, text=True, timeout=30)
    code = r.stdout.strip()
    html = open(path, encoding="utf-8", errors="replace").read()
    addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
    new = [a for a in addrs if a.lower() not in seen_l and a.lower() not in EXCLUDED
           and a.lower() != REGISTRY.lower()]
    text = re.sub(r"<[^>]+>", " ", html); text = re.sub(r"\s+", " ", text)
    figs = []
    for m in re.finditer(r"(.{0,40}\d[\d,]*/\d[\d,]{2,}.{0,10})", text):
        s = m.group(1).strip()
        if len(s) > 12: figs.append(s)
    return {"bytes": len(html), "http_code": code, "full_address_contracts": len(addrs),
            "addresses": addrs, "new": len(new), "new_contracts": new,
            "free_kw": len(re.findall(r"free", html, re.I)),
            "zh_free_kw": len(re.findall(r"\u514d\u8d39", html)), "figures": figs[:25]}
def shape_check(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    r = subprocess.run(["curl", "-s", "-L", "--max-time", "20", url],
                       capture_output=True, timeout=25)
    meta = json.loads(r.stdout.decode())
    abi = meta.get("abi", [])
    fns = {}
    for e in abi:
        if e.get("type") == "function": fns.setdefault(e["name"], []).append(e)
    names = set(fns)
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
    free_views = sorted(names & FREE_VIEWS)
    agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate"})
    is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
    s1 = has_mint and has_quote and bool(free_views) and agent_ref
    mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
    s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) \
        and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
    return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
            "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token,
            "n_fns": len(names), "status": "checked", "verifiedAt": meta.get("verifiedAt")}
targets = []
for lang in ("en", "zh"):
    try:
        out[f"boltbook_{lang}"] = fetch(lang)
        targets += [a for a in out[f"boltbook_{lang}"]["new_contracts"]]
    except Exception as e:
        out[f"boltbook_{lang}"] = {"error": f"{type(e).__name__}: {str(e)[:150]}",
                                   "note": "retry also failed - leg 2 stays skipped, retried next run"}
targets = list(dict.fromkeys(targets))
out["shape_check_targets"] = targets
sc = []
for a in targets:
    try:
        sc.append(shape_check(a))
    except Exception as e:
        sc.append({"address": a, "status": "shape-check-failed", "error": f"{type(e).__name__}: {str(e)[:120]}"})
out["shape_check"] = sc
out["shape_hits"] = [s for s in sc if s.get("S1") or s.get("S2")]
added = []
for s in sc:
    if s.get("status") != "checked": continue
    a = s["address"]
    seen[a] = {"first_seen_wib": now_wib, "source": "boltbook-retry-1414",
               "status": "sale-shape" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape",
               "note": json.dumps(s)[:600], "verifiedAt": s.get("verifiedAt")}
    added.append(a)
out["seen_added"] = added
out["seen_n"] = len(seen)
json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)
out["elapsed_s"] = round(time.time() - T0, 1)
out["executions"] = "none - read-only retry"
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-18-1414-boltbook-retry.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:8000])
