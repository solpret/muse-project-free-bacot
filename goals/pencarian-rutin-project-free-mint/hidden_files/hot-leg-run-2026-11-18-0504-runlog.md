# free-mint-hot-leg run 2026-11-18 05:04 WIB — runlog

- Elapsed 42,4 dtk (di bawah target <2 mnt), blok 134196758. Tanpa eksekusi (read-only; tanpa preview/mint/klaim).
- Leg 1 Sourcify feed: 20 kontrak, 1 BARU (top terverifikasi 2026-11-17T22:03:12Z, maju dari 21:57:53Z di run 0459).
  - 0x81E77C3532315ca215800E6CE8A49191e7025899: S1 false, S2 false — token polos (is_token true, tanpa mint, tanpa free view, tanpa agent ref, 18 fn). Bukan sale shape.
- Leg 2 Boltbook EN+ZH (boltbook.fun): HTTP 200 keduanya (EN 45.896 byte, ZH 45.991 byte), 10/11 alamat, 1 baru.
  - 0x0e63b9c287e32a05e6b9ab8ee8df88a2760225a9: S1 false, S2 false — ada mint + quote tapi tanpa free view dan tanpa agent ref (91 fn, terverifikasi 2025-12-12). Bukan sale shape.
  - Dicatat di hot-leg-seen.json (seen 16163 -> 16165). Leg 3 kosong (tidak ada hit S1/S2 untuk diverifikasi).
- Leg 4 re-read vs run 0459 (34 item, 0 chunk error): perubahan nyata hanya kenaikan kecil — AgentBubble freeMinted 1877 -> 1878 / totalSupply 2022 -> 2023, CPASS totalMinted 1775 -> 1776, STOCKAGENT totalSupply 553 -> 554 / freeLeft 558 -> 557, AgentEcho totalSupply 296 -> 297, ADRAW freeMinted 302 -> 303. Tidak ada sellout, tidak ada slot hilang, tidak ada yang melewati ambang tier.
- Threshold: PunchCard 23,3%, AGCLUB 59,3%, Matrix 59,2%, STOCKAGENT 49,9%, ALIEN 47,9%, PIXELFROGS 15,1% (semuanya <70% strong lead). Lumenhold 83,3% dan AgentBubble 84,5% TAPI umur launch keduanya masih UNVERIFIED (dibawa dari run sebelumnya) -> TIDAK ada promosi strong lead.
- Pending klaim binanceai.fun: launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0 — tanpa perubahan; sudah dilaporkan sekali 2026-11-02, DIAM.
- bsccat: tanpa perubahan. pepe: tanpa perubahan.
- Bridge scan (read-only): 116 kontrak, 0 di luar snapshot, 7 same-owner-discarded. Tidak ada kontrak bridge yang baru memenuhi tier / promosi / perubahan.
- Poffzi FCFS: tidak ada proses berjalan (NO PROCESS FOUND).
- Hasil: TIDAK ADA lead/kandidat/pending/perubahan/promosi baru -> DIAM (tanpa laporan chat).
- File run: run-hot-leg-2026-11-18-0504.py, hot-leg-run-2026-11-18-0504.json, hot-leg-run-2026-11-18-0504-reread.json.
