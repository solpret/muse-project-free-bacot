# Early Buyer — koin BSC terbentuk lain (bukan trio mubarak / SKYAI / EGL1)

Tugas read-only, BSC saja, bagian EARLY BUYER untuk koin terbentuk LAIN. Tidak ada transaksi, approval, signing, login GMGN, atau perubahan file state/feed/cron. Tidak ada seed phrase / private key yang diminta atau dipakai.

Waktu laporan: 2026-11-02 sore WIB. Saldo dibaca selama run stage3 pada 2026-11-02 sore WIB (sebelum laporan ini ditulis). MCap dibaca dari GeckoTerminal trending pools BSC pada 2026-11-02 ~17:35–17:45 WIB, kecuali dinyatakan lain.

## Metode (on-chain saja, tanpa GMGN)

- Pemilihan koin (Langkah 1): GeckoTerminal API publik `networks/bsc/trending_pools` hal. 1–8. Kriteria: sudah terbentuk, likuid (reserve pool > $100.000), mcap yang dilaporkan > $1.000.000, bukan stablecoin, bukan WBNB, bukan koin likuiditas ~0/mati, dan bukan trio mubarak / SKYAI / EGL1. Bila mcap null/0 pada satu koin, koin itu TIDAK dipakai sebagai salah satu dari lima (tidak ditebak angkanya). Contoh yang dicoret di tahap ini: TART (mcap dilaporkan 0), LITY dan JAGENT (mcap null — hanya FDV yang tersedia), ARK (mcap 0), SAFU/B13B (mcap $498.283 < $1 jt), Hachiko (mcap $758.737 < $1 jt).
- Pair PCS V2: `getPair(token, quote)` pada factory `0xca143ce32fe78f1f7019d7d551a6402fc5350c73`, selector dihitung programatik dengan `eth_utils.keccak` (bukan hand-type). Hasil factory dicocokkan dengan pool GeckoTerminal; kelimanya cocok. Satu koreksi salin: string pool IBS yang sempat tercatat tanpa satu karakter akhir adalah salah salin saya — pair yang dipakai adalah hasil factory `0x2a4b99a9c4544d35e8d266111c50b67fea01d53d`, dan penarikan ulang trending hal. 4 mengonfirmasi string yang sama persis.
- Blok creation: blok terkecil yang header timestamp-nya ≥ `pool_created_at` Gecko, dicari dengan binary search atas header blok (`eth_getBlockByNumber` via `~/workspace/fast_exec/fast_rpc.py`). Semua waktu beli awal di bawah adalah timestamp header blok tersebut, dikonversi ke WIB — BUKAN inferensi dari selisih nomor blok.
- Early buyer = penerima Transfer token yang pengirimnya alamat pair, urut kronologis dari Transfer pair-pertama. Log diambil dengan Ankr sebagai MODULE (`~/workspace/custom-connectors/custom.ankr/bin/ankr.py`): `ankr_getLogs` 1000 log/halaman, paging lewat `pageToken` (modul `get_logs` tidak mengekspos `pageToken`, jadi paging dilakukan lewat `ankr_post` dari modul yang sama), chunk 10.000 blok, topik Transfer dihitung programatik (`keccak('Transfer(address,address,uint256)')`). Log diurutkan naik menurut (blok, logIndex).
- Jumlah beli awal = total yang diterima dari pair dalam 6 jam setelah beli pertama wallet itu sendiri (filter timestamp header blok, bukan jumlah blok mentah). Saldo sekarang = `balanceOf` via `fast_rpc.call_many` (batch). Semua token 18 desimal (dibaca on-chain).
- Ambang debu: saldo ≤ 0,5% dari beli awal 6 jam = SOLD (debu/keluar). Status: HOLD ≥ 50%, PARTIAL > 0,5% s.d. < 50%, SOLD ≤ 0,5%. Saldo > beli awal (di atas 100%) berarti ada akumulasi / transfer masuk lanjutan — BUKAN murni posisi awal.
- Dump cepat: transfer wallet → pair dalam 1 jam setelah beli pertama (filter timestamp header) ≥ 80% dari beli awal 6 jam. Aturan coret ≥3 launch (jual ≥80% dalam ~1 jam di ≥3 launch) TIDAK dapat diverifikasi dari 5 koin ini saja — yang dilaporkan adalah dump cepat per koin dan, bila ada, pengulangan di antara kelima koin ini.
- Filter BERSIH (dicoret tapi tetap dicatat): kontrak/bot executor (kode kontrak non-kosong via `eth_getCode`), hub funding sniper `0xf5988713400da6fc8a58ec9515e2b0df9b40b115`, funder `0x318d2aae4c99c2e74f7b5949fa1c34df837789b8`, router PCS V2, exchange (tidak ada yang teridentifikasi dari daftar ini — tidak diklaim), wallet tim/vesting (tidak ada bukti langsung; pembelian kontrak berukuran 5–13% supply dicatat sebagai kontrak, bukan diklaim sebagai tim), wallet user (bukan kandidat, hanya flag). Wallet dengan 1–2 exit cepat dicatat sebagai catatan, bukan coret otomatis lintas launch.
- Linkage: KUAT = shared funding / transfer langsung (TIDAK ditemukan dalam cakupan ini — tidak ada yang diklaim KUAT). LEMAH = co-buy saja (wallet yang sama menjadi early buyer di ≥2 dari kelima koin ini). Pola beli identik (jumlah/buy-count/sell-% sama persis) dicatat sebagai observasi untuk penelusuran lebih dalam, BUKAN bukti linkage. Tidak ada wallet yang ditulis sebagai 'terbukti insider'.
- BATAS METODE (baca sebelum memakai hasil): (1) Metode Transfer buta terhadap transfer BNB native dan call tanpa event — funding BNB antar wallet tidak terlihat. (2) `balanceOf` sekarang mencakup token yang masuk lewat transfer non-pair juga, jadi % masih dipegang adalah proxy, bukan rekonstruksi posisi pair-buy yang eksak. (3) Jual ke pair > 100% dari beli awal berarti wallet itu menjual token yang didapat dari luar pair (transfer masuk) — dicatat, bukan dianggap kesalahan hitung. (4) 'Proxy profit' (beli awal + pegang/jual) BUKAN PnL terealisasi: tidak ada histori harga di log, jadi TIDAK ADA klaim PnL 30 hari terverifikasi di laporan ini. (5) Alamat yang terpotong pada tahap kerja awal dinyatakan VOID dan tidak dipakai — semua alamat di laporan ini adalah alamat lengkap 42 karakter dari log/RPC.

## Ringkasan per koin

| Koin | Pair (PCS V2, factory) | Pool dibuat (Gecko) | Pembeli pair pertama | Rentang 30 pembeli pertama | MCap (pilih) | Reserve | HOLD / PARTIAL / SOLD (dari 30) | Kontrak | Dump cepat ≤1j |
|---|---|---|---|---|---|---|---|---|---|
| GANG | 0x0bd5ded695d61c2db15c703c345d57e039fd0b6d | 2026-10-22T09:57:27Z (16:57:27 WIB) | blok 129109856 — 2026-10-22 16:57:27 WIB | 2026-10-22 16:57:27 WIB s.d. 2026-10-22 16:57:36 WIB | $2.286.276 | $205.550 | 0 / 3 / 27 | 2 | 14 |
| 年年 (singkatan bagian ini: NIAN) | 0x3568b85ca64dce06dc08d1d65042aa737276eb41 | 2026-10-15T13:21:00Z (20:21:00 WIB) | blok 127923614 — 2026-10-16 12:36:51 WIB | 2026-10-16 12:36:51 WIB s.d. 2026-10-16 12:37:26 WIB | $3.285.792 | $194.986 | 0 / 1 / 29 | 9 | 19 |
| IBS | 0x2a4b99a9c4544d35e8d266111c50b67fea01d53d | 2026-04-22T05:58:29Z (12:58:29 WIB) | blok 93986267 — 2026-04-22 15:11:42 WIB | 2026-04-22 15:11:42 WIB s.d. 2026-04-25 09:20:21 WIB | $5.202.558 | $13.445.042 | 1 / 1 / 28 | 11 | 3 |
| MAME | 0xf75cdee96765c6d230528c247fc21d11f9f3927a | 2026-09-24T16:11:24Z (23:11:24 WIB) | blok 123786691 — 2026-09-24 23:11:24 WIB | 2026-09-24 23:11:24 WIB s.d. 2026-09-24 23:11:24 WIB | $1.494.420 (re-read endpoint pool; trending hal. 5: $1.484.393) | $122.536 | 0 / 1 / 29 | 6 | 2 |
| BORT | 0x76c42dda1de814ac60951c2c89c77dbecfb86ffb | 2025-11-04T16:45:10Z (23:45:10 WIB) | blok 67031684 — 2025-11-04 23:45:11 WIB | 2025-11-04 23:45:11 WIB s.d. 2025-11-04 23:45:31 WIB | $1.202.619 | $226.354 | 1 / 1 / 28 | 10 | 14 |

