#!/usr/bin/env python3
"""free-mint-hot-leg run 2026-11-10 01:44 WIB (scheduled 01:44:38).
Lean/fast variant of hot-leg-2026-11-09-2304.py: parallel ABI fetch
(ThreadPoolExecutor), same chunked (<=20) read-only eth_call re-read of the
48 baseline items from hot-leg-2026-11-09-2339-reread.json, read-only bridge
leg. Writes only own hot-leg state files. No chain-wide scan, no preview/mint.
"""
import json, re, time, subprocess, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {
    "0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
    "0x8b47354e7b76b1970a0d06365c8244a810d37493",
}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeMintedTotal"]
MINT_FNS = ["mint", "mintFree", "claimFree", "claim"]
QUOTE_FNS = ["quote", "cost", "PRICE", "price"]
AGENT_MARKERS = ["agentRegistry", "registry", "AGENT_ID", "AgentGate",
                 "agentGate", "isAgent", "hasAgentId", "agentIdRequired"]
TOKEN_FNS = ["name", "symbol", "decimals", "totalSupply"]
T0 = time.time()
RUN = "free-mint-hot-leg 2026-11-10 01:44 WIB (scheduled 01:44:38 WIB)"
UA = {"User-Agent": "hot-leg/1.0"}

try:
    from Crypto.Hash import keccak as _k
    def sel(sig):
        h = _k.new(digest_bits=256); h.update(sig.encode())
        return "0x" + h.hexdigest()[:8]
except Exception:
    sel = None

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def rpc_batch(calls, url):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for i, (to, data) in enumerate(calls)]).encode()
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

RPCS = ["https://bsc-dataseed.bnbchain.org", "https://rpc.ankr.com/bsc"]
CHUNK = 20

def rpc_calls_chunked(calls):
    results = [None] * len(calls)
    failed = []
    used = None
    for s0 in range(0, len(calls), CHUNK):
        sub = calls[s0:s0 + CHUNK]
        done = False
        for url in RPCS:
            try:
                res = rpc_batch(sub, url)
                if isinstance(res, list) and len(res) == len(sub):
                    if len(res) == 1 and isinstance(res[0], dict) and "error" in res[0] and len(sub) > 1:
                        continue
                    results[s0:s0 + len(sub)] = [it.get("result") if isinstance(it, dict) else None for it in res]
                    used = url
                    done = True
                    break
            except Exception:
                continue
        if not done:
            failed.extend(range(s0, s0 + len(sub)))
    return results, failed, used

