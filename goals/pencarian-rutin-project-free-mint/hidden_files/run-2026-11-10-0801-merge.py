#!/usr/bin/env python3
"""Merge run 2026-11-10 08:01 WIB (tag 0801). Reloads snapshot fresh, applies
reread. Scan FAST-FAIL (preflight Ankr 401 x2, outage since 2026-11-09 ~13:33 WIB)
-> watermark NOT advanced. NO execution in this run.
Velocity baseline: snapshot post-merge 0731; interval block-derived 30.08 min
(132680948 ts 1794270757 -> 132684959 ts 1794272562).
Skip-if-fresher: a contract whose live lastReadBlock is newer than this run's
block is skipped. Removals: NONE. Additions: NONE.
"""
import json, shutil, copy
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB)
NOW_STR = NOW.strftime("%Y-%m-%d %H:%M WIB")
INTERVAL = 30.08
NEW_BLOCK = 132684959

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0801-premerge")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
base = copy.deepcopy(s)
rr = json.load(open(f"{BASE}/run-2026-11-10-0801-reread.json"))
C = s["contracts"]; TC = s.get("track_c", {})
BC = base["contracts"]; BTC = base.get("track_c", {})

updated = 0; degraded = 0; skipped_fresher = 0; vel_pass = []
for name, e in list(BC.items()):
    live = C.get(name)
    if live is None:
        continue
    if isinstance(live.get("lastReadBlock"), int) and live["lastReadBlock"] > NEW_BLOCK:
        skipped_fresher += 1
        continue
    r = rr["reread"].get(name)
    if r is None:
        continue
    prev_sup = e.get("totalSupply"); new_sup = r.get("totalSupply")
    if new_sup is None:
        degraded += 1
        note = f"Run 0801 (blok {NEW_BLOCK}, {NOW_STR}): totalSupply None (degradasi eth_call, nilai lama dipertahankan); "
    else:
        minted = None; rate = None; ratio = None; vpass = False
        if prev_sup is not None and isinstance(prev_sup, int) and isinstance(new_sup, int) and prev_sup < 10_000_000:
            minted = new_sup - prev_sup
            rate = minted / INTERVAL
            prev_rate = float(e.get("currentRatePerMin") or e.get("previousRatePerMin") or 0) or 0.0
            if prev_rate > 0:
                ratio = rate / prev_rate
            vpass = bool(minted >= 20 and prev_rate > 0 and ratio is not None and ratio >= 1.5)
            if vpass:
                vel_pass.append((name, minted, round(rate, 4), round(prev_rate, 4), round(ratio, 2)))
            live["previousTotalSupply"] = prev_sup; live["mintedInInterval"] = minted
            live["intervalMinutes"] = INTERVAL; live["currentRatePerMin"] = rate
            live["previousRatePerMin"] = prev_rate; live["velocityRatio"] = ratio
            live["velocityLegPasses"] = vpass
        live["totalSupply"] = new_sup
        note = f"Run 0801 (blok {NEW_BLOCK}, {NOW_STR}): totalSupply {prev_sup}->{new_sup} (+{minted if minted is not None else '?'}), velocity {'LOLOS' if vpass else 'GAGAL'}; "
    for k in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if r.get(k) is not None:
            live[k] = r[k]
    if r.get("balanceOf_user") is not None:
        live["balanceOf_user"] = r["balanceOf_user"]
    if r.get("freeClaimed_user") is not None:
        live["freeClaimed_user"] = r["freeClaimed_user"]
    live["lastReadBlock"] = NEW_BLOCK; live["lastReadWib"] = NOW_STR
    live["runNote0801_1110"] = note + f"free={live.get('freeClaimed')}/{live.get('FREE_SUPPLY')}; bal_user={live.get('balanceOf_user')}; status {live.get('status')}."
    updated += 1

tc_updated = 0
for name, e in list(BTC.items()):
    if not isinstance(e, dict):
        continue
    live = TC.get(name)
    if not isinstance(live, dict):
        continue
    r = rr["track_c"].get(name)
    if r is None:
        continue
    for k in ("totalSupply", "freeMinted", "freeSharesRemaining", "totalFreeShares"):
        if r.get(k) is not None:
            live[k] = r[k]
    live["lastReadBlock"] = NEW_BLOCK; live["lastReadWib"] = NOW_STR
    tc_updated += 1

