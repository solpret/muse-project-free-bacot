#!/usr/bin/env python3
"""Run 2231 route 5a: shape-check 17 fresh Sourcify feed addresses (not hot-leg-seen, not in snapshot). Read-only.
Writes run-2026-11-09-2301-5a.json."""
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

new5a = ["0xC8113f80E2613E4E520F448060e34d85323E764a", "0xc7576eAE6FBaCE4574dae83e3ed041B11eeBb829", "0x5a52fe87c7F498653C596D856F1354E0a2895a07", "0xF62Ca1FEA6e4b92bb4Bb87b686E0da0D3b7e4F0a", "0x66D748022F6C432868bB5E3066fba69b162C4a27", "0x041315502d15D6cF0DfC04f251978933F3044d3F", "0x497d546AAF903782bDd97381e7C68F6788F82106", "0xE5db3F5845F89FB72cfA31AB04503489614977aA", "0x0E5eDC0DbA5655aE228487dECb2EcBC9E2d4caD1", "0x32660E34a5a65925684F12e72A8ECD5D1A50D54d", "0x62C7e9440A96266833E7847246e19f23b6939317", "0x7B7D97E80C25E72A4411467565C4436E88Ae4568", "0x0aF913c0d93767b78E98abaF69972D51E91cEB3B", "0xFdD4fc42D66b9Ae16fEA9Df2d2b528a38EAB0791", "0x0678239c28ad13Eb2659D52fFdb841a7422f0f1A", "0xC5096b830FE0fcC0A9DA96f2989bAAc3C2Fb3aBf", "0x1e926f55e4BcfF65139eecF1c96771A36DeDc296", "0x40E679a18F175fbb1C213A5CE04496cF6f97dBBc", "0x1060E4B31a3974e69CD98d6770e5D2bDD0F37470", "0xcaB81c9337BED2935d24882385F993096386Efc2", "0x8b059e611E5f16b4659f81698CDbcB3dcfcDFDF1", "0xfe50981accA6001f27336EA9234AC590Fe0e60aF"]
out = {"run": "2026-11-09-2301", "5a": {}}
with ThreadPoolExecutor(max_workers=10) as ex:
    for s in ex.map(shape, new5a):
        out["5a"][s["address"]] = s
        print("5a", s["address"], "S1", s.get("S1"), "S2", s.get("S2"),
              "mint", s.get("mint"), "quote", s.get("quote"), "free", s.get("free"),
              "agent", s.get("agent"), "token", s.get("token"), flush=True)
with open(f"{BASE}/run-2026-11-09-2301-5a.json", "w") as f:
    json.dump(out, f, indent=1)
print("5A DONE", flush=True)
