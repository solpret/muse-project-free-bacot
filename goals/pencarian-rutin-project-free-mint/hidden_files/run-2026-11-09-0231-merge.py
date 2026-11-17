#!/usr/bin/env python3
"""Merge run 2026-11-09 02:31 WIB. Reloads snapshot fresh, applies reread +
triage + scan findings on top. Writes snapshot + seen file + scan-state watermark
(ADVANCED to head scanned this run: backfill DISABLED, watermark now owned by
this job per body rule; run 0131 did not advance because it was backfill-owned)."""
import json, shutil
from datetime import datetime, timezone, timedelta
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB)
NOW_STR = NOW.strftime("%Y-%m-%d %H:%M WIB")
INTERVAL = 31.40  # block 132445220 ts 02:03:07 -> block 132449407 ts 02:34:31 WIB

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0231-premerge")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-09-0231-reread.json"))
C = s["contracts"]; TC = s.get("track_c", {})
NEW_BLOCK = rr.get("block")
updated = 0; degraded = 0; vel_pass = []
for name, e in C.items():
    r = rr["reread"].get(name)
    if r is None:
        continue
    prev_sup = e.get("totalSupply"); new_sup = r.get("totalSupply")
    if new_sup is None:
        degraded += 1
        note = f"Run 0231 (blok {NEW_BLOCK}, 02:03 WIB): totalSupply None (degradasi eth_call, nilai lama dipertahankan); "
    else:
        minted = None; rate = None; ratio = None; vpass = False
        if prev_sup is not None:
            minted = new_sup - prev_sup
            rate = minted / INTERVAL
            prev_rate = float(e.get("currentRatePerMin") or e.get("ratePerMin") or 0) or 0.0
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
        note = f"Run 0231 (blok {NEW_BLOCK}, 02:03 WIB): totalSupply {prev_sup}->{new_sup} (+{minted if minted is not None else '?'}), velocity {'LOLOS' if vpass else 'GAGAL'}; "
    for k in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if r.get(k) is not None:
            e[k] = r[k]
    if r.get("balanceOf_user") is not None:
        e["balanceOf_user"] = r["balanceOf_user"]
    e["lastReadBlock"] = NEW_BLOCK; e["lastReadWib"] = "2026-11-09 02:34 WIB"
    e["runNote0231_1109"] = note + f"free={e.get('freeClaimed')}/{e.get('FREE_SUPPLY')}; bal_user={e.get('balanceOf_user')}; status {e.get('status')}."
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
    e["runNote0231_1109"] = f"Run 0231: freeMinted={e.get('freeMinted')}, totalSupply={e.get('totalSupply')} (blok {NEW_BLOCK})."
    tc_updated += 1

# --- Meow Cards: EARLY LEAD (first-seen via Sourcify feed, agent-shaped, first mint verified) ---
C["Meow Cards"] = {
    "address": "0xb8164afefc53910D7A74cEcE15A60a9e0C86089e",
    "status": "early-lead-2026-11-09",
    "name": "Meow Cards", "symbol": "MEOWC", "kind": "ERC721",
    "totalSupply": 3, "totalMinted": 3, "totalCards": 24, "MAX_SUPPLY": 10000,
    "MAX_PER_WALLET": 20, "remaining": 9997, "nextTokenId": 4,
    "freeClaimed": None, "FREE_SUPPLY": None, "firstFreeUsed_user": 0,
    "mintedByWallet_user": 0, "balanceOf_user": 0,
    "firstSeenBlock": 132446691, "firstMintWib": "2026-11-09 02:14:09 WIB",
    "lastReadBlock": 132449375, "lastReadWib": "2026-11-09 02:48 WIB",
    "xVerified": False, "velocityVerified": False, "websiteVerified": False,
    "launchNote": "First mint terverifikasi on-chain blok 132446691 = 2026-11-09 02:14:09 WIB (timestamp blok via dataseed eth_getBlockByNumber, BUKAN Ankr); KOREKSI vs walkback awal run ini yang berhenti di chunk pertama dan salah menyimpulkan 132449926/02:38:25 - walkback mendalam job backfill-followup konkuren (132446388-132449375) menemukan mint pertama di 132446691. Usia peluncuran TERVERIFIKASI <=48 jam (first mint ~02:14 WIB hari ini). Ditemukan via feed Sourcify recently-verified (verifiedAt 2026-11-08T19:20:10Z = 02:20 WIB).",
        "baselineNote": "EARLY lead dilaporkan sekali run 0231 (2026-11-09). Agent-shaped TERKONFIRMASI: Sourcify exact_match (44 fns); agentRegistry() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F persis (baca langsung); mint + priceOf/refPriceOf + free view firstFreeUsed + isAgent; owner 0x077984a60a39a24e8f5b04466d52a2bbbb227e9d, TIDAK ada di same-owner-discards (12 owner terdaftar, dicek). Harga: priceOf(user,0,1)=0 (kartu pertama gratis menurut baca), priceOf(user,1,1)=0,00035 BNB, refPriceOf(1)=0,002 BNB, PRICE_TIER_1 0,00035 / TIER_2 0,00065 BNB. Free% UNVERIFIED: tidak ada free-pool counter (FREE_SUPPLY/freeLeft/freeClaimed total absen; firstFreeUsed hanya bool per-user; remaining 9997 = MAX-totalSupply, bukan pool gratis) - BUKAN strong lead, BUKAN kandidat. Website UNVERIFIED: tokenURI(1)/(2) menunjuk https://meow-cards.pages.dev/metadata/*.json (domain proyek, metode I) - TAPI isi situs belum berhasil dibaca run ini (browser.open gagal fetch, tanpa status HTTP) sehingga belum terverifikasi apakah situs mencetak kontrak persis; domain dicatat sebagai petunjuk untuk run berikut, BUKAN bukti website. X UNVERIFIED. Slot user terbuka menurut baca (firstFreeUsed(user)=0, mintedByWallet(user)=0, balanceOf(user)=0) - BUKAN preview-verified (early lead tidak pernah di-preview/di-mint).",
    "runNote0231_1109": "Run 0231: ditambahkan sebagai early-lead (dilaporkan sekali).",
}

