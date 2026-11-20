# FREE BACOT run 2331 — Rute 4 pre-flight, Rute 5a, Rute 5c, Track-B binanceai
Senin 2026-11-09 23:31 WIB. Subagent: pre-flight + 5a + 5c + binanceai (+ bridge read-only).
Read-only terhadap snapshot/seen/watermark — tidak ada penulisan ke onchain-snapshot.json,
onchain-scan-seen.json, atau onchain-scan-state.json.

## 1) Rute 4 pre-flight — GAGAL (Ankr outage berlanjut) → SCAN FAST-FAIL
- Skrip: run-2026-11-09-2331-preflight.py (salinan 2301), log: run-2026-11-09-2331-preflight.log
- HEAD (dataseed): 132617367. Hasil: PREFLIGHT FAIL dalam 8,3 dtk — HTTPError 401: 'Unauthorized'
  (run 2301: gagal 5,5 dtk, head 132614189). Outage Ankr 401 sejak ~13:33 WIB 2026-11-09 MASIH berlanjut.
- Keputusan: SCAN FAST-FAIL untuk run ini. onchain_nft_scan.py TIDAK dijalankan, TIDAK ada retry agresif.
- Watermark TETAP 132512564 (terverifikasi dari onchain-scan-state.json). Gap ke head kini
  132617367 − 132512564 = 104.803 blok dan terus membesar selama Ankr mati.
- Snapshot tidak tersentuh (mtime tetap 2026-11-09 16:25 WIB run 2301).

## 2) Rute 5a — feed Sourcify, 5 alamat baru, 0 hit S1/S2
- Feed: run-2026-11-09-2331-sourcify-feed.json — 25 entri, verifiedAt 16:13:08Z–16:33:18Z.
- Dedupe vs hot-leg-seen.json (9.615 kunci), hot-leg-reported.json (144), onchain-snapshot.json
  (626 kontrak): 5 alamat baru — run-2026-11-09-2331-5a-new.json.
  Catatan: 0xC8113f80E2613E4E520F448060e34d85323E764a sudah di-shape-check di run 2301
  (S1/S2 False); di run ini dicek ulang sesuai daftar dedupe, hasil sama.
- Shape-check: run-2026-11-09-2331-5a.py/.json/.log — semua S1 False, S2 False:
  - 0xAC80A598bCae80d6559B74f6658d63BF4bE38930 — quote saja, tanpa mint/free/agent
  - 0xF638Fe9aA85eA2Ab3BF5d008E70A53c1C1474485 — tanpa mint/quote/free/agent
  - 0x67BB53e726353489160d925A27154Db99B208b4D — tanpa mint/quote/free/agent
  - 0x88601D45D168f1691eaeB04bc983AF60773F06Ea — quote saja, token, tanpa mint/free/agent
  - 0xC8113f80E2613E4E520F448060e34d85323E764a — token, tanpa mint/quote/free/agent
- TIDAK ada S1/S2 hit baru, TIDAK ada lead track-C baru. STAR CARDS
  0x8b059e611E5f16b4659f81698CDbcB3dcfcDFDF1 (EARLY LEAD run 2301) tidak muncul
  di feed ini dan tidak dilaporkan ulang.

## 3) Rute 5c — DILEWATI (tanpa output scan baru)
Scan fast-fail → tidak ada output scan baru → 5c dilewati sesuai tugas.

## 4) Track-B binanceai.fun — TIDAK BERUBAH
- Skrip: run-2026-11-09-2331-binanceai.py; hasil: run-2026-11-09-2331-binanceai.json/.log
- Blok 132617590: launched 0, failed 1, isRefundPhase 1, totalShares 3110,
  tokenClaimed(user) 0, tokenBalance(user) 0 — IDENTIK dengan run 2301 (blok 132614189).
- Status tetap closed-refund-phase-2026-11-07. Tidak ada perubahan → tidak ada laporan baru.

## 5) Bridge scan-bridge.json — TIDAK BERUBAH
- File: run-2026-11-09-2331-bridge.json. mtime 2026-11-08 18:21:53 UTC
  (= 2026-11-09 01:21:53 WIB) — tidak berubah sejak sebelum run 2301.
- Total 116 kontrak; 7 same_owner_discarded; 7 kontrak belum ada di snapshot
  (perbandingan berbasis alamat di dalam entri snapshot; kunci snapshot adalah nama proyek):
  6 non-discarded (first_seen run-13 s.d. run-123, 2026-11-03 s.d. 2026-11-08)
  + 1 same-owner-discarded 0x0aa11f327313682cdf072affff26d0dffc804483.
  Semua sudah lama tercatat, bukan temuan baru → TIDAK dilaporkan sebagai lead.
  (Konteks run 2301 menyebut 8; hitungan run ini 7 — kemungkinan 1 masuk snapshot
  pada merge 2301 atau perbedaan cakupan banding; bridge-nya sendiri tidak berubah.)

## Kesimpulan run 2331 (bagian ini)
- Pre-flight GAGAL 401 → scan fast-fail, watermark tetap 132512564, gap ~104.803 blok.
- 5a: 5 alamat baru dicek, 0 hit S1/S2 → tidak ada lead baru.
- 5c dilewati (tanpa output scan baru).
- binanceai.fun tidak berubah (closed-refund-phase).
- Bridge tidak berubah, tidak ada temuan pelengkap scan baru.
- TIDAK ada preview/mint/eksekusi apa pun.
