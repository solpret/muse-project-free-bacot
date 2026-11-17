#!/usr/bin/env python3
"""Merge run 2026-11-10 04:01 WIB. Reloads snapshot fresh, applies reread +
triage + discovery findings. Writes snapshot. Scan FAILED (preflight Ankr 401,
5th consecutive) -> watermark NOT advanced. No execution in this run
(no preview/mint/claim).
Velocity baseline: FROZEN 0301 snapshot (run-2026-11-10-0401-baseline-snapshot.json)
so a concurrent 0331 merge cannot corrupt the interval math. Skip-if-fresher:
a contract whose live lastReadBlock is newer than this run's block is skipped.
"""
import json, shutil
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB)
NOW_STR = NOW.strftime("%Y-%m-%d %H:%M WIB")
INTERVAL = 32.9  # (132655642 - 132651254) * 0.45 / 60
NEW_BLOCK = 132655642

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0401-premerge")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
base = json.load(open(f"{BASE}/run-2026-11-10-0401-baseline-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-10-0401-reread.json"))
C = s["contracts"]; TC = s.get("track_c", {}); EX = s.get("excluded", {})
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
        note = f"Run 0401 (blok {NEW_BLOCK}, {NOW_STR}): totalSupply None (degradasi eth_call, nilai lama dipertahankan); "
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
        note = f"Run 0401 (blok {NEW_BLOCK}, {NOW_STR}): totalSupply {prev_sup}->{new_sup} (+{minted if minted is not None else '?'}), velocity {'LOLOS' if vpass else 'GAGAL'}; "
    for k in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if r.get(k) is not None:
            live[k] = r[k]
    if r.get("balanceOf_user") is not None:
        live["balanceOf_user"] = r["balanceOf_user"]
    if r.get("freeClaimed_user") is not None:
        live["freeClaimed_user"] = r["freeClaimed_user"]
    live["lastReadBlock"] = NEW_BLOCK; live["lastReadWib"] = NOW_STR
    live["runNote0401_1110"] = note + f"free={live.get('freeClaimed')}/{live.get('FREE_SUPPLY')}; bal_user={live.get('balanceOf_user')}; status {live.get('status')}."
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
    if r.get("freeMinted") is not None:
        live["freeMinted"] = r["freeMinted"]
    if r.get("totalSupply") is not None:
        live["totalSupply"] = r["totalSupply"]
    live["runNote0401_1110"] = f"Run 0401: freeMinted={live.get('freeMinted')}, totalSupply={live.get('totalSupply')} (blok {NEW_BLOCK})."
    tc_updated += 1