# --- seen file: append scan contracts not yet seen ---
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
sc = json.load(open(f"{BASE}/onchain-scan-2026-11-09-0231.json"))
added = 0
for c in sc.get("contracts", []):
    a = (c.get("address") or "").lower()
    if a and a not in seen.get("contracts", {}):
        seen.setdefault("contracts", {})[a] = c.get("first_block") or sc.get("from_block")
        added += 1
seen.setdefault("_meta", {})["note_0231"] = (
    "Run 0231: scan FULL 132448515-132449514 (partial=false, 40 Ankr calls, 0 error, 111 NFT + 205 ERC-20-mint); "
    f"{added} first-seen appended ke seen['contracts'] (0 truly new vs seen+snapshot; Meow Cards first-mint 132449926 added manually from feed leg). "
    "Skipped gap 132446388-132448430 (2043 blok, backfill OFF); watermark DIMAJUKAN 132446387 -> 132449514.")
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)

# --- top-level run note ---
s["last_run"] = "0231"
s["last_run_wib"] = NOW_STR
s["last_run_note"] = (
    f"Run 0231 (02:31 WIB 9 Nov - {NOW_STR}): re-read blok {NEW_BLOCK} (02:34:31 WIB, interval 31,40 mnt vs blok 132445220 02:03:07 WIB): "
    f"{updated} kontrak + {tc_updated} track_c, 0 batch_fail, {degraded} totalSupply=None degraded (nilai lama dipertahankan, bukan nol). "
    f"Velocity strict: {len(vel_pass)} lolos {vel_pass} - Golden Agents +35 (1,11/mnt) velocity GAGAL (rate sebelumnya dari burst 58->118 jauh lebih tinggi, rasio <1,5x) - tetap early lead; Dragon Agent +26 (0,83/mnt vs prev 1,19 = 0,70x) velocity GAGAL - tetap early lead; Alchemister +2 velocity GAGAL. "
    "Scan leg FULL (pre-flight OK 11,6 dtk, head 132449430, 1000 logs/50 blok; window 132448515-132449514, 1000 blok cap, 40 Ankr calls, 0 error, partial=false; 111 NFT (109 ERC721 + 2 ERC1155) + 205 ERC-20-mint; skipped gap 132446388-132448430 (2043 blok, backfill OFF); watermark DIMAJUKAN 132446387 -> 132449514 (backfill dinonaktifkan, watermark kini milik job ini per body). "
    "Sourcify feed: 5 baru sejak hot-leg 0229 (0x4Ed5, 0xE202, 0x15ee, 0x5A1E, 0xb816 Meow Cards) - 0x4Ed5 agent+mint+quote tanpa free view (bukan S1/S2); 0xE202/0x15ee/0x5A1E tanpa mint (bukan sale-shape); 0xb816 = Meow Cards, agent-shaped NFT (mint + priceOf + firstFreeUsed + agentRegistry; hot-leg strict check: S1=False karena tanpa fungsi bernama 'quote' - BUKAN track-C lead) -> EARLY LEAD. 5c: 2 baru dicek (0xac05 Sourcify 404, 0xB0b8 verified tapi tanpa mint/free/quote/agent), 0 hit S1/S2; 23 sudah dicek. "
    "Boltbook EN+ZH ~02:35 WIB: Ringgent 'BARU' = RE-FIND age-excluded (first mint 2026-11-04); BONK AGENT Collector Card = bukan agent-shaped (sudah run 0131); Gryphlume recheck (sudah age-excluded run 0101, first mint <=2026-11-02 ~13:30 WIB, ~164+ jam); GLOOP cooling (+71/76 mnt, totalMinted 3.024-3.032); BAHUANG2 recheck (free 1.152/3.000, gate-blocked, sudah dilaporkan); NIGHT flat 9.431/10.000 (age-excluded); AGENT DOSSIER 0xac3f BARU di Boltbook (348/1.500, freeLeft 1.152) - owner() 0x11038f4a TERKONFIRMASI di same-owner-discards -> SAME-OWNER DISCARD, tidak dipromosikan/dilaporkan, tidak masuk snapshot (baca segar run ini: totalSupply 360, freeLeft 1140). "
    "EARLY LEAD BARU: Meow Cards (MEOWC) 0xb8164afefc53910D7A74cEcE15A60a9e0C86089e (agentRegistry persis, first mint blok 132446691 = 02:14:09 WIB - dikoreksi dari 02:38:25 salah walkback awal; totalSupply 3/10.000, firstFreeUsed(user)=0, priceOf(user,0,1)=0) - free% UNVERIFIED (tanpa pool counter), website UNVERIFIED (tokenURI menunjuk meow-cards.pages.dev tapi isi situs gagal dibaca run ini), X UNVERIFIED - dilaporkan sekali sebagai EARLY, masuk snapshot, TIDAK di-preview/di-mint. "
    "HIVE Agents: flat 1256, balanceOf(user)=1 (minted-by-user 2026-11-02, token #808) - DIPERTAHANKAN di snapshot sebagai holding yang sudah di-mint (grandfathered), BUKAN kandidat watchlist aktif; aturan umur 48 jam menggugurkan kandidat, bukan menghapus catatan holding yang sudah dimiliki; tidak ada fase/batch mint baru (flat, tidak ada mint baru). Tidak dilaporkan ulang. "
    "NUSA track_c freeMinted 249->251 (lead sudah dilaporkan, gate FAILED - tanpa laporan ulang). Binanceai: tetap refund phase (launched=0, failed=1, isRefundPhase=1, totalShares 3110, baca segar run ini) - sudah dilaporkan sekali + dihapus dari tracking. Bridge: 116 kontrak, 0 baru (8 di luar snapshot sama seperti run 0101/0131, 1 same_owner_discarded). "
    "Web sweep EN+ZH + route 6: 0 kandidat baru (HOPKIN 0x2728 sudah di snapshot watchlist-only; WHALE-B sudah di snapshot; NOVRA track_c pool habis; AGENT MAO paused; Ptah soulbound, mint tutup 8 Nov; Periodic Lab sudah di snapshot). Odaily + PANews 0 penyebutan Agent ID/free mint. "
    "0 kandidat, 0 strong lead baru, 1 early lead baru (Meow Cards), 0 auto-mint.")
