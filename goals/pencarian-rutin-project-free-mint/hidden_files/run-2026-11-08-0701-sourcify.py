#!/usr/bin/env python3
"""Run 2026-11-08 0701 Route 5: poll Sourcify recently-verified feed
(chain 56, limit 20, sort desc), fetch ABI per new contract, classify
mint-shape (S1/S2 sale-shape + NFT mint-shape: free-mint fn / free-supply
constant / AgentGate / registry ref). Cross-check vs scan findings
(scan contracts set) happens at the end; contracts found by both legs
are still reported ONCE. READ-ONLY; writes run-2026-11-08-0701-sourcify.json.
Hot leg 0659 already checked 0xfc97f4Ab89e73D8873BD0940dff995c8165C3eBb
(mint=true, token=true, no quote/free/agent) - NOT agent-shaped, NOT
sale-shape; do not re-report."""
import json, subprocess, datetime, sys, time
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-08-0701"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
HOTLEG_CHECKED = "0xfc97f4ab89e73d8873bd0940dff995c8165c3ebb"

FEED = "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"
feed = None
try:
    r = subprocess.run(["curl", "-sS", "--max-time", "30", FEED],
                       capture_output=True, text=True, timeout=40)
    feed = json.loads(r.stdout)
    print(f"feed OK: {len(feed.get('results', []))} contracts", flush=True)
except Exception as e:
    print(f"feed fetch FAILED: {e}", flush=True)
    feed = {"results": [], "error": str(e)}

GATE_WORDS = ["agentid", "agent_id", "agentregistry", "agent_registry",
              "agentgate", "agent_gate", "hasagentid", "isagent"]
FREE_SHARE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
                    "freeused", "freeavailable", "freesharepoolexhausted",
                    "freesharesclaimed", "freeminted", "freeremaining",
                    "free_slots", "free_supply", "free_amount"]
QUOTE_FNS = ["quote", "quotefor", "quotemint", "quotemintfor", "cost", "costfor",
             "getcost", "price", "mintprice", "feefor"]

def classify(abi):
    funcs = [it.get("name", "") for it in abi if isinstance(it, dict) and it.get("type") == "function"]
    mint_fns = [f for f in funcs if "mint" in f.lower()]
    quote_fns = [f for f in funcs if f.lower() in QUOTE_FNS or f.lower().startswith("quote") or f.lower().startswith("cost")]
    free_views = [f for f in funcs if f.lower() in FREE_SHARE_VIEWS]
    gate = [f for f in funcs if any(g in f.lower() for g in GATE_WORDS)]
    token_fns = [f for f in funcs if f.lower() in ("name", "symbol", "decimals", "totalsupply")]
    noarg_free = [f for f in funcs if f.lower() in ("mintfree", "claimfree")]
    free_funcs = [f for f in funcs if "free" in f.lower() and not f.lower().startswith("freeze")]
    s1 = bool(mint_fns) and bool(quote_fns) and bool(free_views) and bool(gate)
    s2 = len(token_fns) >= 3 and bool(noarg_free) and bool(free_views) and bool(gate)
    mint_shape = bool(mint_fns) and (bool(free_funcs) or bool(gate))
    return {"mint_fns": mint_fns, "quote_fns": quote_fns, "free_views": free_views,
            "gate_fns": gate, "token_fns": token_fns, "noarg_free": noarg_free,
            "free_funcs": free_funcs, "S1": s1, "S2": s2, "mint_shape": mint_shape}

def sourcify_abi(addr):
    try:
        r = subprocess.run(["curl", "-sS", "--max-time", "20",
                            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                           capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and r.stdout.strip():
            d = json.loads(r.stdout)
            if d.get("abi") is not None:
                return ("verified", d.get("abi"))
            return ("not_verified", None)
    except Exception as e:
        print("  curl sourcify err", addr, e, flush=True)
    import urllib.request, urllib.error
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",
                                     headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            d = json.loads(resp.read().decode())
            return ("verified", d.get("abi")) if d.get("abi") is not None else ("not_verified", None)
    except urllib.error.HTTPError as ex:
        return ("not_verified" if ex.code == 404 else f"error:{ex.code}", None)
    except Exception as ex:
        return (f"error:{ex}", None)

now_wib = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
results = feed.get("results", [])
# scan cross-check set (may not exist yet if scan still running)
scan_addrs = set()
try:
    scan = json.load(open(f"{BASE}/onchain-scan-2026-11-08-0701.json"))
    scan_addrs = {c["address"].lower() for c in scan.get("contracts", [])}
    scan_addrs |= {e["address"].lower() for e in scan.get("erc20_mint_contracts_list", [])}
    print(f"scan file present: {len(scan_addrs)} addrs for cross-check", flush=True)
except Exception as e:
    print(f"scan file not yet available for cross-check ({e}); cross-check deferred to triage stage", flush=True)

out = []
for item in results:
    a = item.get("address", "")
    r = {"address": a, "verifiedAt": item.get("verifiedAt"), "match": item.get("match")}
    if a.lower() == HOTLEG_CHECKED:
        r["note"] = "SUDAH DICEK hot leg 0659: mint=true token=true tanpa quote/free/agent - BUKAN agent-shaped, BUKAN sale-shape; tidak dicek ulang, tidak dilaporkan"
        r["sourcify"] = "verified"; r["S1"] = False; r["S2"] = False; r["mint_shape"] = False
        r["in_scan_window"] = a.lower() in scan_addrs
        out.append(r)
        print("FEED", a, "-> hot-leg already checked, skip", flush=True)
        continue
    st, abi = sourcify_abi(a)
    r["sourcify"] = st
    if isinstance(abi, list):
        r.update(classify(abi))
        r["fns"] = len(abi)
    else:
        r["S1"] = False; r["S2"] = False; r["mint_shape"] = False; r["fns"] = 0
    r["in_scan_window"] = a.lower() in scan_addrs
    out.append(r)
    print("FEED", a, "verifiedAt=", r["verifiedAt"], "S1=", r.get("S1"), "S2=", r.get("S2"),
          "mint_shape=", r.get("mint_shape"), "in_scan=", r["in_scan_window"],
          "mint=", r.get("mint_fns"), "quote=", r.get("quote_fns"),
          "free=", r.get("free_views"), "gate=", r.get("gate_fns"), flush=True)
    time.sleep(0.2)

hits = [r for r in out if r.get("S1") or r.get("S2") or r.get("mint_shape")]
result = {"run": TS, "checked_wib": now_wib, "feed_url": FEED,
          "feed_count": len(results), "feed_error": feed.get("error"),
          "results": out, "hits": hits,
          "cross_check_note": "contracts found by both feed and scan legs are reported ONCE"}
json.dump(result, open(f"{BASE}/run-{TS}-sourcify.json", "w"), indent=1)
print("SOURCIFY DONE hits:", [r["address"] for r in hits], flush=True)