# --- ZENSAI twins: checked-not-agent-shaped (Boltbook front page EN+ZH run 0401) ---
EX["ZENSAI"] = {
    "address": "0x6e9259bda18f42abceb4bec794ac3355004f743f",
    "address2": "0xf9e04cc1b4dc91b3cfd5a30d9717d634acf9c3e9",
    "symbol": "ZSAI", "track": "A", "status": "excluded-not-agent-shaped-2026-11-10",
    "note": "Boltbook front page run 0401 (post lloyd.ai /p/F58f-p_bLkAu, ~04:25 WIB): 'ZENSAI second gate cracked: free mint is 0x67f68fac(0x1, 1); 146/3,333 on both'. Triage run 0401 (blok 132657020): twin contracts IDENTIK - Sourcify NOT verified, code 10.454 byte, registry_bytes FALSE, totalSupply 146/146 (cocok post), MAX_SUPPLY 3333, SEMUA free view revert/null (freeClaimed/freeMinted/FREE_SUPPLY/mintOpen/agentId/agentRegistry/freeLeft/quote/mintPrice/PRICE), owner() = 0x0262e8e5e4584d8ab840fd950a6e2e0a414d4097 (cocok post: same owner). Selector probe 0x67f68fac(1,1) via eth_call dari user: result 0x tanpa revert (konsisten fungsi ada, BUKAN bukti agent-gate). TIDAK agent-shaped (tanpa registry/AgentGate/free-mint evidence konkret; Sourcify-unverified bukan agent-shaped hanya dari bytecode - sesuai body). 146/3333 = 4,4% (jauh di bawah 25%). BUKAN early lead, TIDAK masuk snapshot; log saja. Owner + kedua kontrak TIDAK ada di same-owner-discards.",
}
# --- Roguefall: agent-shaped TERKONFIRMASI tapi AGE-EXCLUDED (hot-leg 0404 Boltbook-new) ---
EX["Roguefall"] = {
    "address": "0x5fe03829a2f94a8ba3906459258b1305f0e68934",
    "symbol": "RFALL", "track": "A", "status": "excluded-age-over-48h-2026-11-10",
    "note": "Hot-leg 0404 Boltbook-new (post ~03:40 WIB: 'Roguefall RFALL, 529/4,000, freeMint() sims clean'; S1=True by ABI names). Triage run 0401 (blok 132657020): REGISTRY() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (registry RESMI - agent-shaped TERKONFIRMASI, meresolusi keraguan run 2026-11-05); totalSupply 661, freeMinted 660, FREE_CAP 2000 (33,0% free), MAX_SUPPLY 4000, paidMinted 1, PRICE/basePrice 0,0005 BNB; canFreeMint(user)=1, claimedFree(user)=0 (slot TERBUKA); owner 0x4e9b1d076fda3605ad63f81a94a8693342a08dba (tidak di discards). TAPI AGE-EXCLUDED: minting sudah live 2026-11-05 06:24 WIB (hot-leg-seen: freeMinted 4 = totalSupply 4 saat itu; Sourcify verifiedAt 2026-11-04T23:28:03Z) -> umur >= ~102 jam > 48 jam; postingan Boltbook hari ini hanya status update, BUKAN fase/batch baru. Velocity/33%/slot TIDAK mengesampingkan age exclusion (preseden Ghostling/Pumpkinfarm review hot-leg 0404). BUKAN early/strong lead, BUKAN kandidat; TIDAK masuk snapshot; TIDAK preview/mint; log saja.",
}
# --- Adventure Agent AI: update reread run 0401 (free crossed 25%, still early lead) ---
if isinstance(C.get("Adventure Agent"), dict):
    aa = C["Adventure Agent"]
    aa["freeMinted"] = 505
    aa["freeLeft"] = 1495
    aa["lastReadBlock"] = NEW_BLOCK; aa["lastReadWib"] = NOW_STR
    aa["freePctNote"] = "505/2000 = 25,25% (reread run 0401, blok 132655642; 459->505, +46) - LEWAT 25% strong-lead TAPI umur masih UNVERIFIED + website masih UNVERIFIED -> BUKAN strong lead, tetap early lead."
    aa["velocityNote"] = "Baseline run 0301: freeMinted 459; run 0401: 505 (+46 dalam interval 32,9 mnt, 1,40/mnt) - velocity belum terhitung (tanpa prev rate yang sah; first run setelah baseline)."
    aa["websiteNote"] = "Situs advagent.xyz ditemukan via tokenURI(1) tapi MASIH TIDAK BISA DIAKSES run 0401 (curl HTTP 000, 0 byte - root + /assets/meta/1.json; run 0301: curl empty reply + text-fetch 403) - website MASIH UNVERIFIED. Metode G nihil run 0301; metode J: ABI tanpa fungsi site/URL; metode H: tidak ada contractURI()."
    aa["runNote0401_1110"] = "Run 0401: freeMinted 459->505 (25,25%, LEWAT 25%) TAPI umur UNVERIFIED + website UNVERIFIED (advagent.xyz curl 000) -> tetap early-lead-reported, BUKAN strong lead, TIDAK preview/mint. Slot tampak terbuka (freeClaimed(user)=0, bal 0)."
# --- Sakura: update reread run 0401 ---
if isinstance(C.get("Sakura"), dict):
    sk = C["Sakura"]
    sk["totalSupply"] = 928; sk["freeMinted"] = 923
    sk["lastReadBlock"] = NEW_BLOCK; sk["lastReadWib"] = NOW_STR
    sk["runNote0401_1110"] = "Run 0401: totalSupply 901->928, freeMinted 896->923 (923/6000 = 15,4%, masih <25%); umur terverifikasi (first mint 01:47 WIB 10 Nov); slot belum terverifikasi; website belum ditemukan -> tetap early-lead-reported, bukan strong lead."
# --- Track-C 0x38491597: still NOT LAUNCHED (re-check run 0401) ---
if isinstance(TC.get("0x38491597"), dict):
    t = TC["0x38491597"]
    t["freeSharesRemaining"] = 767; t["publicFreeRemaining"] = 767
    t["totalShares"] = 10
    t["launched"] = 0; t["launchPending"] = 0; t["saleClockStart"] = 0
    t["lastReadBlock"] = 132657357; t["lastReadWib"] = NOW_STR
    t["runNote0401_1110"] = "Run 0401 re-check (blok 132657357): MASIH BELUM LAUNCH (launched=0, launchPending=0, saleClockStart=0); freeSharesRemaining 768->767, totalShares 9->10 (1 share diklaim pihak lain); freeSharesClaimed(user)=0. Tetap watchlist-only-not-launched, BUKAN lead; TIDAK preview/mint."
# --- YAMA: no change (gate failed definitively; deadline ~15:18 WIB) ---
if isinstance(TC.get("YAMA"), dict):
    TC["YAMA"]["runNote0401_1110"] = "Run 0401: tidak ada perubahan - gate website GAGAL definitif (run 0301, metode L+M); tetap lead-reported-gate-blocked; TIDAK preview/mint; deadline umur 48 jam ~15:18 WIB 2026-11-10."

