#!/usr/bin/env python3
"""Run 2201 route 5a: shape-check 25 new Sourcify feed addresses. Read-only.
Writes run-2026-11-09-2201-5a.json."""
import json, urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "FREE_SLOTS", "FREE_SUPPLY", "freeClaimCount", "freeMintsLeft"]

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.load(r)
        return d.get("abi"), d.get("verifiedAt")
    except Exception as e:
        return {"_error": str(e)}, None

def shape(addr):
    abi, verified_at = fetch_abi(addr)
    if not isinstance(abi, list):
        return {"address": addr, "error": str(abi), "verifiedAt": verified_at}
    fns = {}
    for f in abi:
        if f.get("type") == "function":
            fns.setdefault(f.get("name"), []).append(f)
    names = set(fns)
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = any("quote" in n.lower() or n in ("cost", "price", "getPrice", "mintPrice") for n in names)
    free = [n for n in FREE_VIEWS if n in names]
    src = json.dumps(abi).lower()
    agent = ("60b9262456de011f7d15a54cdd8c48baaa8b022f" in src or "agentid" in src
             or "agentgate" in src or "agentregistry" in src or "registry" in names)
    tokenish = bool({"name", "symbol", "decimals", "totalSupply"} <= names)
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = tokenish and ("mintFree" in names or "mintfree" in [n.lower() for n in names]) and bool(free) and agent
    return {"address": addr, "verifiedAt": verified_at, "S1": s1, "S2": s2,
            "mint": has_mint, "quote": has_quote, "free": free, "agent": agent,
            "token": tokenish, "fns": sorted(names)}

new5a = ["0x31600079BA92faa8b99dddDEAd682a829Acd29f0", "0x61820aCD93a3833134b3e1df82Be389EB2Df646c", "0x328D05d87A7e0EC6e31C16a4560080eD82E6d875", "0x2593f5bfcaFb576024D4861C7940e8b3A76A8F8f", "0x43112a60c6fc4Ef973Aca7A00B0b1446A7D6e7C4", "0xdb17930bF0910109c5057c4e0857591457152Ad9", "0xE9B4C0a60926eD9f2c3E13f360c223d1bCDdb63c", "0x5014b341134d0f48cb6b269A26f71C78020D71e8", "0x673D6512F092c7016ECD35f78cBCe344B01a0ed1", "0xba1B4162E87A1EDB09D96cc8087500D55A196C98", "0x2CFC37B68a37922744BD26d19670D4362c2E621A", "0x31B74e69e24C500933bA7dCF8590E6aF34CDc3e7", "0x94f1B41f7458B08853396fB1c05Cab0a652643B8", "0xF56A7946B1A5ac98aa37E213796e8D66C4e22cc4"]
out = {"run": "2026-11-09-2201", "5a": {}}
with ThreadPoolExecutor(max_workers=10) as ex:
    for s in ex.map(shape, new5a):
        out["5a"][s["address"]] = s
        print("5a", s["address"], "S1", s.get("S1"), "S2", s.get("S2"),
              "mint", s.get("mint"), "quote", s.get("quote"), "free", s.get("free"),
              "agent", s.get("agent"), "token", s.get("token"), flush=True)
with open(f"{BASE}/run-2026-11-09-2201-5a.json", "w") as f:
    json.dump(out, f, indent=1)
print("5A DONE", flush=True)
