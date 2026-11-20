# free-mint-hot-leg run 2026-11-18 03:59 WIB — runlog

- Elapsed 26.0 dtk, blok 134188494. Tanpa eksekusi (read-only; tanpa preview/mint/klaim).
- Leg 1 Sourcify feed: 20 kontrak, 6 BARU (terverifikasi ~04:04 WIB):
  0x1d6f1b0637A928b253096FB51296eE054976F288, 0x88fbc458D812a5315f2706644B711459958ED3C5,
  0x9c4bBbF52FB9e35F04A69E453EB251FEE84348f2, 0xb18D2E1dFC20b129bdF5cd126b748e00AdeEBd1c,
  0x580CDa3690067dD00e1e186f5BAe9a8fEd3CF8C2, 0x17196826850F0A4F52E39af1a5DcBf0AE515754d.
  Keenamnya shape-check BUKAN S1/S2 (tanpa quote, tanpa free view, tanpa referensi Agent ID;
  semuanya token ERC-20 polos). Dicatat di hot-leg-seen.json (16131 -> 16137) sebagai checked-not-sale-shape.
  Leg 3: tidak ada hit S1/S2, tidak ada verifikasi on-chain lanjutan.
- Leg 2 Boltbook EN+ZH (boltbook.fun): HTTP 200 keduanya (EN 44.527 byte, ZH 42.844 byte),
  9 alamat di tiap halaman, 0 baru; semua sudah ada di hot-leg-seen dan sudah dicek bukan sale-shape.
- Bridge scan (read-only): 116 kontrak, 0 di luar snapshot, 7 same-owner-discarded. Tidak ada kontrak
  bridge yang baru memenuhi tier / promosi / perubahan.
- Leg 4 re-read vs run 0354: SATU perubahan — Stromboat freeMinted/totalMinted 179 -> 180
  (27,0% dari FREE_SUPPLY 667; di bawah bar 50% dan 70%, tanpa promosi). bsccat tanpa perubahan,
  pepe tanpa perubahan, klaim pending binanceai.fun tanpa perubahan (launched=0, failed=1, isRefundPhase=1;
  sudah dilaporkan sekali 2026-11-02, DIAM).
- Threshold: PunchCard 23,2%, AGCLUB 59,2%, Matrix 59,2%, PIXELFROGS 15,1%, AgentBubble 84,4% TAPI umur
  launch masih UNVERIFIED (dibawa dari run 0204) -> TIDAK ada promosi strong lead.
- Poffzi FCFS: tidak ada proses berjalan (NO PROCESS FOUND).
- Hasil: TIDAK ADA lead/kandidat/pending/perubahan/promosi baru -> DIAM (tanpa laporan chat).
- File run: hot-leg-2026-11-18-0359-run.py, hot-leg-run-2026-11-18-0359.json,
  hot-leg-run-2026-11-18-0359-reread.json, hot-leg-2026-11-18-0359-boltbook-en/zh.html.
