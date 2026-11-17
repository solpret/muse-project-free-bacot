#!/usr/bin/env python3
"""Merge STAGE 1 run 2026-11-09 1401 WIB — re-read velocity, snapshot updates,
track_c updates, structured-launch-time age exclusions. Discovery incorporation
is STAGE 2 (subagent A still running at stage-1 time); stage 2 updates the run
notes and adds any discovery findings. No scan output this run (pre-flight 401).
Read-only w.r.t. chain; never mints/previews.
Writes: onchain-snapshot.json (atomic), run-2026-11-09-1401-merge-stage1.json.
"""
import json, os, shutil
from datetime import datetime, timezone, timedelta

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
NOW = datetime(2026, 11, 9, 14, 35, tzinfo=timezone(timedelta(hours=7)))

snap = json.load(open(f"{HF}/onchain-snapshot.json"))
r1301 = json.load(open(f"{HF}/run-2026-11-09-1301-reread.json"))
r1401 = json.load(open(f"{HF}/run-2026-11-09-1401-reread.json"))

BLOCK_1401 = r1401["block"]
BLOCK_1301 = r1301["block"]
INTERVAL_MIN = (BLOCK_1401 - BLOCK_1301) * 0.45 / 60.0
print(f"interval_minutes (block-based): {INTERVAL_MIN:.2f} blocks {BLOCK_1301}->{BLOCK_1401}")

shutil.copy(f"{HF}/onchain-snapshot.json", f"{HF}/onchain-snapshot.json.bak-2026-11-09-1401")

report = {"run": "2026-11-09-1401", "stage": 1, "interval_minutes": round(INTERVAL_MIN, 2),
          "velocity_pass": [], "sellouts_new": [], "slot_changes": [],
          "age_exclusions": [], "age_candidates_kept": [], "early_leads_new": [],
          "discarded_same_owner": [], "track_c_added": [], "track_c_excluded": []}

contracts = snap.get("contracts", {})

