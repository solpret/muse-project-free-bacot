#!/usr/bin/env python3
"""Run 2026-11-09 20:31 WIB — route 5a shape-check (10 new Sourcify addrs) + route 5c
ERC-20 backlog from last scan output (onchain-scan-2026-11-09-1231.json).
Read-only except track-c-scan-checked.json appends for newly checked addrs.
Writes run-2026-11-09-2031-5a5c.json"""
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

out = {"run": "2026-11-09-2031", "5a": {}, "5c": {}}
new5a = ['0x5B82fFe48400B8d7cE37d9117291525356f967b1', '0x276FECA0b94366afa9DdA9F6Bf296580ebBBa756', '0x1ff5202ec868FB419b8271e3DD6a6eBF6C8Fe5f1', '0x9d898fB21bA43b7e5185A7e081C1E7bB4dd399d9', '0x8553e7033C06fC69B7508d58507b75242cF86EC4', '0xe4517E6718b24D5725956ac7A90686592a7b1539', '0x254061D7Ee8512D3ed3Dd0aff7B31d9EaBdBCfC5', '0xB57641EA973Dc770682d6eBf00e6a5a01Be09894', '0x090B2530d122465510764F028e9bc4F051a2a6E7', '0xaA58b51FB620da9f7eAa9FEE53f88ed5E3D22C34', '0x57440C367DE186040f0efba0f723F7c818948D35', '0x6f650CbBDF1d5da7c78Aa3e9BB069ac0887dC0da', '0xf986969B5C3bd54f1E03C01008dBc51985A506EA', '0x68d2C93571aAfF676134c4A937f81D5bf8a95C1E', '0x4a6dfDf1c04122b7c4547cE6cB6b1c97F8c6a02D', '0x3E47EC7Cc43db54C59b06bd11d6d5cDc11a5BD58', '0x49a0DCb8dBd304B80aA475026CC558D4Bae54382', '0x413810Bff5CC7e33936fa55600F4e0ce3372307f', '0x824c2eE31291414E0ba9CD7c5A30fA27aa8520Cd', '0x16fa7b19b790324B7bB4f9c86D2dace8347e5979', '0x02201E6f13c41506c7Bb635d7543F98826229aB7', '0x9CA1A3eeA74829aA5011c56386b226DB472D0F4f', '0x853Efcdfad40EFCAAe21dA2A7D9ECF74648be9b3', '0xCd497f5b3739fbe392b36BC1704c5C8b6d10a032', '0xE316dbDC9E97b98d21c9523d459eFef41942A8C8', '0xb42Cf1aFFfEdC9d63C519c43d0008Cf92C2D77ae', '0xCC10A5a3fFAb6FF7b29F9239d5d72d6c171c0e7D']
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
        checked[s["address"]] = {"run": "2026-11-09-2031", "S1": s.get("S1"), "S2": s.get("S2")}
        print("5c", s["address"], "S1", s.get("S1"), "S2", s.get("S2"), flush=True)
json.dump(checked, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)
json.dump(out, open(f"{BASE}/run-2026-11-09-2031-5a5c.json", "w"), indent=1)
print("5a5c DONE", flush=True)
