#!/usr/bin/env python3
"""Hot-leg 1819 retry: curl fallback for failed Sourcify shape checks + Boltbook EN/ZH via curl."""
import json, re, subprocess
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
def curl(url, timeout=25):
    r = subprocess.run(["curl","-sS","--max-time",str(timeout),"-A","free-mint-hot-leg/1819",url],
                       capture_output=True, text=True)
    if r.returncode != 0: raise RuntimeError(r.stderr.strip()[:150])
    return r.stdout
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
def shape(addr):
    meta = json.loads(curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"))
    abi = meta.get("abi", [])
    names = {e["name"] for e in abi if e.get("type") == "function"}
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
    free_views = sorted(names & set(FREE_VIEWS))
    agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
    is_token = bool(names & {"name","symbol","decimals","totalSupply"})
    s1 = has_mint and has_quote and bool(free_views) and agent_ref
    s2 = is_token and ("mintFree" in names) and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
    return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
            "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token, "n_fns": len(names)}
out = json.load(open(BASE+"hot-leg-2026-11-16-1819-feedshape.json"))
for i, o in enumerate(out):
    if "error" in o:
        try:
            out[i] = shape(o["address"]); print("RETRY OK", json.dumps(out[i]))
        except Exception as ex:
            print("RETRY FAIL", o["address"], type(ex).__name__, str(ex)[:120])
json.dump(out, open(BASE+"hot-leg-2026-11-16-1819-feedshape.json","w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
print("STILL_ERR:", [o["address"] for o in out if "error" in o])
# Boltbook via curl
for lang in ("en","zh"):
    url = "https://boltbook.fun/?lang="+lang
    try:
        html = curl(url, timeout=30)
        open(BASE+f"hot-leg-2026-11-16-1819-boltbook-{lang}.html","w").write(html)
        found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
        print(f"BOLTBOOK {lang}: {len(html)} bytes, {len(found)} addrs")
        for a in found: print("  ", a)
        json.dump(found, open(BASE+f"hot-leg-2026-11-16-1819-boltbook-{lang}.json","w"))
    except Exception as ex:
        print(f"BOLTBOOK {lang} FAILED: {type(ex).__name__}: {ex}")
