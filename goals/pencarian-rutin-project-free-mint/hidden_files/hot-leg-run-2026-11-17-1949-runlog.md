# Hot-leg run 2026-11-17 19:49 WIB — TENANG (tidak ada lead/kandidat/perubahan tier)

- Script: run-hot-leg-2026-11-17-1949.py (copy of 1944 pattern; CAT402 leg dropped — sold out 100/100 di run 19:44, sudah dilaporkan sebagai sellout, terminal). Outputs run-hot-leg-2026-11-17-1949.json + -reread.json. Elapsed 56,5 dtk — DALAM target <2 menit (chunk leg-4 diperbesar ke 4, sleep 1 dtk).
- Leg 1 Sourcify feed (limit 20): newest verifiedAt 2026-11-17T12:51:57Z, oldest 12:16:27Z. 4 kontrak baru vs hot-leg-seen.json, semua S1/S2 false (0x6a17eAd1, 0x84Cdd6C4, 0x3A86eb33, 0xbf1089E9) — tercatat checked-not-sale-shape. Tidak ada lead baru.
- Leg 2 Boltbook: EN OK kembali (46.297 B; run 19:44 EN gagal RemoteDisconnected) + ZH OK (46.505 B). 0 hit di semua 8 kata kunci sweep di kedua bahasa, 8 alamat di front page. 1 alamat baru vs seen: 0x0d85bfc6ca576d436db3cc691f4de691935f382a — shape-check S1/S2 false (bukan sale shape), tercatat di hot-leg-seen.json. Tidak ada lead baru.
- Bridge leg: scan-bridge.json 116 kontrak, 7 same_owner_discarded, outside_snapshot [] — tidak ada temuan pelengkap.
- Leg 4 reread: 16/16 OK, blok 134122870. Perubahan vs 19:44 hanya kenaikan supply kecil: PXIO-Miners totalSupply 13825→13834 (+9); MineCard totalSupply/totalMinted 951→953 (+2). Bukan perubahan tier (tidak ada sellout, slot tidak berubah, tidak ada pending claim terbuka; BinanceAI tetap launched=0, failed=1, refund phase).
- Threshold check: PunchCard free 1207/5555 = 21,7%; AGCLUB 522/8888 = 5,9%; Matrix 585/(585+415) = 58,5% — semua di bawah bar strong lead >70%. Tidak ada promosi.
- 0 kandidat / 0 eksekusi / 0 preview. Main snapshot, scan seen file, track-c-scan-checked file TIDAK disentuh (read-only).
