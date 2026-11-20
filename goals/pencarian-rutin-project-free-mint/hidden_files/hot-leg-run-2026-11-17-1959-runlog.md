# Hot-leg run 2026-11-17 19:59 WIB — TENANG (tidak ada lead/kandidat/perubahan tier)

- Script: run-hot-leg-2026-11-17-1959.py (copy of 1954 pattern; focus set 16). Outputs run-hot-leg-2026-11-17-1959.json + -reread.json. Elapsed 17,9 dtk — DALAM target <2 menit.
- Leg 1 Sourcify feed (limit 20): newest verifiedAt 2026-11-17T12:58:36Z, oldest 12:26:36Z — feed bergerak dari run 19:54 (newest 12:51:57Z). 3 kontrak baru vs hot-leg-seen.json, ketiganya BUKAN sale shape (S1=false, S2=false, mint=false, agent=false): 0xf3C1BEB7717E8FEb98060F246FE3f2385E7Be7Af, 0x0Cb11d30912E283e64AB0FCb86Cb1Db43af9d6ea (quote=true saja), 0x1945DAcb5213D83Fd215D82437b63b64fd0c715b. Dicatat di seen (15883→15886). Tidak ada lead baru, leg 3 kosong.
- Leg 2 Boltbook: EN OK (46.326 B) + ZH OK (46.437 B). 0 hit di semua 8 kata kunci sweep di kedua bahasa. 0 alamat baru vs seen (alamat 0x7AdB… dan 0xa34c… sudah ada di seen). Tidak ada lead baru.
- Bridge leg: scan-bridge.json 116 kontrak, 7 same_owner_discarded, outside_snapshot [] — tidak ada temuan pelengkap.
- Leg 4 reread: 16/16 OK, blok 134123928. Perubahan vs 19:54 hanya kenaikan supply kecil: PunchCard totalSupply 1224→1228, freeMinted 1210→1214 (+4); ALIEN totalSupply 445→446 (+1); PXIO-Miners totalSupply 13845→13856 (+11); MineCard totalSupply/totalMinted 954→957 (+3). Bukan perubahan tier (tidak ada sellout, slot tidak berubah, tidak ada pending claim terbuka; BinanceAI tetap launched=0, failed=1, refund phase).
- Threshold check: PunchCard free 1214/5555 = 21,9%; AGCLUB 522/8888 = 5,9%; Matrix 585/(585+415) = 58,5% — semua di bawah bar strong lead >70%. Tidak ada promosi.
- 0 kandidat / 0 eksekusi / 0 preview. Main snapshot, scan seen file, track-c-scan-checked file TIDAK disentuh (read-only).
