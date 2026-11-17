# afeng123 / afeng456 vs AFeng main — investigasi on-chain 2026-11-03 (read-only)

Pertanyaan: apakah afeng123.ai dan afeng456.ai dioperasikan pemilik yang sama dengan wallet utama AFeng
`0xbf004bff64725914ee36d03b87d6965b0ced4903`? Wallet dormant AFeng: `0xbd28edf53231cd121a963b4b119d3cc4cb3a368a`.

## Vonis
- **afeng123.ai — indikasi KUAT, TIDAK terbukti.** Kemungkinan anggota klaster yang didanai AFeng, bukan manusia yang terkonfirmasi sama.
- **afeng456.ai — LEMAH saja (berdiri sendiri).** Jangan digabung ke entitas AFeng hanya dari bukti ini.
- **Keduanya TIDAK TERBUKTI sebagai operator yang sama dengan AFeng main.** Kesamaan nama saja = nol bukti.

## Klaim 14,6 BNB / 7 tx — TERKONFIRMASI persis, arah main → jebakan saja
Total 9,6 BNB (afeng123, 4 tx) + 5,0 BNB (afeng456, 3 tx) = 14,6 BNB, semua transfer native biasa (input kosong), status 1.

afeng123 — main → trap (9,6 BNB):
| Waktu (WIB) | Jumlah | Tx hash | Blok |
|---|---|---|---|
| 2026-10-21 13:22 | 0,1 BNB | `0x96befc4466f9b5937de97957e5220959942fdf502438a7d30d45e61178f54880` | 128889329 |
| 2026-10-25 12:11 | 2,0 BNB | `0xffaf9d72e95b4c09c41c8ba9e1d7f4cdc6fdd04e785f01fb3cf009742a2c362f` | 129647512 |
| 2026-10-25 12:22 | 2,5 BNB | `0x35e153f976f117a0324c96abca70b8eb7afb153bbbcbfcb9c221f25b1e20d1da` | 129649002 |
| 2026-10-28 11:58 | 5,0 BNB | `0x7560c46a180b2aa2d60f05a53573fab71000442e844752aa6bf45889ee7dac85` | 130221380 |

afeng456 — main → trap (5,0 BNB, semua 2026-10-27):
| Waktu (WIB) | Jumlah | Tx hash | Blok |
|---|---|---|---|
| 2026-10-27 12:52 | 2,0 BNB | `0x32c0a4aec070a8b6029cf03ffd64dbe76c2ca5bd452d3431733d35de5f664d81` | 130036742 |
| 2026-10-27 18:07 | 2,0 BNB | `0xdba0cfed2a158aa93a6412a6562feb4b3f1c14370f757bd10a2fec10a7e1ad76` | 130078668 |
| 2026-10-27 19:33 | 1,0 BNB | `0x8509eafa1729c58c800d3f7939cf64d574cc3490fa4dbe06b5aa2154df0a14d0` | 130090083 |

## Temuan baru — arus balik afeng123 → main (tidak disebut screening lama)
- 2026-10-27 19:34 WIB, afeng123 → main **3,5 BNB**, tx `0xec117ea4c07f084f3cc8e4e67a3d99663c18f74e6fc5be7716d465238af316d7`, blok 130090208.
- Hanya 1 menit / 125 blok setelah funding terakhir main → afeng456 (19:33). Ini sinyal koordinasi terkuat di data.
- Neto main → afeng123 setelah arus balik = 6,1 BNB.
- Parent memverifikasi ulang 2 tx kunci (funding pertama + arus balik): from/to, jumlah, blok, status 1 cocok.

## Funder pertama
- **afeng123: main adalah funder PERTAMA.** Tx pertamanya adalah 0,1 BNB dari main (2026-10-21 13:22), dan 1 menit
  kemudian (13:23) ia mendaftarkan Agent ID `afeng123` (tx `0x750a6619ed135e5c00fcfa11a957257804f7892060367a80be9f7b587b99e53f`).
- **afeng456: main BUKAN funder pertama.** Tx pertamanya 2,825965886 BNB dari `0x71969e8f649d134d6265f4f2c48265dbc5ca7741`
  (2026-10-26 20:55, tx `0x50ad5be6c2c54e214a8e7369ed44c0e6880faa9c69f3ce1c1b000a213fb33103`, blok 129909094); registrasi
  `afeng456` sekitar 1 jam kemudian (22:01, tx `0x49f122578e6d4634d8d69eb44ff9c5524f32b6c573af65f594af632a87c0ffa9`). Funding main baru mulai keesokan harinya.
- **Tidak ada transaksi** antara kedua jebakan, dan tidak ada transaksi keduanya dengan wallet dormant.

