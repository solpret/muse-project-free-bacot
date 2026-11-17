#!/usr/bin/env python3
"""Merge run 2026-11-10 02:31 WIB. Reloads snapshot fresh, applies reread +
triage + discovery findings. Writes snapshot. Scan FAILED (preflight Ankr 401)
-> watermark NOT advanced. No execution in this run (no preview/mint).
"""
import json, shutil
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB)
NOW_STR = NOW.strftime("%Y-%m-%d %H:%M WIB")
INTERVAL = 50.7  # block 132634589 (01:59 WIB) -> 132641351
NEW_BLOCK = 132641351

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0231-premerge")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-10-0231-reread.json"))
C = s["contracts"]; TC = s.get("track_c", {})
updated = 0; degraded = 0; vel_pass = []
for name, e in C.items():
    r = rr["reread"].get(name)
    if r is None:
        continue
    prev_sup = e.get("totalSupply"); new_sup = r.get("totalSupply")
    if new_sup is None:
        degraded += 1
        note = f"Run 0231 (blok {NEW_BLOCK}, {NOW_STR}): totalSupply None (degradasi eth_call, nilai lama dipertahankan); "
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
            e["previousTotalSupply"] = prev_sup; e["mintedInInterval"] = minted
            e["intervalMinutes"] = INTERVAL; e["currentRatePerMin"] = rate
            e["previousRatePerMin"] = prev_rate; e["velocityRatio"] = ratio
            e["velocityLegPasses"] = vpass
        e["totalSupply"] = new_sup
        note = f"Run 0231 (blok {NEW_BLOCK}, {NOW_STR}): totalSupply {prev_sup}->{new_sup} (+{minted if minted is not None else '?'}), velocity {'LOLOS' if vpass else 'GAGAL'}; "
    for k in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if r.get(k) is not None:
            e[k] = r[k]
    if r.get("balanceOf_user") is not None:
        e["balanceOf_user"] = r["balanceOf_user"]
    if r.get("freeClaimed_user") is not None:
        e["freeClaimed_user"] = r["freeClaimed_user"]
    e["lastReadBlock"] = NEW_BLOCK; e["lastReadWib"] = NOW_STR
    e["runNote0231_1110"] = note + f"free={e.get('freeClaimed')}/{e.get('FREE_SUPPLY')}; bal_user={e.get('balanceOf_user')}; status {e.get('status')}."
    updated += 1

tc_updated = 0
for name, e in TC.items():
    if not isinstance(e, dict):
        continue
    r = rr["track_c"].get(name)
    if r is None:
        continue
    if r.get("freeMinted") is not None:
        e["freeMinted"] = r["freeMinted"]
    if r.get("totalSupply") is not None:
        e["totalSupply"] = r["totalSupply"]
    e["runNote0231_1110"] = f"Run 0231: freeMinted={e.get('freeMinted')}, totalSupply={e.get('totalSupply')} (blok {NEW_BLOCK})."
    tc_updated += 1

