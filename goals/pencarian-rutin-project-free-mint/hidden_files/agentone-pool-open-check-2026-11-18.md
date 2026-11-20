# AGENTONE pool-open check — 2026-11-18 ~20:41 WIB (job agentone-pool-open-check)

Read-only. No claim/swap/execution.

## Bacaan on-chain (cast, BSC)
- Endpoint 1rpc.io/bnb: GAGAL — HTTP 502 Bad Gateway, lalu error -32001 usage limit (plan limit tercapai). Tidak ada data dari 1rpc.
- Endpoint bsc.publicnode.com: BERHASIL.
  - sale 0x84D82E933D7781fe11245e7bbd3Eb23dbb963666 — freeMinted() = 9.994 / 10.000 (dibaca ~20:40 WIB)
  - pair 0x062af274ad1ee9c4e2520968e4d3865784bc7975 — getReserves() = (0, 0, 0); token0 = AONE 0x84a0e2831665f2a9aa3824efbe0f5d32f9331f87, token1 = WBNB 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c
- Pair AONE/WBNB, token0=AONE, token1=WBNB.

## Vonis
- Pool BELUM BUKA: reserves 0, likuiditas belum masuk.
- Kursi gratis tersisa: 6 (9.994/10.000).
- Laju revisi: 18:54 WIB 5.315 → ~20:40 WIB 9.994 = +4.679 dalam ~106 menit ≈ 44/menit (lebih lambat dari ~54/menit yang dipakai perkiraan awal ~20:20 WIB). Dengan 6 kursi tersisa, sale diperkirakan habis ~20:40–20:41 WIB — praktis saat ini juga.
- Perkiraan buka awal ~20:20 WIB TERLEWATI karena laju lebih lambat; tetapi sale kini hampir habis. Kapan likuiditas masuk sesudah sale habis TIDAK bisa ditebak dari state kontrak — hot-leg 5 menit tetap memantau.
- Arena/claimability 6.000 AONE (2 kartu Hero #3330/#3331) TIDAK dicek pada run ini — hanya dicek bila pool sudah buka (langkah 3 body); status tetap UNVERIFIED.
- Tidak ada eksekusi apa pun. Tidak dibuat cron baru, tidak ada loop.