## Funder bersama / pihak ketiga
- **afeng123 — jalur kedua via `0xc4589d0dc9d8e4daa0026f956cb1e01ba9f52d34`:** mengirim 2,0 BNB ke afeng123 (2026-10-23 10:49,
  tx `0xccf383b704f7095e54d3bae51297d02d3231234dcde91f5a2bbf743a04b0e605`). c458 sendiri adalah counterparty dua arah
  main: mengirim 20 BNB ke main (2026-09-26 11:59, tx `0x254a85a29dabff1105d2e2c89fd0ad8577da0e4f906c93c9fb941a8406d80b42`) dan menerima 50 BNB
  dari main (2026-11-01 11:53, tx `0x4e774f9d324e7c39ffe6c1ad6fa0256a3be20c14b0ecbf4a0ba08189a68d525b`). Jadi afeng123 punya jalur
  pendanaan kedua ke dalam klaster main (main ↔ c458 ↔ afeng123).
- **afeng456 — funder bersama `0x71969e8f649d134d6265f4f2c48265dbc5ca7741`:** selain mendanai afeng456 pertama kali, 7196 juga
  mengirim 4,9 BNB ke main (2026-09-27 07:02, tx `0x90ac93ff22053b98e1591f0ffdb29a34f47a0754c3c42780db4b78ca60f8ab2d`). Segitiga
  7196 → main, 7196 → afeng456, main → afeng456. Tetapi 7196 bisa juga pihak independen (OTC desk, layanan, trader lain).
- **Dust — abaikan:** keduanya menerima dust 1,6e-8 BNB dari sender bersama `0x747bf7a9e27d6b6e8955589436a3776b1e808b45`
  (masing-masing 2 tx) plus beberapa sender prefix `0xbf00…`/`0xbf…`. Ini pola spam ke wallet .ai, bukan bukti operator.

## Pola aktivitas bersama (sugestif, bukan bukti)
- 68 dari 97 kontrak yang disentuh afeng456 juga muncul di 126 kontrak afeng123 — termasuk Pearl mining
  (`0x7e2da878217eb995f9e5d36ed32c9cea52442681`, 20 vs 10 tx), minter AGC (`0x6288dfe86f22b53eeb6886ae2d78941de7483743`,
  masing-masing tepat 2 tx @ 0,01 BNB dengan selector identik `0x7a443eb9` + `0x0db5ae5a`), `0xe2ce6ab80874fa9fa2aae65d277dd6b8e65c9de0`
  (67 vs 52 tx), `0x1b8f3f69dfa0a7f63d308c7eb0fd38d8b099966e` (59 vs 45), `0x0d571a5ab62bc7d08ea3715962dcec22d89a4989`
  (6 vs 45). Keduanya jelas menjalankan playbook yang sama — tetapi kontrak-kontrak ini bisa jadi mint publik populer, jadi
  bukti interaksi bersama saja lemah.
- **Divergensi:** kontrak terbanyak afeng123, `0xb300000b72deaeb607a12d5f54773d1c19c7028d` (96 tx, selector `0x810c705b`),
  tidak pernah disentuh afeng456. Di 1.000 tx terbaru main, hanya 11 kontrak yang overlap dengan set jebakan (termasuk Pearl, 4×) —
  tidak ada pola trading berat bersama main di jendela itu (jendela terbatas ~2–3 hari terakhir).

## Keterkaitan Agent ID
- Registry `handleOf`: afeng123 → `afeng123`, afeng456 → `afeng456`; masing-masing registry `balanceOf` = 1 dan AgentGate
  `identityOf` non-nol. Keduanya EOA biasa (code kosong). Ini hanya membuktikan wallet tersebut mendaftarkan handle itu,
  bukan bahwa AFeng mengoperasikannya.
- Koreksi atas catatan investigasi: baca ulang segar parent 2026-11-03 menunjukkan registry `balanceOf` wallet utama = 1
  (bukan 0) — jadi main memang memegang Agent ID di registry itu. Koreksi ini TIDAK mengubah vonis: data Agent ID tetap tidak
  menghubungkan jebakan ke operator main.

## Yang masih belum terverifikasi
- Bukti kontrol kriptografis (signer/key bersama, EOA yang sama di balik smart wallet) — tidak bisa didapat dari bacaan ini.
- Riwayat lengkap main di luar 1.000 tx terbaru, dan riwayat c458 di luar 1.000 tx terbaru — counterparty bersama yang lebih lama
  bisa saja ada di sana.
- Identitas kontrak bersama (`0xe2ce…`, `0x1b8f…`, `0x0d57…`, `0xb300…`) — belum teridentifikasi, jadi bukti interaksi bersama tetap lemah.
- Penjelasan alternatif yang masih cocok dengan semua data: main mendanai wallet satelit/operator bayaran, atau copycat yang
  menarik funding main; arus balik 3,5 BNB afeng123 bisa jadi bagi hasil atau rebate, bukan konsolidasi.

## Cakupan metode
- Ankr `ankr_getTransactionsByAddress` sebagai modul, riwayat penuh tanpa gap paging: afeng123 = 749 tx (2026-10-21 → 2026-11-03),
  afeng456 = 392 tx (2026-10-26 → 2026-11-03). Riwayat funder: `0x7196…` penuh (150 tx); `0xc458…` hanya 1.000 terbaru
  (masih ada halaman lebih lama); main hanya 1.000 tx terbaru (total lifetime ~253 ribu tx).
