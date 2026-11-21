---
id: free-mint-backfill
title: Backfill gap scan FREE BACOT
enabled: false
owner: goal:pencarian-rutin-project-free-mint
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-11-06T07:16:00
  every: 15m
timeout_secs: 3600
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
BACKFILL gap scan FREE BACOT — menutup blok-blok yang tidak ter-scan karena leg scan route-4 job free-mint-search gagal/stall berulang (watermark macet di 131895548 sejak run 0501). Diputuskan user 2026-11-06 ~06:41 WIB, opsi (b) backfill bertahap 2.000 blok/run. Job ini READ-ONLY + penulisan state saja: TIDAK PERNAH preview, mint, klaim, approve, sign, swap, atau eksekusi apa pun.

STATUS AKTIF (catatan eksplisit, ditambahkan 2026-11-09 ~05:33 WIB atas perintah user): perintah nonaktifkan backfill 2026-11-08 06:28 WIB SUDAH DICABUT — user menyalakan lagi backfill 2026-11-08 20:03 WIB dan backfill AKTIF sejak itu (terverifikasi: enabled=true, run berjalan). Jangan pernah menyatakan backfill nonaktif dari perintah 06:28; perintah terakhir user soal backfill = AKTIF.

DIREKTORI KERJA: ~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/
SKRIP: backfill-scan.py + driver backfill-parallel.py (paralel, lihat AMENDMENT PARALEL di bawah).
STATE: onchain-scan-state.json (watermark last_scanned_block), onchain-scan-seen.json (first-seen), onchain-snapshot.json (watchlist), same-owner-discards.json (49 record), track-c-scan-checked.json.

TIAP RUN:
1. Baca watermark dari onchain-scan-state.json. Jalankan SATU run paralel 3 chunk (2.000 blok/chunk = 6.000 blok/run) dari watermark+1:
   cd hidden_files && timeout 3000 python3 -u backfill-parallel.py --chunks 3 --deadline-secs 600
   Driver memegang backfill.lock selama run dan menggabungkan state/seen SEKALI sesudah semua worker selesai (watermark hanya maju atas prefix kontigu; first-seen didedupe lintas chunk). Bila driver exit 3 (run sebelumnya masih jalan) -> DIAM, bukan gagal; chunk di-retry run berikut. JANGAN ubah skrip/driver: Ankr WAJIB lewat proxy env — direct egress diblokir sandbox; set no_proxy untuk rpc.ankr.com TERBUKTI merusak (SSL WRONG_VERSION_NUMBER, smoke test 2026-11-06 06:47).
2. Triase first-seen dari SEMUA chunk JSON yang tercantum di merge summary backfill-parallel-<first>-<last>.json (bila ada). Untuk tiap kontrak: verifikasi agent-shape — ABI Sourcify via curl fallback (urllib sering gagal IncompleteRead/RemoteDisconnected; endpoint https://sourcify.dev/server/v2/contract/56/<addr>?fields=abi), agentRegistry() HARUS persis 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, free quota views + quote(user,1) untuk wallet 0xeb237F6f9FB4e826739F0954e9768914F28b2c2E, first-mint block + timestamp via eth_getBlockByNumber, owner() vs same-owner-discards.json (owner() revert = nyatakan unverified, jangan paksa).
   - Free path terverifikasi (quote=0 atau free view >0 + slot terbuka) + agent-shaped + umur <=48 jam -> EARLY LEAD: tambah ke onchain-snapshot.json watchlist dengan sumber "backfill", laporkan SEKALI ke main chat dengan tag "temuan backfill" (kontrak, waktu first mint, jumlah mint, free %, slot, status tiap leg).
   - Paid-only (quote > 0, tanpa jalur gratis — contoh template Titan Ghost Agent: PRICE 0,002 BNB, supply 3.333, quote(user,1)=0,002) -> catat di log saja, JANGAN laporkan sebagai lead, JANGAN masuk snapshot.
   - Same-owner discard -> catat di log saja, JANGAN laporkan.
   - Bila free % >=25% + slot terbuka + umur <=48 jam + website terverifikasi -> strong lead: laporkan sekali (tag "temuan backfill"). TETAP JANGAN preview/mint — job ini tidak pernah mengeksekusi.
3. Track-C 5c: gabungkan erc20_mint_contracts_list dari SEMUA chunk JSON run ini, ambil mint_count >= 10, urut desc, shape-check maks 20 BARU per run (total, bukan per chunk; Sourcify ABI sale-shape S1/S2), lewati alamat yang sudah ada di track-c-scan-checked.json, catat yang baru dicek di sana. Sale-shape lolos -> verifikasi on-chain (free pool, user quote, umur launch) dan tangani sebagai track-C lead (laporkan sekali, tag "temuan backfill"). JANGAN preview/mint.
4. DIAM bila tidak ada yang baru. Bila watermark mengejar head (gap < 2.000 blok): laporkan SEKALI ke main chat bahwa backfill sudah mengejar head dan parent perlu menonaktifkan cron ini. JANGAN nonaktifkan sendiri.
5. Bila run parsial/gagal (exit 2 = parsial, failed_chunks tercatat): watermark sudah maju atas prefix sukses saja; chunk gagal di-retry run berikut secara otomatis — JANGAN lewati diam-diam, JANGAN jalankan ulang chunk yang sama secara manual. Exit 3 = lock dipegang run sebelumnya (bukan gagal) — DIAM. Catat singkat di log harian ~/memory/2026-11-06.md.

Pace terukur: 2.000 blok ~848 dtk scan (+ triase; satu run penuh ~15–30 menit). AMENDMENT 2026-11-06 ~12:58 WIB (keputusan user: percepat ke 15 menit): cadence 30m -> 15m. AMENDMENT PARALEL 2026-11-06 ~13:12 WIB (keputusan user: "jalankan saja paralel"): tiap run kini 3 worker paralel x 2.000 blok = 6.000 blok/run (driver backfill-parallel.py; worker --worker di backfill-scan.py; merge serial sekali di akhir; lock dipegang driver). Laju rantai terukur ~133 blok/menit (~8.000 blok/jam). Laju paralel ~6.000 blok per ~15–25 menit run ≈ 15.000–24.000 blok/jam → gap ~42.158 blok (13:07) tertutup ~4–5 jam bila tidak ada gangguan. Timeout cron 3600 dtk (run bisa lebih lama dari cadence 15 menit; run berikut antre/exit 3 bila lock masih dipegang). Ankr cost: ~80 panggilan ankr_getLogs per chunk 2.000 blok (~240/run) + shape checks.
