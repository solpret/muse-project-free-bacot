#!/usr/bin/env python3
"""Hot-leg run 2026-11-06 03:04 WIB. Leg 1: shape-check new Sourcify feed contracts.
Writes only its own run files + hot-leg-seen.json. Never touches main snapshot."""
import json, urllib.request, subprocess
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0304"
NOW = "2026-11-06 03:04 WIB"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
        "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed"]

feed = json.load(open(f"{BASE}/hot-leg-{TS}-sourcify.json"))
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
addrs = [x["address"] for x in feed.get("results", [])]
new = [a for a in addrs if a.lower() not in seen_l]
excluded = ["0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"]
new_ne = [a for a in new if a.lower() not in excluded]
print("FEED", len(addrs), "NEW", len(new), new, flush=True)

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

def shape_of(a):
    abi = abi_of(a)
    if isinstance(abi, dict):
        return {"error": abi.get("error", "abi-unavailable"), "S1": False, "S2": False,
                "mint": False, "quote": False, "free": [], "agent": False, "token": False}
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
    return {"abi_functions": fns, "S1": s1, "S2": s2, "mint": has_mint,
            "quote": has_quote, "free": free, "agent": agent, "token": is_token, "nft": nft}

shape = {}
with ThreadPoolExecutor(max_workers=4) as ex:
    for a, sh in zip(new_ne, ex.map(shape_of, new_ne)):
        shape[a] = sh
        print("SHAPE", a, "S1", sh["S1"], "S2", sh["S2"], "mint", sh["mint"], "quote", sh["quote"],
              "free", sh["free"], "agent", sh["agent"], "token", sh["token"], "nft", sh.get("nft"),
              sh.get("error", ""), flush=True)
json.dump(shape, open(f"{BASE}/run-{TS}-sourcify-shape.json", "w"), indent=1)
for a in new:
    if a.lower() in excluded:
        seen[a] = {"first_seen": NOW, "status": "excluded"}
    else:
        sh = shape.get(a, {})
        if sh.get("S1") or sh.get("S2"):
            if sh.get("nft"):
                st = "checked-not-track-c"
                nt = ("S1/S2 literal pass BUT ERC-721 NFT (ownerOf/tokenURI), not a fungible "
                      "share sale, so NOT a track-C lead. NFT early-lead stays with main job; "
                      "never reported/previewed/minted.")
            else:
                st = "sale-shape-NEEDS-VERIFY"
                nt = "SALE SHAPE S1=%s S2=%s" % (sh.get("S1"), sh.get("S2"))
        else:
            st = "checked-not-sale-shape"
            nt = "S1=%s S2=%s mint=%s quote=%s free=%s agent=%s token=%s nft=%s %s" % (
                sh.get("S1"), sh.get("S2"), sh.get("mint"), sh.get("quote"),
                sh.get("free"), sh.get("agent"), sh.get("token"), sh.get("nft"),
                sh.get("error", ""))
        seen[a] = {"first_seen": NOW, "status": st, "note": nt, "source": "sourcify-feed"}
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
print("SEEN-UPDATED total", len(seen), flush=True)
print("SALE-SHAPE-NEW", [a for a in new_ne if shape.get(a, {}).get("S1") or shape.get(a, {}).get("S2")], flush=True)
