#!/usr/bin/env python3
"""Hot-leg run 2026-11-09 16:04 WIB. Legs 1-4 + bridge. Read-only except own hot-leg state files. Never writes main snapshot."""
import json, re, subprocess, urllib.request, time, os, sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-09-1604"
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed", "freeAvailable",
              "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted", "freeCardsRemaining"]
out = {"run": "free-mint-hot-leg 2026-11-09 16:04:38 WIB"}
t0 = time.time()

def shape_check(addr):
    try:
        p = subprocess.run(["curl", "-sS", "--max-time", "20", "-A", "hot-leg/1.0",
                            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                           capture_output=True, text=True, timeout=25)
        if p.returncode != 0:
            return {"address": addr, "error": f"curl rc={p.returncode}: {p.stderr.strip()[:100]}"}
        meta = json.loads(p.stdout)
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate", "AGENT_ID", "agentIdRegistry", "isAgent"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "abi_functions": sorted(names), "S1": s1, "S2": s2,
                "mint": has_mint, "quote": has_quote, "free": free_views, "agent": agent_ref, "token": is_token}
    except Exception as e:
        return {"address": addr, "error": f"{type(e).__name__}: {str(e)[:100]}"}

# ---------- Leg 1: Sourcify feed ----------
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
feed_addrs = []
try:
    cp = subprocess.run(["curl", "-sS", "--max-time", "25", "-A", "hot-leg/1.0",
                         "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"],
                        capture_output=True, text=True, timeout=30)
    data = json.loads(cp.stdout)
    items = data.get("results", data) if isinstance(data, dict) else data
    for it in items:
        a = it.get("address") or it.get("contractAddress")
        if a:
            feed_addrs.append(a)
    out["leg1_feed"] = {"n": len(feed_addrs), "addrs": feed_addrs}
    json.dump(data, open(f"{BASE}/hot-leg-{TS}-sourcify.json", "w"), indent=1)
except Exception as e:
    out["leg1_feed"] = {"error": f"{type(e).__name__}: {e}"}
    feed_addrs = []

new_addrs = [a for a in feed_addrs if a not in seen and a.lower() not in EXCLUDED and a.lower() != REG.lower()]
new_excluded = [a for a in feed_addrs if a.lower() in EXCLUDED]
shapes = []
if new_addrs:
    with ThreadPoolExecutor(max_workers=10) as ex:
        shapes = list(ex.map(shape_check, new_addrs))
    for s in shapes:
        if s.get("error"):
            seen[s["address"]] = {"first_seen_wib": NOW,
                "note": f"shape-check failed on transport ({s.get('error')}) - NOT verified as not-sale-shape; retry next run",
                "source": "sourcify-feed", "status": "shape-check-failed-transport"}
            continue
        seen[s["address"]] = {"first_seen_wib": NOW,
            "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} free={s.get('free')} agent={s.get('agent')} token={s.get('token')}",
            "source": "sourcify-feed", "status": "checked-not-sale-shape" if not (s.get("S1") or s.get("S2")) else "sale-shape"}
    json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
    json.dump(shapes, open(f"{BASE}/hot-leg-{TS}-sourcify-shape.json", "w"), indent=1)
out["leg1"] = {"new": new_addrs, "new_excluded_rediscovered": new_excluded,
               "shapes": [{k: v for k, v in s.items() if k != "abi_functions"} for s in shapes],
               "seen_total": len(seen)}
sale_shapes = [s for s in shapes if s.get("S1") or s.get("S2")]

# ---------- Leg 2: Boltbook EN + ZH ----------
def fetch_boltbook(url):
    try:
        p = subprocess.run(["curl", "-sS", "-L", "--max-time", "15", "-A", "hot-leg/1.0", url],
                           capture_output=True, text=True, timeout=20)
        return p.stdout or "", p.returncode
    except Exception as e:
        return "", f"ERR {e}"