# ---- 1. re-read velocity + snapshot value updates ----
n_upd = 0
for name, d in r1401.get("reread", {}).items():
    old = contracts.get(name)
    if not isinstance(old, dict) or not isinstance(d, dict):
        continue
    base1301 = r1301.get("reread", {}).get(name, {}).get("totalSupply") if isinstance(r1301.get("reread", {}).get(name), dict) else None
    base_snap = old.get("totalSupply")
    new_ts = d.get("totalSupply")
    prev_rate = old.get("currentRatePerMin")
    vel = {"name": name, "baseline": None, "minted": None, "rate": None, "ratio": None, "passes": False, "note": ""}
    kind = str(old.get("kind") or "")
    st = str(old.get("status") or "")
    is_token = ("ERC20" in kind.upper() or "bridge" in kind.lower() or
                "bridge" in st.lower() or "pelengkap-scan" in st.lower() or
                "scan-complement" in st.lower())
    if new_ts is not None and base1301 is not None and not is_token:
        minted = new_ts - base1301
        rate = minted / INTERVAL_MIN
        ratio = (rate / prev_rate) if (prev_rate not in (None, 0)) else None
        vel.update({"baseline": base1301, "minted": minted, "rate": round(rate, 4),
                    "ratio": round(ratio, 2) if ratio is not None else None,
                    "passes": bool(minted >= 20 and ratio is not None and ratio >= 1.5),
                    "note": "baseline=1301 reread"})
        if vel["passes"]:
            report["velocity_pass"].append(vel)
        old["previousTotalSupply"] = base1301
        old["previousRatePerMin"] = prev_rate
        old["currentRatePerMin"] = round(rate, 4)
        old["velocityRatio"] = vel["ratio"]
    elif new_ts is not None and base_snap is not None and new_ts != base_snap:
        vel.update({"note": "baseline 1301 missing (batch fail) — velocity NOT computed over stale snapshot interval"})
        old["previousTotalSupply"] = base_snap
    for k in ["totalSupply", "freeClaimed", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"]:
        if d.get(k) is not None:
            old[k] = d[k]
    if d.get("totalMinted") is not None:
        old["totalMinted"] = d["totalMinted"]
    if d.get("freeMinted") is not None:
        old["freeMinted"] = d["freeMinted"]
    if d.get("balanceOf_user") is not None:
        old["balanceOf_user"] = d["balanceOf_user"]
        old["userBalance"] = d["balanceOf_user"]
    if d.get("freeClaimed_user") is not None:
        old["freeClaimed_user"] = d["freeClaimed_user"]
    fc, fs = old.get("freeClaimed"), old.get("FREE_SUPPLY")
    if isinstance(fc, (int, float)) and isinstance(fs, (int, float)) and fs:
        old["freePctVerified"] = round(100.0 * fc / fs, 2)
    elif isinstance(old.get("freeMinted"), (int, float)) and isinstance(fs, (int, float)) and fs:
        old["freePctVerified"] = round(100.0 * old["freeMinted"] / fs, 2)
    old["lastReadBlock"] = BLOCK_1401
    old["lastReadWib"] = "2026-11-09 14:3x WIB"
    if vel["minted"] is not None:
        old["mintedInInterval"] = vel["minted"]
        old["intervalMinutes"] = round(INTERVAL_MIN, 2)
        old["velocityLegPasses"] = vel["passes"]
        old["runNote1401_1109"] = (f"Run 1401 (blok {BLOCK_1401}, interval {INTERVAL_MIN:.1f} mnt vs run 1301): "
            f"{vel['baseline']}->{new_ts} (+{vel['minted']}, {vel['rate']:.3f}/mnt vs prev {prev_rate} = "
            f"{vel['ratio']}x) -> velocity {'LOLOS' if vel['passes'] else 'GAGAL'}; "
            f"free={old.get('freeClaimed')}/{old.get('FREE_SUPPLY')}; bal_user={d.get('balanceOf_user')}; "
            f"status {old.get('status')}.")
        n_upd += 1
    else:
        old["runNote1401_1109"] = (f"Run 1401 (blok {BLOCK_1401}): totalSupply {new_ts} "
            f"(baseline 1301 gagal baca / snapshot stale — velocity TIDAK dihitung); "
            f"free={old.get('freeClaimed')}/{old.get('FREE_SUPPLY')}; bal_user={d.get('balanceOf_user')}; "
            f"status {old.get('status')}.")
print(f"contracts updated: {n_upd} velocity-pass: {[v['name'] for v in report['velocity_pass']]}")

# ---- 2. track_c re-read updates ----
tc = snap.get("track_c", {})
n_tc = 0
for name, d in r1401.get("track_c", {}).items():
    old = tc.get(name)
    if not isinstance(old, dict) or not isinstance(d, dict):
        continue
    prev_free = old.get("freeSharesRemaining")
    for k in ["freeSharesRemaining", "freeMinted", "totalSupply"]:
        if d.get(k) is not None:
            old[k] = d[k]
    if d.get("balanceOf_user") is not None:
        old["balanceOf_user"] = d["balanceOf_user"]
    if d.get("freeClaimed_user") is not None:
        old["freeClaimed_user"] = d["freeClaimed_user"]
    old["lastReadBlock"] = BLOCK_1401
    n_tc += 1
    if prev_free not in (None, 0) and old.get("freeSharesRemaining") == 0:
        report["sellouts_new"].append({"name": name, "prev_free": prev_free})
print(f"track_c updated: {n_tc} sellouts_new: {report['sellouts_new']}")

# ---- 3. generic structured-launch-time age exclusions (same logic as run 1301) ----
def parse_wib(s):
    if not s:
        return None
    s = str(s).strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S+07:00", "%Y-%m-%d %H:%M:%S WIB", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(s, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone(timedelta(hours=7)))
            return dt
        except Exception:
            continue
    return None

ACTIVE_OK = ("early-lead", "strong-lead", "watchlist-only")
for name, v in list(contracts.items()):
    st = str(v.get("status", ""))
    if not any(x in st for x in ACTIVE_OK):
        continue
    if any(x in st for x in ["minted-by-user", "excluded", "discarded", "paid-only", "sold-out", "soldout"]):
        continue
    t = None
    for f in ["startTimeWib", "firstMintWib", "launchTimeWib", "saleStartWib"]:
        t = parse_wib(v.get(f))
        if t:
            break
    if not t:
        continue
    age_h = (NOW - t).total_seconds() / 3600.0
    if age_h <= 48:
        continue
    r1401d = r1401.get("reread", {}).get(name, {})
    ts = r1401d.get("totalSupply") if isinstance(r1401d, dict) and r1401d.get("totalSupply") is not None else v.get("totalSupply")
    tm = r1401d.get("totalMinted") if isinstance(r1401d, dict) and r1401d.get("totalMinted") is not None else v.get("totalMinted")
    mx = v.get("MAX_SUPPLY")
    sold_out = bool(mx and ((isinstance(ts, (int, float)) and ts >= mx) or
                            (isinstance(tm, (int, float)) and tm >= mx)))
    if sold_out:
        report["age_candidates_kept"].append({"name": name, "age_h": round(age_h, 1), "reason": "sold out — age rule N/A"})
        continue
    mint_open = r1401d.get("mintOpen") if isinstance(r1401d, dict) and r1401d.get("mintOpen") is not None else v.get("mintOpen")
    reason = "age-over-48h-not-sold-out"
    if mint_open == 0:
        reason = "mint-closed (mintOpen=0), age-over-48h"
    report["age_exclusions"].append({"name": name, "address": v.get("address"), "age_h": round(age_h, 1),
                                      "launch_time": t.isoformat(), "totalSupply": ts, "totalMinted": tm,
                                      "reason": reason, "status_was": st})
    del contracts[name]
print(f"age exclusions: {report['age_exclusions']}")
print(f"age kept (sold out): {report['age_candidates_kept']}")

# ---- 4. velocity-pass promotion screening (no promotion without all legs) ----
vel_notes = []
for vp in report["velocity_pass"]:
    old = contracts.get(vp["name"], {})
    fc, fs = old.get("freeClaimed"), old.get("FREE_SUPPLY")
    pct = round(100.0 * fc / fs, 2) if isinstance(fc, (int, float)) and isinstance(fs, (int, float)) and fs else None
    if vp["name"] == "Bubblebruin":
        note = "SUDAH DIMILIKI user (minted-by-user 2026-11-01) — velocity moot, tidak ada promosi."
    elif pct is not None and pct >= 25:
        note = "PROMOTION CHECK NEEDED"
    else:
        note = "no promotion (free% <25% or unverified / age/website unverified — bukan strong lead/kandidat)"
    vel_notes.append(f"{vp['name']}: +{vp['minted']} ({vp['ratio']}x) free%={pct} status={old.get('status')} "
                     f"x={old.get('xVerified')} — {note}")
report["velocity_notes"] = vel_notes

# ---- 5. stage-1 run notes (discovery pending) ----
snap["runNote1401_1109"] = (
    f"Run 1401 STAGE 1: re-read {len(r1401.get('reread', {}))} kontrak + {len(r1401.get('track_c', {}))} track_c "
    f"(blok {BLOCK_1401}, interval {INTERVAL_MIN:.1f} mnt vs run 1301); "
    f"velocity LOLOS {len(report['velocity_pass'])}: {', '.join(v['name'] for v in report['velocity_pass']) or 'tidak ada'} — "
    f"promosi 0: {'; '.join(vel_notes) if vel_notes else 'tidak ada yang lolos'}. "
    f"Age-exclusions stage 1: {len(report['age_exclusions'])}. "
    f"Scan GAGAL CEPAT: Ankr pre-flight 401 x2 (9,2 dtk + 8,3 dtk) — watermark TIDAK dimajukan (tetap 132512564, gap ~30.093 blok ke head 132542657). "
    f"Binanceai tetap refund/failed (launched=0, failed=1, isRefundPhase=1). Bridge tidak berubah (mtime 2026-11-08 18:21 UTC). "
    f"Discovery (Boltbook/Sourcify/sweep/route 6) masih dikerjakan subagent A — digabung di stage 2.")
snap["runNote1401_1109_scan"] = (
    "Run 1401 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs 50 blok (USDT 0x55d3..., blok 132542607-132542657): "
    "ATTEMPT 1 FAIL 9,2 dtk HTTP 401, ATTEMPT 2 FAIL 8,3 dtk HTTP 401 (credential custom.ankr ditolak rpc.ankr.com; outage sejak ~13:33 WIB). "
    "Scan leg TIDAK dijalankan (amendment 2026-11-06: pre-flight gagal = fast-fail, lanjut route lain). Watermark tetap 132512564; "
    "gap ke head 132542657 ~30.093 blok dan tumbuh (milik backfill, ikut gagal 401). Tidak ada first-seen baru dari scan; triage tidak dijalankan.")
snap["runNote1401_1109_binanceai"] = (
    "Run 1401 (blok 132542657, probe dataseed ~14:14 WIB): binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, "
    "totalShares=3110, tokenClaimed(user)=0, saldo TOKEN user=0. Sudah dilaporkan sekali; tidak dilaporkan ulang.")
snap["runNote1401_1109_age_exclusions"] = (
    f"Run 1401 stage 1: age-exclusions baru: {json.dumps(report['age_exclusions'])}; "
    f"kept (sold out, age N/A): {json.dumps(report['age_candidates_kept'])}.")
snap["last_run"] = "1401"
snap["last_run_wib"] = "2026-11-09 ~14:3x WIB"
snap["last_run_note"] = ("Run 1401 stage 1: velocity lolos 4 tanpa promosi; scan fast-fail Ankr 401 (watermark tetap 132512564, gap ~30.093 blok); "
                         "binanceai tetap refund; discovery masih berjalan (stage 2).")
snap["timestamp_wib"] = "2026-11-09 14:3x WIB"

def save_atomic(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)

save_atomic(f"{HF}/onchain-snapshot.json", snap)
json.dump(report, open(f"{HF}/run-2026-11-09-1401-merge-stage1.json", "w"), indent=1)
print("MERGE STAGE 1 DONE. velocity_pass:", report["velocity_pass"])
print("age_exclusions:", report["age_exclusions"])
print("velocity_notes:", report["velocity_notes"])
