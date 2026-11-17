#!/usr/bin/env python3
"""Snapshot update for free-mint-search run 2026-11-14 01:01 WIB.
Merges run-2026-11-14-0101-verify.json + -retry.json into onchain-snapshot.json.
No probe-new.json this run (feed probe was 0x912D only, not agent-shaped).
No preview/mint. Backup saved as onchain-snapshot.json.bak-0101 first."""
import json, shutil, subprocess, os
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
_env = dict(os.environ); _env["TZ"] = "Asia/Jakarta"
NOW = subprocess.check_output(["date", "+%Y-%m-%d ~%H:%M WIB"], env=_env).decode().strip()
LAST_RUN = subprocess.check_output(["date", "+%Y-%m-%dT%H:%M+07:00"], env=_env).decode().strip()
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0101")
print("NOW:", NOW)
snap = json.load(open(BASE + "onchain-snapshot.json"))
verify = json.load(open(BASE + "run-2026-11-14-0101-verify.json"))
retry = json.load(open(BASE + "run-2026-11-14-0101-retry.json"))
READS = {}
for src in (verify, retry):
    for k, v in src["reads"].items():
        if v.get("views") is not None:
            READS[k] = v
VB = verify.get("block")   # 133402541
RB = retry.get("block")    # 133403775

def norm(a):
    return (a or "").lower()

updated = []
for key, ent in snap.get("contracts", {}).items():
    a = norm(ent.get("address"))
    hit = None
    for rk, rv in READS.items():
        if norm(rv.get("address")) == a and a:
            hit = (rk, rv); break
    if not hit:
        continue
    rk, rv = hit
    views = rv["views"]
    for fk, fv in views.items():
        if fk in ("name", "symbol"):
            continue
        if fv is not None:
            ent[fk] = fv
    ent["lastReadBlock"] = RB if rk in retry.get("reads", {}) else VB
    ent["lastReadWib"] = NOW
    updated.append(key)
print("generic-merged:", len(updated), "VB:", VB, "RB:", RB)

def note(key, text):
    ent = snap["contracts"].get(key)
    if ent is not None:
        ent["runNote0101"] = text
    else:
        print("NOTE-MISS:", key)

# Interval 0001->0101: block 133394739 -> 133402541 = 7802 blocks ~58.5 min chain-time.
INTERVAL_MIN = 58.5
def rate(delta):
    return round(delta / INTERVAL_MIN, 3)

def vel(key, delta, prev_rate):
    """Store current rate as previousRatePerMin; return (rate, ratio-or-None, passes)."""
    ent = snap["contracts"].get(key)
    r = rate(delta)
    ratio = (r / prev_rate) if prev_rate else None
    passes = bool(prev_rate and ratio is not None and ratio >= 1.5 and delta >= 20)
    if ent is not None:
        ent["previousRatePerMin"] = r
        ent["currentRatePerMin"] = r
        ent["mintedInInterval"] = delta
        ent["intervalMinutes"] = INTERVAL_MIN
        ent["velocityLegPasses"] = passes
        ent["velocityRatio"] = ratio
    return r, ratio, passes

r, ratio, p = vel("Crown Racer Cards", 48, 2.35)
note("Crown Racer Cards", "Run 0101: totalSupply 405->453 (+48, %.2f/mnt vs prev 2.35 = %.2fx -> velocity GAGAL); freeMinted 451/500 = 90,2%% (>70%%), freeClaimed(user)=0 slot TERBUKA, mintOpen 1. Umur TETAP UNVERIFIED (semua view waktu null run 0001) -> BUKAN strong lead, bukan kandidat. Website/X UNVERIFIED. Tetap early-lead-reported. DIAM." % (r, ratio))
r, ratio, p = vel("Race Agents", 9, 0.55)
note("Race Agents", "Run 0101: totalSupply 348->357 (+9, %.2f/mnt, <20 -> velocity GAGAL); freeMinted 357/1000 = 35,7%%, mintOpen 1. Umur TETAP UNVERIFIED. Bukan strong lead/kandidat. DIAM." % r)
r, ratio, p = vel("Early5877", 58, 2.35)
note("Early5877", "Run 0101: totalMinted 363->421 (+58, %.2f/mnt vs prev 2.35 = %.2fx -> velocity GAGAL); MAX_SUPPLY 10000, mintOpen 1. QUIZ-GATED (sudah dilaporkan run 2231). DIAM." % (r, ratio))
r, ratio, p = vel("Moon", 2, 0.80)
note("Moon", "Run 0101: totalMinted 488->490 (+2, %.2f/mnt -> velocity GAGAL); MAX_SUPPLY 3333, mintOpen 1; free%% UNVERIFIED. Bukan kandidat. DIAM." % r)
r, ratio, p = vel("RoyalRush", 3, 0.0)
note("RoyalRush", "Run 0101: totalSupply 916->919 (+3, <20 -> velocity GAGAL); freeMinted 922/1000 = 92,2%% (free>totalSupply: counter tidak konsisten, dicatat apa adanya); umur TETAP UNVERIFIED. Bukan strong lead/kandidat. DIAM.")
r, ratio, p = vel("MORFO", 13, 0.0)
note("MORFO", "Run 0101: totalSupply 464->477 (+13, <20 -> velocity GAGAL); free%% UNVERIFIED; umur launch tepat UNVERIFIED. Tetap early-lead-reported. DIAM.")
r, ratio, p = vel("Zero", 0, 0.0)
note("Zero", "Run 0101: totalMinted 315 FLAT (+0 -> velocity GAGAL); freeMinted 315/500 = 63,0%% (<70%%), slot terbuka; deadline umur 07:55 WIB 14 Nov. Bukan strong lead. DIAM.")
r, ratio, p = vel("FERO", 1, 0.0)
note("FERO", "Run 0101: totalMinted 19->20 (+1, <20 -> velocity GAGAL); window buka 23:00 WIB 13 Nov; free%% ~20/3333 = 0,6%%. Bukan kandidat/strong lead/early. Tetap watchlist-only. DIAM.")
note("Cinder Crucible", "Run 0101: totalSupply 316->325, freeMinted 325/325 = 100%% SOLD OUT (freeRemaining 0, isFreeOpen 0). Sellout SUDAH dilaporkan hot-leg 01:14 WIB (#sellout-20261114-0029) - TIDAK dilaporkan ulang run ini. Status snapshot -> sold-out-2026-11-14.")
cc = snap["contracts"].get("Cinder Crucible")
if cc is not None:
    cc["status"] = "sold-out-2026-11-14"
