# Discovery — Koin BSC Terbentuk, Mcap > $1.000.000 (Modal Bacot, riset wallet dalam)

- **Tugas:** BAGIAN DISCOVERY saja, read-only, BSC saja. Bukan saran beli/jual.
- **Sumber utama:** API publik GeckoTerminal (JSON, bukan scraping HTML), via python urllib.
- **Waktu baca:** 2026-11-02 17:35 WIB untuk endpoint trending_pools; 2026-11-02 17:36 WIB untuk endpoint token/pools mubarak & SKYAI.
- **Filter yang dipakai:** pool_created_at lama (bukan launch jam-jaman — semua di bawah ini berumur ≥ ~2 bulan pada 2026-11-02), likuiditas > $0 dan bukan ~0/mati, mcap > $1.000.000 menurut endpoint yang dikutip. Stablecoin, WBNB, dan koin likuiditas ~0/mati dicoret.
- **Catatan angka:** angka dikutip persis dari endpoint pada waktu baca; mcap bisa bergeser menit ke menit, jadi angka token-endpoint yang dibaca sesaat kemudian bisa sedikit berbeda dari angka pool-endpoint. Bila satu angka tidak tersedia, ditulis tidak terverifikasi, bukan ditebak.

## Tabel — peringkat berdasarkan mcap (endpoint pool) menurun

