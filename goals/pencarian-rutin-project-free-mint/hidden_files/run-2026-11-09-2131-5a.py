#!/usr/bin/env python3
"""Run 2131 route 5a: shape-check 25 new Sourcify feed addresses. Read-only.
Writes run-2026-11-09-2131-5a.json."""
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

new5a = ["0x841f47fCCd11677BbAEa161156ABBBDF7952fD58", "0x3f508d8826517123Fdd39c776e55F85Fa188E5fD", "0xA3E8dA0612994637D8BE69C1B54C8BE745A4ED19", "0xB91478876dB8cD513dc4bF1AFcF3400a7B3C9B39", "0xB4d6674E099178F8f506CD8a0A59a826A840Cf5E", "0x9D03867736D0677C40dd56b6A92D6F9042B10cB7", "0x84487ceCEAe538c19daaEc3e1Bdb48BA611B3669", "0xaC50E5F52B3289F686D16581C6dC3622d92b133f", "0x50459cd80E6db2C9f4FBb89411935a0Bf3063c28", "0x8f37CBd8c1B9214F2550Ce49a1365275b42ac588", "0x4Bc1A1723a5D8A893695f78c8b2cD39028478d43", "0xA9e6F0E6935662AA30F578884662738f05D1C1e4", "0xA5fBCF44C84F92edc137B630b53171F2Abc1D9eC", "0x28A03235E37E26eD35c4d1ea4aB3c960f1Ea1Bc5", "0x8908F5a23abeC91D1760a4097024DC79F0C25828", "0x8bf446Aa16B8c9bdBcC12B405aD1741a970A660c", "0x0B249dB2a79c43AadE8f701Ae53240Bd7299eCe6", "0x3045825EB7b519c1054b51c517AaDb7c497c219b", "0xc94118024c25360A189F5DDcb17D83AB7058064C", "0x385c2cF7478e9620c93F7C0dE198DF8E2bE5a779", "0x09B3CeB096b1DDbfBB31805AC2e21d45567BC6Ea", "0x691E257acb388C3be692433e70bBee38cB6a5Bcf", "0xe742215aA4FCBfA9047cFae42adecbA96534e03A", "0x08f32aa9fcd8405519982419C810218618dde76B", "0x9Ec179A427964589Ee969494bd14BfA185f7780c"]
out = {"run": "2026-11-09-2131", "5a": {}}
with ThreadPoolExecutor(max_workers=10) as ex:
    for s in ex.map(shape, new5a):
        out["5a"][s["address"]] = s
        print("5a", s["address"], "S1", s.get("S1"), "S2", s.get("S2"),
              "mint", s.get("mint"), "quote", s.get("quote"), "free", s.get("free"),
              "agent", s.get("agent"), "token", s.get("token"), flush=True)
with open(f"{BASE}/run-2026-11-09-2131-5a.json", "w") as f:
    json.dump(out, f, indent=1)
print("5A DONE", flush=True)
