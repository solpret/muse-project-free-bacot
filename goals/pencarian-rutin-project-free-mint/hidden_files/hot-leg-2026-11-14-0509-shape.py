#!/usr/bin/env python3
"""Hot-leg 0509 (2026-11-14): shape-check 5 NEW Sourcify feed contracts
(verified 21:51-21:59 UTC 13 Nov, first seen in feed crawl 22:12 UTC).
Read-only; curl 60s per ABI fetch (egress slow, 8s probes fail).
Writes hot-leg-run-2026-11-14-0509-shape.json. No preview/mint."""
import json, subprocess, time

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
NEW = [
    ("0xCc3cc99dDE77E707a3e444B2084A626ae2C7E033", "2026-11-13T21:59:11Z"),
    ("0xc90131A1BD1e599F308c8461485810011CA0a5aE", "2026-11-13T21:55:43Z"),
    ("0x073E8177923c7b3bA74ac573CE6a34eF62886fd1", "2026-11-13T21:55:41Z"),
    ("0x4d8Ad8395A4F54aD96C2Cc13D41aB715265d2039", "2026-11-13T21:55:38Z"),
    ("0x07f256D8De05Fb16974D634ebb03f78a8Dd16B56", "2026-11-13T21:51:51Z"),
]

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        p = subprocess.run(["curl", "-sS", "-m", "60", "-A", "Mozilla/5.0", url],
                           capture_output=True, text=True, timeout=70)
        if p.returncode != 0 or not p.stdout:
            return None, f"curl rc={p.returncode} err={p.stderr[:100]}"
        meta = json.loads(p.stdout)
        abi = meta.get("abi", [])
        return abi, None
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:120]}"

def shape(addr, verified_at):
    abi, err = fetch_abi(addr)
    if abi is None:
        return {"address": addr, "verifiedAt": verified_at, "S1": None, "S2": None,
                "error": err, "status": "shape-check-failed"}
    names = set()
    for e in abi:
        if e.get("type") == "function":
            names.add(e["name"])
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
    free_views = sorted(names & set(FREE_VIEWS))
    agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId",
                              "agentGate", "AgentGate", "AGENT_ID_REGISTRY", "agentIdRegistry"})
    is_token = bool({"name", "symbol", "decimals", "totalSupply"} <= names)
    fns = {}
    for e in abi:
        if e.get("type") == "function":
            fns.setdefault(e["name"], []).append(e)
    mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
    s1 = bool(has_mint and has_quote and free_views and agent_ref)
    s2 = bool(is_token and mintfree and (names & {"freeClaimed", "freeMinted"})
              and (names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref)
    return {"address": addr, "verifiedAt": verified_at, "S1": s1, "S2": s2,
            "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
            "agent_ref": agent_ref, "is_token": is_token, "n_fns": len(names),
            "functions": sorted(names), "status": "checked"}

t0 = time.time()
out = {"run": "free-mint-hot-leg 2026-11-14 05:09 WIB shape-check",
       "started_wib": time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time() + 7 * 3600)),
       "results": [shape(a, v) for a, v in NEW]}
out["s1_pass"] = [r["address"] for r in out["results"] if r.get("S1")]
out["s2_pass"] = [r["address"] for r in out["results"] if r.get("S2")]
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-14-0509-shape.json", "w"), indent=1)
for r in out["results"]:
    print(r["address"], "S1=", r.get("S1"), "S2=", r.get("S2"),
          "mint=", r.get("has_mint"), "quote=", r.get("has_quote"),
          "free=", r.get("free_views"), "agent=", r.get("agent_ref"),
          "token=", r.get("is_token"), "err=", r.get("error"))
print("elapsed", out["elapsed_s"])