removed = []

# --- FCAT / JINCHAN Agents special updates (run 0801 re-read) ---
fcat = C.get("FCAT Agents")
if isinstance(fcat, dict):
    fcat["freePctVerified"] = round(329 / 888 * 100, 2)
    fcat["freePctNote0801"] = (
        "Run 0801: totalSupply 305->329 (+24), freeClaimed 329/888 = 37,0% TERVERIFIKASI "
        "(run 0731: 305/888 = 34,3%). Velocity GAGAL (rate 0,80/mnt vs prev 0,85 = 0,94x). "
        "Slot TERBUKA (balanceOf(user)=0). Umur UNVERIFIED + website GATE FAILED (metode A/G/H/I, run 0701). "
        "Tetap watchlist-only - BELUM strong lead. TIDAK preview/mint."
    )
jin = C.get("JINCHAN Agents")
if isinstance(jin, dict):
    jin["freePctVerified"] = round(192 / 888 * 100, 2)
    jin["freePctNote0801"] = (
        "Run 0801: totalSupply 170->192 (+22), freeClaimed 192/888 = 21,6% TERVERIFIKASI "
        "(run 0731: 170/888 = 19,1%). Velocity GAGAL (rate 0,73/mnt vs prev 0,74 = 0,99x). "
        "<25% strong-lead leg. Slot terbuka (bal 0). Umur/website UNVERIFIED. Tetap watchlist-only."
    )

