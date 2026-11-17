#!/usr/bin/env python3
"""Hot-leg run 2026-11-09 17:34 WIB - LEG4 CONTINUATION.
The main 1734 process (hot-leg-run-2026-11-09-1734.py) completed legs 1-2
(feed + Boltbook, seen updated, artifacts on disk) but was killed mid-leg4
prefetch (session reaped ~17:44 WIB, no final JSON, no reread file).
This script completes legs 3-4 + bridge + diff, reusing the saved artifacts.
RPC fallback is BOUNDED (no per-call fallback storm that burned the first attempt):
chunk fail -> sub-chunks of 5 once -> None (read artifact, never a change).
Read-only except own hot-leg state files. Never writes main snapshot."""
import json, re, sys, time, os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-09-1734"
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"run": "free-mint-hot-leg 2026-11-09 17:34:38 WIB (leg4 continuation)",
       "note": "Main 1734 process killed mid-leg4 prefetch; legs 1-2 recovered from saved artifacts, legs 3-4+bridge completed here."}
t0 = time.time()
def log(*a):
    print(*a, flush=True)

# ---------- Recover legs 1-2 from saved artifacts ----------
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
feed = json.load(open(f"{BASE}/hot-leg-{TS}-sourcify.json"))
items = feed.get("results", feed) if isinstance(feed, dict) else feed
feed_addrs = [it.get("address") for it in items if it.get("address")]
shapes = json.load(open(f"{BASE}/hot-leg-{TS}-sourcify-shape.json"))
en = open(f"{BASE}/hot-leg-{TS}-boltbook-en.html").read()
zh = open(f"{BASE}/hot-leg-{TS}-boltbook-zh.html").read()
addr_re = re.compile(r"0x[a-fA-F0-9]{40}")
en_addrs = sorted(set(addr_re.findall(en)))
zh_addrs = sorted(set(addr_re.findall(zh)))
all_addrs = sorted(set(en_addrs) | set(zh_addrs))
kw = ["free share", "first share free", "1 free share", "free mint share",
      "免费份额", "首个免费", "免费铸造", "免费mint"]
tl = (en + zh).lower()
kw_hits = {k: tl.count(k.lower()) for k in kw}
new_feed = [s for s in shapes]
out["leg1_feed"] = {"n": len(feed_addrs), "addrs": feed_addrs}
out["leg1"] = {"new": [s["address"] for s in shapes],
               "shapes": [{k: v for k, v in s.items() if k != "abi_functions"} for s in shapes],
               "seen_total": len(seen)}
out["leg2_boltbook"] = {"en_bytes": len(en), "zh_bytes": len(zh),
                        "en_addrs": len(en_addrs), "zh_addrs": len(zh_addrs),
                        "unique_addrs": len(all_addrs), "keyword_hits": kw_hits,
                        "new_vs_seen_shape_checked": ["0x698Fe50F0cF952CC9ba0F84cc34a8038AABEFaEe",
                                                      "0x9ca0078118e3a2346701b48f1c1c04eab0701f48"],
                        "new_vs_seen_in_snapshot_no_shape_check": ["0x86f83e98437a1dcf0e4a62828f68c1d53b3c7ab5",
                                                                    "0xd6fcf9db58a559aafbbf9fd823f4f081e6701311"],
                        "seen_total": len(seen)}
out["leg3_new_sale_shapes"] = []
out["leg3_verify"] = "None - no new sale-shape contract this run (all 5 new feed shapes S1/S2=False; 2 new Boltbook addrs shape-checked, not sale-shape; 2 more already in snapshot)"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
out["pending_claims"] = snap.get("pending_claims") or "snapshot pending_claims empty at run start - nothing to re-read"
log("legs 1-3 recovered; starting leg4")