Temuan headline:
- NIAN dan MAME: TIDAK ADA clean holder di antara 30 pembeli pertama (NIAN hanya PARTIAL dari kontrak token itu sendiri; MAME sama). GANG: 0 HOLD, hanya 3 PARTIAL bersih. IBS: 1 HOLD bersih (dengan catatan akumulasi lanjutan). BORT: 0 HOLD bersih, 1 PARTIAL bersih terbaik (43,8%).
- Pool dibuat ≠ perdagangan dimulai: NIAN tidak punya satu pun transfer dari pair selama ~130.000 blok pertama setelah blok creation (~16 jam 15 menit: dibuat 2026-10-15 20:21 WIB, beli pair pertama 2026-10-16 12:36 WIB), lalu 30 pembeli pertama datang dalam 35 detik. IBS sebaliknya: beli pertama 2 jam 13 menit setelah pool dibuat, tetapi 30 pembeli pertama tersebar selama ~68 jam (trickle 7 wallet dalam ~2 hari, lalu burst 2026-04-25 pagi). GANG, MAME, dan BORT mulai dalam hitungan detik dan 30 pembeli pertama datang dalam 0–20 detik.
- Satu-satunya co-buy di antara kelima koin: `0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae` (NIAN #20 + BORT #22) — kontrak di keduanya, fast dump di BORT (126,9%) → CORET. Alamat yang sama juga terlihat sebagai penerima transfer pair GANG pada chunk uji 1.000 blok (bukan anggota 30 pertama GANG) — dicatat sebagai observasi, bukan keanggotaan first-30.
- TIDAK ADA wallet user (0xeb237F6f9FB4e826739F0954e9768914F28b2c2E / 0xcf3c6fc1bf670a8d3f03436395286f86dbee7418), hub funding sniper, funder sniper, maupun router PCS V2 di antara 150 baris (30 × 5; 149 wallet unik karena 1 co-buy) ini — pengecekan exact-match, hasil nihil.
- TIDAK ADA wallet yang fast-dump di ≥2 koin dari kelima ini, apalagi ≥3 — jadi aturan coret lintas ≥3 launch tidak terpicu oleh dataset ini. Fast dump hanya dinilai per koin di bawah.

## Kandidat terkuat (bersih: bukan kontrak, bukan daftar coret, tanpa fast dump ≤1j)

1. IBS — `0xac739056e611d639abeb0b9a87da38bd297ba00e` (IBS #2): beli awal 6 jam 22,96 IBS (2026-04-22 19:18:04 WIB), saldo sekarang 26.554,05 IBS, sold-to-pair ≤1j 0%. Status HOLD secara angka, TETAPI saldo jauh di atas beli awal → sebagian besar saldo sekarang berasal dari akumulasi / transfer masuk lanjutan, bukan posisi awal. Kandidat terkuat dengan catatan itu — bukan bukti 'smart money' murni dari posisi awal.
2. BORT — `0xcd06af254d0da9dbf95f62a75361c4cab182f13b` (BORT #8): beli awal 6 jam 313.737,68 BORT, saldo sekarang 137.264,53 BORT (43,8% PARTIAL), sold-to-pair ≤1j 56,2% (di bawah ambang 80%). Bukan kontrak, tanpa fast dump. PARTIAL bersih terbaik di seluruh laporan.
3. GANG — `0xf5c318532169bb28ea41f19fc54c224818cba3b7` (#5, 21,6% PARTIAL, saldo 766.439,37 GANG, sold ≤1j 0%), `0xb756710f115e5e928f387ee13f5ace52ebc31c06` (#6, 22,0% PARTIAL, saldo 778.343,19 GANG, sold ≤1j 0%), `0x66c60bdb0f4b510a444dbcd2d172e3978f63b4e1` (#7, 13,7% PARTIAL, saldo 483.630,74 GANG, sold ≤1j 0%). Ketiganya bukan kontrak dan tidak fast dump ≤1j, tetapi sudah menjual sebagian besar (lewat jual setelah 1 jam dan/atau transfer non-pair) — PARTIAL, bukan HOLD.
4. NIAN dan MAME: tidak ada kandidat bersih yang masih memegang (HOLD maupun PARTIAL bersih = 0). Satu-satunya PARTIAL di masing-masing adalah kontrak token itu sendiri (dicoret).

Yang dicoret per koin (ringkas; detail per wallet di tabel): GANG 14 fast dump + 2 kontrak; NIAN 19 fast dump + 9 kontrak (termasuk kontrak token sendiri); IBS 3 fast dump + 11 kontrak; MAME 2 fast dump + 6 kontrak (termasuk kontrak token sendiri); BORT 14 fast dump + 10 kontrak. Total 150 baris (149 wallet unik): HOLD 2 (1 bersih + 1 kontrak), PARTIAL 7 (4 bersih + 3 kontrak/debu-edge), SOLD 141.

## GANG

- Token (CA lengkap): `0x0c6302401aa5325c2e36f170f52c00b1d220b405` — 18 desimal, totalSupply on-chain 999,340,854.10.
- Pair PCS V2 (factory getPair, cocok dengan Gecko): `0x0bd5ded695d61c2db15c703c345d57e039fd0b6d` — pasangan GANG / WBNB.
- Pool dibuat (GeckoTerminal): 2026-10-22T09:57:27Z (16:57:27 WIB). MCap saat pilih: $2.286.276 (Trending BSC hal. 2). Reserve pool saat pilih: $205.550.
- Blok creation on-chain (binary search header): 129109855. Pindai log pair: blok 129109855 s.d. 129119854 (1 chunk × 10.000 blok, paging Ankr 1000/halaman). Pembeli berbeda yang ditemukan dalam pindaian: 2030 (hanya dalam rentang pindai, bukan total pembeli token). Tabel di bawah = 30 pembeli pertama kronologis.
- Pembeli pair pertama: blok 129109856 — 2026-10-22 16:57:27 WIB. Pembeli ke-30: blok 129109876 — 2026-10-22 16:57:36 WIB.
- Catatan khusus: 30 pembeli pertama datang dalam 9 detik (16:57:27–16:57:36 WIB). Pasangan wallet #26/#27 (7 buy, ~1,19 jt, sold ≤1j 57,2% identik) dan #5/#6/#7 (13 buy, jumlah mirip) menunjukkan pola beli identik — dicatat sebagai observasi, BUKAN bukti linkage KUAT (tidak ada shared funding / transfer langsung yang diperiksa di sini).

| # | Wallet (lengkap) | Beli awal (blok — WIB) | Beli awal 6j | Saldo sekarang | % masih dipegang | Status | Jual ke pair ≤1j | Catatan kebersihan |
|---|---|---|---|---|---|---|---|---|
| 1 | `0x87b51e0d40d413d2b7ef480e8b327a57df9769c6` | 129109856 — 2026-10-22 16:57:27 WIB | 45,670,435.94 | 0.00 | 0.0% | SOLD | 86.7% (39,599,801.50) | catatan: fast dump ≤1j 86.7% |
| 2 | `0xaf323920ccefb1763818f9ad16a9364841f4236c` | 129109861 — 2026-10-22 16:57:30 WIB | 16,826,494.44 | 0.00 | 0.0% | SOLD | 100.0% (16,826,494.44) | catatan: fast dump ≤1j 100.0% |
| 3 | `0xe00805e1dc48a014014663ae7fdaf6c695cd50cc` | 129109863 — 2026-10-22 16:57:30 WIB | 813,094.76 | 0.00 | 0.0% | SOLD | 100.0% (813,094.76) | catatan: fast dump ≤1j 100.0% |
| 4 | `0x66c70072385c516c3766123188c40cebff0a7c65` | 129109863 — 2026-10-22 16:57:30 WIB | 6,649,460.58 | 0.00 | 0.0% | SOLD | 27.1% (1,802,003.82) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 5 | `0xf5c318532169bb28ea41f19fc54c224818cba3b7` | 129109863 — 2026-10-22 16:57:30 WIB | 3,552,628.29 | 766,439.37 | 21.6% | PARTIAL | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 6 | `0xb756710f115e5e928f387ee13f5ace52ebc31c06` | 129109863 — 2026-10-22 16:57:30 WIB | 3,530,317.01 | 778,343.19 | 22.0% | PARTIAL | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 7 | `0x66c60bdb0f4b510a444dbcd2d172e3978f63b4e1` | 129109863 — 2026-10-22 16:57:30 WIB | 3,525,074.21 | 483,630.74 | 13.7% | PARTIAL | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 8 | `0xf71f5f4a6fbedf7fb799df08fd400d1404c924e7` | 129109863 — 2026-10-22 16:57:30 WIB | 790,741.54 | 0.00 | 0.0% | SOLD | 100.0% (790,741.54) | catatan: fast dump ≤1j 100.0% |
| 9 | `0xaa984233ba74c1f2836cee2c8b7919b1e46d7e21` | 129109863 — 2026-10-22 16:57:30 WIB | 6,656,320.44 | 0.00 | 0.0% | SOLD | 27.1% (1,803,862.84) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 10 | `0xc1bd70cc33f4c3cb1f264cd147811dae645a1b11` | 129109863 — 2026-10-22 16:57:30 WIB | 1,278,133.84 | 0.00 | 0.0% | SOLD | 27.1% (346,374.27) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 11 | `0x7f85c20f5381123c6413de9829bdbcdb12fd647a` | 129109864 — 2026-10-22 16:57:31 WIB | 602,157.96 | 0.00 | 0.0% | SOLD | 66.8% (402,150.82) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 12 | `0x9170fe41be574349292406caf72d3849cca9d7ec` | 129109864 — 2026-10-22 16:57:31 WIB | 600,245.96 | 0.00 | 0.0% | SOLD | 66.8% (400,873.89) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 13 | `0x18c0f63dcbf237775d579a7655ef757ba1e39083` | 129109864 — 2026-10-22 16:57:31 WIB | 6,508,551.32 | 0.00 | 0.0% | SOLD | 27.1% (1,763,817.41) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 14 | `0x2743a5337628cd931b00c9b868c4340112096e9b` | 129109865 — 2026-10-22 16:57:31 WIB | 8,062,803.49 | 0.00 | 0.0% | SOLD | 134.5% (10,843,955.33) | catatan: fast dump ≤1j 134.5%; jual > beli awal → token juga masuk lewat transfer non-pair |
| 15 | `0x5f9bc316d8473d8c6634bd26f3e0932cd6bf0718` | 129109865 — 2026-10-22 16:57:31 WIB | 11,881,828.43 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | CORET: kontrak (kode non-kosong) / bot executor |
| 16 | `0x7942262a7a5637e6eb0eec9b91b55ec232141f87` | 129109866 — 2026-10-22 16:57:32 WIB | 6,466,020.06 | 0.00 | 0.0% | SOLD | 69.2% (4,477,415.80) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 17 | `0xcf8386b39ff349796ab5650b24d4a0b5f4842a2a` | 129109866 — 2026-10-22 16:57:32 WIB | 39,234.18 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 18 | `0x3267addef42d0f9405bdc6a88b5a381df81cb1eb` | 129109866 — 2026-10-22 16:57:32 WIB | 39,209.75 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 19 | `0x7a624508609f4bda8c296d9a736af0f7b9904841` | 129109866 — 2026-10-22 16:57:32 WIB | 4,052,560.70 | 0.00 | 0.0% | SOLD | 80.6% (3,266,366.56) | catatan: fast dump ≤1j 80.6% |
| 20 | `0xaba1eb319456393a5bebbd9ec2a12cce2e79407d` | 129109866 — 2026-10-22 16:57:32 WIB | 1,041,645.40 | 0.00 | 0.0% | SOLD | 21.3% (222,193.72) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 21 | `0xb8907376abce1a2744b14153e62eb0db94dc021c` | 129109868 — 2026-10-22 16:57:33 WIB | 10,357,106.55 | 0.00 | 0.0% | SOLD | 100.0% (10,357,106.55) | catatan: fast dump ≤1j 100.0% |
| 22 | `0xf16dac84926a4110bd50eb37502a222141939183` | 129109869 — 2026-10-22 16:57:33 WIB | 33,679.75 | 0.00 | 0.0% | SOLD | 100.0% (33,679.75) | catatan: fast dump ≤1j 100.0% |
| 23 | `0xa5ef22e9ef670c14915b9ea4ed3adab589768354` | 129109871 — 2026-10-22 16:57:34 WIB | 51,202,229.92 | 0.00 | 0.0% | SOLD | 85.0% (43,522,874.23) | CORET: kontrak (kode non-kosong) / bot executor; catatan: fast dump ≤1j 85.0% |
| 24 | `0x0f84d2da979180394fbf9c4499febd0f602a6767` | 129109871 — 2026-10-22 16:57:34 WIB | 2,378,815.16 | 0.00 | 0.0% | SOLD | 100.0% (2,378,815.16) | catatan: fast dump ≤1j 100.0% |
| 25 | `0x10d5ad13ea3cfee0451f8d3513f11af01bdc1600` | 129109872 — 2026-10-22 16:57:34 WIB | 144,834.68 | 0.00 | 0.0% | SOLD | 100.0% (144,834.68) | catatan: fast dump ≤1j 100.0% |
| 26 | `0x174e7ad54e17d02a6fa019cdafff1b5e902c98ec` | 129109872 — 2026-10-22 16:57:34 WIB | 1,189,281.64 | 0.00 | 0.0% | SOLD | 57.2% (679,724.89) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 27 | `0xcb44eaad62cd6763c15c3a726f98bc466026e291` | 129109872 — 2026-10-22 16:57:34 WIB | 1,192,278.80 | 0.00 | 0.0% | SOLD | 57.2% (681,847.79) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 28 | `0x38abe698e2322a67b84141ba4998feba0fe478d5` | 129109874 — 2026-10-22 16:57:35 WIB | 1,162,385.27 | 0.00 | 0.0% | SOLD | 100.0% (1,162,385.27) | catatan: fast dump ≤1j 100.0% |
| 29 | `0x4411a84b250417fd4d1f3b91de10ebb691c56fbc` | 129109874 — 2026-10-22 16:57:35 WIB | 1,151,649.25 | 0.00 | 0.0% | SOLD | 100.0% (1,151,649.25) | catatan: fast dump ≤1j 100.0% |
| 30 | `0x79c76a75e895046831ec018f852ede19372ebe2e` | 129109876 — 2026-10-22 16:57:36 WIB | 547,934.15 | 0.00 | 0.0% | SOLD | 647.5% (3,547,934.15) | catatan: fast dump ≤1j 647.5%; jual > beli awal → token juga masuk lewat transfer non-pair |

## 年年 (singkatan bagian ini: NIAN)

- Token (CA lengkap): `0xf4d5765e448774ed9482870420da7c3c4c787777` — 18 desimal, totalSupply on-chain 1,000,000,000.00.
- Pair PCS V2 (factory getPair, cocok dengan Gecko): `0x3568b85ca64dce06dc08d1d65042aa737276eb41` — pasangan 年年 (singkatan bagian ini: NIAN) / B13B (0x4902c5ebc598265ed2212b559b042de8a5eeec3f).
- Pool dibuat (GeckoTerminal): 2026-10-15T13:21:00Z (20:21:00 WIB). MCap saat pilih: $3.285.792 (Trending BSC hal. 3; re-read endpoint pool $3.280.100). Reserve pool saat pilih: $194.986.
- Blok creation on-chain (binary search header): 127793609. Pindai log pair: blok 127793609 s.d. 127933608 (14 chunk × 10.000 blok, paging Ankr 1000/halaman). Pembeli berbeda yang ditemukan dalam pindaian: 75 (hanya dalam rentang pindai, bukan total pembeli token). Tabel di bawah = 30 pembeli pertama kronologis.
- Pembeli pair pertama: blok 127923614 — 2026-10-16 12:36:51 WIB. Pembeli ke-30: blok 127923691 — 2026-10-16 12:37:26 WIB.
- Catatan khusus: TIDAK ADA transfer dari pair selama ~130.000 blok pertama setelah blok creation. 'Jam-jam pertama setelah pair creation' untuk koin ini secara faktual kosong; 30 pembeli pertama diambil dari burst perdagangan pertama (2026-10-16 12:36 WIB), bukan dari jam creation.

| # | Wallet (lengkap) | Beli awal (blok — WIB) | Beli awal 6j | Saldo sekarang | % masih dipegang | Status | Jual ke pair ≤1j | Catatan kebersihan |
|---|---|---|---|---|---|---|---|---|
| 1 | `0xf4d5765e448774ed9482870420da7c3c4c787777` | 127923614 — 2026-10-16 12:36:51 WIB | 6,073,797.19 | 71,701.58 | 1.2% | PARTIAL | 0.0% (0.00) | CORET: kontrak (kode non-kosong) / bot executor; alamat ini = kontrak token itu sendiri |
| 2 | `0xf366a618718210014a0cc99f3787b12f3e621a73` | 127923614 — 2026-10-16 12:36:51 WIB | 210,564.79 | 0.00 | 0.0% | SOLD | 4456.6% (9,383,928.29) | CORET: kontrak (kode non-kosong) / bot executor; catatan: fast dump ≤1j 4456.6%; jual > beli awal → token juga masuk lewat transfer non-pair |
| 3 | `0xbf1db89044b96f9c3c8f874bd3623669ab1394d9` | 127923615 — 2026-10-16 12:36:51 WIB | 347,510.85 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 4 | `0xb5a07f5cfe04ed505277a2f02279756e24a00a4c` | 127923615 — 2026-10-16 12:36:51 WIB | 519,112.05 | 0.00 | 0.0% | SOLD | 97.0% (503,538.69) | CORET: kontrak (kode non-kosong) / bot executor; catatan: fast dump ≤1j 97.0% |
| 5 | `0xf8cbab575fdca339c0196ab3dca9fabc41689d6b` | 127923616 — 2026-10-16 12:36:52 WIB | 917,216.22 | 0.00 | 0.0% | SOLD | 97.0% (889,699.73) | catatan: fast dump ≤1j 97.0% |
| 6 | `0x268e0c06900b572a3860bd5958db9a71db0008e4` | 127923617 — 2026-10-16 12:36:52 WIB | 117,156.79 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | CORET: kontrak (kode non-kosong) / bot executor |
| 7 | `0x3306c13181c197c4f3b2d1e0ffc27aeba0c4fddd` | 127923618 — 2026-10-16 12:36:53 WIB | 767,441.49 | 0.00 | 0.0% | SOLD | 97.0% (744,418.25) | catatan: fast dump ≤1j 97.0% |
| 8 | `0xe40ce1535fd09ac615f67b11ce2b8b8be00d16aa` | 127923618 — 2026-10-16 12:36:53 WIB | 762,151.22 | 0.00 | 0.0% | SOLD | 97.0% (739,286.68) | catatan: fast dump ≤1j 97.0% |
| 9 | `0x2b969a5d35c000ca3efd791a54b9c766e3187ec7` | 127923622 — 2026-10-16 12:36:54 WIB | 952,082.17 | 0.00 | 0.0% | SOLD | 97.0% (923,519.71) | catatan: fast dump ≤1j 97.0% |
| 10 | `0xdb6a329ff14d249c1c8db0c6a1c95edec7ad849a` | 127923624 — 2026-10-16 12:36:56 WIB | 114,092.25 | 0.00 | 0.0% | SOLD | 97.0% (110,669.48) | catatan: fast dump ≤1j 97.0% |
| 11 | `0xa519765f532d257951527cb464c226f260565554` | 127923625 — 2026-10-16 12:36:56 WIB | 1,324,891.30 | 0.00 | 0.0% | SOLD | 97.0% (1,285,144.56) | catatan: fast dump ≤1j 97.0% |
| 12 | `0xb9d7b477bc3c8b5ab5080ac5b78992a489cb3ddf` | 127923625 — 2026-10-16 12:36:56 WIB | 51,624.56 | 0.00 | 0.0% | SOLD | 97.0% (50,075.83) | catatan: fast dump ≤1j 97.0% |
| 13 | `0x57e10b83bf632ac4ba648c9e001bc225175b614e` | 127923625 — 2026-10-16 12:36:56 WIB | 75,046.74 | 0.00 | 0.0% | SOLD | 97.0% (72,795.34) | catatan: fast dump ≤1j 97.0% |
| 14 | `0xe150e84c14f14f425db1a9fcc77bf4458b64ae6c` | 127923625 — 2026-10-16 12:36:56 WIB | 37,504.02 | 0.00 | 0.0% | SOLD | 97.0% (36,378.90) | catatan: fast dump ≤1j 97.0% |
| 15 | `0x05960f84dcdcdaf5a5c70a6406bb9df42c279be5` | 127923625 — 2026-10-16 12:36:56 WIB | 752,915.51 | 0.00 | 0.0% | SOLD | 97.0% (730,328.05) | catatan: fast dump ≤1j 97.0% |
| 16 | `0xdeebe509353336dd4638221065de6b60b481bbbc` | 127923626 — 2026-10-16 12:36:57 WIB | 1,847,236.95 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 17 | `0x71426138acd48f6fe734a1d3c9752e8383f95cc3` | 127923628 — 2026-10-16 12:36:58 WIB | 183,324.89 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | CORET: kontrak (kode non-kosong) / bot executor |
| 18 | `0x4cd2b32dd9cbdc19b320589409e79ceda2f17640` | 127923632 — 2026-10-16 12:36:59 WIB | 2,506,404.01 | 0.00 | 0.0% | SOLD | 97.0% (2,431,211.89) | catatan: fast dump ≤1j 97.0% |
| 19 | `0xb300000b72deaeb607a12d5f54773d1c19c7028d` | 127923635 — 2026-10-16 12:37:01 WIB | 18,966,064.48 | 0.00 | 0.0% | SOLD | 169.7% (32,190,007.66) | CORET: kontrak (kode non-kosong) / bot executor; catatan: fast dump ≤1j 169.7%; jual > beli awal → token juga masuk lewat transfer non-pair |
| 20 | `0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae` | 127923640 — 2026-10-16 12:37:03 WIB | 4,881,497.59 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | CORET: kontrak (kode non-kosong) / bot executor; linkage LEMAH (co-buy): NIAN,BORT |
| 21 | `0x14e502acca2506030453ec364cf71986d349be4a` | 127923643 — 2026-10-16 12:37:04 WIB | 174,957.47 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 22 | `0xc10ee9031f2a0b84766a86b55a8d90f357910fb4` | 127923646 — 2026-10-16 12:37:06 WIB | 190,361.09 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | CORET: kontrak (kode non-kosong) / bot executor |
| 23 | `0xc2c5547658319366b4427a07b9de948fca604b07` | 127923647 — 2026-10-16 12:37:06 WIB | 26,014.53 | 0.00 | 0.0% | SOLD | 97.0% (25,234.09) | catatan: fast dump ≤1j 97.0% |
| 24 | `0x0da5899dbb36bd741885d4228f04cd9c6304fc56` | 127923648 — 2026-10-16 12:37:07 WIB | 40,308,105.17 | 0.00 | 0.0% | SOLD | 126.1% (50,847,802.93) | CORET: kontrak (kode non-kosong) / bot executor; catatan: fast dump ≤1j 126.1%; jual > beli awal → token juga masuk lewat transfer non-pair |
| 25 | `0x98f58c5ae3920a84be0c9db9a8a6c4964860aabb` | 127923650 — 2026-10-16 12:37:07 WIB | 3,277,230.96 | 0.00 | 0.0% | SOLD | 97.0% (3,178,914.03) | catatan: fast dump ≤1j 97.0% |
| 26 | `0x919ffc964a20a3464b383251be1f1da70d5cf246` | 127923671 — 2026-10-16 12:37:17 WIB | 141,192.41 | 0.00 | 0.0% | SOLD | 97.0% (136,956.63) | catatan: fast dump ≤1j 97.0% |
| 27 | `0x2b75aa1385b9ef2d5cba2bdaeba3f3d31aa8cda6` | 127923685 — 2026-10-16 12:37:23 WIB | 363,270.07 | 0.00 | 0.0% | SOLD | 97.0% (352,371.97) | catatan: fast dump ≤1j 97.0% |
| 28 | `0x6ff39c7d87939b3e177ebc0822b61b45efa9b322` | 127923685 — 2026-10-16 12:37:23 WIB | 123,589.78 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 29 | `0xddac62ff7055675febf1d850e15b6a4dd10f308c` | 127923689 — 2026-10-16 12:37:25 WIB | 216,402.92 | 42.78 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 30 | `0x2cfb4746cc62f3ffef7d55bceb9cf8f899045d7a` | 127923691 — 2026-10-16 12:37:26 WIB | 233,811.13 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |

## IBS

- Token (CA lengkap): `0x255e746abb8d9acac00d6d023e5e63e3b8dfa7cd` — 18 desimal, totalSupply on-chain 3,782,383.82.
- Pair PCS V2 (factory getPair, cocok dengan Gecko): `0x2a4b99a9c4544d35e8d266111c50b67fea01d53d` — pasangan IBS / USDT.
- Pool dibuat (GeckoTerminal): 2026-04-22T05:58:29Z (12:58:29 WIB). MCap saat pilih: $5.202.558 (Trending BSC hal. 4; re-read 17:55 WIB $5.168.100; endpoint pool Gecko 404 (pair dipakai dari factory on-chain)). Reserve pool saat pilih: $13.445.042.
- Blok creation on-chain (binary search header): 93968528. Pindai log pair: blok 93968528 s.d. 94518527 (55 chunk × 10.000 blok, paging Ankr 1000/halaman). Pembeli berbeda yang ditemukan dalam pindaian: 62 (hanya dalam rentang pindai, bukan total pembeli token). Tabel di bawah = 30 pembeli pertama kronologis.
- Pembeli pair pertama: blok 93986267 — 2026-04-22 15:11:42 WIB. Pembeli ke-30: blok 94514682 — 2026-04-25 09:20:21 WIB.
- Catatan khusus: 30 pembeli pertama tersebar ~68 jam (2026-04-22 15:11 WIB s.d. 2026-04-25 09:20 WIB). Hanya 7 wallet dalam ~2 hari pertama, lalu burst 2026-04-25 pagi. Jumlah IBS kecil-kecil (supply hanya ~3,78 jt token) — angka di tabel memakai 4 desimal agar beli awal mungil tidak tampil 0,00.

| # | Wallet (lengkap) | Beli awal (blok — WIB) | Beli awal 6j | Saldo sekarang | % masih dipegang | Status | Jual ke pair ≤1j | Catatan kebersihan |
|---|---|---|---|---|---|---|---|---|
| 1 | `0xc50f7e545722a8ef1e17bc3d382d9a93c5554664` | 93986267 — 2026-04-22 15:11:42 WIB | 65,490.1657 | 0.5597 | 0.0% | SOLD | 0.0% (0.0000) | CORET: kontrak (kode non-kosong) / bot executor |
| 2 | `0xac739056e611d639abeb0b9a87da38bd297ba00e` | 94019033 — 2026-04-22 19:18:04 WIB | 22.9630 | 26,554.0462 | 115638.3% | HOLD (saldo > beli awal) | 0.0% (0.0000) | saldo > beli awal → akumulasi/transfer masuk lanjutan |
| 3 | `0x6e94ae13d5776264c9f6831a769d6fbf63f6cc08` | 94019033 — 2026-04-22 19:18:04 WIB | 0.0023 | 0.0000 | 0.0% | SOLD | 97.5% (0.0022) | CORET: kontrak (kode non-kosong) / bot executor; catatan: fast dump ≤1j 97.5% |
| 4 | `0xd000a55d5bdb432806f091a47ad9a3a02c8a74a2` | 94159151 — 2026-04-23 12:50:09 WIB | 4.2716 | 0.0000 | 0.0% | SOLD | 78.2% (3.3383) | CORET: kontrak (kode non-kosong) / bot executor |
| 5 | `0x35dcf62a8dea2087f38e59968ceb8c11d546a2cc` | 94177188 — 2026-04-23 15:05:35 WIB | 0.0048 | 0.0000 | 0.0% | SOLD | 97.5% (0.0047) | CORET: kontrak (kode non-kosong) / bot executor; catatan: fast dump ≤1j 97.5% |
| 6 | `0x004202d0b1759bcdbd939bc5a2bfbceed9dd34b1` | 94369715 — 2026-04-24 15:11:24 WIB | 0.0108 | 0.0000 | 0.0% | SOLD | 0.0% (0.0000) | CORET: kontrak (kode non-kosong) / bot executor |
| 7 | `0xcba922f6aff0ec8cb0703d44249456ef779a394c` | 94400464 — 2026-04-24 19:02:21 WIB | 0.3656 | 0.0000 | 0.0% | SOLD | 273.5% (1.0000) | CORET: kontrak (kode non-kosong) / bot executor; catatan: fast dump ≤1j 273.5%; jual > beli awal → token juga masuk lewat transfer non-pair |
| 8 | `0x72bc5e76bb005f4881fdada7d0c4077425dd8f54` | 94512406 — 2026-04-25 09:03:15 WIB | 326.1964 | 0.0000 | 0.0% | SOLD | 0.0% (0.0000) | CORET: kontrak (kode non-kosong) / bot executor |
| 9 | `0xdbbf67f1ce7b97542fc1d650aa4d72fcf351b07d` | 94513073 — 2026-04-25 09:08:16 WIB | 15.9743 | 0.0000 | 0.0% | SOLD | 0.0% (0.0000) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 10 | `0xd595a6170454943ec9ed486d5b4da0594a479e3e` | 94513082 — 2026-04-25 09:08:20 WIB | 8.3072 | 0.0000 | 0.0% | SOLD | 0.0% (0.0000) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 11 | `0xf0d57125f1eb49bace6e635829ad3884782f3d50` | 94513335 — 2026-04-25 09:10:14 WIB | 28.2812 | 0.0001 | 0.0% | SOLD | 0.8% (0.2386) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 12 | `0xda367e639752c004026ba1f90948b10f44c81bc1` | 94513361 — 2026-04-25 09:10:25 WIB | 3.7621 | 0.0229 | 0.6% | PARTIAL | 0.0% (0.0000) | CORET: kontrak (kode non-kosong) / bot executor; PARTIAL hanya 0,6% dengan saldo 0,02 token — de facto debu (di atas ambang 0,5% karena beli awal sangat kecil) + kontrak → CORET |
| 13 | `0x48064d01870261296504cbd8ed9aba95c86c0e44` | 94513501 — 2026-04-25 09:11:28 WIB | 0.1686 | 0.0000 | 0.0% | SOLD | 0.0% (0.0000) | CORET: kontrak (kode non-kosong) / bot executor |
| 14 | `0x7d29c93196db0028aa738df352553f8d79ed3d87` | 94513581 — 2026-04-25 09:12:05 WIB | 7.9706 | 0.0000 | 0.0% | SOLD | 0.0% (0.0000) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 15 | `0xb34dd06401e3ee15e3d018aaacc98c1d514755f4` | 94513774 — 2026-04-25 09:13:32 WIB | 35.1438 | 0.0002 | 0.0% | SOLD | 6.3% (2.2124) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 16 | `0xede84b4111d228d1c17606443f44749b7defa611` | 94513790 — 2026-04-25 09:13:39 WIB | 49.8408 | 0.0000 | 0.0% | SOLD | 0.0% (0.0000) | CORET: kontrak (kode non-kosong) / bot executor |
| 17 | `0x7c2d304ae29c3f7affc09dbdd596ec2e8f96c910` | 94513808 — 2026-04-25 09:13:47 WIB | 0.7814 | 0.0000 | 0.0% | SOLD | 0.0% (0.0000) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 18 | `0xb1c1be04692a94ea56f9108369c9f2cc95821233` | 94513889 — 2026-04-25 09:14:23 WIB | 17.8574 | 0.0002 | 0.0% | SOLD | 13.6% (2.4245) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 19 | `0xd1c81fbc783827eaeeee805ab6eb218b60684474` | 94514032 — 2026-04-25 09:15:28 WIB | 28.9010 | 0.0002 | 0.0% | SOLD | 14.1% (4.0732) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 20 | `0x2f26092f84cf6b0659b59cfd58ff4e9ac3ed1e52` | 94514034 — 2026-04-25 09:15:29 WIB | 0.5158 | 0.0000 | 0.0% | SOLD | 0.0% (0.0000) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 21 | `0x6de66a684c4af24066c37432cda2a4a73005c525` | 94514103 — 2026-04-25 09:16:00 WIB | 2.6242 | 0.0000 | 0.0% | SOLD | 0.0% (0.0000) | CORET: kontrak (kode non-kosong) / bot executor |
| 22 | `0xb6a97c7b3d463ddaafa5cde66d32f3d59948507f` | 94514205 — 2026-04-25 09:16:46 WIB | 20.9703 | 0.0001 | 0.0% | SOLD | 0.0% (0.0000) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 23 | `0x60743db31e3f25188e023153a4b868b9d8c62a37` | 94514236 — 2026-04-25 09:17:00 WIB | 1.5659 | 0.0000 | 0.0% | SOLD | 0.0% (0.0000) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 24 | `0x554d2edee034bd848cd8fb73e4b57a7a53adb6b0` | 94514332 — 2026-04-25 09:17:43 WIB | 35.6826 | 0.0000 | 0.0% | SOLD | 0.0% (0.0000) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 25 | `0x5b7375ae1cbae2da888e001efd01a816e06a7bea` | 94514363 — 2026-04-25 09:17:57 WIB | 24.0410 | 0.0001 | 0.0% | SOLD | 19.3% (4.6430) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 26 | `0x981e243e0246c3a6de3062e5f5a9a929e7ede4e1` | 94514432 — 2026-04-25 09:18:28 WIB | 1.1676 | 0.0000 | 0.0% | SOLD | 0.0% (0.0000) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 27 | `0x28feb067dc590b735a75e19279ed5b56d5cef580` | 94514490 — 2026-04-25 09:18:54 WIB | 22.5648 | 0.0000 | 0.0% | SOLD | 0.0% (0.0000) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 28 | `0xb079b66f518f3adfdd19f64765c92241df6092bb` | 94514507 — 2026-04-25 09:19:02 WIB | 0.4766 | 0.0000 | 0.0% | SOLD | 0.0% (0.0000) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 29 | `0x860083f17b9b4c0aec91c1a00b749634d100f9b7` | 94514649 — 2026-04-25 09:20:06 WIB | 1.5817 | 0.0000 | 0.0% | SOLD | 0.0% (0.0000) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 30 | `0xeb64fd01bf77e8337a928d24334aac758617a20e` | 94514682 — 2026-04-25 09:20:21 WIB | 3.8275 | 0.0000 | 0.0% | SOLD | 0.0% (0.0000) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |

## MAME

- Token (CA lengkap): `0x39d9b36aa0e7a1fee97d6ff614420f7308ba7777` — 18 desimal, totalSupply on-chain 1,000,000,000.00.
- Pair PCS V2 (factory getPair, cocok dengan Gecko): `0xf75cdee96765c6d230528c247fc21d11f9f3927a` — pasangan MAME / B13B (0x4902c5ebc598265ed2212b559b042de8a5eeec3f).
- Pool dibuat (GeckoTerminal): 2026-09-24T16:11:24Z (23:11:24 WIB). MCap saat pilih: $1.494.420 (re-read endpoint pool; trending hal. 5: $1.484.393) (Trending BSC hal. 5 + endpoint pool). Reserve pool saat pilih: $122.536.
- Blok creation on-chain (binary search header): 123786691. Pindai log pair: blok 123786691 s.d. 123796690 (1 chunk × 10.000 blok, paging Ankr 1000/halaman). Pembeli berbeda yang ditemukan dalam pindaian: 1067 (hanya dalam rentang pindai, bukan total pembeli token). Tabel di bawah = 30 pembeli pertama kronologis.
- Pembeli pair pertama: blok 123786691 — 2026-09-24 23:11:24 WIB. Pembeli ke-30: blok 123786692 — 2026-09-24 23:11:24 WIB.
- Catatan khusus: 30 pembeli pertama semuanya membeli pada blok creation itu sendiri / blok berikutnya (semua dalam detik yang sama, 2026-09-24 23:11:24 WIB). Wallet #2–#24 sold-to-pair ≤1j = 0% tetapi saldo sekarang 0 — mereka keluar setelah 1 jam dan/atau lewat transfer non-pair, bukan pemegang.

| # | Wallet (lengkap) | Beli awal (blok — WIB) | Beli awal 6j | Saldo sekarang | % masih dipegang | Status | Jual ke pair ≤1j | Catatan kebersihan |
|---|---|---|---|---|---|---|---|---|
| 1 | `0x39d9b36aa0e7a1fee97d6ff614420f7308ba7777` | 123786691 — 2026-09-24 23:11:24 WIB | 9,604,791.07 | 100,107.90 | 1.0% | PARTIAL | 0.0% (0.00) | CORET: kontrak (kode non-kosong) / bot executor; alamat ini = kontrak token itu sendiri |
| 2 | `0x7a02c9d5e9c0bf03efdcfe43104442dda4a2137a` | 123786691 — 2026-09-24 23:11:24 WIB | 8,911,494.22 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 3 | `0x80f43209009aa6357e98f04841d0cfc771caa369` | 123786691 — 2026-09-24 23:11:24 WIB | 10,770,991.73 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 4 | `0x57e6c0fb4c051ee498988ed2ce1e1260eccada88` | 123786691 — 2026-09-24 23:11:24 WIB | 679,009.70 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 5 | `0xafc1623b687efa6c1872f01ab359c1d97137e108` | 123786691 — 2026-09-24 23:11:24 WIB | 4,348,405.42 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 6 | `0x644ce141fbf85cba4eb2c13f402c18a0aec5d2e3` | 123786691 — 2026-09-24 23:11:24 WIB | 9,395,500.60 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 7 | `0x8ad9a41acde830c4c48ae53dbf19f375f62b9d83` | 123786691 — 2026-09-24 23:11:24 WIB | 2,557,152.07 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 8 | `0x838869b295cc9d0576910b9f2d9713226ffd3f88` | 123786691 — 2026-09-24 23:11:24 WIB | 908,633.72 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 9 | `0x0fd78d724b5c3af4bd4fec79a7a57e85b51172cf` | 123786691 — 2026-09-24 23:11:24 WIB | 5,876,805.75 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 10 | `0x1bd157cff65d062856f080d3c0871a01f62ff085` | 123786691 — 2026-09-24 23:11:24 WIB | 440,817.36 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 11 | `0x78cd3970e1a9a7d58b80e18f42bf7d3162d5ffe0` | 123786691 — 2026-09-24 23:11:24 WIB | 1,907,746.20 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 12 | `0x7199dab61b1747a78f9b489a3e7b8863413450e2` | 123786691 — 2026-09-24 23:11:24 WIB | 8,517,624.66 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 13 | `0x50d19d2d6558a6eb01e10d36a1c3bd408887be42` | 123786691 — 2026-09-24 23:11:24 WIB | 1,803,552.64 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 14 | `0x6a43c6144bfdd77999edd2803c8bd2ebcc4a45cc` | 123786691 — 2026-09-24 23:11:24 WIB | 797,737.13 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 15 | `0xd1ee0c7aa82e2aa90bdc538b6fe0bddff696fa93` | 123786691 — 2026-09-24 23:11:24 WIB | 8,212,091.18 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 16 | `0x2d4904710e7d5f0f33017489cc8a1c2f41249578` | 123786691 — 2026-09-24 23:11:24 WIB | 1,069,431.38 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 17 | `0x72ef6c6dccf3e819e774f77ca5dc5145e58b02d8` | 123786691 — 2026-09-24 23:11:24 WIB | 5,532,939.68 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 18 | `0x09cd8f07a712f4660ed2190ab1e350418d984847` | 123786691 — 2026-09-24 23:11:24 WIB | 1,634,646.39 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 19 | `0x4101f1fe5d78cbdb33b02d924d31629542731d08` | 123786691 — 2026-09-24 23:11:24 WIB | 4,333,517.28 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 20 | `0xe56180f0abbfe70168c1f80fdd7f863efcb33917` | 123786691 — 2026-09-24 23:11:24 WIB | 1,504,044.42 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 21 | `0x4be7200a60b7ecc9ab925f4209a247694e9dc8da` | 123786691 — 2026-09-24 23:11:24 WIB | 3,538,642.07 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 22 | `0xc14e2dda63cc4d58325d0b300002fa92911911f3` | 123786691 — 2026-09-24 23:11:24 WIB | 4,054,639.03 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 23 | `0x96ea22033f47d923077b72d928b2d8b26b2b0979` | 123786691 — 2026-09-24 23:11:24 WIB | 1,962,274.44 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 24 | `0x71dc3742e18b4791bc5d6a7dceef4a395a4fd813` | 123786691 — 2026-09-24 23:11:24 WIB | 4,880,140.73 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 25 | `0x36f4b7cc58bdfd38e4163b1ef68d074dab6847d6` | 123786692 — 2026-09-24 23:11:24 WIB | 14,824,197.04 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | CORET: kontrak (kode non-kosong) / bot executor |
| 26 | `0x2434109453e5430e22f68572d5e2d4563b105d53` | 123786692 — 2026-09-24 23:11:24 WIB | 22,631,701.74 | 0.00 | 0.0% | SOLD | 52.8% (11,951,928.43) | CORET: kontrak (kode non-kosong) / bot executor |
| 27 | `0x0368a6aab8810d6cf5d35e309f797a04b65fcce5` | 123786692 — 2026-09-24 23:11:24 WIB | 1,377,563.33 | 0.00 | 0.0% | SOLD | 49.5% (681,893.85) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 28 | `0x2340173e4d194b87c934eb3ae0d22aed9d22e6d6` | 123786692 — 2026-09-24 23:11:24 WIB | 268,684.64 | 0.00 | 0.0% | SOLD | 99.0% (265,997.80) | CORET: kontrak (kode non-kosong) / bot executor; catatan: fast dump ≤1j 99.0% |
| 29 | `0x6b352fa008520ff1f9abfeedd65f06c6a2b21c54` | 123786692 — 2026-09-24 23:11:24 WIB | 352,805.54 | 0.00 | 0.0% | SOLD | 67.3% (237,527.63) | CORET: kontrak (kode non-kosong) / bot executor |
| 30 | `0x658a34dba63c548d0d69224d7a02732e87cb8982` | 123786692 — 2026-09-24 23:11:24 WIB | 66,331.32 | 0.00 | 0.0% | SOLD | 99.0% (65,668.01) | CORET: kontrak (kode non-kosong) / bot executor; catatan: fast dump ≤1j 99.0% |

## BORT

- Token (CA lengkap): `0x2a846aaaf896ef393ccb76398c1d96ea97374444` — 18 desimal, totalSupply on-chain 1,000,000,000.00.
- Pair PCS V2 (factory getPair, cocok dengan Gecko): `0x76c42dda1de814ac60951c2c89c77dbecfb86ffb` — pasangan BORT / WBNB.
- Pool dibuat (GeckoTerminal): 2025-11-04T16:45:10Z (23:45:10 WIB). MCap saat pilih: $1.202.619 (Trending BSC hal. 5). Reserve pool saat pilih: $226.354.
- Blok creation on-chain (binary search header): 67031682. Pindai log pair: blok 67031682 s.d. 67041681 (1 chunk × 10.000 blok, paging Ankr 1000/halaman). Pembeli berbeda yang ditemukan dalam pindaian: 838 (hanya dalam rentang pindai, bukan total pembeli token). Tabel di bawah = 30 pembeli pertama kronologis.
- Pembeli pair pertama: blok 67031684 — 2025-11-04 23:45:11 WIB. Pembeli ke-30: blok 67031710 — 2025-11-04 23:45:31 WIB.
- Catatan khusus: pasangan wallet #29/#30 (17 buy, ~148,47 ribu, sold ≤1j 72,1%, saldo sama persis 26,87) menunjukkan pola identik — observasi saja, bukan bukti linkage KUAT.

| # | Wallet (lengkap) | Beli awal (blok — WIB) | Beli awal 6j | Saldo sekarang | % masih dipegang | Status | Jual ke pair ≤1j | Catatan kebersihan |
|---|---|---|---|---|---|---|---|---|
| 1 | `0xdef96579f52be373f150e2e0e59b92b37b77d151` | 67031684 — 2025-11-04 23:45:11 WIB | 11,661,165.62 | 0.00 | 0.0% | SOLD | 100.0% (11,661,165.62) | CORET: kontrak (kode non-kosong) / bot executor; catatan: fast dump ≤1j 100.0% |
| 2 | `0xf862bf8b141d85eb933583af3fb7f22a1f6517c0` | 67031684 — 2025-11-04 23:45:11 WIB | 1,282,320.45 | 0.00 | 0.0% | SOLD | 72.6% (930,936.24) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 3 | `0xdb22abc985553332d614ec2d429258618861d9f5` | 67031684 — 2025-11-04 23:45:11 WIB | 508,620.61 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 4 | `0x38fb583d3a797219651eb960fdbdeb31f8ec7a18` | 67031684 — 2025-11-04 23:45:11 WIB | 51,188,688.66 | 2,240.46 | 0.0% | SOLD | 86.1% (44,049,717.20) | CORET: kontrak (kode non-kosong) / bot executor; catatan: fast dump ≤1j 86.1% |
| 5 | `0x144d395b5562c742259932d2ee6e1d8d092a21b8` | 67031684 — 2025-11-04 23:45:11 WIB | 1,352.51 | 1,350.51 | 99.9% | HOLD | 0.0% (0.00) | CORET: kontrak (kode non-kosong) / bot executor |
| 6 | `0x608fb862b86687e605bb85d1a78b22b196410fec` | 67031685 — 2025-11-04 23:45:12 WIB | 789,074.52 | 0.00 | 0.0% | SOLD | 183.8% (1,450,417.10) | catatan: fast dump ≤1j 183.8%; jual > beli awal → token juga masuk lewat transfer non-pair |
| 7 | `0xccccadca4671e6989a0c0c6c5065b31aa3212a18` | 67031685 — 2025-11-04 23:45:12 WIB | 157,182.81 | 0.00 | 0.0% | SOLD | 100.0% (157,182.81) | CORET: kontrak (kode non-kosong) / bot executor; catatan: fast dump ≤1j 100.0% |
| 8 | `0xcd06af254d0da9dbf95f62a75361c4cab182f13b` | 67031685 — 2025-11-04 23:45:12 WIB | 313,737.68 | 137,264.53 | 43.8% | PARTIAL | 56.2% (176,473.15) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 9 | `0x8d2e9e9d2e3d73567a578bf1fd15766caf5cb62c` | 67031686 — 2025-11-04 23:45:13 WIB | 547,034.85 | 0.00 | 0.0% | SOLD | 100.0% (547,034.85) | catatan: fast dump ≤1j 100.0% |
| 10 | `0x4011b7a4bae37f6ecb0565b479b100e426e6f0d2` | 67031686 — 2025-11-04 23:45:13 WIB | 40,410.54 | 0.00 | 0.0% | SOLD | 100.0% (40,410.54) | catatan: fast dump ≤1j 100.0% |
| 11 | `0x0d4eca97c066961e0caa10608a0736f858dd13e6` | 67031687 — 2025-11-04 23:45:13 WIB | 129,780,772.47 | 0.00 | 0.0% | SOLD | 57.4% (74,463,971.82) | CORET: kontrak (kode non-kosong) / bot executor |
| 12 | `0x50d373194725059c979ecaa3ab77292a95482a2c` | 67031687 — 2025-11-04 23:45:13 WIB | 936,177.68 | 0.00 | 0.0% | SOLD | 76.0% (711,401.42) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 13 | `0x79e337339346c9f5786a746916a0600d3f9eda65` | 67031687 — 2025-11-04 23:45:13 WIB | 311,028.89 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | CORET: kontrak (kode non-kosong) / bot executor |
| 14 | `0xac8fc4e7b39b6e1e868ad77b35efbc0baefaa1cf` | 67031687 — 2025-11-04 23:45:13 WIB | 928,158.71 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 15 | `0xe743a17f56eb09cd1bf904522ad03972280fb497` | 67031688 — 2025-11-04 23:45:14 WIB | 1,514,731.28 | 0.00 | 0.0% | SOLD | 100.0% (1,514,731.28) | catatan: fast dump ≤1j 100.0% |
| 16 | `0xdf82debfd3304e33979b4d790aaaf89eb70c8ff0` | 67031688 — 2025-11-04 23:45:14 WIB | 23,836,104.80 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | CORET: kontrak (kode non-kosong) / bot executor |
| 17 | `0x7e9b08d737534aff2e56a4fca3aac0746cd73540` | 67031689 — 2025-11-04 23:45:15 WIB | 21,627,922.90 | 0.00 | 0.0% | SOLD | 51.1% (11,050,346.06) | CORET: kontrak (kode non-kosong) / bot executor |
| 18 | `0xd547eafde2410e63300fc5308ccea0b356e7b5d8` | 67031689 — 2025-11-04 23:45:15 WIB | 461,100.86 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | CORET: kontrak (kode non-kosong) / bot executor |
| 19 | `0x7f9533efcc4ff9ca467af7ed3c6cf7fadd4f5d09` | 67031690 — 2025-11-04 23:45:16 WIB | 43,477.69 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 20 | `0x148951b28c53a37f72c97229e756ea31b421e4b8` | 67031691 — 2025-11-04 23:45:16 WIB | 2,130,423.61 | 0.00 | 0.0% | SOLD | 100.0% (2,130,423.61) | catatan: fast dump ≤1j 100.0% |
| 21 | `0xca2743a3069c02cea913ca12c33285637db0f058` | 67031691 — 2025-11-04 23:45:16 WIB | 9,952.21 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 22 | `0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae` | 67031694 — 2025-11-04 23:45:19 WIB | 81,687,665.00 | 0.00 | 0.0% | SOLD | 126.9% (103,666,333.87) | CORET: kontrak (kode non-kosong) / bot executor; catatan: fast dump ≤1j 126.9%; jual > beli awal → token juga masuk lewat transfer non-pair; linkage LEMAH (co-buy): NIAN,BORT |
| 23 | `0x00e9dbe4dea05363b7d4e285ddf010c595873d57` | 67031695 — 2025-11-04 23:45:19 WIB | 262,238.97 | 0.00 | 0.0% | SOLD | 381.4% (1,000,084.51) | catatan: fast dump ≤1j 381.4%; jual > beli awal → token juga masuk lewat transfer non-pair |
| 24 | `0xa4a9c3128263243b85383561c0fb41c9a1ded545` | 67031697 — 2025-11-04 23:45:21 WIB | 18,574,098.89 | 0.00 | 0.0% | SOLD | 100.0% (18,574,098.89) | catatan: fast dump ≤1j 100.0% |
| 25 | `0x5ce8ec5c4d2a0b9d53a4a381c263998e1b9b4b28` | 67031699 — 2025-11-04 23:45:22 WIB | 5,063,277.68 | 0.00 | 0.0% | SOLD | 100.0% (5,063,277.68) | catatan: fast dump ≤1j 100.0% |
| 26 | `0xe3be4ead0082bc0ed53e8fe796b8bf219ad6bd5c` | 67031705 — 2025-11-04 23:45:27 WIB | 71,883.60 | 0.00 | 0.0% | SOLD | 0.0% (0.00) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 27 | `0xcdc2ed61261baa1733c5399734672443da9b1a80` | 67031706 — 2025-11-04 23:45:28 WIB | 240,049.39 | 0.00 | 0.0% | SOLD | 100.0% (240,049.39) | catatan: fast dump ≤1j 100.0% |
| 28 | `0xde56d95b9a30e944950728fda2d3d3b312bf6c26` | 67031707 — 2025-11-04 23:45:28 WIB | 2,576.53 | 0.00 | 0.0% | SOLD | 100.0% (2,576.53) | catatan: fast dump ≤1j 100.0% |
| 29 | `0x88240079221a8b66f9202979bbdd8523cd631292` | 67031710 — 2025-11-04 23:45:31 WIB | 148,480.30 | 26.87 | 0.0% | SOLD | 72.1% (107,080.15) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |
| 30 | `0xb4d2a713df19c906fe9e0fb0412396f44319e6d8` | 67031710 — 2025-11-04 23:45:31 WIB | 148,468.28 | 26.87 | 0.0% | SOLD | 72.1% (107,065.25) | bersih dalam cakupan cek ini (bukan kontrak, tanpa fast dump ≤1j, bukan daftar coret) |

## Batas dan pernyataan kejujuran (penutup)

- Tidak ada PnL 30 hari terverifikasi untuk wallet mana pun di laporan ini. Yang ada hanya proxy: beli awal dari pair + saldo sekarang + jual ke pair ≤1 jam. Harga beli/jual per wallet tidak ada di log Transfer.
- Tidak ada klaim 'terbukti insider' untuk wallet mana pun. Linkage KUAT (shared funding / transfer langsung) tidak ditemukan dalam cakupan ini; satu-satunya linkage yang dilaporkan adalah co-buy LEMAH untuk `0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae` (NIAN + BORT, kontrak di keduanya → tetap CORET).
- Aturan coret lintas ≥3 launch tidak terpicu oleh dataset ini (tidak ada wallet yang fast-dump di ≥2 koin dari kelima ini). Untuk memakai wallet di atas sebagai referensi, penelusuran lintas launch yang lebih luas tetap diperlukan — laporan ini bukan promosi wallet.
- Metode Transfer buta terhadap transfer BNB native dan call tanpa event; saldo sekarang dapat mencakup transfer masuk non-pair; % masih dipegang adalah proxy.
- Alamat terpotong yang sempat muncul pada tahap kerja awal dinyatakan VOID dan tidak dipakai di laporan ini; semua alamat di atas lengkap.
- Tidak ada file state/feed/cron yang diubah. File ini adalah satu-satunya output.
