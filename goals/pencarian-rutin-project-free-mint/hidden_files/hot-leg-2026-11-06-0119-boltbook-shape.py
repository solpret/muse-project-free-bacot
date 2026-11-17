#!/usr/bin/env python3
"""Hot-leg run 2026-11-06 01:19 WIB. Leg 2: shape-check 6 NEW Boltbook contracts.
Writes only its own run file; seen update done by caller script step."""
import json, urllib.request, subprocess
from concurrent.futures import ThreadPoolExecutor
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
        "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed"]
NEW = {
 "DEWATA": "0x1362d8733a26b42213ba1b3c61471925d4a2165",
 "MORPHA": "0xb40e4d3b33c5d70ab31a1dde3c240727691cb738",
 "SoulAgent": "0x8fdb9411753c58476a417b88a44989f8d687d63",
 "AgentGrove": "0x8b710e45d38fd55e2d198d2296c0a0d24ebfd64c",
 "AGI-mint": "0xB27e219a28CDE18278355e41C55bdc8828eec459",
 "AGI-token": "0x8F01c3eF1Bc368288067d44C49bA9b147DE3a461",
}
def abi_of(a):
    for getter in ("urllib", "curl"):
        try:
            if getter == "urllib":
                req = urllib.request.Request(
                    f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",
                    headers={"User-Agent": "curl"})
                with urllib.request.urlopen(req, timeout=15) as r:
                    d = json.load(r)
            else:
                out = subprocess.run(["curl", "-s", "--max-time", "15",
                                      f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"],
                                     capture_output=True, text=True, timeout=20)
                d = json.loads(out.stdout)
            return d.get("abi") or d.get("stdJson", {}).get("abi") or []
        except Exception:
            continue
    return {"error": "abi-unavailable"}
def shape_of(item):
    name, a = item
    abi = abi_of(a)
    if isinstance(abi, dict):
        return name, {"error": abi.get("error", "abi-unavailable"), "S1": False, "S2": False}
    fns = sorted({f.get("name") for f in abi if f.get("type") == "function" and f.get("name")})
    has_mint = any(n.startswith("mint") for n in fns)
    has_quote = "quote" in fns
    free = [f for f in fns if any(x in f for x in FREE)]
    agent = ("agentRegistry" in fns or "AGENT_REGISTRY" in fns or "registry" in fns
             or REG in json.dumps(abi).lower())
    is_token = all(x in fns for x in ["name", "symbol", "decimals", "totalSupply"])
    has_mintfree = "mintFree" in fns
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = is_token and has_mintfree and ("freeClaimed" in fns or "freeMinted" in fns) \
        and ("FREE_SLOTS" in fns or "FREE_SUPPLY" in fns) and agent
    nft = ("ownerOf" in fns or "tokenURI" in fns)
    return name, {"address": a, "abi_functions": fns, "S1": s1, "S2": s2, "mint": has_mint,
                  "quote": has_quote, "free": free, "agent": agent, "token": is_token, "nft": nft}
shape = {}
with ThreadPoolExecutor(max_workers=4) as ex:
    for name, sh in ex.map(shape_of, NEW.items()):
        shape[name] = sh
        print("SHAPE", name, sh["address"], "S1", sh.get("S1"), "S2", sh.get("S2"),
              "mint", sh.get("mint"), "quote", sh.get("quote"), "free", sh.get("free"),
              "agent", sh.get("agent"), "token", sh.get("token"), "nft", sh.get("nft"),
              sh.get("error", ""), flush=True)
json.dump(shape, open(f"{BASE}/hot-leg-2026-11-06-0119-boltbook-shape.json", "w"), indent=1)
print("SALE-SHAPE", [n for n, s in shape.items() if s.get("S1") or s.get("S2")], flush=True)
