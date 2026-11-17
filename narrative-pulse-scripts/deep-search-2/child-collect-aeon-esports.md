# Early Buyer first-30 pair V2 — COLLECT, AEON, ESPORTS (BSC, read-only)

Tugas read-only, BSC saja. Tidak ada transaksi, approval, signing, wallet connect, GMGN, atau browser task. Tidak ada seed/private key yang diminta atau dipakai. Tidak ada file state/feed/cron/goal yang diubah; file ini adalah satu-satunya file bukti baru yang ditulis.

Waktu laporan: 2026-11-02 malam WIB. Saldo dibaca ulang pada 2026-11-02 malam WIB (blok latest saat itu ~131,23 juta) — lihat 'Koreksi saldo (penting)' di bawah. MCap sesuai tugas (GeckoTerminal 2026-11-02 17:35 WIB).

## Koreksi saldo (penting — baca sebelum memakai % dipegang)

Saldo pada run stage-2 pertama SALAH dan DIBATALKAN (VOID) untuk ketiga koin: selector `balanceOf` dibangun dari hash keccak penuh, sehingga argumen yang terkirim adalah sisa hash, bukan alamat wallet — yang terbaca adalah saldo suatu alamat sampah turunan hash, bukan wallet pembeli. Akibatnya, kesimpulan interim 'AEON: semua 30 SOLD' (dari saldo nol palsu itu) DIBATALKAN dan tidak dipakai di laporan ini. Saldo pada tabel di bawah dibaca ulang dengan selector 4-byte yang benar (`0x70a08231` + alamat wallet, dihitung programatik dari `keccak('balanceOf(address)')[:4]`) via `fast_rpc` batch yang di-pin ke satu dataseed (grup 10 wallet), dan totalSupply dibaca ulang dengan cara yang sama (nilainya sama dengan sebelumnya: COLLECT 3.000.000.000, AEON 1.000.000.000, ESPORTS 900.000.000 — totalSupply tidak terpengaruh karena tidak memakai argumen alamat). Satu silang-cek: saldo COLLECT #1 dari jalur `fast_rpc` satu panggilan sama persis dengan jalur RPC langsung (0x067827e5758ceb4b). Gagal baca saldo awal (OSError `fast_rpc` di proses stage-2 yang panjang, lalu 403/putus koneksi saat RPC dipadati proses lain) dicatat di bagian gagal baca; saldo final tidak ada yang GAGAL BACA.

## Peringatan debu — sebagian besar 'beli' V2 ini bernilai ekonomi nyaris nol

Pair-pair V2 ini sangat tipis: banyak Transfer pair→ di bawah bernilai token yang sangat kecil (mis. 0,0005 ESPORTS, 0,0003 COLLECT, 0,07–0,10 AEON). Pada harga implisit mcap (COLLECT ~$13,4 jt / 3 mld = ~$0,0045/token; AEON ~$5,9 jt / 1 mld = ~$0,0059/token; ESPORTS ~$2,2 jt / 900 jt = ~$0,0024/token), sebagian besar beli awal 6 jam itu bernilai jauh di bawah $0,01 — lebih menyerupai residu router/arbitrase daripada pembelian intentional. Karena itu: (1) % dipegang yang dihitung dari basis beli-6-jam yang sangat kecil bisa meledak (ratusan ribu hingga miliaran persen) bila wallet itu kemudian menerima token lewat transfer non-pair — angka % itu BUKAN bukti conviction, dan selalu baca bersama nilai absolut beli awal dan saldo; (2) daftar 'bersih' di bawah memakai definisi tugas (HOLD/PARTIAL + bukan kontrak + bukan daftar coret + tanpa fast dump ≤1j) — bersih secara definisi TIDAK berarti posisinya bernilai besar. Koordinator perlu menilai nilai dolarnya sebelum memakai kandidat mana pun sebagai referensi.

## Metode (on-chain saja)

- Pair PCS V2: `getPair(token, WBNB)` pada factory `0xca143ce32fe78f1f7019d7d551a6402fc5350c73`, selector dihitung programatik dengan `eth_utils.keccak` (bukan hand-type). Pair dicocokkan ulang dengan event `PairCreated` factory (topik token0/token1 terurut) — ketiganya cocok persis, satu log PairCreated per pasangan.
- Blok creation pair = blok log PairCreated, tanggal dari timestamp header blok itu (bukan dari nomor blok, bukan dari field timestamp Ankr).
- Pasar-pertama: daftar pool dari endpoint GeckoTerminal `networks/bsc/tokens/{token}/pools` (dipaginasi; lihat catatan per koin). ID pool Gecko yang panjangnya 64 heksadesimal (32 byte) BUKAN alamat kontrak 20-byte dan tidak pernah dipakai sebagai alamat — hanya tanggal/nama pool-nya yang dipakai sebagai bukti ada pool lebih awal. Pool dengan ID 42 karakter dipakai sebagai alamat bila relevan.
- Early buyer = penerima Transfer token yang pengirimnya alamat pair, urut kronologis (blok, logIndex), dipindai dari blok PairCreated ke depan dengan Ankr sebagai module (`ankr_getLogs`, pageSize 1000), chunk 10.000 blok berurutan, tanpa lompat. Bila satu chunk mengembalikan tepat 1000 log, chunk dipecah jadi lebih kecil dan diulang (aturan ini tidak terpicu di pindaian ini: tidak ada chunk yang mencapai 1000 log pair→). Pindaian berhenti setelah blok header chunk melampaui timestamp beli pertama pembeli ke-30 + 6 jam, sehingga jendela beli-6-jam setiap pembeli ter-cover penuh.
- Waktu beli pertama = timestamp header blok (`eth_getBlockByNumber` via `fast_exec/fast_rpc.py`), dikonversi ke WIB — BUKAN inferensi dari selisih nomor blok, BUKAN field timestamp Ankr.
- Beli awal 6 jam = total Transfer pair→wallet dalam 6 jam sejak beli pertama wallet itu sendiri (filter timestamp header blok). Saldo sekarang = `balanceOf` dengan selector 4-byte yang benar via `fast_rpc` batch yang di-pin ke satu dataseed (lihat koreksi saldo di atas), desimal dibaca on-chain per token (COLLECT 18, AEON 8, ESPORTS 18). % dipegang = saldo / beli awal 6 jam. Jual ke pair ≤1 jam = total Transfer wallet→pair dalam 1 jam sejak beli pertama (filter timestamp header), dibagi beli awal 6 jam. Jual >100% berarti wallet itu menjual token yang juga masuk lewat transfer non-pair — dicatat, bukan dianggap kesalahan hitung. Saldo >100% dari beli awal berarti hal yang sama di sisi masuk (transfer masuk lanjutan / akumulasi non-pair).
- Ambang debu: saldo ≤0,5% beli awal 6 jam = SOLD. Status: HOLD ≥50%, PARTIAL >0,5% s.d. <50%, SOLD ≤0,5%. Saldo > beli awal (>100%) berarti ada akumulasi / transfer masuk lanjutan — BUKAN murni posisi awal.
- EOA/kontrak: `eth_getCode` — kode non-kosong = kontrak/bot executor = CORET (tetap dicatat di tabel dengan alasan).
- Daftar bersih per koin = status HOLD atau PARTIAL, BUKAN kontrak, BUKAN daftar coret, dan tanpa fast dump ≥80% dalam ≤1 jam. Wallet SOLD bukan bersih (sudah keluar), meski bukan coret. Fast dump ≤1 jam ≥80% dicatat sebagai catatan, bukan coret otomatis lintas launch — tetapi wallet fast dump tidak masuk daftar bersih.
- Linkage: KUAT = shared funding / transfer langsung SAJA. Co-buy (wallet yang sama menjadi early buyer di ≥2 koin di sini) = LEMAH, dicatat sebagai observasi saja. Funding TIDAK dinilai di sini (kerja koordinator). Tidak ada klaim PnL (proxy profit beli+pegang/jual BUKAN PnL terverifikasi) dan tidak ada klaim 'terbukti insider' untuk apa pun.
- Kegagalan baca dicatat sebagai GAGAL BACA dengan sumbernya — TIDAK PERNAH ditulis sebagai nol/tidak ada/sold out. Alamat yang terpotong dinyatakan VOID — semua alamat di laporan ini lengkap 42 karakter dari log/RPC.

