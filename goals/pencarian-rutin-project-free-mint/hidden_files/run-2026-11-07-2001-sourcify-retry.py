#!/usr/bin/env python3
"""Retry 5a Sourcify ABI fetch via curl for the 13 IncompleteRead failures
(run 2001). Updates run-2026-11-07-2001-sourcify.json in place + appends
to run-2026-11-07-2001-sourcify.log. READ-ONLY otherwise."""
import json, subprocess, time
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
              "freeused", "freeavailable", "freesharepoolexhausted",
              "freesharesclaimed", "isfreemintavailable", "freeminted",
              "free_slots", "free_supply", "freeslots", "freesupply"]
QUOTE_WORDS = ["quote", "cost", "price", "getprice", "mintprice", "mintcost"]

def shape(abi):
    fns = [e for e in abi if isinstance(e, dict) and e.get("type") == "function"]
    names = [f.get("name", "").lower() for f in fns]
    name_set = set(names)
    raw = json.dumps(abi).lower()
    mint = [n for n in names if n.startswith("mint") or n in ("claim", "claimfree")]
    quote = [n for n in names if any(w in n for w in QUOTE_WORDS)]
    freev = [n for n in names if n in FREE_VIEWS]
    has_reg = REGISTRY in raw or "agentregistry" in name_set or "agentgate" in name_set
    is_token = len({"name", "symbol", "decimals", "totalsupply"} & name_set) >= 3
    noarg_free = any(f.get("name", "").lower() in ("mintfree", "claimfree")
                     and len(f.get("inputs", [])) == 0 for f in fns)
    s1 = bool(mint) and bool(quote) and bool(freev) and has_reg
    s2 = is_token and noarg_free and bool(freev) and has_reg
    return {"fns": len(fns), "mint": mint[:4], "quote": quote[:4],
            "free_views": freev[:6], "registry": has_reg,
            "is_token": is_token, "noarg_free": noarg_free,
            "S1": s1, "S2": s2,
            "agent_mint_shape": bool(mint) and bool(freev) and has_reg}

def fetch_abi_curl(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    p = subprocess.run(["curl", "-sS", "--max-time", "25", url],
                       capture_output=True, text=True, timeout=30)
    if p.returncode != 0:
        return None, f"curl:{p.returncode}:{p.stderr[:120]}"
    try:
        d = json.loads(p.stdout)
    except Exception as e:
        return None, f"json:{e}"
    if d.get("abi") is None:
        return "__not_verified__", "no-abi-field"
    return d["abi"], None

out = json.load(open(f"{BASE}/run-2026-11-07-2001-sourcify.json"))
log = open(f"{BASE}/run-2026-11-07-2001-sourcify.log", "a")
targets = [r for r in out["checked"] if r.get("shape") == "abi-unavailable"]
print(f"retry: {len(targets)} abi-unavailable via curl", flush=True)
log.write(f"--- curl retry {len(targets)} abi-unavailable ---\n")
for row in targets:
    addr = row["address"]
    abi, err = fetch_abi_curl(addr)
    if not isinstance(abi, list):
        row["shape"] = "not_verified" if abi == "__not_verified__" else "abi-unavailable"
        row["error"] = f"curl-retry:{err}"
        print(addr, row["shape"], row["error"], flush=True)
        log.write(f"{addr} {row['shape']} {row['error']}\n")
    else:
        row.pop("shape", None)
        row["error"] = None
        row["shape"] = "retried-via-curl"
        row.update(shape(abi))
        tag = "HIT S1" if row["S1"] else ("HIT S2" if row["S2"]
              else ("agent-mint" if row["agent_mint_shape"] else "no-shape"))
        print(addr, tag, "mint=", row["mint"][:3], "free=", row["free_views"][:4],
              "reg=", row["registry"], flush=True)
        log.write(f"{addr} {tag} mint={row['mint'][:3]} free={row['free_views'][:4]} reg={row['registry']}\n")
        if row["S1"] or row["S2"] or row["agent_mint_shape"]:
            out["hits"].append(row)
    time.sleep(0.3)
json.dump(out, open(f"{BASE}/run-2026-11-07-2001-sourcify.json", "w"), indent=1)
print(f"SOURCIFY RETRY DONE hits={len(out['hits'])}", flush=True)
log.write(f"SOURCIFY RETRY DONE hits={len(out['hits'])}\n")
log.close()
