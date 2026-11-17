#!/usr/bin/env python3
"""Merge run 2231 reread + 5a + binanceai + grove + JINMA triage into onchain-snapshot.json.
Fresh script for run 2231 (the copied 2201 merge was stale). INTERVAL 30.75 min
(blocks 132606907 -> 132611007, timestamps 1794237433 -> 1794239278).
Reports due this run: NONE (no new candidate/strong lead/early lead/track-C lead/track-B change/sold-out).
No execution. Read-only except snapshot."""
import json, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
INTERVAL = 30.75
BLOCK = 132611007
NOW_WIB = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-09-2231-reread.json"))
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})
n_upd = 0
vel_pass = []
for name, v in contracts.items():
    r = rr.get("reread", {}).get(name)
    if not isinstance(r, dict):
        continue
    prev_ts = v.get("totalSupply")
    new_ts = r.get("totalSupply")
    minted = None
    if isinstance(prev_ts, int) and isinstance(new_ts, int):
        minted = new_ts - prev_ts
        prev_rate = v.get("currentRatePerMin")
        rate = minted / INTERVAL
        ratio = (rate / prev_rate) if (isinstance(prev_rate, (int, float)) and prev_rate > 0) else None
        v["previousTotalSupply"] = prev_ts
        v["mintedInInterval"] = minted
        v["intervalMinutes"] = INTERVAL
        v["currentRatePerMin"] = round(rate, 4)
        v["previousRatePerMin"] = prev_rate
        v["velocityRatio"] = (round(ratio, 2) if ratio is not None else None)
        v["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        if v["velocityLegPasses"]:
            vel_pass.append((name, minted, round(ratio, 2)))
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
              "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if r.get(k) is not None:
            v[k] = r[k]
    fs = v.get("FREE_SUPPLY")
    fcl = v.get("freeClaimed")
    if isinstance(fs, int) and fs and isinstance(fcl, int):
        v["freePctVerified"] = round(100.0 * fcl / fs, 2)
    elif isinstance(fs, int) and fs and isinstance(v.get("freeMinted"), int):
        v["freePctVerified"] = round(100.0 * v["freeMinted"] / fs, 2)
    v["lastReadBlock"] = BLOCK
    v["lastReadWib"] = NOW_WIB
    v["runNote2231_1109"] = (f"Run 2231 (blok {BLOCK}, interval {INTERVAL} mnt vs run 2201): "
        f"{prev_ts}->{new_ts} (+{minted if minted is not None else 'n/a'}), "
        f"velocity {'LOLOS' if v.get('velocityLegPasses') else 'GAGAL'}; "
        f"free={v.get('freeClaimed')}/{v.get('FREE_SUPPLY')} fm={v.get('freeMinted')}; "
        f"bal_user={v.get('balanceOf_user')}; status {v.get('status')}.")
    n_upd += 1
n_tc = 0
for name, v in track_c.items():
    r = rr.get("track_c", {}).get(name)
    if not isinstance(r, dict) or not isinstance(v, dict):
        continue
    if r.get("totalSupply") is not None:
        v["totalSupply"] = r["totalSupply"]
    if r.get("freeMinted") is not None:
        v["freeMinted"] = r["freeMinted"]
    if r.get("freeSharesRemaining") is not None:
        v["freeSharesRemaining"] = r["freeSharesRemaining"]
    if r.get("balanceOf_user") is not None:
        v["balanceOf_user"] = r["balanceOf_user"]
    v["lastReadBlock"] = BLOCK
    v["lastReadWib"] = NOW_WIB
    n_tc += 1
# --- PIXEL MONSTERS: early lead, still below strong-lead legs ---
px = contracts.get("PIXEL MONSTERS")
if isinstance(px, dict):
    px["freePctVerified"] = round(100.0 * px["freeMinted"] / 2000, 2) if isinstance(px.get("freeMinted"), int) else px.get("freePctVerified")
    px["runNote2231_1109"] = ("Run 2231: early lead tetap (dilaporkan run 2131). totalSupply 196->310 (+114, 3,52/mnt, "
        "ratio 0,84 vs prev -> velocity GAGAL); freeMinted 194->308/2000 = 15,4% (masih <25% strong lead); "
        "slot user terbuka (freeClaimed user 0, bal 0); mintOpen 1. Tetap early lead; TIDAK preview/mint.")
# --- JINMA: already minted by user via hot-leg 20:34 WIB; register in track_c so later runs don't re-triage ---
track_c["JINMA"] = {
    "sale": "0x8553e7033C06fC69B7508d58507b75242cF86EC4",
    "token": "0xe4517e6718b24d5725956ac7a90686592a7b1539",
    "name": "JINMA",
    "status": "minted-by-user-2026-11-09",
    "mintTx": "0x6a1896f26b61db371bce2dea1bcc115452b9c4ce73fd80fc0c8e41b27bccd0a4",
    "mintBlock": 132595827,
    "mintGas": 195418,
    "saleShape": "PASS (S1): mint(uint256,address) + quote + freeSharesRemaining/freeSharesClaimed/publicFreeRemaining + AGENT_ID_REGISTRY = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, Sourcify exact_match (verifiedAt 2026-11-09T13:32:49Z)",
    "totalShares": 1380,
    "FREE_SHARES": 2222,
    "freeSharesRemaining": 842,
    "publicFreeRemaining": 842,
    "totalPaidShares": 0,
    "saleClockStart": 0,
    "TOKENS_PER_SHARE": 50000000000000000000000000,
    "PRICE_PER_SHARE": 2000000000000000,
    "MAX_SHARES": 9999,
    "mintingOpen": True,
    "poolOpen": False,
    "owner": "0x918e4d71337b117c1baee0729d7f371c1fbddc93",
    "owner_in_discards": False,
    "userSlot": {"hasAgentId": True, "freeSharesClaimed": 1, "paidQuotaOf": 10, "balanceOf": 50000000000000000000000000},
    "mintNote": "Hot-leg run 2026-11-09 20:34 WIB: TRACK-C LEAD DIRECT MINT BERHASIL, 1 share gratis = 50.000.000 JINMA (balance agent 0 -> 50.000.000, terverifikasi on-chain 20:58 WIB). Tx 0x6a1896f26b61db371bce2dea1bcc115452b9c4ce73fd80fc0c8e41b27bccd0a4, blok 132595827, gas 195418, receipt 1. Website gate LOLOS saat itu (jinma.pages.dev llms.txt + homepage mencetak kedua kontrak persis). Transfer token TERKUNCI sampai pool dibuka; pair() masih zero saat mint. Pending swap entri #12 (no_pair + transfer terkunci).",
    "website": "https://jinma.pages.dev/",
    "lastReadBlock": 132611754,
    "lastReadWib": NOW_WIB,
    "runNote2231_1109": ("Run 2231: JINMA baru muncul di front page Boltbook (post bangwi.ai /p/j8nsVLKZbbhH, ~22:31 WIB) TAPI SUDAH DIMILIKI user: "
        "triase segar run ini (blok 132611754) - freeSharesClaimed(user)=1, TOKEN balanceOf(user)=50.000.000 JINMA (= 1 share x TOKENS_PER_SHARE), "
        "totalShares 1380/9999, freeSharesRemaining 842/2222, totalPaidShares 0, saleClockStart 0. Konsisten dengan mint hot-leg 20:34 WIB yang sudah dilaporkan 20:58 WIB. "
        "BUKAN lead baru; TIDAK dilaporkan ulang; TIDAK preview/mint. Didaftarkan di track_c agar run berikut tidak men-triase ulang."),
}
# --- 0x4Bc1A172 sale: still not open ---
sale = track_c.get("0x4Bc1A172-sale")
if isinstance(sale, dict):
    sale["runNote2231_1109"] = ("Run 2231: sale MASIH BELUM BUKA (SALE_START 2026-11-10 12:00 WIB); freeMinted 0, totalSupply null (revert saat baca, sale belum buka). "
        "Status tetap watchlist-only-not-open; dicek ulang saat buka; TIDAK dilaporkan.")
snap["last_run"] = 2231
snap["last_run_wib"] = NOW_WIB
snap["last_run_note"] = ("Run 2231: 620 kontrak + 86 track_c re-read (blok 132611007, 685,6 dtk, interval 30,75 mnt vs run 2201); "
    "0 kandidat/strong lead/early lead/track-C baru; 0 sold-out baru; PIXEL MONSTERS tetap early lead (310 total, free 308/2000=15,4%); "
    "JINMA (baru via Boltbook) ternyata SUDAH dimint user via hot-leg 20:34 WIB - terverifikasi konsisten, didaftarkan di track_c, tidak dilaporkan ulang; "
    "5a: 17 alamat baru feed Sourcify, 0 S1/S2 hit; scan fast-fail Ankr 401 (preflight 9,2 dtk, head 132611361; watermark 132512564, gap ~98.797 blok); "
    "binanceai tetap refund; Grove freeOpen=0.")
snap["runNote2231_1109"] = snap["last_run_note"]
snap["runNote2231_1109_scan"] = ("Run 2231 route 4: SCAN FAST-FAIL - Ankr pre-flight HTTP 401 Unauthorized (9,2 dtk, head 132611361); "
    "outage sejak ~13:33 WIB 2026-11-09 (~9,5 jam); watermark TETAP 132512564, gap ~98.797 blok ke head saat preflight. "
    "Backfill bukan tugas job ini; reconnect Ankr belum terverifikasi pulih.")
snap["runNote2231_1109_binanceai"] = ("Run 2231 track-B: binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, "
    "totalShares=3110, tokenClaimed(user)=0, TOKEN balanceOf(user)=0 (probe dataseed, blok 132611434). "
    "Status closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang.")
snap["runNote2231_1109_5a"] = ("Run 2231 route 5a: 17 alamat BARU feed Sourcify (verifiedAt 15:25-15:46Z; 8 sisanya sudah hot-leg-seen), 0 S1/S2 hit "
    "(semua free=[] - tanpa free-share view). 5c: tidak ada output scan baru (scan fast-fail sejak 13:33); tidak ada ERC-20 baru dicek run ini.")
snap["runNote2231_1109_velocity"] = ("Run 2231 velocity LOLOS: " + "; ".join(f"{n} +{m} ({r}x)" for n, m, r in vel_pass) +
    ". Tidak ada yang promotable: 0x1B72ceC5 MATURE (first mint pre-window blok 132426646, umur+free% UNVERIFIED - bukan launch baru); "
    "Skyagent SUDAH age-excluded-2026-11-06 (owner d76d, discarded). PIXEL MONSTERS +114 ratio 0,84 GAGAL; Dragon Agent +19 <20 GAGAL; "
    "Undead NFTs +9 GAGAL; Marbleworks +12 ratio 0,43 GAGAL; Agentic free 473/3333 (post Boltbook) tetap gate-failed (sudah dilaporkan); "
    "Lenx Agent Pass freeMinted 809/3333 (gate-unverified, tanpa perubahan); FMA (track_c) 519.000->525.000 token (+6).")
snap["runNote2231_1109_discovery"] = ("Run 2231 rute 2: Boltbook EN 45.495 byte + ZH 45.418 byte, rc 200; baru vs run 2201: JINMA 0x8553e703 (SUDAH dimint user 20:34 WIB - lihat runNote2231_1109_jinma); "
    "sisanya recheck proyek snapshot: Lenx Agent Pass 0x6e252e3a, Agentic 0x7bcc29c5, CHIPS 0xb2625d56 (0 mint 45 mnt, paid lane mati), Cinder 0xf9876bb1 (9.900/10.000 free), "
    "Neon District CY01 0x796958fa (750/778, pace ~8/jam), Ptah 0x999980fb (token, flat 1.000.000.000). 0x8269... = BoltRewards (footer, bukan proyek). "
    "Rute 3: sweep EN+ZH - MOLT AGENT (artikel 3 hari lalu, pool sudah habis per backfill), Horus AI (free phase sold out, phase 2 berbayar), AgentForge/Pixel Fox (Okt, lama); "
    "ZH: AGC/AGENT MAO/MALTA/YAMA (sudah dikenal), HOPKIN (season berakhir 2026-11-09 12:00:06 UTC = 19:00 WIB, butuh puzzle+X unlock - bukan kandidat). Tidak ada proyek baru. "
    "Rute 6: Odaily 253.049 byte + PANews 119.387 byte, rc 200, 0 mention Agent ID/free-mint. DappBay tidak dikonsultasikan (tidak ada kandidat yang memerlukannya). "
    "Bridge: tidak berubah (mtime 2026-11-08 18:21 UTC); 8 kontrak bridge belum di snapshot semuanya ERC-20 finding tracked-wallet (bukan NFT mint) / 1 same-owner-discarded - tidak ada penambahan ke snapshot run ini.")
snap["runNote2231_1109_grove"] = ("Run 2231 Grove: freeOpen=0 (blok 132608962, file run-2026-11-09-2231-grove-check.json, grove-check job 22:32 WIB) - belum buka.")
snap["runNote2231_1109_jinma"] = ("Run 2231 JINMA triase segar (blok 132611754): sale Sourcify exact_match (verifiedAt 2026-11-09T13:32:49Z); "
    "S1 PASS (mint + quote + freeSharesRemaining/freeSharesClaimed/publicFreeRemaining + AGENT_ID_REGISTRY, registry bytes TRUE, code_len 10.537); "
    "totalShares 1380/9999, FREE_SHARES 2222, freeSharesRemaining 842, publicFreeRemaining 842, totalPaidShares 0, saleClockStart 0, "
    "TOKENS_PER_SHARE 50.000.000, PRICE_PER_SHARE 0,002 BNB, token 0xe4517e6718b24d5725956ac7a90686592a7b1539 (exact_match, totalSupply 811.030.000.000), "
    "owner 0x918e4d71337b117c1baee0729d7f371c1fbddc93 TIDAK ada di same-owner-discards.json (12 owner). "
    "hasAgentId(user)=1, freeSharesClaimed(user)=1, TOKEN balanceOf(user)=50.000.000 JINMA - slot user SUDAH TERPAKAI (mint hot-leg 20:34 WIB, sudah dilaporkan 20:58 WIB). "
    "BUKAN lead baru; tidak ada eksekusi run ini; didaftarkan di track_c sebagai minted-by-user-2026-11-09.")
snap["runNote2231_1109_age_exclusions"] = ("Run 2231 age-exclusions baru: 0. Tiga item >48h diperiksa: Night Bandits Club (launch TERVERIFIKASI 2026-11-07 18:02:28 WIB, umur ~53 jam) - "
    "baca free-quota run ini GAGAL (totalSupply/freeMinted None, degradasi RPC) sehingga 'belum sold out' tidak bisa diverifikasi, DAN statusnya sudah strong-lead-gate-blocked (bukan kandidat aktif yang bisa dipromosikan); "
    "mengikuti preseden run 1931 (item non-aktif dipertahankan catatannya, tidak dihapus) - TIDAK dihapus, dicatat sebagai age-watch. "
    "Pocket Ai (early-lead-backfill, first mint 2026-11-07 10:41:45, umur ~60 jam) - launchNote kosong (status verifikasi umur tidak tegas) + totalMinted 1390/5555; dipertahankan, age-watch. "
    "King's Game (early-lead-2026-11-07, first mint 2026-11-07 21:06:29) - launchNote menyatakan umur UNVERIFIED (first mint hanya lower bound, tanpa waktu launch proyek) sehingga klausul hapus >48h terverifikasi TIDAK terpicu; dipertahankan.")
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE DONE {NOW_WIB} updated={n_upd} track_c={n_tc} vel_pass={vel_pass}")
print("contracts now:", len(snap["contracts"]), "track_c now:", len(snap["track_c"]))
