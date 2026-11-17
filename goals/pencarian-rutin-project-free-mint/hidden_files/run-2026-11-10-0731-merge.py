#!/usr/bin/env python3
"""Merge run 2026-11-10 07:31 WIB (tag 0731). Reloads snapshot fresh, applies
reread. Writes snapshot. Scan FAST-FAIL (preflight Ankr 401 x2, outage since
2026-11-09 ~13:33 WIB) -> watermark NOT advanced. NO execution in this run.
Velocity baseline: snapshot post-merge 0701 (current snapshot before this merge);
interval block-derived 27.0 min (132677349 ts 1794269137 -> 132680948 ts 1794270757).
Skip-if-fresher: a contract whose live lastReadBlock is newer than this run's
block is skipped.
Removals: NONE. Additions: NONE.
FCAT/JINCHAN Agents: free% verified on-chain segar (305/888, 170/888); see run note.
"""
import json, shutil, copy
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB)
NOW_STR = NOW.strftime("%Y-%m-%d %H:%M WIB")
INTERVAL = 27.0
NEW_BLOCK = 132680948

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0731-premerge")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
base = copy.deepcopy(s)
rr = json.load(open(f"{BASE}/run-2026-11-10-0731-reread.json"))
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
        note = f"Run 0731 (blok {NEW_BLOCK}, {NOW_STR}): totalSupply None (degradasi eth_call, nilai lama dipertahankan); "
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
        note = f"Run 0731 (blok {NEW_BLOCK}, {NOW_STR}): totalSupply {prev_sup}->{new_sup} (+{minted if minted is not None else '?'}), velocity {'LOLOS' if vpass else 'GAGAL'}; "
    for k in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if r.get(k) is not None:
            live[k] = r[k]
    if r.get("balanceOf_user") is not None:
        live["balanceOf_user"] = r["balanceOf_user"]
    if r.get("freeClaimed_user") is not None:
        live["freeClaimed_user"] = r["freeClaimed_user"]
    live["lastReadBlock"] = NEW_BLOCK; live["lastReadWib"] = NOW_STR
    live["runNote0731_1110"] = note + f"free={live.get('freeClaimed')}/{live.get('FREE_SUPPLY')}; bal_user={live.get('balanceOf_user')}; status {live.get('status')}."
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

# --- NO age-exclusion this run ---
# MONOLITH: first mint 2026-11-08 17:32:27 WIB, deadline umur 2026-11-10 17:32 WIB (belum lewat).
# Night Bandits Club: launch TERVERIFIKASI 2026-11-07 18:02:28 WIB (~61,5 jam > 48 jam) TAPI semua
# view free-quota None run ini -> 'belum sold out' tak terverifikasi; tetap age-watch per preseden
# run 2231/2301/2331/0601/0701. King's Game: launch UNVERIFIED (first-seen 2026-11-07 21:06 hanya lower
# bound) -> tetap age-watch, bukan exclusion.
removed = []

# --- FCAT / JINCHAN Agents special updates (run 0731 re-read) ---
fcat = C.get("FCAT Agents")
if isinstance(fcat, dict):
    fcat["freePctVerified"] = round(305 / 888 * 100, 2)
    fcat["freePctNote0731"] = (
        "Run 0731: totalSupply 282->305 (+23), freeClaimed 305/888 = 34,3% TERVERIFIKASI "
        "(run 0701: 282/888 = 31,8%). Velocity GAGAL (rate 0,85/mnt vs prev 2,09 = 0,41x). "
        "Slot TERBUKA (balanceOf(user)=0). Umur UNVERIFIED + website GATE FAILED (metode A/G/H/I, run 0701). "
        "Tetap watchlist-only - BELUM strong lead. TIDAK preview/mint."
    )
jin = C.get("JINCHAN Agents")
if isinstance(jin, dict):
    jin["freePctVerified"] = round(170 / 888 * 100, 2)
    jin["freePctNote0731"] = (
        "Run 0731: totalSupply 150->170 (+20), freeClaimed 170/888 = 19,1% TERVERIFIKASI "
        "(run 0701: 150/888 = 16,9%). Velocity GAGAL (rate 0,74/mnt vs prev 0,62 = 1,20x). "
        "<25% strong-lead leg. Slot terbuka (bal 0). Umur/website UNVERIFIED. Tetap watchlist-only."
    )

