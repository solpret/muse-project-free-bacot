#!/usr/bin/env python3
"""Track-C 5c shape-check for run 2201 (2026-11-08). Read-only.
S1: mint fn + quote/cost fn + free-share view + registry ref/AgentGate.
S2: token fns (name/symbol/decimals/totalSupply) + no-arg free-mint fn
    + free views + registry ref/AgentGate.
Sourcify via urllib, curl fallback (lesson: urllib IncompleteRead)."""
import sys, json, urllib.request, urllib.error, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from fast_rpc import batch as _batch

REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
REGISTRY_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_SHARE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
                    "freeUsed", "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed"]
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]

def call(method, params, timeout=15):
    last = None
    for ep in EPS:
        try:
            return _batch([(method, params)], endpoint=ep, timeout=timeout)[0]
        except Exception as e:
            last = e
    raise last

def sourcify_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return "verified", json.loads(resp.read().decode()).get("abi")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "not_verified", None
        return f"http_{e.code}", None
    except Exception:
        pass
    try:
        p = subprocess.run(["curl", "-sS", "-m", "20", "-A", "Mozilla/5.0", url],
                           capture_output=True, text=True, timeout=30)
        if p.returncode == 0 and p.stdout.strip():
            return "verified(curl)", json.loads(p.stdout).get("abi")
        return f"curl_error_rc={p.returncode}", None
    except Exception as e:
        return f"curl_error:{type(e).__name__}", None

def shape_check(addr):
    status, abi = sourcify_abi(addr)
    r = {"sourcify": status}
    if not isinstance(abi, list):
        r["verdict"] = "no-shape (Sourcify ABI unavailable)"
        return r
    fns = [i for i in abi if i.get("type") == "function"]
    names = [f.get("name", "") for f in fns]
    r["abi_functions"] = sorted(set(names))
    lower = [n.lower() for n in names]
    has_mint = any("mint" in n for n in lower)
    has_quote = any("quote" in n or "cost" in n for n in lower)
    free_views = sorted({n for n in names if n in FREE_SHARE_VIEWS})
    has_free_view = bool(free_views)
    gate_names = [n for n in names if n in ("agentRegistry", "AGENT_REGISTRY", "AGENT_ID_REGISTRY", "AGENT_ID")]
    try:
        code = call("eth_getCode", [addr, "latest"])
        reg_bytes = isinstance(code, str) and REGISTRY_BYTES in code[2:].lower()
    except Exception as e:
        reg_bytes = None
        r["getCode_error"] = str(e)[:120]
    r["registry_bytes_hit"] = reg_bytes
    r["gate_functions"] = gate_names
    registry_ref = bool(gate_names) or reg_bytes is True
    # S1
    s1 = has_mint and has_quote and has_free_view and registry_ref
    r["S1"] = {"mint_fn": has_mint, "quote_cost_fn": has_quote,
               "free_views": free_views, "registry_ref": registry_ref, "pass": s1}
    # S2
    token_fns = {"name", "symbol", "decimals", "totalSupply"}
    has_token = token_fns <= set(names)
    noarg_free = [f["name"] for f in fns
                  if "free" in f.get("name", "").lower() and "mint" in f.get("name", "").lower()
                  and len(f.get("inputs", [])) == 0]
    free_views2 = sorted({n for n in names if n in ("freeClaimed", "freeMinted")})
    free_consts = sorted({n for n in names if n in ("FREE_SLOTS", "FREE_SUPPLY")})
    s2 = has_token and bool(noarg_free) and bool(free_views2) and bool(free_consts) and registry_ref
    r["S2"] = {"token_fns": has_token, "noarg_free_mint": noarg_free,
               "free_views": free_views2, "free_consts": free_consts,
               "registry_ref": registry_ref, "pass": s2}
    r["verdict"] = "SALE-SHAPE HIT S1" if s1 else ("SALE-SHAPE HIT S2" if s2 else "no-shape")
    return r

if __name__ == "__main__":
    targets = json.load(open(sys.argv[1]))  # [{address, mint_count, ...}]
    out = {}
    for t in targets:
        a = t["address"]
        print(f"5c checking {a} mint_count={t['mint_count']}", flush=True)
        r = shape_check(a)
        r["mint_count"] = t["mint_count"]
        r["distinct_minters"] = t.get("distinct_minters")
        r["first_block"] = t.get("first_block")
        out[a] = r
        print(f"  -> {r['verdict']} (sourcify={r['sourcify']})", flush=True)
    with open(sys.argv[2], "w") as f:
        json.dump(out, f, indent=1)
    print("wrote", sys.argv[2])
