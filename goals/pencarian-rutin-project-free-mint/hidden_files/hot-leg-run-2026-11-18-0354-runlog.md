# free-mint-hot-leg run 2026-11-18 03:54 WIB — runlog

- Elapsed 25.6 dtk, blok 134187867. Tanpa eksekusi (read-only; tanpa preview/mint/klaim).
- Leg 1 Sourcify feed: 20 kontrak, 4 BARU (terverifikasi ~04:00 WIB):
  0xDEE50Fb229aa13eFF91A9De6471223023BfF3AFb, 0x99cE351f54F02F054713fa31428d5A5ee9c9aAba,
  0xfcBe537F83E049F37dd02a2aDf15C72F000667A0, 0x571f62eDD4693F6A86e024A7a34559d7F63B7777.
  Keempatnya shape-check BUKAN S1/S2 (tanpa mint, tanpa quote, tanpa free view, tanpa referensi Agent ID;
  0x571f... hanya ERC-20 polos). Dicatat di hot-leg-seen.json (16127 -> 16131) sebagai checked-not-sale-shape.
  Leg 3: tidak ada hit S1/S2, tidak ada verifikasi on-chain lanjutan.
- Leg 2 Boltbook EN+ZH (boltbook.fun): 9 alamat di tiap halaman, 0 baru; semua sudah ada di hot-leg-seen
  dan sudah dicek bukan sale-shape. EN fetch awal 302 lalu diikuti ke ?lang=en (HTTP 200).
  Catatan: hitungan keyword script (EN 38) vs file tersimpan (0) berbeda — front page berotasi antar dua
  fetch script; tidak ada alamat baru yang terlewat (union 3 fetch semua sudah seen).
- Bridge scan (read-only): 116 kontrak, 0 di luar snapshot, 7 same-owner-discarded. Tidak ada kontrak
  bridge yang baru memenuhi tier / promosi / perubahan.
- Leg 4 re-read focus set + bsccat + pepe vs run 0349: SATU perubahan — Stromboat freeMinted/totalMinted
  178 -> 179 (26,8% dari FREE_SUPPLY 667; di bawah bar 50% dan 70%, tanpa promosi). bsccat tanpa perubahan,
  pepe tanpa perubahan, klaim pending binanceai.fun tanpa perubahan (launched=0, failed=1, isRefundPhase=1;
  sudah dilaporkan sekali 2026-11-02, DIAM).
- Threshold: PunchCard 23,2%, AGCLUB 59,2%, Matrix 59,2%, PIXELFROGS 15,1%, AgentBubble 84,4% TAPI umur
  launch masih UNVERIFIED (dibawa dari run 0204) -> TIDAK ada promosi strong lead.
- Poffzi FCFS: tidak ada proses berjalan (NO PROCESS FOUND).
- Hasil: TIDAK ADA lead/kandidat/pending/perubahan/promosi baru -> DIAM (tanpa laporan chat).
- File run: hot-leg-2026-11-18-0354-run.py, hot-leg-run-2026-11-18-0354.json,
  hot-leg-run-2026-11-18-0354-reread.json, hot-leg-2026-11-18-0354-boltbook-en/zh.html.