s["runNote0731_1110"] = (
 f"Run 0731 (blok {NEW_BLOCK}, interval 27,0 mnt vs 0701): re-read 632 kontrak + 74 track_c "
 f"(degraded totalSupply None: {degraded}). "
 f"Velocity LOLOS {len(vel_pass)}: {vel_pass} - promosi 0 (semua gagal kaki lain: free%/umur/website "
 f"UNVERIFIED atau gate-blocked/discarded/minted-by-user/age-excluded). "
 f"FCAT Agents: totalSupply 282->305 (+23, rate 0,85/mnt vs prev 2,09 = 0,41x, velocity GAGAL), "
 f"freeClaimed 305/888 = 34,3% TERVERIFIKASI (naik dari 31,8% run 0701), slot TERBUKA (bal 0), "
 f"umur UNVERIFIED + website GATE FAILED (run 0701) -> tetap watchlist-only, BELUM strong lead, "
 f"TIDAK preview/mint. JINCHAN Agents (twin): 150->170 (+20), freeClaimed 170/888 = 19,1% "
 f"TERVERIFIKASI (<25%), velocity GAGAL (0,74 vs 0,62 = 1,20x), umur/website UNVERIFIED -> tetap "
 f"watchlist-only. "
 f"THYRK: totalSupply 1505->1640 (+135, rate 5,00/mnt vs prev 4,71 = 1,06x, velocity GAGAL), "
 f"freeMinted 1634/7777 = 21,0% (INFERENSI bila semua mint gratis, bukan verified; % leg N/A), slot "
 f"TERBUKA, website thyrk.fun TERVERIFIKASI, umur presisi UNVERIFIED - tetap early lead, BELUM strong lead. "
 f"SAKURA: totalSupply 1142->1186 (+44), freeMinted 1176/6000 = 19,6% (<25%), velocity LOLOS "
 f"(1,63/mnt vs prev 1,02 = 1,60x) TAPI TIDAK promosi: free% <25%, slot UNVERIFIED (freeClaimed user "
 f"revert), website GATE FAILED - tetap early lead. "
 f"Age-exclusion baru: TIDAK ADA. MONOLITH deadline umur 2026-11-10 17:32 WIB (belum lewat; 635->638). "
 f"Night Bandits Club (launch terverifikasi 2026-11-07 18:02, ~61,5 jam) + King's Game (launch "
 f"UNVERIFIED) tetap age-watch (semua view free-quota None run ini -> 'belum sold out' tak "
 f"terverifikasi; preseden run 2231/2301/2331/0601/0701). "
 f"binanceai.fun TIDAK BERUBAH (launched=0, failed=1, refund=1, totalShares 3110, tokenClaimed user 0, "
 f"saldo 0) - tidak dilaporkan ulang. "
 f"Track C: sellout/paid-only baru TIDAK ADA yang terverifikasi (NUSA freeMinted 362 flat; FOUNT 1000 "
 f"tetap; BI NIU freeSharesRemaining 0 sudah excluded). "
 f"Scan FAST-FAIL (preflight Ankr 401 x2, 6,2 dtk + 2,2 dtk; outage sejak 2026-11-09 ~13:33 WIB); "
 f"watermark tetap 132512564, gap ke head ~168.600 blok. "
 f"Discovery: Boltbook EN 200 45.918B + ZH 200 46.079B (0 alamat baru vs snapshot+seen+hot; FCAT/JINCHAN/"
 f"THYRK/ADVAGENT sudah dikenal), Sourcify feed 20 (16 baru vs 0701: token sync/ERC-20 polos/"
 f"staking-farm/LayerZero-OApp/hook/launchpad/check-in 0xb023240A agentRegistry tanpa mint+free view/"
 f"craft-box 0xbe8F62f7 agent_id_registry tanpa mint+free view/tax-token 0x28C52880 mint+price+freeview "
 f"tanpa registry - 0 hit S1/S2), sweep ZH + Binance Square (0 proyek baru), Odaily 0, PANews 0, "
 f"bridge 116 kontrak (mtime tak berubah 2026-11-08 18:21 UTC; 8 tidak di snapshot, 7 discarded, sama "
 f"seperti run 0601/0701; 0 promosi). "
 f"TIDAK ADA kandidat/strong lead/early lead baru - run DIAM."
)
s["runNote0731_1110_scan"] = (
 "Run 0731 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs 50 blok (132681136-132681185): FAIL 6,2 dtk "
 "HTTP 401 Unauthorized, retry FAIL 2,2 dtk HTTP 401. Kelanjutan outage Ankr sejak 2026-11-09 ~13:33 "
 "WIB (preflight 0601/0701 juga 401). Scan leg TIDAK dijalankan (amendemen 2026-11-06: "
 "credits-exhausted/paid-gate error -> stop leg run ini, lanjut route lain, tanpa bayar). "
 "Watermark tetap 132512564; gap ke head ~168.600 blok dan tumbuh (milik backfill, backfill OFF). "
 "5c dilewati (tanpa output scan)."
)
s["runNote0731_1110_age_exclusions"] = (
 "Age-exclusion run 0731: TIDAK ADA. MONOLITH belum lewat deadline umur (2026-11-10 17:32 WIB). "
 "Night Bandits Club (launch terverifikasi 2026-11-07 18:02:28 WIB, ~61,5 jam > 48 jam) tetap age-watch: "
 "semua view free-quota None run ini sehingga 'belum sold out' tak terverifikasi (preseden run "
 "2231/2301/2331/0601/0701). King's Game tetap age-watch (launch UNVERIFIED; first-seen 2026-11-07 21:06 "
 "hanya lower bound)."
)

json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"updated={updated} degraded={degraded} skipped_fresher={skipped_fresher} tc_updated={tc_updated}")
print(f"vel_pass={vel_pass}")
print(f"removed={removed}")
print(f"contracts now={len(C)} track_c now={len(TC)}")
