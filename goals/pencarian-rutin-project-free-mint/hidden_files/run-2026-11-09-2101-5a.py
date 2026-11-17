#!/usr/bin/env python3
"""Run 2101 route 5a: shape-check 25 new Sourcify feed addresses. Read-only.
Writes run-2026-11-09-2101-5a.json."""
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

new5a = ['0x08f32aa9fcd8405519982419C810218618dde76B', '0x9Ec179A427964589Ee969494bd14BfA185f7780c',
 '0xfb2E7F9B82A0aA49b371DF606d3409167873e223', '0xD9E0754B06c142D439f4FE3e61D07eE24e5652cA',
 '0xF2bee7327b7AE18b156F5e0BC9c9f03D546c4f5f', '0xaE1c774D1609E4f234ff85C83b93Af661EeFFD86',
 '0x29EC7D0374c026c4D0b6676dbFe21e6dD253aFE8', '0x6F553dD1De1FbE6722eEBd4287e13ed490772F40',
 '0xf919A41E0F7ac931ed756c188f74F82E8EcD2429', '0xe474dC13b8669a78F6B0EABeEf37876F01701184',
 '0x58ceFE5c3f1a3A703CbC0dc4c3417db4056a0Af6', '0x5Ed76674462b6F6a9Bbb47E93984B82B0401AdF4',
 '0xBF55C0f4315c9918D1f2F533Ec69cB2FbD091b61', '0x47b0254b1540F8E0BAF22c82B8bDb260537bDDb6',
 '0x77d4ae71fF333B2b313827D5190BBE6773aaefC2', '0x37e32Caf3a8E346a7e72439148870a70DB85a3CB',
 '0x1145fCf432E39c23ab4927704020738C72495aB3', '0x1E308982dB042879F78CC0D9Da61d1EC4c0047d1',
 '0x201282287d49223236Fac15E841A54Ac43dFEC0F', '0x0EAfDa9842FE0EAB0CE8376Ccf9D3eF3BC9CDdC0',
 '0x2F8EE8cd63aD3A93C3e17DF8d64dED11A474d828', '0xf02E01fBD87cc621CB313101b204CcFa469bFb9f',
 '0x9e25c3a8346D522951A02bE2bFB41327Ea8C7872', '0x5f76cAb7B054e088563D5098E17bD0dc430e61aE',
 '0x268084e23a49a1b797A267Be0F3dF0B667Bf5CD9']
out = {"run": "2026-11-09-2101", "5a": {}}
with ThreadPoolExecutor(max_workers=10) as ex:
    for s in ex.map(shape, new5a):
        out["5a"][s["address"]] = s
        print("5a", s["address"], "S1", s.get("S1"), "S2", s.get("S2"),
              "mint", s.get("mint"), "quote", s.get("quote"), "free", s.get("free"),
              "agent", s.get("agent"), "token", s.get("token"), flush=True)
with open(f"{BASE}/run-2026-11-09-2101-5a.json", "w") as f:
    json.dump(out, f, indent=1)
print("5A DONE", flush=True)