## PERINGATAN BACA DULU — ketiga pair V2 ini BUKAN pasar pertama

Ketiga pair V2 di bawah dibuat JAUH SETELAH tokennya sudah diperdagangkan di pool lain. Jadi tabel di bawah adalah 30 pembeli pertama **pada pair V2 itu**, BUKAN 30 pembeli pertama saat token diluncurkan. Untuk COLLECT, pair V2 baru dibuat 2026-07-08, ~6,5 bulan setelah pool pertama (2025-12-26). Untuk AEON, pair V2 dibuat 2026-08-11, ~16 hari setelah pool pertama (2026-07-26). Untuk ESPORTS, pair V2 dibuat 2025-07-22, ~4 hari setelah pool pertama (2025-07-18). Jangan memakai tabel ini sebagai 'early buyer saat launch' tanpa kualifikasi ini.

## Ringkasan per koin

| Koin | Pair V2 (factory + PairCreated) | Pair dibuat (header) | Pool Gecko paling awal | Pasar-pertama V2? | Rentang 30 pembeli pertama (V2) | Desimal | TotalSupply on-chain | HOLD / PARTIAL / SOLD (dari 30) | Kontrak | Fast dump ≤1j ≥80% | Bersih |
|---|---|---|---|---|---|---|---|---|---|---|---|
| COLLECT | `0x4b5e76fe1acce763a7f23cf10a9db8a9080b5d0d` | blok 108747482 — 2026-07-08 14:25:56 WIB | 2025-12-26T10:17:58Z (17:17:58 WIB) | BUKAN | 2026-07-08 14:26:02 WIB s.d. 2026-09-18 00:05:38 WIB | 18 | 3,000,000,000.00 | 7 / 1 / 22 | 14 | 14 | 1 |
| AEON | `0xf3fdb8a12d3543b7b0cbcdccab17a102d0d6ba69` | blok 115283572 — 2026-08-11 15:49:42 WIB | 2026-07-26T07:09:32Z (14:09:32 WIB) | BUKAN | 2026-08-11 15:49:45 WIB s.d. 2026-08-15 08:37:58 WIB | 8 | 1,000,000,000.00 | 4 / 1 / 25 | 26 | 1 | 1 |
| ESPORTS | `0x7b65b50da0156542c916f04e605c6979819b7a77` | blok 54920638 — 2025-07-22 19:46:49 WIB | 2025-07-18T09:00:04Z (16:00:04 WIB) | BUKAN | 2025-07-22 21:01:47 WIB s.d. 2025-11-21 14:03:47 WIB | 18 | 900,000,000.00 | 14 / 0 / 16 | 19 | 4 | 7 |

Headline:
- COLLECT: bersih = 1 dari 30. `0xcb764b59f9c436ac08da3690336913ca050d6bb0` #24 (100.0%, saldo 0.00062354 COLLECT).
- AEON: bersih = 1 dari 30. `0xd05c3d496371a0ff17977c526cbd48fa9f520440` #1 (100.0%, saldo 0.90172451 AEON).
- ESPORTS: bersih = 7 dari 30. `0x29a4b61a493ca34ab367594594a730fddd131bfa` #3 (100.0%, saldo 0.00086364 ESPORTS), `0x18e31a59caeae97fa9a30a20df3f72a130147752` #4 (100.0%, saldo 0.0005066 ESPORTS), `0x9b69b82b91d9d610d53b41fc69146d6f96101be8` #8 (2482568.3%, saldo 62.21743712 ESPORTS), `0x56a4b3ae3d7d0818db0ed0d88ccad0a70d8f870a` #12 (100.0%, saldo 0.00178388 ESPORTS), `0x7945003735c62195f0f93a623364c2118fd748ea` #13 (100.0%, saldo 0.00109816 ESPORTS), `0x212656945203b29a5583242ea454ff8570a23c77` #15 (100.0%, saldo 0.00156198 ESPORTS), `0x4c1bbb72c8f43107904db33461910a6fd38f6836` #18 (100.0%, saldo 0.00269505 ESPORTS).

Co-buy lintas ketiga koin ini (LEMAH saja, bukan linkage KUAT, funding tidak diperiksa di sini):
- `0x8737a10d9c19af8bb2eae0b5e9cfe7b7276e0638` — first-30 di: COLLECT #1, AEON #29, ESPORTS #20
- `0x426603bac5e0ea73fd13aecad7a80c9f963f6eac` — first-30 di: COLLECT #2, AEON #30, ESPORTS #2
- `0xb4c3277ccad9a74ae7fbcb1688367c2ef73b2786` — first-30 di: COLLECT #6, ESPORTS #27
- `0x1513b37e5bc378b6d2ab0e9553bdc4541cd2eb25` — first-30 di: COLLECT #22, AEON #26
- `0xc795d1dcba3fc71b243112f67a5822938469ef75` — first-30 di: COLLECT #27, ESPORTS #25
- `0x238a358808379702088667322f80ac48bad5e6c4` — first-30 di: COLLECT #28, AEON #10

## COLLECT

- Token (CA lengkap): `0x4b3d30992f003c8167699735f5ab2831b2a087d3` — 18 desimal (dibaca on-chain), totalSupply on-chain 3,000,000,000.00.
- Pair PCS V2 (factory getPair + PairCreated, cocok): `0x4b5e76fe1acce763a7f23cf10a9db8a9080b5d0d` — pasangan COLLECT / WBNB. PairCreated: blok 108747482, 2026-07-08 14:25:56 WIB (header), tx `0x621049ff9d196dd5c430466d83b9c4e96b0e80eb7f6b1ec0bf5899b61b553199`.
- MCap saat pilih (tugas): ~$13,4 juta (GeckoTerminal 2026-11-02 17:35 WIB, sesuai tugas).
- Pool Gecko paling awal: 2025-12-26T10:17:58Z (17:17:58 WIB) — COLLECT / BNB 0.007% (id Gecko 64-heksadesimal, BUKAN alamat 20-byte, jadi tidak dipakai sebagai alamat). Endpoint pools token dipaginasi penuh sampai kosong: 107 pool unik (hal. 1–6, hal. 7 kosong).
- Status pasar-pertama: pair V2 BUKAN pasar pertama — ada pool Gecko yang dibuat lebih awal (lihat di atas). Tanggal pool yang disebut di tugas (2025-12-26) adalah tanggal pool awal, BUKAN tanggal pembuatan pair V2.
- Pindai log pair: dari blok 108747482 s.d. blok akhir pindai (chunk terakhir yang mencakup jendela +6 jam pembeli ke-30), 1376 chunk × 10.000 blok, 0 chunk mencapai cap 1000 log (tidak ada pemecahan chunk yang terpicu). Pembeli pair pertama: blok 108747495 — 2026-07-08 14:26:02 WIB. Pembeli ke-30: blok 122450417 — 2026-09-18 00:05:38 WIB.
- Gagal baca pindai: tidak ada. Gagal baca header: tidak ada. Gagal baca jual/saldo/kode: tidak ada.