s["runNote0231_1109"] = s["last_run_note"]
# --- scan-state watermark: advance to head scanned (body rule; backfill OFF) ---
st = json.load(open(f"{BASE}/onchain-scan-state.json"))
st["last_scanned_block"] = 132449514
st["last_scan_window_from"] = 132448515
st["last_scan_window_to"] = 132449514
st["last_scan_wib"] = "run 2026-11-09 0231"
st["ankr_calls"] = 40
st["errors"] = []
st["nft_contracts"] = 111
st["erc20_mint_contracts"] = 205
st["skipped_gap"] = "132446388-132448430 (2043 blok, backfill OFF)"
st["note_0231"] = ("Watermark dimajukan 132446387 -> 132449514 sesudah scan sukses run 0231 (partial=false, 0 error). "
    "Run 0131 tidak memajukan karena watermark saat itu milik backfill; backfill DINONAKTIFKAN user 2026-11-08, watermark kini milik job ini.")
json.dump(st, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)
# --- hot-leg seen dedupe: 5 feed contracts + Meow Cards ---
hl = json.load(open(f"{BASE}/hot-leg-seen.json"))
for _a, _n in {
  "0x4Ed5ff4076eF87839ed38baDe78c085c6Bd9c7b3": "run 0231 feed-shape: verified, agent+mint+quote tanpa free view - bukan S1/S2",
  "0xE202FE765289F6dc90A05c9248AAF7d92D928A4A": "run 0231 feed-shape: verified, tanpa mint - bukan sale-shape",
  "0x15eebb55d9A0446B2D76104237C09aB97E1a3318": "run 0231 feed-shape: verified, tanpa mint - bukan sale-shape",
  "0x5A1EAE87d3cFa94C72c294D539F6714e3feABbA5": "run 0231 feed-shape: verified, tanpa mint - bukan sale-shape",
  "0xb8164afefc53910D7A74cEcE15A60a9e0C86089e": "run 0231 EARLY LEAD Meow Cards - sudah dilaporkan sekali run 0231, jangan laporkan ulang",
}.items():
    hl.setdefault(_a, {"first_seen_wib": "2026-11-09 02:31 WIB", "note": _n})
json.dump(hl, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
removed = []
print(f"MERGE DONE updated={updated} degraded={degraded} tc={tc_updated} vel_pass={vel_pass} removed={removed} seen_added={added}")
print("contracts now:", len(s["contracts"]), "track_c now:", len(s["track_c"]))