def decode_int(r):
    if isinstance(r, str) and r.startswith("0x") and len(r) > 2:
        try:
            return int(r, 16)
        except Exception:
            return None
    return None

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
    abi = None
    abi_err = None
    try:
        raw = fetch(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=12)
        abi = find_abi(json.loads(raw))
        if abi is None:
            abi_err = "v2-no-abi"
    except Exception as e:
        abi_err = f"{type(e).__name__}: {e}"
    names = set()
    if abi:
        for fn in abi:
            if isinstance(fn, dict) and fn.get("type") == "function":
                names.add(fn.get("name", ""))
    code_has_registry = None
    if not abi:
        try:
            payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                                  "params": [addr, "latest"]}).encode()
            req = urllib.request.Request(RPCS[0], data=payload,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                code = json.load(r).get("result", "")
            code_has_registry = REGISTRY[2:].lower() in (code or "").lower()
        except Exception as e:
            code_has_registry = f"err:{type(e).__name__}"
    has_mint = bool(names & set(MINT_FNS))
    has_quote = bool(names & set(QUOTE_FNS))
    free_found = [f for f in FREE_VIEWS if f in names]
    has_agent = any(m.lower() in n.lower() for n in names for m in AGENT_MARKERS) \
        or code_has_registry is True
    is_token = bool(names & set(TOKEN_FNS))
    s1 = has_mint and has_quote and bool(free_found) and has_agent
    s2 = is_token and ("mintFree" in names) \
        and (("freeClaimed" in names or "freeMinted" in names) or bool(free_found)) \
        and any(x in names for x in ["FREE_SLOTS", "FREE_SUPPLY"]) and has_agent
    return {"address": addr, "S1": bool(s1), "S2": bool(s2),
            "mint": bool(has_mint), "quote": bool(has_quote),
            "free": free_found, "agent": bool(has_agent),
            "token": bool(is_token), "abi_err": abi_err,
            "code_registry": code_has_registry}

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_lower = {k.lower(): k for k in seen}
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
snap_pending = snap.get("pending_claims", {}) or {}
log = {"run": RUN}

# ---------- leg 1: Sourcify feed ----------
feed_addrs, feed_err, verified = [], None, []
try:
    try:
        raw = fetch("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=20)
    except Exception:
        time.sleep(2)
        raw = fetch("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=20)
    feed = json.loads(raw)
    items = feed.get("results", feed) if isinstance(feed, dict) else feed
    for it in items:
        if isinstance(it, dict) and it.get("address"):
            feed_addrs.append(it["address"])
            if it.get("verifiedAt"):
                verified.append(it["verifiedAt"])
except Exception as e:
    feed_err = f"{type(e).__name__}: {e}"
log["leg1_feed"] = {"n": len(feed_addrs), "addrs": feed_addrs, "error": feed_err,
                    "verifiedAt_range": f"{min(verified)}-{max(verified)}" if verified else None}
new_feed = [a for a in feed_addrs if a.lower() not in seen_lower
            and a.lower() != REGISTRY.lower() and a.lower() not in EXCLUDED]
new_excluded = [a for a in feed_addrs if a.lower() in EXCLUDED]
shapes = []
if new_feed:
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(shape_check, a): a for a in new_feed}
        for f in as_completed(futs):
            try:
                shapes.append(f.result())
            except Exception as e:
                shapes.append({"address": futs[f], "error": f"{type(e).__name__}: {e}"})
    shapes.sort(key=lambda s: new_feed.index(s["address"]))
for a in new_feed:
    seen[a] = "2026-11-10 01:44 WIB"
log["leg1"] = {"new": new_feed, "new_excluded_rediscovered": new_excluded,
               "shapes": shapes, "seen_total": len(seen)}

# ---------- leg 2: Boltbook EN + ZH ----------
def boltbook(url):
    try:
        return fetch(url, timeout=15), None
    except Exception as e:
        pass
    # curl fallback (urllib IncompleteRead hit Boltbook at 23:39; curl worked)
    try:
        out = subprocess.run(["curl", "-sL", "--max-time", "20", url],
                             capture_output=True, timeout=25)
        if out.stdout:
            return out.stdout, None
        return b"", f"curl-empty: {out.stderr.decode()[:100]}"
    except Exception as e2:
        return b"", f"urllib+curl failed: {e2}"

en_raw, en_err = boltbook("https://boltbook.fun/")
zh_raw, zh_err = boltbook("https://boltbook.fun/?lang=zh")
open(BASE + "hot-leg-2026-11-10-0144-boltbook-en.html", "wb").write(en_raw)
open(BASE + "hot-leg-2026-11-10-0144-boltbook-zh.html", "wb").write(zh_raw)
en_txt = en_raw.decode("utf-8", "ignore")
zh_txt = zh_raw.decode("utf-8", "ignore")
en_addrs = list(dict.fromkeys(re.findall(r"0x[a-fA-F0-9]{40}", en_txt)))
zh_addrs = list(dict.fromkeys(re.findall(r"0x[a-fA-F0-9]{40}", zh_txt)))
all_bb = list(dict.fromkeys(en_addrs + zh_addrs))
kw_hits = {}
for k in ["free share", "first share free", "1 free share", "free mint share"]:
    kw_hits[k] = en_txt.lower().count(k.lower()) + zh_txt.lower().count(k.lower())
for k in ["免费份额", "首个免费", "免费铸造", "免费mint"]:
    kw_hits[k] = en_txt.count(k) + zh_txt.count(k)
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
    seen[a] = "2026-11-10 01:44 WIB"
log["leg2_boltbook"] = {
    "en_bytes": len(en_raw), "en_err": en_err,
    "zh_bytes": len(zh_raw), "zh_err": zh_err,
    "en_addrs": len(en_addrs), "zh_addrs": len(zh_addrs),
    "unique_addrs": len(all_bb), "keyword_hits": kw_hits,
    "new_vs_seen": bb_new, "new_vs_snapshot": bb_new_vs_snap,
    "shape_check": bb_shapes, "seen_total": len(seen)}

# ---------- leg 3: new sale-shapes ----------
sale_shapes = [s for s in shapes if s.get("S1") or s.get("S2")]
sale_shapes += [dict(s, address=a) for a, s in bb_shapes.items() if s.get("S1") or s.get("S2")]
log["leg3_new_sale_shapes"] = sale_shapes
log["leg3_verify"] = "None - no new sale-shape contract this run" if not sale_shapes else "pending-manual"

# ---------- bridge leg (read-only) ----------
bridge = json.load(open(BASE + "scan-bridge.json"))
bcontracts = bridge.get("contracts", {}) if isinstance(bridge, dict) else {}
b_disc = sum(1 for ent in bcontracts.values()
             if isinstance(ent, dict) and ent.get("same_owner_discarded"))
b_in_snap = sum(1 for addr in bcontracts if addr.lower() in snap_addrs)
log["bridge_leg"] = {"total": len(bcontracts), "same_owner_discarded": b_disc,
                     "in_snapshot_addr": b_in_snap,
                     "not_in_snapshot_addr": len(bcontracts) - b_in_snap,
                     "note": "Bridge is read-only for this job; promotions only if a bridge contract already in snapshot newly meets a tier or changes state."}

# ---------- leg 4: re-read baseline items ----------
NOARG = ["totalSupply", "totalMinted", "totalMints", "freeMinted", "freeClaimed",
         "freeMintedTotal", "freeLeft", "freeUsed", "FREE_CAP", "FREE_SUPPLY",
         "FREE_SLOTS", "FREE_SHARES", "FREE_QUOTA", "FREE_PER_WALLET", "remainingFree",
         "MAX_SUPPLY", "MAX_FREE", "sharesMinted", "sold", "phase", "launched",
         "soldOut", "closed", "finalized", "mintOpen", "mintActive",
         "totalSkunksMinted", "freeSkunksClaimed", "freeSkunksRemaining",
         "freeRemaining", "mintCount", "MAX_MINTS", "opened", "openedAt", "saleActive",
         "soldShares", "publicMinted", "launchTime", "totalShares", "totalFreeShares",
         "mintingOpen", "TOTAL_SHARES", "MAX_FREE_SHARES", "SALE_START", "isSaleEnded",
         "remaining", "mintEnd", "mintStart", "SALE_END", "startTime",
         "freeWindowOpen", "agentFreeUsed", "AGENT_FREE_CAP", "paidMinted"]
ADDRARG = ["balanceOf", "mintedBy", "freeClaimed", "freeLeft", "freeUsed",
           "freeCount", "freeMinted", "mintedCount", "freeAvailable",
           "hasMinted", "quotaOf", "freeTakenBy", "priceFor", "freeClaimedBy",
           "freeUsedByWallet", "hasFreeMinted", "freeAllowance", "maxShares", "remainingShares"]
ADDRUINT = ["quote", "freeFor"]

def calldata(field):
    if sel is None:
        return None
    if field.endswith("_user1"):
        fn = field[:-6]
        if fn in ADDRUINT:
            return sel(f"{fn}(address,uint256)") + USER[2:].lower().rjust(64, "0") + format(1, "064x")
        return None
    if field.endswith("_user"):
        fn = field[:-5]
        if fn in ADDRARG:
            return sel(f"{fn}(address)") + USER[2:].lower().rjust(64, "0")
        return None
    if field in NOARG:
        return sel(f"{field}()")
    return None

prev_rr = json.load(open(BASE + "hot-leg-2026-11-10-0039-reread.json"))
prev_items = prev_rr.get("items", {})
prev_block = prev_rr.get("block")
jobs = []
for name, entry in prev_items.items():
    for field in entry:
        if field == "address":
            continue
        d = calldata(field)
        if d:
            jobs.append((name, field, entry["address"], d))
calls = [(to, data) for (_, _, to, data) in jobs]
res, failed_idx, rpc_used = rpc_calls_chunked(calls)
items_now = {}
read_failed = []
if res is not None:
    for i, ((name, field, addr, _), r) in enumerate(zip(jobs, res)):
        items_now.setdefault(name, {"address": addr})
        v = decode_int(r)
        if v is None:
            items_now[name][field] = prev_items.get(name, {}).get(field)
            read_failed.append({"item": name, "field": field})
        else:
            items_now[name][field] = v
    for name in prev_items:
        items_now.setdefault(name, dict(prev_items[name]))
    blk = None
    try:
        payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber",
                              "params": []}).encode()
        req = urllib.request.Request(rpc_used if isinstance(rpc_used, str) else RPCS[0],
                                     data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as rr2:
            blk = int(json.load(rr2).get("result", "0x0"), 16)
    except Exception:
        blk = None
else:
    blk = None
    items_now = {name: dict(entry) for name, entry in prev_items.items()}

changes = []
for name, entry in items_now.items():
    old = prev_items.get(name, {})
    for field, val in entry.items():
        if field == "address":
            continue
        if old.get(field) != val:
            changes.append({"item": name, "field": field, "old": old.get(field), "new": val})
log["leg4"] = {"block": blk, "prev_block": prev_block, "rpc": rpc_used,
               "items_n": len(items_now), "changes": changes,
               "failed_call_idx": failed_idx, "read_failed": read_failed,
               "mode": "chunked eth_call batches of <=20 (read-only); null reads keep baseline, never a change"}
log["leg4_items"] = items_now

promo_flags = []
snap_contracts = snap.get("contracts", {}) or {}
snap_trackc = snap.get("track_c", {}) or {}
for name, entry in items_now.items():
    meta = snap_contracts.get(name) or snap_trackc.get(name) or {}
    status = (meta.get("status") or "") if isinstance(meta, dict) else ""
    free = entry.get("freeMinted", entry.get("freeClaimed", entry.get("freeMintedTotal")))
    cap = entry.get("FREE_CAP", entry.get("FREE_SUPPLY", entry.get("FREE_SHARES",
          entry.get("FREE_QUOTA", entry.get("MAX_SUPPLY")))))
    if isinstance(free, int) and isinstance(cap, int) and cap > 0:
        pct = free / cap
        user_open = entry.get("freeClaimed_user") in (0, False, None) or entry.get("balanceOf_user") == 0
        if free >= cap:
            promo_flags.append({"item": name, "flag": "sellout?", "pct": round(pct, 4),
                                "free": free, "cap": cap, "snap_status": status})
        elif pct >= 0.25 and user_open:
            promo_flags.append({"item": name, "flag": "promo-candidate-check",
                                "pct": round(pct, 4), "free": free, "cap": cap,
                                "snap_status": status})
log["leg4_promo_flags"] = promo_flags
log["pending_claims"] = "snapshot pending_claims empty at run start - nothing to re-read" \
    if not snap_pending else f"{len(snap_pending)} pending claims - NOT re-read this run (bulk leg skipped)"
log["duration_s"] = round(time.time() - T0, 1)

with open(BASE + "hot-leg-run-2026-11-10-0144.json", "w") as f:
    json.dump(log, f, indent=2, ensure_ascii=False)
with open(BASE + "hot-leg-2026-11-10-0144-reread.json", "w") as f:
    json.dump({"block": blk, "items": items_now, "duration_sec": log["duration_s"]},
              f, indent=2, ensure_ascii=False)
with open(BASE + "hot-leg-seen.json", "w") as f:
    json.dump(seen, f, indent=2, ensure_ascii=False)
print(json.dumps({k: log[k] for k in ("leg1", "leg2_boltbook", "leg3_new_sale_shapes",
                                      "bridge_leg", "leg4", "leg4_promo_flags",
                                      "pending_claims", "duration_s")}, indent=2, ensure_ascii=False))