| # | Wallet (lengkap) | Beli pertama (blok — WIB) | Beli awal 6j | Saldo sekarang | % dipegang | Status | Jual ke pair ≤1j | EOA / Kontrak | Catatan |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `0x8737a10d9c19af8bb2eae0b5e9cfe7b7276e0638` | 108747495 — 2026-07-08 14:26:02 WIB | 0.00027374 | 0.46616643 | 170296.4% | HOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor; co-buy LEMAH juga first-30 di AEON, ESPORTS (bukan linkage KUAT); saldo jauh di atas beli awal → sebagian besar saldo dari transfer masuk lanjutan (non-pair), bukan posisi awal murni |
| 2 | `0x426603bac5e0ea73fd13aecad7a80c9f963f6eac` | 108747499 — 2026-07-08 14:26:04 WIB | 0.00002464 | 0.00167872 | 6812.5% | HOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor; co-buy LEMAH juga first-30 di AEON, ESPORTS (bukan linkage KUAT); saldo jauh di atas beli awal → sebagian besar saldo dari transfer masuk lanjutan (non-pair), bukan posisi awal murni |
| 3 | `0x11d4e88458b872afac2e0e4286451b82f42b6152` | 109674699 — 2026-07-13 10:21:52 WIB | 8.87691418 | 1 wei | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 4 | `0x3530fcbaaef094d14842b8eaf4e4d059b58b5e81` | 110332280 — 2026-07-16 20:35:12 WIB | 0.00005066 | 0.00 | 0.0% | SOLD | 100.0% (0.00005066) | EOA | fast dump ≤1j 100.0% |
| 5 | `0xdbddfac4566689953760aef2b7420eb6d10d82a3` | 110332281 — 2026-07-16 20:35:12 WIB | 0.13041039 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 6 | `0xb4c3277ccad9a74ae7fbcb1688367c2ef73b2786` | 110332281 — 2026-07-16 20:35:12 WIB | 0.00000004 | 0.16093365 | 368470154.6% | HOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor; co-buy LEMAH juga first-30 di ESPORTS (bukan linkage KUAT); saldo jauh di atas beli awal → sebagian besar saldo dari transfer masuk lanjutan (non-pair), bukan posisi awal murni |
| 7 | `0x270d2e4e81297686dc16fc7ba5e2b5458c1a8286` | 110728287 — 2026-07-18 22:06:06 WIB | 0.00029999 | 0.00 | 0.0% | SOLD | 100.0% (0.00029999) | EOA | fast dump ≤1j 100.0% |
| 8 | `0xc9330d686d20b581985dad650d8ce7b60e6e10a9` | 110729507 — 2026-07-18 22:15:15 WIB | 0.00062252 | 0.00 | 0.0% | SOLD | 100.0% (0.00062252) | EOA | fast dump ≤1j 100.0% |
| 9 | `0xab1ff5451603beee58d911ea058e2e96206eee8f` | 111046533 — 2026-07-20 13:53:47 WIB | 0.00031891 | 0.00 | 0.0% | SOLD | 100.0% (0.00031891) | EOA | fast dump ≤1j 100.0% |
| 10 | `0x13c74b6c95e933e8af94edc5a2e6a316b89b857e` | 111046627 — 2026-07-20 13:54:29 WIB | 0.00010665 | 0.00 | 0.0% | SOLD | 100.0% (0.00010665) | EOA | fast dump ≤1j 100.0% |
| 11 | `0x0647884815f1e188bb9091ea98c516a8f0a8bff2` | 111051957 — 2026-07-20 14:34:28 WIB | 0.00016546 | 0.00 | 0.0% | SOLD | 100.0% (0.00016546) | EOA | fast dump ≤1j 100.0% |
| 12 | `0x2c77e16cad4b228c5529dc82c4b783427422b27a` | 111249266 — 2026-07-21 15:14:38 WIB | 0.00027339 | 0.00 | 0.0% | SOLD | 100.0% (0.00027339) | EOA | fast dump ≤1j 100.0% |
| 13 | `0x69acf56b7c2b03b69ada92ed93174e9cfc3e97d1` | 111607207 — 2026-07-23 12:02:04 WIB | 0.00016486 | 0.00 | 0.0% | SOLD | 100.0% (0.00016486) | EOA | fast dump ≤1j 100.0% |
| 14 | `0xf135d75d1360c76dddc01394c82da76a172a00d8` | 111607208 — 2026-07-23 12:02:04 WIB | 0.11657052 | 178.63646606 | 153243.3% | HOLD | 0.2% (0.00025111) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor; pool lain (Gecko: COLLECT / WBNB 0.25%, dibuat 2025-12-27T10:30:15Z); saldo jauh di atas beli awal → sebagian besar saldo dari transfer masuk lanjutan (non-pair), bukan posisi awal murni |
| 15 | `0x8ffaba28181b7ae9121f3534f1e859896652b308` | 111780495 — 2026-07-24 09:41:59 WIB | 0.00031138 | 0.00 | 0.0% | SOLD | 100.0% (0.00031138) | EOA | fast dump ≤1j 100.0% |
| 16 | `0x1fbb9ec06a28e0cab15ac7cdfefe0369cef6afa5` | 112764260 — 2026-07-29 12:45:24 WIB | 0.00119724 | 0.00 | 0.0% | SOLD | 100.0% (0.00119724) | EOA | fast dump ≤1j 100.0% |
| 17 | `0x0000000000367715a1c746bd336b65e5954c7660` | 112764263 — 2026-07-29 12:45:25 WIB | 0.00208658 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 18 | `0x66c8aa6f6071b46c92cc4dec3b054ac8d68b827c` | 112771086 — 2026-07-29 13:36:45 WIB | 0.00071051 | 0.00 | 0.0% | SOLD | 100.0% (0.00071051) | EOA | fast dump ≤1j 100.0% |
| 19 | `0x634002e4972409285001f236be34442499ffb89f` | 113037675 — 2026-07-30 22:57:05 WIB | 0.0003236 | 0.00 | 0.0% | SOLD | 100.0% (0.0003236) | EOA | fast dump ≤1j 100.0% |
| 20 | `0xad69b1ae7052c565b00ba4e49998e237640bc873` | 113041235 — 2026-07-30 23:23:47 WIB | 0.00046033 | 0.00 | 0.0% | SOLD | 100.0% (0.00046033) | EOA | fast dump ≤1j 100.0% |
| 21 | `0x4775a8fbd9a9db89ff020ef1dbc87f7459515414` | 113675967 — 2026-08-03 06:45:26 WIB | 3.75193105 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | EOA | keluar (saldo 0 / debu); bukan coret, bukan bersih (tidak memegang) |
| 22 | `0x1513b37e5bc378b6d2ab0e9553bdc4541cd2eb25` | 115908425 — 2026-08-14 21:57:52 WIB | 0.00133073 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor; co-buy LEMAH juga first-30 di AEON (bukan linkage KUAT) |
| 23 | `0x2cbb25eda3343f54a4769b74c4f197e32358fb9d` | 116263075 — 2026-08-16 18:18:21 WIB | 0.00000151 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 24 | `0xcb764b59f9c436ac08da3690336913ca050d6bb0` | 116494667 — 2026-08-17 23:15:47 WIB | 0.00062354 | 0.00062354 | 100.0% | HOLD | 0.0% (0.00) | EOA | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 25 | `0xdba28c0688c2dd8698f4111806e9a6ad719a3887` | 118895380 — 2026-08-30 11:27:19 WIB | 0.0004107 | 1190957 wei | 0.0% | SOLD | 0.0% (0.00) | EOA | keluar (saldo 0 / debu); bukan coret, bukan bersih (tidak memegang) |
| 26 | `0x5994814f2c4040b863a0125a45de152a8c2a4dec` | 119937253 — 2026-09-04 21:47:58 WIB | 26995844 wei | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 27 | `0xc795d1dcba3fc71b243112f67a5822938469ef75` | 120505952 — 2026-09-07 20:55:00 WIB | 0.00422892 | 0.00040917 | 9.7% | PARTIAL | 90.3% (0.00381975) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor; fast dump ≤1j 90.3%; co-buy LEMAH juga first-30 di ESPORTS (bukan linkage KUAT) |
| 28 | `0x238a358808379702088667322f80ac48bad5e6c4` | 120508833 — 2026-09-07 21:16:39 WIB | 0.08054745 | 48,367,700.32 | 60048701312.6% | HOLD | 0.8% (0.00063005) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor; co-buy LEMAH juga first-30 di AEON (bukan linkage KUAT); saldo jauh di atas beli awal → sebagian besar saldo dari transfer masuk lanjutan (non-pair), bukan posisi awal murni |
| 29 | `0x75ef31f3f958c1ebdcf4e804ab49562787069069` | 120884936 — 2026-09-09 20:18:30 WIB | 0.00036058 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 30 | `0x55367cc72a98f452ed4f28834a038e97575d9ade` | 122450417 — 2026-09-18 00:05:38 WIB | 0.00071259 | 0.00071259 | 100.0% | HOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |

