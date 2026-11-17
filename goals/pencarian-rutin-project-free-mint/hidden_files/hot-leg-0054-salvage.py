#!/usr/bin/env python3
"""Salvage for hot-leg 2026-11-10 00:54 run:
(1) shape-check the 3 new feed contracts (Sourcify v2 ABI, parallel, 12s each)
    - the 1219 shape subprocess timed out at 90s in the main run;
(2) Boltbook EN+ZH via curl (urllib IncompleteRead(0) in the main run);
(3) leg4 re-read vs 0044 baseline (main run hit FileNotFoundError from a
    bad sed patch - baseline path fixed to 0044 afterwards).
Read-only except hot-leg-seen.json notes + this run's own outputs.
No preview/mint, no chain-wide scan."""
import json, re, subprocess, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EP = "https://bsc.nodereal.io/"
T0 = time.time()
NEW = ["0xf80ac3D54226dF2d21ce8aEAf581c5ACf6811Ec8",
       "0xE68DC8801ED7d6eD7C1FAcb8004d7c835b212cA4",
       "0x23fc76e88CB421BC2fa98A746523a245553360e2"]
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeMintedTotal"]
MINT_FNS = ["mint", "mintFree", "claimFree", "claim"]
QUOTE_FNS = ["quote", "cost", "PRICE", "price"]
AGENT_MARKERS = ["agentRegistry", "registry", "AGENT_ID", "AgentGate",
                 "agentGate", "isAgent", "hasAgentId", "agentIdRequired"]
TOKEN_FNS = ["name", "symbol", "decimals", "totalSupply"]
out = {"salvage": "hot-leg 2026-11-10 00:54"}

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
    is_token = bool(names & set(TOKEN_FNS))
    s1 = has_mint and has_quote and bool(free_found) and has_agent
    s2 = is_token and ("mintFree" in names) \
        and (("freeClaimed" in names or "freeMinted" in names) or bool(free_found)) \
        and any(x in names for x in ["FREE_SLOTS", "FREE_SUPPLY"]) and has_agent
    return {"address": addr, "S1": bool(s1), "S2": bool(s2),
            "mint": has_mint, "quote": has_quote, "free": free_found,
            "agent": bool(has_agent), "token": bool(is_token),
            "abi_err": err, "code_registry": code_reg}

shapes = {}
with ThreadPoolExecutor(max_workers=3) as ex:
    futs = {ex.submit(shape_check, a): a for a in NEW}
    for f in as_completed(futs):
        try:
            shapes[futs[f]] = f.result()
        except Exception as e:
            shapes[futs[f]] = {"address": futs[f], "error": f"{type(e).__name__}: {e}"}
out["leg1_shape_salvage"] = shapes
sale = [s for s in shapes.values() if s.get("S1") or s.get("S2")]
out["leg1_new_sale_shapes"] = sale

# update seen notes with real shape results
seen = json.load(open(BASE + "hot-leg-seen.json"))
for a, s in shapes.items():
    if isinstance(seen.get(a), dict):
        seen[a]["status"] = "checked-sale-shape" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape"
        seen[a]["note"] = str(s)[:400]
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["seen_total"] = len(seen)

# ---- Boltbook via curl ----
def boltbook(url):
    try:
        p = subprocess.run(["curl", "-sL", "--max-time", "20", url],
                           capture_output=True, timeout=25)
        return p.stdout, None if p.stdout else f"curl-empty: {p.stderr.decode()[:100]}"
    except Exception as e:
        return b"", f"{type(e).__name__}: {e}"

en_raw, en_err = boltbook("https://boltbook.fun/")
zh_raw, zh_err = boltbook("https://boltbook.fun/?lang=zh")
open(BASE + "hot-leg-2026-11-10-0054-boltbook-en.html", "wb").write(en_raw)
open(BASE + "hot-leg-2026-11-10-0054-boltbook-zh.html", "wb").write(zh_raw)
en_txt, zh_txt = en_raw.decode("utf-8", "ignore"), zh_raw.decode("utf-8", "ignore")
en_addrs = list(dict.fromkeys(re.findall(r"0x[a-fA-F0-9]{40}", en_txt)))
zh_addrs = list(dict.fromkeys(re.findall(r"0x[a-fA-F0-9]{40}", zh_txt)))
all_bb = list(dict.fromkeys(en_addrs + zh_addrs))
kw = {}
for k in ["free share", "first share free", "1 free share", "free mint share"]:
    kw[k] = en_txt.lower().count(k.lower()) + zh_txt.lower().count(k.lower())
for k in ["免费份额", "首个免费", "免费铸造", "免费mint"]:
    kw[k] = en_txt.count(k) + zh_txt.count(k)
bb_new = [a for a in all_bb if a.lower() not in {k.lower() for k in seen}]
bb_shapes = {}
if bb_new:
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(shape_check, a): a for a in bb_new}
        for f in as_completed(futs):
            try:
                bb_shapes[futs[f]] = f.result()
            except Exception as e:
                bb_shapes[futs[f]] = {"address": futs[f], "error": f"{type(e).__name__}: {e}"}
    for a in bb_new:
        seen[a] = {"first_seen_wib": "2026-11-10 00:54 WIB", "source": "boltbook-frontpage",
                   "status": "checked-sale-shape" if (bb_shapes.get(a, {}).get("S1") or bb_shapes.get(a, {}).get("S2")) else "checked-not-sale-shape",
                   "note": str(bb_shapes.get(a, {}))[:400]}
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["leg2_boltbook_salvage"] = {
    "en_bytes": len(en_raw), "en_err": en_err, "zh_bytes": len(zh_raw), "zh_err": zh_err,
    "en_addrs": len(en_addrs), "zh_addrs": len(zh_addrs), "unique_addrs": len(all_bb),
    "keyword_hits": kw, "new_vs_seen": bb_new, "shape_check": bb_shapes,
    "seen_total": len(seen)}
sale += [dict(s, address=a) for a, s in bb_shapes.items() if s.get("S1") or s.get("S2")]
out["leg3_new_sale_shapes"] = sale
out["duration_sec"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + "hot-leg-run-2026-11-10-0054-salvage.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:5000])