en, en_rc = fetch_boltbook("https://boltbook.fun/?lang=en")
zh, zh_rc = fetch_boltbook("https://boltbook.fun/?lang=zh")
open(f"{BASE}/hot-leg-{TS}-boltbook-en.html", "w").write(en)
open(f"{BASE}/hot-leg-{TS}-boltbook-zh.html", "w").write(zh)
addr_re = re.compile(r"0x[a-fA-F0-9]{40}")
en_addrs = sorted(set(addr_re.findall(en)))
zh_addrs = sorted(set(addr_re.findall(zh)))
all_addrs = sorted(set(en_addrs) | set(zh_addrs))
kw_en = ["free share", "first share free", "1 free share", "free mint share"]
kw_zh = ["免费份额", "首个免费", "免费铸造", "免费mint"]
text_low = (en + zh).lower()
kw_hits = {k: text_low.count(k.lower()) for k in kw_en + kw_zh}
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
snap_addr_set = {v.get("address", "").lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
for v in snap.get("track_c", {}).values():
    if isinstance(v, dict):
        for k in ("sale", "token", "address"):
            if v.get(k):
                snap_addr_set.add(str(v[k]).lower())
new_bolt = [a for a in all_addrs if a not in seen]
new_bolt_not_snap = [a for a in all_addrs if a.lower() not in snap_addr_set and a not in seen]
bolt_shapes = {}
for a in new_bolt_not_snap:
    s = shape_check(a)
    if s.get("error"):
        note = f"shape-check failed on transport ({s['error']}) - NOT verified as not-sale-shape; retry next run"
        status = "shape-check-failed-transport"
    else:
        note = (f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} "
                f"free={s.get('free')} agent={s.get('agent')} token={s.get('token')}")
        status = "sale-shape" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape"
    bolt_shapes[a] = {"note": note, "shape": {k: v for k, v in s.items() if k != "abi_functions"}}
    seen[a] = {"first_seen_wib": NOW, "note": note, "source": "boltbook-en" if a in en_addrs else "boltbook-zh",
               "status": status}
in_snap_bolt = [a for a in new_bolt if a.lower() in snap_addr_set]
for a in in_snap_bolt:
    bolt_shapes[a] = {"note": "already in snapshot"}
if new_bolt:
    json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
out["leg2_boltbook"] = {"en_bytes": len(en), "en_rc": en_rc, "zh_bytes": len(zh), "zh_rc": zh_rc,
                        "en_addrs": len(en_addrs), "zh_addrs": len(zh_addrs), "unique_addrs": len(all_addrs),
                        "keyword_hits": kw_hits, "new_vs_seen": new_bolt, "new_vs_snapshot": new_bolt_not_snap,
                        "shape_check": bolt_shapes, "seen_total": len(seen)}
bolt_sale_shapes = [a for a, v in bolt_shapes.items()
                    if isinstance(v, dict) and isinstance(v.get("shape"), dict)
                    and (v["shape"].get("S1") or v["shape"].get("S2"))]

# ---------- Leg 3 (runs after RPC helpers below; placeholder here) ----------
out["leg3_new_sale_shapes"] = [s["address"] for s in sale_shapes] + bolt_sale_shapes
out["leg3_verify"] = "pending - runs after RPC helpers"

# ---------- Pending claims ----------
out["pending_claims"] = snap.get("pending_claims") or "snapshot pending_claims empty at run start - nothing to re-read"

# ---------- Bridge leg (read-only) ----------
try:
    bridge = json.load(open(f"{BASE}/scan-bridge.json"))
    bcontracts = bridge.get("contracts", {})
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

# ---------- Leg 4: priority re-read (single-call reads only) ----------
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def single(addr, sig, args=None):
    data = sel(sig)
    if args:
        for a in args:
            data += enc_addr(a) if isinstance(a, str) and a.startswith("0x") else enc_u(a)
    for ep in EPS:
        try:
            res = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=8)
            return to_int(res[0])
        except Exception:
            continue
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

}
def read_item(item):
    name, (addr, views) = item
    d = {"address": addr}
    for sig in views:
        base = sig.split("(")[0]
        if "(address)" in sig:
            key = base + "_user"; v = single(addr, sig, [USER])
        elif sig == "quote(address,uint256)":
            key = "quote_user1"; v = single(addr, sig, [USER, 1])
        elif sig == "freeFor(address,uint256)":
            key = "freeFor_user1"; v = single(addr, sig, [USER, 1])
        else:
            key = base; v = single(addr, sig)
        d[key] = v
    return name, d
try:
    b = batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=8)
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
# --- Leg 3 verify (new sale-shapes only): fast pool + slot read; age from snapshot first-mint if present ---
def verify_sale_shape(addr, shape):
    fn_names = set(shape.get("abi_functions", []))
    v = {"address": addr, "S1": shape.get("S1"), "S2": shape.get("S2")}
    for sig in ["freeClaimed()", "freeMinted()", "totalSupply()", "mintOpen()",
                "FREE_SUPPLY()", "FREE_SLOTS()", "FREE_CAP()", "freeSharesRemaining()"]:
        base = sig.split("(")[0]
        if base in fn_names:
            v[base] = single(addr, sig)
    for sig in ["freeLeft(address)", "freeUsed(address)", "freeClaimed(address)",
                "freeAvailable(address)", "balanceOf(address)", "mintedBy(address)"]:
        base = sig.split("(")[0]
        if base in fn_names:
            v[base + "_user"] = single(addr, sig, [USER])
    if "quote" in fn_names:
        v["quote_user1"] = single(addr, "quote(address,uint256)", [USER, 1])
    if "freeFor" in fn_names:
        v["freeFor_user1"] = single(addr, "freeFor(address,uint256)", [USER, 1])
    # age: snapshot first-mint / launch note if the main job already verified it
    age_note = None
    for sec in ("contracts", "track_c"):
        for k, sv in snap.get(sec, {}).items():
            if isinstance(sv, dict) and str(sv.get("address", "")).lower() == addr.lower():
                age_note = sv.get("firstMintWib") or sv.get("launchNote") or sv.get("status")
                break
        if age_note:
            break
    v["age_from_snapshot"] = age_note
    return v