Daftar coret COLLECT (14 dari 30):
- #1 `0x8737a10d9c19af8bb2eae0b5e9cfe7b7276e0638` — kontrak (kode non-kosong) / bot executor
- #2 `0x426603bac5e0ea73fd13aecad7a80c9f963f6eac` — kontrak (kode non-kosong) / bot executor
- #3 `0x11d4e88458b872afac2e0e4286451b82f42b6152` — kontrak (kode non-kosong) / bot executor
- #5 `0xdbddfac4566689953760aef2b7420eb6d10d82a3` — kontrak (kode non-kosong) / bot executor
- #6 `0xb4c3277ccad9a74ae7fbcb1688367c2ef73b2786` — kontrak (kode non-kosong) / bot executor
- #14 `0xf135d75d1360c76dddc01394c82da76a172a00d8` — kontrak (kode non-kosong) / bot executor; pool lain (Gecko: COLLECT / WBNB 0.25%, dibuat 2025-12-27T10:30:15Z)
- #17 `0x0000000000367715a1c746bd336b65e5954c7660` — kontrak (kode non-kosong) / bot executor
- #22 `0x1513b37e5bc378b6d2ab0e9553bdc4541cd2eb25` — kontrak (kode non-kosong) / bot executor
- #23 `0x2cbb25eda3343f54a4769b74c4f197e32358fb9d` — kontrak (kode non-kosong) / bot executor
- #26 `0x5994814f2c4040b863a0125a45de152a8c2a4dec` — kontrak (kode non-kosong) / bot executor
- #27 `0xc795d1dcba3fc71b243112f67a5822938469ef75` — kontrak (kode non-kosong) / bot executor
- #28 `0x238a358808379702088667322f80ac48bad5e6c4` — kontrak (kode non-kosong) / bot executor
- #29 `0x75ef31f3f958c1ebdcf4e804ab49562787069069` — kontrak (kode non-kosong) / bot executor
- #30 `0x55367cc72a98f452ed4f28834a038e97575d9ade` — kontrak (kode non-kosong) / bot executor

Daftar bersih COLLECT (HOLD/PARTIAL + bukan kontrak + bukan daftar coret + tanpa fast dump ≤1j):
- #24 `0xcb764b59f9c436ac08da3690336913ca050d6bb0` — beli pertama 2026-08-17 23:15:47 WIB, beli awal 6j 0.00062354, saldo 0.00062354 (100.0%, HOLD), jual ≤1j 0.0%

## AEON

- Token (CA lengkap): `0x277add739c6e0477616948357af9e79fe1ec9b80` — 8 desimal (dibaca on-chain), totalSupply on-chain 1,000,000,000.00.
- Pair PCS V2 (factory getPair + PairCreated, cocok): `0xf3fdb8a12d3543b7b0cbcdccab17a102d0d6ba69` — pasangan AEON / WBNB. PairCreated: blok 115283572, 2026-08-11 15:49:42 WIB (header), tx `0x9afde246392cfe65fea37d3a6cd436f4ea395fb7f716ceb771fb83365115e83e`.
- MCap saat pilih (tugas): ~$5,9 juta (GeckoTerminal 2026-11-02 17:35 WIB, sesuai tugas).
- Pool Gecko paling awal: 2026-07-26T07:09:32Z (14:09:32 WIB) — AEON / USDT 0.007% (id Gecko 64-heksadesimal, BUKAN alamat 20-byte, jadi tidak dipakai sebagai alamat). Endpoint pools token dipaginasi penuh sampai kosong: 84 pool unik (hal. 1–5, hal. 6 kosong).
- Status pasar-pertama: pair V2 BUKAN pasar pertama — ada pool Gecko yang dibuat lebih awal (lihat di atas). Tanggal pool yang disebut di tugas (2026-07-26) adalah tanggal pool awal, BUKAN tanggal pembuatan pair V2.
- Pindai log pair: dari blok 115283572 s.d. blok akhir pindai (chunk terakhir yang mencakup jendela +6 jam pembeli ke-30), 76 chunk × 10.000 blok, 0 chunk mencapai cap 1000 log (tidak ada pemecahan chunk yang terpicu). Pembeli pair pertama: blok 115283579 — 2026-08-11 15:49:45 WIB. Pembeli ke-30: blok 115993752 — 2026-08-15 08:37:58 WIB.
- Gagal baca pindai: tidak ada. Gagal baca header: tidak ada. Gagal baca jual/saldo/kode: tidak ada.