# ---------- Bridge leg (read-only) ----------
try:
    bridge = json.load(open(f"{BASE}/scan-bridge.json"))
    bcontracts = bridge.get("contracts", {})
    snap_addr_set = {v.get("address", "").lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
    for v in snap.get("track_c", {}).values():
        if isinstance(v, dict):
            for k in ("sale", "token", "address"):
                if v.get(k):
                    snap_addr_set.add(str(v[k]).lower())
    discarded = [a for a, v in bcontracts.items() if v.get("same_owner_discarded")]
    in_snap = [a for a in bcontracts if a.lower() in snap_addr_set]
    not_in_snap = [a for a in bcontracts if a.lower() not in snap_addr_set]
    mtime = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(os.path.getmtime(f"{BASE}/scan-bridge.json")))
    out["bridge_leg"] = {"total": len(bcontracts), "same_owner_discarded": len(discarded),
                         "in_snapshot_addr": len(in_snap), "not_in_snapshot_addr": len(not_in_snap),
                         "mtime": mtime,
                         "note": "Bridge is read-only for this job; promotions only if a bridge contract already in snapshot newly meets a tier or changes state."}
except Exception as e:
    out["bridge_leg"] = {"error": f"{type(e).__name__}: {e}", "note": "bridge unreadable - run continues normally"}
log("bridge done")

