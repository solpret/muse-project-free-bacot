#!/usr/bin/env python3
"""BNB Guardian AI 0x1d3B27e222EFDEd06736C503D52c4884BF0a9117 — from MINTS projects.json (own curl fetch).
Shape-check S1/S2 + Sourcify metadata URL grep (method C). Read-only; writes own run json only."""
import json, subprocess, time
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0x1d3B27e222EFDEd06736C503D52c4884BF0a9117"
MINT = ["mint", "mintfree", "claimfree", "claim", "mintagent", "buyshare", "buyshares", "purchase"]
QUOTE = ["quote", "quotefor", "cost", "costfor", "getcost", "price", "mintprice", "feefor"]
FREE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft", "freeused",
              "freeavailable", "freesharepoolexhausted", "freesharesclaimed",
              "freeminted", "freeremaining", "free_slots", "free_supply", "free_amount",
              "freetokens", "freeperwallet"]
GATE = ["agentid", "agent_id", "agentregistry", "agent_registry", "agentgate",
        "agent_gate", "hasagentid", "isagent"]
def curl_json(url, timeout=25):
    try:
        r = subprocess.run(["curl", "-sS", "--max-time", str(timeout), "-A", "free-mint-web/1.0", url],
                           capture_output=True, text=True, timeout=timeout + 10)
        if r.returncode != 0: return None, f"curl rc={r.returncode} {r.stderr.strip()[:120]}"
        if not r.stdout.strip(): return None, "empty response"
        return json.loads(r.stdout), None
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:120]}"
out = {"address": ADDR, "name": "BNB Guardian AI", "source": "MINTS projects.json (thecolony.ai index, updated 2026-11-06T16:33:31Z)",
       "mints_claim": {"status": "free_live", "added_at": "2026-11-06T09:35:43.097Z", "minted": 1420, "max_supply": 3333, "website_in_index": None}}
abi, status, detail = None, "transport-failed", ""
for attempt in (1, 2):
    d, err = curl_json(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi", timeout=20)
    if d is not None:
        abi = d.get("abi")
        status = "verified" if isinstance(abi, list) else "not_verified"
        detail = f"attempt {attempt}"
        break
    detail = err or "unknown"
    time.sleep(1.0)
out["sourcify"] = status
out["detail"] = detail
if isinstance(abi, list):
    ns = [e.get("name", "").lower() for e in abi if isinstance(e, dict) and e.get("type") == "function"]
    fn = [e.get("name", "") for e in abi if isinstance(e, dict) and e.get("type") == "function"]
    has_mint = any(any(m in n for m in MINT) for n in ns)
    has_quote = any(any(q in n for q in QUOTE) for n in ns)
    has_free = any(any(fv in n for fv in FREE_VIEWS) for n in ns)
    has_gate = any(any(g in n for g in GATE) for n in ns)
    has_token = all(any(t in n for n in ns) for t in ["name", "symbol", "decimals", "totalsupply"])
    noarg_free = any(f.lower() in ("mintfree", "claimfree") for f in fn)
    out.update({"mint": has_mint, "quote": has_quote, "free_view": has_free, "agent_gate": has_gate,
                "is_token": has_token, "noarg_free": noarg_free,
                "S1": bool(has_mint and has_quote and has_free and has_gate),
                "S2": bool(has_token and noarg_free and has_free and has_gate),
                "mint_fns": [f for f in fn if "mint" in f.lower()],
                "quote_fns": [f for f in fn if f.lower() in QUOTE or f.lower().startswith(("quote", "cost"))],
                "free_views": [f for f in fn if f.lower() in FREE_VIEWS],
                "gate_fns": [f for f in fn if any(g in f.lower() for g in GATE)],
                "fn_count": len(fn), "fn_names": fn[:80]})
    out["verdict"] = "SALE-SHAPE-HIT" if (out["S1"] or out["S2"]) else "not-sale-shape"
elif status == "not_verified":
    out.update({"S1": False, "S2": False, "verdict": "not-sale-shape"})
else:
    out.update({"S1": None, "S2": None, "verdict": "shape-check-failed-transport"})
# Sourcify metadata (method C) — URLs in source/metadata
meta, merr = curl_json(f"https://sourcify.dev/server/v2/contract/56/{ADDR}", timeout=20)
out["metadata_fetch"] = "ok" if meta is not None else f"failed: {merr}"
if meta is not None:
    blob = json.dumps(meta)
    import re as _re
    urls = sorted(set(_re.findall(r"https?://[^\s\"'<>\\]+", blob)))
    out["metadata_urls"] = urls
    out["metadata_stdJson_abi_present"] = bool(meta.get("stdJson", {}).get("abi"))
json.dump(out, open(f"{BASE}/run-2026-11-06-2331-bnbguardian.json", "w"), indent=1)
print(json.dumps(out, indent=1))