# --- SAKURA: EARLY LEAD (Boltbook front page, first-seen this run) ---
C["Sakura"] = {
    "address": "0xF2705A84602369069782624279837A08bdbBf6D6",
    "status": "early-lead-reported-2026-11-10",
    "name": "Sakura", "symbol": "SAKURA", "kind": "ERC721",
    "totalSupply": 854, "totalMinted": 854, "freeMinted": 849,
    "FREE_SUPPLY": 6000, "freeSupplyNote": "6000 dari postingan Boltbook qlp.ai (free pool 6000; FREE_SUPPLY() on-chain revert, jadi angka ini klaim postingan, BUKAN view terverifikasi)",
    "MAX_SUPPLY": 6666, "mintOpen": 1, "balanceOf_user": 0,
    "registry_bytes": True, "code_len": 18932,
    "firstSeenBlock": 132634312, "firstMintWib": "2026-11-10 01:47 WIB",
    "firstSeenSource": "Boltbook front page en+zh run 0231 (post qlp.ai /p/JuKd39eKiH8h 02:29 WIB + rizeiki.ai 01:47 WIB)",
    "lastReadBlock": NEW_BLOCK, "lastReadWib": NOW_STR,
    "xVerified": False, "xHandle": "@sakurashenft (disebut 'official X' di postingan qlp.ai, 63 followers; belum diverifikasi independen)",
    "websiteVerified": False,
    "websiteNote": "Situs disebut di postingan ('the site's button') tapi URL tidak tercetak di postingan; belum ditemukan (metode B/G/H/I: postingan tanpa link, contractURI revert, tokenURI belum dibaca run ini).",
    "launchNote": "First mint TERVERIFIKASI on-chain: tx 0xbfe477a38a9784d2618edd5ffc6bb31cb4363054929bf5ab09fa7e10c995e659, blok 132634312 = 01:47 WIB 2026-11-10, receipt status 1, Transfer dari zero address di kontrak SAKURA (verifikasi run 0231 via eth_getTransactionReceipt). Umur <=48 jam TERVERIFIKASI.",
    "velocityVerified": False, "velocityNote": "Baseline run 0231: totalSupply 854, freeMinted 849 (14,15% dari 6000 klaim postingan); tidak ada rate sebelumnya, velocity belum terhitung.",
    "freePctNote": "849/6000 = 14,15% (FREE_SUPPLY dari klaim postingan, bukan view) - di bawah 25% strong lead. 5 paid mints (854-849). Paid tier 0,001 BNB untuk NFT ke-2 s.d. ke-6 per wallet (per postingan).",
    "mintFn": "mintFree() (0x8ab53447) value 0, clean preview per postingan rizeiki.ai (receipt status 1).",
    "runNote0231_1110": "Run 0231 EARLY LEAD (dilaporkan sekali): agent-shaped (registry bytes TRUE + mintFree + freeMinted 849); first mint terverifikasi 01:47 WIB blok 132634312; free 14,15% (<25% strong lead); slot user belum terverifikasi (freeClaimed(user)/mintedBy revert); website + X discussion belum terverifikasi (X handle @sakurashenft dari postingan). TIDAK PERNAH preview/mint sebagai early lead.",
}
# --- HashHaunts: STRONG LEAD, website gate pending method L ---
C["HashHaunts"] = {
    "address": "0x0ee89b62d0b19C6BF4eDe98aC0542cd604B0E011",
    "status": "strong-lead-gate-pending-L-2026-11-10",
    "name": "HashHaunts", "symbol": "HASHHAUNTS", "kind": "ERC721",
    "totalSupply": 750, "freeClaimed": 735, "FREE_SUPPLY": 855, "freePctVerified": 85.96,
    "MAX_SUPPLY": 1222, "PRICE": 50000000000000, "FREE_PER_WALLET": 1, "MAX_PER_WALLET": 50,
    "mintOpen": 1, "agentIdRequired": 1, "AGENT_ID": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "quote_user_1": 0, "freeFor_user_1": 1, "freeLeft_user": 1, "freeUsed_user": 0,
    "mintedBy_user": 0, "balanceOf_user": 0,
    "owner": "0x60575d8321ac6533aeb32cf2ee14586de6690aea",
    "registry_bytes": True, "sourcify": "exact_match",
    "verifiedAt": "2026-11-09T19:06:23Z",
    "firstSeenWib": "2026-11-10 02:14 WIB",
    "firstSeenSource": "Sourcify recently-verified feed (hot-leg-seen first_seen 02:14:38 WIB; run 0201 5a S1+S2 pass; triage3 run 0231 konfirmasi independen S1=True S2=True)",
    "lastReadBlock": NEW_BLOCK, "lastReadWib": NOW_STR,
    "xVerified": False, "velocityVerified": False, "websiteVerified": False,
    "launchNote": "Umur TERVERIFIKASI <=48 jam sebagai batas: kontrak pertama muncul di feed Sourcify recently-verified 02:06 WIB hari ini (verifiedAt 2026-11-09T19:06:23Z), pertama dicatat hot leg 02:14 WIB; mint aktif (735/855 free claimed per 02:50 WIB); tidak ada bukti launch lebih awal (tidak ada di feed poll / snapshot sebelumnya). First-mint event belum dikoroborasi langsung (Ankr getLogs 401). Launch tidak mungkin mendahului deployment; deployment <= verifikasi 02:06 WIB.",
    "websiteNote": "Gate metode (A) pencarian alamat kontrak nihil; (B) site:boltbook.fun HashHaunts nihil; (G) pencarian nama nihil; (H) contractURI base64 JSON tanpa external_link; (I) tokenURI(1) tanpa external_url (art on-chain SVG); (J) ABI 39 fungsi tanpa fungsi site/URL; (K) GitHub butuh auth (limitasi dinyatakan); (M) site:vercel/pages/surge/deed nihil; (E) owner TIDAK ada di same-owner-discards (60 entri). (L) BscScan token-info via live browser MASIH BERJALAN saat merge (task 86599616) - hasil menyusul.",
    "runNote0231_1110": "Run 0231 STRONG LEAD (3 kaki lolos: umur terverifikasi <=48 jam sbg batas + free 735/855=85,96% + slot user terbuka quote=0/freeLeft=1). KOREKSI hot-leg 0214 ('0 sale-shape'): triase independen run 0231 (ABI Sourcify + on-chain) membuktikan S1=True S2=True + NFT-shaped + registry bytes. Website gate BELUM lolos (metode A/B/G/H/I/J/K/M nihil; L pending) -> TIDAK preview/mint run ini. Bila L menemukan situs terverifikasi yang mencetak kontrak persis -> strong-lead direct mint (audit + preview bersih dulu); bila L kosong -> laporkan sekali sebagai strong lead + alasan blokir.",
}
# --- Deltavane: watchlist-only, age unverified ---
C["Deltavane"] = {
    "address": "0xfcfdc06c85877d3f2d316595882e1aa9e7f2eebc",
    "status": "watchlist-only-age-unverified-2026-11-10",
    "name": "Deltavane", "symbol": "DLVN", "kind": "ERC721",
    "totalSupply": 1414, "freeClaimed": 1410, "FREE_SUPPLY": 1607, "freePctVerified": 87.74,
    "MAX_SUPPLY": 2297, "mintOpen": 1, "balanceOf_user": 0, "mintedBy_user": 0, "freeUsed_user": 0,
    "registry_bytes": True, "code_len": 25736,
    "firstSeenBlock": 132644685, "firstSeenSource": "Boltbook front page en run 0231 (post quyennuong.ai, ~02:55 WIB)",
    "lastReadBlock": 132644685, "lastReadWib": NOW_STR,
    "xVerified": False, "velocityVerified": False, "websiteVerified": False,
    "launchNote": "Launch time UNVERIFIED: postingan menyebut '+151 in 39h' (minting berjalan ~39 jam) tapi bukan waktu launch terverifikasi; first-mint event belum dikoroborasi (Ankr getLogs 401). Bukan early lead (minting sudah 1414, bukan first-seen minting run ini).",
    "runNote0231_1110": "Run 0231 watchlist-only: agent-shaped (registry bytes TRUE + free views + deskripsi contractURI 'gated to .ai Agent ID holders'); free 1410/1607=87,74%; slot user tampak terbuka (mintedBy 0, freeUsed 0, bal 0) tapi quote(user) belum terverifikasi (butuh ABI); umur UNVERIFIED; website/X unverified. TIDAK dilaporkan sebagai lead; TIDAK preview/mint.",
}
# --- Coracle + PixelFox: sold out, checked-not-lead (triage run 0201, dicatat run 0231) ---
C["Coracle"] = {
    "address": "0x2FCefA216dA37751E102399aCbe1dCC86Dc96eCf",
    "status": "checked-not-lead-sold-out-2026-11-10",
    "name": "Coracle", "kind": "ERC721",
    "totalSupply": 10000, "MAX_SUPPLY": 10000, "mintOpen": 1, "mintPrice": 500000000000000,
    "balanceOf_user": 0,
    "lastReadBlock": 132641640, "lastReadWib": "2026-11-10 02:3x WIB",
    "runNote0231_1110": "Triage run 0201 (dicatat run 0231): totalSupply 10000 = MAX_SUPPLY 10000 -> SOLD OUT; free views (freeClaimed/freeMinted/FREE_SUPPLY/freeLeft/freeFor) semua revert; mintPrice 0,0005 BNB. BUKAN lead; tidak dilaporkan; tidak masuk watchlist aktif.",
}
C["PixelFox"] = {
    "address": "0x9134ae94ab0739cf0e0f4f5e9cacfa5e1d029b0c",
    "status": "checked-not-lead-sold-out-2026-11-10",
    "name": "PixelFox", "kind": "ERC721",
    "totalSupply": 3333, "MAX_SUPPLY": 3333, "balanceOf_user": 0, "mintedBy_user": 0,
    "owner": "0x90541008777137975601623729234620922977116487299",
    "lastReadBlock": 132641640, "lastReadWib": "2026-11-10 02:3x WIB",
    "runNote0231_1110": "Triage run 0201 (dicatat run 0231): totalSupply 3333 = MAX_SUPPLY 3333 -> SOLD OUT; free views semua revert. Konfirmasi Binance Square (post 2026-10-25): first NFT free, total 3.333. BUKAN lead; tidak dilaporkan.",
}