| # | Wallet (lengkap) | Beli pertama (blok — WIB) | Beli awal 6j | Saldo sekarang | % dipegang | Status | Jual ke pair ≤1j | EOA / Kontrak | Catatan |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `0xd05c3d496371a0ff17977c526cbd48fa9f520440` | 115283579 — 2026-08-11 15:49:45 WIB | 0.90172451 | 0.90172451 | 100.0% | HOLD | 0.0% (0.00) | EOA | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 2 | `0x9017da9bf9fbab29e9c4c51c777e9a4de261ec68` | 115293467 — 2026-08-11 17:03:57 WIB | 2.04908982 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 3 | `0x0019d4af214145bdc5e8b69faad0179d90f65485` | 115299874 — 2026-08-11 17:52:01 WIB | 7.39202322 | 0.00532556 | 0.1% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 4 | `0xa72ac8edf286e89e14052b3b72db5d66ddd08e80` | 115300544 — 2026-08-11 17:57:03 WIB | 3.4845966 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | EOA | keluar (saldo 0 / debu); bukan coret, bukan bersih (tidak memegang) |
| 5 | `0x95a5e32fd9e73ea095ef8c76852d9a235191e77f` | 115304971 — 2026-08-11 18:30:17 WIB | 6.08653719 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 6 | `0xcb3d2a42022741b06f9b38459e3dd1ee9a64d129` | 115338971 — 2026-08-11 22:45:26 WIB | 3.32275936 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 7 | `0x8456d79f0ff0baf8c02e84be4cebd149de68b5f5` | 115342320 — 2026-08-11 23:10:34 WIB | 13.60033844 | 0.00025797 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 8 | `0x5260f8edb4c383cd69ceb8afc042e290c1ff490a` | 115342979 — 2026-08-11 23:15:31 WIB | 8.38647382 | 0.00876795 | 0.1% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 9 | `0x8d77cda1ba91a59d1e563ddf9a576233c6d3b10e` | 115411869 — 2026-08-12 07:52:24 WIB | 3.47041321 | 0.00000001 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 10 | `0x238a358808379702088667322f80ac48bad5e6c4` | 115411919 — 2026-08-12 07:52:46 WIB | 13.98315889 | 25,203,587.97 | 180242448.6% | HOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor; co-buy LEMAH juga first-30 di COLLECT (bukan linkage KUAT); saldo jauh di atas beli awal → sebagian besar saldo dari transfer masuk lanjutan (non-pair), bukan posisi awal murni |
| 11 | `0xedec5c92d845ffdf9e142f2489b6fdaf3b23add1` | 115435607 — 2026-08-12 10:50:28 WIB | 7.12765721 | 0.00 | 0.0% | SOLD | 99.4% (7.08642238) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor; fast dump ≤1j 99.4% |
| 12 | `0x77519fa2324078e75b43c1bf2f8681069100c6c0` | 115436744 — 2026-08-12 10:59:00 WIB | 9.93985809 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 13 | `0x120de0bd30d55822ce5029c7eeeb669611983282` | 115446967 — 2026-08-12 12:15:40 WIB | 13.22323232 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 14 | `0x011af51cc6614fec1de0e0ff6dc315a150f3851c` | 115484958 — 2026-08-12 17:00:39 WIB | 2.07233769 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 15 | `0x9999b0cdd35d7f3b281ba02efc0d228486940515` | 115500393 — 2026-08-12 18:56:26 WIB | 15.68491749 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 16 | `0x62ccef0b4545166f721caa9fee13c1d3767e27dc` | 115507042 — 2026-08-12 19:46:19 WIB | 1.70786226 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 17 | `0x0b1f1b27c4ce05b36f3625404e4f0c2a6aa55011` | 115513585 — 2026-08-12 20:35:24 WIB | 1.02658619 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 18 | `0xa2b65a85509fb90d31db56489bf85d5691a20f0f` | 115595895 — 2026-08-13 06:52:54 WIB | 2.2803445 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 19 | `0xbb01342f5134c17dc955673cd6adf3accf3b7c25` | 115689145 — 2026-08-13 18:32:28 WIB | 6.96748128 | 1.12580524 | 16.2% | PARTIAL | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 20 | `0xd38e82b4701c38f022dd0a1086da8d5eaffa56bf` | 115727420 — 2026-08-13 23:19:38 WIB | 59.18968931 | 0.00000001 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 21 | `0x42b7aa66ac5dd487b54b075f5ceda93ff4a055cd` | 115778307 — 2026-08-14 05:41:23 WIB | 84.32154788 | 0.0000009 | 0.0% | SOLD | 0.0% (0.00) | EOA | keluar (saldo 0 / debu); bukan coret, bukan bersih (tidak memegang) |
| 22 | `0x9ff785f7fcfb5982a883197089eefaa61663d599` | 115794040 — 2026-08-14 07:39:28 WIB | 6.03440988 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 23 | `0x972e8a5172f566cd24e2845553831f68f8e9dd3c` | 115848093 — 2026-08-14 14:25:09 WIB | 3.89099086 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | EOA | keluar (saldo 0 / debu); bukan coret, bukan bersih (tidak memegang) |
| 24 | `0x3b92cc7b0b5a0fe677c5a7de748030c9b4545e6d` | 115869917 — 2026-08-14 17:08:53 WIB | 0.00003268 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 25 | `0xa011c991555673132c7996dd474cc0979619822c` | 115881005 — 2026-08-14 18:32:06 WIB | 20 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 26 | `0x1513b37e5bc378b6d2ab0e9553bdc4541cd2eb25` | 115906958 — 2026-08-14 21:46:52 WIB | 44.74578805 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor; co-buy LEMAH juga first-30 di COLLECT (bukan linkage KUAT) |
| 27 | `0xcfc344af0fecbbc7e14d05510992931a5e702213` | 115949544 — 2026-08-15 03:06:18 WIB | 19.51737373 | 0.00350227 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 28 | `0x10ed43c718714eb63d5aa57b78b54704e256024e` | 115993738 — 2026-08-15 08:37:52 WIB | 1,451.03 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 29 | `0x8737a10d9c19af8bb2eae0b5e9cfe7b7276e0638` | 115993739 — 2026-08-15 08:37:52 WIB | 0.09849129 | 0.46333996 | 470.4% | HOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor; co-buy LEMAH juga first-30 di COLLECT, ESPORTS (bukan linkage KUAT); saldo jauh di atas beli awal → sebagian besar saldo dari transfer masuk lanjutan (non-pair), bukan posisi awal murni |
| 30 | `0x426603bac5e0ea73fd13aecad7a80c9f963f6eac` | 115993752 — 2026-08-15 08:37:58 WIB | 0.06575189 | 0.23159306 | 352.2% | HOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor; co-buy LEMAH juga first-30 di COLLECT, ESPORTS (bukan linkage KUAT); saldo jauh di atas beli awal → sebagian besar saldo dari transfer masuk lanjutan (non-pair), bukan posisi awal murni |

