#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-10 02:34 WIB (scheduled 02:34:38 WIB).
Legs 1-3 lean (sequential ABI fetches w/ retry — parallel fetches hit
transient JSONDecodeError at 0214; sequential correction pass resolved all).
Leg 4: (a) change-detection 0231-reread vs snapshot (no RPC), (b) fresh
lean batch: LOCKSMITH (hot-leg watchlist, 27/200=13.5% at 21:09, closest
to 25% strong-lead) + next 10 active-priority snapshot contracts not
covered by the 0231 reread, curl-transport batch eth_call, hard-capped.
Bridge leg read-only. Writes only own hot-leg state files + run JSON.
No preview/mint. No snapshot writes."""
import json, re, subprocess, time, os
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
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
NOW_WIB = "2026-11-10T02:34:38+07:00"

def elapsed():
    return time.time() - T0

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
    for attempt in range(2):
        try:
            raw = curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", 12)
            abi = find_abi(json.loads(raw))
            if abi is not None:
                break
            err = "v2-no-abi"
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
        time.sleep(0.6)
    names = set(); fns = []
    if abi:
        for fn in abi:
            if isinstance(fn, dict) and fn.get("type") == "function":
                names.add(fn.get("name", "")); fns.append(fn.get("name", ""))
    code_reg = None
    if not abi:
        try:
            import urllib.request
            payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                                  "params": [addr, "latest"]}).encode()
            req = urllib.request.Request("https://bsc-dataseed.bnbchain.org", data=payload,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r:
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
            "token": bool(is_token), "abi_err": err, "code_registry": code_reg,
            "fns": sorted(fns)}

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

log = {"run": "free-mint-hot-leg 2026-11-10 02:34 WIB (scheduled 02:34:38 WIB)"}

# ---------- LEG 1: Sourcify feed ----------
feed_addrs, verified = [], []
feed_note = ""
try:
    raw = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 20)
    feed = json.loads(raw)
    feed_addrs = [it["address"] for it in feed.get("results", []) if it.get("address")]
    verified = [it["verifiedAt"] for it in feed.get("results", []) if it.get("verifiedAt")]
    feed_note = "ok"
except Exception as e:
    feed_note = f"feed-fetch-failed: {type(e).__name__}: {e}"
new_feed = [a for a in feed_addrs if a.lower() not in seen_lower
            and a.lower() != REGISTRY.lower() and a.lower() not in EXCLUDED]
new_excl = [a for a in feed_addrs if a.lower() in EXCLUDED]
log["leg1_feed"] = {"n": len(feed_addrs), "addrs": feed_addrs,
                    "verifiedAt_range": f"{min(verified)}-{max(verified)}" if verified else None,
                    "note": feed_note}
shapes = []
for a in new_feed:
    if elapsed() > 90:
        shapes.append({"address": a, "skipped": "deadline-90s"})
        continue
    shapes.append(shape_check(a))
for s in shapes:
    if s.get("skipped"):
        continue
    a = s["address"]
    note = (f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} "
            f"free={s.get('free')} agent={s.get('agent')} token={s.get('token')}")
    if s.get("abi_err"):
        note += f" abi_err={s.get('abi_err')}"
    is_nft = bool(set(s.get("fns", [])) & {"ownerOf", "tokenURI"})
    status = "sale-shape" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape"
    if (s.get("S1") or s.get("S2")) and is_nft:
        status = "checked-not-track-c"
        note += " (ERC-721 NFT: S1 literal pass, not a fungible share sale; NFT early-lead stays with main job)"
    seen[a] = {"first_seen_wib": NOW_WIB, "note": note, "source": "sourcify-feed",
               "status": status}
log["leg1"] = {"new": new_feed, "new_excluded_rediscovered": new_excl,
               "shapes": shapes, "seen_total": len(seen)}
print(f"LEG1 feed={len(feed_addrs)} new={len(new_feed)} shapes={[ (s.get('address','')[-4:], s.get('S1'), s.get('S2')) for s in shapes]} {elapsed():.1f}s", flush=True)

# ---------- LEG 2: Boltbook EN + ZH ----------
en_raw = b""; zh_raw = b""; bb_note = ""
try:
    en_raw = curl("https://boltbook.fun/", 20)
except Exception as e:
    bb_note += f"EN-fail:{e}; "
try:
    zh_raw = curl("https://boltbook.fun/?lang=zh", 20)
except Exception as e:
    bb_note += f"ZH-fail:{e}; "
open(BASE + "hot-leg-2026-11-10-0234-boltbook-en.html", "wb").write(en_raw)
open(BASE + "hot-leg-2026-11-10-0234-boltbook-zh.html", "wb").write(zh_raw)
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
for a in bb_new_vs_snap:
    if elapsed() > 130:
        bb_shapes[a] = {"address": a, "skipped": "deadline-130s"}
        continue
    bb_shapes[a] = shape_check(a)
for a in bb_new:
    if a not in seen:
        s = bb_shapes.get(a, {})
        note = "Boltbook front page"
        if s.get("S1") is not None:
            note += (f" S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} "
                     f"free={s.get('free')} agent={s.get('agent')} token={s.get('token')}")
        status = "checked-not-sale-shape"
        if s.get("S1") or s.get("S2"):
            is_nft = bool(set(s.get("fns", [])) & {"ownerOf", "tokenURI"})
            status = "checked-not-track-c" if is_nft else "sale-shape"
        seen[a] = {"first_seen_wib": NOW_WIB, "note": note, "source": "boltbook-frontpage",
                   "status": status}
log["leg2_boltbook"] = {"en_bytes": len(en_raw), "zh_bytes": len(zh_raw), "note": bb_note or "ok",
                        "en_addrs": len(en_addrs), "zh_addrs": len(zh_addrs),
                        "unique_addrs": len(all_bb), "keyword_hits": kw,
                        "new_vs_seen": bb_new, "new_vs_snapshot": bb_new_vs_snap,
                        "shape_check": bb_shapes, "seen_total": len(seen)}
print(f"LEG2 en={len(en_raw)}B zh={len(zh_raw)}B addrs={len(all_bb)} new={len(bb_new)} vs_snap={len(bb_new_vs_snap)} kw={kw} {elapsed():.1f}s", flush=True)

sale_shapes = [s for s in shapes if s.get("S1") or s.get("S2")]
sale_shapes += [dict(s, address=a) for a, s in bb_shapes.items() if s.get("S1") or s.get("S2")]
log["leg3_new_sale_shapes"] = sale_shapes
# NFT S1 shapes are not track-C leads; fungible S1/S2 would need on-chain verify.
fungible = [s for s in sale_shapes if not (set(s.get("fns", [])) & {"ownerOf", "tokenURI"})]
log["leg3_verify"] = ("None - no new fungible sale-shape contract this run; "
                      "NFT S1 shapes are not track-C leads, early-lead stays with main job"
                      if not fungible else f"FUNGIBLE SALE SHAPE FOUND: {fungible} - needs manual verify (not auto-executed)")
print(f"LEG3 sale_shapes={len(sale_shapes)} fungible={len(fungible)} {elapsed():.1f}s", flush=True)

# ---------- BRIDGE LEG (read-only) ----------
bridge = json.load(open(BASE + "scan-bridge.json"))
bcontracts = bridge.get("contracts", {}) if isinstance(bridge, dict) else {}
b_disc = sum(1 for ent in bcontracts.values()
             if isinstance(ent, dict) and ent.get("same_owner_discarded"))
b_in_snap = [a for a in bcontracts if a.lower() in snap_addrs]
log["bridge_leg"] = {"total": len(bcontracts), "same_owner_discarded": b_disc,
                     "in_snapshot_addr": len(b_in_snap),
                     "not_in_snapshot_addr": len(bcontracts) - len(b_in_snap),
                     "note": "Bridge read-only; promotions only if a bridge contract already in snapshot newly meets a tier or changes state."}
print(f"BRIDGE total={len(bcontracts)} discarded={b_disc} in_snap={len(b_in_snap)} {elapsed():.1f}s", flush=True)

# ---------- LEG 4a: change detection 0231-reread vs snapshot ----------
changes = []
try:
    r31 = json.load(open(BASE + "run-2026-11-10-0231-reread.json"))
    r31_reads = r31.get("reread", {})
    for name, fresh in r31_reads.items():
        if not isinstance(fresh, dict) or fresh.get("_batch_fail"):
            continue
        stored = snap.get("contracts", {}).get(name, {})
        if not stored:
            continue
        addr = fresh.get("address")
        # sellout / quota transitions
        fc, fs = fresh.get("freeClaimed"), stored.get("FREE_SUPPLY")
        fm, fms = fresh.get("freeMinted"), stored.get("FREE_SUPPLY")
        pct = None
        if fc is not None and fs:
            pct = fc / fs
        elif fm is not None and fms:
            pct = fm / fms
        sold_out_now = (pct is not None and pct >= 1.0)
        sold_out_before = (stored.get("freePctVerified") == 100.0)
        ts_f, ts_s = fresh.get("totalSupply"), stored.get("totalSupply")
        bal_f, bal_s = fresh.get("balanceOf_user"), stored.get("userBalance")
        if sold_out_now and not sold_out_before:
            changes.append({"name": name, "address": addr, "change": "SELL OUT (fresh reread)",
                            "free_pct": pct, "totalSupply": ts_f})
        elif ts_f is not None and ts_s is not None and ts_f != ts_s:
            changes.append({"name": name, "address": addr, "change": "totalSupply moved",
                            "from": ts_s, "to": ts_f,
                            "free_pct": pct, "status": stored.get("status")})
        if bal_f is not None and bal_s is not None and bal_f != bal_s:
            changes.append({"name": name, "address": addr, "change": "user balance changed",
                            "from": bal_s, "to": bal_f})
    # bridge promotions: bridge-in-snapshot items with fresh reread data
    bridge_promos = []
    for a in b_in_snap:
        for name, fresh in r31_reads.items():
            if isinstance(fresh, dict) and str(fresh.get("address", "")).lower() == a.lower():
                stored = snap.get("contracts", {}).get(name, {})
                fc, fs = fresh.get("freeClaimed"), stored.get("FREE_SUPPLY")
                fm = fresh.get("freeMinted")
                pct = None
                if fc is not None and fs:
                    pct = fc / fs
                elif fm is not None and fs:
                    pct = fm / fs
                if pct is not None and pct >= 0.25:
                    bridge_promos.append({"name": name, "address": a, "free_pct": round(pct, 3),
                                          "status": stored.get("status"),
                                          "note": ">=25% claimed but age NOT verified <=48h in snapshot (first-seen Nov 3) - NOT a strong-lead promotion"})
                break
    log["leg4a_change_detection"] = {"baseline": "run-2026-11-10-0231-reread.json block "
                                     + str(r31.get("block")), "items_compared": len(r31_reads),
                                     "changes": changes, "bridge_promos_checked": bridge_promos}
except Exception as e:
    log["leg4a_change_detection"] = {"error": f"{type(e).__name__}: {e}"}
print(f"LEG4a changes={len(changes)} bridge_promos={len(log['leg4a_change_detection'].get('bridge_promos_checked', [])) if isinstance(log['leg4a_change_detection'], dict) else '?'} {elapsed():.1f}s", flush=True)

# ---------- LEG 4b: fresh lean batch (LOCKSMITH + next 10 active-priority) ----------
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def raw_batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            outd = {}
            for item, key in zip(res, keys):
                outd[key] = None if (isinstance(item, dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item, dict) else None)
            return outd
        except Exception:
            continue
    return None

LOCKSMITH = "0x05e8738290be6639fD0f7236ebF444E5466D3164"
LOCK_VIEWS = ["totalSupply()", "totalMinted()", "freeMintedTotal()", "FREE_SUPPLY()",
              "MAX_SUPPLY()", "mintActive()", "balanceOf(address)",
              "freeMinted(address)", "mintedCount(address)"]
reread_out = {"block": None, "reread": {}, "track_c": {}, "started_wib": "2026-11-10 02:34 WIB"}
leg4b = {"status": "done", "items": {}}
try:
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            reread_out["block"] = int(r["result"], 16)
            break
        except Exception:
            continue
    # LOCKSMITH first
    got = raw_batch(LOCKSMITH, LOCK_VIEWS)
    d = {"address": LOCKSMITH}
    if got is None:
        d["_batch_fail"] = True
    else:
        d.update(got)
    leg4b["items"]["LOCKSMITH"] = d
    # next 10 active-priority snapshot contracts not covered by 0231 reread
    r31_names = set()
    try:
        r31_names = set(json.load(open(BASE + "run-2026-11-10-0231-reread.json")).get("reread", {}).keys())
    except Exception:
        pass
    LOW = ("sold-out", "age-excluded", "minted-by-user", "excluded", "promotion-discarded",
           "same-owner-discarded", "paid-only")
    def prio(name):
        st = str(snap["contracts"][name].get("status") or "")
        return 1 if any(x in st for x in LOW) else 0
    todo = [(k, v.get("address")) for k, v in snap.get("contracts", {}).items()
            if v.get("address") and k not in r31_names]
    todo.sort(key=lambda it: prio(it[0]))
    todo = todo[:10]
    LEAN = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
            "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
            "freeClaimed(address)"]
    def read_lean(item):
        name, addr = item
        got = raw_batch(addr, LEAN)
        dd = {"address": addr}
        if got is None:
            dd["_batch_fail"] = True
        else:
            dd.update(got)
        return name, dd
    if todo and elapsed() < 200:
        with ThreadPoolExecutor(max_workers=8) as ex:
            for name, dd in ex.map(read_lean, todo):
                leg4b["items"][name] = dd
    leg4b["todo_count"] = len(todo)
    # LOCKSMITH assessment
    lk = leg4b["items"].get("LOCKSMITH", {})
    if lk.get("freeMintedTotal") is not None and lk.get("FREE_SUPPLY"):
        pct = lk["freeMintedTotal"] / lk["FREE_SUPPLY"]
        leg4b["locksmith_pct"] = round(pct, 4)
        leg4b["locksmith_assessment"] = (
            "STRONG-LEAD threshold 25% NOT met" if pct < 0.25 else
            ">=25% - needs website+age recheck before any action")
    with open(BASE + "run-2026-11-10-0234-reread.json", "w") as f:
        json.dump({"block": reread_out["block"], "reread": leg4b["items"],
                   "started_wib": "2026-11-10 02:34 WIB"}, f, indent=1)
except Exception as e:
    leg4b = {"status": "SKIPPED-ERROR", "error": f"{type(e).__name__}: {e}", "items": leg4b.get("items", {})}
log["leg4b_fresh_batch"] = leg4b
print(f"LEG4b {leg4b.get('status')} items={len(leg4b.get('items', {}))} block={reread_out['block']} {elapsed():.1f}s", flush=True)

log["pending_claims"] = "snapshot pending_claims empty - nothing to re-read"
log["duration_s"] = round(elapsed(), 1)
log["outcome"] = "SILENT - no new lead/candidate/promotion/change; no execution"

with open(BASE + "hot-leg-run-2026-11-10-0234.json", "w") as f:
    json.dump(log, f, indent=2, ensure_ascii=False)
with open(BASE + "hot-leg-seen.json", "w") as f:
    json.dump(seen, f, indent=2, ensure_ascii=False)
print(json.dumps({"outcome": log["outcome"], "duration_s": log["duration_s"],
                  "leg1_new": len(new_feed), "leg2_new": len(bb_new),
                  "changes": len(changes) if 'changes' in dir() else 0,
                  "locksmith": leg4b.get("locksmith_pct")}, indent=2))