s["runNote0801_1110"] = (
 f"Run 0801 (blok {NEW_BLOCK}, interval 30,08 mnt vs 0731): re-read 632 kontrak + 74 track_c "
 f"(degraded totalSupply None: {degraded}). "
 f"Velocity LOLOS {len(vel_pass)}: {vel_pass} - promosi 0. SlimySlug +90 (2,99/mnt vs prev 0,11 = 26,93x) "
 f"TAPI free% UNVERIFIED (None/None), X false, umur UNVERIFIED, watchlist-only sejak 2026-11-05 - bukan "
 f"strong lead/kandidat. bridge-0x93bf08d2 terbuang oleh guard prev_sup<10jt (totalSupply raksasa, artefak baca). "
 f"FCAT Agents: totalSupply 305->329 (+24, rate 0,80/mnt vs prev 0,85 = 0,94x, velocity GAGAL), "
 f"freeClaimed 329/888 = 37,0% TERVERIFIKASI (naik dari 34,3% run 0731), slot TERBUKA (bal 0), "
 f"umur UNVERIFIED + website GATE FAILED (run 0701) -> tetap watchlist-only, BELUM strong lead, "
 f"TIDAK preview/mint. JINCHAN Agents (twin): 170->192 (+22), freeClaimed 192/888 = 21,6% "
 f"TERVERIFIKASI (<25%), velocity GAGAL (0,73 vs 0,74 = 0,99x), umur/website UNVERIFIED -> tetap "
 f"watchlist-only. "
 f"THYRK: totalSupply 1640->1775 (+135, rate 4,49/mnt vs prev 5,00 = 0,90x, velocity GAGAL), "
 f"freeMinted 1766/7777 = 22,7% (INFERENSI bila semua mint gratis, bukan verified; % leg N/A), slot "
 f"TERBUKA, website thyrk.fun TERVERIFIKASI, umur presisi UNVERIFIED - tetap early lead, BELUM strong lead. "
 f"SAKURA: totalSupply 1186->1210 (+24), freeMinted 1200/6000 = 20,0% (<25%), velocity GAGAL "
 f"(0,80/mnt vs prev 1,63 = 0,49x; run 0731 sempat LOLOS 1,60x) - tetap early lead. "
 f"Lenx Agent Pass: totalSupply None (degradasi, nilai lama 128 dipertahankan); freeMinted/totalMinted "
 f"tetap 1000 (nilai konstan sejak 0731, tidak konsisten dgn totalSupply 128 - view tak andal, bukan sold out "
 f"terverifikasi); bal_user=0; status strong-lead-gate-unverified, tanpa perubahan. "
 f"Age-exclusion baru: TIDAK ADA. MONOLITH deadline umur 2026-11-10 17:32 WIB (belum lewat; 638->639). "
 f"Night Bandits Club (launch terverifikasi 2026-11-07 18:02, ~62 jam) + King's Game (launch "
 f"UNVERIFIED) tetap age-watch (semua view free-quota None run ini -> 'belum sold out' tak "
 f"terverifikasi; preseden run 2231/2301/2331/0601/0701/0731). "
 f"binanceai.fun TIDAK BERUBAH (launched=0, failed=1, refund=1, totalShares 3110, tokenClaimed user 0, "
 f"saldo 0, blok 132685386) - tidak dilaporkan ulang. "
 f"Track C: sellout/paid-only baru TIDAK ADA yang terverifikasi (NUSA freeMinted 362 flat; FOUNT 1000 "
 f"flat; BI NIU freeSharesRemaining 0 sudah excluded; COSO v2 sudah age-excluded, 634->643 tak relevan). "
 f"Scan FAST-FAIL (preflight Ankr 401 x2: 5,4 dtk + 2,9 dtk; outage sejak 2026-11-09 ~13:33 WIB); "
 f"watermark tetap 132512564, gap ke head ~173.900 blok. "
 f"Discovery: Boltbook EN 200 47.847B + ZH 200 48.019B (0 alamat baru vs snapshot+seen+hot), Sourcify feed 20 "
 f"(11 baru vs 0731: 0 hit S1/S2 - 0x143E3Bcd mint+quote+freeUsed tanpa registry; 0x4CA724a3 mint+quote+"
 f"freeMinted ERC-721 tanpa registry; sisanya tanpa mint/quote/free/registry), sweep rute 3 (EN+ZH): "
 f"Lenx Agent Pass sudah di snapshot; AgentForge/Hundred/PocketDragons/Gloomies (post 24-27 Okt, >48 jam) "
 f"age-excluded saat discovery, tidak dilaporkan; Odaily 0, PANews 0, "
 f"bridge 116 kontrak (mtime tak berubah 2026-11-08 18:21 UTC; 8 tidak di snapshot, 7 discarded, sama "
 f"seperti run 0731; 0 promosi). "
 f"TIDAK ADA kandidat/strong lead/early lead baru - run DIAM."
)
s["runNote0801_1110_scan"] = (
 "Run 0801 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs 50 blok (head 132685162): FAIL 5,4 dtk "
 "HTTP 401 Unauthorized, retry FAIL 2,9 dtk HTTP 401 (head 132686486). Kelanjutan outage Ankr sejak "
 "2026-11-09 ~13:33 WIB (preflight 0601/0701/0731 juga 401). Scan leg TIDAK dijalankan (amendemen 2026-11-06: "
 "credits-exhausted/paid-gate error -> stop leg run ini, lanjut route lain, tanpa bayar). "
 "Watermark tetap 132512564; gap ke head ~173.900 blok dan tumbuh (milik backfill, backfill OFF). "
 "5c dilewati (tanpa output scan)."
)
s["runNote0801_1110_age_exclusions"] = (
 "Age-exclusion run 0801: TIDAK ADA. MONOLITH belum lewat deadline umur (2026-11-10 17:32 WIB). "
 "Night Bandits Club (launch terverifikasi 2026-11-07 18:02:28 WIB, ~62 jam > 48 jam) tetap age-watch: "
 "semua view free-quota None run ini sehingga 'belum sold out' tak terverifikasi (preseden run "
 "2231/2301/2331/0601/0701/0731). King's Game tetap age-watch (launch UNVERIFIED; first-seen 2026-11-07 21:06 "
 "hanya lower bound). Discovery: AgentForge (post 27 Okt), Hundred (25 Okt), PocketDragons (24 Okt), "
 "Gloomies (25 Okt, tanpa syarat Agent ID) - semuanya >48 jam sejak publikasi, age-excluded saat discovery, "
 "tidak masuk snapshot, tidak dilaporkan."
)

json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"updated={updated} degraded={degraded} skipped_fresher={skipped_fresher} tc_updated={tc_updated}")
print(f"vel_pass={vel_pass}")
print(f"removed={removed}")
print(f"contracts now={len(C)} track_c now={len(TC)}")