Daftar coret AEON (26 dari 30):
- #2 `0x9017da9bf9fbab29e9c4c51c777e9a4de261ec68` — kontrak (kode non-kosong) / bot executor
- #3 `0x0019d4af214145bdc5e8b69faad0179d90f65485` — kontrak (kode non-kosong) / bot executor
- #5 `0x95a5e32fd9e73ea095ef8c76852d9a235191e77f` — kontrak (kode non-kosong) / bot executor
- #6 `0xcb3d2a42022741b06f9b38459e3dd1ee9a64d129` — kontrak (kode non-kosong) / bot executor
- #7 `0x8456d79f0ff0baf8c02e84be4cebd149de68b5f5` — kontrak (kode non-kosong) / bot executor
- #8 `0x5260f8edb4c383cd69ceb8afc042e290c1ff490a` — kontrak (kode non-kosong) / bot executor
- #9 `0x8d77cda1ba91a59d1e563ddf9a576233c6d3b10e` — kontrak (kode non-kosong) / bot executor
- #10 `0x238a358808379702088667322f80ac48bad5e6c4` — kontrak (kode non-kosong) / bot executor
- #11 `0xedec5c92d845ffdf9e142f2489b6fdaf3b23add1` — kontrak (kode non-kosong) / bot executor
- #12 `0x77519fa2324078e75b43c1bf2f8681069100c6c0` — kontrak (kode non-kosong) / bot executor
- #13 `0x120de0bd30d55822ce5029c7eeeb669611983282` — kontrak (kode non-kosong) / bot executor
- #14 `0x011af51cc6614fec1de0e0ff6dc315a150f3851c` — kontrak (kode non-kosong) / bot executor
- #15 `0x9999b0cdd35d7f3b281ba02efc0d228486940515` — kontrak (kode non-kosong) / bot executor
- #16 `0x62ccef0b4545166f721caa9fee13c1d3767e27dc` — kontrak (kode non-kosong) / bot executor
- #17 `0x0b1f1b27c4ce05b36f3625404e4f0c2a6aa55011` — kontrak (kode non-kosong) / bot executor
- #18 `0xa2b65a85509fb90d31db56489bf85d5691a20f0f` — kontrak (kode non-kosong) / bot executor
- #19 `0xbb01342f5134c17dc955673cd6adf3accf3b7c25` — kontrak (kode non-kosong) / bot executor
- #20 `0xd38e82b4701c38f022dd0a1086da8d5eaffa56bf` — kontrak (kode non-kosong) / bot executor
- #22 `0x9ff785f7fcfb5982a883197089eefaa61663d599` — kontrak (kode non-kosong) / bot executor
- #24 `0x3b92cc7b0b5a0fe677c5a7de748030c9b4545e6d` — kontrak (kode non-kosong) / bot executor
- #25 `0xa011c991555673132c7996dd474cc0979619822c` — kontrak (kode non-kosong) / bot executor
- #26 `0x1513b37e5bc378b6d2ab0e9553bdc4541cd2eb25` — kontrak (kode non-kosong) / bot executor
- #27 `0xcfc344af0fecbbc7e14d05510992931a5e702213` — kontrak (kode non-kosong) / bot executor
- #28 `0x10ed43c718714eb63d5aa57b78b54704e256024e` — kontrak (kode non-kosong) / bot executor
- #29 `0x8737a10d9c19af8bb2eae0b5e9cfe7b7276e0638` — kontrak (kode non-kosong) / bot executor
- #30 `0x426603bac5e0ea73fd13aecad7a80c9f963f6eac` — kontrak (kode non-kosong) / bot executor

Daftar bersih AEON (HOLD/PARTIAL + bukan kontrak + bukan daftar coret + tanpa fast dump ≤1j):
- #1 `0xd05c3d496371a0ff17977c526cbd48fa9f520440` — beli pertama 2026-08-11 15:49:45 WIB, beli awal 6j 0.90172451, saldo 0.90172451 (100.0%, HOLD), jual ≤1j 0.0%

## ESPORTS

- Token (CA lengkap): `0xf39e4b21c84e737df08e2c3b32541d856f508e48` — 18 desimal (dibaca on-chain), totalSupply on-chain 900,000,000.00.
- Pair PCS V2 (factory getPair + PairCreated, cocok): `0x7b65b50da0156542c916f04e605c6979819b7a77` — pasangan ESPORTS / WBNB. PairCreated: blok 54920638, 2025-07-22 19:46:49 WIB (header), tx `0x970b345bf84131980df2274e655dcb02e55f89eaff0b46aebe93b3594d2d74e7`.
- MCap saat pilih (tugas): ~$2,2 juta (GeckoTerminal 2026-11-02 17:35 WIB, sesuai tugas).
- Pool Gecko paling awal: 2025-07-18T09:00:04Z (16:00:04 WIB) — ESPORTS / WBNB 0.01%, alamat pool 0x5bb59bb9371cbec158ed602d5f3cf1ad1c9b4462 (alamat 20-byte valid). Endpoint pools token: hal. 1–10 terbaca (200 pool unik); hal. 11 GAGAL BACA (HTTP 401 Unauthorized dari GeckoTerminal) sehingga paginasi penuh TIDAK selesai. Vonis pasar-pertama tidak bergantung pada paginasi penuh: satu pool lebih awal (2025-07-18) sudah cukup membuktikan V2 bukan yang pertama.
- Status pasar-pertama: pair V2 BUKAN pasar pertama — ada pool Gecko yang dibuat lebih awal (lihat di atas). Tanggal pool yang disebut di tugas (2025-07-19) adalah tanggal pool awal, BUKAN tanggal pembuatan pair V2.
- Pindai log pair: dari blok 54920638 s.d. blok akhir pindai (chunk terakhir yang mencakup jendela +6 jam pembeli ke-30), 1406 chunk × 10.000 blok, 0 chunk mencapai cap 1000 log (tidak ada pemecahan chunk yang terpicu). Pembeli pair pertama: blok 54926636 — 2025-07-22 21:01:47 WIB. Pembeli ke-30: blok 68943080 — 2025-11-21 14:03:47 WIB.
- Gagal baca pindai: tidak ada. Gagal baca header: tidak ada. Gagal baca jual/saldo/kode: tidak ada.

