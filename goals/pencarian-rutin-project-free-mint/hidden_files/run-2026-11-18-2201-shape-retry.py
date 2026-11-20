#!/usr/bin/env python3
"""Direct retry of the 7 Sourcify ABI shape-checks that failed (curl rc=28) at
hot-leg 2154, done OUTSIDE the hot-leg-seen filter (they are recorded in seen
as attempted, so both main-run and hot-leg filters skip them). Read-only.
Writes run-2026-11-18-2201-shape-retry.json."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.quicknode/bin")
from quicknode import ProxyHTTPSConnection
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TARGETS = ["0x13b08F3C65661fCD27Cf3DD09168b5e1DF93ee27", "0xeae2b0FFa3676898Edacb8E4D111ed305Cb4584B",
           "0x67419c348EE5f7D6EBfA085511C34062EF217069", "0x1Fbc07bCe6D3A384890879A31cc694266D653Fa6",
           "0x1C0e0fBe2b29C05a41C3e762ea6394AF78c78F27", "0x595010667AB6E89BB4d25C66788dfd74688946a9",
           "0x0883ba789DD45a94fBc8a7eD116c20e516228309"]
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed", "freeAvailable",
              "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted", "freeCardsRemaining"}
def https_get(host, path, timeout=25):
    conn = ProxyHTTPSConnection(host, 443, timeout=timeout)
    try:
        conn.request("GET", path, headers={"User-Agent": UA, "Accept": "*/*"})
        resp = conn.getresponse(); raw = resp.read(); status = resp.status
    finally:
        conn.close()
    return status, raw
def shape_check(addr):
    t0 = time.time()
    try:
        st2, raw2 = https_get("sourcify.dev", f"/server/v2/contract/56/{addr}?fields=abi", timeout=25)
        meta2 = json.loads(raw2.decode()); abi = meta2.get("abi", [])
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
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token,
                "n_fns": len(names), "status": "checked", "verifiedAt": meta2.get("verifiedAt"),
                "elapsed_s": round(time.time() - t0, 1)}
    except Exception as e:
        return {"address": addr, "status": "shape-check-failed", "error": f"{type(e).__name__}: {str(e)[:120]}",
                "elapsed_s": round(time.time() - t0, 1)}
sc = [shape_check(a) for a in TARGETS]
out = {"run": "free-mint-search 2026-11-18 22:01 WIB shape-retry (7 addrs from hot-leg 2154)",
       "results": sc,
       "sale_shape": [x for x in sc if x.get("S1") or x.get("S2")]}
json.dump(out, open(f"{HF}/run-2026-11-18-2201-shape-retry.json", "w"), indent=1)
for x in sc:
    print(x["address"], x.get("status"), "S1=", x.get("S1"), "S2=", x.get("S2"),
          "free_views=", x.get("free_views"), "agent_ref=", x.get("agent_ref"), x.get("error", ""))
print("SALE_SHAPE:", out["sale_shape"])