note("Mossbound Key", "Run 0101: totalSupply 327->329 (+2), freeMinted 325/325 = 100%% sold out (sudah dilaporkan). DIAM.")
note("Ochre Medallion", "Run 0101: totalSupply 211 FLAT, freeMinted 210/210 = 100%% sold out (sudah dilaporkan). DIAM.")
note("OLIVER", "Run 0101: totalSupply 1034, freeMinted 984, freeRemaining 16. AGE-EXCLUDED (dilaporkan 21:00). DIAM.")
note("Slate", "Run 0101: totalSupply 91, freeMinted 90/480 = 18,8%%, freeRemaining 390, saleOpen 1, mintOpen 1. Bukan kandidat. DIAM.")
note("BUBB", "Run 0101: totalSupply 1406->1410 (+4, <20 -> velocity GAGAL); freeMinted 1269, mintOpen 1. DIAM.")
note("MECHA", "Run 0101 retry: totalMinted 1978->1985 (+7, <20 -> velocity GAGAL); freeClaimed 1984. DIAM.")
note("CY24", "Run 0101 retry: totalSupply 464 FLAT, MAX_SUPPLY 1703, mintOpen 1, costOf(user,1)=0. DIAM.")
note("MossSignal", "Run 0101 retry: totalSupply 805, mintOpen 1. DIAM.")
note("OBFG", "Run 0101: verify + retry KEDUANYA transport FAIL (views null) - nilai snapshot dipertahankan, BUKAN nol. AGE-EXCLUDED. DIAM.")
note("OUTY", "Run 0101: verify + retry KEDUANYA transport FAIL (views null) - nilai snapshot dipertahankan, BUKAN nol. DIAM.")
note("PX24", "Run 0101: verify + retry KEDUANYA transport FAIL (views null) - nilai snapshot dipertahankan, BUKAN nol. DIAM.")
note("HIVE Agents", "Run 0101: totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
note("BUILD", "Run 0101: totalMinted 206 FLAT, freeMinted 200/200 = 100%% free pool habis, freeClaimed(user)=1. Minted-by-user. DIAM.")
note("SKRR", "Run 0101: totalSupply 518->519 (+1), MAX_SUPPLY 1682, mintOpen 1, costOf(user,1)=0. DIAM.")
note("HANAMI", "Run 0101: totalSupply 132 FLAT, freeMinted 130, MAX_SUPPLY 3333. DIAM.")
note("UNRES1", "Run 0101: totalSupply 128 FLAT, freeMinted 128, mintOpen 1. Tidak masuk snapshot (identitas belum jelas). DIAM.")
note("AgentMuse", "Run 0101: verify views null (nilai snapshot dipertahankan); deadline umur 05:53 WIB 14 Nov. DIAM.")
note("BinanceAI-mint", "Run 0101: launched()=0, tokenClaimed(user)=0, isRefundPhase()=1, failed()=1, refundClaimed(user)=0 - TIDAK BERUBAH (refund phase sudah dilaporkan sekali 2 Nov). Tetap pending, TIDAK dilaporkan ulang. DIAM.")

snap["last_run_wib"] = LAST_RUN
snap["last_run_note"] = ("Run 0101: verify 55/61 OK (blok 133402541, 1463,7 dtk) + retry 3/6 (blok 133403775, 342,7 dtk; OBFG/OUTY/PX24 transport FAIL 2x); "
    "0 kandidat baru, 0 strong lead baru, 0 early lead baru; Cinder Crucible SOLD OUT 325/325 (sudah dilaporkan hot-leg 01:14, tidak re-report); "
    "Crown Racer 451/500 = 90,2% tapi umur UNVERIFIED -> bukan strong lead; binanceai pending TIDAK BERUBAH (refund phase); "
    "scan leg fast-fail (pre-flight: no head, dataseed timeout 30 dtk; Ankr 401 sejak 2026-11-09); watermark 132512564; "
    "Sourcify feed: 1 baru 0x912D bukan agent-shaped (registry bytes tidak ada); Boltbook EN+ZH 0 baru; KOMA age-excluded (sudah di track_c); Odaily 0 baru.")
snap["timestamp_wib"] = NOW
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("snapshot updated; contracts:", len(snap.get("contracts", {})), "track_c:", len(snap.get("track_c", {})))