| # | Wallet (lengkap) | Beli pertama (blok — WIB) | Beli awal 6j | Saldo sekarang | % dipegang | Status | Jual ke pair ≤1j | EOA / Kontrak | Catatan |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `0x01ba7fd30ab44b8d4040254432fc2a1b50214b61` | 54926636 — 2025-07-22 21:01:47 WIB | 264.49330867 | 0.13189987 | 0.0% | SOLD | 0.0% (0.00) | EOA | keluar (saldo 0 / debu); bukan coret, bukan bersih (tidak memegang) |
| 2 | `0x426603bac5e0ea73fd13aecad7a80c9f963f6eac` | 54926639 — 2025-07-22 21:01:50 WIB | 0.00147005 | 0.03348127 | 2277.6% | HOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor; co-buy LEMAH juga first-30 di COLLECT, AEON (bukan linkage KUAT); saldo jauh di atas beli awal → sebagian besar saldo dari transfer masuk lanjutan (non-pair), bukan posisi awal murni |
| 3 | `0x29a4b61a493ca34ab367594594a730fddd131bfa` | 54926753 — 2025-07-22 21:03:15 WIB | 0.00086364 | 0.00086364 | 100.0% | HOLD | 0.0% (0.00) | EOA | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 4 | `0x18e31a59caeae97fa9a30a20df3f72a130147752` | 54926816 — 2025-07-22 21:04:02 WIB | 0.0005066 | 0.0005066 | 100.0% | HOLD | 0.0% (0.00) | EOA | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 5 | `0xa07263ecc86326e9b4e6175eed779288b724927f` | 55177249 — 2025-07-25 01:14:50 WIB | 0.00067703 | 9060375674 wei | 0.0% | SOLD | 0.0% (0.00) | EOA | keluar (saldo 0 / debu); bukan coret, bukan bersih (tidak memegang) |
| 6 | `0xda006dcb8ab8b670c98fe5103340a16387187d7e` | 55177250 — 2025-07-25 01:14:51 WIB | 3.21643019 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 7 | `0x0000000000d5b78f0e7c6d9b4022c53ad21e9338` | 55177250 — 2025-07-25 01:14:51 WIB | 0.00055943 | 0.00055943 | 100.0% | HOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 8 | `0x9b69b82b91d9d610d53b41fc69146d6f96101be8` | 55177257 — 2025-07-25 01:14:56 WIB | 0.00250617 | 62.21743712 | 2482568.3% | HOLD | 0.0% (0.00) | EOA | saldo jauh di atas beli awal → sebagian besar saldo dari transfer masuk lanjutan (non-pair), bukan posisi awal murni |
| 9 | `0xa4d8ca843293b45cb2f61d54509186ca81a34408` | 55405721 — 2025-07-27 00:50:57 WIB | 810.5764201 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 10 | `0x96b5e65d55c3c2dd0faa15953c2168d508b87679` | 55524003 — 2025-07-28 01:29:36 WIB | 0.00153085 | 0.00 | 0.0% | SOLD | 100.0% (0.00153085) | EOA | fast dump ≤1j 100.0% |
| 11 | `0x3c331805089be6d3b68b485b85eaf5c299f5d0e2` | 55524046 — 2025-07-28 01:30:08 WIB | 0.00026958 | 1241 wei | 0.0% | SOLD | 100.0% (0.00026958) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor; fast dump ≤1j 100.0% |
| 12 | `0x56a4b3ae3d7d0818db0ed0d88ccad0a70d8f870a` | 55546102 — 2025-07-28 06:05:50 WIB | 0.00178388 | 0.00178388 | 100.0% | HOLD | 0.0% (0.00) | EOA | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 13 | `0x7945003735c62195f0f93a623364c2118fd748ea` | 55743880 — 2025-07-29 23:18:21 WIB | 0.00109816 | 0.00109816 | 100.0% | HOLD | 0.0% (0.00) | EOA | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 14 | `0xcc770ed954f48c2437b776042abfbfbb2fbef1e3` | 55743963 — 2025-07-29 23:19:23 WIB | 0.00031149 | 955 wei | 0.0% | SOLD | 100.0% (0.00031149) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor; fast dump ≤1j 100.0% |
| 15 | `0x212656945203b29a5583242ea454ff8570a23c77` | 55747515 — 2025-07-30 00:03:47 WIB | 0.00156198 | 0.00156198 | 100.0% | HOLD | 0.0% (0.00) | EOA | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 16 | `0xf098cc405ffa19503d969f8c7c6b8eecb4fc2565` | 55747627 — 2025-07-30 00:05:11 WIB | 0.00039033 | 3242 wei | 0.0% | SOLD | 100.0% (0.00039033) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor; fast dump ≤1j 100.0% |
| 17 | `0x60aecaf099040486763e7a87374bebc104f55617` | 55923270 — 2025-07-31 12:41:13 WIB | 0.00044632 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 18 | `0x4c1bbb72c8f43107904db33461910a6fd38f6836` | 68051262 — 2025-11-13 20:11:30 WIB | 0.00269505 | 0.00269505 | 100.0% | HOLD | 0.0% (0.00) | EOA | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 19 | `0xb21a7d6b07ad608202c5c057031a034bf4166b38` | 68051264 — 2025-11-13 20:11:31 WIB | 0.00623978 | 0.05256508 | 842.4% | HOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor; saldo jauh di atas beli awal → sebagian besar saldo dari transfer masuk lanjutan (non-pair), bukan posisi awal murni |
| 20 | `0x8737a10d9c19af8bb2eae0b5e9cfe7b7276e0638` | 68051264 — 2025-11-13 20:11:31 WIB | 0.03595473 | 1.4172258 | 3941.7% | HOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor; co-buy LEMAH juga first-30 di COLLECT, AEON (bukan linkage KUAT); saldo jauh di atas beli awal → sebagian besar saldo dari transfer masuk lanjutan (non-pair), bukan posisi awal murni |
| 21 | `0xd2b37ade14708bf18904047b1e31f8166d39612b` | 68161463 — 2025-11-14 19:09:43 WIB | 0.00000005 | 1 wei | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 22 | `0xdf82debfd3304e33979b4d790aaaf89eb70c8ff0` | 68339815 — 2025-11-16 08:19:17 WIB | 0.00002853 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 23 | `0x7297ca7e59a7a9328cabd86908c86b97c9de5634` | 68587505 — 2025-11-18 11:55:40 WIB | 4,904.35 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 24 | `0x000000000000fb06f868b46876350c37f5c86610` | 68587590 — 2025-11-18 11:56:44 WIB | 0.00001228 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 25 | `0xc795d1dcba3fc71b243112f67a5822938469ef75` | 68684559 — 2025-11-19 08:08:58 WIB | 0.0016142 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor; co-buy LEMAH juga first-30 di COLLECT (bukan linkage KUAT) |
| 26 | `0x927f64c33f48de56577fb08c87b58c66a038f53e` | 68684560 — 2025-11-19 08:08:59 WIB | 0.60093507 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 27 | `0xb4c3277ccad9a74ae7fbcb1688367c2ef73b2786` | 68684560 — 2025-11-19 08:08:59 WIB | 0.00001144 | 0.04367556 | 381660.0% | HOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor; co-buy LEMAH juga first-30 di COLLECT (bukan linkage KUAT); saldo jauh di atas beli awal → sebagian besar saldo dari transfer masuk lanjutan (non-pair), bukan posisi awal murni |
| 28 | `0x4f9308463e8694d311ce287b43ec1c1b75d49e3d` | 68754318 — 2025-11-19 22:43:59 WIB | 0.00338827 | 0.00338827 | 100.0% | HOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor |
| 29 | `0x5bb59bb9371cbec158ed602d5f3cf1ad1c9b4462` | 68754371 — 2025-11-19 22:44:39 WIB | 0.02480155 | 1,915,427.62 | 7723015860.9% | HOLD | 0.0% (0.00) | Kontrak | CORET: kontrak (kode non-kosong) / bot executor; pool lain (Gecko: ESPORTS / WBNB 0.01%, dibuat 2025-07-18T09:00:04Z); saldo jauh di atas beli awal → sebagian besar saldo dari transfer masuk lanjutan (non-pair), bukan posisi awal murni |
| 30 | `0xbf71ff1f8284abbc4eb11297bce7f979acf959f7` | 68943080 — 2025-11-21 14:03:47 WIB | 0.00003483 | 1 wei | 0.0% | SOLD | 0.0% (0.00) | EOA | keluar (saldo 0 / debu); bukan coret, bukan bersih (tidak memegang) |

