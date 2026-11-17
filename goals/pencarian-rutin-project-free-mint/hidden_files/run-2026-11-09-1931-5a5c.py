#!/usr/bin/env python3
"""Run 2026-11-09 19:31 WIB — route 5a shape-check (10 new Sourcify addrs) + route 5c
ERC-20 backlog from last scan output (onchain-scan-2026-11-09-1231.json).
Read-only except track-c-scan-checked.json appends for newly checked addrs.
Writes run-2026-11-09-1931-5a5c.json"""
import json, urllib.request, time
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "FREE_SLOTS", "FREE_SUPPLY"]

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            d = json.load(r)
        return d.get("abi")
    except Exception as e:
        return {"_error": str(e)}

def shape(addr):
    abi = fetch_abi(addr)
    if not isinstance(abi, list):
        return {"address": addr, "error": str(abi)}
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
    s2 = tokenish and ("mintFree" in names or "mintfree" in [n.lower() for n in names]) \
        and bool(free) and agent
    return {"address": addr, "S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote,
            "free": free, "agent": agent, "token": tokenish,
            "fns": sorted(names)[:40]}

out = {"run": "2026-11-09-1931", "5a": {}, "5c": {}}
new5a = ["0x0e59FD02513548f0840EAcF4Fc1b5C222Ce88Ac4", "0x1638056996B3e902f4888380C1c83f2362153B6E",
         "0x05FD44F2f1bfBd1bC3DF0CAE0002ffb49EAc2057", "0x80C2436b19BD1fbCc5c35375D5d5Ff1FB28Ae323",
         "0xe154bA89724CcB149a6d85b91384A0DA2B45e114", "0x45a13dEd8d9306197C7bEf04A32Cd079F1D1B435",
         "0x6069D8428263d9b3EEBE4621518455c652cacA41", "0xd59f46fE363DCA6745d96f69aD5544E93D2f3ADf",
         "0x9953C55Ddc5de486bf1D8e3F5078d8FAE2Ef7D31", "0xC80Ba5B5B9a84237d6D6005b3CCa928c89fdea28"]
with ThreadPoolExecutor(max_workers=5) as ex:
    for s in ex.map(shape, new5a):
        out["5a"][s["address"]] = s
        print("5a", s["address"], "S1", s.get("S1"), "S2", s.get("S2"), "mint", s.get("mint"),
              "quote", s.get("quote"), "free", s.get("free"), "agent", s.get("agent"), flush=True)

# 5c backlog
scan = json.load(open(f"{BASE}/onchain-scan-2026-11-09-1231.json"))
erc = scan.get("erc20_mint_contracts_list", [])
checked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
if isinstance(checked, list):
    checked = {c: True for c in checked}
cands = [e for e in sorted(erc, key=lambda x: -x.get("mint_count", 0))
         if e.get("mint_count", 0) >= 10 and e["address"].lower() not in
         {k.lower() for k in checked}]
print("5c candidates (top unchecked >=10):", len(cands), "total erc20:", len(erc), flush=True)
todo = [e["address"] for e in cands[:20]]
out["5c"]["todo"] = todo
out["5c"]["skipped_already_checked"] = len(erc) - len(cands)
with ThreadPoolExecutor(max_workers=5) as ex:
    for s in ex.map(shape, todo):
        out["5c"][s["address"]] = s
        checked[s["address"]] = {"run": "2026-11-09-1931", "S1": s.get("S1"), "S2": s.get("S2")}
        print("5c", s["address"], "S1", s.get("S1"), "S2", s.get("S2"), flush=True)
json.dump(checked, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)
json.dump(out, open(f"{BASE}/run-2026-11-09-1931-5a5c.json", "w"), indent=1)
print("5a5c DONE", flush=True)
