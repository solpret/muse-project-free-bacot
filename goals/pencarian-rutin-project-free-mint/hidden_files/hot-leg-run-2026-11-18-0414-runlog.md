# free-mint-hot-leg run 2026-11-18 04:14 WIB — runlog

- Elapsed 20.2 dtk, blok 134189911. Tanpa eksekusi (read-only; tanpa preview/mint/klaim).
- Leg 1 Sourcify feed: 20 kontrak, 1 BARU (terverifikasi 2026-11-17T21:15:52Z):
  0xb36fEBC3555f3742b8b218bfF1A16311f2d95A5b — shape-check BUKAN S1/S2 (has_mint true,
  agent_ref true, is_token true, TAPI tanpa quote/cost fn dan tanpa free view).
  Dicatat di hot-leg-seen.json (16145 -> 16147) sebagai checked-not-sale-shape.
  Leg 3: tidak ada hit S1/S2, tidak ada verifikasi on-chain lanjutan.
- Leg 2 Boltbook EN+ZH (boltbook.fun): HTTP 200 keduanya (EN 44.262 byte, ZH 42.470 byte),
  1 "baru" di tiap halaman: 0xc29f49110bc1ab1387df07b30c17733c1b5a5370 — artefak regex,
  40 karakter pertama dari tx hash 66 karakter di sebuah post, BUKAN alamat kontrak;
  dicatat sebagai checked-not-contract, tidak di-shape-check. 0 lead baru.
- Leg 4 re-read vs run 0409: 0 perubahan (208 calls, 0 chunk error, 0 null).
  bsccat tanpa perubahan, pepe tanpa perubahan, klaim pending binanceai.fun tanpa
  perubahan (launched=0, failed=1, isRefundPhase=1; sudah dilaporkan sekali 2026-11-02, DIAM).
- Threshold: PunchCard 23,2%, AGCLUB 59,2%, Matrix 59,2%, PIXELFROGS 15,1%, AgentBubble 84,4%
  TAPI umur launch masih UNVERIFIED (dibawa dari run 0204) -> TIDAK ada promosi strong lead.
- Bridge scan (read-only): 116 kontrak, 0 di luar snapshot, 7 same-owner-discarded. Tidak ada
  kontrak bridge yang baru memenuhi tier / promosi / perubahan.
- Poffzi FCFS: tidak ada proses berjalan (NO PROCESS FOUND).
- Hasil: TIDAK ADA lead/kandidat/pending/perubahan/promosi baru -> DIAM (tanpa laporan chat).
- File run: hot-leg-2026-11-18-0414-run.py, hot-leg-run-2026-11-18-0414.json,
  hot-leg-run-2026-11-18-0414-reread.json, hot-leg-2026-11-18-0414-boltbook-en/zh.html.
