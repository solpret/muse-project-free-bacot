#!/usr/bin/env python3
"""Hot-leg 2026-11-16 19:04 WIB — leg 1 shape-check, curl-based (urllib 400s at 19:01 main run)."""
import json, subprocess

NEW = ["0x2Ae7AB9CE6945E48002F9005b85A67AE55A0a0e6",
       "0xd579E804C8D276135Ec82E3562fE3007e6126456",
       "0xe86558Cf812f39d29C98Baeb376e81BF53c6D5a6",
       "0x4b233500BB5f55480cf240E553A29bb403cA1aFd",
       "0x9d0A496bf73DE0E793182Ad546F2AfAaC0F452E0",
       "0xB30FAf20E96ec78eD7838cAC50e1333967CFBEC3"]
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeMintedBy"]
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"

def curl_json(url, timeout=30):
    try:
        p = subprocess.run(["curl", "-sS", "--max-time", str(timeout), url],
                           capture_output=True, text=True, timeout=timeout + 5)
        if p.returncode != 0 or not p.stdout.strip():
            return None, f"curl rc={p.returncode} err={p.stderr[:100]}"
        return json.loads(p.stdout), None
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:100]}"

def get_code(addr):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                          "params": [addr, "latest"]})
    try:
        p = subprocess.run(["curl", "-sS", "--max-time", "25", "-X", "POST",
                            "-H", "Content-Type: application/json", "-d", payload,
                            "https://bsc-dataseed.binance.org/"],
                           capture_output=True, text=True, timeout=30)
        d = json.loads(p.stdout)
        return d.get("result", "") or ""
    except Exception:
        return ""

res = {}
for a in NEW:
    d, err = curl_json(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=metadata,abi")
    if not d:
        res[a] = {"shape": "abi-unavailable", "err": err}
        print(a, "ABI UNAVAILABLE:", err, flush=True)
        continue
    abi = d.get("abi") or d.get("metadata", {}).get("output", {}).get("abi") or []
    names = [f.get("name", "") for f in abi if f.get("type") == "function"]
    has_mint = any(n.startswith("mint") for n in names)
    has_quote = any("quote" in n.lower() or "cost" in n.lower() or "price" in n.lower() for n in names)
    free_views = [n for n in names if n in FREE_VIEWS]
    code = get_code(a)
    has_reg = REG in code.lower() or any("agentidregistry" in n.lower() or "agentgate" in n.lower() for n in names)
    is_token = any(n in names for n in ("name", "symbol", "decimals", "totalSupply"))
    has_mintfree = "mintFree" in names
    s1 = has_mint and has_quote and bool(free_views) and has_reg
    s2 = is_token and has_mintfree and bool(free_views) and has_reg
    shape = "S1" if s1 else ("S2" if s2 else "checked-not-sale-shape")
    print(a, "fns=", len(names), "mint=", has_mint, "quote=", has_quote,
          "free_views=", free_views, "reg=", has_reg, "token=", is_token,
          "mintFree=", has_mintfree, "=>", shape, flush=True)
    res[a] = {"shape": shape, "fns": len(names), "mint": has_mint, "quote": has_quote,
              "free_views": free_views, "registry": has_reg, "token": is_token,
              "mintFree": has_mintfree}
json.dump(res, open("hot-leg-2026-11-16-1904-feedshape.json", "w"), indent=1)
print("DONE")