s["runNote0401_1110"] = (
    f"Run 0401 (2026-11-10 {NOW_STR}): reread 631 kontrak + 91 track_c (blok {NEW_BLOCK}, interval 32,9 mnt; "
    f"reread selesai 809,4 dtk via exec terkelola, tanpa mati tengah jalan; degraded reads={degraded}, skipped-fresher={skipped_fresher}). "
    f"Velocity LOLOS (metode merge, prev rate = currentRatePerMin baseline 0301): {vel_pass if vel_pass else '[]'} - AgentX (+126, ~71x) watchlist-only-age-unverified + website UNVERIFIED + free% UNVERIFIED, TIDAK dipromosikan; MONOLITH (+122, ~46x) early-lead-reported, free% UNVERIFIED + slot UNVERIFIED, TIDAK dipromosikan. "
    "Sold-out baru: []. Free>=25% / >=50% crossing baru: [] (Adventure Agent 459->505 = 25,25% TAPI umur+website unverified -> tetap early lead, bukan strong lead). Slot berubah: []. "
    "ZENSAI twins dicatat excluded-not-agent-shaped (bukan early lead); Roguefall dicatat excluded-age-over-48h (agent-shaped terkonfirmasi tapi umur >=102 jam). "
    "0x38491597 tetap watchlist-only-not-launched (launched=0; free 768->767, totalShares 9->10). "
    "Sakura +27 (901->928, free 923/6000=15,4%, tetap early-lead). "
    "YAMA: tanpa perubahan, gate gagal definitif, deadline umur ~15:18 WIB. "
    "binanceai tetap closed-refund-phase-2026-11-07 (tidak dibaca ulang; pending_claims kosong)."
)
s["runNote0401_1110_scan"] = (
    "Scan run 0401 FAST-FAIL: preflight (head 132655679) Ankr ankr_getLogs "
    "HTTP 401 Unauthorized dalam 8,2 dtk (ke-5 kalinya berturut-turut: run 0001, 0201, 0231, 0301, 0401; outage sejak 2026-11-09 ~13:33 WIB). Watermark TIDAK dimajukan "
    "(tetap 132512564, gap ~143.115 blok); backfill terpisah yang menutup gap. Scan leg gagal cepat sesuai amendemen 2026-11-06; route lain tetap jalan."
)
s["runNote0401_1110_discovery"] = (
    "Discovery run 0401: Boltbook front page en (47.013 byte) + zh (47.223 byte) dibaca langsung ~04:25 WIB; "
    "7 alamat/halaman; baru vs snapshot+seen: ZENSAI twins 0x6e9259bd + 0xf9e04cc1 (post lloyd.ai /p/F58f-p_bLkAu, 146/3,333) + owner 0x0262e8e5 (bukan proyek); "
    "BAHBEAST 0x2ccb3fa9 sudah di snapshot (BAHUANG3, strong-lead-gate-failed-2026-11-09); BOLT 0xBbDd8C77 platform token (non-lead); 0x8269Ea16 chrome footer. "
    "Roguefall 0x5fe03829 dari hot-leg 0404 (Boltbook-new ~03:40 WIB, S1=True) - ditriase run ini: agent-shaped terkonfirmasi (REGISTRY()=registry resmi) TAPI age-excluded. "
    "Sweep web (EN+ZH): tanpa proyek baru - Substack '22 projects' (13 hari), AgentForge/Pixel Fox/PocketDragons/Horus (sold-out/paid/age-excluded, sudah diketahui), "
    "MOLT AGENT free pool habis (sudah diketahui), daftar @congge918 26 Okt (Subsonic Tribe sudah di snapshot; BNBmeme/PixelFox excluded; Laser Agents excluded per body), Believers minted out. "
    "Route 6: Odaily (251.303 byte) + PANews (119.190 byte) tanpa item Agent ID free-mint baru; DappBay tidak dipakai. "
    "Bridge: tidak berubah sejak 8 Nov 18:21 (116 kontrak, 8 tidak ada di snapshot - semua temuan lama Nov 3-8, tanpa promosi). "
    "Hot leg 0404: SILENT (review: 15 promo flags = status lama; 12 perubahan kecil rutin; 0 sale-shape; 5 shape-check timeout carry-over ke run berikut)."
)
s["runNote0401_1110_5a"] = (
    "5a run 0401: feed SEGAR via curl (20 alamat, verifiedAt 21:02-21:24Z = 04:02-04:24 WIB); 10 baru di-shape-check (10 dilewati hot-leg-seen); "
    "0 S1 pass, 0 S2 pass; 5 transport error (Sourcify v2 retry-exhausted: 0x8Da25aCb, 0xfC033C70, 0x439fe0b6, 0x603fC44B, 0x5847aA98) - belum terverifikasi, retry run berikut. "
    "Catatan: script 5a run ini sempat membaca feed 0301 yang usang (bug salin); diperbaiki ke feed segar 0401 sebelum eksekusi - hasil di atas dari feed segar."
)
s["runNote0401_1110_binanceai"] = (
    "binanceai: TIDAK dibaca ulang run 0401 (pending_claims kosong; status closed-refund-phase-2026-11-07). "
    "Bacaan terakhir triage run 0201 blok 132639870: launched()=0, failed()=1, isRefundPhase()=1, totalShares()=3110 - tetap refund, tidak ada perubahan."
)
s["last_run_wib"] = NOW_STR
s["last_run_note"] = s["runNote0401_1110"]
json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGED updated={updated} degraded={degraded} skipped_fresher={skipped_fresher} tc_updated={tc_updated} vel_pass={vel_pass}")
print("NOW:", NOW_STR)
