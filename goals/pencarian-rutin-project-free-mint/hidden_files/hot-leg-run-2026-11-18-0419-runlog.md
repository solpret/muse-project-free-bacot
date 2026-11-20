# free-mint-hot-leg run 2026-11-18 04:19 WIB — runlog

- Elapsed 21.0 dtk, blok 134190542. Tanpa eksekusi (read-only; tanpa preview/mint/klaim).
- Leg 1 Sourcify feed: 20 kontrak, 1 BARU (terverifikasi 2026-11-17T21:17:37Z):
  0xaC231e2E7375811a03442Cc6Dc8ee92CEcFc9FA3 — shape-check BUKAN S1/S2 (has_mint true,
  agent_ref true, is_token true, TAPI tanpa quote/cost fn dan tanpa free view).
  Dicatat di hot-leg-seen.json (16147 -> 16148) sebagai checked-not-sale-shape.
  Leg 3: tidak ada hit S1/S2, tidak ada verifikasi on-chain lanjutan.
- Leg 2 Boltbook EN+ZH (boltbook.fun): HTTP 200 keduanya (EN 43.528 byte, ZH 41.962 byte),
  0 alamat baru di tiap halaman. 0 lead baru.
- Leg 4 re-read vs run 0414: 208 calls, 0 chunk error — TAPI 44 nilai kembali null
  (DRAGON 4, AGCLUB 5, BNBG 1, SPARKS 1, Ledgera 5, BoldLeonidas 3, RaceAgents 3,
  CPASS 2, Stromboat 8, binanceai-mint 5, bsccat 7) dan retry backup endpoint
  (bsc-dataseed1.defibit.io) memulihkan 0 dari 44. BUKAN perubahan state: verifikasi
  ulang pasca-run (batch kecil 6 calls, kedua endpoint) mengembalikan nilai nyata
  yang cocok dengan state 0414 — DRAGON freeMinted 1000 (=0414), AGCLUB 527 (0414: 526,
  +1 mint wajar), Stromboat 180 (=0414), binanceai launched 0 (=0414), bsccat
  freeMinted 520 (=0414), Ledgera totalSupply 2717 (0414: 2709, +8 mint wajar).
  Kesimpulan: 44 null = kegagalan baca RPC sementara (respons batch terpotong/hilang
  di bsc-dataseed; backup ikut gagal di retry), BUKAN sellout / slot hilang /
  perubahan kontrak. TIDAK ada laporan perubahan dari diff mekanis ini.
- Perubahan nyata terverifikasi: PunchCard totalSupply 1312->1314, freeMinted
  1290->1292 (+2 mint/5 mnt); AGCLUB freeMinted 526->527; Ledgera totalSupply
  2709->2717. Tidak ada yang melewati ambang tier.
- Threshold: PunchCard 23,3%, AGCLUB ~59,3%, Matrix 59,2%, PIXELFROGS 15,1%,
  AgentBubble 84,4% TAPI umur launch masih UNVERIFIED (dibawa dari run 0204)
  -> TIDAK ada promosi strong lead.
- Pending klaim binanceai.fun: launched=0, failed=1, isRefundPhase=1 (terverifikasi
  ulang pasca-run) — tanpa perubahan; sudah dilaporkan sekali 2026-11-02, DIAM.
- Bridge scan (read-only): 116 kontrak, 0 di luar snapshot, 7 same-owner-discarded.
  Tidak ada kontrak bridge yang baru memenuhi tier / promosi / perubahan.
- Poffzi FCFS: tidak ada proses berjalan (NO PROCESS FOUND).
- Hasil: TIDAK ADA lead/kandidat/pending/perubahan/promosi baru -> DIAM (tanpa laporan chat).
- File run: hot-leg-2026-11-18-0419-run.py, hot-leg-run-2026-11-18-0419.json,
  hot-leg-run-2026-11-18-0419-reread.json, hot-leg-2026-11-18-0419-boltbook-en/zh.html.
