#!/usr/bin/env python3
"""Merge run 2026-11-09 1201 WIB — re-read velocity, snapshot updates, Lenx early lead,
seen appends, track_c updates, age-exclusion candidates. PACTA handled separately
(website gate pending BscScan browser read) — this script does NOT add PACTA.
Writes: onchain-snapshot.json (atomic), onchain-scan-seen.json (atomic),
run-2026-11-09-1201-merge.json (report). Read-only w.r.t. chain; never mints/previews.
"""
import json, os, shutil, re
from datetime import datetime, timezone, timedelta

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
NOW = datetime(2026, 11, 9, 12, 45, tzinfo=timezone(timedelta(hours=7)))
BLOCK_1201 = 132526110
BLOCK_1131 = 132522548
INTERVAL_MIN = (BLOCK_1201 - BLOCK_1131) * 0.45 / 60.0  # chain-time interval, ~26.7 min
print(f"interval_minutes (block-based): {INTERVAL_MIN:.2f}")

snap = json.load(open(f"{HF}/onchain-snapshot.json"))
r1131 = json.load(open(f"{HF}/run-2026-11-09-1131-reread.json"))
r1201 = json.load(open(f"{HF}/run-2026-11-09-1201-reread.json"))
tri = json.load(open(f"{HF}/run-2026-11-09-1201-triage.json"))
disc = json.load(open(f"{HF}/run-2026-11-09-1201-discovery-A.json"))
bna = json.load(open(f"{HF}/run-2026-11-09-1201-binanceai.json"))
seen = json.load(open(f"{HF}/onchain-scan-seen.json"))
lenx_state = json.load(open(f"{HF}/run-2026-11-09-1201-6e25-state.json"))
lenx_first = json.load(open(f"{HF}/run-2026-11-09-1201-firstmint-6E25.json"))

shutil.copy(f"{HF}/onchain-snapshot.json", f"{HF}/onchain-snapshot.json.bak-2026-11-09-1201")
shutil.copy(f"{HF}/onchain-scan-seen.json", f"{HF}/onchain-scan-seen.json.bak-2026-11-09-1201")

report = {"run": "2026-11-09-1201", "interval_minutes": round(INTERVAL_MIN, 2),
          "velocity_pass": [], "velocity_fail_note": [], "sellouts_new": [],
          "slot_changes": [], "age_exclusions": [], "age_candidates_kept": []}

