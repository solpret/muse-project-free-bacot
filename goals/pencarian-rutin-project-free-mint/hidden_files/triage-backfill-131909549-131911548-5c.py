#!/usr/bin/env python3
"""Track-C 5c for backfill chunk 131909549-131911548 (read-only + state write).
Shape-check max 20 new ERC20 (mint_count>=10, desc) via Sourcify ABI; S1/S2.
Records newly checked into track-c-scan-checked.json (backup first)."""
import json, subprocess, shutil, sys

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
CHUNK = "backfill-131909549-131911548.json"

def sourcify_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    p = subprocess.run(["curl", "-s", "-m", "20", "-A", "Mozilla/5.0", url],
                       capture_output=True, text=True, timeout=30)
    try:
        d = json.loads(p.stdout)
    except Exception:
        return None, f"curl-json-err:{p.stdout[:80]}"
    abi = d.get("abi")
    if isinstance(abi, list):
        return abi, "verified"
    return None, "not_verified"

def main():
    chunk = json.load(open(f"{BASE}/{CHUNK}"))
    lst = chunk["erc20_mint_contracts_list"]
    checked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
    # checked is a dict; 'checked' key holds nested dict; addresses are top-level keys
    def is_checked(a):
        return a.lower() in {k.lower() for k in checked.keys()}
    big = sorted([x for x in lst if x["mint_count"] >= 10], key=lambda x: -x["mint_count"])
    new = [x for x in big if not is_checked(x["address"])][:20]
    print(f">=10: {len(big)}, already checked: {len(big)-len(new)}, new to check: {len(new)}", flush=True)
    out = []
    for x in new:
        addr = x["address"]
        r = {"address": addr, "mint_count": x["mint_count"],
             "distinct_minters": x["distinct_minters"]}
        abi, status = sourcify_abi(addr)
        r["sourcify"] = status
        if abi is None:
            r["S1"] = False; r["S2"] = False
            print(addr, x["mint_count"], "sourcify:", status, "S1=False S2=False", flush=True)
        else:
            fns = sorted({it.get("name", "") for it in abi if it.get("type") == "function"})
            mint_fns = [f for f in fns if f in ("mint", "mintFree", "mintPaid", "mintShare", "buyShare", "claimShare")]
            quote_fns = [f for f in fns if "quote" in f.lower() or "cost" in f.lower() or f in ("getPrice", "price")]
            free_views = [f for f in fns if "free" in f.lower()]
            gate_fns = [f for f in fns if any(g in f.lower() for g in ("agentregistry", "agentgate", "agentid", "agent_id"))]
            token_fns = [f for f in fns if f in ("name", "symbol", "decimals", "totalSupply")]
            r["mint_fns"] = mint_fns; r["quote_fns"] = quote_fns
            r["free_views"] = free_views; r["gate_fns"] = gate_fns; r["token_fns"] = token_fns
            s1 = bool(mint_fns) and bool(quote_fns) and bool(free_views) and bool(gate_fns)
            s2 = (len(token_fns) >= 4 and "mintFree" in fns and bool(free_views)
                  and bool(gate_fns) and ("mintPaid" in fns or "PRICE" in fns))
            r["S1"] = s1; r["S2"] = s2
            print(addr, x["mint_count"], f"verified fns={len(fns)} mint={mint_fns} quote={quote_fns} free={free_views} gate={gate_fns} token={token_fns} S1={s1} S2={s2}", flush=True)
        out.append(r)
        checked[addr] = {"source": "backfill-131909549-131911548-5c",
                         "mint_count": x["mint_count"], "S1": r["S1"], "S2": r["S2"],
                         "sourcify": r["sourcify"]}
    json.dump(out, open(f"{BASE}/triage-backfill-131909549-131911548-5c.json", "w"), indent=1)
    shutil.copy(f"{BASE}/track-c-scan-checked.json",
                f"{BASE}/track-c-scan-checked.json.bak-5c-131909549-131911548")
    json.dump(checked, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)
    hits = [r for r in out if r.get("S1") or r.get("S2")]
    print(f"5c done: {len(out)} checked, S1/S2 hits: {len(hits)}", flush=True)
    for h in hits:
        print("HIT:", json.dumps(h), flush=True)

if __name__ == "__main__":
    main()