# ---------- Leg 4: priority re-read (bounded RPC) ----------
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
EPS_PIN = ["https://bsc.publicnode.com/", "https://bsc-dataseed1.bnbchain.org/",
           "https://bsc-dataseed-public.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
_CACHE = {}
def _call_data(addr, sig, args=None):
    data = sel(sig)
    if args:
        for a in args:
            data += enc_addr(a) if isinstance(a, str) and a.startswith("0x") else enc_u(a)
    return data
def pinned_batch(calls, timeout=12):
    last = None
    for ep in EPS_PIN:
        try:
            return batch(calls, endpoint=ep, timeout=timeout), ep
        except Exception as e:
            last = e
            continue
    raise IOError(f"pinned batch failed on all endpoints: {last}")
def single(addr, sig, args=None):
    key = (addr, sig, tuple(args) if args else None)
    if key in _CACHE:
        return _CACHE[key]
    return None
ITEMS = {
 "Tri333": ("0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f", ["freeMinted()","FREE_CAP()","freeCount(address)","mintOpen()","balanceOf(address)"]),
 "WAR3": ("0x1Aa9797cC762b838388566Daa45A56b1709F4Bbe", ["freeMinted()","totalSupply()","balanceOf(address)"]),
 "HUNT PASS": ("0x885128Cf234c768F1353e2C1432D55873C6b67dD", ["totalMinted()","FREE_SUPPLY()","freeMinted()","balanceOf(address)","mintedBy(address)"]),
 "fab7-variant": ("0xfab7dd20e8816e10227C1222bd4Bd446FecF1B72", ["freeMinted()","FREE_SHARES()","totalMinted()","finalized()"]),
 "DinoAgent": ("0xcE19D6A5FF15e088D4bf23614242927139084895", ["freeMinted()","FREE_SUPPLY()","freeClaimed(address)"]),
 "LOCKSMITH": ("0x05e8738290be6639fD0f7236ebF444E5466D3164", ["totalMinted()","freeMintedTotal()","FREE_CAP()","mintActive()"]),
 "HOG ORBIT": ("0x7bc0b487febcbb1caa781148bf05a8cd72d02ec5", ["freeLeft()","totalSupply()","balanceOf(address)"]),
 "AgentBook": ("0xEECaCBE6eAC6D6F2a38e8daA9049C7AA08aD43b0", ["FREE_QUOTA()","remainingFree()"]),
 "Night Bandits Club": ("0xa849aEd9dC19FBA823CcEf1FA01BdA72Fbb8fcDf", ["freeUsed()","freeTakenBy(address)"]),
 "Ink Koi": ("0xbd4B4e7189ae9356514664146b0eD683601200A9", ["freeMinted()","freeClaimed(address)"]),
 "AURISLE": ("0xC52a979C20C5a43e5Be4Ffa6d1A4DD50069D5E2D", ["freeMinted()","FREE_SUPPLY()","freeClaimed(address)"]),
 "CipherAgent": ("0x158b5e25015758a94703A27c152889451E5d52E5", ["totalMints()","mintOpen()","balanceOf(address)"]),
 "MarsAgent": ("0x2231FdAe405c33dc4993f8C577c453802FF1AcE9", ["totalMints()","mintOpen()","balanceOf(address)"]),
 "OnlyAI": ("0x156482ad3f0eebd8e3f70d494ebd1da3f738f5ba", ["totalSupply()","balanceOf(address)"]),
 "Gloops": ("0x183CBb52B3C7BCB2433d50dE0Add99B59f4DE4fE", ["totalMinted()","mintOpen()"]),
 "Saturnagent": ("0xef870a9b4a529373fb2e174b59ca7a66eb018074", ["freeClaimed()","quote(address,uint256)"]),
 "Lumenhold": ("0x9701980b0afd825134390ee46fb3bd675a2f356f", ["freeClaimed()","quote(address,uint256)"]),
 "Ninetailix": ("0x809215729bcbff2ef31dea5efd6c12a6b788ba9a", ["totalSupply()","freeClaimed()","FREE_SUPPLY()","freeLeft(address)","freeUsed(address)","freeFor(address,uint256)","quote(address,uint256)","balanceOf(address)","mintOpen()"]),
 "REWARD": ("0xcfe5e4925a76a3aa11afa79e04c6fad3611cee40", ["freeMintedTotal()","FREE_CAP()","totalMinted()","mintActive()","freeMinted(address)","mintedCount(address)"]),
 "AgentSeat": ("0x3c1daedd9c9a4318e858229dd44608d3d5003d4b", ["totalSupply()","MAX_SUPPLY()","FREE_SUPPLY()","priceFor(address)","mintedBy(address)","balanceOf(address)"]),
 "Pumpkinfarm": ("0x77e38295603a06654a6ed3ed0849e6aa50749963", ["totalSupply()","FREE_SUPPLY()","freeClaimed()","mintOpen()","FREE_PER_WALLET()","freeLeft(address)","freeUsed(address)","freeFor(address,uint256)","quote(address,uint256)","balanceOf(address)"]),
 "Ghostling": ("0x6a4847cb5f658943222fbd23d2520049f824789d", ["freeClaimed()","FREE_SUPPLY()","freeLeft(address)","freeUsed(address)","mintedBy(address)","balanceOf(address)","freeFor(address,uint256)","quote(address,uint256)","mintOpen()"]),
 "KAGENT": ("0xb34105002B19EF0ce43B59011fE848df5c8B174f", ["phase()","launched()","sold()","freeClaimed()","balanceOf(address)"]),
 "Dafeiyu": ("0xD8DE64ACB25A87D98F1E170BF082a01427772511", ["totalSupply()","FREE_SUPPLY()","freeClaimed()","freeMinted()","mintOpen()","balanceOf(address)"]),
 "HokiKoi": ("0x74055b4Afe2d8c7347e8D4c0fc23e704405F7A36", ["freeMinted()","FREE_CAP()","mintOpen()","balanceOf(address)","freeCount(address)"]),
 "Jinli Agents": ("0x0f45b52f80a3a42e56e66Cd8CFd1A65895c34496", ["freeClaimed()","FREE_SUPPLY()","totalSupply()","mintOpen()","balanceOf(address)"]),
 "NUSA": ("0x7D08289E962f5aEc00d56D67322eb2FD056B687c", ["freeMinted()","MAX_FREE()","sharesMinted()","soldOut()","closed()","freeAvailable(address)","freeClaimed(address)","hasMinted(address)","quotaOf(address)"]),
 "Kiko9393": ("0x34aE861Fbeb2aaA6071248F8a27AcE5f30aA7bBf", ["freeMinted()","sharesMinted()","MAX_FREE()","freeAvailable(address)","freeClaimed(address)"]),
 "Ringgent": ("0xf1d1650dbfeb0fa8082481c8213accd59af3cf4a", ["freeClaimed()","totalSupply()","mintOpen()","freeLeft(address)","freeUsed(address)","balanceOf(address)"]),
 "Stampooor": ("0xCFB72b0E311796C478c6b74C1cd4592BbAa17aab", ["freeMinted()","FREE_SUPPLY()","totalMinted()","mintOpen()","freeAvailable(address)","freeUsed(address)","balanceOf(address)"]),
 "Skunk Hollow": ("0x88E4b613609af6C479F11D78e5a696d84B78993B", ["totalSkunksMinted()","freeSkunksClaimed()","freeSkunksRemaining()","freeWindowOpen()","balanceOf(address)","freeClaimedBy(address)"]),
 "Marbleworks": ("0xCc844748C64b9b8e45aC4504553C9757c7CDB7E0", ["freeMinted()","FREE_SUPPLY()","totalMinted()","totalSupply()","mintOpen()","freeAvailable(address)","freeUsed(address)","balanceOf(address)"]),
}
def prefetch_all():
    keys, calls = [], []
    for _name, (_addr, _views) in ITEMS.items():
        for sig in _views:
            if "(address)" in sig:
                _args = [USER]
            elif sig == "quote(address,uint256)":
                _args = [USER, 1]
            elif sig == "freeFor(address,uint256)":
                _args = [USER, 1]
            else:
                _args = None
            keys.append((_addr, sig, tuple(_args) if _args else None))
            calls.append(("eth_call", [{"to": _addr, "data": _call_data(_addr, sig, _args)}, "latest"]))
    chunk_stats = []
    for i in range(0, len(calls), 25):
        cc, ck = calls[i:i+25], keys[i:i+25]
        try:
            res, ep = pinned_batch(cc, timeout=12)
            for k, r in zip(ck, res):
                _CACHE[k] = to_int(r)
            chunk_stats.append({"chunk": i // 25, "endpoint": ep, "mode": "batch", "n": len(cc)})
            log(f"chunk {i//25} ok via {ep}")
        except Exception as e:
            n_ok = n_none = 0
            for j in range(0, len(cc), 5):
                sc, sk = cc[j:j+5], ck[j:j+5]
                try:
                    res, _ep2 = pinned_batch(sc, timeout=8)
                    for k, r in zip(sk, res):
                        _CACHE[k] = to_int(r)
                        n_ok += 1
                except Exception:
                    # BOUNDED: no per-call fallback - mark None (read failure, never a change)
                    for k in sk:
                        _CACHE[k] = None
                        n_none += 1
            chunk_stats.append({"chunk": i // 25, "mode": "subchunk-fallback-bounded",
                                "ok": n_ok, "none": n_none, "err": str(e)[:120]})
            log(f"chunk {i//25} fallback ok={n_ok} none={n_none}")
    out["leg4_chunks"] = chunk_stats
    return len(calls)
def read_item(item):
    name, (addr, views) = item
    d = {"address": addr}
    for sig in views:
        base = sig.split("(")[0]
        if "(address)" in sig:
            key = base + "_user"; v = _CACHE.get((addr, sig, (USER,)))
        elif sig == "quote(address,uint256)":
            key = "quote_user1"; v = _CACHE.get((addr, sig, (USER, 1)))
        elif sig == "freeFor(address,uint256)":
            key = "freeFor_user1"; v = _CACHE.get((addr, sig, (USER, 1)))
        else:
            key = base; v = _CACHE.get((addr, sig, None))
        d[key] = v
    return name, d
prefetch_n = prefetch_all()
out["leg4_prefetch_calls"] = prefetch_n
try:
    b, _ep = pinned_batch([("eth_blockNumber", [])], timeout=12)
    block = int(b[0], 16)
except Exception as e:
    block = None
    out["leg4_block_error"] = str(e)
reread = {"block": block, "items": {}}
t1 = time.time()
with ThreadPoolExecutor(max_workers=8) as ex:
    for name, d in ex.map(read_item, ITEMS.items()):
        reread["items"][name] = d
reread["duration_sec"] = round(time.time() - t1, 1)
json.dump(reread, open(f"{BASE}/hot-leg-{TS}-reread.json", "w"), indent=1)
out["leg4_priority"] = reread
log("leg4 reread done, block", block)
# --- ghostling age (verified AGE-EXCLUDED, first mint 2026-11-05 22:14:54 WIB) ---
ghost_age = {"address": "0x6a4847cb5f658943222fbd23d2520049f824789d",
             "verdict": "AGE-EXCLUDED >48h (verified first-mint time 2026-11-05 22:14:54 WIB, run 0639)"}
out["ghostling_age"] = ghost_age
out["age_48h_crossed"] = {"Ghostling": {"verdict": ghost_age["verdict"]},
                          "Ink Koi": {"verdict": "AGE-EXCLUDED >48h per main job run 1631 (age ~48,1 jam), removed from watchlist; user slot already used (INKOI #712 held, unaffected)"}}
try:
    gseen = seen.get("0x6a4847cb5f658943222fbd23d2520049f824789d", {})
    _prior = (gseen.get("note", "") or "")
    _g = reread["items"].get("Ghostling", {})
    seen["0x6a4847cb5f658943222fbd23d2520049f824789d"] = {
        "first_seen_wib": gseen.get("first_seen_wib", NOW),
        "note": (_prior + f" | Run 1734: freeClaimed {_g.get('freeClaimed')}/7000, "
                 f"slot open (freeLeft {_g.get('freeLeft_user')}, quote {_g.get('quote_user1')}). {ghost_age['verdict']}."),
        "source": "boltbook-en",
        "status": "checked-not-lead-age-excluded"}
    # Skunk Hollow re-read note (minted by user 17:25 WIB, #708; window closes 19:00:15 WIB)
    _sk = reread["items"].get("Skunk Hollow", {})
    sseen = seen.get("0x88E4b613609af6C479F11D78e5a696d84B78993B", {})
    _sprior = (sseen.get("note", "") or "")
    seen["0x88E4b613609af6C479F11D78e5a696d84B78993B"] = {
        "first_seen_wib": sseen.get("first_seen_wib", NOW),
        "note": (_sprior + f" | Run 1734 re-read block {block}: totalSkunksMinted {_sk.get('totalSkunksMinted')}, "
                 f"freeSkunksClaimed {_sk.get('freeSkunksClaimed')}/2500, freeRemaining {_sk.get('freeSkunksRemaining')}, "
                 f"windowOpen {_sk.get('freeWindowOpen')}, balanceOf(user) {_sk.get('balanceOf_user')}. Minted by user #708 17:25 WIB."),
        "source": sseen.get("source", "sourcify-feed"),
        "status": "minted-by-user-2026-11-09"}
    # Marbleworks re-read note (early lead run 1631, free 80/1111 at triage)
    _mw = reread["items"].get("Marbleworks", {})
    mseen = seen.get("0xCc844748C64b9b8e45aC4504553C9757c7CDB7E0", {})
    _mprior = (mseen.get("note", "") or "")
    seen["0xCc844748C64b9b8e45aC4504553C9757c7CDB7E0"] = {
        "first_seen_wib": mseen.get("first_seen_wib", NOW),
        "note": (_mprior + f" | Run 1734 re-read block {block}: freeMinted {_mw.get('freeMinted')}/1111, "
                 f"totalMinted {_mw.get('totalMinted')}, mintOpen {_mw.get('mintOpen')}, "
                 f"freeAvailable(user) {_mw.get('freeAvailable_user')}, balanceOf(user) {_mw.get('balanceOf_user')}. Early lead run 1631."),
        "source": mseen.get("source", "sourcify-feed"),
        "status": mseen.get("status", "checked-not-sale-shape")}
    json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
except Exception as e:
    out["seen_update_error"] = str(e)
# --- diff vs 1724 reread (change detection only) ---
changes = []
read_artifacts = []
promo_flags = []
try:
    prev_items = {}
    prev_blocks = {}
    for _pf in ("hot-leg-2026-11-09-1724-reread.json",):
        try:
            _pd = json.load(open(f"{BASE}/{_pf}"))
            prev_items.update(_pd.get("items", {}))
            prev_blocks[_pf] = _pd.get("block")
        except Exception as _e:
            out.setdefault("leg4_diff_prev_notes", []).append(f"{_pf}: {_e}")
    out["leg4_diff_prev"] = prev_blocks
    reported = json.load(open(f"{BASE}/hot-leg-reported.json"))
    rep_addrs = {k.lower().split("#")[0] for k in reported}
    for name, d in reread["items"].items():
        p = prev_items.get(name, {})
        for k, v in d.items():
            if k == "address":
                continue
            if k in p and p[k] != v:
                if p[k] is None or v is None:
                    read_artifacts.append({"item": name, "field": k, "old": p[k], "new": v})
                else:
                    changes.append({"item": name, "field": k, "old": p[k], "new": v})
        num = d.get("freeMinted") or d.get("freeClaimed") or d.get("freeMintedTotal")
        den = d.get("FREE_CAP") or d.get("FREE_SUPPLY") or d.get("FREE_SHARES")
        if isinstance(num, int) and isinstance(den, int) and den > 0:
            pct = num / den
            slot_open = ((d.get("freeLeft_user") or 0) > 0 or d.get("freeFor_user1") == 1
                         or d.get("quote_user1") == 0 or d.get("freeClaimed_user") == 0
                         or d.get("freeCount_user") == 0 or d.get("freeAvailable_user") == 1)
            minted_by_user = (d.get("balanceOf_user") or 0) > 0 or d.get("freeClaimed_user") == 1
            addr_low = d.get("address", "").lower()
            seen_entry = seen.get(d.get("address")) or seen.get(addr_low) or {}
            seen_status = seen_entry.get("status", "") if isinstance(seen_entry, dict) else ""
            snap_status = ""
            for _v in snap.get("contracts", {}).values():
                if isinstance(_v, dict) and str(_v.get("address", "")).lower() == addr_low:
                    snap_status = str(_v.get("status", "")); break
            age_excluded = seen_status == "checked-not-lead-age-excluded"
            already_reported_snap = any(t in snap_status for t in ("strong-lead", "early-lead-reported", "gate-blocked", "candidate", "sold-out"))
            ghostling_age_ok = True
            if name == "Ghostling":
                ghostling_age_ok = ghost_age.get("verdict", "").startswith("VERIFIED")
            discarded = False
            try:
                _disc = json.load(open(f"{BASE}/same-owner-discards.json"))
                discarded = any(isinstance(_e, dict) and _e.get("discarded_wib") and
                                str(_e.get("contract", "")).lower() == addr_low for _e in _disc)
            except Exception:
                discarded = False
            if pct >= 0.25 and slot_open and not minted_by_user and addr_low not in rep_addrs \
                    and not age_excluded and not already_reported_snap and ghostling_age_ok and not discarded:
                promo_flags.append({"item": name, "address": d.get("address"), "pct": round(pct, 4),
                                    "free": num, "cap": den})
            elif pct >= 0.25 and slot_open and not minted_by_user:
                promo_flags.append({"item": name, "address": d.get("address"), "pct": round(pct, 4),
                                    "free": num, "cap": den, "suppressed": True,
                                    "reason": ("same-owner-discarded" if discarded else
                                               "age-excluded" if age_excluded else
                                               "already-reported-in-snapshot" if already_reported_snap else
                                               "ghostling-age-unverified" if name == "Ghostling" else
                                               "already-in-hot-leg-reported")})
except Exception as e:
    out["leg4_diff_error"] = f"{type(e).__name__}: {e}"
out["leg4_changes"] = changes
out["leg4_read_artifacts"] = read_artifacts
out["leg4_promo_flags"] = promo_flags
out["leg4_bulk"] = "not attempted - priority items cover all promotion/sellout watches; bulk leg skipped to stay under 2-min target"
out["duration_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{BASE}/hot-leg-run-{TS}.json", "w"), indent=1)
log("DONE duration_s", out["duration_s"])
print(json.dumps(out, indent=1, default=str))