Daftar coret ESPORTS (19 dari 30):
- #2 `0x426603bac5e0ea73fd13aecad7a80c9f963f6eac` — kontrak (kode non-kosong) / bot executor
- #6 `0xda006dcb8ab8b670c98fe5103340a16387187d7e` — kontrak (kode non-kosong) / bot executor
- #7 `0x0000000000d5b78f0e7c6d9b4022c53ad21e9338` — kontrak (kode non-kosong) / bot executor
- #9 `0xa4d8ca843293b45cb2f61d54509186ca81a34408` — kontrak (kode non-kosong) / bot executor
- #11 `0x3c331805089be6d3b68b485b85eaf5c299f5d0e2` — kontrak (kode non-kosong) / bot executor
- #14 `0xcc770ed954f48c2437b776042abfbfbb2fbef1e3` — kontrak (kode non-kosong) / bot executor
- #16 `0xf098cc405ffa19503d969f8c7c6b8eecb4fc2565` — kontrak (kode non-kosong) / bot executor
- #17 `0x60aecaf099040486763e7a87374bebc104f55617` — kontrak (kode non-kosong) / bot executor
- #19 `0xb21a7d6b07ad608202c5c057031a034bf4166b38` — kontrak (kode non-kosong) / bot executor
- #20 `0x8737a10d9c19af8bb2eae0b5e9cfe7b7276e0638` — kontrak (kode non-kosong) / bot executor
- #21 `0xd2b37ade14708bf18904047b1e31f8166d39612b` — kontrak (kode non-kosong) / bot executor
- #22 `0xdf82debfd3304e33979b4d790aaaf89eb70c8ff0` — kontrak (kode non-kosong) / bot executor
- #23 `0x7297ca7e59a7a9328cabd86908c86b97c9de5634` — kontrak (kode non-kosong) / bot executor
- #24 `0x000000000000fb06f868b46876350c37f5c86610` — kontrak (kode non-kosong) / bot executor
- #25 `0xc795d1dcba3fc71b243112f67a5822938469ef75` — kontrak (kode non-kosong) / bot executor
- #26 `0x927f64c33f48de56577fb08c87b58c66a038f53e` — kontrak (kode non-kosong) / bot executor
- #27 `0xb4c3277ccad9a74ae7fbcb1688367c2ef73b2786` — kontrak (kode non-kosong) / bot executor
- #28 `0x4f9308463e8694d311ce287b43ec1c1b75d49e3d` — kontrak (kode non-kosong) / bot executor
- #29 `0x5bb59bb9371cbec158ed602d5f3cf1ad1c9b4462` — kontrak (kode non-kosong) / bot executor; pool lain (Gecko: ESPORTS / WBNB 0.01%, dibuat 2025-07-18T09:00:04Z)

Daftar bersih ESPORTS (HOLD/PARTIAL + bukan kontrak + bukan daftar coret + tanpa fast dump ≤1j):
- #3 `0x29a4b61a493ca34ab367594594a730fddd131bfa` — beli pertama 2025-07-22 21:03:15 WIB, beli awal 6j 0.00086364, saldo 0.00086364 (100.0%, HOLD), jual ≤1j 0.0%
- #4 `0x18e31a59caeae97fa9a30a20df3f72a130147752` — beli pertama 2025-07-22 21:04:02 WIB, beli awal 6j 0.0005066, saldo 0.0005066 (100.0%, HOLD), jual ≤1j 0.0%
- #8 `0x9b69b82b91d9d610d53b41fc69146d6f96101be8` — beli pertama 2025-07-25 01:14:56 WIB, beli awal 6j 0.00250617, saldo 62.21743712 (2482568.3%, HOLD), jual ≤1j 0.0%
- #12 `0x56a4b3ae3d7d0818db0ed0d88ccad0a70d8f870a` — beli pertama 2025-07-28 06:05:50 WIB, beli awal 6j 0.00178388, saldo 0.00178388 (100.0%, HOLD), jual ≤1j 0.0%
- #13 `0x7945003735c62195f0f93a623364c2118fd748ea` — beli pertama 2025-07-29 23:18:21 WIB, beli awal 6j 0.00109816, saldo 0.00109816 (100.0%, HOLD), jual ≤1j 0.0%
- #15 `0x212656945203b29a5583242ea454ff8570a23c77` — beli pertama 2025-07-30 00:03:47 WIB, beli awal 6j 0.00156198, saldo 0.00156198 (100.0%, HOLD), jual ≤1j 0.0%
- #18 `0x4c1bbb72c8f43107904db33461910a6fd38f6836` — beli pertama 2025-11-13 20:11:30 WIB, beli awal 6j 0.00269505, saldo 0.00269505 (100.0%, HOLD), jual ≤1j 0.0%

## Batasan metode (baca sebelum memakai hasil)

1. Metode Transfer buta terhadap transfer BNB native dan call tanpa event — funding BNB antar wallet tidak terlihat, jadi tidak ada klaim linkage KUAT di sini.
2. `balanceOf` sekarang mencakup token yang masuk lewat transfer non-pair juga, jadi % masih dipegang adalah proxy, bukan rekonstruksi posisi pair-buy yang eksak.
3. 'Proxy profit' (beli awal + pegang/jual) BUKAN PnL terealisasi: tidak ada histori harga di log, jadi TIDAK ADA klaim PnL di laporan ini.
4. Cek daftar coret: hub sniper `0xf5988713400da6fc8a58ec9515e2b0df9b40b115` dan funder `0x318d2aae4c99c2e74f7b5949fa1c34df837789b8` dicek exact-match (hasil per koin ada di tabel — tidak ada yang cocok di ketiga koin ini kecuali dinyatakan lain). Klaster insider MSX: tidak ada daftar alamat klaster yang dilampirkan di tugas ini selain token MSX `0x23214ccbffb6ef479da64d1842b10b5525997777` itu sendiri — cek exact-match terhadap alamat token itu saja yang dilakukan; alamat-alamat MSX terpotong di file lama tidak dapat di-exact-match dan TIDAK diklaim tercakup. Exchange dan pemegang round-amount tim/vesting: tidak ada daftar yang dilampirkan di tugas ini, dan tidak ada wallet yang dilabeli tim/vesting hanya dari data Transfer — label semacam itu butuh bukti funding/vesting yang tidak diperiksa di sini. Koordinator perlu cek funding/daftar itu untuk finalis (bila ada).
5. Set terpantau dibaca dari `~/workspace/narrative-pulse/tier-ab-watch-state.json` (kunci `wallets`, 50 wallet, dibaca saat run ini). Wallet yang sudah terpantau tetap dicatat dan ditandai 'sudah-terpantau, bukan baru'.
6. Jendela jual ≤1 jam diukur dari beli pertama wallet itu, bukan dari jam creation pair. Jual ke pair setelah 1 jam, atau transfer keluar non-pair, tidak masuk kolom jual ≤1j — tetapi saldo 0 tetap berarti keluar (SOLD).
7. Untuk ESPORTS, paginasi Gecko tidak selesai (401 pada hal. 11) — daftar pool Gecko yang dipakai untuk identifikasi 'pool lain' hanya mencakup 200 pool pertama; pool ESPORTS di luar itu yang kebetulan menjadi pembeli first-30 tidak teridentifikasi sebagai pool di sini, tetapi tetap tercatat sebagai EOA/kontrak sesuai `eth_getCode`-nya.

## Semua gagal baca (gabungan)

- COLLECT: pindai=tidak ada; header=tidak ada; jual/saldo/kode=tidak ada.
- AEON: pindai=tidak ada; header=tidak ada; jual/saldo/kode=tidak ada.
- ESPORTS: pindai=tidak ada; header=tidak ada; jual/saldo/kode=tidak ada.
- GeckoTerminal ESPORTS hal. 11+: GAGAL BACA (HTTP 401 Unauthorized) — paginasi berhenti di 200 pool; vonis pasar-pertama ESPORTS tidak bergantung padanya (pool 2025-07-18 sudah terbaca).
- GeckoTerminal COLLECT/AEON: paginasi selesai sampai respons kosong, tanpa gagal baca.
