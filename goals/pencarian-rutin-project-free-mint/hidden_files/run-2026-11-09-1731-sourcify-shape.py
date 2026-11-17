#!/usr/bin/env python3
"""Shape-check Sourcify feed newest (verifiedAt >= 17:28 WIB) for S1/S2 sale shape
+ agent-mint shape. Read-only; writes run-2026-11-09-1731-sourcify-shape.json."""
import json, urllib.request
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
ADDRS = [
 ("0xa705707F96d4ADFF8c2CC457bBa68CBdbdD0Be38", "2026-11-09T10:36:02Z"),
 ("0x13A1Ebc988977f8AF0c2983027FF72f4D81BEF00", "2026-11-09T10:34:24Z"),
 ("0x260bf39a6f3aB5E459856297178CC0DF6003374a", "2026-11-09T10:33:09Z"),
 ("0xaA972433937D6eD7AFd91cabE3B4a26746D94A11", "2026-11-09T10:29:32Z"),
 ("0xB65390e3Af752e4e74D88c43c8eA326eee175485", "2026-11-09T10:29:19Z"),
 ("0x32CBF1f57090394cF2578aDEa345051e75b37B8d", "2026-11-09T10:28:24Z"),
]
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted",
              "freeSupply","freeLeft"]
def fetch(addr):
    req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",
                                 headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)
out = {}
for addr, vat in ADDRS:
    try:
        d = fetch(addr)
        abi = d.get("abi") or []
        fns = [f.get("name") for f in abi if isinstance(f, dict) and f.get("type") == "function"]
        src = json.dumps(d.get("stdJson", {}) or {})
        reg = REG.lower() in src.lower() or "agentIdRegistry" in src.lower() or "AGENT_ID_REGISTRY" in src
        has_mint = any(n in fns for n in ("mint", "mintFree", "claimFree", "mintWithAgentTokenId"))
        has_quote = any("quote" in n.lower() or "cost" in n.lower() for n in fns)
        free_views = [n for n in fns if any(fv.lower() in n.lower() for fv in FREE_VIEWS)]
        is_token = all(n in fns for n in ("name", "symbol", "decimals", "totalSupply"))
        s1 = has_mint and has_quote and bool(free_views) and reg
        s2 = is_token and ("mintFree" in fns) and bool(free_views) and reg
        out[addr] = {"verifiedAt": vat, "match": d.get("match"), "fns": fns[:60],
                     "registry_ref": reg, "has_mint": has_mint, "has_quote": has_quote,
                     "free_views": free_views, "is_token": is_token,
                     "S1": s1, "S2": s2}
        print(addr, "S1" if s1 else "-", "S2" if s2 else "-", "reg" if reg else "noreg",
              "fns:", len(fns), fns[:12], flush=True)
    except Exception as e:
        out[addr] = {"error": str(e)[:200]}
        print(addr, "ERR", str(e)[:150], flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-09-1731-sourcify-shape.json", "w"), indent=1)
print("SHAPE DONE")