contracts = snap.get("contracts", {})
# ---- 1. re-read velocity + snapshot value updates ----
n_upd = 0
for name, d in r1201.get("reread", {}).items():
    old = contracts.get(name)
    if not isinstance(old, dict):
        continue
    base1131 = r1131.get("reread", {}).get(name, {}).get("totalSupply")
    base_snap = old.get("totalSupply")
    new_ts = d.get("totalSupply")
    prev_rate = old.get("currentRatePerMin")
    vel = {"name": name, "baseline": None, "minted": None, "rate": None, "ratio": None, "passes": False, "note": ""}
    # Velocity leg applies ONLY to NFT mint counts. Fungible/bridge token entries
    # (kind contains ERC20/bridge, or status is a scan-complement token) must NOT
    # pass velocity on raw 18-decimal supply deltas (2026-11-09 1201 correction).
    kind = str(old.get("kind") or "")
    st = str(old.get("status") or "")
    is_token = ("ERC20" in kind.upper() or "bridge" in kind.lower() or
                "bridge" in st.lower() or "pelengkap-scan" in st.lower() or
                "scan-complement" in st.lower())
    if new_ts is not None and base1131 is not None and not is_token:
        minted = new_ts - base1131
        rate = minted / INTERVAL_MIN
        ratio = (rate / prev_rate) if (prev_rate not in (None, 0)) else None
        vel.update({"baseline": base1131, "minted": minted, "rate": round(rate, 4),
                    "ratio": round(ratio, 2) if ratio is not None else None,
                    "passes": bool(minted >= 20 and ratio is not None and ratio >= 1.5),
                    "note": "baseline=1131 reread"})
        if vel["passes"]:
            report["velocity_pass"].append(vel)
        old["previousTotalSupply"] = base1131
        old["previousRatePerMin"] = prev_rate
        old["currentRatePerMin"] = round(rate, 4)
        old["velocityRatio"] = vel["ratio"]
    elif new_ts is not None and base_snap is not None and new_ts != base_snap:
        vel.update({"note": "baseline 1131 missing (batch fail) — velocity NOT computed over stale snapshot interval"})
        old["previousTotalSupply"] = base_snap
    # value updates (only when read succeeded, never overwrite with None)
    for k in ["totalSupply", "freeClaimed", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"]:
        if d.get(k) is not None:
            old[k] = d[k]
    if d.get("balanceOf_user") is not None:
        old["balanceOf_user"] = d["balanceOf_user"]
        old["userBalance"] = d["balanceOf_user"]
    if d.get("freeClaimed_user") is not None:
        old["freeClaimed_user"] = d["freeClaimed_user"]
    fc, fs = old.get("freeClaimed"), old.get("FREE_SUPPLY")
    if isinstance(fc, (int, float)) and isinstance(fs, (int, float)) and fs:
        old["freePctVerified"] = round(100.0 * fc / fs, 2)
    old["lastReadBlock"] = BLOCK_1201
    old["lastReadWib"] = "2026-11-09 12:2x WIB"
    if vel["minted"] is not None:
        old["mintedInInterval"] = vel["minted"]
        old["intervalMinutes"] = round(INTERVAL_MIN, 2)
        old["velocityLegPasses"] = vel["passes"]
        old["runNote1201_1109"] = (f"Run 1201 (blok {BLOCK_1201}, interval {INTERVAL_MIN:.1f} mnt vs run 1131): "
            f"{vel['baseline']}->{new_ts} (+{vel['minted']}, {vel['rate']:.3f}/mnt vs prev {prev_rate} = "
            f"{vel['ratio']}x) -> velocity {'LOLOS' if vel['passes'] else 'GAGAL'}; "
            f"free={old.get('freeClaimed')}/{old.get('FREE_SUPPLY')}; bal_user={d.get('balanceOf_user')}; "
            f"status {old.get('status')}.")
        n_upd += 1
    else:
        old["runNote1201_1109"] = (f"Run 1201 (blok {BLOCK_1201}): totalSupply {new_ts} "
            f"(baseline 1131 gagal baca / snapshot stale — velocity TIDAK dihitung); "
            f"free={old.get('freeClaimed')}/{old.get('FREE_SUPPLY')}; bal_user={d.get('balanceOf_user')}; "
            f"status {old.get('status')}.")
print(f"contracts updated: {n_upd} velocity-pass: {[v['name'] for v in report['velocity_pass']]}")

# ---- 2. track_c re-read updates ----
tc = snap.get("track_c", {})
n_tc = 0
for name, d in r1201.get("track_c", {}).items():
    old = tc.get(name)
    if not isinstance(old, dict):
        continue
    prev_free = old.get("freeSharesRemaining")
    for k in ["freeSharesRemaining", "freeMinted", "totalSupply"]:
        if d.get(k) is not None:
            old[k] = d[k]
    if d.get("balanceOf_user") is not None:
        old["balanceOf_user"] = d["balanceOf_user"]
    if d.get("freeClaimed_user") is not None:
        old["freeClaimed_user"] = d["freeClaimed_user"]
    old["lastReadBlock"] = BLOCK_1201
    n_tc += 1
    if prev_free not in (None, 0) and old.get("freeSharesRemaining") == 0:
        report["sellouts_new"].append({"name": name, "prev_free": prev_free})
    if prev_free == 0 and old.get("freeSharesRemaining") not in (None, 0):
        report["slot_changes"].append({"name": name, "note": "free pool reopened?"})
print(f"track_c updated: {n_tc} sellouts_new: {report['sellouts_new']}")

# ---- 3. Lenx Agent Pass — early lead (reported once this run) ----
LENX = "0x6E252E3a3584BD6a64C103e4eDFa761f6335980F"
contracts["Lenx Agent Pass"] = {
    "address": LENX,
    "status": "early-lead-reported-2026-11-09",
    "name": "Lenx Agent Pass",
    "symbol": "LAP",
    "kind": "ERC721",
    "totalSupply": lenx_state.get("totalMinted"),
    "totalMinted": lenx_state.get("totalMinted"),
    "freeClaimed": lenx_state.get("freeMinted"),
    "freeMinted": lenx_state.get("freeMinted"),
    "freeRemaining": lenx_state.get("freeRemaining"),
    "FREE_CAP": lenx_state.get("FREE_CAP"),
    "MAX_SUPPLY": lenx_state.get("MAX_SUPPLY"),
    "freePctVerified": round(100.0 * lenx_state["freeMinted"] / lenx_state["FREE_CAP"], 2),
    "mintOpen": None,
    "userBalance": 0,
    "freeClaimed_user": lenx_state.get("freeClaimed_user"),
    "userSlotNote": "Slot OPEN: freeClaimed(user)=0, mintedOf(user)=0 (fresh read run 1201).",
    "firstSeenBlock": lenx_first["first_mint_block"],
    "firstMintWib": "2026-11-09 11:38:27 WIB",
    "firstMintTx": lenx_first["tx"],
    "lastReadBlock": BLOCK_1201,
    "lastReadWib": "2026-11-09 12:2x WIB",
    "xVerified": False,
    "velocityVerified": False,
    "website": None,
    "gate": "NOT CHECKED (early lead — never previewed/minted; website methods H/C/G tried, no site found)",
    "launchNote": ("First mint verified on-chain: first Transfer-from-zero at block 132521921, "
                   "2026-11-09 11:38:27 WIB (Ankr getLogs, address-filtered); age ~1 jam at report, WITHIN 48h. "
                   "Sourcify verifiedAt 2026-11-09T04:41:04Z is verification time, NOT launch time."),
    "baselineNote": ("EARLY lead reported once run 1201: agent-shaped (registry bytes in code + Sourcify exact_match "
                     "ABI with freeMint/freeMinted/freeClaimed/freeRemaining/FREE_CAP + mintPaid; 1131 triage ABI read), "
                     "first mints verified on-chain in run (14 in 1201 scan window, 56 in 10k-block chunk, totalMinted 128). "
                     "Free 128/1000 = 12.8% (<25% strong lead), user slot open, X unverified, website unverified "
                     "(contractURI() empty; Sourcify metadata fetch timeout; name search 0 hits), velocity baseline recorded this run. "
                     "Owner 0x9e3b3e87dfadea885ad82d6cd22e3505c7741619 NOT in same-owner-discards (60 entries checked). "
                     "Promotes to strong lead only on all 3 legs (age<=48h + free>=25% + slot open); to candidate only on ALL criteria + safety."),
    "velocityNote": "run 1201: baseline first recorded (totalMinted 128, rate n/a) — velocity NOT passed on baseline alone.",
    "previousTotalSupply": None,
    "mintedInInterval": None,
    "intervalMinutes": None,
    "currentRatePerMin": None,
    "previousRatePerMin": None,
    "velocityLegPasses": False,
    "supplyView": "totalMinted",
    "owner": "0x9e3b3e87dfadea885ad82d6cd22e3505c7741619",
    "PAID_PRICE": lenx_state.get("PAID_PRICE"),
    "scanWindow": "132525040-132526039",
    "scanMints": 14,
    "scanMinters": 14,
}

# ---- 4. seen appends (ONLY the 11 triage first-seen, per the body:
# a contract counts as first-seen ONLY if absent from both seen and snapshot) ----
scan = json.load(open(f"{HF}/run-2026-11-09-1201-scan.json"))
seen_contracts = seen.setdefault("contracts", {})
seen_top_lows = {k.lower() for k in seen}
seen_nested_lows = {k.lower() for k in seen_contracts}
added = 0
raw_by_addr = {c["address"].lower(): c for c in scan.get("contracts_raw", [])}
for t in tri.get("first_seen_triage", []):
    key = t["address"].lower()
    if key in seen_top_lows or key in seen_nested_lows:
        continue
    seen_contracts[key] = raw_by_addr.get(key, {}).get("first_block", t.get("first_block"))
    added += 1
print(f"seen appended: {added}")
report["seen_appended"] = added

# ---- 5. age-exclusion scan (structured launch times only) ----
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
    # sold out? totalSupply/totalMinted >= MAX_SUPPLY (fresh 1201 read preferred)
    r1201d = r1201.get("reread", {}).get(name, {})
    ts = r1201d.get("totalSupply") if r1201d.get("totalSupply") is not None else v.get("totalSupply")
    tm = r1201d.get("totalMinted") if r1201d.get("totalMinted") is not None else v.get("totalMinted")
    mx = v.get("MAX_SUPPLY")
    sold_out = bool(mx and ((isinstance(ts, (int, float)) and ts >= mx) or
                            (isinstance(tm, (int, float)) and tm >= mx)))
    if sold_out:
        report["age_candidates_kept"].append({"name": name, "age_h": round(age_h, 1), "reason": "sold out — age rule N/A"})
        continue
    mint_open = r1201d.get("mintOpen") if r1201d.get("mintOpen") is not None else v.get("mintOpen")
    reason = "age-over-48h-not-sold-out"
    if mint_open == 0:
        reason = "mint-closed (mintOpen=0), age-over-48h"
    # age-exclude: remove from active watchlist
    report["age_exclusions"].append({"name": name, "address": v.get("address"), "age_h": round(age_h, 1),
                                      "launch_time": t.isoformat(), "totalSupply": ts, "totalMinted": tm,
                                      "reason": reason, "status_was": st})
    del contracts[name]
print(f"age exclusions: {report['age_exclusions']}")
print(f"age kept (sold out): {report['age_candidates_kept']}")

# ---- 6. run notes ----
snap["runNote1201_1109"] = (
    "Run 1201 (SILENT + 2 lead): re-read 594/594 kontrak + 79/79 track_c (blok 132526110); "
    "velocity LOLOS 1: AgentPad Pass (+70, ~26x) TAPI umur UNVERIFIED + free% UNVERIFIED -> tetap watchlist-only-age-unverified, "
    "tidak dipromosikan. Lenx Agent Pass 0x6E252E3a = EARLY LEAD BARU (dilaporkan sekali): first mint 11:38:27 WIB, "
    "free 128/1000=12,8%, slot user terbuka, X + website UNVERIFIED. PACTA sale 0x6Cbf2E38 = TRACK-C LEAD BARU "
    "(dilaporkan sekali; gate website masih dicek via BscScan — lihat runNote1201_1109_pacta). "
    "Scan SUKSES: window 132525040-132526039 (1000 blok), 40 panggilan Ankr, 0 error, 99 NFT + 374 ERC20-mint, "
    "11 first-seen (triage: 0 S1/S2; Sourcify terdegradasi run ini — error:JSONDecodeError massal, bentuk dinilai dari baca 1131 + baca on-chain segar). "
    "5c: 56 kandidat mc>=10, 13 baru dicek, 0 sale-shape. Binanceai tetap refund/failed. Bridge tidak berubah. "
    "Boltbook crawl sama dengan 1131 (tidak ada post baru). ORDIagent belum buka (saleStart 17:00 WIB; '18:00' di Boltbook = zona UTC+8 yang sama). "
    "META BLOOM bukan agent-shaped (tanpa registry/agent fn) -> bukan lead. BI NIU free pool habis sudah excluded sebelumnya.")
snap["runNote1201_1109_scan"] = (
    "Run 1201 scan: pre-flight OK 6,2 dtk. Window 132525040-132526039 (1000 blok, cap amendment), 40 panggilan Ankr, 0 error, "
    "99 NFT + 374 ERC20-mint. Enrich phase lambat (Sourcify) — file partial dipakai triage (contracts_raw lengkap). "
    "11 first-seen: 0x33862343 (91 mint, registry bytes, tanpa free view — bukan early lead), 0x6E252E3a Lenx (14 mint, agent-shaped — EARLY LEAD), "
    "0xD7Eb2979 (2 mint, bukan agent-shaped), 8 kontrak 1-mint (registry bytes saja, Sourcify gagal baca — bentuk unverified, log only). "
    "Watermark TIDAK dimajukan (milik backfill). 5c: 13 baru dicek, 0 S1/S2.")
snap["runNote1201_1109_discovery"] = (
    "Run 1201 discovery (Subagent A): NOTHING NEW selain 2 watch item. Boltbook EN+ZH crawl sama dengan 1131 (04:40-04:41 UTC) — tidak ada post baru. "
    "Sourcify feed 20 entri, shape-check ulang dengan ?fields=abi (fetch pertama gagal — endpoint telanjang tanpa ABI). "
    "PACTA sale 0x6Cbf2E38 S1 LOLOS (ditemukan via feed; parent verifikasi segar + gate). Odaily/PANews 0 mention. "
    "DappBay 'Bloom' nihil. Bridge mtime tidak berubah (0 baru). YAMA gate tetap FAILED.")
snap["runNote1201_1109_binanceai"] = (
    f"Run 1201 (blok {bna.get('block')}): binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, "
    f"totalShares=3110, tokenClaimed(user)=0, saldo TOKEN user=0. Sudah dilaporkan sekali; tidak dilaporkan ulang.")
snap["runNote1201_1109_age_exclusions"] = (
    f"Run 1201: age-exclusions baru: {json.dumps(report['age_exclusions'])}; "
    f"kept (sold out, age N/A): {json.dumps(report['age_candidates_kept'])}.")
snap["last_run"] = "1201"
snap["last_run_wib"] = "2026-11-09 ~12:4x WIB"
snap["last_run_note"] = ("Run 1201: 1 early lead baru (Lenx Agent Pass) + 1 track-C lead baru (PACTA, gate website pending BscScan); "
                         "velocity lolos 1 (AgentPad Pass, tidak promosi — umur/free unverified); scan sukses; binanceai tetap refund.")
snap["timestamp_wib"] = "2026-11-09 12:4x WIB"

def save_atomic(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)

save_atomic(f"{HF}/onchain-snapshot.json", snap)
save_atomic(f"{HF}/onchain-scan-seen.json", seen)
json.dump(report, open(f"{HF}/run-2026-11-09-1201-merge.json", "w"), indent=1)
print("MERGE DONE. velocity_pass:", report["velocity_pass"])
print("age_exclusions:", report["age_exclusions"])
