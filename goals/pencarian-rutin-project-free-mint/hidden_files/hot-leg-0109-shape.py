#!/usr/bin/env python3
"""hot-leg 2026-11-10 01:09 shape-check: 4 new Sourcify feed contracts.
Direct Sourcify v2 ABI check (parallel), same S1/S2 logic as hot-leg-0054-salvage.
Read-only except hot-leg-seen.json notes + this run's own output. No preview/mint."""
import json, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EP = "https://bsc.nodereal.io/"
NEW = ["0x7156D9435A06A8aa5DA740f46278bF9Cc30d8ec8",
       "0xd73A0cDCe58e07D8e2a38EE771Cc3aBC45B6FA45",
       "0x8bd2444C2D985Bd6A84540308E634948fB964421",
       "0xaB36C1C92a3De7462b91306c63C63A4bD5317972"]
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeMintedTotal"]
MINT_FNS = ["mint", "mintFree", "claimFree", "claim"]
QUOTE_FNS = ["quote", "cost", "PRICE", "price"]
AGENT_MARKERS = ["agentRegistry", "registry", "AGENT_ID", "AgentGate",
                 "agentGate", "isAgent", "hasAgentId", "agentIdRequired"]
TOKEN_FNS = ["name", "symbol", "decimals", "totalSupply"]
T0 = time.time()

def fetch(url, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent": "hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def find_abi(obj):
    if isinstance(obj, list) and obj and all(
            isinstance(x, dict) and x.get("type") in ("function", "event", "constructor", "error")
            for x in obj if isinstance(x, dict)):
        return obj
    if isinstance(obj, dict):
        for v in obj.values():
            a = find_abi(v)
            if a is not None:
                return a
    if isinstance(obj, list):
        for v in obj:
            a = find_abi(v)
            if a is not None:
                return a
    return None

def shape_check(addr):
    abi, err = None, None
    try:
        raw = fetch(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=12)
        abi = find_abi(json.loads(raw))
        if abi is None:
            err = "v2-no-abi"
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
    names = set()
    if abi:
        for fn in abi:
            if isinstance(fn, dict) and fn.get("type") == "function":
                names.add(fn.get("name", ""))
    code_reg = None
    if not abi:
        try:
            payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                                  "params": [addr, "latest"]}).encode()
            req = urllib.request.Request(EP, data=payload,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                code = json.load(r).get("result", "")
            code_reg = REGISTRY[2:].lower() in (code or "").lower()
        except Exception as e:
            code_reg = f"err:{type(e).__name__}"
    has_mint = bool(names & set(MINT_FNS))
    has_quote = bool(names & set(QUOTE_FNS))
    free_found = [f for f in FREE_VIEWS if f in names]
    has_agent = any(m.lower() in n.lower() for n in names for m in AGENT_MARKERS) \
        or code_reg is True
    is_token = all(f in names for f in TOKEN_FNS)
    s1 = has_mint and has_quote and bool(free_found) and has_agent
    s2 = is_token and ("mintFree" in names) \
        and (("freeClaimed" in names or "freeMinted" in names) or bool(free_found)) \
        and any(x in names for x in ["FREE_SLOTS", "FREE_SUPPLY"]) and has_agent
    return {"address": addr, "S1": bool(s1), "S2": bool(s2),
            "mint": has_mint, "quote": has_quote, "free": free_found,
            "agent": bool(has_agent), "token": bool(is_token),
            "abi_err": err, "code_registry": code_reg}

shapes = {}
with ThreadPoolExecutor(max_workers=4) as ex:
    futs = {ex.submit(shape_check, a): a for a in NEW}
    for f in as_completed(futs):
        try:
            shapes[futs[f]] = f.result()
        except Exception as e:
            shapes[futs[f]] = {"address": futs[f], "error": f"{type(e).__name__}: {e}"}

seen = json.load(open(BASE + "hot-leg-seen.json"))
for a, s in shapes.items():
    seen[a] = {"first_seen_wib": "2026-11-10 01:09 WIB", "source": "sourcify-feed",
               "status": "checked-sale-shape" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape",
               "note": str(s)[:400]}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out = {"shapes": shapes,
       "sale_shapes": [s for s in shapes.values() if s.get("S1") or s.get("S2")],
       "seen_total": len(seen), "duration_sec": round(time.time() - T0, 1)}
json.dump(out, open(BASE + "hot-leg-2026-11-10-0109-shape.json", "w"), indent=1)
print(json.dumps(out, indent=1))
