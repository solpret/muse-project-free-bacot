# free-mint-hot-leg run 2026-11-18 04:39 WIB — runlog

- Elapsed 35,6 dtk (di bawah target <2 mnt), blok 134193878. Tanpa eksekusi (read-only; tanpa preview/mint/klaim).
- Leg 1 Sourcify feed: 20 kontrak, 2 BARU (top terverifikasi 2026-11-17T21:44:35Z):
  0xbB85aA1345fB95c640E966082C8554E62da47984 (tanpa mint/quote/free/agent, 64 fn),
  0x1C848c0A6A9883ef070d8a35F0280DBd720776Ea (ERC-20 biasa, ada quote/price tapi tanpa mint/free/agent, 63 fn).
  Keduanya BUKAN S1/S2. Dicatat di hot-leg-seen.json (16156 -> 16158) sebagai checked.
  Leg 3: tidak ada hit S1/S2, tidak ada verifikasi on-chain lanjutan.
- Leg 2 Boltbook EN+ZH (boltbook.fun): HTTP 200 keduanya (EN 46.401 byte, ZH 46.557 byte),
  8 alamat, 0 baru, 0 lead baru.
- Leg 4 re-read vs run 0434 (34 item, 0 chunk error): perubahan nyata terverifikasi hanya
  +1 mint di tiga item — ALIEN totalSupply 478 -> 479, AgentEcho 289 -> 290,
  Stromboat freeMinted/totalMinted 181 -> 182. Tidak ada sellout, tidak ada slot hilang,
  tidak ada yang melewati ambang tier.
- Threshold: PunchCard 23,3%, AGCLUB 59,3%, Matrix 59,2%, STOCKAGENT 49,1%, ALIEN 47,9%,
  PIXELFROGS 15,1% (semuanya <70% strong lead; AGCLUB/Matrix >50% tapi sudah early-lead
  di snapshot, tanpa perubahan vs 0434). Lumenhold 83,2% dan AgentBubble 84,4% (FLAT vs 0434)
  TAPI umur launch keduanya masih UNVERIFIED (dibawa dari run sebelumnya) -> TIDAK ada
  promosi strong lead.
- Pending klaim binanceai.fun: launched=0, failed=1, isRefundPhase=1, totalShares 3110,
  tokenClaimed(user)=0 — tanpa perubahan; sudah dilaporkan sekali 2026-11-02, DIAM.
- bsccat: tanpa perubahan (freeMinted 520). pepe: tanpa perubahan.
- Bridge scan (read-only): 116 kontrak, 0 di luar snapshot, 7 same-owner-discarded.
  Tidak ada kontrak bridge yang baru memenuhi tier / promosi / perubahan.
- Poffzi FCFS: tidak ada proses berjalan (NO PROCESS FOUND).
- Hasil: TIDAK ADA lead/kandidat/pending/perubahan/promosi baru -> DIAM (tanpa laporan chat).
- File run: run-hot-leg-2026-11-18-0439.py, hot-leg-run-2026-11-18-0439.json,
  hot-leg-run-2026-11-18-0439-reread.json.
