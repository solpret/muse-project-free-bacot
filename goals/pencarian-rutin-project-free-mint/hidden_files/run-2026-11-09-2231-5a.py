#!/usr/bin/env python3
"""Run 2231 route 5a: shape-check 17 fresh Sourcify feed addresses (not hot-leg-seen, not in snapshot). Read-only.
Writes run-2026-11-09-2231-5a.json."""
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

new5a = ['0xc53740416E9Cb86075967c1fdc592F39C5046FF7', '0xEBCb43F4f9C689B9b99F57899C72eF9CFE8f70CB', '0xd15De55dFAeD7047cff63d8E189647e9Dba7d663', '0x24307e68d4C3B62077E89B721f9B7a7D1caB8eC3', '0x943F7b002E214535646F3DAB94cC9fF15402dA50', '0x87F9315b008ffF762F0A6C1C41fc1aF523D8ceE0', '0x4d5FDb5AEa3BBAec3f0B4174B20BC201fBaB8fEb', '0xBEB8833c5a5290678e67Af65a4c12f9402bA404F', '0x992597E09AeE76eB6dC752988cFA732c7Ec88048', '0x4D46aD56b530760a690433F80a282E42D8D32039', '0xE97E4683ffe6d13Be81Ea03f17a190cc9Ad098c2', '0xd1F60EE61d864adF24C358d771BfCBD18390fFb0', '0xb22f3257F2F8C8dC9A85756Cf23B20cD37a42CC1', '0x3E4A575c3C40F97da8A7b571f6552180b445F870', '0xD3330521cF18Fd89A53EfD71271Ce818e60610Fc', '0x25F13ee566F496494F232AF90360E0C2Ca99d44c', '0x36A8C76cFf55D0471e8272913094f9688cA6e6ea']
out = {"run": "2026-11-09-2231", "5a": {}}
with ThreadPoolExecutor(max_workers=10) as ex:
    for s in ex.map(shape, new5a):
        out["5a"][s["address"]] = s
        print("5a", s["address"], "S1", s.get("S1"), "S2", s.get("S2"),
              "mint", s.get("mint"), "quote", s.get("quote"), "free", s.get("free"),
              "agent", s.get("agent"), "token", s.get("token"), flush=True)
with open(f"{BASE}/run-2026-11-09-2231-5a.json", "w") as f:
    json.dump(out, f, indent=1)
print("5A DONE", flush=True)