s["runNote0231_1110"] = (
    f"Run 0231 (2026-11-10 {NOW_STR}): reread 625 kontrak + 90 track_c (blok {NEW_BLOCK}, interval 50,7 mnt). "
    "Velocity LOLOS: AGENT CORE (+104, 3,38x - promotion-discarded-same-owner, TIDAK dipromosikan), "
    "PilotBoarding (+70, 43,27x - watchlist-only-age-unverified + tanpa website + bukan agent-shaped, TIDAK dipromosikan), "
    "Rookling (+20, 12,36x - age-excluded 2026-11-06, TIDAK dipromosikan). "
    "Sold-out baru: []. Free>=25% / >=50% crossing baru: []. Slot berubah: []. "
    "1 EARLY LEAD BARU: SAKURA (dilaporkan sekali). 1 STRONG LEAD BARU: HashHaunts (gate website pending metode L, TIDAK preview/mint run ini). "
    "Deltavane BARU watchlist-only-age-unverified. Coracle + PixelFox BARU checked-not-lead-sold-out (triage 0201). "
    "WNO tetap watchlist-only-website-gate-failed (recheck Boltbook 02:25 WIB: 275/3000 share; gate tetap gagal, tidak dilaporkan ulang). "
    "binanceai tetap refund (triage 0201 blok 132639870: launched 0, failed 1, isRefundPhase 1; pending_claims kosong)."
)
s["runNote0231_1110_scan"] = (
    "Scan run 0231 FAST-FAIL (preflight 13,2 dtk, head 132641542): Ankr ankr_getLogs HTTP 401 Unauthorized "
    "(ke-3 kalinya berturut-turut: run 0001, 0201, 0231). Watermark TIDAK dimajukan (tetap 132512564, gap ~129.000 blok); "
    "backfill terpisah yang menutup gap. Scan leg gagal cepat sesuai amendemen 2026-11-06; route lain tetap jalan."
)
s["runNote0231_1110_discovery"] = (
    "Discovery run 0231: Boltbook front page en (44.516 byte) + zh (43.228 byte) dibaca langsung 02:37 WIB; "
    "15 alamat per halaman; 2 baru vs seen+snapshot: SAKURA 0xF2705A84 (EARLY LEAD) + 0xbfe477a3 (TX HASH, bukan kontrak). "
    "2 alamat baru hot-leg 0214 sudah ditriase run ini: 0xb46093 (kontrak Elysium chain 99901, bukan BSC) + 0x6fca4b (tx hash, code_len 0) - keduanya BUKAN lead. "
    "Sourcify feed 02:37 WIB: 20 alamat, 12 baru, 0 sale-shape (5a). "
    "Sweep web (EN+ZH): Horus AI Phase 1 sold out 2.000/2.000 + soulbound (bukan kandidat; tanpa alamat kontrak di sumber, tidak masuk snapshot); "
    "MOLT AGENT free pool habis (sudah diketahui); tidak ada proyek baru lain. "
    "Route 6: Odaily (252.057 byte) + PANews (118.981 byte) tanpa item Agent ID free-mint baru (hanya kata 'Binance' generik); DappBay tidak dipakai (tidak ada proyek yang butuh cek gate). "
    "Bridge: 116 kontrak, 8 tidak ada di snapshot (semua temuan lama Nov 3-8, ERC-20 paid/1-entity, 1 same-owner-discarded) - tidak ada promosi."
)
s["runNote0231_1110_5a"] = (
    "5a run 0231: feed 20 alamat (verifiedAt 19:00-19:36 UTC); 12 baru di-shape-check, semua S1=False S2=False; "
    "8 sudah hot-leg-seen (termasuk HashHaunts 0x0ee89b62 - dilewati 5a, tapi triage3 independen membuktikan S1=True S2=True + NFT-shaped + registry bytes; "
    "koreksi atas klaim hot-leg 0214 '0 sale-shape'). 0 track-C lead baru dari feed."
)
s["runNote0231_1110_binanceai"] = (
    "binanceai: TIDAK dibaca ulang run 0231 (pending_claims kosong; status closed-refund-phase-2026-11-07). "
    "Bacaan terakhir triage run 0201 blok 132639870: launched()=0, failed()=1, isRefundPhase()=1, totalShares()=3110, tokenClaimed_user=0, tokenBalance_user=0 - tetap refund, tidak ada perubahan."
)
s["last_run_wib"] = NOW_STR
s["last_run_note"] = s["runNote0231_1110"]
json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGED updated={updated} degraded={degraded} tc_updated={tc_updated} vel_pass={vel_pass}")
print("NOW:", NOW_STR)
