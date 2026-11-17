#!/usr/bin/env python3
"""Shape-check the 2 Sourcify items new since hot-leg 0109. Read-only."""
import json, urllib.request
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
def sourcify(addr):
    url = f"https://sourcify.dev/server/v2/contracts/56/{addr}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except Exception as e:
        return {"_error": str(e)}
out = {}
for addr in ["0x4233C62919CC03168a361C547117c1553C375bfC",
             "0x0B3254717c3C8AD2c3615a1BC5d9fA79480e79a4"]:
    sc = sourcify(addr)
    abi = None
    try:
        abi = sc.get("stdJson", {}).get("output", {}).get("abi") or sc.get("abi")
    except Exception:
        pass
    if abi:
        fns = [f.get("name") for f in abi if f.get("type") == "function"]
        free = [f for f in fns if "free" in f.lower()]
        mint = any("mint" in f.lower() for f in fns)
        quote = any("quote" in f.lower() or "cost" in f.lower() or "price" in f.lower() for f in fns)
        agent = any("agent" in f.lower() or "registry" in f.lower() for f in fns)
        token = all(x in fns for x in ["name", "symbol", "decimals", "totalSupply"])
        out[addr] = {"S1": bool(mint and quote and free and agent),
                     "S2": bool(token and free and agent),
                     "mint": mint, "quote": quote, "free": free, "agent": agent,
                     "token": token, "fns": len(fns),
                     "registry_bytes": REG in json.dumps(sc).lower()}
    else:
        out[addr] = {"error": sc.get("_error"), "verified": False}
    print(addr, json.dumps(out[addr]), flush=True)
json.dump(out, open("run-2026-11-09-0131-feed-shape.json", "w"), indent=1)
print("FEED-SHAPE DONE", flush=True)
