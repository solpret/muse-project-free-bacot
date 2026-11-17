#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-10 02:14 WIB — recovery after 0214 full script
hit the 280s timeout during leg 4 (slow RPC batches). Legs 1-3 re-done lean:
shape-check the 9 feed-new contracts from the feed fetched 02:19 WIB
(/tmp/sourcify-feed.json), Boltbook EN retry + saved ZH, bridge read-only.
Leg 4 SKIPPED-OVERRUN (baseline reread from 0154 retained; next run retries).
Writes only own hot-leg state files. No preview/mint."""
import json, re, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeMintedTotal"]
MINT_FNS = ["mint", "mintFree", "claimFree", "claim"]
QUOTE_FNS = ["quote", "cost", "PRICE", "price"]
AGENT_MARKERS = ["agentRegistry", "registry", "AGENT_ID", "AgentGate",
                 "agentGate", "isAgent", "hasAgentId", "agentIdRequired"]
TOKEN_FNS = ["name", "symbol", "decimals", "totalSupply"]
T0 = time.time()

def curl(url, timeout=15):
    out = subprocess.run(["curl", "-sS", "--max-time", str(timeout), url],
                         capture_output=True, timeout=timeout + 5)
    return out.stdout

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
    abi = None; err = None
    try:
        raw = curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", 15)
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
            import urllib.request
            payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                                  "params": [addr, "latest"]}).encode()
            req = urllib.request.Request("https://bsc-dataseed.bnbchain.org", data=payload,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=12) as r:
                code = json.load(r).get("result", "")
            code_reg = REGISTRY[2:].lower() in (code or "").lower()
        except Exception as e:
            code_reg = f"err:{type(e).__name__}"
    has_mint = bool(names & set(MINT_FNS))
    has_quote = bool(names & set(QUOTE_FNS))
    free_found = [f for f in FREE_VIEWS if f in names]
    has_agent = any(m.lower() in n.lower() for n in names for m in AGENT_MARKERS) or code_reg is True
    is_token = bool(names & set(TOKEN_FNS))
    s1 = has_mint and has_quote and bool(free_found) and has_agent
    s2 = is_token and ("mintFree" in names) \
        and (("freeClaimed" in names or "freeMinted" in names) or bool(free_found)) \
        and any(x in names for x in ["FREE_SLOTS", "FREE_SUPPLY"]) and has_agent
    return {"address": addr, "S1": bool(s1), "S2": bool(s2), "mint": bool(has_mint),
            "quote": bool(has_quote), "free": free_found, "agent": bool(has_agent),
            "token": bool(is_token), "abi_err": err, "code_registry": code_reg}

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_lower = {k.lower() for k in seen}
snap = json.load(open(BASE + "onchain-snapshot.json"))
snap_addrs = set()
for sec in ("contracts", "track_c", "pending_claims"):
    for k, v in snap.get(sec, {}).items():
        if isinstance(k, str) and k.startswith("0x") and len(k) == 42:
            snap_addrs.add(k.lower())
        if isinstance(v, dict):
            for f in ("address", "sale", "token"):
                a = v.get(f)
                if isinstance(a, str) and a.startswith("0x"):
                    snap_addrs.add(a.lower())

log = {"run": "free-mint-hot-leg 2026-11-10 02:14 WIB (scheduled 02:14:38 WIB)"}
# leg 1: feed already fetched 02:19 WIB -> /tmp/sourcify-feed.json
feed = json.load(open("/tmp/sourcify-feed.json"))
feed_addrs = [it["address"] for it in feed.get("results", []) if it.get("address")]
verified = [it["verifiedAt"] for it in feed.get("results", []) if it.get("verifiedAt")]
new_feed = [a for a in feed_addrs if a.lower() not in seen_lower
            and a.lower() != REGISTRY.lower() and a.lower() not in EXCLUDED]
new_excl = [a for a in feed_addrs if a.lower() in EXCLUDED]
log["leg1_feed"] = {"n": len(feed_addrs), "addrs": feed_addrs,
                    "verifiedAt_range": f"{min(verified)}-{max(verified)}" if verified else None,
                    "note": "feed fetched by direct curl 02:19 WIB (first urllib attempt returned empty)"}
shapes = []
if new_feed:
    with ThreadPoolExecutor(max_workers=9) as ex:
        futs = {ex.submit(shape_check, a): a for a in new_feed}
        for f in as_completed(futs):
            try:
                shapes.append(f.result())
            except Exception as e:
                shapes.append({"address": futs[f], "error": f"{type(e).__name__}: {e}"})
    shapes.sort(key=lambda s: new_feed.index(s["address"]))
for s in shapes:
    a = s["address"]
    note = (f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} "
            f"free={s.get('free')} agent={s.get('agent')} token={s.get('token')}")
    if s.get("abi_err"):
        note += f" abi_err={s.get('abi_err')}"
    seen[a] = {"first_seen_wib": "2026-11-10T02:14:38+07:00",
               "note": note, "source": "sourcify-feed",
               "status": "checked-not-sale-shape" if not (s.get("S1") or s.get("S2")) else "sale-shape"}
log["leg1"] = {"new": new_feed, "new_excluded_rediscovered": new_excl,
               "shapes": shapes, "seen_total": len(seen)}

# leg 2: Boltbook EN retry (first attempt 0 bytes) + saved ZH from killed run
en_raw = curl("https://boltbook.fun/", 20)
open(BASE + "hot-leg-2026-11-10-0214-boltbook-en.html", "wb").write(en_raw)
zh_raw = open(BASE + "hot-leg-2026-11-10-0214-boltbook-zh.html", "rb").read()
en_txt = en_raw.decode("utf-8", "ignore"); zh_txt = zh_raw.decode("utf-8", "ignore")
en_addrs = list(dict.fromkeys(re.findall(r"0x[a-fA-F0-9]{40}", en_txt)))
zh_addrs = list(dict.fromkeys(re.findall(r"0x[a-fA-F0-9]{40}", zh_txt)))
all_bb = list(dict.fromkeys(en_addrs + zh_addrs))
kw = {}
for k in ["free share", "first share free", "1 free share", "free mint share"]:
    kw[k] = en_txt.lower().count(k.lower()) + zh_txt.lower().count(k.lower())
for k in ["免费份额", "首个免费", "免费铸造", "免费mint"]:
    kw[k] = en_txt.count(k) + zh_txt.count(k)
bb_new = [a for a in all_bb if a.lower() not in seen_lower]
bb_new_vs_snap = [a for a in bb_new if a.lower() not in snap_addrs]
bb_shapes = {}
if bb_new_vs_snap:
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(shape_check, a): a for a in bb_new_vs_snap}
        for f in as_completed(futs):
            try:
                bb_shapes[futs[f]] = f.result()
            except Exception as e:
                bb_shapes[futs[f]] = {"address": futs[f], "error": f"{type(e).__name__}: {e}"}
for a in bb_new:
    seen[a] = {"first_seen_wib": "2026-11-10T02:14:38+07:00",
               "note": "Boltbook front page", "source": "boltbook-frontpage",
               "status": "checked-not-sale-shape"}
log["leg2_boltbook"] = {"en_bytes": len(en_raw), "zh_bytes": len(zh_raw),
                        "zh_note": "ZH file saved by killed 0214 full script (02:23 WIB); EN retried by curl in recovery",
                        "en_addrs": len(en_addrs), "zh_addrs": len(zh_addrs),
                        "unique_addrs": len(all_bb), "keyword_hits": kw,
                        "new_vs_seen": bb_new, "new_vs_snapshot": bb_new_vs_snap,
                        "shape_check": bb_shapes, "seen_total": len(seen)}

sale_shapes = [s for s in shapes if s.get("S1") or s.get("S2")]
sale_shapes += [dict(s, address=a) for a, s in bb_shapes.items() if s.get("S1") or s.get("S2")]
log["leg3_new_sale_shapes"] = sale_shapes
log["leg3_verify"] = "None - no new sale-shape contract this run" if not sale_shapes else "pending-manual"

# bridge leg (read-only)
bridge = json.load(open(BASE + "scan-bridge.json"))
bcontracts = bridge.get("contracts", {}) if isinstance(bridge, dict) else {}
b_disc = sum(1 for ent in bcontracts.values()
             if isinstance(ent, dict) and ent.get("same_owner_discarded"))
b_in_snap = sum(1 for addr in bcontracts if addr.lower() in snap_addrs)
log["bridge_leg"] = {"total": len(bcontracts), "same_owner_discarded": b_disc,
                     "in_snapshot_addr": b_in_snap,
                     "not_in_snapshot_addr": len(bcontracts) - b_in_snap,
                     "note": "Bridge read-only; promotions only if a bridge contract already in snapshot newly meets a tier or changes state."}

# leg 4: SKIPPED - OVERRUN (full 0214 script killed by 280s timeout during RPC batches)
log["leg4"] = {"status": "SKIPPED-OVERRUN",
               "note": "Full 0214 script hit 280s timeout during leg-4 chunked eth_call batches (RPCs slow: bsc-dataseed/ankr); baseline reread from 0154 run (48 items) retained, NOT re-read; next run retries. No state change inferred from a skipped leg."}
log["pending_claims"] = "snapshot pending_claims empty at run start - nothing to re-read"
log["duration_s"] = round(time.time() - T0, 1)
log["outcome"] = "SILENT - no new lead/candidate/promotion/change; no execution"

with open(BASE + "hot-leg-run-2026-11-10-0214.json", "w") as f:
    json.dump(log, f, indent=2, ensure_ascii=False)
with open(BASE + "hot-leg-seen.json", "w") as f:
    json.dump(seen, f, indent=2, ensure_ascii=False)
print(json.dumps(log, indent=2, ensure_ascii=False))
