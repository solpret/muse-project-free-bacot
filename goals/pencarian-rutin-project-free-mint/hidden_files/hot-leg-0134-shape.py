#!/usr/bin/env python3
"""hot-leg 2026-11-10 01:34 legs 1+2+shape+bridge. Sourcify feed (limit 20),
Boltbook EN+ZH front pages (boltbook.fun), shape-check new contracts via
Sourcify v2 ABI, read-only bridge scan. Read-only except hot-leg-seen.json
notes + this run's own outputs. No preview/mint."""
import json, re, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EP = "https://bsc.nodereal.io/"
T0 = time.time()
out = {"run": "2026-11-10 01:34 WIB"}

def fetch(url, timeout=15, headers=None):
    h = {"User-Agent": "hot-leg/1.0"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

# --- Leg 1: Sourcify feed ---
sourcify_new, sourcify_err = [], None
try:
    raw = fetch("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=15)
    feed = json.loads(raw)
    json.dump(feed, open(BASE + "hot-leg-2026-11-10-0134-sourcify.json", "w"), indent=1)
    contracts = []
    for c in feed if isinstance(feed, list) else feed.get("results", []):
        a = c.get("address") if isinstance(c, dict) else None
        if a: contracts.append(a)
    seen = json.load(open(BASE + "hot-leg-seen.json"))
    sourcify_new = [a for a in contracts if a not in seen and a.lower() != REGISTRY.lower()]
    out["leg1"] = {"feed_n": len(contracts), "new_vs_seen": sourcify_new,
                   "excluded_or_registry": [a for a in contracts if a in seen or a.lower() == REGISTRY.lower()]}
except Exception as e:
    sourcify_err = f"{type(e).__name__}: {e}"
    out["leg1"] = {"error": sourcify_err}

# --- Leg 2: Boltbook EN + ZH ---
def boltbook(lang):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    try:
        raw = fetch(url, timeout=20)
    except Exception:
        import subprocess
        r = subprocess.run(["curl", "-sL", "--max-time", "25", url],
                           capture_output=True)
        if r.returncode != 0 or not r.stdout:
            raise RuntimeError("curl fallback failed: " + r.stderr.decode(errors="ignore")[:120])
        raw = r.stdout
    open(BASE + f"hot-leg-2026-11-10-0134-boltbook-{lang}.html", "wb").write(raw)
    text = raw.decode("utf-8", errors="ignore")
    addrs = sorted(set(re.findall(r"0x[a-fA-F0-9]{40}", text)))
    return {"bytes": len(raw),
            "addrs": addrs,
            "kw_free_share": text.lower().count("free share"),
            "kw_first_share_free": text.lower().count("first share free"),
            "kw_free_mint_share": text.lower().count("free mint share"),
            "kw_zh": {k: text.count(k) for k in ["免费份额", "首个免费", "免费铸造", "免费mint"]}}

bb = {}
for lang in ("en", "zh"):
    try:
        bb[lang] = boltbook(lang)
    except Exception as e:
        bb[lang] = {"error": f"{type(e).__name__}: {e}"}
out["leg2"] = bb
seen = json.load(open(BASE + "hot-leg-seen.json"))
bb_new = []
for lang in ("en", "zh"):
    for a in bb.get(lang, {}).get("addrs", []):
        if a not in seen and a not in bb_new:
            bb_new.append(a)
out["leg2_new_vs_seen"] = bb_new

# --- Shape-check new contracts (legs 1+2) ---
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeMintedTotal"]
MINT_FNS = ["mint", "mintFree", "claimFree", "claim"]
QUOTE_FNS = ["quote", "cost", "PRICE", "price"]
AGENT_MARKERS = ["agentRegistry", "registry", "AGENT_ID", "AgentGate",
                 "agentGate", "isAgent", "hasAgentId", "agentIdRequired"]
TOKEN_FNS = ["name", "symbol", "decimals", "totalSupply"]

def find_abi(obj):
    if isinstance(obj, list) and obj and all(
            isinstance(x, dict) and x.get("type") in ("function", "event", "constructor", "error")
            for x in obj if isinstance(x, dict)):
        return obj
    if isinstance(obj, dict):
        for v in obj.values():
            a = find_abi(v)
            if a is not None: return a
    if isinstance(obj, list):
        for v in obj:
            a = find_abi(v)
            if a is not None: return a
    return None

def shape_check(addr):
    abi, err = None, None
    try:
        raw = fetch(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=12)
        abi = find_abi(json.loads(raw))
        if abi is None: err = "v2-no-abi"
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
    has_agent = any(m.lower() in n.lower() for n in names for m in AGENT_MARKERS) or code_reg is True
    is_token = all(f in names for f in TOKEN_FNS)
    s1 = has_mint and has_quote and bool(free_found) and has_agent
    s2 = is_token and ("mintFree" in names) \
        and (("freeClaimed" in names or "freeMinted" in names) or bool(free_found)) \
        and any(x in names for x in ["FREE_SLOTS", "FREE_SUPPLY"]) and has_agent
    return {"address": addr, "S1": bool(s1), "S2": bool(s2),
            "mint": has_mint, "quote": has_quote, "free": free_found,
            "agent": bool(has_agent), "token": bool(is_token),
            "abi_err": err, "code_registry": code_reg,
            "fn_names": sorted(names) if names else []}

new_all = list(dict.fromkeys(sourcify_new + bb_new))
shapes = {}
if new_all:
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(shape_check, a): a for a in new_all}
        for f in as_completed(futs):
            try: shapes[futs[f]] = f.result()
            except Exception as e: shapes[futs[f]] = {"address": futs[f], "error": f"{type(e).__name__}: {e}"}
out["shapes"] = shapes
out["sale_shapes"] = [s for s in shapes.values() if s.get("S1") or s.get("S2")]

# record newly seen (non-sale-shape notes)
seen = json.load(open(BASE + "hot-leg-seen.json"))
for a in sourcify_new:
    s = shapes.get(a, {})
    seen[a] = {"first_seen_wib": "2026-11-10 01:34 WIB", "source": "sourcify-feed",
               "status": "checked-sale-shape" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape",
               "note": str(s)[:500]}
for a in bb_new:
    s = shapes.get(a, {})
    seen[a] = {"first_seen_wib": "2026-11-10 01:34 WIB", "source": "boltbook-en",
               "status": "checked-sale-shape" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape",
               "note": str(s)[:500]}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["seen_total"] = len(seen)

# --- Bridge leg (read-only) ---
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for sec in ("contracts", "track_c", "pending_claims"):
        for name, e in (snap.get(sec) or {}).items():
            a = (e.get("address") or e.get("sale") or "") if isinstance(e, dict) else ""
            if a: snap_addrs.add(a.lower())
    bcontracts = bridge.get("contracts", {}) or {}
    in_snap = [a for a in bcontracts if a.lower() in snap_addrs]
    not_in_snap = [a for a in bcontracts if a.lower() not in snap_addrs]
    discarded = [a for a, e in bcontracts.items() if isinstance(e, dict) and e.get("same_owner_discarded")]
    out["bridge"] = {"contracts_n": len(bcontracts), "same_owner_discarded_n": len(discarded),
                     "in_snapshot": len(in_snap), "not_in_snapshot": len(not_in_snap),
                     "not_in_snapshot_addrs": not_in_snap,
                     "note": "read-only; bridge never written by hot leg; no promotion unless hot-leg re-read shows a snapshot contract newly meeting tier criteria"}
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {e}", "note": "bridge skipped, run continues"}

out["duration_sec"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + "hot-leg-run-2026-11-10-0134.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:8000])
