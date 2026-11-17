#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-14 22:01 WIB.
Merges run-2026-11-14-2201-reread.json + velocity (vs hot-leg 2159) into
onchain-snapshot.json. Mapping rule (from run 2031 merge v2): address
candidates -> exact name -> name-prefix -> live non-checked entry.
Works directly on the live snapshot (no v1 misroute this run).
GUARD velocity ratio corrected here: prev rate read from PenjagaArusNFT
(2.239/mnt), not from the name-key lookup that missed. No preview/mint."""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
WIB = "2026-11-14 ~22:01 WIB"
_r = json.load(open(BASE + "run-2026-11-14-2201-reread.json"))
BLOCK = _r.get("block")
_vel0 = json.load(open(BASE + "run-2026-11-14-2201-velocity.json"))
INT_MIN = round(_vel0.get("interval_min") or 30.0, 2)

shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-20261114-2201")
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-14-2201-reread.json"))
vel = json.load(open(BASE + "run-2026-11-14-2201-velocity.json"))
web = json.load(open(BASE + "run-2026-11-14-2201-web.json"))

contracts = snap["contracts"]

def pick_key(name, addr):
    addr = (addr or "").lower()
    cands = [k for k, v in contracts.items()
             if (v.get("address") or "").lower() == addr] if addr else []
    if len(cands) == 1:
        return cands[0]
    if len(cands) > 1:
        if name in cands:
            return name
        for k in cands:
            if k.startswith(name) or name.startswith(k):
                return k
        live = [k for k in cands
                if not k.startswith("Feed-")
                and not str(contracts[k].get("status", "")).startswith("checked-")]
        if live:
            return live[0]
        return cands[0]
    if name in contracts:
        return name
    return None

vel_by_name = {r["name"]: r for r in vel["rows"]}
FREE_FIELDS = ["freeClaimed", "freeMinted", "freeRemaining", "FREE_SUPPLY", "FREE_MAX",
               "FREE_POOL", "freeLeft", "freeSupply", "totalMinted", "totalSupply"]
updated, skipped = [], []

for name, rd in reread["reads"].items():
    addr = rd.get("address")
    if name == "RigForge":
        continue  # track_c, handled below
    if name == "BinanceAI-mint":
        continue  # track B pending_claims, handled below
    key = pick_key(name, addr)
    if not key:
        skipped.append((name, addr))
        continue
    e = contracts[key]
    vrow = dict(vel_by_name.get(name, {}))
    views = rd.get("views") or {}
    # GUARD ratio correction: prev rate lives on PenjagaArusNFT (2.239/mnt)
    if name == "GUARD":
        prev_rate = contracts.get("PenjagaArusNFT", {}).get("currentRatePerMin")
        if vrow.get("rate") is not None and prev_rate:
            vrow["prev_rate"] = prev_rate
            vrow["ratio"] = round(vrow["rate"] / prev_rate, 2)
            vrow["vel_pass"] = bool(vrow["ratio"] >= 1.5 and (vrow.get("minted") or 0) >= 20)
    sk = vrow.get("supply_key")
    if sk and vrow.get("cur") is not None:
        e["previousTotalSupply"] = vrow.get("prev")
        e[sk] = vrow["cur"]
        e["mintedInInterval"] = vrow.get("minted")
        e["intervalMinutes"] = INT_MIN
        e["currentRatePerMin"] = vrow.get("rate")
        e["previousRatePerMin"] = vrow.get("prev_rate")
        e["velocityRatio"] = vrow.get("ratio")
        e["velocityLegPasses"] = False
    for f in FREE_FIELDS:
        if f in views and views[f] is not None and f != sk:
            e[f] = views[f]
    for f, val in views.items():
        if ("_user" in f or f == "balanceOf_user") and val is not None:
            e[f] = val
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = WIB
    none_views = vrow.get("views_none_2201") or []
    fp = vrow.get("free_pct")
    note = "Run 2201 (blok %d, interval %.2f mnt vs hot-leg 2159): " % (BLOCK, INT_MIN)
    if sk and vrow.get("cur") is not None:
        note += "%s %s->%s (+%s, %.3f/mnt, rasio %s) -> velocity GAGAL; " % (
            sk, vrow.get("prev"), vrow.get("cur"), vrow.get("minted"),
            vrow.get("rate") or 0.0,
            ("%.2fx" % vrow["ratio"]) if vrow.get("ratio") is not None else "None")
    elif sk:
        note += "%s gagal baca (None) - degradasi RPC, nilai lama dipertahankan; " % sk
    else:
        note += "tidak ada supply view; "
    if fp is not None:
        note += "free %s%% (%s); " % (fp, vrow.get("free_basis"))
    if none_views:
        note += "view gagal (None, persisten): %s; " % ", ".join(none_views)
    note += "DIAM."
    e["runNote2201_1114"] = note
    updated.append((name, key))

# Track B — binanceai.fun (values read FRESH from reread; change flagged)
_bna = (reread["reads"].get("BinanceAI-mint", {}) or {}).get("views") or {}
pc = snap["pending_claims"]["binanceai.fun"]
_bna_old = {k: pc.get(k) for k in ("launched", "failed", "isRefundPhase", "tokenClaimed_user")}
_bna_now = {"launched": _bna.get("launched"), "failed": _bna.get("failed"),
            "isRefundPhase": _bna.get("isRefundPhase"),
            "tokenClaimed_user": _bna.get("tokenClaimed_user")}
_bna_changed = [k for k in _bna_now if _bna_now[k] is not None and _bna_old.get(k) is not None and _bna_now[k] != _bna_old[k]]
for k, v in _bna_now.items():
    if v is not None:
        pc[k] = v
pc["runNote2201"] = ("Run 2201: launched=%s, failed=%s, isRefundPhase=%s, totalShares=%s, "
                     "tokenClaimed(user)=%s (blok %d)%s" % (
                         _bna.get("launched"), _bna.get("failed"), _bna.get("isRefundPhase"),
                         _bna.get("totalShares"), _bna.get("tokenClaimed_user"), BLOCK,
                         " - PERUBAHAN: %s - BUTUH TINDAK LANJUT!" % ", ".join(_bna_changed) if _bna_changed
                         else " - tetap pending/refund, sudah dilaporkan sekali, DIAM"))
pc["lastReadWib"] = WIB
print("BINANCEAI change:", _bna_changed or "none", _bna_now)

# Track C — RigForge / ORBIT (values read FRESH from reread; change flagged)
tc = snap["track_c"]
_rf = (reread["reads"].get("RigForge", {}) or {}).get("views") or {}
if "RigForge" in tc:
    _rf_old = {"freeSharesLeft": tc["RigForge"].get("freeSharesLeft"), "openedAt": tc["RigForge"].get("openedAt"),
               "freeClaimed": tc["RigForge"].get("freeClaimed")}
    _rf_now = {"freeSharesLeft": _rf.get("freeSharesLeft"), "openedAt": _rf.get("openedAt"),
               "freeClaimed": _rf.get("freeClaimed")}
    _rf_chg = [k for k in _rf_now if _rf_now[k] is not None and _rf_old.get(k) is not None and _rf_now[k] != _rf_old[k]]
    for k, v in _rf_now.items():
        if v is not None:
            tc["RigForge"][k] = v
    tc["RigForge"]["runNote2201_1114"] = ("Run 2201 (blok %d): freeSharesLeft %s, openedAt %s, freeClaimed %s, "
        "freeBooked(user) %s%s" % (BLOCK, _rf.get("freeSharesLeft"), _rf.get("openedAt"), _rf.get("freeClaimed"),
        _rf.get("freeBooked_user"), " - PERUBAHAN: %s" % ", ".join(_rf_chg) if _rf_chg else " - tidak berubah, DIAM"))
    tc["RigForge"]["lastReadBlock"] = BLOCK
    print("RIGFORGE change:", _rf_chg or "none", _rf_now)
_ob = (reread["reads"].get("ORBIT", {}) or {}).get("views") or {}
if "ORBIT" in tc:
    _ob_old = {"freeClaimed": tc["ORBIT"].get("freeClaimed"), "claimOpen": tc["ORBIT"].get("claimOpen"),
               "hasFreeClaimed_user": tc["ORBIT"].get("hasFreeClaimed_user")}
    _ob_now = {"freeClaimed": _ob.get("freeClaimed"), "claimOpen": _ob.get("claimOpen"),
               "hasFreeClaimed_user": _ob.get("hasFreeClaimed_user")}
    _ob_chg = [k for k in _ob_now if _ob_now[k] is not None and _ob_old.get(k) is not None and _ob_now[k] != _ob_old[k]]
    for k, v in _ob_now.items():
        if v is not None:
            tc["ORBIT"][k] = v
    tc["ORBIT"]["runNote2201_1114"] = ("Run 2201 (blok %d): freeClaimed %s/%s = %s%%, claimOpen %s, "
        "hasFreeClaimed(user)=%s%s" % (BLOCK, _ob.get("freeClaimed"), _ob.get("FREE_MAX"),
        round(100 * _ob["freeClaimed"] / _ob["FREE_MAX"], 1) if _ob.get("freeClaimed") is not None and _ob.get("FREE_MAX") else "?",
        _ob.get("claimOpen"), _ob.get("hasFreeClaimed_user"),
        " - PERUBAHAN: %s" % ", ".join(_ob_chg) if _ob_chg else " - tidak berubah, DIAM"))
    tc["ORBIT"]["lastReadBlock"] = BLOCK
    print("ORBIT change:", _ob_chg or "none", _ob_now)

# Feed shape-check: 8 new Sourcify contracts, all S1=False S2=False
def feed_note(s):
    if s.get("error"):
        return "shape-check error: " + str(s["error"])[:120]
    return ("S1=%s S2=%s mint=%s quote=%s free=%s agent=%s token=%s n_fns=%s" % (
        s.get("S1"), s.get("S2"), s.get("has_mint"), s.get("has_quote"),
        s.get("free_views"), s.get("agent_ref"), s.get("is_token"), s.get("n_fns")))
feed_notes = {s["address"]: feed_note(s) for s in web.get("shape_check", [])}
for s in web.get("shape_check", []):
    a = s["address"]
    short = "Feed-" + a[2:8].lower()
    if short in contracts or a.lower() in [ (v.get("address") or "").lower() for v in contracts.values() ]:
        continue
    contracts[short] = {
        "address": a,
        "status": "checked-not-sale-shape-2026-11-14",
        "lastReadWib": WIB,
        "lastReadBlock": BLOCK,
        "baselineNote": ("Feed Sourcify run 2201 (verifiedAt %s): %s; "
            "bukan sale-shape, bukan agent-shaped (first mints tidak diverifikasi - bukan early lead). "
            "Tidak dilaporkan, tidak masuk watchlist aktif." % (s.get("verifiedAt"), feed_notes.get(a, "checked"))),
        "runNote2201_1114": "Run 2201: feed %s %s -> bukan sale-shape." % (a, feed_notes.get(a, "")),
    }

# Sweep finds run 2201 (from run-2026-11-14-2201-sweep-decisions.json)
try:
    _sd = json.load(open(BASE + "run-2026-11-14-2201-sweep-decisions.json"))
    for _k, _v in (_sd.get("excluded") or {}).items():
        snap.setdefault("excluded", {})[_k] = _v
    for _k, _v in (_sd.get("watchlist_add") or {}).items():
        if _k not in contracts:
            contracts[_k] = _v
    print("sweep decisions applied:", list((_sd.get("excluded") or {}).keys()),
          "+", list((_sd.get("watchlist_add") or {}).keys()))
except Exception as _e:
    print("sweep decisions NOT applied:", type(_e).__name__, str(_e)[:150])

# Top-level run notes (from run-2026-11-14-2201-summary.json, written after legs finish)
try:
    _summ = json.load(open(BASE + "run-2026-11-14-2201-summary.json"))
except Exception:
    _summ = {}
for _k in ("runNote2201_1114", "runNote2201_1114_scan", "runNote2201_1114_feedshape",
           "runNote2201_1114_boltbook", "runNote2201_1114_sweep", "runNote2201_1114_binanceai",
           "runNote2201_1114_bridge", "runNote2201_1114_parus", "runNote2201_1114_pixelfrogs",
           "runNote2201_1114_rave"):
    if _k in _summ:
        snap[_k] = _summ[_k]
snap["last_run_wib"] = WIB
snap["last_run_block"] = BLOCK
snap["last_run_note"] = snap["runNote2201_1114"]

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1, ensure_ascii=False)
print("updated:", len(updated))
print("skipped:", skipped)
print("mapping sample:", [u for u in updated if u[0] in ("GUARD", "AbsurdAgentNFT", "PX24", "B77D", "HIVE", "CPASS", "NOISE")])
print("contracts now:", len(snap["contracts"]))
print("OK merged 2201, block", BLOCK)