| Peringkat | Nama / Simbol | CA Token (lengkap) | Pair (lengkap) | Tanggal pair creation (UTC, dari pool_created_at) | Mcap USD | Likuiditas USD | Sumber (endpoint persis) + waktu baca |
|---|---|---|---|---|---|---|---|
| 1 | AKE / AKE | 0x2c3a8ee94ddd97244a93bc48298f97d2c412f7db | 0x4d3bf29ba30f8bfe4624e7678709afa195689c5d | 2025-08-20T07:40:09Z | 141.006.743,89 | 1.408.665,01 | https://api.geckoterminal.com/api/v2/networks/bsc/trending_pools — 2026-11-02 17:35 WIB |
| 2 | Quack AI Token / Q | 0xc07e1300dc138601fa6b0b59f8d0fa477e690589 | 0x8bafe0bdd3eb9ae0539f5b32e771c1a72a189b7f | 2025-08-31T08:07:27Z | 127.318.031,99 | 1.063.350,22 | https://api.geckoterminal.com/api/v2/networks/bsc/trending_pools — 2026-11-02 17:35 WIB |
| 3 | MEET48 Token / IDOL | 0x3b4de3c7855c03bb9f50ea252cd2c9fa1125ab07 | 0xfff4857a955b2b460c27fd431aa5a85fabca5559 | 2025-06-10T13:33:11Z | 57.938.868,48 | 1.377.181,17 | https://api.geckoterminal.com/api/v2/networks/bsc/trending_pools — 2026-11-02 17:35 WIB |
| 4 | Infinity Ground AI / AIN | 0x9558a9254890b2a8b057a789f413631b9084f4a3 | 0xf4262c4dbf524f53851a5176bdc7d6c1e0fa82d8 | 2025-07-04T12:46:04Z | 50.253.462,64 | 121.764,02 | https://api.geckoterminal.com/api/v2/networks/bsc/trending_pools — 2026-11-02 17:35 WIB |
| 5 | JANCTION / JCT | 0xea37a8de1de2d9d10772eeb569e28bfa5cb17707 | 0x7bb2f6dab157e444ad8717b0178035c1b1cf24958b37c2a205e61a3582283249 | 2026-06-03T15:17:17Z | 46.582.462,90 | 769.651,02 | https://api.geckoterminal.com/api/v2/networks/bsc/trending_pools — 2026-11-02 17:35 WIB |
| 6 | mubarak / mubarak (koin dikenal, lolos filter) | 0x5c85d6c6825ab4032337f11ee92a72df936b46f6 | 0x90a54475d512b8f3852351611c38fad30a513491 | 2025-03-13T09:36:13Z | 43.829.274,25 | 2.526.507,82 | https://api.geckoterminal.com/api/v2/networks/bsc/tokens/0x5c85d6c6825ab4032337f11ee92a72df936b46f6/pools — 2026-11-02 17:36 WIB (token endpoint pada waktu sama: mcap 43.829.274,25; FDV 42.598.618,82) |
| 7 | UnifAI / UAI | 0x3e5d4f8aee0d9b3082d5f6da5d6e225d17ba9ea0 | 0x57004a34731b96d9e86b706cd629f24456ca2c7bdfcc5aae2417496d65090eb7 | 2025-11-04T07:08:50Z | 40.339.760,43 | 864.451,72 | https://api.geckoterminal.com/api/v2/networks/bsc/trending_pools — 2026-11-02 17:35 WIB |
| 8 | Beat Token / Beat | 0xcf3232b85b43bca90e51d38cc06cc8bb8c8a3e36 | 0xb2842060d68177ff202e81b3bd8588630fe7ede60e1a19f4d327125f73ae92be | 2025-11-19T05:50:12Z | 37.118.398,18 | 607.380,81 | https://api.geckoterminal.com/api/v2/networks/bsc/trending_pools — 2026-11-02 17:35 WIB |
| 9 | LAB / LAB | 0x7ec43cf65f1663f820427c62a5780b8f2e25593a | 0xd9434e63fe78a6e77dafe2abc504121bf8500822f6d3a59eccba577cf0a070f2 | 2025-10-13T09:20:50Z | 33.849.985,18 | 780.584,83 | https://api.geckoterminal.com/api/v2/networks/bsc/trending_pools — 2026-11-02 17:35 WIB |
| 10 | SKYAI / SKYAI (koin dikenal, lolos filter — status tetap INFERRED sesuai penugasan) | 0x92aa03137385f18539301349dcfc9ebc923ffb10 | 0xbc42145d5a574ede9b8860fca2a49eb7b239efa5 | 2025-04-20T03:42:03Z | 30.304.224,39 | 4.842.899,72 | https://api.geckoterminal.com/api/v2/networks/bsc/tokens/0x92aa03137385f18539301349dcfc9ebc923ffb10/pools — 2026-11-02 17:36 WIB (token endpoint pada waktu sama: mcap 30.309.732,96; FDV 30.309.732,96) |
| 11 | Teller / DEBIT | 0x66661c7229901f568f16bd1551b3ba826f83ce49 | 0x36f0e68ef7a97744389b9b5c859566629ba7c3f3899f0cc630ca68d82b6f488f | 2026-08-24T12:56:22Z | 24.079.749,76 | 1.342.010,53 | https://api.geckoterminal.com/api/v2/networks/bsc/trending_pools — 2026-11-02 17:35 WIB |
| 12 | ARIA.AI / ARIA | 0x5d3a12c42e5372b2cc3264ab3cdcf660a1555238 | 0xa5dbeaf16fc031eae92175974f8d0a439be4ad17 | 2025-08-19T09:07:05Z | 23.347.932,17 | 1.725.795,88 | https://api.geckoterminal.com/api/v2/networks/bsc/trending_pools — 2026-11-02 17:35 WIB |
| 13 | Collect on Fanable / COLLECT | 0x4b3d30992f003c8167699735f5ab2831b2a087d3 | 0xef470f9ae8512d2762e4f1cd91ae58caea17143afa61b8d56e9b20c8f87688c4 | 2025-12-26T10:17:58Z | 13.350.557,84 | 2.358.423,35 | https://api.geckoterminal.com/api/v2/networks/bsc/trending_pools — 2026-11-02 17:35 WIB |
| 14 | AEON / AEON | 0x277add739c6e0477616948357af9e79fe1ec9b80 | 0x25042161f871a34e77a7af1aff74aa1a0dc9b4c661fd53c7504948ad97f8d13f | 2026-07-26T07:09:32Z | 5.908.393,98 | 714.478,14 | https://api.geckoterminal.com/api/v2/networks/bsc/trending_pools — 2026-11-02 17:35 WIB |
| 15 | Yooldo Games / ESPORTS | 0xf39e4b21c84e737df08e2c3b32541d856f508e48 | 0x83738a0b95cbd7dfd6989569a99edaed3dd704d0 | 2025-07-19T09:08:11Z | 2.231.520,55 | 99.941,46 | https://api.geckoterminal.com/api/v2/networks/bsc/trending_pools — 2026-11-02 17:35 WIB |

