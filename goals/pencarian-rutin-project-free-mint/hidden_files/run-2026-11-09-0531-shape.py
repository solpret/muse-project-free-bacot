#!/usr/bin/env python3
"""Shape-check run 2026-11-09 0531 WIB — Sourcify feed (20) + Boltbook-new (3).
Reuses hot-leg shape_check logic (Sourcify ABI fields=abi).
Read-only except writing run-2026-11-09-0531-shape.json.
"""
import json, subprocess, re
from concurrent.futures import ThreadPoolExecutor

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted",
              "freeRemaining"]

def curl_get(url, timeout=12):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), url],
                       capture_output=True, text=True, timeout=timeout + 5)
    return r.stdout

def shape_check(addr):
    try:
        d = json.loads(curl_get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=12))
        abi = d.get("abi") or []
        fns = [e.get("name") for e in abi if isinstance(e, dict) and e.get("type") == "function"]
    except Exception as e:
        return {"address": addr, "error": f"{type(e).__name__}: {e}"}
    names = set(fns)
    has_mint = bool(names & {"mint", "mintFree", "mintWithInviter", "claimMint", "mintShare", "buyShare"})
    has_quote = bool(names & {"quote", "cost", "price", "priceFor", "getPrice", "mintPrice"})
    free = sorted([f for f in FREE_VIEWS if f in names])
    agent = bool(names & {"identityRegistry", "agentRegistry", "AgentGate", "agentId", "agentID"}) or any("agent" in (f or "").lower() or "registry" in (f or "").lower() for f in fns)
    token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = token and ("mintFree" in names) and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY", "FREE_AMOUNT"})
    return {"address": addr, "S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote,
            "free": free, "agent": agent, "token": token,
            "note": f"S1={s1} S2={s2} mint={has_mint} quote={has_quote} free={free} agent={agent} token={token}"}

feed = json.load(open(f"{HF}/run-2026-11-09-0531-sourcify-feed.json"))
addrs = [r["address"] for r in feed.get("results", [])]
addrs += ["0x20b123955bAbC4D5661C54EE7e149e0B71cCAc8f",
          "0xcd1bb8013e924e26ed4131a69304f2969c4f8d28",
          "0xf7f9a787d7ea0c73beac06eba6b8c01ab3edcf73"]
addrs = list(dict.fromkeys(addrs))
print(f"checking {len(addrs)} addresses", flush=True)
out = []
with ThreadPoolExecutor(max_workers=6) as ex:
    for res in ex.map(shape_check, addrs):
        out.append(res)
        print(res.get("address"), res.get("note", res.get("error")), flush=True)
hits = [r for r in out if r.get("S1") or r.get("S2")]
print("SALE-SHAPE HITS:", len(hits))
for h in hits:
    print("HIT", h)
json.dump(out, open(f"{HF}/run-2026-11-09-0531-shape.json", "w"), indent=1)
