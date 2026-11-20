# free-mint-hot-leg run 2026-11-18 04:59 WIB — runlog

- Elapsed 40,0 dtk (di bawah target <2 mnt), blok 134195910. Tanpa eksekusi (read-only; tanpa preview/mint/klaim).
- Leg 1 Sourcify feed: 20 kontrak, 1 BARU (top terverifikasi 2026-11-17T21:57:53Z, maju dari 21:53:53Z di run 0454).
  - 0x14D9b5778BcD84914C31a9Ad13fa4C14E206D3Aa: S1 false, S2 false — token polos (is_token true, tanpa mint, tanpa free view, tanpa agent ref, 8 fn). Bukan sale shape.
  - Dicatat di hot-leg-seen.json (seen 16162 -> 16163). Leg 3 kosong (tidak ada hit S1/S2 untuk diverifikasi).
- Leg 2 Boltbook EN+ZH (boltbook.fun): HTTP 200 keduanya (EN 45.788 byte, ZH 45.925 byte), 7/7 alamat, 0 baru, 0 lead baru.
- Leg 4 re-read vs run 0454 (34 item, 0 chunk error; chunk 5 sempat gagal di endpoint pertama lalu sukses via bnbchain.org): perubahan nyata hanya kenaikan kecil — AgentBubble freeMinted 1876 -> 1877 / totalSupply 2021 -> 2022, CPASS totalMinted 1774 -> 1775, PunchCard freeMinted 1292 -> 1293 / totalSupply 1314 -> 1315, STOCKAGENT totalSupply 546 -> 553 / freeLeft 565 -> 558, Lumenhold freeClaimed 1248 -> 1249 / totalSupply 1253 -> 1254, AgentEcho totalSupply 293 -> 296. Tidak ada sellout, tidak ada slot hilang, tidak ada yang melewati ambang tier.
- Threshold: PunchCard 23,3%, AGCLUB 59,3%, Matrix 59,2%, STOCKAGENT 49,8%, ALIEN 47,9%, PIXELFROGS 15,1% (semuanya <70% strong lead). Lumenhold 83,3% dan AgentBubble 84,5% (naik tipis vs 0454) TAPI umur launch keduanya masih UNVERIFIED (dibawa dari run sebelumnya) -> TIDAK ada promosi strong lead.
- Pending klaim binanceai.fun: launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0 — tanpa perubahan; sudah dilaporkan sekali 2026-11-02, DIAM.
- bsccat: tanpa perubahan. pepe: tanpa perubahan.
- Bridge scan (read-only): 116 kontrak, 0 di luar snapshot, 7 same-owner-discarded. Tidak ada kontrak bridge yang baru memenuhi tier / promosi / perubahan.
- Poffzi FCFS: tidak ada proses berjalan (NO PROCESS FOUND).
- Hasil: TIDAK ADA lead/kandidat/pending/perubahan/promosi baru -> DIAM (tanpa laporan chat).
- File run: run-hot-leg-2026-11-18-0459.py, hot-leg-run-2026-11-18-0459.json, hot-leg-run-2026-11-18-0459-reread.json.