_leg3 = []
for _s in sale_shapes:
    _v = verify_sale_shape(_s["address"], _s)
    _leg3.append(_v)
for _a in bolt_sale_shapes:
    _sh = bolt_shapes.get(_a, {}).get("shape", {})
    if _sh and "abi_functions" not in _sh:
        # FIX 2026-11-09 15:39: bolt shapes strip abi_functions, so verify_sale_shape
        # read nothing for Boltbook-found sale-shapes (Gryphlume this run needed a
        # manual follow-up). Re-fetch the full shape so leg3 actually probes.
        _sh = shape_check(_a)
    if _sh:
        _leg3.append(verify_sale_shape(_a, _sh))
if _leg3:
    for _v in _leg3:
        _a = _v["address"]
        _age = _v.get("age_from_snapshot")
        _note = (f"Leg3 verify block {reread.get('block')}: {json.dumps(_v)}; "
                 f"age {'from snapshot: ' + str(_age) if _age else 'UNVERIFIED - no first-mint in snapshot, watchlist-only, never lead'}; "
                 f"never previewed/minted this run.")
        _cur = seen.get(_a, {})
        if isinstance(_cur, dict):
            seen[_a] = {"first_seen_wib": _cur.get("first_seen_wib", NOW),
                        "note": ((_cur.get("note", "") or "") + " | " + _note),
                        "source": _cur.get("source", "sourcify-feed"),
                        "status": _cur.get("status", "sale-shape")}
    json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
    out["leg3_verify"] = _leg3
else:
    out["leg3_verify"] = "None - no new sale-shape contract this run"
# first mint block 131838993 = 2026-11-05 22:14:54 WIB -> AGE-EXCLUDED >48h. No re-test.
# This run only appends fresh numbers to the seen note.
ghost_age = {"address": "0x6a4847cb5f658943222fbd23d2520049f824789d",
             "verdict": "AGE-EXCLUDED >48h (verified first-mint time 2026-11-05 22:14:54 WIB, run 0639)"}
out["ghostling_age"] = ghost_age
out["age_48h_crossed"] = {"Ghostling": {"verdict": ghost_age["verdict"]},
                          "Voltoad": {"verdict": "not tracked this run"}}
try:
    gseen = seen.get("0x6a4847cb5f658943222fbd23d2520049f824789d", {})
    _prior = (gseen.get("note", "") or "")
    _g = reread["items"].get("Ghostling", {})
    seen["0x6a4847cb5f658943222fbd23d2520049f824789d"] = {
        "first_seen_wib": gseen.get("first_seen_wib", NOW),
        "note": (_prior + f" | Run 1604: freeClaimed {_g.get('freeClaimed')}/7000, "
                 f"slot open (freeLeft {_g.get('freeLeft_user')}, quote {_g.get('quote_user1')}). {ghost_age['verdict']}."),
        "source": "boltbook-en",
        "status": "checked-not-lead-age-excluded"}
    json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
except Exception as e:
    out["ghostling_age_seen_update_error"] = str(e)
# --- diff vs 08:14 reread (change detection only) ---
changes = []
read_artifacts = []
promo_flags = []
try:
    prev_items = {}
    prev_blocks = {}
    for _pf, _key in (("hot-leg-2026-11-09-1559-reread.json", "items"),):
        try:
            _pd = json.load(open(f"{BASE}/{_pf}"))
            prev_items.update(_pd.get(_key, {}))
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
                # null transitions are read failures (AGENTS.md: all-null = failed read),
                # NOT state changes - record separately, never as a change
                if p[k] is None or v is None:
                    read_artifacts.append({"item": name, "field": k, "old": p[k], "new": v})
                else:
                    changes.append({"item": name, "field": k, "old": p[k], "new": v})
        # promotion flag: free pct >=25% + slot open + not already reported + not minted by user
        # + NOT age-excluded in hot-leg seen + NOT already strong/early-reported in main snapshot
        # + Ghostling only if its age test just verified <=48h
        num = d.get("freeMinted") or d.get("freeClaimed") or d.get("freeMintedTotal")
        den = d.get("FREE_CAP") or d.get("FREE_SUPPLY") or d.get("FREE_SHARES")
        if isinstance(num, int) and isinstance(den, int) and den > 0:
            pct = num / den
            slot_open = ((d.get("freeLeft_user") or 0) > 0 or d.get("freeFor_user1") == 1
                         or d.get("quote_user1") == 0 or d.get("freeClaimed_user") == 0
                         or d.get("freeCount_user") == 0)
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
print(json.dumps(out, indent=1, default=str))