Catatan per baris:
- FDV (pool endpoint, 17:35 WIB) sebagai konteks, bukan pengganti mcap: AKE $618.552.366,46; Q $135.239.543,60; IDOL $125.998.419,02; AIN $270.489.379,34; JCT $41.792.908,35; UAI $168.785.608,48; Beat $98.579.308,89; LAB $43.210.350,15; DEBIT $139.835.213,03; ARIA $127.584.328,51; COLLECT $74.584.122,01; AEON $24.052.499,45; ESPORTS $13.230.350,29. FDV bisa jauh di atas mcap (suplai beredar < suplai total) — itu data endpoint, bukan kesimpulan.
- Beberapa ID pool di atas lebih panjang dari alamat 20-byte biasa (mis. UAI, JCT, COLLECT, Beat) — dikutip verbatim dari field `id` GeckoTerminal (`bsc_<id>` tanpa prefix), bukan dipotong/ditebak.

## Dicoret / tidak masuk tabel utama

- **TART (TartSwap, 0x7ab8d02cbb51ff7223fde700eaaa2a91bf750314, pool 0x30000a407fabebe29439f8e437050512ff6661be, dibuat 2026-08-23):** FDV $13.396.597,89 dan likuiditas $846.724,09, tetapi `market_cap_usd = 0.0` di trending_pools maupun token endpoint (17:35 WIB) — mcap lag/tidak tersedia, jadi TIDAK dihitung sebagai lolos filter mcap > $1 jt. Dinyatakan begitu, tidak ditebak.
- **IAO, LITY, JAGENT, ZIG (dari trending_pools yang sama):** dicoret dari daftar "terbentuk" karena pool_created_at 2026-10-19 s.d. 2026-11-01 — terlalu baru untuk kriteria "bukan launch baru jam-jaman/hari-harian" dalam tugas ini, meskipun likuid.
- **Stablecoin, WBNB, koin likuiditas ~0/mati:** tidak ada yang dimasukkan; tidak ada baris seperti itu di tabel.
- **EGL1 — PROVISIONAL, TIDAK TERVERIFIKASI via GeckoTerminal pada bacaan ini:** CA yang ditugaskan 0xf4b385849f2e817e92fbfb9aeb48f950ff4444 mengembalikan HTTP 404 pada `https://api.geckoterminal.com/api/v2/networks/bsc/tokens/0xf4b385849f2e817e92fbfb9aeb48f950ff4444` dan array kosong pada endpoint `/tokens/multi/<alamat>` (17:36 WIB). Jadi mcap, pair, dan tanggal pair creation EGL1 TIDAK TERVERIFIKASI dari sumber ini — tidak dimasukkan ke tabel, tidak ditebak angkanya, dan konflik MCAP 10x yang disebut dalam penugasan tidak dapat dikonfirmasi/dibantah dari bacaan ini. Perlu verifikasi lewat sumber lain bila tim lain menanganinya.

## Yang tidak dilakukan (sesuai batas tugas)

- Tidak mengubah file state/feed/cron apa pun; tidak ada transaksi, approval, signing, atau login GMGN; tidak meminta seed phrase/private key.
- Tidak ada verifikasi holder, audit keamanan, atau rekomendasi beli untuk koin-koin di atas — itu di luar BAGIAN DISCOVERY ini dan menjadi pekerjaan tahap berikutnya bila ditugaskan.
