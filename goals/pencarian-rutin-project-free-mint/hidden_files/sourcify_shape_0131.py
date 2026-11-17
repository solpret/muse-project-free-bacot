#!/usr/bin/env python3
"""Sourcify recently-verified feed shape-check, run 0131 (2026-11-06). Read-only.
Fetches the feed fresh (limit 20, sort desc) and shape-checks S1/S2 for each
contract, following hot-leg-2026-11-06-0129.py. Writes run-2026-11-06-0131-sourcify-shape.json."""
import json, urllib.request, subprocess
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
        "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed"]

def fetch_feed():
    req = urllib.request.Request(
        "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc",
        headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)

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
    is_token = all(x in fns for x in ("name", "symbol", "decimals", "totalSupply"))
    has_mintfree = "mintFree" in fns
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = is_token and has_mintfree and ("freeClaimed" in fns or "freeMinted" in fns) \
        and ("FREE_SLOTS" in fns or "FREE_SUPPLY" in fns) and agent
    nft = ("ownerOf" in fns or "tokenURI" in fns)
    return {"abi_functions": fns, "S1": s1, "S2": s2, "mint": has_mint,
            "quote": has_quote, "free": free, "agent": agent, "token": is_token, "nft": nft}

def main():
    feed = fetch_feed()
    json.dump(feed, open(f"{BASE}/run-2026-11-06-0131-sourcify-feed.json", "w"), indent=1)
    addrs = [x["address"] for x in feed.get("results", [])]
    print("FEED", len(addrs), addrs, flush=True)
    shape = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        for a, sh in zip(addrs, ex.map(shape_of, addrs)):
            shape[a] = sh
            print("SHAPE", a, "S1", sh["S1"], "S2", sh["S2"], "mint", sh["mint"], "quote", sh["quote"],
                  "free", sh["free"], "agent", sh["agent"], "token", sh["token"], "nft", sh.get("nft"),
                  sh.get("error", ""), flush=True)
    json.dump(shape, open(f"{BASE}/run-2026-11-06-0131-sourcify-shape.json", "w"), indent=1)
    print("wrote run-2026-11-06-0131-sourcify-shape.json")

if __name__ == "__main__":
    main()
