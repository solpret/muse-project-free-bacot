# Log Pemantau Tier A+B (internal, SENYAP ke chat)

## Run 1 — Sabtu 2026-10-31, 23:22–23:40 WIB (run pertama cron ini)

- Daftar dibaca dari `tier-ab-watch.md` setiap run: 14 EOA privat (Tier A privat 13 + Tier B privat 1).
  Daftar lama 23 alamat TIDAK dipakai (6 wallet exchange + 3 kontrak sudah dipindah ke Tier E).
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Text fetch GMGN hanya mengembalikan shell generik situs (bukan data wallet), jadi dipakai
  pemeriksaan browser live read-only dengan instruksi eksplisit: bila login-gated, catat saja
  dan lanjut, JANGAN klik login.
- Hasil pemeriksaan browser: browser mengunjungi ke-14 halaman wallet GMGN BSC secara berurutan
  (teramati lewat judul tab: halaman memuat data wallet, mis. "30D Realized Profit" tampil untuk
  beberapa wallet — BUKAN tampilan "You are not logged in"). Jendela browser kemudian tertutup.
- GAP YANG DICATAT JUJUR: laporan per-wallet terperinci (holdings + trade terbaru per wallet)
  dari browser BELUM terkirim ke konteks run ini pada saat penulisan log, meski jendela sudah
  tertutup dua kali (kunjungan awal + permintaan pengiriman laporan). Karena itu:
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA sinyal (ambang: minimal 4 entitas privat berbeda membeli token baru yang sama).
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline holdings per wallet BELUM terbentuk — state sebelumnya kosong (last_checked null),
    jadi run ini TIDAK BOLEH dipakai sebagai pembanding "token baru vs lama" untuk run berikutnya
    sampai holdings per wallet benar-benar tercatat.
- Kesimpulan run ini: TIDAK ADA SINYAL. Bukan karena wallet terbukti tidak membeli, melainkan
  karena bukti per-wallet belum diterima — wallet yang tidak terbaca datanya TIDAK dianggap
  tidak membeli, sesuai aturan run.
- Tindak lanjut: run berikutnya (interval 2 jam) harus mengulang pembacaan ke-14 wallet dan
  mencatat holdings + aktivitas terbaru per wallet secara eksplisit sebelum menghitung sinyal
  apa pun. Bila laporan browser dari run ini tiba belakangan, tambahkan sebagai adendum run ini
  dengan stempel waktu penerimaan, jangan menimpa kesimpulan di atas tanpa bukti.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Adendum Run 1 — laporan browser diterima Sabtu 2026-10-31 ~23:41 WIB

Pemeriksaan browser terukur 23:24–23:32 WIB (bukan klaim waktu di dalam laporan). Semua 14 halaman
memuat data publik TANPA login-gated, tanpa klik Log in/Sign up/Connect, tanpa sign/transaksi.
Koreksi atas bagian "GAP" di atas: bukti per-wallet AKHIRNYA diterima, sehingga baseline run 1
dapat ditetapkan dari laporan ini. Batasan laporan yang wajib dicatat:
- Tab Holdings GMGN memakai filter default "Hide Didn't Buy": token yang hanya diterima lewat
  Tx In TIDAK tampil di Holdings. "Tidak ada aset yang ditampilkan" = sesuai tampilan tab itu,
  BUKAN klaim saldo on-chain nol.
- Contract address HANYA terverifikasi untuk 2 token di wallet 1 (CZ dan CT PACKS, dari tautan
  token); CA token lain TIDAK ditebak dari simbol dan tidak dicatat sebagai CA.
- Waktu aktivitas bersifat relatif terhadap ~23:32 WIB ("menit lalu", "hari lalu") seperti
  dilaporkan browser, bukan stempel waktu absolut yang diverifikasi on-chain.

Per-wallet (urutan sesuai tier-ab-watch.md; nilai seperti dilaporkan GMGN):
1. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — BNB 0,057 ($40,23). Holdings tampil: CZ $4,14 /
   551,1K (CA 0xaaf020aa16449b342cb09d0107cabf9b2dd57777); MAX $4,27 / 655,6K; CT PACKS $2,63 /
   605,1K (CA 0xa92df72e93d8a0d5fc03b37f3f69679c4b867777); 币安守护 $3,57 / 631,7K; SAT $3,98 /
   942,1K; 安心 $4,54 / 609,4K; MAX $3,38 / 945,5K; MAX $2,40 / 674,7K; MAX $2,45 / 737,6K;
   视界之眼 $3,21 / 467,3K. Buy terbaru: CZ 551,1K $4,15 (43 detik lalu); MAX 655,6K $4,178
   (1 menit lalu); CT PACKS 605,1K $4,19 (4 menit lalu); 币安守护 631,7K $4,104 (4 menit lalu).
   Ukuran buy sangat kecil (~$4) — dicatat apa adanya, bukan dinilai sebagai sinyal kuat.
2. 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02 — Holdings: tidak ada aset tampil; BNB 0 ($0,008);
   7D TXs 0/0. Aktivitas terbaru semuanya Tx In, tanpa Buy (terbaru 46 hari lalu).
3. 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5 — Holdings: "No assets held."; BNB 0 ($0,014);
   7D TXs 0/0. Aktivitas terbaru semuanya Tx In, tanpa Buy (terbaru 46 hari lalu).
4. 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7 — Holdings: tidak ada aset tampil; BNB 0,001
   ($1,05). 10 aktivitas terbaru tanpa Buy (Tx In/Tx Out, terbaru 2 hari lalu).
5. 0x75642756e4ba4cc8fbe76df2239cada046cfc854 — Holdings: "No assets held."; BNB 0 ($0,03);
   7D TXs 0/0. Aktivitas terbaru semuanya Tx In, tanpa Buy (terbaru 33 hari lalu).
6. 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a — Holdings: tidak ada aset tampil; BNB 0 ($0,011);
   7D TXs 0/0. 7 aktivitas total, semuanya Tx In, tanpa Buy; termasuk Tx In SKYAI +2,7M
   (126 hari lalu) — itu holding/transfer lama, BUKAN pembelian baru, tidak dihitung.
7. 0x892200223bdfb11d2506c5ab1cae9222ce253acc — Holdings tampil: XPIN $258,3K / 323,1M; WKC
   $1,01K / 17,9B; XRP $37,7K / 30.069,58; SLX $10,7K / 242,4K; BANK $4,79K / 182,3K; SKYAI
   $186,3K / 5,9M; CREPE $126,7K / 14,4B; TAG $157,52 / 215,8K; PENGU $52,2K / 7,1M; elizaOS
   $862,28 / 3,4M. Aktivitas terbaru: Tx In (2 dan 10 hari lalu); Buy XPIN 5,8M $4,2K
   (15 hari lalu). SKYAI di sini holding lama, bukan pembelian baru.
8. 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c — Holdings: tidak ada aset tampil; BNB 0 ($0,01);
   7D TXs 0/0. 6 aktivitas total, semuanya Tx In, tanpa Buy; termasuk Tx In SKYAI +4,6M
   (125 hari lalu) — holding lama, bukan pembelian baru.
9. 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e — Holdings: "No assets held."; BNB 0 ($0).
   2 aktivitas total, semuanya Tx In SKYAI (5 hari lalu) — transfer masuk, bukan Buy yang
   terverifikasi sebagai pembelian baru.
10. 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462 — Holdings: tidak ada aset tampil; BNB 0,007
    ($4,84). 1 aktivitas total: Tx In SKYAI +24,8M (12 hari lalu) — bukan Buy.
11. 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf — Holdings: "No assets held."; BNB 0 ($0);
    7D TXs 0/0. Aktivitas terbaru semuanya Tx In, tanpa Buy (terbaru 46 hari lalu).
12. 0xda91cefe240175e6fab56271110427a4195ab71f — Holdings: tidak ada aset tampil; BNB 0,05
    ($35,3). 10 aktivitas terbaru tanpa Buy; termasuk Tx In/Tx Out mubarak (11–19 hari lalu) —
    itu holding/transfer lama, BUKAN pembelian baru, tidak dihitung.
13. 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc — Holdings: "No assets held."; BNB 0 ($0);
    7D TXs 0/0. Aktivitas terbaru semuanya Tx In, tanpa Buy (terbaru 10 hari lalu).
14. 0x2325f175975abdbcde555c79cc8e63381d28551b — BNB 0,449 ($317,15); 7D TXs 100/94; win rate
    7D 50%. Holdings teratas tampil: 盘古重生 $70,09 / 15,2M; PTG $102,83 / 34,29. 10 aktivitas
    terbaru: Buy 盘古重生 15,2M $67,37 (2 menit lalu); Sell 盘古重生 13,4M $57,12 (2 menit lalu);
    Sell 莫大回归 12,1M $67,24 (6 menit lalu); Buy 盘古重生 13,4M $67,52 (7 menit lalu);
    Buy 莫大回归 12,1M $66,8 (10 menit lalu); Sell 币安人生 13,8M $93,4 (34 menit lalu);
    Buy 币安人生 13,8M $67,9 (37 menit lalu); Sell GPAY 8,1M $105,4 (1 jam lalu);
    Sell 7JAGENT 13,2M $63,83 (1 jam lalu); Buy GPAY 8,3M $69,87 (1 jam lalu).

Hitungan sinyal run 1 (entitas, bukan alamat mentah):
- Token dengan Buy teramati: wallet 1 = CZ, MAX, CT PACKS, 币安守护 (masing-masing 1 entitas);
  wallet 7 = XPIN (1 entitas, 15 hari lalu — dicatat sebagai baseline, bukan buy dalam jendela
  run ini); wallet 14 = 盘古重生, 莫大回归, 币安人生, GPAY (masing-masing 1 entitas).
- TIDAK ADA token yang dibeli oleh 2 wallet atau lebih dalam laporan ini, apalagi 4.
  Jadi TIDAK ADA SINYAL (ambang: minimal 4 entitas privat berbeda membeli token baru yang sama).
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada
  runtuhan entitas. Co-buy/co-hold saja tidak meruntuhkan entitas (dan di sini bahkan tidak ada
  co-buy yang sama).
- Pembelian 1 wallet saja = bukan sinyal, hanya dicatat di atas.
- Status baseline: DITETAPKAN oleh adendum ini (holdings tampil + buy teramati per wallet di
  atas). Run berikutnya membandingkan terhadap baseline ini; token yang sudah tampil di sini
  bukan lagi "token baru" bagi wallet tersebut.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 2 — Minggu 2026-11-01, 01:23–01:38 WIB

- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat (Tier A privat 13 + Tier B privat 1).
  Daftar lama 23 alamat TIDAK dipakai.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-14 halaman GMGN BSC (URL https://gmgn.ai/bsc/address/<alamat>),
  status semua halaman "Disconnected". Semua halaman memuat data publik — TIDAK ADA yang login-gated.
- Batasan yang wajib dicatat:
  - Tab Holdings memakai filter default "Hide Didn't Buy" (plus "Hide Tiny Pool", "Hide Honeypot",
    "Hide Closed" di beberapa halaman): "No assets held." = tidak ada aset yang dibeli yang masih
    dipegang menurut filter itu, BUKAN klaim saldo on-chain nol; token yang hanya diterima lewat
    Tx In tersaring dari Holdings.
  - CA token TIDAK tercatat pada run ini: tautan token di tampilan halaman tidak menampilkan
    alamat kontrak lengkap dalam bentuk teks yang dapat dikutip; CA tidak ditebak dari simbol.
    Token baru dicatat berdasarkan simbol saja, dan karena itu TIDAK dapat dipakai sebagai
    CA terverifikasi untuk perbandingan antar wallet — hitungan sinyal di bawah ini memakai
    simbol + konteks baseline, dan tidak ada token yang lolos sebagai CA sama antar wallet.
  - Waktu aktivitas bersifat relatif terhadap waktu baca ("menit/jam lalu") seperti dilaporkan
    GMGN, bukan stempel waktu absolut yang diverifikasi on-chain.
- Per-wallet (ringkas; detail penuh ada di laporan browser run ini):
  1. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — dibaca ~01:23–01:24 WIB. BNB 0,08 ($56,44);
     7D TXs 363/349. Holdings tampil (14 baris pertama): MAX, 视界之眼, 朗月, 贵人鸟, 奶蛙党, ok,
     星游记, 旺财, 隆德齐, 雨爱, 咪咪, lucky, WTB, SIC (masing-masing bought ~$4,1). Buy baru
     dalam jendela (setelah 23:41 WIB 2026-10-31): KIM 229,9K $1,382 (56 menit lalu, lalu dijual
     jumlah yang sama 35 menit lalu — tidak muncul di Holdings, konsisten dengan filter
     Hide Closed); GOAT 653,7K $4,149; Goats 615,4K $4,149; Floki 580,7K $4,179 (masing-masing
     ~1 jam lalu). Re-buy token yang SUDAH ada di baseline run 1 (bukan token baru bagi wallet
     ini): MAX, 币安人生, CT PACKS. Ukuran buy sangat kecil (~$4) — dicatat apa adanya.
  2. 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02 — BNB 0 ($0,008). Holdings: "No assets held."
     Aktivitas hanya Tx In lama, tanpa Buy. TIDAK ADA buy baru.
  3. 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5 — BNB 0 ($0,014). Holdings: "No assets held."
     Aktivitas hanya Tx In lama, tanpa Buy. TIDAK ADA buy baru.
  4. 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7 — BNB 0,001 ($1,05). Holdings: "No assets held."
     (Distribution 9 token = token Tx In, tersaring). 50 entri pertama Tx In/Tx Out, tanpa Buy.
     TIDAK ADA buy baru.
  5. 0x75642756e4ba4cc8fbe76df2239cada046cfc854 — BNB 0 ($0,03). Holdings: "No assets held."
     (diverifikasi lewat klik tab Holdings). Hanya Tx In lama. TIDAK ADA buy baru.
  6. 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a — BNB 0 ($0,011). Holdings: "No assets held."
     (diverifikasi lewat klik tab Holdings). Hanya Tx In lama. TIDAK ADA buy baru.
  7. 0x892200223bdfb11d2506c5ab1cae9222ce253acc — BNB 0 ($0,041). Holdings tampil: XPIN, WKC,
     XRP, SLX, BANK, SKYAI, CREPE, TAG, PENGU, elizaOS. Buy terbaru 15 hari lalu (XPIN) —
     baseline, bukan buy baru. TIDAK ADA buy baru.
  8. 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c — BNB 0 ($0,01). Holdings: "No assets held."
     Hanya Tx In (6 baris), tanpa Buy. TIDAK ADA buy baru.
  9. 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e — BNB 0 ($0). Holdings: "No assets held."
     Hanya 2 Tx In SKYAI (5 dan 6 hari lalu), bukan Buy. TIDAK ADA buy baru.
  10. 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462 — BNB 0,007 ($4,84). Holdings: "No assets held."
      Hanya 1 Tx In SKYAI (12 hari lalu). TIDAK ADA buy baru.
  11. 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf — BNB 0 ($0). Holdings: "No assets held."
      50 entri pertama dibaca baris demi baris: semuanya Tx In (kecuali satu Burn CEMINER 307 hari
      lalu), tanpa Buy/Sell. TIDAK ADA buy baru.
  12. 0xda91cefe240175e6fab56271110427a4195ab71f — BNB 0,05 ($35,36). Holdings: "No assets held."
      16 entri pertama hanya Tx In/Tx Out mubarak lama (11–36 hari lalu), bukan Buy.
      TIDAK ADA buy baru.
  13. 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc — BNB 0 ($0). Holdings: "No assets held."
      Hanya Tx In (12 baris), tanpa Buy. TIDAK ADA buy baru.
  14. 0x2325f175975abdbcde555c79cc8e63381d28551b — dibaca ~01:34 WIB. BNB 0,625 ($442,08);
      7D TXs 100/95. Holdings tampil hanya PTG $106,98 / 34,29 (bought $67,31, 5 jam lalu —
      SEBELUM batas 23:41 WIB, dan sudah tercatat di baseline run 1). Aktivitas: Sell 盘古重生
      15,2M $129,9 (1 jam lalu); Buy 盘古重生 / 莫大回归 / 币安人生 berlabel 2 jam lalu pada
      pembacaan 01:34 WIB — menunjuk sekitar pukul 23:xx WIB 2026-10-31, tepat di zona batas
      23:41 WIB, sehingga TIDAK terverifikasi sebagai buy setelah batas dari label relatif saja.
      Terlebih lagi token-token itu SUDAH ada di baseline run 1 wallet ini, jadi bukan token baru
      bagi wallet ini apa pun posisi waktunya. TIDAK ADA buy baru yang terverifikasi.
- Hitungan sinyal run 2 (entitas, bukan alamat mentah):
  - Token baru yang terverifikasi dalam jendela: KIM, GOAT, Goats, Floki — masing-masing hanya
    1 entitas (wallet 1 saja).
  - TIDAK ADA token yang dibeli oleh 2 wallet atau lebih dalam jendela ini, apalagi 4.
    Jadi TIDAK ADA SINYAL (ambang: minimal 4 entitas privat berbeda membeli token baru yang sama).
  - Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada
    runtuhan entitas. Co-buy/co-hold saja (mis. wallet 1 dan wallet 14 sama-sama pernah
    bertransaksi 币安人生) TIDAK meruntuhkan entitas, dan 币安人生 di sini pun bukan token baru
    bagi kedua wallet tersebut.
  - Pembelian 1 wallet saja = bukan sinyal, hanya dicatat di atas.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-01T01:38+07:00; wallet 1
  holdings + buy baru; wallet 14 BNB + holdings PTG; wallet 7 BNB). Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 3 — Minggu 2026-11-01, 03:22–~03:52 WIB

- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat (Tier A privat 13 + Tier B privat 1).
  Daftar lama 23 alamat TIDAK dipakai.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-14 halaman GMGN BSC (URL https://gmgn.ai/bsc/address/<alamat>)
  diterima dan berjalan: jendela browser teramati memuat halaman wallet publik secara berurutan
  (judul tab menampilkan data wallet, mis. "30D Realized Profit $0(0)" untuk wallet yang dibaca —
  BUKAN tampilan "You are not logged in"), termasuk wallet 0x93e7… (ke-8), 0xda91… (ke-12),
  dan 0x8922… (ke-7, kunjungan ulang) sebelum jendela tertutup. Permintaan kedua kepada tugas
  browser yang sama agar mengirim laporan per-wallet terstruktur juga diterima, jendela tertutup
  lagi — tetapi laporan per-wallet terperinci (holdings + trade terbaru per wallet) BELUM terkirim
  ke konteks run ini pada saat penulisan log. Ini pola yang sama seperti Run 1 sebelum adendumnya.
- Text fetch GMGN (browser.open) hanya mengembalikan shell generik situs, bukan data wallet —
  dikonfirmasi ulang pada run ini untuk wallet 0x8e96…, jadi bukan jalur pengganti.
- Percobaan verifikasi on-chain mandiri via RPC publik gagal pada langkah ini: eth_getLogs tanpa
  filter alamat ditolak dataseed dengan error -32005 "limit exceeded" (diuji pada rentang
  10–4000 blok, semua gagal). Jadi jalur itu TIDAK dipakai untuk klaim apa pun pada run ini.
- GAP YANG DICATAT JUJUR, mengikuti preseden Run 1:
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim (ambang: minimal 4 entitas privat berbeda membeli token baru
    yang sama) — bukan karena wallet terbukti tidak membeli, melainkan karena bukti per-wallet
    belum diterima. Wallet yang tidak terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline / state run 2 TIDAK diubah: last_checked tetap 2026-11-01T01:38:00+07:00 dan holdings
    per wallet tetap dari run 2, sampai laporan browser run ini benar-benar diterima. Hanya field
    `last_attempt` di state yang ditambahkan sebagai penanda run ini, tanpa menyentuh baseline.
- Bukti parsial read-only yang DIDAPAT pada run ini (saldo BNB on-chain via batch RPC, blok
  130923887, ~03:52 WIB) — saldo saja, BUKAN bukti beli/jual dan BUKAN pengganti laporan GMGN:
  - 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6: 0,0773 BNB (run 2: 0,08) — turun kecil.
  - 0x2325f175975abdbcde555c79cc8e63381d28551b: 0,6253 BNB (run 2: 0,625) — praktis sama.
  - 0xda91cefe240175e6fab56271110427a4195ab71f: 0,0500 BNB (run 2: 0,05) — sama.
  - 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462: 0,00685 BNB (run 2: 0,007) — sama.
  - 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc: 0,02479 BNB (run 2: 0 / $0) — PERUBAHAN MATERIAL
    yang belum terjelaskan: saldo naik dari nol menjadi ~0,0248 BNB. Ini dicatat sebagai
    perubahan saldo saja — TIDAK diklaim sebagai pembelian, karena sumber BNB masuk dan token
    apa pun (bila ada) belum terverifikasi. Wajib dicek aktivitasnya (Tx In vs Buy) pada run
    berikutnya / bila laporan browser run ini tiba.
  - Wallet lain praktis sama dengan run 2 (debu <0,002 BNB): 0x13d1… 0,0000119; 0x5b2f… 0,0000192;
    0x6ba7… 0,00148; 0x7564… 0,0000429; 0x8272… 0,0000158; 0x8922… 0,0000583; 0x93e7… 0,0000143;
    0xaab8… 0; 0xbe59… 0.
- Tindak lanjut: bila laporan browser run ini tiba belakangan, tambahkan sebagai adendum run ini
  dengan stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs baseline
  run 2. Bila tidak tiba, run berikutnya harus mengulang pembacaan ke-14 wallet dan mencatat
  holdings + aktivitas terbaru per wallet secara eksplisit, dengan perhatian khusus pada wallet
  0xf6a8… (perubahan saldo di atas) sebelum menghitung sinyal apa pun.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Adendum Run 3 — laporan browser diterima setelah log gap ditulis

Pemeriksaan browser terukur 03:23–03:36 WIB (waktu ukur runtime, bukan klaim di dalam laporan).
Semua 14 halaman memuat data publik TANPA login-gated, tanpa klik Log in/Sign up/Connect, tanpa
sign/transaksi. Koreksi atas bagian "GAP" di atas: bukti per-wallet AKHIRNYA diterima, sehingga
hitungan sinyal run 3 dapat ditetapkan dari laporan ini dan state diperbarui dari laporan ini
(last_checked 2026-11-01T03:36:00+07:00). Batasan laporan yang wajib dicatat:
- Tab Holdings memakai filter default "Hide Didn't Buy" (plus "Hide Tiny Pool", "Hide Honeypot",
  "Hide Closed" di beberapa halaman): "No assets held." = sesuai tampilan tab itu, BUKAN klaim
  saldo on-chain nol; token yang hanya diterima lewat Tx In tersaring dari Holdings.
- Contract address TIDAK tercatat pada run ini untuk token mana pun: tidak ada alamat kontrak
  lengkap yang terlihat dalam teks; CA tidak ditebak dari simbol. Token baru dicatat berdasarkan
  simbol saja, dan karena itu tidak dapat dipakai sebagai CA terverifikasi untuk perbandingan
  antar wallet — hitungan di bawah memakai simbol + konteks baseline, dan tidak ada token yang
  dibeli 2 wallet atau lebih sehingga keterbatasan ini tidak mengubah kesimpulan.
- Waktu aktivitas bersifat relatif terhadap waktu baca ("menit/jam lalu") seperti dilaporkan
  GMGN, bukan stempel waktu absolut yang diverifikasi on-chain; label "2h ago"/"3h ago"/"4h ago"
  bersifat kasar dan harus dicocokkan dengan jumlah/nilai transaksi sebelum dinyatakan baru.

Per-wallet (ringkas; urutan sesuai tier-ab-watch.md):
1. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — dibaca ~03:24 WIB. BNB 0,077 ($54,57).
   Holdings bernilai bukan nol: 爪子 $0,92 / 214K; MAX; 视界之眼; 朗月; 贵人鸟; 奶蛙党
   (banyak baris lama kini $0 Sell All). Buy BARU dalam jendela (vs baseline run 2):
   爪子 214K $1,38 (40m lalu, ~02:44 WIB); MMGA 143,8K $1,386 (1h lalu, ~02:24 WIB, lalu dijual
   jumlah yang sama 1h lalu). BUKAN baru: Buy KIM 229,9K $1,382 berlabel 2h lalu adalah
   transaksi KIM yang SAMA dengan yang sudah tercatat di run 2 (jumlah dan nilai identik,
   lalu dijual jumlah yang sama) — tidak dihitung ganda. GOAT/MAX/Goats berlabel 3h lalu
   adalah buy jendela run 2, bukan baru di run 3.
2.–6., 8.–13. (0x13d1…, 0x5b2f…, 0x6ba7…, 0x7564…, 0x8272…, 0x93e7…, 0xaab8…, 0xb787…,
   0xbe59…, 0xda91…, 0xf6a8…): TIDAK ADA buy baru. Aktivitas terbaru hanya Tx In/Tx Out lama
   (termasuk SKYAI dan mubarak sebagai holding/transfer lama, bukan buy baru). Holdings:
   "No assets held." kecuali wallet 12 (0xda91…) yang juga "No assets held." dengan BNB 0,05.
   Khusus wallet 13 (0xf6a8…): GMGN pada 03:33 WIB menunjukkan BNB 0 ($0) dan tidak ada Buy —
   ini BERBEDA WAKTU dengan batch on-chain ~03:52 WIB yang menunjukkan 0,02479 BNB (lihat
   entri gap di atas). Perubahan saldo itu terjadi SETELAH pembacaan GMGN, penyebabnya belum
   terverifikasi, dan TIDAK diklaim sebagai pembelian; wajib dicek ulang pada run berikutnya.
7. 0x892200223bdfb11d2506c5ab1cae9222ce253acc — dibaca ~03:28 WIB, aktivitas diverifikasi
   ulang ~03:35 WIB. BNB 0 ($0,041). Holdings tampil: XPIN, WKC, XRP, SLX, BANK, SKYAI, CREPE,
   TAG, PENGU, elizaOS. Buy terbaru 15 hari lalu (XPIN) — baseline, bukan buy baru.
   TIDAK ADA buy baru.
14. 0x2325f175975abdbcde555c79cc8e63381d28551b — dibaca ~03:34 WIB. BNB 0,625 ($441,03).
   Holdings tampil hanya PTG $106,98 / 34,29. Aktivitas: Sell 盘古重生 3h lalu; Buy-buy berlabel
   4h lalu (盘古重生, 莫大回归, 币安人生) adalah token baseline run 1/run 2, di luar jendela
   2 jam run ini. TIDAK ADA buy baru yang terverifikasi dalam jendela run 3.

Hitungan sinyal run 3 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela: 爪子 dan MMGA — masing-masing hanya 1 entitas
  (wallet 1 saja).
- TIDAK ADA token yang dibeli oleh 2 wallet atau lebih dalam jendela ini, apalagi 4.
  Jadi TIDAK ADA SINYAL (ambang: minimal 4 entitas privat berbeda membeli token baru yang sama).
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada
  runtuhan entitas. Co-buy/co-hold saja TIDAK meruntuhkan entitas.
- Pembelian 1 wallet saja = bukan sinyal, hanya dicatat di atas.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-01T03:36:00+07:00; wallet 1 holdings + buy baru 爪子/MMGA; wallet 14 BNB + holdings PTG;
  wallet 7 holdings; wallet 13 dicatat dengan diskrepansi waktu saldo di atas).
  Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 4 — Minggu 2026-11-01, 05:22–05:24 WIB (gap: laporan browser belum diterima saat penulisan)

- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat (Tier A privat 13 + Tier B privat 1).
  Daftar lama 23 alamat TIDAK dipakai.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-14 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>)
  DIDISPATCH (task browser-task:51bf9b74-02b2-5ed7-ae2a-a10901081329) pada 05:23 WIB, dengan
  instruksi eksplisit: bila login-gated, catat saja dan lanjut, JANGAN klik login.
- GAP YANG DICATAT JUJUR, mengikuti preseden Run 1 dan Run 3:
  - Laporan per-wallet terperinci (holdings + trade terbaru per wallet) dari browser BELUM
    terkirim ke konteks run ini pada saat penulisan log.
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim (ambang: minimal 4 entitas privat berbeda membeli token baru
    yang sama) — bukan karena wallet terbukti tidak membeli, melainkan karena bukti per-wallet
    belum diterima. Wallet yang tidak terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline / state run 3 TIDAK diubah: last_checked tetap 2026-11-01T03:36:00+07:00 dan holdings
    per wallet tetap dari run 3, sampai laporan browser run ini benar-benar diterima. Hanya field
    `last_attempt` di state yang diperbarui sebagai penanda run ini.
- Bukti parsial read-only yang DIDAPAT pada run ini (saldo BNB on-chain via batch RPC, blok
  130936481, ~05:24 WIB) — saldo saja, BUKAN bukti beli/jual dan BUKAN pengganti laporan GMGN:
  - 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6: 0,07603 BNB (run 3: 0,0773) — turun kecil.
  - 0x2325f175975abdbcde555c79cc8e63381d28551b: 0,62530 BNB (run 3: 0,6253) — praktis sama.
  - 0xda91cefe240175e6fab56271110427a4195ab71f: 0,05000 BNB (run 3: 0,0500) — sama.
  - 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462: 0,00685 BNB (run 3: 0,00685) — sama.
  - 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc: 0,02479 BNB (run 3 batch ~03:52 WIB: 0,02479) —
    TIDAK BERUBAH sejak batch run 3; inflow yang terjadi antara pembacaan GMGN 03:33 WIB (BNB 0)
    dan batch 03:52 WIB itu belum terjelaskan aktivitasnya, dan TIDAK diklaim sebagai pembelian.
    Wajib dicek aktivitasnya (Tx In vs Buy) dari laporan browser run ini / run berikutnya.
  - Wallet lain praktis sama dengan run 3 (debu): 0x13d1… 0,0000119; 0x5b2f… 0,0000192;
    0x6ba7… 0,00148; 0x7564… 0,0000429; 0x8272… 0,0000158; 0x8922… 0,0000583; 0x93e7… 0,0000143;
    0xaab8… 0; 0xbe59… 0.
- Tindak lanjut: bila laporan browser run ini tiba belakangan, tambahkan sebagai adendum run ini
  dengan stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs baseline
  run 3. Bila tidak tiba, run berikutnya harus mengulang pembacaan ke-14 wallet dan mencatat
  holdings + aktivitas terbaru per wallet secara eksplisit, dengan perhatian khusus pada wallet
  0xf6a8… (perubahan saldo di atas) sebelum menghitung sinyal apa pun.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Adendum Run 4 — laporan browser diterima ~05:34 WIB

Pemeriksaan browser terukur 05:24–05:32 WIB (waktu ukur runtime 05:23–05:34 WIB, bukan klaim di
dalam laporan). Semua 14 halaman memuat data publik TANPA login-gated, tanpa klik Log in/Sign
up/Connect, tanpa sign/transaksi. Koreksi atas bagian "GAP" di atas: bukti per-wallet AKHIRNYA
diterima, sehingga hitungan sinyal run 4 dapat ditetapkan dari laporan ini dan state diperbarui
dari laporan ini (last_checked 2026-11-01T05:32:00+07:00). Batasan laporan yang wajib dicatat:
- Tab Holdings memakai filter default "Hide Didn't Buy" (plus filter lain di beberapa halaman):
  "No assets held." = sesuai tampilan tab itu, BUKAN klaim saldo on-chain nol; token yang hanya
  diterima lewat Tx In tersaring dari Holdings.
- Contract address TIDAK tercatat pada run ini untuk token mana pun: tidak ada alamat kontrak
  lengkap yang terlihat dalam teks; CA tidak ditebak dari simbol. Token dicatat berdasarkan
  simbol saja, dan karena itu tidak dapat dipakai sebagai CA terverifikasi untuk perbandingan
  antar wallet — hitungan di bawah memakai simbol + konteks baseline, dan tidak ada token baru
  yang dibeli 2 wallet atau lebih sehingga keterbatasan ini tidak mengubah kesimpulan.
- Waktu aktivitas bersifat relatif terhadap waktu baca ("menit/jam lalu") seperti dilaporkan
  GMGN, bukan stempel waktu absolut yang diverifikasi on-chain; label relatif dicocokkan dengan
  jumlah/nilai transaksi sebelum dinyatakan baru, mengikuti preseden run 3 (KIM).

Per-wallet (ringkas; urutan sesuai tier-ab-watch.md):
1. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — dibaca ~05:24 WIB. BNB 0,076 ($53,5).
   Holdings bukan nol: 爪子 $0,705 / 214K; MAX $2,45 / 737,6K; 视界之眼 $2,22 / 467,3K;
   朗月 $2,87 / 585,7K; 贵人鸟 $3,32 / 857,4K; 奶蛙党 $2,54 / 745,4K (sisanya $0 / terjual habis).
   Aktivitas terbaru: Sell Kim 133,5K $1,187 (34m lalu, ~04:50 WIB); Buy Kim 133,5K $1,376
   (52m lalu, ~04:32 WIB); Buy 爪子 214K $1,38 (2h lalu); Sell MMGA 143,8K $1,247 (3h lalu);
   Buy MMGA 143,8K $1,386 (3h lalu). Penilaian vs baseline run 3: Buy 爪子 dan Buy MMGA
   berlabel 2h/3h lalu adalah transaksi run 3 yang SAMA (jumlah dan nilai identik) — TIDAK
   dihitung ganda. Buy Kim 133,5K adalah trade Kim BARU dalam jendela run 4, TETAPI Kim
   BUKAN token baru bagi wallet ini (sudah tercatat sejak run 2, 229,9K, lalu dijual) — ini
   re-trade token yang sudah dikenal, lalu dijual lagi jumlah yang sama ~04:50 WIB, sehingga
   TIDAK dihitung sebagai pembelian token baru. Jadi: TIDAK ADA token baru di run 4 untuk wallet ini.
2.–6., 8.–13. (0x13d1…, 0x5b2f…, 0x6ba7…, 0x7564…, 0x8272…, 0x93e7…, 0xaab8…, 0xb787…,
   0xbe59…, 0xda91…, 0xf6a8…): TIDAK ADA buy baru. Aktivitas terbaru hanya Tx In/Tx Out lama
   (termasuk SKYAI dan mubarak sebagai holding/transfer lama, bukan buy baru). Holdings:
   "No assets held." untuk semuanya. Khusus wallet 13 (0xf6a8…): GMGN pada ~05:30 WIB MASIH
   menunjukkan BNB 0 ($0) dan aktivitas terbaru 10 hari lalu (Tx In NEX) — TIDAK menjelaskan
   saldo on-chain 0,02479 BNB yang tercatat di batch ~03:52 WIB maupun batch ~05:24 WIB
   (tidak berubah). Diskrepansi GMGN-vs-on-chain ini MASIH belum terjelaskan, penyebabnya belum
   terverifikasi, dan TIDAK diklaim sebagai pembelian; wajib dicek ulang pada run berikutnya.
7. 0x892200223bdfb11d2506c5ab1cae9222ce253acc — dibaca ~05:27 WIB. BNB 0 ($0,041).
   Holdings tampil: XPIN, WKC, XRP, SLX, BANK, SKYAI, CREPE, TAG, PENGU, elizaOS (nilai
   bergeser tipis vs run 3). Buy terbaru 15 hari lalu (XPIN) — baseline, bukan buy baru.
   TIDAK ADA buy baru.
14. 0x2325f175975abdbcde555c79cc8e63381d28551b — dibaca ~05:30–05:32 WIB. BNB 0,625 ($440,1).
   Holdings bukan nol hanya PTG $106,98 / 34,29; sisanya $0 / terjual habis. Aktivitas terbaru:
   Tx In NS +0,0₄63399 $0,003 (1h lalu, ~04:30 WIB) — Tx In, BUKAN Buy, nilai debu, tidak
   dihitung sebagai pembelian; Sell 盘古重生 15,2M $129,9 (5h lalu, ~00:30 WIB — transaksi
   yang sama dengan Sell 3h lalu di laporan run 3, bukan sell baru); Buy-buy berlabel 6h–9h
   lalu (盘古重生, 莫大回归, 币安人生, GPAY, 7JAGENT, PTG) menunjuk sekitar 20:30–23:30 WIB
   2026-10-31, yaitu SEBELUM jendela run 4 dan semuanya token baseline run 1/run 2 — bukan
   token baru bagi wallet ini. TIDAK ADA buy baru yang terverifikasi dalam jendela run 4.

Hitungan sinyal run 4 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 4 (setelah 03:36 WIB): TIDAK ADA.
  Satu-satunya trade dalam jendela adalah re-trade Kim oleh wallet 1, dan Kim bukan token baru
  bagi wallet itu.
- TIDAK ADA token yang dibeli oleh 2 wallet atau lebih dalam jendela ini, apalagi 4.
  Jadi TIDAK ADA SINYAL (ambang: minimal 4 entitas privat berbeda membeli token baru yang sama).
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada
  runtuhan entitas. Co-buy/co-hold saja TIDAK meruntuhkan entitas.
- Pembelian 1 wallet saja = bukan sinyal; di run ini bahkan tidak ada pembelian token baru
  1 wallet pun.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-01T05:32:00+07:00; wallet 1 holdings + re-trade Kim; wallet 14 BNB + Tx In NS;
  wallet 13 dicatat dengan diskrepansi saldo yang masih belum terjelaskan).
  Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 5 — Minggu 2026-11-01, 07:22–~07:25 WIB (gap: laporan browser belum diterima saat penulisan)

- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat (Tier A privat 13 + Tier B privat 1).
  Daftar lama 23 alamat TIDAK dipakai.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-14 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>)
  DIDISPATCH (task browser-task:9aa20c30-07e0-5f3b-b100-d18668f83f72) pada ~07:23 WIB, dengan
  instruksi eksplisit: bila login-gated, catat saja dan lanjut, JANGAN klik login.
- GAP YANG DICATAT JUJUR, mengikuti preseden Run 1, Run 3, dan Run 4:
  - Laporan per-wallet terperinci (holdings + trade terbaru per wallet) dari browser BELUM
    terkirim ke konteks run ini pada saat penulisan log.
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim (ambang: minimal 4 entitas privat berbeda membeli token baru
    yang sama) — bukan karena wallet terbukti tidak membeli, melainkan karena bukti per-wallet
    belum diterima. Wallet yang tidak terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline / state run 4 TIDAK diubah: last_checked tetap 2026-11-01T05:32:00+07:00 dan holdings
    per wallet tetap dari run 4, sampai laporan browser run ini benar-benar diterima. Hanya field
    `last_attempt` di state yang diperbarui sebagai penanda run ini.
- Bukti parsial read-only yang DIDAPAT pada run ini (saldo BNB on-chain via batch RPC, blok
  130952547, ~07:25 WIB) — saldo saja, BUKAN bukti beli/jual dan BUKAN pengganti laporan GMGN:
  - 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6: 0,07603 BNB (run 4: 0,076) — praktis sama.
  - 0x2325f175975abdbcde555c79cc8e63381d28551b: 0,62530 BNB (run 4: 0,625) — praktis sama.
  - 0xda91cefe240175e6fab56271110427a4195ab71f: 0,05000 BNB (run 4: 0,05) — sama.
  - 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462: 0,00685 BNB (run 4: 0,00685) — sama.
  - 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc: 0,02479 BNB (run 4 batch: 0,02479) —
    TIDAK BERUBAH sejak batch run 3/run 4; diskrepansi GMGN-vs-on-chain (GMGN menunjukkan 0)
    MASIH belum terjelaskan, penyebabnya belum terverifikasi, dan TIDAK diklaim sebagai pembelian.
    Wajib dicek aktivitasnya (Tx In vs Buy) dari laporan browser run ini / run berikutnya.
  - Wallet lain praktis sama dengan run 4 (debu): 0x13d1… 0,0000119; 0x5b2f… 0,0000192;
    0x6ba7… 0,00148; 0x7564… 0,0000429; 0x8272… 0,0000158; 0x8922… 0,0000583; 0x93e7… 0,0000143;
    0xaab8… 0; 0xbe59… 0.
- Tindak lanjut: bila laporan browser run ini tiba belakangan, tambahkan sebagai adendum run ini
  dengan stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs baseline
  run 4. Bila tidak tiba, run berikutnya harus mengulang pembacaan ke-14 wallet dan mencatat
  holdings + aktivitas terbaru per wallet secara eksplisit, dengan perhatian khusus pada wallet
  0xf6a8… (diskrepansi saldo di atas) sebelum menghitung sinyal apa pun.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Adendum Run 5 — laporan browser diterima ~07:39 WIB

Pemeriksaan browser terukur 07:23–07:39 WIB (waktu ukur runtime; laporan per-wallet
07:24–07:38 WIB). Semua 14 halaman memuat data publik TANPA login-gated, status
"Disconnected", tanpa klik Log in/Sign up/Connect, tanpa sign/transaksi. Koreksi atas
bagian "GAP" di atas: bukti per-wallet AKHIRNYA diterima, sehingga hitungan sinyal run 5
dapat ditetapkan dari laporan ini dan state diperbarui dari laporan ini (last_checked
2026-11-01T07:38:00+07:00). Batasan laporan yang wajib dicatat:
- Tab Holdings memakai filter default yang teramati: "Hide Didn't Buy" tercentang,
  "Hide Tiny Pool"/"Hide Honeypot"/"Hide Closed" tidak tercentang: "No assets held." =
  sesuai tampilan tab itu, BUKAN klaim saldo on-chain nol; token yang hanya diterima
  lewat Tx In tersaring dari Holdings.
- Contract address TIDAK tercatat pada run ini untuk token mana pun: tidak ada alamat
  kontrak lengkap yang terlihat dalam teks halaman (hanya alamat wallet sendiri); CA
  tidak ditebak dari simbol. Token dicatat berdasarkan simbol saja, dan karena itu
  tidak dapat dipakai sebagai CA terverifikasi untuk perbandingan antar wallet —
  hitungan di bawah memakai simbol + konteks baseline, dan tidak ada token baru yang
  dibeli 2 wallet atau lebih sehingga keterbatasan ini tidak mengubah kesimpulan.
- Waktu aktivitas bersifat relatif terhadap waktu baca ("jam lalu") seperti dilaporkan
  GMGN, bukan stempel waktu absolut yang diverifikasi on-chain; label relatif dicocokkan
  dengan jumlah/nilai transaksi sebelum dinyatakan baru, mengikuti preseden run 3–4.

Per-wallet (ringkas; urutan sesuai tier-ab-watch.md):
1. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — dibaca ~07:24 WIB. BNB 0,076 ($53,51).
   Holdings bukan nol: 爪子 $0,705 / 214K; MAX $2,45 / 737,6K; 视界之眼 $2,20 / 467,3K;
   朗月 $2,82 / 585,7K; 贵人鸟 $3,18 / 857,4K; 奶蛙党 $2,54 / 745,4K (sisanya $0).
   Aktivitas terbaru: Sell Kim 133,5K $1,187 (2h lalu); Buy Kim 133,5K $1,376 (2h lalu);
   Buy 爪子 214K $1,38 (4h lalu); Sell MMGA 143,8K $1,247 (5h lalu); Buy MMGA 143,8K
   $1,386 (5h lalu). Penilaian vs baseline run 4: Buy/Sell Kim 133,5K adalah trade Kim
   yang SAMA dengan run 4 (jumlah dan nilai identik, ~04:32/~04:50 WIB) — label relatif
   bergeser karena waktu baca lebih lambat, TIDAK dihitung ganda dan Kim pun bukan token
   baru bagi wallet ini (sejak run 2). Buy 爪子/MMGA adalah transaksi run 3 yang SAMA.
   Jadi: TIDAK ADA token baru di run 5 untuk wallet ini.
2.–6., 8.–13. (0x13d1…, 0x5b2f…, 0x6ba7…, 0x7564…, 0x8272…, 0x93e7…, 0xaab8…, 0xb787…,
   0xbe59…, 0xda91…, 0xf6a8…): TIDAK ADA buy baru. Aktivitas terbaru hanya Tx In/Tx Out
   lama (termasuk SKYAI dan mubarak sebagai holding/transfer lama, bukan buy baru).
   Holdings: "No assets held." untuk semuanya. Khusus wallet 13 (0xf6a8…): GMGN pada
   ~07:36–07:37 WIB MASIH menunjukkan BNB 0 ($0) dan aktivitas terbaru 11 hari lalu
   (Tx In NEX) — TIDAK menjelaskan saldo on-chain 0,02479 BNB yang tercatat di batch
   ~03:52, ~05:24, maupun ~07:25 WIB (tidak berubah). Diskrepansi GMGN-vs-on-chain ini
   MASIH belum terjelaskan, penyebabnya belum terverifikasi, dan TIDAK diklaim sebagai
   pembelian; wajib dicek ulang pada run berikutnya.
7. 0x892200223bdfb11d2506c5ab1cae9222ce253acc — dibaca ~07:29 WIB. BNB 0 ($0,041).
   Holdings tampil: XPIN, WKC, XRP, SLX, BANK, SKYAI, CREPE, TAG, PENGU, elizaOS (nilai
   bergeser tipis vs run 4). Buy terbaru 15–17 hari lalu (XPIN, XRP) — baseline, bukan
   buy baru. TIDAK ADA buy baru.
14. 0x2325f175975abdbcde555c79cc8e63381d28551b — dibaca ~07:37–07:38 WIB. BNB 0,625
   ($440,81). Holdings bukan nol hanya PTG $112,51 / 34,29 (sebelumnya $106,98).
   Aktivitas terbaru: Tx In NS +0,0₄63399 $0,003 (3h lalu, ~04:38 WIB) — Tx In yang SAMA
   dengan debu NS run 4 (1h lalu pada baca ~05:30 WIB, ~04:30 WIB), BUKAN Buy; Sell
   盘古重生 15,2M $129,9 (7h lalu) adalah sell yang SAMA dengan run 4 (5h lalu saat itu);
   Buy-buy berlabel 8h–9h lalu (盘古重生, 莫大回归, 币安人生, GPAY) menunjuk sekitar
   22:30–23:30 WIB 2026-10-31, yaitu SEBELUM jendela run 5 dan semuanya token baseline
   run 1/run 2 — bukan token baru bagi wallet ini. TIDAK ADA buy baru yang terverifikasi
   dalam jendela run 5.

Hitungan sinyal run 5 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 5 (setelah 05:32 WIB): TIDAK ADA.
  Satu-satunya trade dalam jendela yang tampak adalah duplikat label dari trade run 3–4
  dan satu Tx In debu yang bukan Buy.
- TIDAK ADA token yang dibeli oleh 2 wallet atau lebih dalam jendela ini, apalagi 4.
  Jadi TIDAK ADA SINYAL (ambang: minimal 4 entitas privat berbeda membeli token baru yang sama).
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada
  runtuhan entitas. Co-buy/co-hold saja TIDAK meruntuhkan entitas.
- Pembelian 1 wallet saja = bukan sinyal; di run ini bahkan tidak ada pembelian token baru
  1 wallet pun.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-01T07:38:00+07:00; wallet 1 holdings; wallet 14 BNB + PTG + Tx In NS;
  wallet 13 dicatat dengan diskrepansi saldo yang masih belum terjelaskan).
  Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 6 — Minggu 2026-11-01, 09:22–~09:24 WIB (gap: laporan browser belum diterima saat penulisan)

- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat (Tier A privat 13 + Tier B privat 1).
  Daftar lama 23 alamat TIDAK dipakai.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-14 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>)
  DIDISPATCH (task browser-task:1b1e08c2-6078-5d5f-bc20-a74327e6b5e2) pada ~09:23 WIB, dengan
  instruksi eksplisit: bila login-gated, catat saja dan lanjut, JANGAN klik login.
- GAP YANG DICATAT JUJUR, mengikuti preseden Run 1, Run 3, Run 4, dan Run 5:
  - Laporan per-wallet terperinci (holdings + trade terbaru per wallet) dari browser BELUM
    terkirim ke konteks run ini pada saat penulisan log.
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim (ambang: minimal 4 entitas privat berbeda membeli token baru
    yang sama) — bukan karena wallet terbukti tidak membeli, melainkan karena bukti per-wallet
    belum diterima. Wallet yang tidak terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline / state run 5 TIDAK diubah: last_checked tetap 2026-11-01T07:38:00+07:00 dan holdings
    per wallet tetap dari run 5, sampai laporan browser run ini benar-benar diterima. Hanya field
    `last_attempt` di state yang diperbarui sebagai penanda run ini.
- Bukti parsial read-only yang DIDAPAT pada run ini (saldo BNB on-chain via batch RPC, blok
  130968402, ~09:24 WIB) — saldo saja, BUKAN bukti beli/jual dan BUKAN pengganti laporan GMGN:
  - 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6: 0,07222 BNB (run 5: 0,07603) — TURUN ~0,0038 BNB,
    lebih besar dari pergeseran kecil run-run sebelumnya; penyebabnya (trade/gas/transfer)
    belum terverifikasi, TIDAK diklaim sebagai pembelian; wajib dicocokkan dengan laporan browser.
  - 0x2325f175975abdbcde555c79cc8e63381d28551b: 0,62530 BNB (run 5: 0,62530) — sama.
  - 0xda91cefe240175e6fab56271110427a4195ab71f: 0,05000 BNB (run 5: 0,05) — sama.
  - 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462: 0,00685 BNB (run 5: 0,00685) — sama.
  - 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc: 0,02479 BNB (run 5 batch: 0,02479) —
    TIDAK BERUBAH sejak batch run 3/run 4/run 5; diskrepansi GMGN-vs-on-chain (GMGN menunjukkan 0)
    MASIH belum terjelaskan, penyebabnya belum terverifikasi, dan TIDAK diklaim sebagai pembelian.
    Wajib dicek aktivitasnya (Tx In vs Buy) dari laporan browser run ini / run berikutnya.
  - Wallet lain praktis sama dengan run 5 (debu): 0x13d1… 0,0000119; 0x5b2f… 0,0000192;
    0x6ba7… 0,00148; 0x7564… 0,0000429; 0x8272… 0,0000158; 0x8922… 0,0000583; 0x93e7… 0,0000143;
    0xaab8… 0; 0xbe59… 0.
- Tindak lanjut: bila laporan browser run ini tiba belakangan, tambahkan sebagai adendum run ini
  dengan stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs baseline
  run 5. Bila tidak tiba, run berikutnya harus mengulang pembacaan ke-14 wallet dan mencatat
  holdings + aktivitas terbaru per wallet secara eksplisit, dengan perhatian khusus pada wallet
  0x8e96… (penurunan saldo di atas) dan 0xf6a8… (diskrepansi saldo) sebelum menghitung sinyal apa pun.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Adendum Run 6 — laporan browser diterima ~09:39 WIB

Pemeriksaan browser terukur 09:23–09:39 WIB (waktu ukur runtime; laporan per-wallet
09:24–09:37 WIB). Semua 14 halaman memuat data publik TANPA login-gated, status
"Disconnected", tanpa klik Log in/Sign up/Connect, tanpa sign/transaksi. Koreksi atas
bagian "GAP" di atas: bukti per-wallet AKHIRNYA diterima, sehingga hitungan sinyal run 6
dapat ditetapkan dari laporan ini dan state diperbarui dari laporan ini (last_checked
2026-11-01T09:37:00+07:00). Batasan laporan yang wajib dicatat:
- Tab Holdings memakai filter default yang teramati: "Hide Didn't Buy" tercentang,
  "Hide Tiny Pool"/"Hide Honeypot"/"Hide Closed" tidak tercentang: "No assets held." =
  sesuai tampilan tab itu, BUKAN klaim saldo on-chain nol; token yang hanya diterima
  lewat Tx In tersaring dari Holdings.
- Contract address TIDAK tercatat pada run ini untuk token mana pun: tidak ada alamat
  kontrak lengkap yang terlihat dalam teks halaman (hanya alamat wallet sendiri dan
  alamat pengirim/penerima yang terpotong); CA tidak ditebak dari simbol. Token dicatat
  berdasarkan simbol saja, dan karena itu tidak dapat dipakai sebagai CA terverifikasi
  untuk perbandingan antar wallet — hitungan di bawah memakai simbol + konteks baseline,
  dan tidak ada token baru yang dibeli 2 wallet atau lebih sehingga keterbatasan ini
  tidak mengubah kesimpulan.
- Waktu aktivitas bersifat relatif terhadap waktu baca ("menit/jam lalu") seperti dilaporkan
  GMGN, bukan stempel waktu absolut yang diverifikasi on-chain; label relatif dicocokkan
  dengan jumlah/nilai transaksi sebelum dinyatakan baru, mengikuti preseden run 3–5.

Per-wallet (ringkas; urutan sesuai tier-ab-watch.md):
1. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — dibaca ~09:24 WIB. BNB 0,072 ($50,77),
   kini cocok dengan batch on-chain 0,07222 BNB — penurunan ~0,0038 BNB vs run 5 konsisten
   dengan aktivitas trading dalam jendela, tetapi penurunan itu sendiri TIDAK diklaim sebagai
   pembelian tertentu. Holdings bukan nol: 币安人生 $2,03 / 213K; 爪子 $0,705 / 214K;
   MAX $2,45 / 737,6K; 视界之眼 $2,04 / 467,3K; 朗月 $2,82 / 585,7K; 贵人鸟 $3,18 / 857,4K;
   奶蛙党 $2,54 / 745,4K (sisanya $0 pada 50 baris pertama). Aktivitas terbaru: Sell
   币安必胜 196,1K $1,253 (16m lalu); Buy 币安人生 213K $1,365 (18m lalu, ~09:06 WIB);
   Sell 月球兔 165,2K $0,704 (34m lalu); Buy 币安必胜 196,1K $1,379 (53m lalu, ~08:31 WIB);
   Buy 月球兔 165,2K $1,381 (1h lalu, ~08:24 WIB). Penilaian vs baseline run 5:
   币安必胜 dan 月球兔 adalah token BARU bagi wallet ini (belum pernah tercatat dipegang/
   dibeli wallet ini di state sebelumnya) — masing-masing dibeli lalu dijual jumlah yang
   sama dalam jendela. Buy 币安人生 adalah RE-BUY token yang sudah dikenal wallet ini sejak
   run 1/run 2, BUKAN token baru. Jadi: 2 token baru di run 6 untuk wallet ini, masing-masing
   1 entitas.
2.–6., 8.–13. (0x13d1…, 0x5b2f…, 0x6ba7…, 0x7564…, 0x8272…, 0x93e7…, 0xaab8…, 0xb787…,
   0xbe59…, 0xda91…, 0xf6a8…): TIDAK ADA buy baru. Aktivitas terbaru hanya Tx In/Tx Out
   lama (termasuk SKYAI dan mubarak sebagai holding/transfer lama, bukan buy baru).
   Holdings: "No assets held." untuk semuanya. Khusus wallet 13 (0xf6a8…): GMGN pada
   ~09:36–09:37 WIB MASIH menunjukkan BNB 0 ($0) dan aktivitas terbaru 11 hari lalu
   (Tx In NEX) — TIDAK menjelaskan saldo on-chain 0,02479 BNB yang tercatat di batch
   ~03:52, ~05:24, ~07:25, maupun ~09:24 WIB (tidak berubah). Diskrepansi GMGN-vs-on-chain ini
   MASIH belum terjelaskan, penyebabnya belum terverifikasi, dan TIDAK diklaim sebagai
   pembelian; wajib dicek ulang pada run berikutnya.
7. 0x892200223bdfb11d2506c5ab1cae9222ce253acc — dibaca ~09:28–09:29 WIB. BNB 0 ($0,041).
   Holdings tampil: XPIN, WKC, XRP, SLX, BANK, SKYAI, CREPE, TAG, PENGU, elizaOS (nilai
   bergeser tipis vs run 5), plus ETH dan BTCB $0 (Sell All). Buy terbaru 15–16 hari lalu
   (XPIN) — baseline, bukan buy baru. TIDAK ADA buy baru.
14. 0x2325f175975abdbcde555c79cc8e63381d28551b — dibaca ~09:37 WIB. BNB 0,625 ($439,28).
   Holdings bukan nol hanya PTG $112,51 / 34,29 (sama seperti run 5). Aktivitas terbaru:
   Tx In NS +0,0₄63399 $0,003 (5h lalu, ~04:30 WIB) — Tx In yang SAMA dengan debu NS run 4/5,
   BUKAN Buy; Sell 盘古重生 15,2M $129,9 (9h lalu) dan Buy/Sell 盘古重生/莫大回归 berlabel
   10h lalu menunjuk sekitar 23:xx WIB 2026-10-31, yaitu SEBELUM jendela run 6 dan semuanya
   token baseline run 1/run 2 — bukan token baru bagi wallet ini. TIDAK ADA buy baru yang
   terverifikasi dalam jendela run 6.

Hitungan sinyal run 6 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 6 (setelah 07:38 WIB): 币安必胜 dan 月球兔 —
  masing-masing hanya 1 entitas (wallet 1 saja). Buy 币安人生 oleh wallet 1 tidak dihitung
  sebagai token baru (re-buy token yang sudah dikenal).
- TIDAK ADA token yang dibeli oleh 2 wallet atau lebih dalam jendela ini, apalagi 4.
  Jadi TIDAK ADA SINYAL (ambang: minimal 4 entitas privat berbeda membeli token baru yang sama).
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada
  runtuhan entitas. Co-buy/co-hold saja TIDAK meruntuhkan entitas.
- Pembelian token baru 1 wallet saja = bukan sinyal, hanya dicatat di atas.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-01T09:37:00+07:00; wallet 1 holdings + buy baru 币安必胜/月球兔 + re-buy 币安人生;
  wallet 14 BNB + Tx In NS; wallet 13 dicatat dengan diskrepansi saldo yang masih belum
  terjelaskan). Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 7 — Minggu 2026-11-01, 11:22–~11:24 WIB (gap: laporan browser belum diterima saat penulisan)

- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat (Tier A privat 13 + Tier B privat 1).
  Daftar lama 23 alamat TIDAK dipakai.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-14 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>)
  DIDISPATCH (task browser-task:5de6541f-a338-5c66-a99d-c5ac3aae4279) pada ~11:23 WIB, dengan
  instruksi eksplisit: bila login-gated, catat saja dan lanjut, JANGAN klik login.
- GAP YANG DICATAT JUJUR, mengikuti preseden Run 1, Run 3, Run 4, Run 5, dan Run 6:
  - Laporan per-wallet terperinci (holdings + trade terbaru per wallet) dari browser BELUM
    terkirim ke konteks run ini pada saat penulisan log.
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim (ambang: minimal 4 entitas privat berbeda membeli token baru
    yang sama) — bukan karena wallet terbukti tidak membeli, melainkan karena bukti per-wallet
    belum diterima. Wallet yang tidak terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline / state run 6 TIDAK diubah: last_checked tetap 2026-11-01T09:37:00+07:00 dan holdings
    per wallet tetap dari run 6, sampai laporan browser run ini benar-benar diterima. Hanya field
    `last_attempt` di state yang diperbarui sebagai penanda run ini.
- Bukti parsial read-only yang DIDAPAT pada run ini (saldo BNB on-chain via batch RPC, blok
  130984438, ~11:24 WIB) — saldo saja, BUKAN bukti beli/jual dan BUKAN pengganti laporan GMGN:
  - 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6: 0,07531 BNB (run 6: 0,07222) — NAIK ~0,0031 BNB;
    penyebabnya (sell/transfer masuk/gas) belum terverifikasi, TIDAK diklaim sebagai pembelian;
    wajib dicocokkan dengan laporan browser.
  - 0x2325f175975abdbcde555c79cc8e63381d28551b: 0,62530 BNB (run 6: 0,62530) — sama.
  - 0xda91cefe240175e6fab56271110427a4195ab71f: 0,05000 BNB (run 6: 0,05) — sama.
  - 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462: 0,00685 BNB (run 6: 0,00685) — sama.
  - 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc: 0,02479 BNB (run 6 batch: 0,02479) —
    TIDAK BERUBAH sejak batch run 3/run 4/run 5/run 6; diskrepansi GMGN-vs-on-chain (GMGN menunjukkan 0)
    MASIH belum terjelaskan, penyebabnya belum terverifikasi, dan TIDAK diklaim sebagai pembelian.
    Wajib dicek aktivitasnya (Tx In vs Buy) dari laporan browser run ini / run berikutnya.
  - Wallet lain praktis sama dengan run 6 (debu): 0x13d1… 0,0000119; 0x5b2f… 0,0000192;
    0x6ba7… 0,00148; 0x7564… 0,0000429; 0x8272… 0,0000158; 0x8922… 0,0000583; 0x93e7… 0,0000143;
    0xaab8… 0; 0xbe59… 0.
- Tindak lanjut: bila laporan browser run ini tiba belakangan, tambahkan sebagai adendum run ini
  dengan stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs baseline
  run 6. Bila tidak tiba, run berikutnya harus mengulang pembacaan ke-14 wallet dan mencatat
  holdings + aktivitas terbaru per wallet secara eksplisit, dengan perhatian khusus pada wallet
  0x8e96… (kenaikan saldo di atas) dan 0xf6a8… (diskrepansi saldo) sebelum menghitung sinyal apa pun.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.


## Adendum Run 7 — laporan browser diterima belakangan (setelah entri gap)

Pemeriksaan browser terukur 11:23–11:35 WIB per laporan (runtime mengukur jendela
11:23–11:36 WIB — selisih 1 menit di ujung akhir dicatat, tidak mengubah kesimpulan).
Semua 14 halaman memuat data publik TANPA login-gated, status "Disconnected", tanpa
klik Log in/Sign up/Connect, tanpa sign/transaksi. Koreksi atas bagian "GAP" di atas:
bukti per-wallet AKHIRNYA diterima, sehingga hitungan sinyal run 7 dapat ditetapkan
dari laporan ini dan state diperbarui dari laporan ini (last_checked
2026-11-01T11:35:00+07:00). Batasan laporan yang wajib dicatat:
- Tab Holdings memakai filter default yang teramati: "No assets held." = sesuai
  tampilan tab itu, BUKAN klaim saldo on-chain nol; token yang hanya diterima lewat
  Tx In tersaring dari Holdings.
- Contract address TIDAK tercatat pada run ini untuk token mana pun: tidak ada alamat
  kontrak lengkap yang terlihat dalam teks halaman (hanya alamat wallet sendiri dan
  alamat pengirim/penerima yang terpotong); CA tidak ditebak dari simbol. Token dicatat
  berdasarkan simbol saja, dan karena itu tidak dapat dipakai sebagai CA terverifikasi
  untuk perbandingan antar wallet — hitungan di bawah memakai simbol + konteks baseline,
  dan tidak ada token baru yang dibeli 2 wallet atau lebih sehingga keterbatasan ini
  tidak mengubah kesimpulan.
- Waktu aktivitas bersifat relatif terhadap waktu baca ("jam lalu") seperti dilaporkan
  GMGN, bukan stempel waktu absolut yang diverifikasi on-chain; label relatif dicocokkan
  dengan jumlah/nilai transaksi sebelum dinyatakan baru, mengikuti preseden run 3–6.

Per-wallet (ringkas; urutan sesuai tier-ab-watch.md):
1. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — dibaca ~11:23 WIB. BNB 0,075 ($53,06),
   kini cocok dengan batch on-chain 0,07531 BNB — kenaikan ~0,0031 BNB vs run 6 konsisten
   dengan aktivitas jual dalam jendela, tetapi kenaikan itu sendiri TIDAK diklaim sebagai
   pembelian tertentu. Holdings bukan nol: 爪子 $0,705 / 214K; MAX $2,44 / 737,6K;
   视界之眼 $4,42 / 467,3K; 朗月 $2,82 / 585,7K; 贵人鸟 $3,15 / 857,4K;
   奶蛙党 $2,54 / 745,4K. Aktivitas terbaru: Sell 币安人生 213K $2,25 (1h lalu) — trade
   BARU dalam jendela run 7, TETAPI ini SELL (dari re-buy 09:06 WIB run 6), bukan Buy,
   sehingga tidak dihitung sebagai pembelian token baru. Buy 币安人生 213K $1,365 (2h lalu),
   Buy 币安必胜 196,1K $1,379 (2h lalu), Buy 月球兔 165,2K $1,381 (3h lalu) adalah transaksi
   run 6 yang SAMA (jumlah dan nilai identik) — TIDAK dihitung ganda. Jadi: TIDAK ADA
   token baru di run 7 untuk wallet ini.
2.–6., 8.–13. (0x13d1…, 0x5b2f…, 0x6ba7…, 0x7564…, 0x8272…, 0x93e7…, 0xaab8…, 0xb787…,
   0xbe59…, 0xda91…, 0xf6a8…): TIDAK ADA buy baru. Aktivitas terbaru hanya Tx In/Tx Out
   lama (termasuk SKYAI dan mubarak sebagai holding/transfer lama, bukan buy baru).
   Holdings: "No assets held." untuk semuanya. Khusus wallet 13 (0xf6a8…): GMGN pada
   ~11:33 WIB MASIH menunjukkan BNB 0 ($0) dan aktivitas terbaru 11 hari lalu
   (Tx In NEX) — TIDAK menjelaskan saldo on-chain 0,02479 BNB yang tercatat di batch
   ~03:52, ~05:24, ~07:25, ~09:24, maupun ~11:24 WIB (tidak berubah). Diskrepansi
   GMGN-vs-on-chain ini MASIH belum terjelaskan, penyebabnya belum terverifikasi, dan
   TIDAK diklaim sebagai pembelian; wajib dicek ulang pada run berikutnya.
7. 0x892200223bdfb11d2506c5ab1cae9222ce253acc — dibaca ~11:28 WIB. BNB 0 ($0,041).
   Holdings tampil: XPIN, WKC, XRP, SLX, BANK, SKYAI, CREPE, TAG, PENGU, elizaOS (nilai
   bergeser tipis vs run 6). Buy terbaru 16–18 hari lalu (XPIN, XRP) — baseline, bukan
   buy baru. TIDAK ADA buy baru.
14. 0x2325f175975abdbcde555c79cc8e63381d28551b — dibaca ~11:35 WIB. BNB 0,625 ($440,91).
   Holdings bukan nol hanya PTG $106,96 / 34,29 (sebelumnya $112,51). Aktivitas terbaru:
   Tx In NS +0,0₄63399 $0,003 (7h lalu, ~04:30 WIB) — Tx In yang SAMA dengan debu NS
   run 4/5/6, BUKAN Buy; Buy/Sell 盘古重生/莫大回归/币安人生 berlabel 12h lalu menunjuk
   sekitar 23:xx WIB 2026-10-31, yaitu SEBELUM jendela run 7 dan semuanya token baseline
   run 1/run 2 — bukan token baru bagi wallet ini. TIDAK ADA buy baru yang terverifikasi
   dalam jendela run 7.

Hitungan sinyal run 7 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 7 (setelah 09:37 WIB): TIDAK ADA.
  Satu-satunya trade baru dalam jendela adalah Sell 币安人生 oleh wallet 1, dan Sell
  bukan pembelian.
- TIDAK ADA token yang dibeli oleh 2 wallet atau lebih dalam jendela ini, apalagi 4.
  Jadi TIDAK ADA SINYAL (ambang: minimal 4 entitas privat berbeda membeli token baru yang sama).
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada
  runtuhan entitas. Co-buy/co-hold saja TIDAK meruntuhkan entitas.
- Pembelian 1 wallet saja = bukan sinyal; di run ini bahkan tidak ada pembelian token baru
  1 wallet pun.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-01T11:35:00+07:00; wallet 1 BNB + holdings + Sell 币安人生; wallet 14 BNB + PTG +
  Tx In NS; wallet 13 dicatat dengan diskrepansi saldo yang masih belum terjelaskan).
  Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 8 — Minggu 2026-11-01, 13:22–~13:25 WIB (gap: laporan browser belum diterima saat penulisan)

- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat (Tier A privat 13 + Tier B privat 1).
  Daftar lama 23 alamat TIDAK dipakai.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-14 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>)
  DIDISPATCH (task browser-task:2496fd9f-97ec-5b39-8a90-32adcc2eddd6) pada ~13:23 WIB, dengan
  instruksi eksplisit: bila login-gated, catat saja dan lanjut, JANGAN klik login.
- GAP YANG DICATAT JUJUR, mengikuti preseden Run 1, Run 3, Run 4, Run 5, Run 6, dan Run 7:
  - Laporan per-wallet terperinci (holdings + trade terbaru per wallet) dari browser BELUM
    terkirim ke konteks run ini pada saat penulisan log.
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim (ambang: minimal 4 entitas privat berbeda membeli token baru
    yang sama) — bukan karena wallet terbukti tidak membeli, melainkan karena bukti per-wallet
    belum diterima. Wallet yang tidak terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline / state run 7 TIDAK diubah: last_checked tetap 2026-11-01T11:35:00+07:00 dan holdings
    per wallet tetap dari run 7, sampai laporan browser run ini benar-benar diterima. Hanya field
    `last_attempt` di state yang diperbarui sebagai penanda run ini.
- Bukti parsial read-only yang DIDAPAT pada run ini (saldo BNB on-chain via batch RPC, blok
  131000359, ~13:25 WIB) — saldo saja, BUKAN bukti beli/jual dan BUKAN pengganti laporan GMGN:
  - 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6: 0,07531 BNB (run 7: 0,07531) — sama.
  - 0x2325f175975abdbcde555c79cc8e63381d28551b: 0,62530 BNB (run 7: 0,62530) — sama.
  - 0xda91cefe240175e6fab56271110427a4195ab71f: 0,05000 BNB (run 7: 0,05) — sama.
  - 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462: 0,00685 BNB (run 7: 0,00685) — sama.
  - 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc: 0,02479 BNB (run 7 batch: 0,02479) —
    TIDAK BERUBAH; diskrepansi GMGN-vs-on-chain (GMGN menunjukkan 0 di run-run sebelumnya)
    MASIH belum terjelaskan, penyebabnya belum terverifikasi, dan TIDAK diklaim sebagai pembelian.
    Wajib dicek aktivitasnya (Tx In vs Buy) dari laporan browser run ini / run berikutnya.
  - Wallet lain praktis sama dengan run 7 (debu): 0x13d1… 0,0000119; 0x5b2f… 0,0000192;
    0x6ba7… 0,00148; 0x7564… 0,0000429; 0x8272… 0,0000158; 0x8922… 0,0000583; 0x93e7… 0,0000143;
    0xaab8… 0; 0xbe59… 0.
- Tindak lanjut: bila laporan browser run ini tiba belakangan, tambahkan sebagai adendum run ini
  dengan stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs baseline
  run 7. Bila tidak tiba, run berikutnya harus mengulang pembacaan ke-14 wallet dan mencatat
  holdings + aktivitas terbaru per wallet secara eksplisit, dengan perhatian khusus pada wallet
  0xf6a8… (diskrepansi saldo di atas) sebelum menghitung sinyal apa pun.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Adendum Run 8 — laporan browser diterima setelah log gap ditulis

Pemeriksaan browser terukur 13:23–13:32 WIB (waktu ukur runtime, bukan klaim di dalam laporan).
Semua 14 halaman memuat data publik TANPA login-gated, status "Disconnected", tanpa klik
Log in/Sign up/Connect, tanpa sign/transaksi. Koreksi atas bagian "GAP" di atas: bukti per-wallet
AKHIRNYA diterima, sehingga hitungan sinyal run 8 dapat ditetapkan dari laporan ini dan state
diperbarui dari laporan ini (last_checked 2026-11-01T13:32:00+07:00). Batasan laporan yang wajib
dicatat:
- Tab Holdings memakai filter default yang teramati: "Hide Didn't Buy" tercentang,
  "Hide Tiny Pool"/"Hide Honeypot"/"Hide Closed" tidak tercentang: "No assets held." =
  sesuai tampilan tab itu, BUKAN klaim saldo on-chain nol; token yang hanya diterima lewat
  Tx In tersaring dari Holdings.
- Contract address TIDAK tercatat pada run ini untuk token mana pun: tidak ada alamat kontrak
  lengkap yang terlihat dalam teks halaman (alamat yang disingkat bukan CA lengkap); CA tidak
  ditebak dari simbol. Token dicatat berdasarkan simbol saja, dan karena itu tidak dapat dipakai
  sebagai CA terverifikasi untuk perbandingan antar wallet — hitungan di bawah memakai simbol +
  konteks baseline, dan tidak ada token baru yang dibeli 2 wallet atau lebih sehingga
  keterbatasan ini tidak mengubah kesimpulan.
- Waktu aktivitas bersifat relatif terhadap waktu baca ("jam lalu") seperti dilaporkan GMGN,
  bukan stempel waktu absolut yang diverifikasi on-chain; label relatif dicocokkan dengan
  jumlah/nilai transaksi sebelum dinyatakan baru, mengikuti preseden run 3–7.

Per-wallet (ringkas; urutan sesuai tier-ab-watch.md):
1. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — dibaca ~13:23–13:32 WIB. BNB 0,075 ($53,14),
   cocok dengan batch on-chain 0,07531 BNB (blok 131000359). Holdings bukan nol: 爪子 $0,705 /
   214K; MAX $2,44 / 737,6K; 视界之眼 $4,92 / 467,3K; 朗月 $2,63 / 585,7K; 贵人鸟 $3,09 / 857,4K;
   奶蛙党 $2,54 / 745,4K (sisanya $0 / Sell All). Aktivitas terbaru: Sell 币安人生 213K $2,25
   (3h lalu); Sell 币安必胜 196,1K $1,253 (4h lalu); Buy 币安人生 213K $1,365 (4h lalu); Sell
   月球兔 165,2K $0,704 (4h lalu); Buy 币安必胜 196,1K $1,379 (4h lalu); Buy 月球兔 165,2K $1,381
   (5h lalu); Sell/Buy Kim 133,5K (8h lalu); Buy 爪子 214K $1,38 (10h lalu); Sell MMGA 143,8K
   $1,247 (11h lalu). Penilaian vs baseline run 7: SEMUA ini adalah trade run 6/run 3/run 4 yang
   SAMA (jumlah dan nilai identik) dengan label relatif bergeser karena waktu baca lebih lambat
   — TIDAK ada buy baru di run 8 untuk wallet ini.
2.–6., 8.–13. (0x13d1…, 0x5b2f…, 0x6ba7…, 0x7564…, 0x8272…, 0x93e7…, 0xaab8…, 0xb787…,
   0xbe59…, 0xda91…, 0xf6a8…): TIDAK ADA buy baru. Aktivitas terbaru hanya Tx In/Tx Out lama
   (termasuk SKYAI dan mubarak sebagai holding/transfer lama, bukan buy baru). Holdings:
   "No assets held." untuk semuanya. Khusus wallet 13 (0xf6a8…): GMGN pada ~13:32 WIB MASIH
   menunjukkan BNB 0 ($0) dan aktivitas terbaru 11 hari lalu (Tx In NEX) — TIDAK menjelaskan
   saldo on-chain 0,02479 BNB yang tercatat di batch ~03:52, ~05:24, ~07:25, ~09:24, maupun
   ~13:25 WIB (tidak berubah). Diskrepansi GMGN-vs-on-chain ini MASIH belum terjelaskan,
   penyebabnya belum terverifikasi, dan TIDAK diklaim sebagai pembelian; wajib dicek ulang pada
   run berikutnya.
7. 0x892200223bdfb11d2506c5ab1cae9222ce253acc — BNB 0 ($0,041). Holdings tampil: XPIN, WKC,
   XRP, SLX, BANK, SKYAI, CREPE, TAG, PENGU, elizaOS (nilai bergeser tipis vs run 7), plus ETH
   dan BTCB $0 (Sell All). Buy terbaru 16–18 hari lalu (XPIN, XRP) — baseline, bukan buy baru.
   TIDAK ADA buy baru.
14. 0x2325f175975abdbcde555c79cc8e63381d28551b — BNB 0,625 ($441,08). Holdings bukan nol hanya
   PTG $106,96 / 34,29 (kembali ke nilai run 7 setelah $112,51 di run 5/6). Aktivitas terbaru:
   Tx In NS +0,0₄63399 $0,003 (9h lalu, ~04:30 WIB) — Tx In yang SAMA dengan debu NS run 4/5/6/7,
   BUKAN Buy; Sell 盘古重生 15,2M $129,9 (13h lalu) adalah sell yang SAMA dengan run 4; Buy/Sell
   盘古重生/莫大回归/币安人生 berlabel 14h lalu menunjuk sekitar 23:xx WIB 2026-10-31, yaitu
   SEBELUM jendela run 8 dan semuanya token baseline run 1/run 2 — bukan token baru bagi wallet
   ini. TIDAK ADA buy baru yang terverifikasi dalam jendela run 8.

Hitungan sinyal run 8 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 8 (setelah 11:35 WIB): TIDAK ADA.
- TIDAK ADA token yang dibeli oleh 2 wallet atau lebih dalam jendela ini, apalagi 4.
  Jadi TIDAK ADA SINYAL (ambang: minimal 4 entitas privat berbeda membeli token baru yang sama).
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada
  runtuhan entitas. Co-buy/co-hold saja TIDAK meruntuhkan entitas.
- Pembelian 1 wallet saja = bukan sinyal; di run ini bahkan tidak ada pembelian token baru
  1 wallet pun.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-01T13:32:00+07:00; wallet 1 BNB + holdings; wallet 14 BNB + PTG + Tx In NS;
  wallet 13 dicatat dengan diskrepansi saldo yang masih belum terjelaskan).
  Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 9 — Minggu 2026-11-01, 15:22–~15:25 WIB (gap: laporan browser belum diterima saat penulisan)

- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat (Tier A privat 13 + Tier B privat 1).
  Daftar lama 23 alamat TIDAK dipakai.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-14 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>)
  DIDISPATCH (task browser-task:6da5c2af-ac65-59e8-9b1f-989d940d64b9) pada ~15:23 WIB, dengan
  instruksi eksplisit: bila login-gated, catat saja dan lanjut, JANGAN klik login.
- GAP YANG DICATAT JUJUR, mengikuti preseden Run 1, Run 3, Run 4, Run 5, Run 6, dan Run 7:
  - Laporan per-wallet terperinci (holdings + trade terbaru per wallet) dari browser BELUM
    terkirim ke konteks run ini pada saat penulisan log.
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim (ambang: minimal 4 entitas privat berbeda membeli token baru
    yang sama) — bukan karena wallet terbukti tidak membeli, melainkan karena bukti per-wallet
    belum diterima. Wallet yang tidak terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline / state run 8 TIDAK diubah: last_checked tetap 2026-11-01T13:32:00+07:00 dan holdings
    per wallet tetap dari run 8, sampai laporan browser run ini benar-benar diterima. Hanya field
    `last_attempt` di state yang diperbarui sebagai penanda run ini.
- Bukti parsial read-only yang DIDAPAT pada run ini (saldo BNB on-chain via batch RPC, blok
  131016344, ~15:25 WIB) — saldo saja, BUKAN bukti beli/jual dan BUKAN pengganti laporan GMGN:
  - 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6: 0,07529 BNB (run 8: 0,07531) — praktis sama.
  - 0x2325f175975abdbcde555c79cc8e63381d28551b: 0,62530 BNB (run 8: 0,625) — praktis sama.
  - 0xda91cefe240175e6fab56271110427a4195ab71f: 0,05000 BNB (run 8: 0,05) — sama.
  - 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462: 0,00685 BNB (run 8: 0,007) — sama.
  - 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc: 0,02479 BNB (run 8 batch: 0,02479) —
    TIDAK BERUBAH sejak batch run 3–8; diskrepansi GMGN-vs-on-chain (GMGN menunjukkan 0)
    MASIH belum terjelaskan, penyebabnya belum terverifikasi, dan TIDAK diklaim sebagai pembelian.
    Wajib dicek aktivitasnya (Tx In vs Buy) dari laporan browser run ini / run berikutnya.
  - Wallet lain praktis sama dengan run 8 (debu): 0x13d1… 0,0000119; 0x5b2f… 0,0000192;
    0x6ba7… 0,00148; 0x7564… 0,0000429; 0x8272… 0,0000158; 0x8922… 0,0000583; 0x93e7… 0,0000143;
    0xaab8… 0; 0xbe59… 0.
- Tindak lanjut: bila laporan browser run ini tiba belakangan, tambahkan sebagai adendum run ini
  dengan stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs baseline
  run 8. Bila tidak tiba, run berikutnya harus mengulang pembacaan ke-14 wallet dan mencatat
  holdings + aktivitas terbaru per wallet secara eksplisit, dengan perhatian khusus pada wallet
  0xf6a8… (diskrepansi saldo di atas) sebelum menghitung sinyal apa pun.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Adendum Run 9 — laporan browser diterima setelah log gap ditulis

Pemeriksaan browser terukur 15:23–15:35 WIB (waktu ukur runtime; klaim di dalam laporan
15:23–15:34 WIB, selisih 1 menit pada akhir — dipakai waktu ukur runtime). Semua 14 halaman
memuat data publik TANPA login-gated, status Disconnected, tanpa klik Log in/Sign up/Connect,
tanpa sign/transaksi. Koreksi atas bagian "GAP" di atas: bukti per-wallet AKHIRNYA diterima,
sehingga hitungan sinyal run 9 dapat ditetapkan dari laporan ini dan state diperbarui dari
laporan ini (last_checked 2026-11-01T15:35:00+07:00). Batasan laporan yang wajib dicatat:
- Tab Holdings memakai filter default "Hide Didn't Buy" (tercentang di semua halaman):
  "No assets held." = sesuai tampilan tab itu, BUKAN klaim saldo on-chain nol; token yang hanya
  diterima lewat Tx In tersaring dari Holdings.
- Contract address TIDAK tercatat pada run ini untuk token mana pun: tidak ada alamat kontrak
  lengkap yang terlihat dalam teks halaman; CA tidak ditebak dari simbol. Token dicatat
  berdasarkan simbol/nama tampil saja, dan karena itu tidak dapat dipakai sebagai CA terverifikasi
  untuk perbandingan antar wallet — hitungan di bawah memakai simbol + konteks baseline, dan
  tidak ada token baru yang dibeli 2 wallet atau lebih sehingga keterbatasan ini tidak mengubah
  kesimpulan.
- Waktu aktivitas bersifat relatif terhadap waktu baca ("jam lalu") seperti dilaporkan GMGN,
  bukan stempel waktu absolut yang diverifikasi on-chain; label relatif dicocokkan dengan
  jumlah/nilai transaksi sebelum dinyatakan baru, mengikuti preseden run 3–8.

Per-wallet (ringkas; urutan sesuai tier-ab-watch.md):
1. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — dibaca ~15:23 WIB. BNB 0,075 ($53,26),
   cocok dengan batch on-chain run 9 (0,07529 BNB). Holdings bersaldo di atas (diurutkan
   Balance menurun): 旺财 $6,71 / 851,5K; 视界之眼 $5,33 / 467,3K; 雨爱 $4,09 / 851K;
   隆德齐 $3,62 / 751,7K; 贵人鸟 $3,53 / 857,4K; 星游记 $2,77 / 840K; ok $2,62 / 840,2K;
   朗月 $2,6 / 585,7K; 咪咪 $2,55 / 775,6K; 奶蛙党 $2,54 / 745,4K; MAX $2,44 / 737,6K;
   lucky $2,39 / 632,4K; WTB $1,42 / 522,1K; SIC $1,4 / 675,5K; 爪子 $0,705 / 214K
   (sisanya $0 / Sell All). Token-token ini SUDAH ada di baseline run 2 (daftar holdings
   run 2 yang sama), hanya urutan/nilai bergeser — bukan buy baru. Aktivitas terbaru:
   Sell 币安人生 213K $2,25; Buy 币安人生 213K $1,365; Sell/Buy 币安必胜 196,1K; Sell/Buy
   月球兔 165,2K; Sell/Buy Kim 133,5K; Buy 爪子 214K $1,38; Sell MMGA 143,8K — semuanya
   transaksi run 3/run 4/run 6 yang SAMA (jumlah dan nilai identik, label relatif bergeser
   karena waktu baca lebih lambat), semuanya SEBELUM jendela run 9 (13:32 WIB). Jadi:
   TIDAK ADA buy baru di run 9 untuk wallet ini.
2.–6., 8.–13. (0x13d1…, 0x5b2f…, 0x6ba7…, 0x7564…, 0x8272…, 0x93e7…, 0xaab8…, 0xb787…,
   0xbe59…, 0xda91…, 0xf6a8…): TIDAK ADA buy baru. Aktivitas terbaru hanya Tx In/Tx Out lama
   (termasuk SKYAI dan mubarak sebagai holding/transfer lama, bukan buy baru).
   Holdings: "No assets held." untuk semuanya. Khusus wallet 13 (0xf6a8…): GMGN pada
   ~15:34 WIB MASIH menunjukkan BNB 0 ($0) dan aktivitas terbaru 11 hari lalu (Tx In NEX) —
   TIDAK menjelaskan saldo on-chain 0,02479 BNB yang tercatat di batch run 3–9 (tidak berubah).
   Diskrepansi GMGN-vs-on-chain ini MASIH belum terjelaskan, penyebabnya belum terverifikasi,
   dan TIDAK diklaim sebagai pembelian; wajib dicek ulang pada run berikutnya.
7. 0x892200223bdfb11d2506c5ab1cae9222ce253acc — BNB 0 ($0,041). Holdings tampil: XPIN,
   WKC, XRP, SLX, BANK, SKYAI, CREPE, TAG, PENGU, elizaOS (nilai bergeser tipis vs run 8),
   plus ETH dan BTCB $0 (Sell All). Buy terbaru 16–18 hari lalu (XPIN, XRP) — baseline,
   bukan buy baru. TIDAK ADA buy baru.
14. 0x2325f175975abdbcde555c79cc8e63381d28551b — BNB 0,625 ($442,5). Holdings bersaldo
   hanya PTG $97,7 / 34,29 (jumlah sama seperti run 8, nilai bergeser dari $106,96) plus
   BNC4 $0,006 debu; sisanya $0 / Sell All. Aktivitas terbaru: Tx In NS debu 11h lalu
   (~04:30 WIB) — Tx In yang SAMA dengan debu NS run 4/5/6/7/8, BUKAN Buy; Sell 盘古重生
   15,2M $129,9 (15h lalu) adalah sell yang SAMA dengan run 4; Buy-buy berlabel 16h lalu
   (盘古重生, 莫大回归, 币安人生) menunjuk sekitar 23:xx WIB 2026-10-31, yaitu SEBELUM
   jendela run 9 dan semuanya token baseline run 1/run 2 — bukan token baru bagi wallet ini.
   TIDAK ADA buy baru yang terverifikasi dalam jendela run 9.

Hitungan sinyal run 9 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 9 (setelah 13:32 WIB): TIDAK ADA.
  Satu-satunya aktivitas dalam jendela yang tampak adalah duplikat label dari trade run 3/4/6
  dan satu Tx In debu yang bukan Buy.
- TIDAK ADA token yang dibeli oleh 2 wallet atau lebih dalam jendela ini, apalagi 4.
  Jadi TIDAK ADA SINYAL (ambang: minimal 4 entitas privat berbeda membeli token baru yang sama).
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada
  runtuhan entitas. Co-buy/co-hold saja TIDAK meruntuhkan entitas.
- Pembelian 1 wallet saja = bukan sinyal; di run ini bahkan tidak ada pembelian token baru
  1 wallet pun.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-01T15:35:00+07:00; wallet 1 holdings + BNB; wallet 14 BNB + PTG + Tx In NS;
  wallet 7 holdings; wallet 13 dicatat dengan diskrepansi saldo yang masih belum terjelaskan).
  Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 10 — Minggu 2026-11-01, 17:22–~17:25 WIB (gap: laporan browser belum diterima saat penulisan)

- Daftar dibaca dari `tier-ab-watch.md` setiap run: SETELAH promosi 2026-11-01 ~17:16 WIB,
  set terpantau adalah 49 entitas (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35),
  BUKAN lagi 14. Daftar lama 23 alamat TIDAK dipakai (6 wallet exchange + 3 kontrak di Tier E).
  Ambang sinyal SETELAH promosi: >25% dari 49 = minimal 13 entitas berbeda membeli token baru
  yang sama. Ambang lama 4 TIDAK lagi berlaku untuk set ini.
- CATATAN PENTING UNTUK RUN INI: 35 wallet Tier C berstatus `pending_first_run` di state —
  baseline GMGN mereka BELUM terbentuk (sumber baseline mereka hanya scan ekspansi 2026-11-01).
  Pembacaan GMGN pertama ini MENETAPKAN baseline mereka; trade lama mereka dari scan ekspansi
  (beli awal di >=2 pool) BUKAN pembelian baru dalam jendela run ini, dan tidak boleh dihitung
  sebagai sinyal hanya karena pertama kali tampil di GMGN. Hanya Buy yang terverifikasi terjadi
  setelah batas jendela run sebelumnya (15:35 WIB) dan belum pernah tercatat bagi wallet itu
  yang dapat dihitung sebagai pembelian baru — dan untuk Tier C, pembandingnya adalah data scan
  ekspansi, bukan baseline GMGN yang belum ada.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-49 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>)
  DIDISPATCH (task browser-task:f76b1758-32f3-5add-b5fe-443475082ef7) pada ~17:23 WIB, dengan
  instruksi eksplisit: bila login-gated, catat saja dan lanjut, JANGAN klik login.
- GAP YANG DICATAT JUJUR, mengikuti preseden Run 1, Run 3, Run 4, Run 5, Run 6, dan Run 7:
  - Laporan per-wallet terperinci (holdings + trade terbaru per wallet) dari browser BELUM
    terkirim ke konteks run ini pada saat penulisan log.
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim (ambang baru: minimal 13 entitas berbeda membeli token baru
    yang sama) — bukan karena wallet terbukti tidak membeli, melainkan karena bukti per-wallet
    belum diterima. Wallet yang tidak terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
    Verifikasi deployer + pendanaan untuk 35 wallet Tier C MASIH tertunda (diungkap sebelum
    promosi) — tidak ada runtuhan yang diklaim dari run ini.
  - Baseline / state run 9 TIDAK diubah: last_checked tetap 2026-11-01T15:35:00+07:00 dan holdings
    per wallet tetap dari run 9, sampai laporan browser run ini benar-benar diterima. Hanya field
    `last_attempt` di state yang diperbarui sebagai penanda run ini.
- Bukti parsial read-only yang DIDAPAT pada run ini (saldo BNB on-chain via batch RPC,
  ~17:25 WIB) — saldo saja, BUKAN bukti beli/jual dan BUKAN pengganti laporan GMGN:
  - 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6: 0,07327 BNB (run 9: 0,07529) — TURUN ~0,002 BNB;
    penyebabnya (trade/gas/transfer) belum terverifikasi, TIDAK diklaim sebagai pembelian;
    wajib dicocokkan dengan laporan browser.
  - 0x2325f175975abdbcde555c79cc8e63381d28551b: 0,61525 BNB (run 9: 0,62530) — TURUN ~0,010 BNB;
    penyebabnya belum terverifikasi, TIDAK diklaim sebagai pembelian; wajib dicocokkan
    dengan laporan browser.
  - 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc: 0,02479 BNB (run 9 batch: 0,02479) —
    TIDAK BERUBAH sejak batch run 3–9; diskrepansi GMGN-vs-on-chain (GMGN menunjukkan 0 di
    run-run sebelumnya) MASIH belum terjelaskan, penyebabnya belum terverifikasi, dan TIDAK
    diklaim sebagai pembelian. Wajib dicek aktivitasnya (Tx In vs Buy) dari laporan browser
    run ini / run berikutnya.
  - Wallet asli lain praktis sama dengan run 9: 0x13d1… ~0,00001; 0x5b2f… ~0,00002;
    0x6ba7… 0,00148; 0x7564… ~0,00004; 0x8272… ~0,00002; 0x8922… ~0,00006; 0x93e7… ~0,00001;
    0xaab8… 0; 0xbe59… 0; 0xb787… 0,00685; 0xda91… 0,05.
  - Tier C (snapshot saldo pertama pada run ini, BUKAN pembanding baseline — tidak ada
    perubahan yang diklaim): 0x9856… 0; 0x3628… 0,01024; 0xa0c1… 0,02286; 0x40a8… 0,02215;
    0xc7c5… 0,01077; 0xad94… 0,04843; 0x3803… 0,03642; 0x7488… 0,02375; 0xdb2d… 0,29355;
    0xc621… 0,02924; 0xf795… 0,3004; 0x9cdd… 0,02928; 0xaa49… 0,21817; 0x82c6… 0,35552;
    0x3154… 0,31444; 0xca4e… 0,31389; 0xe9ed… 0,37562; 0x3a39… 0,30953; 0xcb08… 0,28552;
    0xb940… 0,25678; 0x4522… 0,37374; 0x5b4b… 0,33307; 0xc659… 0,15893; 0x3623… 0,3;
    0xf968… 0,3; 0x2cc8… 0,29539; 0x97bd… 0,02947; 0x1cce… 0,36777; 0xc0c8… 0,3;
    0xc194… 0,32604; 0xa952… 0,32467; 0x92bc… 0,0295; 0x9b51… 0,32011; 0xfdec… 0,3;
    0x64e8… 0,32627. Beberapa wallet Tier C tepat di 0,3 BNB dicatat apa adanya sebagai
    saldo saja, bukan sebagai pola yang diverifikasi.
- Tindak lanjut: bila laporan browser run ini tiba belakangan, tambahkan sebagai adendum run ini
  dengan stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs baseline
  run 9 (untuk 14 wallet asli) serta tetapkan baseline GMGN pertama untuk 35 wallet Tier C.
  Bila tidak tiba, run berikutnya harus mengulang pembacaan ke-49 wallet dan mencatat holdings
  + aktivitas terbaru per wallet secara eksplisit, dengan perhatian khusus pada wallet
  0x8e96… dan 0x2325… (penurunan saldo di atas) dan 0xf6a8… (diskrepansi saldo) sebelum
  menghitung sinyal apa pun.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Adendum Run 10 — laporan browser diterima setelah log gap ditulis

Pemeriksaan browser terukur 17:24–18:38 WIB (waktu ukur runtime; klaim di dalam laporan
17:24–18:35 WIB — selisih 3 menit pada akhir, dipakai waktu ukur runtime). 49 dari 50 halaman
terpantau memuat data publik TANPA login-gated, status Disconnected, tanpa klik Log in/Sign
up/Connect, tanpa sign/transaksi. SATU PENGECUALIAN CAKUPAN: wallet 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36
(whale SENSEI #1) dipromosikan secara individual ~17:44 WIB, SETELAH dispatch browser run ini
(~17:23 WIB), sehingga TIDAK terbaca di run 10. Wallet itu dicatat TIDAK TERBACA, bukan tidak
membeli, dan wajib dibaca pada run 11. Ambang pada 50 entitas tetap 13 (floor(0,25×50)+1),
jadi celah cakupan ini tidak mengubah kesimpulan sinyal di bawah.
Batasan laporan yang wajib dicatat:
- Tab Holdings memakai filter default "Hide Didn't Buy": "No assets held." = sesuai tampilan
  tab itu, BUKAN klaim saldo on-chain nol; token yang hanya diterima lewat Tx In tersaring
  dari Holdings. Beberapa wallet Tier C tidak menampilkan frasa itu melainkan baris-baris $0
  Sell All — perbedaan itu dipertahankan di state.
- Contract address TIDAK tercatat untuk token mana pun: tidak ada alamat kontrak lengkap yang
  terlihat dalam teks halaman; CA tidak ditebak dari simbol. Ini PENTING pada run ini (lihat
  hitungan sinyal): daftar holdings wallet 0xc7c5… (149 baris non-nol) dan 0x3803… (169 baris
  non-nol) menampilkan simbol yang sama sebagai baris terpisah berulang (mis. KIM, Tofu,
  ZERODAY) — bukti langsung bahwa SIMBOL YANG SAMA BUKAN BERARTI CA YANG SAMA di tampilan
  GMGN ini. Karena itu kecocokan berdasarkan simbol saja TIDAK dapat dipakai sebagai
  CA-terverifikasi untuk perbandingan antar wallet.
- Waktu aktivitas bersifat relatif terhadap waktu baca ("menit/jam lalu") seperti dilaporkan
  GMGN, bukan stempel waktu absolut yang diverifikasi on-chain; label relatif dicocokkan
  dengan jumlah/nilai transaksi sebelum dinyatakan baru, mengikuti preseden run 3–9.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

Per-wallet (ringkas; urutan sesuai tier-ab-watch.md; detail penuh ada di laporan browser run ini):
1. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — BNB 0,073 ($52,31), cocok dengan batch
   on-chain 17:25 WIB (0,07327). Holdings bukan nol: 旺财 $6,76; 视界之眼 $6,74; 雨爱 $4,09;
   隆德齐 $3,62; 贵人鸟 $3,12; 星游记 $2,77; 朗月 $2,56; ok $2,56; 咪咪 $2,55; 奶蛙党 $2,54;
   MAX $2,44; lucky $2,39; 币安人生 $1,52 / 141,6K; WTB $1,42; SIC $1,40; 爪子 $0,705.
   SATU trade dalam jendela (setelah 15:35 WIB): Buy 币安人生 141,6K $1,379 (~47m sebelum
   pembacaan wallet ini, ~16:4x WIB). Ini RE-BUY token yang sudah dikenal wallet ini sejak
   run 1/run 2, BUKAN token baru — tidak dihitung. Trade lain di 10 teratas (7–14h lalu)
   adalah trade run 3/4/6 yang sama. Penurunan BNB 0,07529→0,07327 seukuran dengan buy
   $1,379 + gas, dicatat sebagai konsistensi saja, bukan bukti tersendiri.
2.–6., 8.–13. (0x13d1…, 0x5b2f…, 0x6ba7…, 0x7564…, 0x8272…, 0x93e7…, 0xaab8…, 0xb787…,
   0xbe59…, 0xda91…, 0xf6a8…): TIDAK ADA buy baru. Aktivitas terbaru hanya Tx In/Tx Out lama
   (termasuk SKYAI dan mubarak sebagai holding/transfer lama, bukan buy baru). Holdings:
   "No assets held." untuk semuanya. Khusus wallet 13 (0xf6a8…): GMGN pada run 10 MASIH
   menunjukkan BNB 0 ($0) dan aktivitas terbaru 11 hari lalu (Tx In NEX) — TIDAK menjelaskan
   saldo on-chain 0,02479 BNB yang tercatat di batch 17:25 WIB (tidak berubah sejak run 3).
   Diskrepansi GMGN-vs-on-chain ini MASIH belum terjelaskan, penyebabnya belum terverifikasi,
   dan TIDAK diklaim sebagai pembelian; wajib dicek ulang pada run berikutnya.
7. 0x892200223bdfb11d2506c5ab1cae9222ce253acc — BNB 0 ($0,042). Holdings tampil: XPIN
   $268,3K; SKYAI $185,4K; CREPE $128,3K; PENGU $51,8K; XRP $37,8K; SLX $10,7K; BANK $4,81K;
   WKC $1,04K; elizaOS $961,26; TAG $166. Buy terbaru 16–18 hari lalu (XPIN, XRP) — baseline,
   bukan buy baru. TIDAK ADA buy baru.
14. 0x2325f175975abdbcde555c79cc8e63381d28551b — BNB 0,615 ($439,22), cocok dengan batch
   on-chain 17:25 WIB (0,61525). Holdings bukan nol: PTG $100,14 / 34,29; BNCB $0,503 / 0,099;
   BNC4 $0,006 debu. Aktivitas dalam jendela BUKAN Buy: Tx In BNCB (24–27m sebelum baca);
   Tx In 币安狗 +250B dan Add 币安狗 +0,01 WBNB and 250B (1h sebelum baca — penambahan
   likuiditas, bukan Buy). BNCB adalah holding BARU lewat Tx In, dicatat sebagai holding,
   BUKAN sebagai pembelian. Tx In NS debu 13h lalu adalah debu yang SAMA dengan run 4–9.
   Sell/Buy 盘古重生 17–18h lalu adalah trade baseline sebelum jendela. Penurunan BNB
   0,62530→0,61525 seukuran dengan Add 0,01 WBNB, dicatat sebagai konsistensi saja.
   Jadi: TIDAK ADA buy baru yang terverifikasi untuk wallet ini di run 10.
15.–49. Tier C (35 wallet, BASELINE GMGN PERTAMA pada run ini — lihat peringatan di bawah):
   Semua wallet ini aktif bertransaksi pada menit-menit pembacaan. Ringkas per wallet
   (BNB GMGN; holdings non-nol utama; buy teratas dalam 10 aktivitas):
   - 0x9856…: BNB 0; holdings $0 (鼻涕, ZAGS Sell All); Buy/Sell 鼻涕 7,93K $0,498 dan
     ZAGS 22,68K $0,498 (~52–54m sebelum baca).
   - 0x3628…: BNB 0,01; ZAGS $0,142; Buy/Sell ZAGS dan 鼻涕 1,13K $0,071.
   - 0xa0c1…: BNB 0,023; LAPTOP $0,164, UNSAFU $0,147; Buy ZAGS dan 鼻涕 1,13K $0,071.
   - 0x40a8…: BNB 0,022; 币安马到成功 $209,64 / 1,5M; Buy NITRO 894,78 $5,002, 鼻涕 188K $5,
     FORX 8,65K $5, ZAGS 187,5K $5,005.
   - 0xc7c5…: BNB 0,011; 149 baris non-nol debu (masing-masing <$0,26; simbol berulang
     sebagai baris terpisah); Buy MARVIN/Coomer/ZAGS/Chub/MUSK 1,13K $0,024.
   - 0xad94…: BNB 0,048; debu BSA/AgenC/Hypurr/dll ($0,025–$0,06); Buy BLACKED/ZAGS 1,13K $0,024.
   - 0x3803…: BNB 0,037; 169 baris non-nol debu (masing-masing <$0,26; simbol berulang);
     Buy Anakin/Marvin/byenance/白いヤ 832,25 $0,018; ZAGS hanya dijual di 10 teratas.
   - 0x7488…: BNB 0,024; holdings $0 Sell All; Buy SOS 1,1K $0,062, 6O6 11 $0,063,
     DRIVE 11 $0,057, BULL 110K $0,063, x425 110 $0,064 — TIDAK ada buy ZAGS/SI di 10 teratas.
   - 0xdb2d…: BNB 0,405; OnHold $0,132; Buy SI 8,1M $193,1, 2,9M $108,6, 3,3M $111,1
     diselingi penjualan SI besar-besaran.
   - 0xc621…: BNB 0,407; holdings $0 Sell All; Buy SI 295K $9,233 dan 8,2M $200,6.
   - 0xf795…: BNB 0,208; holdings $0 Sell All; Buy SI 6,3M $217,3, 6,1M $192,6, 5,2M $192,8
     dan Buy ZAGS 8M $221.
   - 0x9cdd…: BNB 0,328; ZAGS $31,71 / 1,8M; Buy ZAGS 7,7M $111,5 dan Buy SI 14,6M $194.
   - 0xaa49…: BNB 0,167; ZAGS $124,04 / 7,1M; Buy ZAGS 7,1M $112,6 dan Buy SI 11,4M $192,8.
   - 0x82c6…: BNB 0,3; ZAGS $0,198; Buy ZAGS 9,11K $0,081 dan Buy SI (beberapa, $0,02–$197,8).
   - 0x3154…: BNB 0,382; ZAGS $39,11 / 1,9M; Buy ZAGS 11,9M $255,3 dan Buy SI 10,3M $212,8.
   - 0xca4e…: BNB 0,292; ZAGS $10,39; Buy ZAGS 11,9M $193 dan Buy SI 5,1M $193,9.
   - 0xe9ed…: BNB 0,22; ZAGS $164,57 / 5M; Buy ZAGS 4,8M $152,5 dan Buy SI 9,3M $192,8.
   - 0x3a39…: BNB 0,359; ZAGS $8,57; Buy ZAGS (864,6K–12,1M, $19,76–$210,3); SI hanya dijual.
   - 0xcb08…: BNB 0,219; 特斯拉 $3,34, ZAGS $2,20; Buy ZAGS 5,2M $193,1 dan Buy SI 8,8M $255,5.
   - 0xb940…: BNB 0,034; ZAGS $312,58 / 7,9M; Buy ZAGS 7,9M $222,1 dan Buy SI 6M $249,1.
   - 0x4522…: BNB 0,343; ZAGS $0,126; Buy ZAGS 7,8M $193,1 dan Buy SI 7,3M $323,9.
   - 0x5b4b…: BNB 0,312; ZAGS $31,07; Buy ZAGS 5,1M $193,2 dan Buy SI 9,8M $206,1.
   - 0xc659…: BNB 0,461; ZAGS $16,05; Buy ZAGS 6,3M $278,8, 5M $126,1, 11,1M $172.
   - 0x3623…: BNB 0,029; ZAGS $235,81 / 4,8M; Buy ZAGS 4,8M $193,5 dan Buy SI 5,3M $192,6.
   - 0xf968…: BNB 0,632; holdings $0 Sell All; Buy ZAGS (30,85K–10M, $1,033–$202,5).
   - 0x2cc8…: BNB 0,417; holdings $0 Sell All; Buy ZAGS 9,5M $193,1 dan Buy SI 6,2M $208,7.
   - 0x97bd…: BNB 0,303; holdings $0 Sell All pada konfirmasi akhir (posisi ZAGS terjual
     selama pembacaan); Buy ZAGS 2,7M $104 dan 3,4M $112,2; SI hanya dijual.
   - 0x1cce…: BNB 0,355; holdings $0 Sell All; Buy ZAGS 9,5M $213 dan Buy SI 5,6M $206,8.
   - 0xc0c8…: BNB 0,3; holdings $0 Sell All; Buy ZAGS 6M $216,5 dan Buy SI 755,1K $28,39.
   - 0xc194…: BNB 0,311; ZAGS $0,04; Buy ZAGS 2,36K $0,021, 14,3M $193,2, 9,11K $0,081.
   - 0xa952…: BNB 0,3; Monkey $2,82, DAWG $0,052, SUPERMAMA $0,004; Buy ZAGS 259,1K $10,66
     dan 6,3M $203,6, Buy SI 190,9K $6,725 dan 3,5M $115.
   - 0x92bc…: BNB 0,197; ZAGS $23,41; Buy ZAGS 5,1M $193, 5,9M $212,1, 7,5M $193,1 dan
     Buy SI 4,1M $192,8, 5M $193,2.
   - 0x9b51…: BNB 0,333; holdings $0 Sell All pada konfirmasi akhir (posisi ZAGS terjual
     selama pembacaan); Buy ZAGS 14,7M $198 dan pecahan kecil.
   - 0xfdec…: BNB 0,308; holdings $0 Sell All pada konfirmasi akhir (posisi ZAGS terjual
     selama pembacaan); Buy ZAGS 11,5M $193 dan Buy SI 3,9M $192,8.
   - 0x64e8…: BNB 0,151; ZAGS $174,16 / 4,2M; Buy ZAGS 204,2K $7,03, 4M $125,8, 5,9M $114,1,
     6,7M $122.

Hitungan sinyal run 10 (entitas, bukan alamat mentah; ambang baru 13):
- POLA YANG TERAMATI (bukan sinyal — alasan di bawah): berdasarkan SIMBOL saja, ZAGS dibeli
  oleh 31 wallet Tier C dan SI dibeli oleh 20 wallet Tier C dalam jendela sore ini, banyak
  dengan ukuran buy ~$193 (SI dan ZAGS). Wallet 0x7488… tidak membeli keduanya di 10 teratas;
  wallet 0x3803… hanya menjual ZAGS; wallet 0xdb2d…/0xc621… hanya membeli SI.
- MENGAPA INI BUKAN SINYAL TERVERIFIKASI (tiga alasan, masing-masing cukup untuk menahan klaim):
  (1) CA TIDAK TERVERIFIKASI: laporan tidak menampilkan CA untuk token mana pun, dan aturan
      sinyal mensyaratkan CA yang sama. Simbol berulang sebagai baris holdings terpisah
      membuktikan simbol saja tidak mengidentifikasi satu kontrak.
  (2) TOKEN BARU TIDAK TERVERIFIKASI BAGI WALLET TIER C: run ini adalah pembacaan GMGN
      pertama mereka — tidak ada baseline GMGN sebelumnya untuk membandingkan "baru vs lama".
      Scan ekspansi 17:08 WIB hanya mencatat jumlah pool (>=2) tanpa nama token/CA, sehingga
      tidak dapat membuktikan ZAGS/SI belum pernah dipegang/diperdagangkan wallet itu
      sebelumnya. Aktivitas mereka sendiri menunjukkan perdagangan bolak-balik (Buy/Sell
      berselingan, puluhan baris Sell All) yang konsisten dengan token yang SUDAH diperdagangkan,
      bukan entri pertama yang terverifikasi.
  (3) TIDAK ADA KETERKAITAN KUAT BARU YANG TERVERIFIKASI: laporan GMGN ini tidak memuat data
      pendanaan; scan ekspansi mencatat cabal 0 terdeteksi dengan funder None yang dinyatakan
      tidak konklusif (bukan bukti tidak ada). Jadi tidak ada runtuhan entitas, dan tidak ada
      klaim cabal dari run ini.
- Untuk 14 wallet asli: TIDAK ADA pembelian token baru yang terverifikasi dalam jendela
  (satu-satunya trade dalam jendela adalah re-buy 币安人生 oleh wallet 1; Tx In/Add wallet 14
  bukan Buy).
- KESIMPULAN: TIDAK ADA SINYAL pada run 10 (ambang: minimal 13 entitas berbeda membeli token
  baru yang SAMA dengan CA terverifikasi). Pola simbol ZAGS/SI di atas dicatat sebagai
  OBSERVASI WAJIB TINDAK LANJUT, bukan sinyal: pada run 11, ZAGS dan SI kini TERCATAT sebagai
  token yang diketahui bagi wallet-wallet Tier C tersebut (baseline run 10), sehingga buy
  ZAGS/SI berikutnya adalah re-trade, bukan token baru — KECUALI bila CA yang berbeda dari
  baseline terverifikasi. Bila pada run berikutnya muncul token yang benar-benar baru
  (CA terverifikasi, belum ada di state) yang dibeli >=13 entitas, barulah itu sinyal.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-01T18:38:00+07:00 waktu ukur runtime; 14 wallet asli + baseline GMGN pertama untuk
  35 wallet Tier C; wallet 0x81c3… dicatat belum terbaca di run 10). Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 11 — Minggu 2026-11-01, 19:22–~19:23 WIB (gap: laporan browser belum diterima saat penulisan)

- Daftar dibaca dari `tier-ab-watch.md` setiap run: 50 entitas terpantau (Tier A privat 13 +
  Tier B privat 1 + Tier C ekspansi 35 + promosi individual 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36).
  Daftar lama 23 alamat TIDAK dipakai (6 wallet exchange + 3 kontrak sudah dipindah ke Tier E).
  Ambang sinyal: minimal 13 entitas berbeda membeli token baru yang SAMA dengan CA terverifikasi
  (floor(0,25×50)+1 = 13, lantai 4). Jendela run ini: setelah last_checked run 10, 2026-11-01T18:38:00+07:00.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-50 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>)
  DIDISPATCH (task browser-task:1949b6ff-70fb-5c06-95ac-22c9174a5e15) pada ~19:22 WIB, dengan
  instruksi eksplisit: bila login-gated, catat saja dan lanjut, JANGAN klik login. Perhatian
  khusus: wallet 0x81c3… yang TIDAK terbaca di run 10 wajib dibaca di run ini, dan token
  ZAGS/SI kini adalah token yang diketahui bagi wallet-wallet Tier C (baseline run 10), sehingga
  buy ZAGS/SI berikutnya adalah re-trade, bukan token baru, kecuali CA berbeda terverifikasi.
- GAP YANG DICATAT JUJUR, mengikuti preseden Run 1, Run 3, Run 4, Run 5, Run 6, Run 7, dan Run 10:
  - Laporan per-wallet terperinci (holdings + trade terbaru per wallet) dari browser BELUM
    terkirim ke konteks run ini pada saat penulisan log.
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim (ambang: minimal 13 entitas berbeda membeli token baru yang
    sama dengan CA terverifikasi) — bukan karena wallet terbukti tidak membeli, melainkan karena
    bukti per-wallet belum diterima. Wallet yang tidak terbaca datanya TIDAK dianggap tidak membeli,
    sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline / state run 10 TIDAK diubah: last_checked tetap 2026-11-01T18:38:00+07:00 dan holdings
    per wallet tetap dari run 10, sampai laporan browser run ini benar-benar diterima. Hanya field
    `last_attempt` di state yang diperbarui sebagai penanda run ini.
- Bukti parsial read-only yang DIDAPAT pada run ini (saldo BNB on-chain via batch RPC, blok
  131048380, ~19:23 WIB) — saldo saja, BUKAN bukti beli/jual dan BUKAN pengganti laporan GMGN.
  Hanya 15 wallet asli + promosi individual yang dibaca batch ini; Tier C tidak dibaca batch run ini:
  - 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6: 0,07515 BNB (run 10: 0,07327) — NAIK ~0,0019 BNB;
    penyebabnya (Tx In/trade/gas) belum terverifikasi, TIDAK diklaim sebagai pembelian;
    wajib dicocokkan dengan laporan browser.
  - 0x2325f175975abdbcde555c79cc8e63381d28551b: 0,48515 BNB (run 10: 0,61525) — TURUN ~0,130 BNB,
    perubahan MATERIAL; penyebabnya (jual/transfer/gas) belum terverifikasi, TIDAK diklaim sebagai
    pembelian dan TIDAK diklaim sebagai penjualan tertentu; wajib dicocokkan dengan laporan browser.
  - 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc: 0,02479 BNB (run 10 batch: 0,02479) —
    TIDAK BERUBAH sejak batch run 3–10; diskrepansi GMGN-vs-on-chain (GMGN menunjukkan 0 di
    run-run sebelumnya) MASIH belum terjelaskan, penyebabnya belum terverifikasi, dan TIDAK
    diklaim sebagai pembelian. Wajib dicek aktivitasnya (Tx In vs Buy) dari laporan browser
    run ini / run berikutnya.
  - 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36 (belum terbaca di run 10, snapshot saldo pertama
    pada run ini, BUKAN pembanding baseline): 0,01298 BNB.
  - Wallet asli lain praktis sama dengan run 10: 0x13d1… ~0,00001; 0x5b2f… ~0,00002;
    0x6ba7… 0,00148; 0x7564… ~0,00004; 0x8272… ~0,00002; 0x8922… ~0,00006; 0x93e7… ~0,00001;
    0xaab8… 0; 0xbe59… 0; 0xb787… 0,00685; 0xda91… 0,05.
- Tindak lanjut: bila laporan browser run ini tiba belakangan, tambahkan sebagai adendum run ini
  dengan stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs baseline
  run 10 (untuk 14 wallet asli + baseline pertama wallet 0x81c3… + baseline run 10 untuk Tier C).
  Bila tidak tiba, run berikutnya harus mengulang pembacaan ke-50 wallet dan mencatat holdings
  + aktivitas terbaru per wallet secara eksplisit, dengan perhatian khusus pada wallet
  0x2325… (penurunan saldo ~0,130 BNB di atas), 0x8e96… (kenaikan saldo), dan 0xf6a8…
  (diskrepansi saldo) sebelum menghitung sinyal apa pun.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah. SENYAP ke chat.

## Adendum Run 11 — laporan browser diterima setelah log gap ditulis

Pemeriksaan browser terukur runtime 19:23–19:58 WIB (klaim di dalam laporan 19:23–19:57 WIB —
selisih 1 menit pada akhir, dipakai waktu ukur runtime). Semua 50 halaman memuat data publik
TANPA login-gated, status Disconnected, tanpa klik Log in/Sign up/Connect, tanpa sign/transaksi.
Koreksi atas bagian "GAP" di atas: bukti per-wallet AKHIRNYA diterima, sehingga hitungan sinyal
run 11 dapat ditetapkan dari laporan ini dan state diperbarui dari laporan ini (last_checked
2026-11-01T19:58:00+07:00 waktu ukur runtime). Batasan laporan yang wajib dicatat:
- Tab Holdings memakai filter default "Hide Didn't Buy": "No assets held." = sesuai tampilan
  tab itu, BUKAN klaim saldo on-chain nol; token yang hanya diterima lewat Tx In tersaring
  dari Holdings. Untuk wallet 2–3 tab Holdings tidak diklik terpisah, jadi tidak diklaim sebagai
  konfirmasi klik tab; untuk wallet 17, 20, 22 pernyataan holdings dibatasi pada 50 baris tampil.
- Contract address TIDAK tercatat untuk token mana pun: tidak ada alamat kontrak lengkap yang
  terlihat dalam teks halaman; CA tidak ditebak dari simbol. Ini MENENTUKAN kesimpulan run ini
  (lihat hitungan sinyal): kecocokan berdasarkan simbol saja TIDAK dapat dipakai sebagai
  CA-terverifikasi, mengikuti preseden run 10 (simbol berulang sebagai baris holdings terpisah).
- Waktu aktivitas bersifat relatif terhadap waktu baca ("menit/jam lalu") seperti dilaporkan
  GMGN, bukan stempel waktu absolut yang diverifikasi on-chain; label relatif dicocokkan
  dengan jumlah/nilai transaksi sebelum dinyatakan baru, mengikuti preseden run 3–10. Satu
  kasus batas yang ditangani eksplisit: Buy CAPTCHA wallet 22 berlabel 1h ago pada baca
  ~19:35 WIB (~18:35 WIB) dinyatakan SEBELUM batas 18:38 WIB, tidak dihitung.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
- Hanya ~10 aktivitas teratas per wallet yang dilaporkan browser; hitungan di bawah adalah
  hitungan dari 10 teratas itu, bukan klaim atas seluruh riwayat wallet.

Per-wallet (ringkas; urutan sesuai tier-ab-watch.md; detail penuh ada di laporan browser run ini):
1. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — dibaca ~19:23 WIB. BNB GMGN 0,075 ($53,58),
   cocok dengan batch on-chain 19:23 WIB (0,07515). Holdings bukan nol: 爪子 $0,705; MAX $2,44;
   视界之眼 $7,89; 朗月 $2,34; 贵人鸟 $3,12; 奶蛙党 $2,54 (sisanya $0 Sell All). Aktivitas terbaru:
   Tx In 567Ucom $0,015 (1h lalu, Tx In BUKAN Buy, tidak dihitung); Sell 币安人生 141,6K $1,395
   (1h lalu); Buy 币安人生 141,6K $1,379 (2h lalu) adalah trade run 10 yang SAMA (jumlah/nilai
   identik), sebelum jendela, dan 币安人生 pun token yang sudah dikenal sejak run 1/2.
   TIDAK ADA buy baru dalam jendela.
2.–6., 8.–13. (0x13d1…, 0x5b2f…, 0x6ba7…, 0x7564…, 0x8272…, 0x93e7…, 0xaab8…, 0xb787…,
   0xbe59…, 0xda91…, 0xf6a8…): TIDAK ADA buy baru. Aktivitas terbaru hanya Tx In/Tx Out lama
   (termasuk SKYAI dan mubarak sebagai holding/transfer lama, bukan buy baru). Holdings:
   "No assets held." (wallet 2–3: tidak ada baris tampil, tab tidak diklik terpisah).
   Khusus wallet 13 (0xf6a8…): GMGN pada ~19:29 WIB MASIH menunjukkan BNB 0 ($0) dan aktivitas
   terbaru 11 hari lalu (Tx In NEX) — TIDAK menjelaskan saldo on-chain 0,02479 BNB yang tercatat
   di batch 19:23 WIB (tidak berubah sejak run 3). Diskrepansi GMGN-vs-on-chain ini MASIH belum
   terjelaskan, penyebabnya belum terverifikasi, dan TIDAK diklaim sebagai pembelian.
7. 0x892200223bdfb11d2506c5ab1cae9222ce253acc — BNB 0 ($0,042). Holdings tampil: XPIN
   $268,5K; SKYAI $183,3K; CREPE $127,2K; PENGU $51,7K; XRP $37,5K; SLX $10,5K; BANK $4,79K;
   WKC $1,02K; elizaOS $933,63; TAG $169,23. Buy terbaru 16 hari lalu (XPIN) — baseline,
   bukan buy baru. TIDAK ADA buy baru.
14. 0x2325f175975abdbcde555c79cc8e63381d28551b — dibaca ~19:30 WIB. BNB GMGN 0,606 ($431,82),
   BERBEDA dengan batch on-chain 19:23 WIB (0,48515): selisih ~0,121 BNB dalam ~7 menit, waktu
   baca berbeda, penyebabnya belum terverifikasi, TIDAK diklaim sebagai pembelian/penjualan
   tertentu; wajib dicek ulang pada run berikutnya. (Penurunan batch vs run 10, 0,61525 →
   0,48515, yang dicatat di entri gap, tetap tidak terjelaskan sebagai trade tertentu.)
   Holdings bukan nol: BNBH $23,25 / 537,1M; PTG $100,14 / 34,29; BNCB $0,612 Sell All.
   Buy DALAM jendela: Buy BNBH 1,6B $69,25 (26m lalu, ~19:04 WIB) dan Buy BNBH 529,5M $20,81
   (22m lalu, ~19:08 WIB), lalu Sell BNBH 1,6B $88,8 (3m lalu). BNBH adalah token BARU bagi
   wallet ini menurut simbol (tidak ada di baseline run 10: PTG/BNCB/BNC4), TETAPI CA-nya
   TIDAK terverifikasi, dan hanya 1 entitas — tidak dihitung sebagai sinyal.
15., 17., 18., 20. (0x9856…, 0xa0c1…, 0x40a8…, 0xad94…): Buy-buy berlabel 2h lalu adalah trade
   run 10 yang SAMA (jumlah/nilai identik: ZAGS/鼻涕, NITRO/FORX, BLACKED/ZAGS), sebelum jendela.
   TIDAK ADA buy baru dalam jendela.
16. 0x3628764a6576b8dfb31fba0aac6a333b64851423 — dibaca ~19:30–19:31 WIB. BNB 0,011 ($7,89).
   Holdings bukan nol hanya 超级智 $0,128 / 1.130,95. Buy DALAM jendela (semua setelah 18:38 WIB):
   超级智 1,13K $0,071 (4m lalu); SA 1,13K $0,071 (16m dan 39m lalu); BNBFT 1,13K $0,071
   (27m lalu); SA 1,13K $0,071 (50m lalu, ~18:40 WIB, masih setelah batas). Menurut simbol,
   ketiganya baru bagi wallet ini (baseline run 10: ZAGS/鼻涕 saja), TETAPI CA tidak terverifikasi.
19. 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74 — dibaca ~19:33–19:34 WIB. BNB 0,012 ($8,21).
   Buy DALAM jendela: P2P 1,13K $0,024 (2m lalu); SA 1,13K $0,024 (5m lalu); MARS 1,13K $0,024
   (12m–17m lalu, 6 kali). Menurut simbol, P2P/SA/MARS baru bagi wallet ini (baseline run 10:
   MARVIN/Coomer/ZAGS/Chub/MUSK), TETAPI CA tidak terverifikasi.
21. 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a — dibaca ~19:34–19:35 WIB. BNB 0,036 ($25,56).
   Buy DALAM jendela: P2P 1,44K $0,031 (3m lalu); SA 1,44K $0,031 (6m lalu); MARS 1,44K $0,031
   (13m–18m lalu, 6 kali). Menurut simbol, P2P/SA/MARS baru bagi wallet ini (baseline run 10:
   Anakin/Marvin/byenance/白いヤ; ZAGS hanya dijual), TETAPI CA tidak terverifikasi.
   Pola P2P/SA/MARS wallet 19 dan 21 yang hampir identik (ukuran dan urutan) dicatat sebagai
   observasi pola saja, BUKAN sebagai keterkaitan KUAT — laporan ini tidak memuat data pendanaan,
   dan co-buy saja TIDAK meruntuhkan entitas.
22. 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650 — dibaca ~19:35 WIB. BNB 0,024 ($17,10).
   Buy DALAM jendela: PIKACHU 110 $0,056 (13m lalu); p202 1,1K $0,061 (29m lalu); POKEMON 11
   $0,057 (46m lalu); RIVVER 110K $0,063 (49m lalu). Menurut simbol, keempatnya baru bagi wallet
   ini (baseline run 10: SOS/6O6/DRIVE/BULL/x425; tidak ada ZAGS/SI di 10 teratas saat itu),
   TETAPI CA tidak terverifikasi dan masing-masing hanya 1 entitas. Buy CAPTCHA 1h lalu
   (~18:35 WIB) dinyatakan sebelum batas, tidak dihitung (lihat batasan di atas).
23.–49. Tier C lainnya (kecuali 15, 17, 18, 20 di atas): aktivitas dalam jendela didominasi
   re-trade ZAGS dan, untuk sebagian wallet, FAGENT — ringkas per wallet (Buy dalam jendela
   dari 10 teratas; semua CA tidak terverifikasi):
   - ZAGS RE-TRADE (bukan token baru — ZAGS sudah tercatat di baseline run 10 bagi wallet-wallet
     ini, sehingga buy ZAGS berikutnya adalah re-trade, sesuai adendum run 10): 0xdb2d… (Buy
     3,1M $126,7 dan 8,9M $192,7); 0xc621… (314,2K $17,25; 11,3M $350,8; 8,7M $206,8; 13,8M $238,2);
     0xf795… (4,8M $192,2); 0x9cdd… (7,8M $192,5); 0xaa49… (9,3M $192,5); 0x82c6… (14M $192,6;
     9,11K $0,081); 0x3154… (13,9M $198,1; 10,8M $192,5); 0xca4e… (5,4M $192,3); 0xe9ed…
     (384,5K $15,05; 800,1K $27,87; 86,62K $1,562; 10,5M $194); 0x3a39… (7,7M $216,9; 10,2M $192,5);
     0xcb08… (11,1M $232,4; 10,1M $215,6; 16M $192,4); 0xb940… (11,1M $228,3; 8,7M $111; pecahan
     $0,152–$0,171); 0x4522… (5,1M $192,1); 0x5b4b… (16,7M $192,4; 9,11K $0,081; 5,4M $194,5);
     0xc659… (11,1M $192,4); 0x3623… (5,1M $182,7; 394K $11,16; 5,6M $192,7; 4,1M $135,7; 10M $215,9);
     0xf968… (3,9M $123,3; 11,5M $165,5; 271,4K $9,227; 5,7M $170,3); 0x2cc8… (9,8M $192,4; 6M $214,8;
     7,9M $192,4); 0x97bd… (350K $18,45; 11,5M $372,2; 9,2M $207,2; 14,4M $237,9; 7M $307,1);
     0x1cce… (5,3M $192,6; 9,11K $0,081; 2,5M $93,75; 3,5M $111,5); 0xc0c8… (4,6M $192,4; 56,39K $2,672;
     7,5M $242,4; 19,5M $192,4); 0xc194… (11,7M $192,3; 6,1M $216,9); 0xa952… (255,8K $9,218; 7,7M $192,6;
     7,6M $237,8); 0x92bc… (7,9M $222; 10,9M $192,4; 4,6M $192,1); 0x9b51… (429,6K $16,8; 1,1M $30,4;
     89,19K $1,563; 12M $192,5); 0xfdec… (2,5M $94,13; 3,5M $111,8; 5,3M $192,3; 9,11K $0,081);
     0x64e8… (6M $215; 7,5M $192,4; 3,6M $192,1). Buy ZAGS dalam jendela teramati pada 27 wallet
     Tier C di 10 teratas, TETAPI semuanya re-trade token yang sudah dikenal — TIDAK dihitung.
   - FAGENT — OBSERVASI WAJIB TINDAK LANJUT, BUKAN SINYAL: menurut simbol, FAGENT baru bagi
     wallet-wallet ini (tidak ada di baseline run 10 mereka, yang hanya mencatat ZAGS/SI dan
     beberapa token lain), dan Buy FAGENT dalam jendela teramati pada 11 wallet di 10 teratas:
     0xdb2d… (4,1M $134,8; 10,2M $214,8); 0xc621… (7,8M $341,4); 0xf795… (5,9M $213,9; 429,6K $12,38;
     6,5M $207,4); 0x9cdd… (8,5M $394,7; 6,9M $213,9); 0xaa49… (229,2K $12,79; 10,1M $318,1; 6,8M $160,9;
     10,7M $181,6); 0x3154… (3,6M $192,5); 0xca4e… (6,1M $218,3; 7,9M $192,6); 0x3a39… (27,5K $1,071;
     6,4M $234); 0x4522… (294K $11,72; 6,5M $205,2); 0xc659… (6,2M $219,5); 0x2cc8… (53,69K $2,55;
     7,3M $242,1). Hitungan ini adalah BATAS BAWAH dari 10 teratas saja — wallet lain yang
     menampilkan baris FAGENT $0 Sell All di holdings (mis. 0x82c6…, 0xe9ed…, 0xcb08…, 0xb940…,
     0x5b4b…, 0x3623…, 0xf968…, 0x97bd…, 0x1cce…, 0xc0c8…, 0xc194…, 0xa952…, 0x92bc…, 0x9b51…,
     0xfdec…, 0x64e8…) mungkin juga membeli FAGENT dalam jendela di luar 10 teratas, tetapi itu
     tidak terverifikasi dari laporan ini dan tidak diklaim. Alasan FAGENT BUKAN sinyal ada dua,
     masing-masing cukup: (1) CA tidak terverifikasi untuk token mana pun, padahal aturan sinyal
     mensyaratkan CA yang sama; (2) bahkan menurut simbol saja, 11 entitas < ambang 13.
     Mulai run ini, FAGENT TERCATAT sebagai token yang diketahui bagi 11 wallet di atas (dan
     bagi wallet lain yang menampilkan baris FAGENT di holdings), sehingga buy FAGENT berikutnya
     adalah re-trade, bukan token baru — KECUALI bila CA yang berbeda dari baseline terverifikasi.
   - TART: Buy TART 9,6M $192,9 (40m lalu) oleh 0x4522… — menurut simbol baru bagi wallet itu,
     hanya 1 entitas, CA tidak terverifikasi, tidak dihitung sebagai sinyal.
   - SI: TIDAK ADA Buy SI dalam 10 teratas pada run ini (SI hanya muncul sebagai baris $0
     Sell All / dijual) — rotasi dari SI di run 10 ke FAGENT di run 11 dicatat sebagai observasi
     pola saja, bukan klaim hubungan antar token.
50. 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36 — BASELINE GMGN PERTAMA pada run ini (tidak
   terbaca di run 10, kini terbaca ~19:56–19:57 WIB). BNB GMGN 0,013 ($9,15) setelah halaman
   selesai memuat, cocok dengan batch on-chain 19:23 WIB (0,01298). Panel 7D: Realized PnL
   +$2,4K (+19,11%), Win Rate 46,67%, Total PnL +$6,04K (+42,42%), Unrealized $3,64K, 7D TXs 30/25.
   Holdings bukan nol: 社群人生 $1,12K / 285,8K; 分红BNCB股票 $1,47K / 9,7M; ALOY $2,69K / 1M;
   SENSEI $0 Sell All; sisanya $0 Sell All. Aktivitas terbaru BUKAN Buy: Sell SENSEI 9,9B $387,4
   dan $565,2 (16m dan 22m lalu) dengan Burn SENSEI 99,4M masing-masing; Buy terbaru SENSEI
   2,7B $97,73 berlabel 2h lalu (~17:57 WIB), SEBELUM jendela. Jadi: TIDAK ADA buy baru dalam
   jendela untuk wallet ini, dan baseline GMGN-nya kini ditetapkan (SENSEI, 社群人生, 分红BNCB股票,
   ALOY, dan token-token $0 Sell All di atas adalah token yang diketahui bagi wallet ini).

Hitungan sinyal run 11 (entitas, bukan alamat mentah; ambang 13 dengan CA terverifikasi):
- Token dengan CA terverifikasi yang dibeli >=13 entitas dalam jendela: TIDAK ADA — CA tidak
  ditampilkan untuk token mana pun, sehingga TIDAK ADA token yang dapat lolos sebagai CA sama
  antar wallet, apa pun hitungan simbolnya.
- Hitungan simbol HANYA sebagai observasi (bukan sinyal): FAGENT 11 entitas (daftar di atas);
  SA 3 entitas (0x3628…, 0xc7c5…, 0x3803…); P2P 2 entitas (0xc7c5…, 0x3803…); MARS 2 entitas
  (0xc7c5…, 0x3803…); BNBH 1 entitas (0x2325…); TART 1 entitas (0x4522…); PIKACHU/p202/POKEMON/
  RIVVER masing-masing 1 entitas (0x7488…); 超级智/BNBFT masing-masing 1 entitas (0x3628…).
  ZAGS 27 wallet di 10 teratas TIDAK dihitung karena re-trade token yang sudah dikenal (baseline
  run 10). Tidak ada hitungan simbol yang mencapai 13 untuk token yang benar-benar baru.
- KESIMPULAN: TIDAK ADA SINYAL pada run 11 (ambang: minimal 13 entitas berbeda membeli token
  baru yang SAMA dengan CA terverifikasi). Pola FAGENT di atas dicatat sebagai OBSERVASI WAJIB
  TINDAK LANJUT untuk run 12 (kini token yang diketahui, lihat di atas), bukan sinyal, bukan
  rekomendasi beli, bukan promosi, bukan bukti insider, bukan pemicu trade.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau (laporan ini
  tidak memuat data pendanaan; co-buy/co-hold saja, termasuk pola P2P/SA/MARS yang hampir
  identik pada wallet 19/21 dan rotasi ZAGS→FAGENT pada banyak wallet Tier C, TIDAK meruntuhkan
  entitas), jadi tidak ada runtuhan entitas. Ambang absolut tetap 13.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-01T19:58:00+07:00 waktu ukur runtime; baseline GMGN pertama wallet 0x81c3…;
  BNBH/FAGENT/SA/P2P/MARS/PIKACHU/p202/POKEMON/RIVVER/TART/超级智/BNBFT dicatat sebagai token
  yang diketahui bagi wallet-wallet bersangkutan; ZAGS/SI tetap token yang diketahui Tier C).
  Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah. SENYAP ke chat.

## Run 12 — Minggu 2026-11-01, 21:22–~21:24 WIB (gap: laporan browser belum diterima saat penulisan)

- Daftar dibaca dari `tier-ab-watch.md` setiap run: 50 entitas privat (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi 0x81c3… 1). Daftar lama 23 alamat TIDAK dipakai (6 wallet exchange + 3 kontrak sudah dipindah ke Tier E). Ambang sinyal: minimal 13 entitas berbeda membeli token baru yang SAMA dengan CA terverifikasi.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-50 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>)
  DIDISPATCH (task browser-task:90e08a63-8c99-5d56-a19b-0fef21aee05e) pada ~21:23 WIB, dengan
  instruksi eksplisit: bila login-gated, catat saja dan lanjut, JANGAN klik login.
- GAP YANG DICATAT JUJUR, mengikuti preseden Run 1, 3, 4, 5, 6, 7:
  - Laporan per-wallet terperinci (holdings + trade terbaru per wallet) dari browser BELUM
    terkirim ke konteks run ini pada saat penulisan log.
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim (ambang: minimal 13 entitas privat berbeda membeli token baru
    yang sama dengan CA terverifikasi) — bukan karena wallet terbukti tidak membeli, melainkan
    karena bukti per-wallet belum diterima. Wallet yang tidak terbaca datanya TIDAK dianggap
    tidak membeli, sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline / state run 11 TIDAK diubah: last_checked tetap 2026-11-01T19:58:00+07:00 dan holdings
    per wallet tetap dari run 11, sampai laporan browser run ini benar-benar diterima. Hanya field
    `last_attempt` di state yang diperbarui sebagai penanda run ini.
- Bukti parsial read-only yang DIDAPAT pada run ini (saldo BNB on-chain via batch RPC, blok
  0x7cfe24e, ~21:24 WIB) — saldo saja, BUKAN bukti beli/jual dan BUKAN pengganti laporan GMGN:
  - 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6: 0,07226 BNB (run 11 GMGN 0,075; batch run 6 0,07222) — praktis sama dengan batch terakhir, bukan perubahan material.
  - 0x2325f175975abdbcde555c79cc8e63381d28551b: 0,67816 BNB (run 11: GMGN 0,606 ~19:30, batch on-chain 0,48515 ~19:23) — NAIK ~0,053 BNB vs batch run 11 dan ~0,072 vs GMGN run 11; penyebabnya (trade/sell/Tx In/transfer) belum terverifikasi, TIDAK diklaim sebagai pembelian; wajib dicocokkan dengan laporan browser run ini. Diskrepansi GMGN-vs-on-chain run 11 (0,606 vs 0,48515) tetap belum terjelaskan dan kini bergeser lagi.
  - 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc: 0,02479 BNB — TIDAK BERUBAH sejak batch run 3/4/5/6; diskrepansi GMGN-vs-on-chain (GMGN menunjukkan 0) MASIH belum terjelaskan, penyebabnya belum terverifikasi, dan TIDAK diklaim sebagai pembelian.
  - 0xda91cefe240175e6fab56271110427a4195ab71f: 0,05000 BNB — sama.
  - 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462: 0,00685 BNB — sama.
  - Wallet lain praktis sama dengan run sebelumnya (debu): 0x13d1… 0,0000119; 0x5b2f… 0,0000192; 0x6ba7… 0,00148; 0x7564… 0,0000429; 0x8272… 0,0000158; 0x8922… 0,0000583; 0x93e7… 0,0000143; 0xaab8… 0; 0xbe59… 0.
- Tindak lanjut: bila laporan browser run ini tiba belakangan, tambahkan sebagai adendum run ini
  dengan stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs baseline
  run 11 — dengan perhatian khusus pada wallet 0x2325… (kenaikan saldo di atas) dan observasi
  wajib tindak lanjut FAGENT run 11 (FAGENT kini token yang diketahui bagi wallet-wallet run 11,
  sehingga buy FAGENT berikutnya adalah re-trade kecuali CA berbeda terverifikasi). Bila tidak
  tiba, run berikutnya harus mengulang pembacaan ke-50 wallet dan mencatat holdings + aktivitas
  terbaru per wallet secara eksplisit sebelum menghitung sinyal apa pun.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah. SENYAP ke chat.

## Adendum Run 12 — laporan browser diterima, pemeriksaan terukur 21:23–22:15 WIB

Pemeriksaan browser terukur runtime 21:23–22:15 WIB (52 menit; klaim di dalam laporan
21:23–22:14 WIB, selisih 1 menit di ujung dicatat apa adanya). Semua 50 halaman memuat data
publik TANPA login-gated, status Disconnected, tanpa klik Log in/Sign up/Connect, tanpa
sign/transaksi. Koreksi atas bagian "GAP" di atas: bukti per-wallet AKHIRNYA diterima,
sehingga hitungan sinyal run 12 dapat ditetapkan dari laporan ini dan state diperbarui dari
laporan ini (last_checked 2026-11-01T22:15:00+07:00 waktu ukur runtime). Batasan laporan yang
wajib dicatat:
- Tab Holdings memakai filter default GMGN ("Hide Didn't Buy" dll.): "No assets held." =
  sesuai tampilan tab itu, BUKAN klaim saldo on-chain nol; token yang hanya diterima lewat
  Tx In tersaring dari Holdings.
- Contract address TIDAK tercatat pada run ini untuk token mana pun: tidak ada alamat kontrak
  lengkap yang terlihat dalam teks halaman; CA tidak ditebak dari simbol. Token dicatat
  berdasarkan simbol saja, dan karena itu TIDAK dapat dipakai sebagai CA terverifikasi untuk
  perbandingan antar wallet — ini penentu kesimpulan di bawah, meski satu hitungan simbol
  melewati ambang.
- Waktu aktivitas bersifat relatif terhadap waktu baca masing-masing wallet ("menit/jam lalu")
  seperti dilaporkan GMGN, bukan stempel waktu absolut yang diverifikasi on-chain; label
  relatif dicocokkan dengan jumlah/nilai transaksi sebelum dinyatakan baru, mengikuti preseden
  run 3–11. Wallet dibaca berurutan, jadi jendela run 12 (setelah 19:58 WIB) dinilai per wallet
  dari waktu bacanya sendiri: trade berlabel ~4h lalu pada pembacaan ~21:30–22:00 WIB yang
  jumlah/nilainya identik dengan baseline run 10 adalah trade run 10 yang SAMA, bukan baru.

Per-wallet (ringkas; urutan sesuai tier-ab-watch.md):
1. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — dibaca pertama, BNB GMGN 0,072 ($51,7),
   cocok dengan batch on-chain 21:24 WIB (0,07226). Buy BARU dalam jendela (simbol, CA
   unverified): 火龙果人生 219K $1,385 + 165K $1,382 (~1h lalu, ~20:24 WIB) dan Lulu 160,6K
   $1,394 (~1h lalu); keduanya lalu dijual jumlah yang sama. Buy 币安人生 141,6K $1,379
   berlabel 4h lalu adalah trade run 10 yang SAMA, bukan baru. Jadi: 2 simbol baru, masing-masing
   1 entitas.
2.–6., 8.–13. (0x13d1…, 0x5b2f…, 0x6ba7…, 0x7564…, 0x8272…, 0x93e7…, 0xaab8…, 0xb787…,
   0xbe59…, 0xda91…, 0xf6a8…): TIDAK ADA buy baru. Aktivitas terbaru hanya Tx In/Tx Out lama
   (termasuk SKYAI dan mubarak sebagai holding/transfer lama, bukan buy baru). Holdings:
   "No assets held." untuk semuanya. Khusus wallet 13 (0xf6a8…): GMGN MASIH menunjukkan BNB 0
   ($0) dan aktivitas terbaru 11 hari lalu — TIDAK menjelaskan saldo on-chain 0,02479 BNB
   (batch 21:24 WIB, tidak berubah sejak run 3). Diskrepansi GMGN-vs-on-chain ini MASIH belum
   terjelaskan, penyebabnya belum terverifikasi, dan TIDAK diklaim sebagai pembelian.
7. 0x892200223bdfb11d2506c5ab1cae9222ce253acc — BNB 0 ($0,042). Holdings tampil: XPIN, WKC,
   XRP, SLX, BANK, SKYAI, CREPE, TAG, PENGU, elizaOS. Buy terbaru 16–18 hari lalu (XPIN, XRP)
   — baseline, bukan buy baru. TIDAK ADA buy baru.
14. 0x2325f175975abdbcde555c79cc8e63381d28551b — BNB GMGN 0,578 ($413,65) pada pembacaan
   ini, BERBEDA dari batch on-chain 21:24 WIB (0,67816) maupun GMGN run 11 (0,606 ~19:30):
   diskrepansi GMGN-vs-on-chain run 11 tetap belum terjelaskan dan kini bergeser lagi, sejalan
   dengan aktivitas trading dalam jendela — penurunan/kenaikan saldo itu sendiri TIDAK diklaim
   sebagai pembelian tertentu. Holdings bukan nol: BNBH $76,74 / 3,5B, PTG $105,79 / 34,29,
   BNCB $1,17 / 0,229. Aktivitas dalam jendela: Buy BNBH 3,5B $69,44 (9m lalu) dan 2,4B $41,52
   (1h lalu) adalah RE-TRADE BNBH (dikenal sejak run 11, bukan token baru); Buy BNCB 0,238
   $1,214 (32m lalu) adalah token yang SUDAH tercatat dipegang wallet ini di run 11 (baris
   $0,612 / 0,12 Sell All), jadi BUKAN token baru menurut definisi state ini; Buy CZAI 15,3B
   $41,56 (1h lalu) adalah simbol BARU bagi wallet ini (tidak ada di state run 1–11), 1 entitas,
   CA unverified. Sell 4444 dan Burn-burn bukan Buy.
15. 0x9856bac497634a62a970233bc4b0f5bb52c844c1 — TIDAK ADA buy baru. Aktivitas 10 teratas
   semuanya berlabel 4h lalu dengan jumlah/nilai IDENTIK dengan baseline run 10 (Buy/Sell
   鼻涕 7,93–7,94K $0,498; Buy/Sell ZAGS 22,68–22,69K $0,498) — trade run 10 yang SAMA, bukan baru.
16. 0x3628764a6576b8dfb31fba0aac6a333b64851423 — BNB 0,01 ($7,29). Buy BARU dalam jendela
   (simbol, CA unverified): 雪眉娘 1,13K $0,071 (1m lalu) dan PARITY 1,13K $0,071 (24m lalu).
   Buy SA berulang adalah re-trade SA (dikenal run 11). Jadi: 2 simbol baru, masing-masing
   1 entitas.
17. 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e — TIDAK ADA buy baru. Aktivitas semuanya
   berlabel 4h lalu dengan jumlah/nilai run 10 (ZAGS/鼻涕 1,13K $0,071) — trade run 10 yang SAMA.
18. 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c — TIDAK ADA buy baru. Aktivitas semuanya
   berlabel 4h lalu dengan jumlah/nilai run 10 (NITRO 894,78 $5,002; 鼻涕 188K $5; FORX 8,65K
   $5; ZAGS 187,5K $5,005) — trade run 10 yang SAMA.
19. 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74 — BNB 0,011 ($7,54). Buy BARU dalam jendela
   (simbol, CA unverified): TESTES 1,13K $0,024 (4m lalu), PARITY 1,13K $0,024 (6m lalu),
   GRND 1,13K $0,024 (13m lalu), Dante 1,13K $0,024 (24m lalu). Buy SA adalah re-trade SA
   (dikenal run 11). Jadi: 4 simbol baru, masing-masing 1 entitas.
20. 0xad94ee77d0e868d299fb3e92b9d67560257f656d — TIDAK ADA buy baru. Aktivitas semuanya
   berlabel 4h lalu dengan jumlah/nilai run 10 (BLACKED/ZAGS 1,13K $0,024) — trade run 10
   yang SAMA.
21. 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a — BNB 0,037 ($26,22). Buy BARU dalam jendela
   (simbol, CA unverified): TESTES 1,5K $0,033 (6m lalu), PARITY 1,5K $0,033 (7m lalu),
   GRND 1,5K $0,033 (15m lalu), Dante 1,5K $0,033 (25m lalu). Buy SA adalah re-trade SA.
   Pola TESTES/PARITY/GRND/Dante yang hampir identik dengan wallet 19 (urutan dan ukuran
   relatif sama) adalah co-buy saja, BUKAN keterkaitan KUAT — tidak meruntuhkan entitas.
   Jadi: 4 simbol baru, masing-masing 1 entitas.
22. 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650 — BNB 0,024 ($17,26). Buy BARU dalam jendela
   (simbol, CA unverified): QS 110K $0,06 (7m lalu), HM 11 $0,058 (23m lalu), TERMINAL 11
   $0,061 (41m lalu), BIGDOG 11 $0,059 (57m lalu), MONKEY 11 $0,056 (1h lalu). Token-token
   run 11 wallet ini (PIKACHU/p202/POKEMON/RIVVER) tidak muncul sebagai Buy di 10 teratas
   run ini. Jadi: 5 simbol baru, masing-masing 1 entitas.
23.–34., 36.–49. (Tier C, kecuali 0x4522… di bawah) — TART, OBSERVASI WAJIB TINDAK LANJUT,
   BUKAN SINYAL (lihat hitungan di bawah). Semua wallet ini menampilkan Buy TART dalam
   jendela di 10 teratas (berlabel 7m–1h lalu pada pembacaannya masing-masing, yaitu
   ~21:00–22:10 WIB, setelah batas 19:58 WIB), dengan ukuran khas ~$193 (beberapa buy kecil
   $0,02–$30 dan buy besar $200–$350 di antaranya), lalu Sell berulang. Daftar wallet
   (26 entitas, TART simbol-baru menurut state yang tercatat): 0xdb2d… (Buy 8,2M $193,2;
   6,5M $217,9; 6,2M $193,3), 0xc621… (11,9M $193,3; 7,3M $213,3), 0xf795… (7,2M $296;
   6M $160), 0x9cdd… (4M $193,2; 5,1M $186,3; 5,5M $193,6; 476K $12,44), 0xaa49… (12,1M
   $193,5; 888,6K $30,35; 457,9K $16,41), 0x82c6… (7,7M $214,3; 9M $159,4; 5,9M $193,6),
   0x3154… (11M $191,3; 10M $205,4), 0xca4e… (4,2M $159,3; 4,3M $159,6), 0xe9ed… (6,5M
   $219,2; 6,4M $193,2; 4,1M $193,2; 5,5M $251,4), 0x3a39… (10,2M $211,1; 4,2M $138,8;
   7,6M $111,6), 0xcb08… (5,1M $193,2; 5,4M $193,2; 5,1M $180,8), 0xb940… (2,6M $92,22;
   3,5M $112,1), 0x5b4b… (7,5M $143,5; 5,1M $219,2; 5,1M $162,8; 12,6M $193,5), 0xc659…
   (7,1M $193,5; 4,04K $0,149; 4,55K $0,167–$0,168), 0x3623… (9,5M $294,3; 8,5M $160;
   11,6M $193,5; 3,9M $147,1), 0xf968… (4,1M $144,8; 4,1M $159,4; 4,9M $193,3; 5,1M
   $192,9), 0x2cc8… (7,9M $193,5; 270K $9,254; 461K $16,76), 0x97bd… (3,6M $191,2; 5M
   $184,3), 0x1cce… (8,8M $190,4; 13,6M $159,4; 5,2M $193,5; 9,11K $0,081), 0xc0c8…
   (8,8M $185,2; 6,5M $111,8; 5,4M $193,1 — holdings TART bukan nol $209,89 / 8,8M),
   0xc194… (7M $175,7; 9,4M $191,7; 15,1M $177,8), 0xa952… (6M $193,9; 5,6M $169;
   428,5K $12,46 — holdings TART bukan nol $206,1 / 6,4M), 0x92bc… (7,9M $193,9),
   0x9b51… (7,4M $177,5; 6,2M $193,5), 0xfdec… (4,3M $116,9; 8,2M $169,7; 13,9M $194),
   0x64e8… (4M $145,3; 4,5M $159,4). TART tidak tercatat di state run 1–11 bagi wallet-wallet
   ini (satu-satunya TART run 11 adalah wallet 35 di bawah), sehingga menurut state yang
   tercatat ini adalah simbol baru bagi ke-26 wallet tersebut. Batasan ini dinyatakan
   eksplisit: bila baris TART $0 Sell All pernah ada di run 11 tetapi tidak tercatat di
   state, hitungan simbol ini bisa lebih rendah — tetapi berdasarkan state, hitungannya 26.
35. 0x4522e661d9c94ec54b37e71896351a7440ec4f07 — Buy TART dalam jendela (14,5M $193,4;
   7,6M $143,4) adalah RE-TRADE TART (dikenal sejak run 11), BUKAN token baru, jadi TIDAK
   dihitung dalam 26 entitas TART di atas. Total wallet yang menampilkan Buy TART di 10
   teratas run ini adalah 27, tetapi hanya 26 yang simbol-baru.
50. 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36 — BNB GMGN 0,013 ($9,16), sama seperti
   baseline run 11. Buy SENSEI 9,3B $488,5 (40m lalu, ~21:32 WIB) dalam jendela, tetapi
   SENSEI adalah token yang SUDAH dikenal wallet ini sejak baseline run 11 (dan buy-buy
   SENSEI 5h lalu adalah trade lama) — jadi RE-TRADE, bukan token baru. Tx In BNCB
   +0,869 $4,426 (1h lalu) adalah Tx In, bukan Buy. TIDAK ADA token baru untuk wallet ini.

Hitungan sinyal run 12 (entitas, bukan alamat mentah; ambang 13 dengan CA terverifikasi):
- Token dengan CA terverifikasi yang dibeli >=13 entitas dalam jendela: TIDAK ADA — CA tidak
  ditampilkan untuk token mana pun, sehingga TIDAK ADA token yang dapat lolos sebagai CA sama
  antar wallet, apa pun hitungan simbolnya.
- Hitungan simbol HANYA sebagai observasi (bukan sinyal): TART 26 entitas simbol-baru
  (daftar di atas; 27 wallet menampilkan Buy TART, 1 di antaranya re-trade); PARITY 3 entitas
  (0x3628…, 0xc7c5…, 0x3803…); TESTES 2 entitas (0xc7c5…, 0x3803…); GRND 2 entitas; Dante 2
  entitas; 火龙果人生 1 entitas; Lulu 1 entitas; CZAI 1 entitas; 雪眉娘 1 entitas; QS/HM/
  TERMINAL/BIGDOG/MONKEY masing-masing 1 entitas (0x7488…). ZAGS/鼻涕/SI/FAGENT tidak
  dihitung karena re-trade token yang sudah dikenal (FAGENT dikenal sejak run 11; ZAGS/SI
  sejak run 10).
- KESIMPULAN: TIDAK ADA SINYAL pada run 12 (ambang: minimal 13 entitas berbeda membeli token
  baru yang SAMA dengan CA terverifikasi). TART adalah OBSERVASI WAJIB TINDAK LANJUT untuk
  run 13: hitungan simbolnya (26) melewati ambang 13, tetapi tanpa CA terverifikasi ia TIDAK
  memenuhi definisi sinyal, dan bukan rekomendasi beli, bukan promosi, bukan bukti insider,
  bukan pemicu trade. Mulai run ini, TART TERCATAT sebagai token yang diketahui bagi ke-26
  wallet di atas (dan sudah diketahui bagi 0x4522… sejak run 11), sehingga buy TART berikutnya
  adalah re-trade, bukan token baru — KECUALI bila CA yang berbeda dari baseline terverifikasi.
  Demikian pula 火龙果人生, Lulu, CZAI, 雪眉娘, PARITY, TESTES, GRND, Dante, QS, HM, TERMINAL,
  BIGDOG, MONKEY kini tercatat sebagai token yang diketahui bagi wallet-wallet bersangkutan.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau (laporan ini
  tidak memuat data pendanaan; co-buy/co-hold saja, termasuk pola TART serentak pada 27 wallet
  Tier C dan pola TESTES/PARITY/GRND/Dante yang hampir identik pada wallet 19/21, TIDAK
  meruntuhkan entitas), jadi tidak ada runtuhan entitas. Ambang absolut tetap 13.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-01T22:15:00+07:00 waktu ukur runtime; TART dan simbol-simbol baru di atas dicatat
  sebagai token yang diketahui bagi wallet-wallet bersangkutan; BNB GMGN per wallet diperbarui;
  diskrepansi 0x2325… dan 0xf6a8… dicatat masih belum terjelaskan). Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah. SENYAP ke chat.

## Run 13 — Minggu 2026-11-01, 23:22–~23:24 WIB (gap: laporan browser belum diterima saat penulisan)

- Daftar dibaca dari `tier-ab-watch.md` setiap run: 50 entitas privat (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi 0x81c3… 1). Daftar lama 23 alamat TIDAK dipakai (6 wallet exchange + 3 kontrak sudah dipindah ke Tier E). Ambang sinyal: minimal 13 entitas berbeda membeli token baru yang SAMA dengan CA terverifikasi.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-50 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>)
  DIDISPATCH pada ~23:24 WIB, dengan instruksi eksplisit: bila login-gated, catat saja dan lanjut, JANGAN klik login.
- GAP YANG DICATAT JUJUR, mengikuti preseden Run 1, 3, 4, 5, 6, 7, 12:
  - Laporan per-wallet terperinci (holdings + trade terbaru per wallet) dari browser BELUM
    terkirim ke konteks run ini pada saat penulisan log.
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim (ambang: minimal 13 entitas privat berbeda membeli token baru
    yang sama dengan CA terverifikasi) — bukan karena wallet terbukti tidak membeli, melainkan
    karena bukti per-wallet belum diterima. Wallet yang tidak terbaca datanya TIDAK dianggap
    tidak membeli, sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline / state run 12 TIDAK diubah: last_checked tetap 2026-11-01T22:15:00+07:00 dan holdings
    per wallet tetap dari run 12, sampai laporan browser run ini benar-benar diterima. Hanya field
    `last_attempt` di state yang diperbarui sebagai penanda run ini.
- Bukti parsial read-only yang DIDAPAT pada run ini (saldo BNB on-chain via batch RPC, blok
  0x7d0208f, ~23:24 WIB) — saldo saja, BUKAN bukti beli/jual dan BUKAN pengganti laporan GMGN:
  - 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6: 0,07226 BNB (run 12 batch 21:24: 0,07226) — sama.
  - 0x2325f175975abdbcde555c79cc8e63381d28551b: 0,62128 BNB (run 12: batch 0,67816; GMGN 0,578) — TURUN ~0,057 BNB vs batch run 12; penyebabnya (trade/sell/Tx In/transfer) belum terverifikasi, TIDAK diklaim sebagai pembelian; wajib dicocokkan dengan laporan browser run ini. Diskrepansi GMGN-vs-on-chain run 12 tetap belum terjelaskan.
  - 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc: 0,02479 BNB — TIDAK BERUBAH sejak batch run 3/4/5/6/12; diskrepansi GMGN-vs-on-chain (GMGN menunjukkan 0) MASIH belum terjelaskan, penyebabnya belum terverifikasi, dan TIDAK diklaim sebagai pembelian.
  - 0xda91cefe240175e6fab56271110427a4195ab71f: 0,05000 BNB — sama.
  - 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462: 0,00685 BNB — sama.
  - Wallet lain praktis sama dengan run sebelumnya (debu): 0x13d1… 0,0000119; 0x5b2f… 0,0000192; 0x6ba7… 0,00148; 0x7564… 0,0000429; 0x8272… 0,0000158; 0x8922… 0,0000583; 0x93e7… 0,0000143; 0xaab8… 0; 0xbe59… 0.
- Tindak lanjut: bila laporan browser run ini tiba belakangan, tambahkan sebagai adendum run ini
  dengan stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs baseline
  run 12 — dengan perhatian khusus pada wallet 0x2325… (penurunan saldo di atas) dan observasi
  wajib tindak lanjut TART run 12 (TART kini token yang diketahui bagi 27 wallet, sehingga buy
  TART berikutnya adalah re-trade kecuali CA berbeda terverifikasi). Bila tidak tiba, run
  berikutnya harus mengulang pembacaan ke-50 wallet dan mencatat holdings + aktivitas terbaru
  per wallet secara eksplisit sebelum menghitung sinyal apa pun.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah. SENYAP ke chat.

## Adendum Run 13 — laporan browser diterima, pemeriksaan terukur 23:23–23:59 WIB

Pemeriksaan browser terukur runtime 23:23–23:59 WIB (36 menit; klaim di dalam laporan
23:24–23:58 WIB untuk dompet terakhir, selisih 1 menit di ujung dicatat apa adanya).
Semua 50 halaman memuat data publik TANPA login-gated, status Disconnected, tanpa klik
Log in/Sign up/Connect, tanpa sign/transaksi. Koreksi atas bagian "GAP" di atas: bukti
per-wallet AKHIRNYA diterima, sehingga hitungan sinyal run 13 dapat ditetapkan dari
laporan ini dan state diperbarui dari laporan ini (last_checked
2026-11-01T23:59:00+07:00 waktu ukur runtime). Batasan laporan yang wajib dicatat:
- Tab Holdings memakai filter default GMGN ("Hide Didn't Buy" dll.): "No assets held." =
  sesuai tampilan tab itu, BUKAN klaim saldo on-chain nol; token yang hanya diterima lewat
  Tx In tersaring dari Holdings.
- Contract address TIDAK tercatat pada run ini untuk token mana pun: tidak ada alamat kontrak
  lengkap yang terlihat dalam teks halaman; CA tidak ditebak dari simbol. Token dicatat
  berdasarkan simbol saja, dan karena itu TIDAK dapat dipakai sebagai CA terverifikasi untuk
  perbandingan antar wallet — ini penentu kesimpulan di bawah.
- Waktu aktivitas bersifat relatif terhadap waktu baca masing-masing wallet ("menit/jam lalu")
  seperti dilaporkan GMGN, bukan stempel waktu absolut yang diverifikasi on-chain; label
  relatif dicocokkan dengan jumlah/nilai transaksi sebelum dinyatakan baru, mengikuti preseden
  run 3–12. Jendela run 13 adalah setelah 22:15 WIB (last_checked run 12).

Per-wallet (ringkas; urutan sesuai tier-ab-watch.md):
1. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — BNB GMGN 0,072 ($51,46), cocok dengan batch
   on-chain 23:24 WIB (0,07226). Buy 火龙果人生 219K $1,385 + 165K $1,382 dan Lulu 160,6K
   $1,394 berlabel 3h lalu adalah trade run 12 yang SAMA (jumlah/nilai identik), bukan baru.
   Buy 币安人生 141,6K $1,379 berlabel 6h lalu adalah trade run 10 yang SAMA. TIDAK ADA token baru.
2.–6., 8.–13. (0x13d1…, 0x5b2f…, 0x6ba7…, 0x7564…, 0x8272…, 0x93e7…, 0xaab8…, 0xb787…,
   0xbe59…, 0xda91…, 0xf6a8…): TIDAK ADA buy baru. Aktivitas terbaru hanya Tx In/Tx Out lama
   (termasuk SKYAI dan mubarak sebagai holding/transfer lama, bukan buy baru). Holdings:
   "No assets held." untuk semuanya. Khusus wallet 13 (0xf6a8…): GMGN MASIH menunjukkan BNB 0
   ($0) — TIDAK menjelaskan saldo on-chain 0,02479 BNB (batch 23:24 WIB, tidak berubah sejak
   run 3). Diskrepansi GMGN-vs-on-chain ini MASIH belum terjelaskan, penyebabnya belum
   terverifikasi, dan TIDAK diklaim sebagai pembelian.
7. 0x892200223bdfb11d2506c5ab1cae9222ce253acc — BNB 0 ($0,042). Holdings tampil: XPIN, WKC,
   XRP, SLX, BANK, SKYAI, CREPE, TAG, PENGU, elizaOS. Buy terbaru 16–18 hari lalu (XPIN, XRP)
   — baseline, bukan buy baru. TIDAK ADA buy baru.
14. 0x2325f175975abdbcde555c79cc8e63381d28551b — BNB GMGN 0,656 ($466,59) pada pembacaan
   ini, BERBEDA dari batch on-chain 23:24 WIB (0,62128) maupun GMGN run 12 (0,578):
   diskrepansi GMGN-vs-on-chain tetap belum terjelaskan dan kini bergeser lagi, sejalan dengan
   aktivitas trading dalam jendela — perubahan saldo itu sendiri TIDAK diklaim sebagai
   pembelian tertentu. Holdings bukan nol: POPZERO $8,07 dan BNCB $1,27 / 0,248; BNBH, CZAI,
   4444, dll. $0 / Sell All. Aktivitas dalam jendela: Buy POPZERO 1,09e+29 $20,89 (11m lalu),
   1,08e+29 $20,98 (24m lalu), 3,79e+29 $69,98 (39m lalu) — simbol BARU bagi wallet ini
   (tidak ada di state run 1–12), 1 entitas, CA unverified. Buy BNBH 2,9B $69,4 (1h lalu)
   adalah RE-TRADE BNBH (dikenal sejak run 11). POPZERO kini tercatat sebagai token yang
   diketahui bagi wallet ini.
15. 0x9856bac497634a62a970233bc4b0f5bb52c844c1 — TIDAK ADA buy baru. Aktivitas 10 teratas
   semuanya berlabel 6h lalu dengan jumlah/nilai IDENTIK dengan baseline run 10 (Buy/Sell
   鼻涕 7,93–7,94K $0,498; Buy/Sell ZAGS 22,68–22,69K $0,498) — trade run 10 yang SAMA, bukan baru.
16. 0x3628764a6576b8dfb31fba0aac6a333b64851423 — BNB 0,01 ($7,19). Buy SA 1,13K $0,071
   (6m–34m lalu) adalah re-trade SA (dikenal run 11); Buy PARITY 1,13K $0,071 (23m lalu)
   adalah re-trade PARITY (dikenal run 12). TIDAK ADA token baru.
17. 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e — BNB 0,022 ($15,67). Buy BARU dalam jendela
   (simbol, CA unverified): SA 1,13K $0,071 (7m, 18m, 19m, 20m lalu) dan PARITY 1,13K $0,071
   (25m lalu) — keduanya belum pernah tercatat bagi wallet ini di state run 10–12 (state
   hanya mencatat ZAGS/鼻涕 dan holdings LAPTOP/UNSAFU). Masing-masing 1 entitas. SA/PARITY
   kini tercatat sebagai token yang diketahui bagi wallet ini.
18. 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c — TIDAK ADA buy baru. Aktivitas semuanya
   berlabel 6h lalu dengan jumlah/nilai run 10 (NITRO 894,78 $5,002; 鼻涕 188K $5; FORX 8,65K
   $5; ZAGS 187,5K $5,005) — trade run 10 yang SAMA.
19. 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74 — BNB 0,011 ($7,75). Buy BARU dalam jendela
   (simbol, CA unverified): Anakin 1,13K $0,024 (7m lalu), 盘古人 1,13K $0,024 (9m lalu),
   RAM 1,13K $0,024 (12m dan 14m lalu). Buy SA 1,13K $0,024 (13m lalu) adalah re-trade SA
   (dikenal run 11). Masing-masing simbol baru 1 entitas. Anakin/盘古人/RAM kini tercatat
   sebagai token yang diketahui bagi wallet ini.
20. 0xad94ee77d0e868d299fb3e92b9d67560257f656d — BNB 0,047 ($33,39). Buy BARU dalam jendela
   (simbol, CA unverified): Anakin 1,13K $0,024 (7m lalu) — belum tercatat bagi wallet ini
   di state run 10–12. Baris 10 teratas lainnya adalah Sell (RAM, SA, Wen, SISY), yang
   buy-nya tidak tampil di 10 teratas dan TIDAK dihitung sebagai buy baru. Anakin kini
   tercatat sebagai token yang diketahui bagi wallet ini.
21. 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a — BNB 0,021 ($15,01). Buy BARU dalam jendela
   (simbol, CA unverified): Anakin 832,26 $0,018 (8m lalu), 盘古人 832,26 $0,018 (10m lalu),
   RAM 832,26/864,27 $0,018 (13m dan 14m lalu). Buy SA 864,27 $0,018 (14m lalu) adalah
   re-trade SA (dikenal run 11). Pola Anakin/盘古人/RAM yang hampir identik dengan wallet 19
   (urutan dan ukuran relatif sama) adalah co-buy saja, BUKAN keterkaitan KUAT — tidak
   meruntuhkan entitas. Masing-masing simbol baru 1 entitas. Anakin/盘古人/RAM kini tercatat
   sebagai token yang diketahui bagi wallet ini.
22. 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650 — BNB 0,024 ($17,25). Buy BARU dalam jendela
   (simbol, CA unverified): FLIPPER 11 $0,062 (8m lalu), FP 110 $0,06 (24m lalu), ZKOS 11K
   $0,06 (41m lalu), BOWL 110K $0,059 (58m lalu), TCN 11K $0,059 (1h lalu) — masing-masing
   1 entitas, belum tercatat bagi wallet ini di state run 10–12 (token run 12 wallet ini
   adalah QS/HM/TERMINAL/BIGDOG/MONKEY, yang tidak muncul sebagai Buy di 10 teratas run ini).
   FLIPPER/FP/ZKOS/BOWL/TCN kini tercatat sebagai token yang diketahui bagi wallet ini.
23.–49. (Tier C, termasuk 0x4522…) — TART, RE-TRADE, BUKAN BARU. Semua wallet ini menampilkan
   Buy TART dalam jendela di 10 teratas (berlabel 1h–2h lalu pada pembacaannya masing-masing,
   yaitu ~22:45–22:57 WIB, setelah batas 22:15 WIB), tetapi TART sudah tercatat sebagai token
   yang diketahui bagi ke-27 wallet ini sejak run 12 (26 wallet) / run 11 (0x4522…), sehingga
   buy TART run ini adalah re-trade, bukan token baru, dan TIDAK dihitung. Holdings TART $0
   / Sell All di 10 teratas. Catatan: GMGN menampilkan BNB 0,3 ($213–$214) untuk semua wallet
   Tier C TART ini pada run ini, vs nilai bervariasi 0,17–0,41 pada run 12 — dicatat apa adanya
   sebagai tampilan GMGN, bukan klaim saldo on-chain.
50. 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36 — BNB GMGN 0,013 ($9,09). Buy SENSEI 9,3B
   $488,5 (2h lalu) adalah RE-TRADE SENSEI (dikenal sejak baseline run 11) dan pada label
   relatifnya menunjuk sekitar 21:57 WIB, sebelum batas 22:15 WIB — bukan token baru. Tx In
   BNCB +0,869 (2h lalu) adalah Tx In, bukan Buy. TIDAK ADA token baru untuk wallet ini.

Hitungan sinyal run 13 (entitas, bukan alamat mentah; ambang 13 dengan CA terverifikasi):
- Token dengan CA terverifikasi yang dibeli >=13 entitas dalam jendela: TIDAK ADA — CA tidak
  ditampilkan untuk token mana pun, sehingga TIDAK ADA token yang dapat lolos sebagai CA sama
  antar wallet, apa pun hitungan simbolnya.
- Hitungan simbol HANYA sebagai observasi (bukan sinyal): Anakin 3 entitas (0xc7c5…,
  0xad94…, 0x3803…); 盘古人 2 entitas (0xc7c5…, 0x3803…); RAM 2 entitas (0xc7c5…, 0x3803…);
  POPZERO 1 entitas (0x2325…); SA 1 entitas baru (0xa0c1…; SA wallet lain adalah re-trade);
  PARITY 1 entitas baru (0xa0c1…; PARITY wallet lain adalah re-trade); FLIPPER/FP/ZKOS/BOWL/
  TCN masing-masing 1 entitas (0x7488…). TART TIDAK dihitung karena re-trade token yang sudah
  dikenal (dikenal sejak run 12/11).
- KESIMPULAN: TIDAK ADA SINYAL pada run 13 (ambang: minimal 13 entitas berbeda membeli token
  baru yang SAMA dengan CA terverifikasi). Observasi simbol di atas dicatat sebagai token yang
  diketahui bagi wallet-wallet bersangkutan, bukan rekomendasi beli, bukan promosi, bukan bukti
  insider, bukan pemicu trade.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau (laporan ini
  tidak memuat data pendanaan; co-buy saja, termasuk pola Anakin/盘古人/RAM yang hampir identik
  pada wallet 19/21 dan pola TART serentak pada wallet Tier C, TIDAK meruntuhkan entitas),
  jadi tidak ada runtuhan entitas. Ambang absolut tetap 13.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-01T23:59:00+07:00 waktu ukur runtime; POPZERO, SA/PARITY wallet 17, Anakin/盘古人/RAM
  wallet 19/21, Anakin wallet 20, FLIPPER/FP/ZKOS/BOWL/TCN wallet 22 dicatat sebagai token yang
  diketahui bagi wallet-wallet bersangkutan; BNB GMGN per wallet diperbarui; diskrepansi
  0x2325… dan 0xf6a8… dicatat masih belum terjelaskan). Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah. SENYAP ke chat.

## Run 14 — Senin 2026-11-02, 01:22 WIB (gap: laporan browser belum diterima saat penulisan)

- Daftar dibaca dari `tier-ab-watch.md`: 50 entitas (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 0x81c3...). Daftar lama 23 alamat TIDAK dipakai. Ambang sinyal: minimal 13 entitas berbeda membeli token baru yang sama (CA sama).
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow. Pemeriksaan browser live read-only ke-50 halaman GMGN BSC DIDISPATCH (task browser-task:2558bdfe-e3c0-575a-9043-9ad27a29920a) pada ~01:23 WIB, dengan instruksi eksplisit: bila login-gated, catat saja dan lanjut, JANGAN klik login.
- GAP YANG DICATAT JUJUR, mengikuti preseden Run 1, 3, 4, 5, 6:
  - Laporan per-wallet terperinci dari browser BELUM terkirim ke konteks run ini pada saat penulisan log.
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim — bukan karena wallet terbukti tidak membeli, melainkan karena bukti per-wallet belum diterima. Wallet yang tidak terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline / state run 13 TIDAK diubah: last_checked tetap 2026-11-01T23:59:00+07:00, hanya field `last_attempt` di state yang diperbarui sebagai penanda run ini.
- Tindak lanjut: bila laporan browser run ini tiba belakangan, tambahkan sebagai adendum run ini dengan stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs baseline run 13. Bila tidak tiba, run berikutnya harus mengulang pembacaan ke-50 wallet.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Adendum Run 14 — laporan browser diterima 2026-11-02 (pemeriksaan 01:24–03:06 WIB; runtime-measured task 01:23–03:09 WIB)

Pemeriksaan browser read-only ke-50 halaman GMGN BSC selesai. Semua halaman memuat data publik TANPA login-gated, status "Disconnected", tanpa klik Log in/Sign up/Connect, tanpa sign/transaksi. Koreksi atas bagian "GAP" Run 14 di atas: bukti per-wallet AKHIRNYA diterima, sehingga hitungan sinyal run 14 dapat ditetapkan dari laporan ini dan state diperbarui dari laporan ini (last_checked 2026-11-02T03:06:00+07:00). Batasan laporan yang wajib dicatat:
- Tab Holdings memakai filter default yang teramati: "Hide Didn't Buy" tercentang; "Hide Tiny Pool"/"Hide Honeypot"/"Hide Closed" tidak tercentang: "No assets held." = sesuai tampilan tab itu, BUKAN klaim saldo on-chain nol; token yang hanya diterima lewat Tx In tersaring dari Holdings.
- Contract address TIDAK tercatat pada run ini untuk token mana pun: tidak ada alamat kontrak lengkap yang terlihat dalam teks halaman; CA tidak ditebak dari simbol. Karena itu hitungan sinyal CA-sama TIDAK dapat dibuat dari run ini.
- Waktu aktivitas bersifat relatif terhadap waktu baca ("menit/jam lalu") seperti dilaporkan GMGN, bukan stempel waktu absolut yang diverifikasi on-chain; stempel durasi Holdings dipakai sebagai pembeda yang lebih akurat bila tersedia. Waktu relatif GMGN dibulatkan ke bawah (mis. "1h ago" mencakup ~1 jam 00 menit–1 jam 59 menit).
- Untuk dompet 0x13d1…, 0x7564…, 0x93e7…, 0xb787…, 0xbe59… (dan sebagian lain), tab Holdings tidak selalu dibuka terpisah; Holdings kosong dicatat berdasarkan Distribution Token 0 (atau Distribution bukan-hasil-Buy), mengikuti pola yang terkonfirmasi pada dompet serupa — dicatat sebagai keterbatasan, bukan sebagai saldo on-chain nol.

Per-wallet (ringkas; urutan sesuai tier-ab-watch.md; BNB seperti dilaporkan GMGN):
1. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — BNB 0,067 ($47,7). Kandidat Buy baru (simbol, CA TIDAK terverifikasi): AMINE 156,5K $1,392 dan 币在 206,5K $1,407 — kedua simbol tidak ada di state sebelum run ini (grep-verified 0 hit). Masing-masing 1 entitas.
2.–13. kecuali 14 (0x13d1…, 0x5b2f…, 0x6ba7… BNB 0,001, 0x7564…, 0x8272…, 0x8922… BNB 0, 0x93e7…, 0xaab8…, 0xb787… BNB 0,007, 0xbe59…, 0xda91… BNB 0,05, 0xf6a8… BNB 0): TIDAK ADA buy baru; aktivitas terbaru hanya Tx In/Tx Out lama (termasuk SKYAI dan mubarak sebagai holding/transfer lama). Khusus 0xf6a8…: GMGN MASIH menunjukkan BNB 0, sementara saldo on-chain 0,02479 BNB dari run-run sebelumnya TIDAK dicek ulang on-chain pada run ini — diskrepansi MASIH belum terjelaskan, TIDAK diklaim sebagai pembelian.
14. 0x2325f175975abdbcde555c79cc8e63381d28551b — BNB 0,496 ($352,46). Buy baru TERKONFIRMASI oleh durasi holding (simbol, CA TIDAK terverifikasi): JAGENT矿机 10,7M $68,15, durasi holding mulai 2026/11/02 00:05:40 — 1 entitas. BUKAN baru: BDOG (mulai 2026/11/01 23:54:26) dan 羊头锁 (23:39:22) sebelum batas 23:59 WIB; POPZERO adalah jendela run 13. JAGENT矿机 kini dikenal untuk wallet ini.
15., 18. (0x9856…, 0x40a8…): TIDAK ADA buy baru; aktivitas terbaru ~8 jam lalu (≈17:4x 2026-11-01, sebelum batas).
16., 17., 19.–22. (0x3628…, 0xa0c1…, 0xc7c5…, 0xad94…, 0x3803…, 0x7488…): TIDAK ADA token baru. Buy mikro setelah batas ada, tetapi berukuran/nilai identik dengan pola perdagangan sebelumnya, sehingga diklasifikasikan BUKAN token baru (metode dedupe yang sama seperti run-run sebelumnya; ringkasan state bersifat ringkas, jadi ketiadaan simbol di ringkasan saja tidak mengalahkan kecocokan jumlah/nilai pola). Simbol kunci run 13 — Anakin/盘古人/RAM, FLIPPER/FP/ZKOS/BOWL/TCN, SA/PARITY — seluruhnya berdurasikan sebelum batas atau berupa pengulangan pola, BUKAN baru.
23.–49. (27 wallet Tier C, 0xdb2d… s.d. 0x64e8…): Buy SATO dalam sesi-sesi setelah batas 23:59 WIB (ukuran umumnya ~$100–$300 per Buy; durasi Holdings seluruhnya setelah batas), dan SATO TIDAK ADA di state sebelum run ini (grep-verified 0 hit untuk seluruh state). Buy TART pada wallet-wallet ini adalah RE-TRADE (dikenal sejak run 12/11), BUKAN baru. SATO kini dikenal untuk ke-27 wallet ini; Buy SATO berikutnya adalah re-trade kecuali CA berbeda terverifikasi.
50. 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36 — BNB 0,013 ($9,05). TIDAK ADA buy baru; seluruh Buy SENSEI berdurasikan sebelum batas (holding mulai 2026/11/01 21:32:01).

Hitungan sinyal run 14 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi sebagai SIMBOL saja dalam jendela (setelah 23:59 WIB 2026-11-01): SATO — 27 entitas (simbol saja); JAGENT矿机, AMINE, 币在 — masing-masing 1 entitas.
- TIDAK ADA SINYAL YANG TERVERIFIKASI: ambang adalah minimal 13 entitas membeli token baru yang SAMA dengan CA yang sama, dan CA TIDAK terverifikasi untuk token mana pun pada run ini. Hitungan simbol SATO 27 TIDAK BOLEH dibaca sebagai sinyal — simbol bukan CA, dan beberapa token berbeda dapat memakai simbol yang sama. Ini preseden yang sama seperti observasi simbol TART 26 entitas pada run 12, yang juga dicatat BUKAN sinyal.
- SATO dicatat sebagai observasi simbol saja untuk tindak lanjut (bukan rekomendasi beli, bukan promosi, bukan bukti insider, bukan pemicu trade): run berikutnya wajib berusaha menangkap CA SATO dari tautan token GMGN / verifikasi on-chain sebelum menghitungnya sebagai sinyal apa pun. Sampai CA terverifikasi sama, SATO tetap BUKAN sinyal.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada runtuhan entitas. Co-buy/co-hold saja (termasuk pola SATO yang sama di 27 wallet) TIDAK meruntuhkan entitas.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked 2026-11-02T03:06:00+07:00; BNB ke-50 wallet; run14_summary per wallet; SATO/JAGENT矿机/AMINE/币在 kini dikenal untuk wallet masing-masing). Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.


## Run 15 — Senin 2026-11-02, 03:22 WIB (pemeriksaan browser 03:24–03:42 WIB, runtime-measured)

- Daftar dibaca dari `tier-ab-watch.md`: 50 entitas (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 0x81c3...). Daftar lama 23 alamat TIDAK dipakai. Ambang sinyal: minimal 13 entitas berbeda membeli token baru yang SAMA dengan CA terverifikasi.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow. Pemeriksaan browser live read-only ke-50 halaman GMGN BSC selesai; semua halaman memuat data publik, status "Disconnected", tidak ada yang login-gated, tidak ada yang tidak terbaca.
- Jendela: setelah run 14 berakhir 2026-11-02 03:06 WIB. Waktu aktivitas bersifat relatif terhadap waktu baca GMGN ("menit lalu"), bukan stempel waktu on-chain yang terverifikasi; waktu ~03:xx WIB di bawah ini adalah perkiraan dari usia relatif itu.
- Per-wallet (ringkas; BNB seperti dilaporkan GMGN): Tier A/B — 0x8e96... BNB 0,073, tidak ada buy baru (buy terbaru 2 jam lalu AMINE/币在, dikenal, sebelum jendela); 0x13d1..., 0x5b2f..., 0x6ba7..., 0x7564..., 0x8272..., 0x93e7..., 0xaab8..., 0xb787... (0,007), 0xbe59..., 0xda91... (0,05), 0xf6a8... (0): tidak ada buy baru, hanya Tx In lama. 0x8922... BNB 0, tidak ada buy baru (XPIN 3 hari lalu, XRP/SLX 4 hari lalu, dikenal). 0x2325... BNB 0,496, tidak ada buy baru (buy terbaru 3 jam lalu JAGENT矿机/BDOG/羊头锁/POPZERO, dikenal, sebelum jendela). Tier C mikro: 0x9856... dan 0x40a8... tidak ada buy baru (buy terbaru 10 jam lalu, dikenal); 0x3628... dan 0xa0c1... hanya SA re-trade 1,13K $0,07; 0xc7c5.../0xad94.../0x3803... hanya SA/RAM re-trade plus observasi PI/JENSEN di bawah; 0x7488... hanya observasi USDT/EURO di bawah. Tier C besar (27 wallet, 0xdb2d... s.d. 0x64e8...): buy TART dalam jendela di semua wallet yang dilaporkan, semuanya RE-TRADE (dikenal sejak run 12/11), BUKAN baru; SATO, bila muncul, likewise re-trade (dikenal sejak run 14). 0x81c3... BNB 0,013, tidak ada buy baru (SENSEI 6 jam lalu, dikenal, sebelum jendela).
- Observasi simbol SAJA (BUKAN sinyal, CA TIDAK terverifikasi, simbol bukan CA): PI dibeli 0xc7c5... (1,13K $0,024, ~03:25 dan ~03:22 WIB), 0xad94... (1,13K $0,024, ~03:25 dan ~03:23 WIB), 0x3803... (832,26 $0,018, ~03:25 dan ~03:22 WIB); JENSEN dibeli ketiga wallet yang sama pada ukuran/nilai yang sama persis (~03:06–03:07 WIB, tepat di batas jendela). Keduanya diklasifikasikan sebagai ROTASI POLA MIKRO, bukan token baru, dengan metode dedupe yang sama seperti run 14: ukuran/nilai identik dengan pola SA/RAM wallet-wallet itu, muncul serentak pada menit yang sama. PI/JENSEN kini dicatat sebagai simbol pola yang diketahui bagi ketiga wallet itu; buy PI/JENSEN berikutnya adalah pengulangan pola kecuali CA berbeda terverifikasi. USDT 11K $0,06 (~03:31 WIB) dan EURO 110 $0,062 (~03:14 WIB) untuk 0x7488... adalah observasi rotasi $0,06 satu entitas saja, likewise dicatat sebagai simbol rotasi yang diketahui bagi wallet itu, bukan token baru yang terkonfirmasi.
- Hitungan sinyal run 15 (entitas, ambang 13 dengan CA terverifikasi): TIDAK ADA SINYAL. CA tidak ditampilkan untuk token mana pun, sehingga tidak ada hitungan CA-sama yang dapat dibuat, apa pun hitungan simbolnya. PI/JENSEN 3 entitas simbol saja pun berada di bawah ambang 13 dan tidak terverifikasi CA-nya, jadi tetap bukan sinyal.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau (laporan ini tidak memuat data pendanaan; co-buy/co-hold saja, termasuk pola PI/JENSEN dan TART serentak, TIDAK meruntuhkan entitas), jadi tidak ada runtuhan entitas. Ambang absolut tetap 13.
- Diskrepansi yang masih terbuka: 0xf6a8... GMGN masih BNB 0 vs on-chain 0,02479 dari run-run sebelumnya, TIDAK dicek ulang on-chain pada run ini — tetap belum terjelaskan, tidak diklaim sebagai pembelian.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked 2026-11-02T03:42:00+07:00; BNB ke-50 wallet; run15_summary per wallet; PI/JENSEN untuk 0xc7c5.../0xad94.../0x3803... dan USDT/EURO untuk 0x7488... dicatat sebagai simbol pola/rotasi yang diketahui). Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah. SENYAP ke chat.

## Run 16 — Senin 2026-11-02, 05:22–~05:24 WIB (gap: laporan browser belum diterima saat penulisan)

- Daftar dibaca dari `tier-ab-watch.md`: 50 entitas terpantau (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 1). Daftar lama 23 alamat TIDAK dipakai. Ambang sinyal: minimal 13 entitas berbeda membeli token baru yang sama (CA sama).
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-50 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>)
  DIDISPATCH (task browser-task:699b35fe-0704-520e-b3ef-ec287df8c12f) pada ~05:23 WIB, dengan
  instruksi eksplisit: bila login-gated, catat saja dan lanjut, JANGAN klik login.
- GAP YANG DICATAT JUJUR, mengikuti preseden Run 1, Run 3, Run 4, Run 5, dan Run 6:
  - Laporan per-wallet terperinci (holdings + trade terbaru per wallet) dari browser BELUM
    terkirim ke konteks run ini pada saat penulisan log.
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim (ambang: minimal 13 entitas berbeda membeli token baru yang sama,
    CA sama) — bukan karena wallet terbukti tidak membeli, melainkan karena bukti per-wallet
    belum diterima. Wallet yang tidak terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline / state run 15 TIDAK diubah: last_checked tetap 2026-11-02T03:42:00+07:00 dan holdings
    per wallet tetap dari run 15, sampai laporan browser run ini benar-benar diterima.
- Tindak lanjut: bila laporan browser run ini tiba belakangan, tambahkan sebagai adendum run ini
  dengan stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs baseline
  run 15 (jendela setelah 03:42 WIB 2026-11-02). Bila tidak tiba, run berikutnya harus mengulang
  pembacaan ke-50 wallet dan mencatat holdings + aktivitas terbaru per wallet secara eksplisit
  sebelum menghitung sinyal apa pun.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Adendum Run 16 — laporan browser diterima, pemeriksaan terukur 05:24–05:54 WIB (runtime-measured 05:24–05:58 WIB)

Pemeriksaan browser live read-only ke-50 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>).
Semua 50 halaman memuat data publik TANPA login-gated, status Disconnected, tanpa klik Log in/
Sign up/Connect, tanpa sign/transaksi. Koreksi atas bagian "GAP" di atas: bukti per-wallet
AKHIRNYA diterima, sehingga hitungan run 16 dapat ditetapkan dari laporan ini dan state
diperbarui dari laporan ini (last_checked 2026-11-02T05:54:00+07:00). Batasan laporan yang wajib
dicatat:
- Tab Holdings memakai filter default yang teramati di run-run sebelumnya: "No assets held." =
  sesuai tampilan tab itu, BUKAN klaim saldo on-chain nol; token yang hanya diterima lewat
  Tx In tersaring dari Holdings.
- Contract address TIDAK tercatat pada run ini untuk token mana pun: tidak ada alamat kontrak
  lengkap yang terlihat dalam teks halaman; CA tidak ditebak dari simbol. Token dicatat
  berdasarkan simbol saja, dan karena itu TIDAK dapat dipakai sebagai CA terverifikasi untuk
  perbandingan antar wallet — hitungan di bawah memakai simbol + konteks baseline, dan
  kesimpulan sinyal mengikuti preseden TART run 12 dan SATO run 14.
- Waktu aktivitas bersifat relatif terhadap waktu baca ("menit/jam lalu") seperti dilaporkan
  GMGN, bukan stempel waktu absolut yang diverifikasi on-chain; label relatif dicocokkan
  dengan jumlah/nilai transaksi sebelum dinyatakan baru. Jendela run 16 adalah setelah
  03:42 WIB 2026-11-02 (last_checked run 15). Label di bawah 2 jam pada saat kunjungan jelas
  setelah cutoff; label di atas 2 jam jelas sebelum cutoff; label tepat 2 jam berada di sekitar
  batas dan tidak dipastikan hanya dari label itu — tidak ada hitungan di bawah yang bergantung
  pada label 2 jam yang ambigu.
- Saldo BNB GMGN untuk wallet Tier C besar berfluktuasi lebar vs baseline state (mis. 0,03–0,45
  pada run ini vs 0,03–0,54 sebelumnya, termasuk pola 0,3 yang berulang) dan TIDAK dipakai
  sebagai bukti beli/jual; saldo dicatat apa adanya di state.

Per-wallet (ringkas; urutan sesuai tier-ab-watch.md, nomor 1–50 sesuai laporan browser):
1. 0x8e96… — BNB 0,073 ($51,77). Buy AES 133,1K $1,382 (1m lalu, pasca-cutoff) — simbol-baru
   bagi wallet ini (0 hit di state sebelum run ini), CA UNVERIFIED, 1 entitas. Buy AMINE/
   币在/ZachCBX/火龙果人生 4–9 jam lalu adalah token yang sudah dikenal, sebelum jendela.
2.–6., 8.–13. (0x13d1…, 0x5b2f…, 0x6ba7…, 0x7564…, 0x8272…, 0x93e7…, 0xaab8…, 0xb787…,
   0xbe59…, 0xda91…, 0xf6a8…): TIDAK ADA buy baru. Aktivitas terbaru hanya Tx In/Tx Out lama
   (termasuk SKYAI dan mubarak sebagai holding/transfer lama, bukan buy baru). Holdings:
   "No assets held." untuk semuanya. Khusus wallet 13 (0xf6a8…): GMGN MASIH menunjukkan BNB 0
   ($0) dan aktivitas terbaru 11 hari lalu (Tx In NEX) — diskrepansi GMGN-vs-on-chain (on-chain
   0,02479 BNB sejak run 3) MASIH belum terjelaskan, TIDAK diklaim sebagai pembelian, dan
   TIDAK dicek ulang on-chain pada run ini.
7. 0x8922… — BNB 0 ($0). Holdings tampil: XPIN, WKC, XRP, SLX, BANK, SKYAI, CREPE, TAG, PENGU,
   elizaOS. Buy terbaru XPIN 16 hari lalu — baseline, bukan buy baru. TIDAK ADA buy baru.
14. 0x2325… — BNB 0,496 ($350,12). Holdings bukan nol: BDOG $98,64 / 5B, 羊头锁 $70,15 / 7,2M,
   PTG $105,79 / 34,29. Buy terbaru 5 jam lalu (JAGENT矿机, BDOG, 羊头锁, POPZERO) adalah
   token yang sudah dikenal, sebelum jendela. TIDAK ADA buy baru.
15. 0x9856… — BNB 0 ($0). Buy terbaru 12 jam lalu (鼻涕, ZAGS) adalah token yang sudah dikenal,
   sebelum jendela. TIDAK ADA buy baru.
16. 0x3628… — BNB 0,011 ($7,53). Buy SA 1,13K $0,07 berulang adalah re-trade; Buy BAGENT 1,13K
   $0,07 (1h lalu, pasca-cutoff) — simbol-baru bagi wallet ini, CA UNVERIFIED, 2 entitas
   bersama wallet 17. BAGENT kini dikenal bagi wallet ini.
17. 0xa0c1… — BNB 0,023 ($16,39). Sama seperti wallet 16: SA re-trade; Buy BAGENT 1,13K $0,07
   (1h lalu, pasca-cutoff) — simbol-baru, CA UNVERIFIED, 2 entitas bersama wallet 16.
   BAGENT kini dikenal bagi wallet ini.
18. 0x40a8… — BNB 0,022 ($15,63). Buy terbaru 12 jam lalu (NITRO, 鼻涕, FORX, ZAGS) adalah
   token yang sudah dikenal, sebelum jendela. TIDAK ADA buy baru.
19. 0xc7c5… — BNB 0,011 ($7,85). Buy SA re-trade; Buy Rockhopp 1,13K $0,024, HI 1,13K $0,024,
   PEAK 1,13K $0,024, uni 1,13K $0,024 (6–45m lalu, pasca-cutoff) — observasi rotasi pola mikro
   (ukuran/nilai identik dengan pola SA/RAM wallet ini, serentak dengan wallet 20/21),
   CA UNVERIFIED, 3 entitas, TIDAK dihitung sebagai token baru mengikuti metode dedupe
   run 14/15 (PI/JENSEN). Rockhopp/HI/PEAK/uni kini tercatat sebagai simbol pola yang dikenal
   bagi wallet ini.
20. 0xad94… — BNB 0,049 ($34,90). Sama seperti wallet 19: SA re-trade; Buy Rockhopp/HI 1,13K
   $0,024 (7–22m lalu) — observasi rotasi pola, CA UNVERIFIED, 3 entitas, TIDAK dihitung
   sebagai token baru. Rockhopp/HI kini tercatat sebagai simbol pola yang dikenal bagi
   wallet ini.
21. 0x3803… — BNB 0,023 ($16,14). Sama seperti wallet 19/20: SA re-trade; Buy Rockhopp/HI
   832,26 $0,018 (7–23m lalu) — observasi rotasi pola, CA UNVERIFIED, 3 entitas, TIDAK
   dihitung sebagai token baru. Rockhopp/HI kini tercatat sebagai simbol pola yang dikenal
   bagi wallet ini.
22. 0x7488… — BNB 0,025 ($17,48). Buy TSLA 110K $0,059, USD 11K $0,056, FNCY 110K $0,06,
   PIVT 110 $0,062, ANCHORAGE 1,1K $0,059 (9m–1h lalu, pasca-cutoff) — observasi rotasi pola
   $0,06 satu entitas (analog dengan USDT/EURO run 15), CA UNVERIFIED, TIDAK dihitung
   sebagai token baru. TSLA/USD/FNCY/PIVT/ANCHORAGE kini tercatat sebagai simbol rotasi
   yang dikenal bagi wallet ini.
23.–49. (Tier C besar, 0xdb2d… s.d. 0x64e8…): Buy FAGENT dan TART dalam jendela adalah
   RE-TRADE (FAGENT dikenal sejak run 11, TART sejak run 12/11), BUKAN baru, dan TIDAK
   dihitung. Yang baru menurut simbol (CA UNVERIFIED, lihat hitungan di bawah):
   - SAFU, simbol-baru bagi 26 entitas (0xdb2d…, 0xc621…, 0x9cdd…, 0xaa49…, 0x82c6…,
     0x3154…, 0xca4e…, 0xe9ed…, 0x3a39…, 0xcb08…, 0xb940…, 0x4522…, 0x5b4b…, 0xc659…,
     0x3623…, 0xf968…, 0x2cc8…, 0x97bd…, 0x1cce…, 0xc0c8…, 0xc194…, 0xa952…, 0x92bc…,
     0x9b51…, 0xfdec…, 0x64e8…), ukuran umumnya ~$140–$310 per Buy pasca-cutoff.
     Wallet 0xf795… TIDAK menampilkan Buy SAFU di 5 teratas, jadi SAFU TIDAK tercatat
     sebagai dikenal bagi wallet itu dari run ini.
   - PYRO, simbol-baru bagi 24 entitas (0xdb2d…, 0xc621…, 0xf795…, 0x9cdd…, 0xaa49…,
     0x82c6…, 0xca4e…, 0xe9ed…, 0x3a39…, 0xcb08…, 0x4522…, 0x5b4b…, 0xc659…, 0x3623…,
     0xf968…, 0x2cc8…, 0x97bd…, 0x1cce…, 0xc0c8…, 0xc194…, 0x92bc…, 0x9b51…, 0xfdec…,
     0x64e8…), ukuran umumnya ~$140–$310 per Buy pasca-cutoff. Wallet 0x3154…, 0xb940…,
     dan 0xa952… TIDAK menampilkan Buy PYRO di 5 teratas, jadi PYRO TIDAK tercatat sebagai
     dikenal bagi ketiga wallet itu dari run ini.
   SAFU dan PYRO kini tercatat sebagai token yang diketahui bagi wallet-wallet di atas
   (sesuai daftar masing-masing), sehingga buy SAFU/PYRO berikutnya adalah re-trade
   kecuali CA berbeda terverifikasi.
50. 0x81c3… — BNB 0,013 ($9,02). Buy terbaru SENSEI 8 jam lalu adalah token yang sudah
   dikenal, sebelum jendela. TIDAK ADA buy baru.

Hitungan sinyal run 16 (entitas, bukan alamat mentah):
- TIDAK ADA SINYAL YANG TERVERIFIKASI: ambang adalah minimal 13 entitas membeli token baru
  yang SAMA dengan CA yang sama, dan CA TIDAK terverifikasi untuk token mana pun pada run
  ini. Hitungan simbol SAFU 26 entitas dan PYRO 24 entitas TIDAK BOLEH dibaca sebagai sinyal
  — simbol bukan CA, dan beberapa token berbeda dapat memakai simbol yang sama. Ini preseden
  yang sama seperti observasi simbol TART 26 entitas pada run 12 dan SATO 27 entitas pada
  run 14, yang juga dicatat BUKAN sinyal. SAFU/PYRO adalah OBSERVASI WAJIB TINDAK LANJUT:
  bila pada run berikutnya CA SAFU/PYRO terverifikasi sama antar wallet, hitungan itu harus
  dihitung ulang dari data run ini; sampai saat itu, tidak ada pemicu screening paper, tidak
  ada rekomendasi beli, tidak ada promosi, dan tidak ada pemicu trade dari run ini.
- Hitungan simbol lain di bawah ambang dan/atau bukan token baru: AES 1 entitas; BAGENT
  2 entitas; Rockhopp/HI/PEAK/uni 3 entitas (rotasi pola, bukan token baru); TSLA/USD/FNCY/
  PIVT/ANCHORAGE 1 entitas (rotasi pola, bukan token baru).
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau (laporan ini
  tidak memuat data pendanaan; co-buy/co-hold saja, termasuk pola SAFU/PYRO serentak pada
  wallet Tier C besar dan pola mikro serentak, TIDAK meruntuhkan entitas), jadi tidak ada
  runtuhan entitas. Ambang absolut tetap 13.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-02T05:54:00+07:00; run16_summary untuk ke-50 wallet; BNB GMGN terbaru per wallet;
  SAFU/PYRO dicatat sebagai dikenal sesuai daftar di atas; BAGENT/Rockhopp/HI/PEAK/uni/
  TSLA/USD/FNCY/PIVT/ANCHORAGE dicatat sebagai simbol pola/rotasi yang dikenal sesuai
  wallet masing-masing). Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 17 — Senin 2026-11-02, 07:22–~07:24 WIB (gap: laporan browser belum diterima saat penulisan)

- Daftar dibaca dari `tier-ab-watch.md` setiap run: 50 entitas privat (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 0x81c3… = 50). Daftar lama 23 alamat TIDAK dipakai. Ambang sinyal: minimal 13 entitas berbeda membeli token baru yang sama (CA sama).
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-50 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>)
  DIDISPATCH (task browser-task:b85e753c-4bf3-53e0-bd39-fdaa810d63c4) pada ~07:23 WIB, dengan
  instruksi eksplisit: bila login-gated, catat saja dan lanjut, JANGAN klik login.
- GAP YANG DICATAT JUJUR, mengikuti preseden Run 1, Run 3, Run 4, Run 5, dan Run 6:
  - Laporan per-wallet terperinci (holdings + trade terbaru per wallet) dari browser BELUM
    terkirim ke konteks run ini pada saat penulisan log.
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim (ambang: minimal 13 entitas privat berbeda membeli token baru
    yang sama, CA sama) — bukan karena wallet terbukti tidak membeli, melainkan karena bukti
    per-wallet belum diterima. Wallet yang tidak terbaca datanya TIDAK dianggap tidak membeli,
    sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline / state run 16 TIDAK diubah: last_checked tetap 2026-11-02T05:54:00+07:00 dan holdings
    per wallet tetap dari run 16, sampai laporan browser run ini benar-benar diterima. Hanya field
    `last_attempt` di state yang diperbarui sebagai penanda run ini.
- Tindak lanjut: bila laporan browser run ini tiba belakangan, tambahkan sebagai adendum run ini
  dengan stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs baseline
  run 16. Bila tidak tiba, run berikutnya harus mengulang pembacaan ke-50 wallet dan mencatat
  holdings + aktivitas terbaru per wallet secara eksplisit sebelum menghitung sinyal apa pun.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Adendum Run 17 — laporan browser diterima ~07:49 WIB

Pemeriksaan browser terukur 07:25–07:49 WIB (waktu ukur runtime; laporan per-wallet
07:25–07:47 WIB). Semua 50 halaman memuat data publik TANPA login-gated, status
"Disconnected", tanpa klik Log in/Sign up/Connect, tanpa sign/transaksi. Koreksi atas
bagian "GAP" di atas: bukti per-wallet AKHIRNYA diterima, sehingga hitungan sinyal run 17
dapat ditetapkan dari laporan ini dan state diperbarui dari laporan ini (last_checked
2026-11-02T07:47:00+07:00). Batasan laporan yang wajib dicatat:
- Contract address TIDAK tercatat pada run ini untuk token mana pun: tidak ada alamat
  kontrak lengkap yang terlihat dalam teks halaman; CA tidak ditebak dari simbol. Token
  dicatat berdasarkan simbol saja, dan karena itu tidak dapat dipakai sebagai CA
  terverifikasi untuk perbandingan antar wallet — hitungan di bawah memakai simbol +
  konteks baseline, dan tidak ada token CA-sama yang lolos ambang.
- Waktu aktivitas bersifat relatif terhadap waktu baca ("m/h ago") seperti dilaporkan
  GMGN, bukan stempel waktu absolut yang diverifikasi on-chain; label relatif dicocokkan
  dengan jumlah/nilai transaksi sebelum dinyatakan baru, mengikuti preseden run 3–16.
- Tab Holdings DIBUKA dan diperiksa hanya untuk dompet 1–18; untuk dompet 19–50
  pemeriksaan difokuskan pada saldo BNB dan Activity teratas, dan tab Holdings TIDAK
  dibuka — kolom holdings dompet 19–50 di state TIDAK diubah (bukan dikosongkan), dan
  "tidak dibuka" bukan klaim "tidak ada aset".
- Untuk dompet 0x9cdd…, 0x82c6…, 0x3a39…, 0xb940…, 0x4522…, 0x5b4b…, 0xc659…, 0x3623…,
  0x2cc8…, 0x97bd…, 0x1cce…, 0xa952…, dan 0x81c3…: baris Buy teratas berada di bawah
  viewport (di bawah Sell/Tx In teratas), sehingga jumlah/nilai/token Buy teratas TIDAK
  dicatat dan TIDAK ditebak; khusus 0x81c3… token Buy teratasnya pun tidak tercatat,
  sehingga wallet itu tidak menyumbang hitungan apa pun pada run ini.

Per-wallet (ringkas; urutan sesuai tier-ab-watch.md; detail penuh ada di
run17_summary tiap wallet di state):
1. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — dibaca 07:25, kunjungan ulang 07:47.
   BNB 0,07 ($49,77) pada tampilan 30D, tetapi 0 ($0) pada tampilan 7D saat kunjungan
   ulang — inkonsistensi tampilan GMGN, BUKAN klaim on-chain. Buy BARU simbol (CA
   UNVERIFIED, 1 entitas): 即梦ai 188,3K $1,409 (11m ago pada 07:25, ~07:14 WIB), lalu
   Sell 即梦ai 188,3K $1,179 (4m ago pada 07:47). Buy 视界之眼/朗月/MAX/爪子 ~1h ago
   adalah holding yang sudah dikenal, re-trade. 即梦ai kini dikenal untuk wallet ini.
2.–13. (0x13d1…, 0x5b2f…, 0x6ba7…, 0x7564…, 0x8272…, 0x8922…, 0x93e7…, 0xaab8…,
   0xb787…, 0xbe59…, 0xda91…, 0xf6a8…): TIDAK ADA buy baru. Aktivitas terbaru hanya
   Tx In/Tx Out lama (termasuk SKYAI dan mubarak sebagai holding/transfer lama, bukan
   buy baru). Khusus wallet 13 (0xf6a8…): GMGN MASIH menunjukkan BNB 0 ($0) — diskrepansi
   GMGN-vs-on-chain (on-chain 0,02479 BNB) MASIH belum terjelaskan, TIDAK dicek ulang
   on-chain pada run ini, dan TIDAK diklaim sebagai pembelian.
14. 0x2325f175975abdbcde555c79cc8e63381d28551b — dibaca 07:34. BNB 0,833 ($591,7).
   Buy BNCB 0,175 $0,894 (13m ago, ~07:21 WIB) adalah token yang SUDAH tercatat dipegang
   sejak run 11, BUKAN token baru bagi wallet ini. Holdings tampil antara lain BNCB,
   BDOG, POPZERO, BNBH, JAGENT矿机, 币安狗 — semuanya token yang sudah dikenal.
15. 0x9856bac497634a62a970233bc4b0f5bb52c844c1 — dibaca 07:35. TIDAK ADA buy baru;
   Buy terbaru 14h ago (鼻涕, ZAGS) adalah transaksi yang sudah dikenal, di luar jendela.
16.–17. 0x3628… / 0xa0c1… — dibaca 07:35–07:37. Buy SA 1,13K $0,07 (9m/10m ago) adalah
   re-trade/pola berulang, BUKAN baru. BAGENT sudah dikenal sejak run 16.
18. 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c — dibaca 07:38. TIDAK ADA buy baru;
   Buy terbaru 14h ago (NITRO, 鼻涕, FORX, ZAGS) sudah dikenal, di luar jendela.
19.–21. 0xc7c5… / 0xad94… / 0x3803… — dibaca 07:38–07:39. Buy MOVEMBER (1,13K $0,024 /
   1,13K $0,024 / 832,25 $0,018; 5m–6m ago, ~07:32–07:33 WIB) + Buy SA pola yang sama
   adalah observasi rotasi-pola simbol saja (CA UNVERIFIED, 3 entitas), TIDAK dihitung
   sebagai token baru mengikuti metode dedupe run 14/15/16 (PI/JENSEN/Rockhopp/HI/
   PEAK/uni). MOVEMBER kini dicatat sebagai simbol pola yang dikenal untuk ketiga wallet.
22. 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650 — dibaca 07:39. Buy GIST 1,1K $0,058
   (13m ago) adalah observasi rotasi-pola $0,06 satu entitas (CA UNVERIFIED), TIDAK
   dihitung sebagai token baru mengikuti preseden run 15/16 (USDT/EURO, TSLA/USD/
   FNCY/PIVT/ANCHORAGE). GIST kini dicatat sebagai simbol rotasi yang dikenal.
23.–49. Klaster besar Tier C — dibaca 07:40–07:47. Buy SAFU ~1h ago (~06:40 WIB,
   di dalam jendela setelah 05:54 WIB) terlihat pada seluruh klaster ini. Penilaian
   vs baseline run 16 adalah KUNCI: SAFU SUDAH dicatat sebagai dikenal untuk 26 entitas
   besar Tier C pada run 16, sehingga Buy SAFU run 17 bagi mereka adalah RE-TRADE,
   BUKAN token baru — KECUALI SATU: 0xf795… (Buy SAFU 45,89K $2,031) yang pada run 16
   secara eksplisit TIDAK tercatat SAFU-nya (tidak ada Buy SAFU di top 5), sehingga
   SAFU adalah simbol-baru untuk wallet itu saja (1 entitas, CA UNVERIFIED). Untuk
   dompet-dompet yang baris Buy teratasnya di bawah viewport (daftar di batasan di
   atas), Buy SAFU-nya dicatat ada di daftar tetapi jumlah/nilai tidak ditebak, dan
   karena SAFU sudah dikenal sejak run 16 bagi mereka, mereka tetap re-trade.
   Buy FAGENT/TART, bila ada, juga re-trade (dikenal sejak run 11/12). Tidak ada Buy
   PYRO baru yang dilaporkan pada run ini.
50. 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36 — dibaca 07:47. Baris Buy ada di
   halaman (20 sel Buy) tetapi baris teratasnya di bawah viewport, sehingga
   token/jumlah/nilai Buy teratas TIDAK dicatat dan TIDAK ditebak; aktivitas teratas
   yang terlihat adalah Tx Out BNCB 23m ago dan Sell 社群人生 24m ago. Wallet ini
   TIDAK menyumbang hitungan apa pun pada run ini.

Hitungan sinyal run 17 (entitas, bukan alamat mentah; ambang 13 entitas, CA sama):
- Token simbol-baru yang terverifikasi dalam jendela (setelah 05:54 WIB): 即梦ai —
  1 entitas (wallet 1); SAFU — 1 entitas simbol-baru (0xf795… saja, karena SAFU
  klaster lainnya adalah re-trade). MOVEMBER (3 entitas) dan GIST (1 entitas) TIDAK
  dihitung sebagai token baru karena metode dedupe rotasi-pola run 14–16. BNCB, SA,
  dan SAFU klaster lainnya adalah re-trade token yang sudah dikenal.
- TIDAK ADA token CA-sama yang dibeli oleh 13 entitas atau lebih — bahkan tidak ada
  yang mencapai 4 entitas sebagai simbol-baru, dan CA tidak terverifikasi untuk token
  mana pun sehingga hitungan CA-sama tidak mungkin dilakukan sama sekali.
  Jadi TIDAK ADA SINYAL (ambang: minimal 13 entitas privat berbeda membeli token baru
  yang sama, CA sama).
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi
  tidak ada runtuhan entitas. Co-buy/co-hold saja (termasuk pola MOVEMBER/SAFU yang
  bersamaan) TIDAK meruntuhkan entitas.
- Pembelian 1 wallet saja = bukan sinyal; di run ini bahkan token simbol-baru terbanyak
  pun hanya 1 entitas setelah dedupe dan re-trade diterapkan.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-02T07:47:00+07:00; run17_summary untuk ke-50 wallet; BNB diperbarui di mana
  dilaporkan; holdings dompet 19–50 TIDAK diubah karena tab Holdings tidak dibuka).
  Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 18 — Senin 2026-11-02, 09:22 WIB (gap: laporan browser belum diterima saat penulisan)

- Daftar dibaca dari `tier-ab-watch.md`: 50 entitas (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi 0x81c3…). Daftar lama 23 alamat TIDAK dipakai. Ambang sinyal: minimal 13 entitas berbeda membeli token baru yang sama (CA sama), sesuai skala >25% di file.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-50 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>)
  DIDISPATCH (task browser-task:bf6abab4-eb30-5c26-9d9e-03b35bd89b71) pada 09:22 WIB, dengan
  instruksi eksplisit: bila login-gated, catat saja dan lanjut, JANGAN klik login. Jendela yang
  dicari: trade setelah last_checked run 17 (2026-11-02T07:47:00+07:00).
- GAP YANG DICATAT JUJUR, mengikuti preseden run-run sebelumnya:
  - Laporan per-wallet terperinci (aktivitas terbaru per wallet) dari browser BELUM terkirim
    ke konteks run ini pada saat penulisan log.
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim (ambang 13 entitas, CA sama) — bukan karena wallet terbukti
    tidak membeli, melainkan karena bukti per-wallet belum diterima. Wallet yang tidak terbaca
    datanya TIDAK dianggap tidak membeli, sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline / state run 17 TIDAK diubah kecuali field `last_attempt` sebagai penanda run ini:
    last_checked tetap 2026-11-02T07:47:00+07:00 dan holdings per wallet tetap dari run 17,
    sampai laporan browser run ini benar-benar diterima.
- Tindak lanjut: bila laporan browser run ini tiba, tambahkan sebagai adendum run ini dengan
  stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs baseline run 17
  (termasuk dedupe rotasi-pola run 14–17 dan re-trade token yang sudah dikenal). Bila tidak tiba,
  run berikutnya harus mengulang pembacaan ke-50 wallet.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Adendum Run 18 — laporan browser diterima, pemeriksaan terukur 09:25–09:42 WIB (runtime 09:24–09:45 WIB)

Pemeriksaan browser read-only ke-50 halaman GMGN BSC, tanpa login, tanpa klik Log in/Sign
up/Connect, tanpa sign/transaksi. Semua 50 halaman memuat data publik — TIDAK ADA yang
login-gated. Batasan yang wajib dicatat:
- Contract address TIDAK tercatat untuk token mana pun: tidak ada alamat kontrak lengkap yang
  tampil di teks halaman; CA tidak ditebak dari simbol. Token dicatat berdasarkan simbol saja,
  dan karena itu hitungan CA-sama antar wallet TIDAK mungkin dilakukan pada run ini.
- Waktu aktivitas bersifat relatif terhadap waktu baca ("menit/jam lalu") seperti dilaporkan
  GMGN, bukan stempel waktu absolut yang diverifikasi on-chain; label relatif dicocokkan
  dengan jumlah/nilai transaksi sebelum dinyatakan baru, mengikuti preseden run 3–17.
- Tab Holdings TIDAK dibuka untuk dompet 19–50 (Activity/BNB saja sesuai instruksi run ini),
  dan untuk dompet 1–18 prioritas diberikan ke Activity sehingga holdings tidak dicatat di
  laporan ini; field holdings dompet 19–50 TIDAK diubah, bukan dikosongkan.
- Koreksi bookkeeping state: kunci lama untuk dompet Tier C 0x97bd895f8123a7837368df410e7d308246c0b3e9a
  ternyata terpotong satu karakter (…0b3e9) di state run-run sebelumnya; riwayatnya digabungkan
  ke kunci alamat lengkap yang benar pada run ini, sehingga jumlah kunci kembali 50 dan
  baseline run 10–17 dompet itu tidak hilang.

Per-wallet (ringkas; urutan sesuai tier-ab-watch.md; jendela = setelah 07:47 WIB 2026-11-02):
1. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — dibaca 09:25. BNB 0,07 ($49,71).
   Buy SIMBOL-BARU dalam jendela: 豹拉 198,9K $1,395 (8m ago, ~09:17 WIB, CA UNVERIFIED,
   1 entitas). Buy 即梦ai 2h ago, AES 4h ago, AMINE/币在 8h ago, ZachCBX/火龙果人生 9–13h ago
   adalah trade yang sudah dikenal run 12–17, bukan baru. Sell 即梦ai 188,3K $1,179 1h ago
   cocok jumlah/nilai dengan sell run 17, diperlakukan sebagai trade yang sama.
2.–6., 8.–13. (0x13d1…, 0x5b2f…, 0x6ba7…, 0x7564…, 0x8272…, 0x93e7…, 0xaab8…, 0xb787…,
   0xbe59…, 0xda91…, 0xf6a8…): TIDAK ADA buy baru. Aktivitas terbaru hanya Tx In lama
   (termasuk SKYAI sebagai holding lama, bukan buy baru). Khusus 0xf6a8…: GMGN MASIH
   menunjukkan BNB 0 ($0) dan aktivitas terbaru 13 hari lalu — diskrepansi GMGN-vs-on-chain
   (on-chain 0,02479 BNB) MASIH belum terjelaskan, TIDAK dicek ulang on-chain pada run ini,
   dan TIDAK diklaim sebagai pembelian.
7. 0x892200223bdfb11d2506c5ab1cae9222ce253acc — dibaca 09:27. BNB 0 ($0). Activity:
   "No Data" pada halaman publik (BUKAN login-gated) — aktivitas TIDAK TERBACA pada run ini,
   TIDAK dihitung sebagai tidak membeli; field holdings tidak diubah.
14. 0x2325f175975abdbcde555c79cc8e63381d28551b — dibaca 09:29. BNB 0,773 ($551,86), turun
    dari 0,833 run 17. Buy SIMBOL-BARU dalam jendela: 哆啦B梦 8,6M $40,9 (32m ago, ~08:57 WIB,
    CA UNVERIFIED, 1 entitas). Buy BNCB 2h ago adalah token yang SUDAH tercatat dipegang
    sejak run 11 dan pra-jendela (~07:29 WIB), bukan baru. Sell 币安狗 / Burns 2h ago dan
    trade POPZERO/JAGENT矿机/BDOG/羊头锁 9–10h ago adalah trade yang sudah dikenal/pra-jendela.
15. 0x9856bac497634a62a970233bc4b0f5bb52c844c1 — dibaca 09:29. TIDAK ADA buy baru;
    Buy terbaru 16h ago (鼻涕, ZAGS) sudah dikenal, di luar jendela.
16.–17. 0x3628… / 0xa0c1… — dibaca 09:29–09:30. Buy 老板 1,13K $0,071 (1m/2m ago),
    茧 1,13K $0,071 (12m ago), 羊了个 1,13K $0,071 (21m ago) adalah observasi rotasi-pola
    simbol saja (CA UNVERIFIED, batch yang sama dengan dompet 19–21), TIDAK dihitung sebagai
    token baru mengikuti metode dedupe run 14–17; 老板/茧/羊了个 kini dicatat sebagai simbol
    pola yang dikenal untuk kedua dompet. Buy SA adalah re-trade/pola berulang, bukan baru.
18. 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c — dibaca 09:30. TIDAK ADA buy baru;
    Buy terbaru 16h ago (NITRO, 鼻涕, FORX, ZAGS) sudah dikenal, di luar jendela.
19.–21. 0xc7c5… / 0xad94… / 0x3803… — dibaca 09:31–09:32. Buy DOGE, 豹拉, MEMECOINS,
    老板, 茧, STEALTH, 羊了个, 박진혁 (1,13K $0,024 / 1,13K $0,024 / 832,25 $0,018; 2m–31m ago)
    adalah observasi rotasi-pola simbol saja (CA UNVERIFIED, batch yang sama dengan dompet
    16–17), TIDAK dihitung sebagai token baru mengikuti metode dedupe run 14–17; simbol-simbol
    itu kini dicatat sebagai simbol pola yang dikenal untuk ketiga dompet. Catatan penting:
    豹拉 ukuran mikro di sini adalah observasi rotasi dan TIDAK digabung dengan Buy 豹拉
    $1,395 dompet 1 — simbol bukan CA. Buy SA adalah re-trade.
22. 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650 — dibaca 09:32. TIDAK ADA token baru yang
    terkonfirmasi; Buy DURIAN 11K $0,06 (9m/14m ago), BSIN 11K $0,06 (13m–17m ago),
    DOGE 11K $0,06 (15m ago) adalah observasi rotasi-pola $0,06 satu entitas (CA UNVERIFIED),
    TIDAK dihitung sebagai token baru mengikuti preseden run 15–17 (USDT/EURO, TSLA/USD/
    FNCY/PIVT/ANCHORAGE, GIST); DURIAN/BSIN/DOGE kini dicatat sebagai simbol rotasi yang dikenal.
23.–49. Klaster besar Tier C — dibaca 09:33–09:41. Buy SAFU berlabel 3h ago (~06:33–06:41 WIB)
    adalah PRA-JENDELA (sebelum batas 07:47 WIB) DAN SAFU sudah dikenal sejak run 16/17 untuk
    klaster ini, sehingga semuanya RE-TRADE, bukan token baru — termasuk 0xf795… yang SAFU-nya
    baru dicatat pada run 17 (kini re-trade). Buy PYRO/FAGENT, bila ada, juga re-trade
    (dikenal sejak run 11/12/16). Pengecualian bukan-Buy: Tx In BPX debu 2h ago di dompet 33
    (0xcb08…) dan 45 (0xa952…) — Tx In, BUKAN Buy, dan pra-jendela (~07:36–07:40 WIB).
    Field holdings dompet-dompet ini tidak diubah (tab Holdings tidak dibuka).
41. 0x97bd895f8123a7837368df410e7d308246c0b3e9a — dibaca 09:39. BNB 0 ($0). Activity:
    "No Data" pada halaman publik (BUKAN login-gated) — aktivitas TIDAK TERBACA pada run ini,
    TIDAK dihitung sebagai tidak membeli; field holdings tidak diubah. (Lihat koreksi kunci
    state di atas.)
50. 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36 — dibaca 09:42. BNB 0,012 ($8,88).
    Buy SIMBOL-BARU dalam jendela: YUN 2,05K $1.530 (4m ago, ~09:38 WIB, CA UNVERIFIED,
    1 entitas). Sell SENSEI 9,3B $393,7 (1m ago) adalah sell token yang sudah dikenal, bukan
    buy. Tx In BNCB +0,794 (31m ago) BUKAN Buy; Tx Out BNCB / Sell 社群人生 2h ago
    pra-jendela/sudah dikenal.

Hitungan sinyal run 18 (entitas, bukan alamat mentah; ambang 13 entitas, CA sama):
- Token simbol-baru yang terverifikasi dalam jendela (setelah 07:47 WIB): 豹拉 — 1 entitas
  (dompet 1 saja, setelah observasi rotasi mikro tidak digabung karena simbol bukan CA);
  哆啦B梦 — 1 entitas (dompet 14 saja); YUN — 1 entitas (dompet 50 saja).
- Observasi rotasi-pola (老板/茧/羊了个/MEMECOINS/STEALTH/박진혁/DOGE/DURIAN/BSIN) TIDAK
  dihitung sebagai token baru mengikuti metode dedupe run 14–17, sehingga tidak menambah
  hitungan apa pun meskipun batch-nya tampak pada 5–6 dompet sekaligus.
- TIDAK ADA token CA-sama yang dibeli oleh 13 entitas atau lebih — bahkan pada tingkat simbol
  pun token simbol-baru terbanyak hanya 1 entitas setelah dedupe dan re-trade diterapkan, dan
  CA tidak terverifikasi untuk token mana pun sehingga hitungan CA-sama tidak mungkin
  dilakukan sama sekali. Jadi TIDAK ADA SINYAL (ambang: minimal 13 entitas privat berbeda
  membeli token baru yang sama, CA sama).
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada
  runtuhan entitas. Co-buy/co-hold saja (termasuk batch rotasi yang bersamaan) TIDAK
  meruntuhkan entitas.
- Pembelian 1 wallet saja = bukan sinyal; di run ini token simbol-baru terbanyak pun hanya
  1 entitas.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-02T09:42:00+07:00; run18_summary untuk ke-50 wallet; BNB diperbarui di mana
  dilaporkan; holdings dompet 19–50 TIDAK diubah karena tab Holdings tidak dibuka).
  Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 19 — Senin 2026-11-02, 11:24–11:42 WIB (browser task runtime-measured 11:24–11:46 WIB)

- Daftar dibaca dari `tier-ab-watch.md` setiap run: 50 entitas (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi 0x81c3...). Daftar lama 23 alamat TIDAK dipakai.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow. Pemeriksaan browser live read-only ke-50 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>). Semua 50 halaman memuat data publik, status Disconnected — TIDAK ADA yang login-gated, TIDAK ADA yang Activity 'No Data'.
- Diskrepansi waktu yang dicatat jujur: laporan browser mengklaim pembacaan per-wallet 11:24–11:42 WIB, sedangkan runtime mengukur tugas browser sampai 11:46 WIB (selisih akhir 4 menit, seperti preseden run-run sebelumnya). last_checked state memakai 11:42 WIB (baca per-wallet terakhir).
- Batasan yang wajib dicatat:
  - CA token TIDAK tercatat untuk token mana pun: tidak ada CA lengkap yang terlihat di teks halaman; CA tidak ditebak dari simbol. Token dicatat berdasarkan simbol saja, sehingga hitungan CA-sama antar wallet TIDAK mungkin dari run ini.
  - Waktu aktivitas bersifat relatif terhadap waktu baca ("menit/jam lalu") seperti dilaporkan GMGN, bukan stempel waktu absolut yang diverifikasi on-chain; label relatif dicocokkan dengan jumlah/nilai transaksi sebelum dinyatakan baru, mengikuti preseden run 3–18.
  - Tab Holdings TIDAK dibuka untuk wallet 2–50 (Activity/BNB saja); field holdings di state dibiarkan tidak berubah, bukan diset kosong. Wallet 1 sempat menampilkan tab Holdings sebagai tab awal, tetapi tidak ada daftar holdings yang dilaporkan, jadi field-nya juga tidak berubah.
  - Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
- Jendela run 19: setelah last_checked run 18 (2026-11-02 09:42 WIB).
- Per-wallet (ringkas):
  - Tier A/B dormant, tanpa Buy baru: 0x13d1... (Tx In 47d lalu), 0x5b2f... (47d), 0x6ba7... (Tx In 3d, Tx Out USDT 9d), 0x7564... (34d), 0x8272... (sampai 127d, SKYAI lama), 0x93e7... (68d/126d), 0xaab8... (SKYAI 6d/7d), 0xb787... (SKYAI 13d), 0xbe59... (47d), 0xda91... (sampai 20d, mubarak lama), 0xf6a8... (12d; diskrepansi GMGN BNB 0 vs on-chain 0,02479 MASIH belum terjelaskan, tidak dicek ulang on-chain run ini).
  - 0x8e96... (dibaca 11:24, BNB 0,072 / $51,72): symbol-new Buy DASHCAT 1,5M $0,011/$0,008 (46m lalu, ~10:38 WIB, CA UNVERIFIED, 1 entitas, BUKAN sinyal); DASHCAT kini dikenal untuk wallet ini. Baris Soldier di top 10 hanya Sell (144,1K $0,602/$0,6, 31m lalu, ~10:53 WIB), tidak ada baris Buy Soldier di top 10 — tidak diklaim sebagai pembelian.
  - 0x8922... (dibaca 11:28, BNB 0 / $0,042): TERBACA LAGI (run 18 Activity 'No Data' teratasi); tanpa Buy baru — aktivitas terbaru Tx In LYX/金钱自由 3d lalu, Buy XPIN 17d lalu adalah baseline.
  - 0x2325... (dibaca 11:30, BNB 0,773 / $551,95): Buy 哆啦B梦 8,6M $40,9 berlabel 2h lalu adalah DUPLIKAT trade run 18 (jumlah/nilai identik), pra-jendela, BUKAN baru. Buy BNCB 4h lalu adalah token yang sudah dikenal sejak run 11 dan pra-jendela. Sell/Burn 4h lalu dan trade POPZERO/JAGENT矿机 11h lalu adalah dikenal/pra-jendela.
  - 0x9856... dan 0x40a8...: Buy-buy 18h lalu (鼻涕/ZAGS; NITRO/鼻涕/FORX/ZAGS) adalah dikenal, pra-jendela.
  - Klaster mikro (pola rotasi, TIDAK dihitung sebagai baru mengikuti dedupe run 14–18): 0x3628... (11:31, BNB 0,011) dan 0xa0c1... (11:32, BNB 0,025) — Buy 噜噜 1,13K $0,071, MAI 1,13K $0,071, 牛子AI 1,13K $0,071; 0xc7c5... (11:32), 0xad94... (11:33), 0x3803... (11:33) — Buy 噜噜, PEACE, 牛子AI dengan ukuran/nilai identik per wallet (1,13K $0,024 / 1,13K $0,024 / 832,25 $0,018). Simbol 噜噜/MAI/牛子AI/PEACE kini tercatat sebagai simbol pola yang dikenal untuk wallet-wallet ini. MAI hanya muncul sebagai Sell di top 10 untuk 0xc7c5.../0xad94.../0x3803..., buy-nya tidak terlihat — tidak dihitung.
  - 0x7488... (11:33, BNB 0,025): observasi rotasi satu entitas, TIDAK dihitung sebagai baru mengikuti preseden run 15–18 — Buy CARROT 1,1K $0,057 (12m lalu), BANANA 110K $0,059 (28m), LIME 110 $0,061 (45m), PEACH 11K $0,063 (1h), POMEGRANATE 110 $0,062 (1h); kelimanya kini simbol rotasi yang dikenal untuk wallet ini.
  - Klaster SAFU (27 wallet Tier C, dibaca 11:34–11:41, BNB masing-masing 0,3): Buy-buy SAFU berlabel 5h lalu (~06:34–06:41 WIB) adalah PRA-JENDELA (sebelum 09:42 WIB) dan SAFU sudah dikenal sejak run 16/17 — re-trade, BUKAN baru. Buy/sell PYRO/FAGENT 6h lalu, bila tampil, juga pra-jendela dan dikenal. 0x97bd... TERBACA LAGI (run 18 Activity 'No Data' teratasi), dengan pola SAFU/PYRO yang sama. 0xcb08... dan 0xa952...: Tx In BPX debu 4h lalu (~07:36–07:40 WIB) adalah Tx In, BUKAN Buy, dan pra-jendela.
  - 0x81c3... (11:42, BNB 0,012 / $8,88): Buy YUN 2,05K $1,530 berlabel 2h lalu adalah trade run 18 yang SAMA (jumlah/nilai identik), BUKAN baru. Sell SENSEI 2h lalu, Buy SENSEI 14h lalu, Sell 社群人生 4h lalu adalah dikenal/pra-jendela.
- Hitungan sinyal run 19 (entitas, bukan alamat mentah; ambang 13 entitas berbeda membeli token baru yang SAMA dengan CA sama):
  - TIDAK ADA SINYAL TERVERIFIKASI: CA tidak ditampilkan untuk token mana pun, sehingga hitungan CA-sama tidak mungkin.
  - Simbol-baru dalam jendela (CA UNVERIFIED, BUKAN sinyal): DASHCAT — 1 entitas (0x8e96... saja).
  - Observasi pola rotasi (TIDAK dihitung sebagai baru, CA UNVERIFIED): 噜噜 5 entitas, 牛子AI 5 entitas, PEACE 3 entitas, MAI (buy di top 10) 2 entitas, CARROT/BANANA/LIME/PEACH/POMEGRANATE masing-masing 1 entitas. Sekalipun observasi pola ini dihitung mentah, maksimum 5 entitas < 13 — kesimpulan tidak berubah.
  - Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada runtuhan entitas. Co-buy/co-hold saja (termasuk batch mikro yang identik) TIDAK meruntuhkan entitas. Pendanaan dari exchange tidak dihitung sebagai keterkaitan.
  - Pembelian 1 wallet saja = bukan sinyal; di run ini satu-satunya simbol-baru non-pola pun hanya 1 entitas.
- Koreksi state run 19: kunci state lama untuk 0x97bd... membawa satu 'a' ekstra di akhir (0x97bd...b3e9a); diperbaiki ke alamat file tier 0x97bd...b3e9 dengan riwayat sebelumnya dipertahankan — jumlah wallet tetap 50.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-02T11:42:00+07:00; ringkasan run19 per wallet; BNB per wallet). SENYAP ke chat sesuai aturan; tidak ada promosi terpercaya yang terpenuhi run ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 20 — Senin 2026-11-02, 13:22 WIB (gap: laporan browser belum diterima saat penulisan)

- Daftar dibaca dari `tier-ab-watch.md` setiap run: 50 entitas (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi 0x81c3...). Daftar lama 23 alamat TIDAK dipakai. Ambang sinyal: minimal 13 entitas berbeda membeli token baru yang sama (CA sama), sesuai skala >25% di file.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-50 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>)
  DIDISPATCH (task browser-task:d538d8c5-e13e-5374-928c-549d83758042) pada 13:22 WIB, dengan
  instruksi eksplisit: bila login-gated, catat saja dan lanjut, JANGAN klik login. Jendela yang
  dicari: trade setelah last_checked run 19 (2026-11-02T11:42:00+07:00).
- GAP YANG DICATAT JUJUR, mengikuti preseden run-run sebelumnya:
  - Laporan per-wallet terperinci (aktivitas terbaru per wallet) dari browser BELUM terkirim
    ke konteks run ini pada saat penulisan log.
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim (ambang 13 entitas, CA sama) — bukan karena wallet terbukti
    tidak membeli, melainkan karena bukti per-wallet belum diterima. Wallet yang tidak terbaca
    datanya TIDAK dianggap tidak membeli, sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline / state run 19 TIDAK diubah kecuali field `last_attempt` sebagai penanda run ini:
    last_checked tetap 2026-11-02T11:42:00+07:00 dan holdings per wallet tetap dari run 19,
    sampai laporan browser run ini benar-benar diterima.
- Tindak lanjut: bila laporan browser run ini tiba, tambahkan sebagai adendum run ini dengan
  stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs baseline run 19
  (termasuk dedupe rotasi-pola run 14–19 dan re-trade token yang sudah dikenal). Bila tidak tiba,
  run berikutnya harus mengulang pembacaan ke-50 wallet.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Adendum Run 20 — laporan browser diterima, pemeriksaan terukur 13:24–13:38 WIB (runtime 13:24–13:41 WIB)

Pemeriksaan browser read-only ke-50 halaman GMGN BSC, tanpa login, tanpa klik Log in/Sign
up/Connect, tanpa sign/transaksi. Semua 50 halaman memuat data publik — TIDAK ADA yang
login-gated, TIDAK ADA yang Activity 'No Data'. Diskrepansi waktu yang dicatat jujur:
laporan browser mengklaim pembacaan per-wallet 13:24–13:38 WIB (dompet 1 dibaca pertama
13:24 WIB, diverifikasi ulang 13:38 WIB), sedangkan runtime mengukur tugas browser sampai
13:41 WIB (selisih akhir 3 menit, seperti preseden run-run sebelumnya). last_checked state
memakai 13:38 WIB (baca per-wallet terakhir). Koreksi atas bagian "GAP" run 20 di atas:
bukti per-wallet AKHIRNYA diterima, sehingga hitungan sinyal run 20 dapat ditetapkan dari
laporan ini dan state diperbarui dari laporan ini (last_checked 2026-11-02T13:38:00+07:00).
Batasan laporan yang wajib dicatat:
- Contract address TIDAK tercatat untuk token mana pun: tidak ada alamat kontrak lengkap yang
  tampil di teks halaman; CA tidak ditebak dari simbol. Token dicatat berdasarkan simbol saja,
  dan karena itu hitungan CA-sama antar wallet TIDAK mungkin dari run ini.
- Waktu aktivitas bersifat relatif terhadap waktu baca ("menit/jam lalu") seperti dilaporkan
  GMGN, bukan stempel waktu absolut yang diverifikasi on-chain; label relatif dicocokkan
  dengan jumlah/nilai transaksi sebelum dinyatakan baru, mengikuti preseden run 3–19. Label
  "2h ago" pada dompet 1 bersifat kasar dan berada di zona batas 11:42 WIB, sehingga buy-buy
  berlabel itu TIDAK dihitung sebagai baru dalam jendela (lihat di bawah).
- Tab Holdings TIDAK dibuka untuk dompet 2–50 (Activity/BNB saja); field holdings di state
  dibiarkan tidak berubah, bukan diset kosong. Dompet 1 sempat menampilkan tab Holdings sebagai
  tab awal, tetapi tidak ada daftar holdings yang dilaporkan, jadi field-nya juga tidak berubah.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

Per-wallet (ringkas; urutan sesuai tier-ab-watch.md; jendela = setelah 11:42 WIB 2026-11-02;
detail penuh ada di run20_summary tiap wallet di state):
- Tier A/B dormant, tanpa Buy baru: 0x13d1... (Tx In 47d lalu), 0x5b2f... (47d), 0x6ba7...
  (Tx In 3d, Tx Out USDT 9d), 0x7564... (34d), 0x8272... (sampai 127d, SKYAI lama), 0x93e7...
  (68d/126d), 0xaab8... (SKYAI 7d), 0xb787... (SKYAI 14d), 0xbe59... (47d), 0xda91... (sampai
  20d, mubarak lama), 0xf6a8... (12d; diskrepansi GMGN BNB 0 vs on-chain 0,02479 MASIH belum
  terjelaskan, tidak dicek ulang on-chain run ini).
- 0x8922... (13:26, BNB 0 / $0,041): tanpa Buy baru — Tx In LYX/金钱自由 3d lalu, Buy XPIN
  17–19d lalu adalah baseline.
- 0x8e96... (dibaca ulang 13:38, BNB 0,067 / $47,25): symbol-new Buy dalam jendela — 괴렘
  195,2K $1,389 (42m lalu, ~12:56 WIB), SA 195,3K $1,392 (1h lalu, ~12:38 WIB), 金将军 169,6K
  $1,381 (1h lalu, ~12:38 WIB) — masing-masing CA UNVERIFIED, 1 entitas, BUKAN sinyal.
  Buy-buy berlabel 2h lalu (哈基米机 150,2K $1,393; 噜噜 163,1K $1,396; Soldier 144,1K
  $1,414) menunjuk sekitar 11:38 WIB, di zona batas/pra-jendela, sehingga TIDAK dihitung
  sebagai baru dalam jendela; Soldier di run 19 hanya muncul sebagai Sell.
  괴렘/SA/金将军 kini dikenal untuk wallet ini. 괴렘/SA/金将军 di sini TIDAK digabung dengan
  trade mikro bersimbol sama — simbol bukan CA.
- 0x2325... (13:27, BNB 0,84 / $595,07, naik dari 0,773 run 19): symbol-new Buy 金将军 10,8M
  $68,49 (1h lalu, ~12:27 WIB, CA UNVERIFIED, 1 entitas, BUKAN sinyal, TIDAK digabung dengan
  Buy 金将军 dompet 1 — simbol bukan CA, ukuran berbeda). Buy 哆啦B梦 4h lalu adalah trade
  run 18 yang dikenal dan pra-jendela. Sell/Burn BDOG 1h lalu dan Sell/Burn 币安狗 6h lalu
  bukan Buy. 金将军 kini dikenal untuk wallet ini.
- 0x9856... dan 0x40a8...: Buy-buy 20h lalu (鼻涕/ZAGS; NITRO/鼻涕/FORX/ZAGS) adalah dikenal,
  pra-jendela.
- Klaster mikro (pola rotasi, TIDAK dihitung sebagai baru mengikuti dedupe run 14–19):
  0x3628... (13:28, BNB 0,01) dan 0xa0c1... (13:28, BNB 0,025) — Buy 词元 1,13K $0,07,
  괴렘 1,13K $0,07, 0agent 1,13K $0,07; 0xc7c5... (13:29), 0xad94... (13:29), 0x3803...
  (13:29) — Buy HODL, 0agent, faucet, 괴렘, OKCAT dengan ukuran/nilai identik per wallet
  (1,13K $0,024 / 1,13K $0,024 / 832,25 $0,018), plus 词元 untuk 0x3803.... Simbol
  词元/괴렘/0agent/HODL/faucet/OKCAT kini tercatat sebagai simbol pola yang dikenal untuk
  wallet-wallet ini. OKCAT untuk 0x3803... hanya muncul sebagai Sell di top 10, buy-nya
  tidak terlihat — tidak dihitung.
- 0x7488... (13:30, BNB 0,026): observasi rotasi satu entitas, TIDAK dihitung sebagai baru
  mengikuti preseden run 15–19 — Buy BLUEBERRY 110 $0,056 (11m lalu), GRAPEFRUIT 11K
  $0,061 (27m), ROMANESCO 1,1K $0,055 (44m), STRAWBERRY 110 $0,056 (1h), WALNUT 11K $0,06
  (1h); kelimanya kini simbol rotasi yang dikenal untuk wallet ini.
- Klaster besar Tier C, dompet 23–49 (dibaca 13:30–13:38, BNB masing-masing sekitar 0,3
  kecuali 0xdb2d... 0,299; 0xc621... 0,184; 0xf795... 0,426; 0x9cdd... 0,184; 0x2cc8...
  0,277; 0xc0c8... 0,288; 0xfdec... 0,356; 0x64e8... 0,271): Buy-buy 我靠 dalam jendela
  pada SELURUH 27 dompet ini (ukuran khas ~$190 untuk buy besar, plus buy-buy kecil
  $0,02–$30 pada beberapa dompet; contoh: 0xdb2d... 11,6M $191,4 11m lalu; 0xc621...
  9,9M $203,5 10m lalu; 0xf795... 11,3M $189,5 11m lalu). 我靠 sebelumnya TIDAK PERNAH
  tercatat di state pemantau ini (0 kemunculan sebelum run 20), sehingga secara simbol
  ini adalah token baru bagi ke-27 dompet tersebut. NAMUN CA-nya TIDAK terverifikasi untuk
  token mana pun, sehingga observasi ini TIDAK BOLEH dibaca sebagai sinyal (lihat hitungan
  di bawah). SAFU Buy dalam jendela untuk 0xf795... (7,8M $325,5), 0x3154... (419K
  $21,44), 0x5b4b... (5M $192,6), dan 0x1cce... (412,2K $15,03) adalah RE-TRADE (SAFU
  dikenal sejak run 16/17), bukan baru. SAFU untuk 0x3a39.../0xcb08.../0x64e8... hanya
  muncul sebagai Sell di top 10, buy-nya tidak dihitung.
- 0x81c3... (13:38, BNB 0,012 / $8,41): symbol-new Buy dalam jendela — 0agent 5,6M $483,6
  (1m lalu, ~13:37 WIB), SNOWBALL 5,3B $193,4 (5m lalu) + 10,5B $483,5 (14m lalu), RFP
  4,75K $1,8K (1h lalu, ~12:38 WIB, lalu Sell jumlah yang sama 1h lalu) — masing-masing
  CA UNVERIFIED, 1 entitas, BUKAN sinyal. 0agent di sini TIDAK digabung dengan trade
  0agent mikro klaster — simbol bukan CA, ukuran berbeda jauh. Sell YUN 1h lalu adalah
  sell token yang dikenal, bukan buy; Sell SENSEI 3h lalu adalah dikenal/pra-jendela.
  0agent/SNOWBALL/RFP kini dikenal untuk wallet ini.

Hitungan sinyal run 20 (entitas, bukan alamat mentah; ambang 13 entitas berbeda membeli
token baru yang SAMA dengan CA sama):
- TIDAK ADA SINYAL TERVERIFIKASI: CA tidak ditampilkan untuk token mana pun, sehingga
  hitungan CA-sama tidak mungkin dilakukan sama sekali.
- OBSERVASI SIMBOL WAJIB TINDAK LANJUT (BUKAN sinyal, preseden yang sama seperti observasi
  simbol SAFU 26 entitas pada run 16, TART 26 entitas pada run 12, dan SATO 27 entitas pada
  run 14, yang semuanya dicatat BUKAN sinyal): 我靠 — simbol-baru untuk 27 entitas Tier C
  dalam jendela run 20. Angka mentah simbol 27 MELEBIHI ambang 13, tetapi karena simbol
  bukan CA dan CA tidak terverifikasi, angka itu TIDAK BOLEH dibaca sebagai sinyal, tidak
  memicu screening paper, tidak menjadi rekomendasi beli, tidak menjadi promosi, dan tidak
  menjadi pemicu trade. Bila pada run berikutnya CA 我靠 terverifikasi sama antar wallet,
  hitungan itu harus dihitung ulang dari data run ini; sampai saat itu, tidak ada pemicu
  apa pun dari observasi ini.
- Simbol-baru lain dalam jendela (CA UNVERIFIED, BUKAN sinyal): 괴렘 — 1 entitas non-pola
  (dompet 1; trade mikro klaster tidak digabung); SA — 1 entitas (dompet 1); 金将军 —
  2 entitas pada tingkat simbol mentah (dompet 1 + dompet 14) tetapi TIDAK digabung sebagai
  CA-sama karena CA tidak terverifikasi; 0agent — 1 entitas non-pola (dompet 50; trade
  mikro klaster tidak digabung); SNOWBALL — 1 entitas (dompet 50); RFP — 1 entitas
  (dompet 50).
- Observasi pola rotasi (TIDAK dihitung sebagai baru, CA UNVERIFIED): 词元 3 entitas,
  괴렘 mikro 5 entitas, 0agent mikro 5 entitas, HODL 3 entitas, faucet 3 entitas, OKCAT
  2 entitas, BLUEBERRY/GRAPEFRUIT/ROMANESCO/STRAWBERRY/WALNUT masing-masing 1 entitas.
  Sekalipun observasi pola ini dihitung mentah (di luar 我靠), maksimumnya 5 entitas < 13 —
  kesimpulan untuk kategori pola tidak berubah.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau (laporan ini
  tidak memuat data pendanaan; co-buy saja, termasuk Buy 我靠 serentak pada 27 dompet,
  TIDAK meruntuhkan entitas), jadi tidak ada runtuhan entitas. Ambang absolut tetap 13.
- Pembelian 1 wallet saja = bukan sinyal; di run ini satu-satunya observasi di atas ambang
  adalah observasi simbol 我靠 yang gagal syarat CA-sama.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-02T13:38:00+07:00;
  ringkasan run20 per wallet; BNB per wallet). SENYAP ke chat sesuai aturan; tidak ada
  promosi terpercaya yang terpenuhi run ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 21 — Senin 2026-11-02, 15:22 WIB (gap: laporan browser belum diterima saat penulisan)

- Daftar dibaca dari `tier-ab-watch.md`: 50 entitas terpantau (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 1). Daftar lama 23 alamat TIDAK dipakai. Ambang sinyal: minimal 13 entitas berbeda membeli token baru yang SAMA (CA sama).
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-50 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>)
  DIDISPATCH (task browser-task:1a8e8d71-1781-5061-80e9-f71d7138bea7) pada ~15:23 WIB, dengan
  instruksi eksplisit: bila login-gated, catat saja dan lanjut, JANGAN klik login; CA hanya
  dicatat bila benar-benar terlihat, tidak ditebak dari simbol. Jendela run: pembelian setelah
  13:38 WIB 2026-11-02 (last_checked run 20).
- GAP YANG DICATAT JUJUR, mengikuti preseden Run 1/3/4/5/6:
  - Laporan per-wallet terperinci (holdings + trade terbaru per wallet) dari browser BELUM
    terkirim ke konteks run ini pada saat penulisan log.
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim (ambang: minimal 13 entitas) — bukan karena wallet terbukti
    tidak membeli, melainkan karena bukti per-wallet belum diterima. Wallet yang tidak terbaca
    datanya TIDAK dianggap tidak membeli, sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline / state run 20 TIDAK diubah: last_checked tetap 2026-11-02T13:38:00+07:00 dan holdings
    per wallet tetap dari run 20, sampai laporan browser run ini benar-benar diterima. Hanya field
    `last_attempt` di state yang diperbarui sebagai penanda run ini.
  - Catatan untuk perhitungan saat laporan tiba: pembelian 我靠 oleh 27 wallet Tier C di run 20
    sudah tercatat sebagai diketahui (known) bagi wallet-wallet itu, jadi pengulangan 我靠 di run 21
    adalah re-trade, bukan token baru; observasi simbol 我靠 run 20 tetap BUKAN sinyal karena CA
    tidak terverifikasi (simbol bukan CA).
- Tindak lanjut: bila laporan browser run ini tiba belakangan, tambahkan sebagai adendum run ini
  dengan stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs baseline
  run 20. Bila tidak tiba, run berikutnya harus mengulang pembacaan ke-50 wallet.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Adendum Run 21 — laporan browser diterima ~16:00 WIB

Pemeriksaan browser terukur runtime 15:24–16:00 WIB (laporan per-wallet 15:24–15:56 WIB;
selisih akhir 4 menit dicatat seperti pada run-run sebelumnya, bukan klaim di dalam laporan).
Semua 50 halaman memuat data publik TANPA login-gated, status Disconnected, tanpa klik
Log in/Sign up/Connect, tanpa sign/transaksi. Koreksi atas bagian "GAP" di atas: bukti
per-wallet AKHIRNYA diterima, sehingga hitungan sinyal run 21 dapat ditetapkan dari laporan
ini dan state diperbarui dari laporan ini (last_checked 2026-11-02T15:56:00+07:00).
Batasan laporan yang wajib dicatat:
- Tab Holdings memakai filter default GMGN: "No assets held." = sesuai tampilan tab itu,
  BUKAN klaim saldo on-chain nol; token yang hanya diterima lewat Tx In tersaring dari Holdings.
- Contract address TIDAK tercatat pada run ini untuk token mana pun: tidak ada alamat kontrak
  lengkap yang terlihat dalam teks halaman; CA tidak ditebak dari simbol. Token dicatat
  berdasarkan simbol saja, dan karena itu tidak dapat dipakai sebagai CA terverifikasi untuk
  perbandingan antar wallet — hitungan di bawah memakai simbol + konteks baseline run 20.
- Waktu aktivitas bersifat relatif terhadap waktu baca ("menit/jam lalu") seperti dilaporkan
  GMGN, bukan stempel waktu absolut yang diverifikasi on-chain; label "2h ago" bersifat
  borderline terhadap batas 13:38 WIB dan TIDAK dihitung sebagai terverifikasi dalam jendela.
- Satu gangguan teknis: navigasi ke wallet 38 (0x3623…) gagal dua kali 15:43–15:48 WIB,
  pulih setelah jeda 30 detik; halaman wallet 37 tidak berubah selama kegagalan itu, tidak ada
  transaksi yang dilakukan.

Per-wallet (ringkas; urutan sesuai tier-ab-watch.md):
1. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — dibaca ~15:24 WIB. BNB 0,067 ($47,21).
   Symbol-new Buy 剑来 184,6K $1,374 (1h lalu, ~14:24 WIB, CA UNVERIFIED, 1 entitas),
   lalu Sell 剑来 jumlah yang sama $1,454 (20m lalu); 剑来 kini diketahui bagi wallet ini.
   AMBIGU, TIDAK DIHITUNG sebagai baru: baris aktivitas berlabel 怪兽 163,1K $0,81 dan
   195,2K $0,809 (1h lalu) memiliki jumlah/nilai yang persis sama dengan holdings yang
   diketahui 噜噜 163,1K dan 괴렘 195,2K — simbol tidak konsisten dengan baris holdings,
   jadi tidak diklaim sebagai token baru; wajib diklarifikasi pada run berikutnya.
   Buy 金将军 3–4h lalu adalah token yang diketahui (run 20) / pra-jendela.
2.–6., 8., 10.–13. (0x13d1…, 0x5b2f…, 0x6ba7…, 0x7564…, 0x8272…, 0x93e7…, 0xb787…,
   0xbe59…, 0xda91…, 0xf6a8…): TIDAK ADA buy baru. Aktivitas terbaru hanya Tx In/Tx Out lama
   (termasuk SKYAI dan mubarak sebagai holding/transfer lama, bukan buy baru). Khusus wallet 13
   (0xf6a8…): GMGN pada ~15:31 WIB MASIH menunjukkan BNB 0 ($0) — diskrepansi GMGN-vs-on-chain
   (on-chain 0,02479 BNB) MASIH belum terjelaskan, tidak dicek ulang on-chain pada run ini.
7. 0x892200223bdfb11d2506c5ab1cae9222ce253acc — BNB 0 ($0,041). Holdings tampil: XPIN,
   WKC, XRP, SLX, BANK, SKYAI, CREPE. Buy terbaru 17–19 hari lalu (XPIN/XRP) — baseline,
   bukan buy baru. TIDAK ADA buy baru.
9. 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e — Activity menunjukkan "No Data" pada halaman
   publik (BUKAN login-gated) — aktivitas tidak terbaca pada run ini, TIDAK dihitung sebagai
   tidak membeli; holdings "No assets held." dilaporkan.
14. 0x2325f175975abdbcde555c79cc8e63381d28551b — dibaca ~15:31 WIB. BNB 0,903 ($641,27),
   naik dari 0,84 pada run 20. Symbol-new Buy SWARM 4,7B $69,32 (1h lalu, ~14:31 WIB,
   CA UNVERIFIED, 1 entitas, TIDAK digabung dengan SWARM wallet 50 — simbol bukan CA);
   SWARM kini diketahui bagi wallet ini. Buy BNCB 0,497 $2,531 adalah token yang SUDAH
   diketahui dipegang sejak run 11, BUKAN baru. Buy 币安狗 2h lalu bersifat borderline /
   pra-jendela (~13:31 WIB) dan token yang diketahui, TIDAK dihitung terverifikasi dalam
   jendela. Buy 金将军 3h lalu diketahui (run 20) / pra-jendela. Holdings: BNCB $2,22 / 0,434,
   哆啦B梦 $45,96 / 8,6M, PTG $93,55 / 34,29, sisanya $0.
15. 0x9856bac497634a62a970233bc4b0f5bb52c844c1 — Buy-buy 22h lalu (鼻涕, ZAGS) diketahui,
   pra-jendela. TIDAK ADA buy baru.
16.–17. (0x3628…, 0xa0c1…): Buys RAM / 眉眉 / 安 / 食蟹猴 1,13K $0,07 adalah observasi rotasi
   pola simbol saja (CA UNVERIFIED, batch yang sama), TIDAK dihitung sebagai baru mengikuti
   dedupe run 14–20; simbol-simbol itu kini tercatat sebagai simbol pola yang diketahui bagi
   kedua wallet. 我靠 di bawah 15 teratas, 3h lalu, pra-jendela. BNB: wallet 16 0,012 ($8,18);
   wallet 17 0,025 ($17,94).
18. 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c — Buy-buy 22h lalu (NITRO, 鼻涕, FORX, ZAGS)
   diketahui, pra-jendela. TIDAK ADA buy baru.
19.–21. (0xc7c5…, 0xad94…, 0x3803…): Buys PMUP / dih / WWIII / OS / Warcoin / 眉眉
   1,13K $0,024 (wallet 19–20) dan 832,25 $0,018 (wallet 21) adalah observasi rotasi pola simbol
   saja (CA UNVERIFIED, batch yang sama), TIDAK dihitung sebagai baru mengikuti dedupe run
   14–20; simbol-simbol itu kini tercatat sebagai simbol pola yang diketahui. 我靠 $0 terjual
   habis 3h lalu, pra-jendela. BNB: wallet 19 0,01 ($6,88); wallet 20 0,054 ($38,50);
   wallet 21 0,025 ($17,84).
22. 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650 — TIDAK ADA token baru yang terkonfirmasi;
   Buys GARLIC / GINGER / MANGO / CACTUS / JACKFRUIT / KIWI / QUINCE / CHILI $0,056–$0,063
   adalah observasi rotasi pola satu entitas (CA UNVERIFIED), TIDAK dihitung sebagai baru
   mengikuti preseden run 15–20; simbol-simbol itu kini tercatat sebagai simbol rotasi yang
   diketahui. BNB 0,026 ($18,28).
23.–49. (seluruh wallet Tier C 我靠): Buy-buy 我靠 dalam jendela SEMUANYA re-trade
   (diketahui sejak run 20), BUKAN token baru, BUKAN sinyal. Catatan per wallet: wallet 28
   juga memiliki Tx In 凤凰链 +143 $0,05 (bukan Buy); wallet 33 BNB turun tajam menjadi
   0,029 ($20,79) dari kisaran 0,3 — dicatat saja, TIDAK diklaim sebagai pembelian tertentu;
   wallet 34 BNB 0,067 ($47,48) dengan holding 我靠 $227,58 / 9M; wallet 38 BNB 0,397 ($282,45)
   setelah gangguan navigasi di atas; wallet 40 BNB 0,188 ($133,89); wallet 31/35/37/42
   masing-masing memegang sisa 我靠 kecil ($1,45–$40,23). Wallet lainnya BNB ~0,3 ($201–$214).
50. 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36 — dibaca ~15:56 WIB. BNB 0,011 ($8,14).
   Buy SNOWBALL 1,9B $290,2 (12m lalu) dan 3,6B $483,6 (58m lalu) adalah RE-TRADE
   (diketahui sejak run 20), BUKAN baru. Buy 0agent 5,6M $483,6 berlabel 2h lalu bersifat
   borderline / pra-jendela dan diketahui (run 20), TIDAK dihitung terverifikasi dalam jendela.
   Sell ALOY / RFP bukan buy. Holdings: SNOWBALL $1,06K / 5,5B, 分红BNCB股票 $1,24K / 9,7M.

Hitungan sinyal run 21 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 21 (setelah 13:38 WIB), di luar rotasi mikro
  dan di luar 我靠: 剑来 (wallet 1 saja, 1 entitas) dan SWARM (wallet 14 saja, 1 entitas).
  Keduanya CA UNVERIFIED (simbol saja), dan tidak ada token yang dibeli 2 wallet atau lebih
  dalam jendela ini, apalagi 13.
- Jadi TIDAK ADA SINYAL (ambang: minimal 13 entitas berbeda membeli token baru yang SAMA
  dengan CA yang sama).
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada
  runtuhan entitas. Co-buy/co-hold saja (termasuk klaster 我靠 dan batch rotasi mikro) TIDAK
  meruntuhkan entitas. Laporan ini tidak memuat data pendanaan, jadi tidak ada runtuhan yang
  dapat diverifikasi dari run ini.
- Pembelian 1 wallet saja = bukan sinyal, hanya dicatat di atas. Tidak ada pemicu screening
  paper, rekomendasi beli, promosi, atau pemicu trade dari run ini.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-02T15:56:00+07:00; ringkasan run 21 per wallet; 剑来 dan SWARM kini diketahui bagi
  wallet masing-masing; simbol rotasi baru tercatat sebagai simbol pola yang diketahui).
  Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 22 — 2026-11-02 17:24–18:12 WIB (PARSIAL, login-gated)

Jendela run: pembelian setelah ~16:00 WIB (akhir run 21). Tugas browser runtime-measured
17:24–18:12 WIB. TIDAK ADA login, connect wallet, sign, beli/jual/follow, atau trade.
Hanya 5 dari 50 halaman GMGN BSC yang tampil publik (17:24–17:26 WIB, status Disconnected).
Sejak ~17:27 WIB semua halaman dompet berikutnya hanya menampilkan beranda GMGN dengan panel
"You are not logged in to GMGN" — tanpa header dompet, saldo profil, maupun tab Activity.
Upaya pemulihan tanpa login yang sudah dicoba: navigasi langsung, muat ulang berulang, tab baru,
pencarian internal GMGN, jeda 30 detik–5 menit, pergantian lingkungan browser, dan dua agen
bot-challenge (17:34–17:51 WIB dan 18:00–18:04 WIB); agen kedua menyimpulkan halaman dompet
kini login-gated. Satu render sesaat tanpa login atas dompet 1 sekitar 17:40 WIB ("Bal 0 BNB")
kembali ke beranda sebelum Activity sempat dibaca dan TIDAK dipakai (bertentangan dengan
pembacaan 17:24 WIB).

Per dompet yang TERBACA:
1. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — dibaca 17:24 WIB. BNB 0,068 ($47,82),
   naik dari 0,067 pada run 21. Symbol-new Buy memes 161,7K $1,407 (1h lalu, ~16:24 WIB,
   DALAM jendela, CA UNVERIFIED, 1 entitas, BUKAN sinyal); memes kini diketahui bagi wallet ini.
   PERHATIAN: Sell memes 161,7K $2,205 juga berlabel 1h lalu dalam jam yang sama, jadi urutan
   buy/sell dalam jam itu tidak dapat dipastikan dari label relatif saja. Buy-buy lain diketahui /
   pra-jendela: 剑来 3h lalu (diketahui run 21); 괴렘/SA/金将军/哈基米机/噜噜/Soldier 4–6h lalu
   (perdagangan run 20/21 yang diketahui). Tidak ada CA yang ditampilkan halaman untuk token
   mana pun; simbol bukan CA.
2. 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02 — dibaca 17:25 WIB. BNB 0 ($0,008).
   Activity hanya Tx In (14 baris, terbaru 47d lalu). TIDAK ADA buy baru.
3. 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5 — dibaca 17:25 WIB. BNB 0 ($0,014).
   Activity hanya Tx In (13 baris, terbaru 47d lalu, termasuk SKYAI holding lama 168d lalu).
   TIDAK ADA buy baru.
4. 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7 — dibaca 17:26 WIB. BNB 0,001 ($1,05).
   Activity hanya Tx In (2 baris, terbaru 4d lalu). TIDAK ADA buy baru.
5. 0x75642756e4ba4cc8fbe76df2239cada046cfc854 — dibaca 17:26 WIB, dikonfirmasi ulang 17:29 WIB.
   BNB 0 ($0,03). Activity hanya Tx In lama (terbaru 35d lalu, termasuk SKYAI holding lama).
   TIDAK ADA buy baru. Entri Tx In airdrop yang dibagi dengan dompet 2/3 adalah co-receipt saja,
   BUKAN keterkaitan KUAT, tidak meruntuhkan entitas.

Per dompet LOGIN-GATED (45 dompet — Activity TIDAK terbaca, BUKAN "tidak ada buy",
BUKAN "No Data", dan TIDAK ada upaya login; saldo/holding tidak diubah di state):
6. 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a — 18:05 WIB (juga gagal 17:27–17:31 WIB)
7. 0x892200223bdfb11d2506c5ab1cae9222ce253acc — 18:05 WIB (juga gagal 17:31–17:32 WIB)
8. 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c — 18:06 WIB (juga gagal 17:32 WIB)
9. 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e — 18:06 WIB
10. 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462 — 18:07 WIB
11. 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf — 18:07 WIB
12. 0xda91cefe240175e6fab56271110427a4195ab71f — 18:07 WIB
13. 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc — 18:07 WIB
14. 0x2325f175975abdbcde555c79cc8e63381d28551b — 18:00–18:04 WIB; cuplikan pencarian GMGN
    "Bal 0,677" TIDAK dipakai sebagai saldo profil/bukti buy.
15. 0x9856bac497634a62a970233bc4b0f5bb52c844c1 — 18:07 WIB
16. 0x3628764a6576b8dfb31fba0aac6a333b64851423 — 18:08 WIB
17. 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e — 18:08 WIB
18. 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c — 18:08 WIB
19. 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74 — 18:08 WIB
20. 0xad94ee77d0e868d299fb3e92b9d67560257f656d — 18:08 WIB
21. 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a — 18:08 WIB
22. 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650 — 18:08 WIB
23. 0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b — 18:08 WIB
24. 0xc621946845d0fd5d1dbc6d6beb3e22aed39d7050 — 18:09 WIB
25. 0xf795c5250f3d4006283a0d0dbb378dc0e69df923 — 18:09 WIB
26. 0x9cdd08f30188c2732cdbcac8eebf4e6e8bf0c1b2 — 18:09 WIB
27. 0xaa49e7fec503664a39598645c7a3fbfa0374380d — 18:09 WIB
28. 0x82c6085f9ec2722fd6c8fc47577368a156a25b9b — 18:09 WIB
29. 0x3154f6949285ee7ac1593bd2bdf974adb6731c32 — 18:09 WIB
30. 0xca4e67bb5737c095bd3a80f79ecc6607e5723f1a — 18:09 WIB
31. 0xe9ed24db105a6b15f880025ed9ad024c06783895 — 18:09 WIB
32. 0x3a39aa05b149141a4bfc7d73611dceb0557b39c4 — 18:09 WIB
33. 0xcb08c02c0a386a10773a2c6589e7089a3dd5aca3 — 18:10 WIB
34. 0xb940e4cd40ea9e887cbc92879062676e2bc4a924 — 18:10 WIB
35. 0x4522e661d9c94ec54b37e71896351a7440ec4f07 — 18:10 WIB
36. 0x5b4beded36c1ea380abe8c6a6a0c4408f38e5024 — 18:10 WIB
37. 0xc6591fde9b44aa081062c9fc6ee48e443d24ef57 — 18:10 WIB
38. 0x362396125a55d932a09f0a5182140cbbcaf30b70 — 18:10 WIB
39. 0xf9689b9d0a675ff9ad876f1d766fb460dbde7d20 — 18:10 WIB
40. 0x2cc8192fc62e3640de91e75582cf3dbbd571b970 — 18:10 WIB
41. 0x97bd895f8123a7837368df410e7d308246c0b3e9 — 18:10 WIB
42. 0x1cce4ec5a7c5e8cfc8dedd771876c61e60b8b645 — 18:10 WIB
43. 0xc0c84518ced6a61d2a4f4a50bc0f438e0cb1031b — 18:10 WIB
44. 0xc194efe22e874a3fe666b5de5a8fd369f12c32d5 — 18:10 WIB
45. 0xa952331ea48ea9c00c4608d8259c186021331f31 — 18:11 WIB
46. 0x92bc32975b0fbf1a19caf7cc6e3f9ea4092fd314 — 18:11 WIB
47. 0x9b519f5d52cdd03e4b10484829bc137eef1f8c1a — 18:11 WIB
48. 0xfdec62fde1f1dc56c0ba5e50f4cae5d6c63762bf — 18:11 WIB
49. 0x64e893a4c5c930b2cc68b054792cbc66344aeb9a — 18:11 WIB
50. 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36 — 18:11 WIB; re-trade SNOWBALL/0agent yang
    diketahui tidak dapat dikonfirmasi dari halaman yang login-gated ini.

Hitungan sinyal run 22 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 22 (setelah 16:00 WIB): memes
  (wallet 1 saja, 1 entitas, CA UNVERIFIED). Tidak ada token yang dibeli 2 wallet atau lebih
  dalam jendela ini, apalagi 13.
- Jadi TIDAK ADA SINYAL (ambang: minimal 13 entitas berbeda membeli token baru yang SAMA
  dengan CA yang sama). 45 dompet yang login-gated TIDAK dapat mengonfirmasi maupun
  menyingkirkan buy dalam jendela — buy mereka pada jendela ini TIDAK DIKETAHUI, bukan nol.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada
  runtuhan entitas. Laporan ini tidak memuat data pendanaan; co-buy/co-hold saja TIDAK
  meruntuhkan entitas.
- Pembelian 1 wallet saja = bukan sinyal, hanya dicatat di atas. Tidak ada pemicu screening
  paper, rekomendasi beli, promosi, atau pemicu trade dari run ini.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-02T18:12:00+07:00; ringkasan run 22 per wallet; memes kini diketahui bagi wallet 1;
  45 dompet dicatat login-gated dengan field saldo/holding tidak diubah).
  Baseline baru = state ini, dengan catatan jendela 45 dompet yang login-gated belum terbaca.
- Blokir yang tersisa: halaman dompet GMGN login-gated sejak ~17:27 WIB. Penyelesaian butuh
  sign-in GMGN (di luar kewenangan baca-saja run ini — run ini TIDAK mencoba login) atau
  menunggu GMGN kembali menampilkan halaman publik tanpa login lalu membaca ulang 45 dompet itu.
  Diskrepansi BNB GMGN vs on-chain untuk 0xf6a8... tetap TIDAK TERSELESAIKAN, tidak dicek
  ulang (dompet login-gated pada run ini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 23 — 2026-11-02 19:23–19:29 WIB (FULLY LOGIN-GATED, tanpa data publik)

Jendela run: pembelian setelah 18:12 WIB (akhir run 22). Tugas browser runtime-measured
19:23–19:29 WIB (laporan per-wallet 19:23–19:28 WIB). TIDAK ADA login, connect wallet, sign,
beli/jual/follow, atau trade. TIDAK ADA tantangan bot (CAPTCHA) yang dilaporkan; penghalangnya
adalah panel login GMGN itu sendiri.

Hasil: 0 dari 50 halaman GMGN BSC memuat data dompet publik. Setiap URL
https://gmgn.ai/bsc/address/<alamat> hanya menampilkan beranda GMGN dengan panel
"You are not logged in to GMGN" — tanpa header dompet, saldo BNB, maupun tab Holdings/Activity.
Ini BERBEDA dari run 22 yang masih sempat membaca 5 dompet pada 17:24–17:26 WIB sebelum gate
menutup; pada run 23 ini gate sudah menutup untuk semua dompet sejak dompet pertama.

Per dompet LOGIN-GATED (50 dompet — Activity TIDAK terbaca, BUKAN "tidak ada buy",
BUKAN "No Data", dan TIDAK ada upaya login; saldo/holding tidak diubah di state):
- 19:23 WIB: 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6, 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02, 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5
- 19:24 WIB: 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7, 0x75642756e4ba4cc8fbe76df2239cada046cfc854, 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a, 0x892200223bdfb11d2506c5ab1cae9222ce253acc, 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c, 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e, 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462, 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf, 0xda91cefe240175e6fab56271110427a4195ab71f, 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc, 0x2325f175975abdbcde555c79cc8e63381d28551b
- 19:25 WIB: 0x9856bac497634a62a970233bc4b0f5bb52c844c1, 0x3628764a6576b8dfb31fba0aac6a333b64851423, 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e, 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c, 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74, 0xad94ee77d0e868d299fb3e92b9d67560257f656d, 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a, 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650, 0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b
- 19:26 WIB: 0xc621946845d0fd5d1dbc6d6beb3e22aed39d7050, 0xf795c5250f3d4006283a0d0dbb378dc0e69df923, 0x9cdd08f30188c2732cdbcac8eebf4e6e8bf0c1b2, 0xaa49e7fec503664a39598645c7a3fbfa0374380d, 0x82c6085f9ec2722fd6c8fc47577368a156a25b9b, 0x3154f6949285ee7ac1593bd2bdf974adb6731c32, 0xca4e67bb5737c095bd3a80f79ecc6607e5723f1a, 0xe9ed24db105a6b15f880025ed9ad024c06783895, 0x3a39aa05b149141a4bfc7d73611dceb0557b39c4, 0xcb08c02c0a386a10773a2c6589e7089a3dd5aca3, 0xb940e4cd40ea9e887cbc92879062676e2bc4a924
- 19:27 WIB: 0x4522e661d9c94ec54b37e71896351a7440ec4f07, 0x5b4beded36c1ea380abe8c6a6a0c4408f38e5024, 0xc6591fde9b44aa081062c9fc6ee48e443d24ef57, 0x362396125a55d932a09f0a5182140cbbcaf30b70, 0xf9689b9d0a675ff9ad876f1d766fb460dbde7d20, 0x2cc8192fc62e3640de91e75582cf3dbbd571b970, 0x97bd895f8123a7837368df410e7d308246c0b3e9, 0x1cce4ec5a7c5e8cfc8dedd771876c61e60b8b645, 0xc0c84518ced6a61d2a4f4a50bc0f438e0cb1031b
- 19:28 WIB: 0xc194efe22e874a3fe666b5de5a8fd369f12c32d5, 0xa952331ea48ea9c00c4608d8259c186021331f31, 0x92bc32975b0fbf1a19caf7cc6e3f9ea4092fd314, 0x9b519f5d52cdd03e4b10484829bc137eef1f8c1a, 0xfdec62fde1f1dc56c0ba5e50f4cae5d6c63762bf, 0x64e893a4c5c930b2cc68b054792cbc66344aeb9a, 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36

Hitungan sinyal run 23 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 23 (setelah 18:12 WIB): TIDAK ADA yang
  terverifikasi, karena tidak satu pun Activity terbaca. TIDAK ADA token yang dibeli 2 wallet
  atau lebih dalam jendela ini, apalagi 13 — tetapi ini adalah ketiadaan bukti, bukan bukti
  ketiadaan buy.
- Jadi TIDAK ADA SINYAL yang diklaim dari run ini (ambang: minimal 13 entitas berbeda membeli
  token baru yang SAMA dengan CA yang sama). Pembelian pada jendela ini untuk ke-50 dompet
  TIDAK DIKETAHUI, bukan nol. Jendela run 22 untuk 45 dompet yang saat itu login-gated juga
  tetap TIDAK DIKETAHUI.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada
  runtuhan entitas. Laporan ini tidak memuat data pendanaan; co-buy/co-hold saja TIDAK
  meruntuhkan entitas.
- Tidak ada pemicu screening paper, rekomendasi beli, promosi, atau pemicu trade dari run ini.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-02T19:29:00+07:00; ringkasan run 23 per wallet; field saldo/holding tidak diubah).
  Baseline holdings tetap dari run 22 dan sebelumnya, dengan catatan jendela 18:12–19:29 WIB
  belum terbaca untuk semua dompet.
- Blokir yang tersisa: halaman dompet GMGN login-gated sejak ~17:27 WIB run 22 dan kini untuk
  semua 50 dompet pada run 23. Penyelesaian butuh sign-in GMGN (di luar kewenangan baca-saja
  run ini — run ini TIDAK mencoba login) atau menunggu GMGN kembali menampilkan halaman publik
  tanpa login lalu membaca ulang ke-50 dompet itu. Diskrepansi BNB GMGN vs on-chain untuk
  0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc tetap TIDAK TERSELESAIKAN, tidak dicek ulang
  (dompet login-gated pada run ini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 24 — Senin 2026-11-02, 21:22 WIB (gap: laporan browser belum diterima saat penulisan)

- Daftar dibaca dari `tier-ab-watch.md`: 50 entitas terpantau (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 1). Daftar lama 23 alamat TIDAK dipakai. Ambang sinyal yang berlaku: >25% dari 50 = minimal 13 entitas berbeda membeli token baru yang sama (CA sama); ambang absolut dari body awal (4 dari 14) sudah digantikan oleh skala di file setelah promosi 2026-11-01, dengan lantai 4.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-50 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>)
  DIDISPATCH (task browser-task:ad4ca7d3-719c-5cef-82e4-276192141dcc) pada 21:22 WIB, dengan
  instruksi eksplisit: bila login-gated, catat saja dan lanjut, JANGAN klik login.
- GAP YANG DICATAT JUJUR, mengikuti preseden run-run sebelumnya:
  - Laporan per-wallet terperinci (holdings + trade terbaru per wallet) dari browser BELUM
    terkirim ke konteks run ini pada saat penulisan log.
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim (ambang: minimal 13 entitas berbeda membeli token baru yang sama)
    — bukan karena wallet terbukti tidak membeli, melainkan karena bukti per-wallet belum diterima.
    Wallet yang tidak terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline / state run 23 TIDAK diubah: last_checked tetap 2026-11-02T19:29:00+07:00 dan holdings
    per wallet tetap dari run 23, sampai laporan browser run ini benar-benar diterima. Hanya field
    `last_attempt` di state yang diperbarui sebagai penanda run ini.
  - Jendela yang belum terjelaskan: pembelian setelah 19:29 WIB (run 23, sepenuhnya login-gated)
    untuk ke-50 wallet MASIH UNKNOWN, ditambah jendela run 22 untuk wallet-wallet yang sudah
    login-gated di run 22 — laporan run 24 harus dicocokkan jumlah/nilai dengan state sebelum
    ada trade dinyatakan baru, bukan hanya mengandalkan label relatif.
- Tindak lanjut: bila laporan browser run ini tiba belakangan, tambahkan sebagai adendum run ini
  dengan stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs state.
  Bila tidak tiba, run berikutnya harus mengulang pembacaan ke-50 wallet.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Adendum Run 24 — laporan browser diterima ~21:30 WIB

Pemeriksaan browser terukur runtime 21:23–21:30 WIB (laporan internal menyebut jendela
21:24–21:30 WIB — selisih awal 1 menit dicatat, waktu ukur runtime yang dipakai). Semua 50
halaman LOGIN-GATED, tanpa klik Log in/Sign up/Connect, tanpa sign/transaksi, tanpa upaya
login — sesuai aturan baca-saja. Koreksi atas bagian "GAP" di atas: bukti yang diterima
bukan data per-wallet, melainkan konfirmasi bahwa data per-wallet TIDAK dapat dibaca pada
run ini, sehingga hitungan sinyal run 24 tetap TIDAK dapat ditetapkan:
- Memuat data dompet publik: 0 dari 50. LOGIN-GATED: 50 dari 50. Tidak dapat dibaca karena
  alasan lain: 0 dari 50. Tidak ada bot challenge yang dilaporkan.
- Pada setiap halaman hanya tampil beranda GMGN dengan panel "You are not logged in to GMGN",
  tanpa header dompet, saldo BNB, holdings, maupun tab Activity. Karena itu TIDAK ADA saldo,
  holdings, aktivitas Buy/Sell/Tx In/Tx Out/Add/Burn, maupun contract address token yang
  tercatat dari run ini, dan TIDAK ADA CA yang ditebak dari simbol.
- TIDAK ADA SINYAL (ambang: minimal 13 entitas berbeda membeli token baru yang sama) —
  bukan karena wallet terbukti tidak membeli, melainkan karena aktivitasnya tidak terbaca.
  Wallet yang login-gated TIDAK dianggap tidak membeli, sesuai aturan run.
- TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada data pendanaan, jadi tidak ada
  keterkaitan KUAT baru yang terverifikasi). Co-buy/co-hold saja tidak meruntuhkan entitas.
- Jendela yang tetap UNKNOWN: pembelian setelah 19:29 WIB (run 23) untuk ke-50 wallet,
  ditambah jendela run 22 untuk wallet-wallet yang sudah login-gated di run 22 — semuanya
  tetap UNKNOWN, bukan nol. Diskrepansi GMGN-vs-on-chain BNB untuk 0xf6a8… tetap
  UNRESOLVED dan tidak dicek ulang pada run ini (halaman login-gated).
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-02T21:30:00+07:00; run24_summary ditambahkan ke ke-50 wallet; last_run_note
  run 24; holdings/saldo per wallet TIDAK diubah karena tidak dibuka).
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-50 wallet dan mencatat
  holdings + aktivitas terbaru per wallet secara eksplisit sebelum menghitung sinyal apa pun.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 25 — Senin 2026-11-02, 23:23–23:29 WIB (FULLY LOGIN-GATED, tanpa data publik)

- Daftar dibaca dari `tier-ab-watch.md`: 50 entitas terpantau (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 1). Daftar lama 23 alamat TIDAK dipakai. Ambang sinyal yang berlaku: >25% dari 50 = minimal 13 entitas berbeda membeli token baru yang sama (CA sama).
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-50 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>),
  runtime-measured 23:23–23:29 WIB (waktu laporan per-wallet 23:23–23:29 WIB, selaras — tidak ada
  selisih waktu yang perlu dicatat). TIDAK ADA tantangan bot (CAPTCHA) yang muncul.
- Hasil: 0 dari 50 halaman memuat data dompet publik. Setiap URL hanya menampilkan beranda GMGN
  dengan panel "You are not logged in to GMGN" — tanpa header dompet, saldo BNB, holdings, maupun
  tab Activity. Ini melanjutkan pola run 22 (parsial, gate menutup ~17:27 WIB), run 23, dan run 24
  yang sepenuhnya login-gated.

Per dompet LOGIN-GATED (50 dompet — Activity TIDAK terbaca, BUKAN "tidak ada buy",
BUKAN "No Data", dan TIDAK ada upaya login; saldo/holding tidak diubah di state):
- 23:23 WIB: 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6, 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02
- 23:24 WIB: 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5, 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7, 0x75642756e4ba4cc8fbe76df2239cada046cfc854, 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a, 0x892200223bdfb11d2506c5ab1cae9222ce253acc, 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c, 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e, 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462, 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf, 0xda91cefe240175e6fab56271110427a4195ab71f, 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc, 0x2325f175975abdbcde555c79cc8e63381d28551b
- 23:25 WIB: 0x9856bac497634a62a970233bc4b0f5bb52c844c1, 0x3628764a6576b8dfb31fba0aac6a333b64851423, 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e, 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c, 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74, 0xad94ee77d0e868d299fb3e92b9d67560257f656d, 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a, 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650, 0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b
- 23:26 WIB: 0xc621946845d0fd5d1dbc6d6beb3e22aed39d7050, 0xf795c5250f3d4006283a0d0dbb378dc0e69df923, 0x9cdd08f30188c2732cdbcac8eebf4e6e8bf0c1b2, 0xaa49e7fec503664a39598645c7a3fbfa0374380d, 0x82c6085f9ec2722fd6c8fc47577368a156a25b9b, 0x3154f6949285ee7ac1593bd2bdf974adb6731c32, 0xca4e67bb5737c095bd3a80f79ecc6607e5723f1a, 0xe9ed24db105a6b15f880025ed9ad024c06783895
- 23:27 WIB: 0x3a39aa05b149141a4bfc7d73611dceb0557b39c4, 0xcb08c02c0a386a10773a2c6589e7089a3dd5aca3, 0xb940e4cd40ea9e887cbc92879062676e2bc4a924, 0x4522e661d9c94ec54b37e71896351a7440ec4f07, 0x5b4beded36c1ea380abe8c6a6a0c4408f38e5024, 0xc6591fde9b44aa081062c9fc6ee48e443d24ef57, 0x362396125a55d932a09f0a5182140cbbcaf30b70, 0xf9689b9d0a675ff9ad876f1d766fb460dbde7d20, 0x2cc8192fc62e3640de91e75582cf3dbbd571b970
- 23:28 WIB: 0x97bd895f8123a7837368df410e7d308246c0b3e9, 0x1cce4ec5a7c5e8cfc8dedd771876c61e60b8b645, 0xc0c84518ced6a61d2a4f4a50bc0f438e0cb1031b, 0xc194efe22e874a3fe666b5de5a8fd369f12c32d5, 0xa952331ea48ea9c00c4608d8259c186021331f31, 0x92bc32975b0fbf1a19caf7cc6e3f9ea4092fd314, 0x9b519f5d52cdd03e4b10484829bc137eef1f8c1a, 0xfdec62fde1f1dc56c0ba5e50f4cae5d6c63762bf, 0x64e893a4c5c930b2cc68b054792cbc66344aeb9a
- 23:29 WIB: 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36

Hitungan sinyal run 25 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 25 (setelah 21:30 WIB): TIDAK ADA yang
  terverifikasi, karena tidak satu pun Activity terbaca. TIDAK ADA token yang dibeli 2 wallet
  atau lebih dalam jendela ini, apalagi 13 — tetapi ini adalah ketiadaan bukti, bukan bukti
  ketiadaan buy.
- Jadi TIDAK ADA SINYAL yang diklaim dari run ini (ambang: minimal 13 entitas berbeda membeli
  token baru yang SAMA dengan CA yang sama). Pembelian pada jendela ini untuk ke-50 dompet
  TIDAK DIKETAHUI, bukan nol. Jendela run 22 untuk dompet-dompet yang saat itu login-gated,
  serta jendela run 23 dan run 24 untuk semua dompet, juga tetap TIDAK DIKETAHUI.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada
  runtuhan entitas. Laporan ini tidak memuat data pendanaan; co-buy/co-hold saja TIDAK
  meruntuhkan entitas.
- Tidak ada pemicu screening paper, rekomendasi beli, promosi, atau pemicu trade dari run ini.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-02T23:29:00+07:00; ringkasan run 25 per wallet; field saldo/holding tidak diubah).
  Baseline holdings tetap dari run 22 dan sebelumnya, dengan catatan jendela 21:30–23:29 WIB
  belum terbaca untuk semua dompet.
- Blokir yang tersisa: halaman dompet GMGN login-gated sejak ~17:27 WIB run 22 dan kini untuk
  semua 50 dompet pada run 25 (run ke-4 berturut-turut yang sepenuhnya login-gated: run 23, 24,
  25, setelah run 22 parsial). Penyelesaian butuh sign-in GMGN (di luar kewenangan baca-saja
  run ini — run ini TIDAK mencoba login) atau menunggu GMGN kembali menampilkan halaman publik
  tanpa login lalu membaca ulang ke-50 dompet itu. Diskrepansi BNB GMGN vs on-chain untuk
  0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc tetap TIDAK TERSELESAIKAN, tidak dicek ulang
  (dompet login-gated pada run ini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 26 — Selasa 2026-11-03, 01:24–01:31 WIB (FULLY LOGIN-GATED, tanpa data publik)

- Daftar dibaca dari `tier-ab-watch.md`: 50 entitas terpantau (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 1). Daftar lama 23 alamat TIDAK dipakai. Ambang sinyal yang berlaku: >25% dari 50 = minimal 13 entitas berbeda membeli token baru yang sama (CA sama).
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-50 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>),
  runtime-measured 01:24–01:31 WIB (waktu laporan per-wallet 01:24–01:30 WIB, selisih akhir 1 menit
  dicatat, waktu ukur runtime yang dipakai). TIDAK ADA tantangan bot (CAPTCHA) yang dilaporkan.
- Hasil: 0 dari 50 halaman memuat data dompet publik. Setiap URL hanya menampilkan beranda GMGN
  dengan panel "You are not logged in to GMGN" — tanpa header dompet, saldo BNB, holdings, maupun
  tab Activity. Ini melanjutkan pola run 22 (parsial, gate menutup ~17:27 WIB 2026-11-02), run 23,
  run 24, dan run 25 yang sepenuhnya login-gated — run 26 adalah run ke-5 berturut-turut yang
  sepenuhnya login-gated.

Per dompet LOGIN-GATED (50 dompet — Activity TIDAK terbaca, BUKAN "tidak ada buy",
BUKAN "No Data", dan TIDAK ada upaya login; saldo/holding tidak diubah di state):
- 01:24 WIB: 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6, 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02, 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5, 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7, 0x75642756e4ba4cc8fbe76df2239cada046cfc854
- 01:25 WIB: 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a, 0x892200223bdfb11d2506c5ab1cae9222ce253acc, 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c, 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e, 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462, 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf, 0xda91cefe240175e6fab56271110427a4195ab71f, 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc, 0x2325f175975abdbcde555c79cc8e63381d28551b
- 01:26 WIB: 0x9856bac497634a62a970233bc4b0f5bb52c844c1, 0x3628764a6576b8dfb31fba0aac6a333b64851423, 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e, 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c, 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74, 0xad94ee77d0e868d299fb3e92b9d67560257f656d, 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a
- 01:27 WIB: 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650, 0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b, 0xc621946845d0fd5d1dbc6d6beb3e22aed39d7050, 0xf795c5250f3d4006283a0d0dbb378dc0e69df923, 0x9cdd08f30188c2732cdbcac8eebf4e6e8bf0c1b2, 0xaa49e7fec503664a39598645c7a3fbfa0374380d, 0x82c6085f9ec2722fd6c8fc47577368a156a25b9b
- 01:28 WIB: 0x3154f6949285ee7ac1593bd2bdf974adb6731c32, 0xca4e67bb5737c095bd3a80f79ecc6607e5723f1a, 0xe9ed24db105a6b15f880025ed9ad024c06783895, 0x3a39aa05b149141a4bfc7d73611dceb0557b39c4, 0xcb08c02c0a386a10773a2c6589e7089a3dd5aca3, 0xb940e4cd40ea9e887cbc92879062676e2bc4a924, 0x4522e661d9c94ec54b37e71896351a7440ec4f07
- 01:29 WIB: 0x5b4beded36c1ea380abe8c6a6a0c4408f38e5024, 0xc6591fde9b44aa081062c9fc6ee48e443d24ef57, 0x362396125a55d932a09f0a5182140cbbcaf30b70, 0xf9689b9d0a675ff9ad876f1d766fb460dbde7d20, 0x2cc8192fc62e3640de91e75582cf3dbbd571b970, 0x97bd895f8123a7837368df410e7d308246c0b3e9, 0x1cce4ec5a7c5e8cfc8dedd771876c61e60b8b645, 0xc0c84518ced6a61d2a4f4a50bc0f438e0cb1031b, 0xc194efe22e874a3fe666b5de5a8fd369f12c32d5
- 01:30 WIB: 0xa952331ea48ea9c00c4608d8259c186021331f31, 0x92bc32975b0fbf1a19caf7cc6e3f9ea4092fd314, 0x9b519f5d52cdd03e4b10484829bc137eef1f8c1a, 0xfdec62fde1f1dc56c0ba5e50f4cae5d6c63762bf, 0x64e893a4c5c930b2cc68b054792cbc66344aeb9a, 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36

Hitungan sinyal run 26 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 26 (setelah 23:29 WIB 2026-11-02): TIDAK ADA yang
  terverifikasi, karena tidak satu pun Activity terbaca. TIDAK ADA token yang dibeli 2 wallet
  atau lebih dalam jendela ini, apalagi 13 — tetapi ini adalah ketiadaan bukti, bukan bukti
  ketiadaan buy.
- Jadi TIDAK ADA SINYAL yang diklaim dari run ini (ambang: minimal 13 entitas berbeda membeli
  token baru yang SAMA dengan CA yang sama). Pembelian pada jendela ini untuk ke-50 dompet
  TIDAK DIKETAHUI, bukan nol. Jendela run 22 untuk dompet-dompet yang saat itu login-gated,
  serta jendela run 23, run 24, dan run 25 untuk semua dompet, juga tetap TIDAK DIKETAHUI.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada
  runtuhan entitas. Laporan ini tidak memuat data pendanaan; co-buy/co-hold saja TIDAK
  meruntuhkan entitas.
- Tidak ada pemicu screening paper, rekomendasi beli, promosi, atau pemicu trade dari run ini.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-03T01:31:00+07:00; ringkasan run 26 per wallet; field saldo/holding tidak diubah).
  Baseline holdings tetap dari run 22 dan sebelumnya, dengan catatan jendela 23:29–01:31 WIB
  belum terbaca untuk semua dompet.
- Blokir yang tersisa: halaman dompet GMGN login-gated sejak ~17:27 WIB run 22 dan kini untuk
  semua 50 dompet pada run 26 (run ke-5 berturut-turut yang sepenuhnya login-gated: run 23, 24,
  25, 26, setelah run 22 parsial). Penyelesaian butuh sign-in GMGN (di luar kewenangan baca-saja
  run ini — run ini TIDAK mencoba login) atau menunggu GMGN kembali menampilkan halaman publik
  tanpa login lalu membaca ulang ke-50 dompet itu. Diskrepansi BNB GMGN vs on-chain untuk
  0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc tetap TIDAK TERSELESAIKAN, tidak dicek ulang
  (dompet login-gated pada run ini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 27 — Selasa 2026-11-03, 03:23–03:33 WIB (FULLY LOGIN-GATED, tanpa data publik)

- Daftar dibaca dari `tier-ab-watch.md`: 50 entitas terpantau (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 1). Daftar lama 23 alamat TIDAK dipakai. Ambang sinyal yang berlaku: >25% dari 50 = minimal 13 entitas berbeda membeli token baru yang sama (CA sama).
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-50 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>),
  runtime-measured 03:23–03:33 WIB (waktu laporan per-wallet 03:24–03:32 WIB, selisih akhir 1 menit
  dicatat, waktu ukur runtime yang dipakai). TIDAK ADA tantangan bot (CAPTCHA) yang dilaporkan.
- Hasil: 0 dari 50 halaman memuat data dompet publik. Setiap URL hanya menampilkan beranda GMGN
  dengan panel "You are not logged in to GMGN" — tanpa header dompet, saldo BNB, holdings, maupun
  tab Activity. Ini melanjutkan pola run 22 (parsial, gate menutup ~17:27 WIB 2026-11-02) dan
  run 23, 24, 25, 26 yang sepenuhnya login-gated — run 27 adalah run ke-5 berturut-turut dalam
  rangkaian run 23–27 yang sepenuhnya login-gated. Token-token yang tampak di panel beranda umum
  GMGN BUKAN holdings dompet yang diperiksa dan tidak dicatat sebagai holdings dompet mana pun.

Per dompet LOGIN-GATED (50 dompet — Activity TIDAK terbaca, BUKAN "tidak ada buy",
BUKAN "No Data", dan TIDAK ada upaya login; saldo/holding tidak diubah di state):
- 03:24 WIB: 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6, 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02, 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5, 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7
- 03:25 WIB: 0x75642756e4ba4cc8fbe76df2239cada046cfc854, 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a
- 03:26 WIB: 0x892200223bdfb11d2506c5ab1cae9222ce253acc, 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c, 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e, 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462, 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf
- 03:27 WIB: 0xda91cefe240175e6fab56271110427a4195ab71f, 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc, 0x2325f175975abdbcde555c79cc8e63381d28551b, 0x9856bac497634a62a970233bc4b0f5bb52c844c1, 0x3628764a6576b8dfb31fba0aac6a333b64851423, 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e, 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c
- 03:28 WIB: 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74, 0xad94ee77d0e868d299fb3e92b9d67560257f656d, 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a, 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650, 0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b, 0xc621946845d0fd5d1dbc6d6beb3e22aed39d7050, 0xf795c5250f3d4006283a0d0dbb378dc0e69df923
- 03:29 WIB: 0x9cdd08f30188c2732cdbcac8eebf4e6e8bf0c1b2, 0xaa49e7fec503664a39598645c7a3fbfa0374380d, 0x82c6085f9ec2722fd6c8fc47577368a156a25b9b, 0x3154f6949285ee7ac1593bd2bdf974adb6731c32, 0xca4e67bb5737c095bd3a80f79ecc6607e5723f1a, 0xe9ed24db105a6b15f880025ed9ad024c06783895, 0x3a39aa05b149141a4bfc7d73611dceb0557b39c4
- 03:30 WIB: 0xcb08c02c0a386a10773a2c6589e7089a3dd5aca3, 0xb940e4cd40ea9e887cbc92879062676e2bc4a924, 0x4522e661d9c94ec54b37e71896351a7440ec4f07, 0x5b4beded36c1ea380abe8c6a6a0c4408f38e5024, 0xc6591fde9b44aa081062c9fc6ee48e443d24ef57, 0x362396125a55d932a09f0a5182140cbbcaf30b70, 0xf9689b9d0a675ff9ad876f1d766fb460dbde7d20
- 03:31 WIB: 0x2cc8192fc62e3640de91e75582cf3dbbd571b970, 0x97bd895f8123a7837368df410e7d308246c0b3e9, 0x1cce4ec5a7c5e8cfc8dedd771876c61e60b8b645, 0xc0c84518ced6a61d2a4f4a50bc0f438e0cb1031b, 0xc194efe22e874a3fe666b5de5a8fd369f12c32d5, 0xa952331ea48ea9c00c4608d8259c186021331f31
- 03:32 WIB: 0x92bc32975b0fbf1a19caf7cc6e3f9ea4092fd314, 0x9b519f5d52cdd03e4b10484829bc137eef1f8c1a, 0xfdec62fde1f1dc56c0ba5e50f4cae5d6c63762bf, 0x64e893a4c5c930b2cc68b054792cbc66344aeb9a, 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36

Hitungan sinyal run 27 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 27 (setelah 01:31 WIB 2026-11-03): TIDAK ADA yang
  terverifikasi, karena tidak satu pun Activity terbaca. TIDAK ADA token yang dibeli 2 wallet
  atau lebih dalam jendela ini, apalagi 13 — tetapi ini adalah ketiadaan bukti, bukan bukti
  ketiadaan buy.
- Jadi TIDAK ADA SINYAL yang diklaim dari run ini (ambang: minimal 13 entitas berbeda membeli
  token baru yang SAMA dengan CA yang sama). Pembelian pada jendela ini untuk ke-50 dompet
  TIDAK DIKETAHUI, bukan nol. Jendela run 22 untuk dompet-dompet yang saat itu login-gated,
  serta jendela run 23, run 24, run 25, dan run 26 untuk semua dompet, juga tetap TIDAK DIKETAHUI.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada
  runtuhan entitas. Laporan ini tidak memuat data pendanaan; co-buy/co-hold saja TIDAK
  meruntuhkan entitas.
- Tidak ada pemicu screening paper, rekomendasi beli, promosi, atau pemicu trade dari run ini.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-03T03:33:00+07:00; ringkasan run 27 per wallet; field saldo/holding tidak diubah).
  Baseline holdings tetap dari run 22 dan sebelumnya, dengan catatan jendela 01:31–03:33 WIB
  belum terbaca untuk semua dompet.
- Blokir yang tersisa: halaman dompet GMGN login-gated sejak ~17:27 WIB run 22 dan kini untuk
  semua 50 dompet pada run 27. Penyelesaian butuh sign-in GMGN (di luar kewenangan baca-saja
  run ini — run ini TIDAK mencoba login) atau menunggu GMGN kembali menampilkan halaman publik
  tanpa login lalu membaca ulang ke-50 dompet itu. Diskrepansi BNB GMGN vs on-chain untuk
  0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc tetap TIDAK TERSELESAIKAN, tidak dicek ulang
  (dompet login-gated pada run ini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 28 — Selasa 2026-11-03, 07:22–07:23 WIB (gap: laporan browser belum diterima saat penulisan)

- Daftar dibaca dari `tier-ab-watch.md` setiap run: 50 entitas terpantau (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 1). Ambang sinyal saat ini: minimal 13 entitas berbeda membeli token baru yang sama (floor(25% x 50)+1), bukan ambang 4 dari set 14 lama — set 14 lama sudah digantikan oleh promosi 2026-11-01.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow. Pemeriksaan browser live read-only ke-50 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>) DIDISPATCH pada ~07:23 WIB, dengan instruksi eksplisit: bila login-gated, catat saja dan lanjut, JANGAN klik login.
- GAP YANG DICATAT JUJUR, mengikuti preseden Run 1/3/4/5/6:
  - Laporan per-wallet terperinci (holdings + trade terbaru per wallet) dari browser BELUM terkirim ke konteks run ini pada saat penulisan log.
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim — bukan karena wallet terbukti tidak membeli, melainkan karena bukti per-wallet belum diterima. Wallet yang tidak terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline / state run 27 TIDAK diubah: last_checked tetap 2026-11-03T03:33:00+07:00; hanya field `last_attempt` di state yang diperbarui sebagai penanda run ini.
  - Konteks dari run 27: run 27 FULLY LOGIN-GATED (0 dari 50 halaman memuat publik); jendela pembelian setelah run 27 dan semua jendela sejak run 22 partial gate / run 23-26 tetap UNKNOWN untuk ke-50 wallet, bukan nol, sampai laporan yang dapat dibaca diterima.
- Tindak lanjut: bila laporan browser run ini tiba, tambahkan sebagai adendum run ini dengan stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs baseline run 27. Bila laporan menunjukkan login-gated lagi, catat run 28 sebagai login-gated penuh dan jendela tetap UNKNOWN.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Adendum Run 28 — laporan browser diterima ~08:03 WIB

Pemeriksaan browser terukur runtime 07:35–08:03 WIB (laporan per-wallet 07:37–08:01 WIB, selisih dalam 2 menit, dipakai waktu ukur runtime). Hasil: 50 dari 50 dompet LOGIN-GATED, 0 dompet publik. Setiap URL https://gmgn.ai/bsc/address/<alamat> hanya menampilkan beranda GMGN dengan panel "You are not logged in to GMGN", tanpa header dompet, saldo BNB, maupun tab Activity. Sesuai instruksi, tidak ada klik Log in/Sign up/Connect, tidak ada upaya login, koneksi dompet, sign, beli/jual/follow, dan tidak ada bot challenge yang dilaporkan.

Konsekuensi, mengikuti aturan run:
- TIDAK ADA pembelian baru yang terverifikasi dari run ini.
- TIDAK ADA SINYAL yang diklaim (ambang saat ini: minimal 13 entitas berbeda membeli token baru yang sama) — bukan karena wallet terbukti tidak membeli, melainkan karena aktivitas tidak terbaca. Wallet yang tidak terbaca datanya TIDAK dianggap tidak membeli.
- TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi, karena tidak ada data pendanaan).
- Baseline / state TIDAK diubah kecuali penanda run: last_checked tetap 2026-11-03T03:33:00+07:00; tiap wallet mendapat `run28_summary` login-gated; `last_run` diperbarui ke run 28.
- Jendela pembelian setelah 03:33 WIB 2026-11-03 dan semua jendela sejak run 22 partial gate / run 23–27 tetap UNKNOWN untuk ke-50 wallet, bukan nol. Ini run ke-6 berturut-turut yang sepenuhnya login-gated (run 23–28).
- Diskrepansi GMGN-vs-on-chain BNB untuk 0xf6a8… tetap UNRESOLVED, tidak dicek ulang pada run ini (halaman login-gated).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 29 — Selasa 2026-11-03, 09:23–09:31 WIB

- Daftar dibaca dari `tier-ab-watch.md` + state setiap run: 54 entitas terpantau (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 1 + tambahan JAGENT 4, 2026-11-03 ~08:47 WIB). Ambang sinyal saat ini: minimal 14 entitas berbeda membeli token baru yang sama (floor(25% x 54)+1), bukan ambang 4 dari set 14 lama.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow. Pemeriksaan browser live read-only ke-54 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>), runtime-measured 09:23–09:31 WIB (laporan per-wallet 09:23–09:30 WIB).
- Hasil: FULLY LOGIN-GATED — 0 dari 54 halaman memuat publik, 54 login-gated, 0 tidak terbaca. Setiap URL hanya menampilkan beranda GMGN dengan panel "You are not logged in to GMGN", tanpa header dompet, saldo BNB, daftar holdings, maupun tab Activity. Tidak ada bot challenge yang dilaporkan. Tidak ada klik Log in/Sign up/Connect, tidak ada upaya login.
- Konsekuensi, mengikuti aturan run:
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim (ambang: minimal 14 entitas) — bukan karena wallet terbukti tidak membeli, melainkan karena aktivitas tidak terbaca. Wallet yang tidak terbaca datanya TIDAK dianggap tidak membeli.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi, karena tidak ada data pendanaan).
  - Baseline / state TIDAK diubah kecuali penanda run: last_checked tetap 2026-11-03T03:33:00+07:00; tiap wallet mendapat `run29_summary` login-gated; `last_run` diperbarui ke run 29.
  - Jendela pembelian setelah 03:33 WIB 2026-11-03 dan semua jendela sejak run 22 partial gate / run 23–28 tetap UNKNOWN untuk ke-54 wallet, bukan nol. Ini run ke-7 berturut-turut yang sepenuhnya login-gated (run 23–29).
  - Diskrepansi GMGN-vs-on-chain BNB untuk 0xf6a8… tetap UNRESOLVED, tidak dicek ulang pada run ini (halaman login-gated).
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
- SENYAP ke chat sesuai aturan run (tidak ada laporan rutin; tidak ada wallet yang memenuhi kriteria promosi terpercaya pada run ini).

## Run 30 — Selasa 2026-11-03, 11:22 WIB (gap: laporan browser belum diterima saat penulisan)

- Daftar dibaca dari `tier-ab-watch.md` + state setiap run: 54 entitas terpantau (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 1 + tambahan JAGENT 4, 2026-11-03 ~08:47 WIB). Ambang sinyal saat ini: minimal 14 entitas berbeda membeli token baru yang sama (floor(25% x 54)+1), bukan ambang 4 dari set 14 lama — set 14 lama sudah digantikan oleh promosi 2026-11-01 dan tambahan 2026-11-03. Daftar lama 23 alamat TIDAK dipakai.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow. Pemeriksaan browser live read-only ke-54 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>) DIDISPATCH pada ~11:23 WIB, dengan instruksi eksplisit: bila login-gated, catat saja dan lanjut, JANGAN klik login.
- GAP YANG DICATAT JUJUR, mengikuti preseden Run 1/3/4/5/6:
  - Laporan per-wallet terperinci (holdings + trade terbaru per wallet) dari browser BELUM terkirim ke konteks run ini pada saat penulisan log.
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim — bukan karena wallet terbukti tidak membeli, melainkan karena bukti per-wallet belum diterima. Wallet yang tidak terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline / state run 29 TIDAK diubah: last_checked tetap 2026-11-03T03:33:00+07:00; hanya field `last_attempt` di state yang diperbarui sebagai penanda run ini.
  - Konteks dari run 29: run 29 FULLY LOGIN-GATED (0 dari 54 halaman memuat publik); jendela pembelian setelah 03:33 WIB 2026-11-03 dan semua jendela sejak run 22 partial gate / run 23–29 tetap UNKNOWN untuk ke-54 wallet, bukan nol, sampai laporan yang dapat dibaca diterima. Ini akan menjadi run ke-8 berturut-turut yang sepenuhnya login-gated bila laporan run 30 juga login-gated.
- Tindak lanjut: bila laporan browser run ini tiba, tambahkan sebagai adendum run ini dengan stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs baseline run 29. Bila laporan menunjukkan login-gated lagi, catat run 30 sebagai login-gated penuh dan jendela tetap UNKNOWN.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Adendum Run 30 — laporan browser diterima ~11:34 WIB

Pemeriksaan browser terukur runtime 11:24–11:34 WIB (laporan per-wallet 11:24–11:33 WIB, selisih akhir 1 menit dicatat, waktu ukur runtime yang dipakai). Hasil: 54 dari 54 dompet LOGIN-GATED, 0 dompet publik. Setiap URL https://gmgn.ai/bsc/address/<alamat> hanya menampilkan beranda GMGN dengan panel "You are not logged in to GMGN", tanpa header dompet, saldo BNB, daftar holdings, maupun tab Activity. Sesuai instruksi, tidak ada klik Log in/Sign up/Connect, tidak ada upaya login, koneksi dompet, sign, beli/jual/follow, dan tidak ada bot challenge yang dilaporkan. Token yang tampak di beranda umum GMGN BUKAN holdings dompet yang diperiksa dan tidak dicatat sebagai holdings dompet mana pun.

Per dompet LOGIN-GATED (54 dompet — Activity TIDAK terbaca, BUKAN "tidak ada buy", BUKAN "No Data", dan TIDAK ada upaya login; saldo/holding tidak diubah di state):
- 11:24 WIB: 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6
- 11:25 WIB: 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02, 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5, 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7, 0x75642756e4ba4cc8fbe76df2239cada046cfc854, 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a, 0x892200223bdfb11d2506c5ab1cae9222ce253acc
- 11:26 WIB: 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c, 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e, 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462, 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf
- 11:27 WIB: 0xda91cefe240175e6fab56271110427a4195ab71f, 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc, 0x2325f175975abdbcde555c79cc8e63381d28551b, 0x9856bac497634a62a970233bc4b0f5bb52c844c1
- 11:28 WIB: 0x3628764a6576b8dfb31fba0aac6a333b64851423, 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e, 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c, 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74, 0xad94ee77d0e868d299fb3e92b9d67560257f656d, 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a, 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650, 0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b
- 11:29 WIB: 0xc621946845d0fd5d1dbc6d6beb3e22aed39d7050, 0xf795c5250f3d4006283a0d0dbb378dc0e69df923, 0x9cdd08f30188c2732cdbcac8eebf4e6e8bf0c1b2, 0xaa49e7fec503664a39598645c7a3fbfa0374380d, 0x82c6085f9ec2722fd6c8fc47577368a156a25b9b, 0x3154f6949285ee7ac1593bd2bdf974adb6731c32, 0xca4e67bb5737c095bd3a80f79ecc6607e5723f1a, 0xe9ed24db105a6b15f880025ed9ad024c06783895
- 11:30 WIB: 0x3a39aa05b149141a4bfc7d73611dceb0557b39c4, 0xcb08c02c0a386a10773a2c6589e7089a3dd5aca3, 0xb940e4cd40ea9e887cbc92879062676e2bc4a924, 0x4522e661d9c94ec54b37e71896351a7440ec4f07, 0x5b4beded36c1ea380abe8c6a6a0c4408f38e5024, 0xc6591fde9b44aa081062c9fc6ee48e443d24ef57, 0x362396125a55d932a09f0a5182140cbbcaf30b70, 0xf9689b9d0a675ff9ad876f1d766fb460dbde7d20
- 11:31 WIB: 0x2cc8192fc62e3640de91e75582cf3dbbd571b970, 0x97bd895f8123a7837368df410e7d308246c0b3e9, 0x1cce4ec5a7c5e8cfc8dedd771876c61e60b8b645, 0xc0c84518ced6a61d2a4f4a50bc0f438e0cb1031b, 0xc194efe22e874a3fe666b5de5a8fd369f12c32d5, 0xa952331ea48ea9c00c4608d8259c186021331f31, 0x92bc32975b0fbf1a19caf7cc6e3f9ea4092fd314
- 11:32 WIB: 0x9b519f5d52cdd03e4b10484829bc137eef1f8c1a, 0xfdec62fde1f1dc56c0ba5e50f4cae5d6c63762bf, 0x64e893a4c5c930b2cc68b054792cbc66344aeb9a, 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36
- 11:33 WIB: 0x341bed5b412968755f3dd6e9946636ac6f97457a, 0xd124dd5825ecaad959acdea6336926eb40aa0c9b, 0x5cf3f945620ba1a3cc9065a2086bfc728b172a0f, 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db

Hitungan sinyal run 30 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 30 (setelah 03:33 WIB 2026-11-03): TIDAK ADA yang terverifikasi, karena tidak satu pun Activity terbaca. TIDAK ADA token yang dibeli 2 wallet atau lebih dalam jendela ini, apalagi 14 — tetapi ini adalah ketiadaan bukti, bukan bukti ketiadaan buy.
- Jadi TIDAK ADA SINYAL yang diklaim dari run ini (ambang: minimal 14 entitas berbeda membeli token baru yang SAMA dengan CA yang sama). Pembelian pada jendela ini untuk ke-54 dompet TIDAK DIKETAHUI, bukan nol. Jendela run 22 untuk dompet-dompet yang saat itu login-gated, serta jendela run 23, run 24, run 25, run 26, run 27, run 28, dan run 29 untuk semua dompet, juga tetap TIDAK DIKETAHUI.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada runtuhan entitas. Laporan ini tidak memuat data pendanaan; co-buy/co-hold saja TIDAK meruntuhkan entitas.
- Tidak ada pemicu screening paper, rekomendasi beli, promosi, atau pemicu trade dari run ini.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked tetap 2026-11-03T03:33:00+07:00; ringkasan run 30 per wallet; field saldo/holding tidak diubah; `last_run` diperbarui ke run 30). Baseline holdings tetap dari run 22 dan sebelumnya, dengan catatan jendela 03:33–11:34 WIB belum terbaca untuk semua dompet.
- Blokir yang tersisa: halaman dompet GMGN login-gated sejak ~17:27 WIB run 22 dan kini untuk semua 54 dompet pada run 30 (run ke-8 berturut-turut yang sepenuhnya login-gated: run 23–30). Penyelesaian butuh sign-in GMGN (di luar kewenangan baca-saja run ini — run ini TIDAK mencoba login) atau menunggu GMGN kembali menampilkan halaman publik tanpa login lalu membaca ulang ke-54 dompet itu. Diskrepansi BNB GMGN vs on-chain untuk 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc tetap TIDAK TERSELESAIKAN, tidak dicek ulang (dompet login-gated pada run ini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
- SENYAP ke chat sesuai aturan run (tidak ada laporan rutin; tidak ada wallet yang memenuhi kriteria promosi terpercaya pada run ini).

## Run 31 — Selasa 2026-11-03, 13:24–13:38 WIB (FULLY LOGIN-GATED, tanpa data publik)
- Daftar dibaca dari `tier-ab-watch.md` + state setiap run: 54 entitas terpantau (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 1 + tambahan JAGENT 4, 2026-11-03 ~08:47 WIB). Ambang sinyal yang berlaku: minimal 14 entitas berbeda membeli token baru yang sama (floor(25% x 54)+1), bukan ambang 4 dari set 14 lama — set 14 lama sudah digantikan oleh promosi 2026-11-01 dan tambahan 2026-11-03. Daftar lama 23 alamat TIDAK dipakai. Catatan: body jadwal run ini masih menyebut set 14/ambang 4; run ini mengikuti set terpantau terkini di file + state (54 entitas), yang mencakup ke-14 dompet inti itu, dan ambang 14 yang lebih konservatif.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow. Pemeriksaan browser live read-only ke-54 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>), runtime-measured 13:24–13:38 WIB (laporan per-wallet 13:24–13:37 WIB, selisih akhir 1 menit dicatat, waktu ukur runtime yang dipakai). TIDAK ADA tantangan bot (CAPTCHA) yang dilaporkan.
- Hasil: 0 dari 54 halaman memuat data dompet publik. Setiap URL hanya menampilkan beranda GMGN dengan panel "You are not logged in to GMGN" — tanpa header dompet, saldo BNB, holdings, maupun tab Activity. Ini melanjutkan pola run 22 (parsial, gate menutup ~17:27 WIB 2026-11-02) dan run 23–30 yang sepenuhnya login-gated — run 31 adalah run ke-9 berturut-turut yang sepenuhnya login-gated.

Per dompet LOGIN-GATED (54 dompet — Activity TIDAK terbaca, BUKAN "tidak ada buy", BUKAN "No Data", dan TIDAK ada upaya login; saldo/holding tidak diubah di state):
- 13:24 WIB: 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6, 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02
- 13:25 WIB: 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5, 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7, 0x75642756e4ba4cc8fbe76df2239cada046cfc854, 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a
- 13:26 WIB: 0x892200223bdfb11d2506c5ab1cae9222ce253acc, 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c
- 13:27 WIB: 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e, 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462, 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf, 0xda91cefe240175e6fab56271110427a4195ab71f
- 13:28 WIB: 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc, 0x2325f175975abdbcde555c79cc8e63381d28551b, 0x9856bac497634a62a970233bc4b0f5bb52c844c1
- 13:29 WIB: 0x3628764a6576b8dfb31fba0aac6a333b64851423, 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e, 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c
- 13:30 WIB: 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74, 0xad94ee77d0e868d299fb3e92b9d67560257f656d
- 13:31 WIB: 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a, 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650, 0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b, 0xc621946845d0fd5d1dbc6d6beb3e22aed39d7050
- 13:32 WIB: 0xf795c5250f3d4006283a0d0dbb378dc0e69df923, 0x9cdd08f30188c2732cdbcac8eebf4e6e8bf0c1b2, 0xaa49e7fec503664a39598645c7a3fbfa0374380d, 0x82c6085f9ec2722fd6c8fc47577368a156a25b9b, 0x3154f6949285ee7ac1593bd2bdf974adb6731c32
- 13:33 WIB: 0xca4e67bb5737c095bd3a80f79ecc6607e5723f1a, 0xe9ed24db105a6b15f880025ed9ad024c06783895, 0x3a39aa05b149141a4bfc7d73611dceb0557b39c4
- 13:34 WIB: 0xcb08c02c0a386a10773a2c6589e7089a3dd5aca3, 0xb940e4cd40ea9e887cbc92879062676e2bc4a924, 0x4522e661d9c94ec54b37e71896351a7440ec4f07, 0x5b4beded36c1ea380abe8c6a6a0c4408f38e5024, 0xc6591fde9b44aa081062c9fc6ee48e443d24ef57, 0x362396125a55d932a09f0a5182140cbbcaf30b70, 0xf9689b9d0a675ff9ad876f1d766fb460dbde7d20
- 13:35 WIB: 0x2cc8192fc62e3640de91e75582cf3dbbd571b970, 0x97bd895f8123a7837368df410e7d308246c0b3e9, 0x1cce4ec5a7c5e8cfc8dedd771876c61e60b8b645, 0xc0c84518ced6a61d2a4f4a50bc0f438e0cb1031b, 0xc194efe22e874a3fe666b5de5a8fd369f12c32d5, 0xa952331ea48ea9c00c4608d8259c186021331f31
- 13:36 WIB: 0x92bc32975b0fbf1a19caf7cc6e3f9ea4092fd314, 0x9b519f5d52cdd03e4b10484829bc137eef1f8c1a, 0xfdec62fde1f1dc56c0ba5e50f4cae5d6c63762bf, 0x64e893a4c5c930b2cc68b054792cbc66344aeb9a, 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36, 0x341bed5b412968755f3dd6e9946636ac6f97457a, 0xd124dd5825ecaad959acdea6336926eb40aa0c9b
- 13:37 WIB: 0x5cf3f945620ba1a3cc9065a2086bfc728b172a0f, 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db

Hitungan sinyal run 31 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 31 (setelah 03:33 WIB 2026-11-03): TIDAK ADA yang terverifikasi, karena tidak satu pun Activity terbaca. TIDAK ADA token yang dibeli 2 wallet atau lebih dalam jendela ini, apalagi 14 — tetapi ini adalah ketiadaan bukti, bukan bukti ketiadaan buy.
- Jadi TIDAK ADA SINYAL yang diklaim dari run ini (ambang: minimal 14 entitas berbeda membeli token baru yang SAMA dengan CA yang sama). Pembelian pada jendela ini untuk ke-54 dompet TIDAK DIKETAHUI, bukan nol. Jendela run 22 untuk dompet-dompet yang saat itu login-gated, serta jendela run 23, run 24, run 25, run 26, run 27, run 28, run 29, dan run 30 untuk semua dompet, juga tetap TIDAK DIKETAHUI.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada runtuhan entitas. Laporan ini tidak memuat data pendanaan; co-buy/co-hold saja TIDAK meruntuhkan entitas.
- Tidak ada pemicu screening paper, rekomendasi beli, promosi, atau pemicu trade dari run ini.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked tetap 2026-11-03T03:33:00+07:00; ringkasan run 31 per wallet; field saldo/holding tidak diubah; `last_run` diperbarui ke run 31). Baseline holdings tetap dari run 22 dan sebelumnya, dengan catatan jendela 03:33–13:38 WIB belum terbaca untuk semua dompet.
- Blokir yang tersisa: halaman dompet GMGN login-gated sejak ~17:27 WIB run 22 dan kini untuk semua 54 dompet pada run 31 (run ke-9 berturut-turut yang sepenuhnya login-gated: run 23–31). Penyelesaian butuh sign-in GMGN (di luar kewenangan baca-saja run ini — run ini TIDAK mencoba login) atau menunggu GMGN kembali menampilkan halaman publik tanpa login lalu membaca ulang ke-54 dompet itu. Diskrepansi BNB GMGN vs on-chain untuk 0xf6a8… tetap TIDAK TERSELESAIKAN, tidak dicek ulang (dompet login-gated pada run ini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
- SENYAP ke chat sesuai aturan run (tidak ada laporan rutin; tidak ada wallet yang memenuhi kriteria promosi terpercaya pada run ini).

## Run 32 — Selasa 2026-11-03, 15:22 WIB (gap: laporan browser belum diterima saat penulisan)

- Daftar dibaca dari `tier-ab-watch.md` + state setiap run: 54 entitas terpantau (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 1 + tambahan JAGENT 4, 2026-11-03 ~08:47 WIB). Ambang sinyal yang berlaku: minimal 14 entitas berbeda membeli token baru yang sama (floor(25% x 54)+1), bukan ambang 4 dari set 14 lama — set 14 lama sudah digantikan oleh promosi 2026-11-01 dan tambahan 2026-11-03. Daftar lama 23 alamat TIDAK dipakai. Catatan: body jadwal run ini masih menyebut set 14/ambang 4; run ini mengikuti set terpantau terkini di file + state (54 entitas), yang mencakup ke-14 dompet inti itu, dan ambang 14 yang lebih konservatif.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow. Pemeriksaan browser live read-only ke-54 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>) DIDISPATCH pada ~15:23 WIB, dengan instruksi eksplisit: bila login-gated, catat saja dan lanjut, JANGAN klik login.
- GAP YANG DICATAT JUJUR, mengikuti preseden Run 1/3/4/5/6:
  - Laporan per-wallet terperinci (holdings + trade terbaru per wallet) dari browser BELUM terkirim ke konteks run ini pada saat penulisan log.
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim — bukan karena wallet terbukti tidak membeli, melainkan karena bukti per-wallet belum diterima. Wallet yang tidak terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline / state run 31 TIDAK diubah: last_checked tetap 2026-11-03T03:33:00+07:00; hanya field `last_attempt` di state yang diperbarui sebagai penanda run ini.
  - Konteks dari run 31: run 31 FULLY LOGIN-GATED (0 dari 54 halaman memuat publik); jendela pembelian setelah 03:33 WIB 2026-11-03 dan semua jendela sejak run 22 partial gate / run 23–31 tetap UNKNOWN untuk ke-54 wallet, bukan nol, sampai laporan yang dapat dibaca diterima. Ini akan menjadi run ke-10 berturut-turut yang sepenuhnya login-gated bila laporan run 32 juga login-gated.
- Tindak lanjut: bila laporan browser run ini tiba, tambahkan sebagai adendum run ini dengan stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs baseline run 31. Bila laporan menunjukkan login-gated lagi, catat run 32 sebagai login-gated penuh dan jendela tetap UNKNOWN.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Adendum Run 32 — laporan browser diterima ~15:32 WIB

Pemeriksaan browser terukur runtime 15:23–15:32 WIB (laporan per-wallet 15:24–15:32 WIB, selisih akhir dalam 1 menit dicatat, waktu ukur runtime yang dipakai). Hasil: 54 dari 54 dompet LOGIN-GATED, 0 dompet publik. Setiap URL https://gmgn.ai/bsc/address/<alamat> hanya menampilkan beranda GMGN dengan panel "You are not logged in to GMGN", tanpa header dompet, saldo BNB, daftar holdings, maupun tab Activity. Sesuai instruksi, tidak ada klik Log in/Sign up/Connect, tidak ada upaya login, koneksi dompet, sign, beli/jual/follow, dan tidak ada bot challenge yang dilaporkan. Token yang tampak di beranda umum GMGN BUKAN holdings dompet yang diperiksa dan tidak dicatat sebagai holdings dompet mana pun.

Per dompet LOGIN-GATED (54 dompet — Activity TIDAK terbaca, BUKAN "tidak ada buy", BUKAN "No Data", dan TIDAK ada upaya login; saldo/holding tidak diubah di state):
- 15:24 WIB: 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6, 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02, 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5, 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7
- 15:25 WIB: 0x75642756e4ba4cc8fbe76df2239cada046cfc854, 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a, 0x892200223bdfb11d2506c5ab1cae9222ce253acc, 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c, 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e, 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462, 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf
- 15:26 WIB: 0xda91cefe240175e6fab56271110427a4195ab71f, 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc, 0x2325f175975abdbcde555c79cc8e63381d28551b, 0x9856bac497634a62a970233bc4b0f5bb52c844c1, 0x3628764a6576b8dfb31fba0aac6a333b64851423, 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e, 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c, 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74
- 15:27 WIB: 0xad94ee77d0e868d299fb3e92b9d67560257f656d, 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a, 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650, 0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b, 0xc621946845d0fd5d1dbc6d6beb3e22aed39d7050
- 15:28 WIB: 0xf795c5250f3d4006283a0d0dbb378dc0e69df923, 0x9cdd08f30188c2732cdbcac8eebf4e6e8bf0c1b2, 0xaa49e7fec503664a39598645c7a3fbfa0374380d, 0x82c6085f9ec2722fd6c8fc47577368a156a25b9b, 0x3154f6949285ee7ac1593bd2bdf974adb6731c32, 0xca4e67bb5737c095bd3a80f79ecc6607e5723f1a, 0xe9ed24db105a6b15f880025ed9ad024c06783895
- 15:29 WIB: 0x3a39aa05b149141a4bfc7d73611dceb0557b39c4, 0xcb08c02c0a386a10773a2c6589e7089a3dd5aca3, 0xb940e4cd40ea9e887cbc92879062676e2bc4a924, 0x4522e661d9c94ec54b37e71896351a7440ec4f07, 0x5b4beded36c1ea380abe8c6a6a0c4408f38e5024, 0xc6591fde9b44aa081062c9fc6ee48e443d24ef57, 0x362396125a55d932a09f0a5182140cbbcaf30b70
- 15:30 WIB: 0xf9689b9d0a675ff9ad876f1d766fb460dbde7d20, 0x2cc8192fc62e3640de91e75582cf3dbbd571b970, 0x97bd895f8123a7837368df410e7d308246c0b3e9, 0x1cce4ec5a7c5e8cfc8dedd771876c61e60b8b645, 0xc0c84518ced6a61d2a4f4a50bc0f438e0cb1031b, 0xc194efe22e874a3fe666b5de5a8fd369f12c32d5, 0xa952331ea48ea9c00c4608d8259c186021331f31
- 15:31 WIB: 0x92bc32975b0fbf1a19caf7cc6e3f9ea4092fd314, 0x9b519f5d52cdd03e4b10484829bc137eef1f8c1a, 0xfdec62fde1f1dc56c0ba5e50f4cae5d6c63762bf, 0x64e893a4c5c930b2cc68b054792cbc66344aeb9a, 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36, 0x341bed5b412968755f3dd6e9946636ac6f97457a, 0xd124dd5825ecaad959acdea6336926eb40aa0c9b
- 15:32 WIB: 0x5cf3f945620ba1a3cc9065a2086bfc728b172a0f, 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db

Hitungan sinyal run 32 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 32 (setelah 03:33 WIB 2026-11-03): TIDAK ADA yang terverifikasi, karena tidak satu pun Activity terbaca. TIDAK ADA token yang dibeli 2 wallet atau lebih dalam jendela ini, apalagi 14 — tetapi ini adalah ketiadaan bukti, bukan bukti ketiadaan buy.
- Jadi TIDAK ADA SINYAL yang diklaim dari run ini (ambang: minimal 14 entitas berbeda membeli token baru yang SAMA dengan CA yang sama). Pembelian pada jendela ini untuk ke-54 dompet TIDAK DIKETAHUI, bukan nol. Jendela run 22 untuk dompet-dompet yang saat itu login-gated, serta jendela run 23, run 24, run 25, run 26, run 27, run 28, run 29, run 30, dan run 31 untuk semua dompet, juga tetap TIDAK DIKETAHUI.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada runtuhan entitas. Laporan ini tidak memuat data pendanaan; co-buy/co-hold saja TIDAK meruntuhkan entitas.
- Tidak ada pemicu screening paper, rekomendasi beli, promosi, atau pemicu trade dari run ini.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked tetap 2026-11-03T03:33:00+07:00; ringkasan run 32 per wallet; field saldo/holding tidak diubah; `last_run` diperbarui ke run 32). Baseline holdings tetap dari run 22 dan sebelumnya, dengan catatan jendela 03:33–15:32 WIB belum terbaca untuk semua dompet.
- Blokir yang tersisa: halaman dompet GMGN login-gated sejak ~17:27 WIB run 22 dan kini untuk semua 54 dompet pada run 32 (run ke-10 berturut-turut yang sepenuhnya login-gated: run 23–32). Penyelesaian butuh sign-in GMGN (di luar kewenangan baca-saja run ini — run ini TIDAK mencoba login) atau menunggu GMGN kembali menampilkan halaman publik tanpa login lalu membaca ulang ke-54 dompet itu. Diskrepansi BNB GMGN vs on-chain untuk 0xf6a8… tetap TIDAK TERSELESAIKAN, tidak dicek ulang (dompet login-gated pada run ini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
- SENYAP ke chat sesuai aturan run (tidak ada laporan rutin; tidak ada wallet yang memenuhi kriteria promosi terpercaya pada run ini).

## Run 33 — Selasa 2026-11-03, 17:23–17:30 WIB (FULLY LOGIN-GATED, tanpa data publik)

- Daftar dibaca dari `tier-ab-watch.md` + state setiap run: 54 entitas terpantau (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 1 + tambahan JAGENT 4, 2026-11-03 ~08:47 WIB). Ambang sinyal yang berlaku: minimal 14 entitas berbeda membeli token baru yang sama (floor(25% x 54)+1), bukan ambang 4 dari set 14 lama — set 14 lama sudah digantikan oleh promosi 2026-11-01 dan tambahan 2026-11-03. Daftar lama 23 alamat TIDAK dipakai. Catatan: body jadwal run ini masih menyebut set 14/ambang 4; run ini mengikuti set terpantau terkini di file + state (54 entitas), yang mencakup ke-14 dompet inti itu, dan ambang 14 yang lebih konservatif.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow. Pemeriksaan browser live read-only ke-54 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>), runtime-measured 17:23–17:30 WIB (laporan per-wallet 17:24–17:30 WIB, selisih awal 1 menit dicatat, waktu ukur runtime yang dipakai). TIDAK ADA tantangan bot (CAPTCHA) yang dilaporkan.
- Hasil: 0 dari 54 halaman memuat data dompet publik. Setiap URL hanya menampilkan beranda GMGN dengan panel "You are not logged in to GMGN" — tanpa header dompet, saldo BNB, holdings, maupun tab Activity. Ini melanjutkan pola run 22 (parsial, gate menutup ~17:27 WIB 2026-11-02) dan run 23–32 yang sepenuhnya login-gated — run 33 adalah run ke-11 berturut-turut yang sepenuhnya login-gated.

Per dompet LOGIN-GATED (54 dompet — Activity TIDAK terbaca, BUKAN "tidak ada buy", BUKAN "No Data", dan TIDAK ada upaya login; saldo/holding tidak diubah di state):
- 17:24 WIB: 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6, 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02, 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5, 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7, 0x75642756e4ba4cc8fbe76df2239cada046cfc854, 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a, 0x892200223bdfb11d2506c5ab1cae9222ce253acc, 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c
- 17:25 WIB: 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e, 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462, 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf, 0xda91cefe240175e6fab56271110427a4195ab71f, 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc, 0x2325f175975abdbcde555c79cc8e63381d28551b, 0x9856bac497634a62a970233bc4b0f5bb52c844c1, 0x3628764a6576b8dfb31fba0aac6a333b64851423
- 17:26 WIB: 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e, 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c, 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74, 0xad94ee77d0e868d299fb3e92b9d67560257f656d, 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a, 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650, 0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b, 0xc621946845d0fd5d1dbc6d6beb3e22aed39d7050
- 17:27 WIB: 0xf795c5250f3d4006283a0d0dbb378dc0e69df923, 0x9cdd08f30188c2732cdbcac8eebf4e6e8bf0c1b2, 0xaa49e7fec503664a39598645c7a3fbfa0374380d, 0x82c6085f9ec2722fd6c8fc47577368a156a25b9b, 0x3154f6949285ee7ac1593bd2bdf974adb6731c32, 0xca4e67bb5737c095bd3a80f79ecc6607e5723f1a, 0xe9ed24db105a6b15f880025ed9ad024c06783895, 0x3a39aa05b149141a4bfc7d73611dceb0557b39c4, 0xcb08c02c0a386a10773a2c6589e7089a3dd5aca3
- 17:28 WIB: 0xb940e4cd40ea9e887cbc92879062676e2bc4a924, 0x4522e661d9c94ec54b37e71896351a7440ec4f07, 0x5b4beded36c1ea380abe8c6a6a0c4408f38e5024, 0xc6591fde9b44aa081062c9fc6ee48e443d24ef57, 0x362396125a55d932a09f0a5182140cbbcaf30b70, 0xf9689b9d0a675ff9ad876f1d766fb460dbde7d20, 0x2cc8192fc62e3640de91e75582cf3dbbd571b970, 0x97bd895f8123a7837368df410e7d308246c0b3e9
- 17:29 WIB: 0x1cce4ec5a7c5e8cfc8dedd771876c61e60b8b645, 0xc0c84518ced6a61d2a4f4a50bc0f438e0cb1031b, 0xc194efe22e874a3fe666b5de5a8fd369f12c32d5, 0xa952331ea48ea9c00c4608d8259c186021331f31, 0x92bc32975b0fbf1a19caf7cc6e3f9ea4092fd314, 0x9b519f5d52cdd03e4b10484829bc137eef1f8c1a, 0xfdec62fde1f1dc56c0ba5e50f4cae5d6c63762bf, 0x64e893a4c5c930b2cc68b054792cbc66344aeb9a, 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36, 0x341bed5b412968755f3dd6e9946636ac6f97457a
- 17:30 WIB: 0xd124dd5825ecaad959acdea6336926eb40aa0c9b, 0x5cf3f945620ba1a3cc9065a2086bfc728b172a0f, 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db

Hitungan sinyal run 33 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 33 (setelah 03:33 WIB 2026-11-03): TIDAK ADA yang terverifikasi, karena tidak satu pun Activity terbaca. TIDAK ADA token yang dibeli 2 wallet atau lebih dalam jendela ini, apalagi 14 — tetapi ini adalah ketiadaan bukti, bukan bukti ketiadaan buy.
- Jadi TIDAK ADA SINYAL yang diklaim dari run ini (ambang: minimal 14 entitas berbeda membeli token baru yang SAMA dengan CA yang sama). Pembelian pada jendela ini untuk ke-54 dompet TIDAK DIKETAHUI, bukan nol. Jendela run 22 untuk dompet-dompet yang saat itu login-gated, serta jendela run 23, run 24, run 25, run 26, run 27, run 28, run 29, run 30, run 31, dan run 32 untuk semua dompet, juga tetap TIDAK DIKETAHUI.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada runtuhan entitas. Laporan ini tidak memuat data pendanaan; co-buy/co-hold saja TIDAK meruntuhkan entitas.
- Tidak ada pemicu screening paper, rekomendasi beli, promosi, atau pemicu trade dari run ini.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked tetap 2026-11-03T03:33:00+07:00; ringkasan run 33 per wallet; field saldo/holding tidak diubah; `last_run` diperbarui ke run 33). Baseline holdings tetap dari run 22 dan sebelumnya, dengan catatan jendela 03:33–17:30 WIB belum terbaca untuk semua dompet.
- Blokir yang tersisa: halaman dompet GMGN login-gated sejak ~17:27 WIB run 22 dan kini untuk semua 54 dompet pada run 33 (run ke-11 berturut-turut yang sepenuhnya login-gated: run 23–33). Penyelesaian butuh sign-in GMGN (di luar kewenangan baca-saja run ini — run ini TIDAK mencoba login) atau menunggu GMGN kembali menampilkan halaman publik tanpa login lalu membaca ulang ke-54 dompet itu. Diskrepansi BNB GMGN vs on-chain untuk 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc tetap TIDAK TERSELESAIKAN, tidak dicek ulang (dompet login-gated pada run ini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
- SENYAP ke chat sesuai aturan run (tidak ada laporan rutin; tidak ada wallet yang memenuhi kriteria promosi terpercaya pada run ini).

## Run 34 — Selasa 2026-11-03, 19:23–19:29 WIB (FULLY LOGIN-GATED, tanpa data publik)

- Daftar dibaca dari `tier-ab-watch.md` + state setiap run: 54 entitas terpantau (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 1 + tambahan JAGENT 4, 2026-11-03 ~08:47 WIB). Ambang sinyal yang berlaku: minimal 14 entitas berbeda membeli token baru yang sama (floor(25% x 54)+1), bukan ambang 4 dari set 14 lama — set 14 lama sudah digantikan oleh promosi 2026-11-01 dan tambahan 2026-11-03. Daftar lama 23 alamat TIDAK dipakai. Catatan proses run ini: dispatch pertama hanya memuat 14 dompet inti (mengikuti bunyi body jadwal lama), lalu dilanjutkan pada tugas browser yang sama ke 40 dompet terpantau sisanya, sehingga run 34 tetap mencakup ke-54 dompet seperti run 32–33; body jadwal yang masih menyebut set 14/ambang 4 tidak mengubah cakupan ini.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow. Pemeriksaan browser live read-only ke-54 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>), runtime-measured 19:23–19:24 WIB untuk 14 dompet inti dan 19:25–19:29 WIB untuk 40 dompet sisanya. TIDAK ADA tantangan bot (CAPTCHA) yang dilaporkan.
- Hasil: 0 dari 54 halaman memuat data dompet publik. Setiap URL hanya menampilkan beranda GMGN dengan panel "You are not logged in to GMGN" — tanpa header dompet, saldo BNB, holdings, maupun tab Activity. Ini melanjutkan pola run 22 (parsial, gate menutup ~17:27 WIB 2026-11-02) dan run 23–33 yang sepenuhnya login-gated — run 34 adalah run ke-12 berturut-turut yang sepenuhnya login-gated. Daftar umum Picks/Trending/Callout di panel samping beranda BUKAN holdings maupun Activity dompet yang diperiksa dan tidak dicatat sebagai data dompet mana pun.

Per dompet LOGIN-GATED (54 dompet — Activity TIDAK terbaca, BUKAN "tidak ada buy", BUKAN "No Data", dan TIDAK ada upaya login; saldo/holding tidak diubah di state):
- 19:23 WIB: 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6, 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02, 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5, 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7, 0x75642756e4ba4cc8fbe76df2239cada046cfc854, 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a, 0x892200223bdfb11d2506c5ab1cae9222ce253acc
- 19:24 WIB: 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c, 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e, 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462, 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf, 0xda91cefe240175e6fab56271110427a4195ab71f, 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc, 0x2325f175975abdbcde555c79cc8e63381d28551b
- 19:25 WIB: 0x9856bac497634a62a970233bc4b0f5bb52c844c1, 0x3628764a6576b8dfb31fba0aac6a333b64851423, 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e, 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c, 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74, 0xad94ee77d0e868d299fb3e92b9d67560257f656d, 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a, 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650
- 19:26 WIB: 0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b, 0xc621946845d0fd5d1dbc6d6beb3e22aed39d7050, 0xf795c5250f3d4006283a0d0dbb378dc0e69df923, 0x9cdd08f30188c2732cdbcac8eebf4e6e8bf0c1b2, 0xaa49e7fec503664a39598645c7a3fbfa0374380d, 0x82c6085f9ec2722fd6c8fc47577368a156a25b9b, 0x3154f6949285ee7ac1593bd2bdf974adb6731c32, 0xca4e67bb5737c095bd3a80f79ecc6607e5723f1a, 0xe9ed24db105a6b15f880025ed9ad024c06783895
- 19:27 WIB: 0x3a39aa05b149141a4bfc7d73611dceb0557b39c4, 0xcb08c02c0a386a10773a2c6589e7089a3dd5aca3, 0xb940e4cd40ea9e887cbc92879062676e2bc4a924, 0x4522e661d9c94ec54b37e71896351a7440ec4f07, 0x5b4beded36c1ea380abe8c6a6a0c4408f38e5024, 0xc6591fde9b44aa081062c9fc6ee48e443d24ef57, 0x362396125a55d932a09f0a5182140cbbcaf30b70, 0xf9689b9d0a675ff9ad876f1d766fb460dbde7d20
- 19:28 WIB: 0x2cc8192fc62e3640de91e75582cf3dbbd571b970, 0x1cce4ec5a7c5e8cfc8dedd771876c61e60b8b645, 0xc0c84518ced6a61d2a4f4a50bc0f438e0cb1031b, 0xc194efe22e874a3fe666b5de5a8fd369f12c32d5, 0xa952331ea48ea9c00c4608d8259c186021331f31, 0x92bc32975b0fbf1a19caf7cc6e3f9ea4092fd314, 0x9b519f5d52cdd03e4b10484829bc137eef1f8c1a, 0xfdec62fde1f1dc56c0ba5e50f4cae5d6c63762bf, 0x64e893a4c5c930b2cc68b054792cbc66344aeb9a, 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36, 0x97bd895f8123a7837368df410e7d308246c0b3e9, 0x341bed5b412968755f3dd6e9946636ac6f97457a, 0xd124dd5825ecaad959acdea6336926eb40aa0c9b
- 19:29 WIB: 0x5cf3f945620ba1a3cc9065a2086bfc728b172a0f, 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db

Hitungan sinyal run 34 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 34 (setelah 03:33 WIB 2026-11-03): TIDAK ADA yang terverifikasi, karena tidak satu pun Activity terbaca. TIDAK ADA token yang dibeli 2 wallet atau lebih dalam jendela ini, apalagi 14 — tetapi ini adalah ketiadaan bukti, bukan bukti ketiadaan buy.
- Jadi TIDAK ADA SINYAL yang diklaim dari run ini (ambang: minimal 14 entitas berbeda membeli token baru yang SAMA dengan CA yang sama). Pembelian pada jendela ini untuk ke-54 dompet TIDAK DIKETAHUI, bukan nol. Jendela run 22 untuk dompet-dompet yang saat itu login-gated, serta jendela run 23, run 24, run 25, run 26, run 27, run 28, run 29, run 30, run 31, run 32, dan run 33 untuk semua dompet, juga tetap TIDAK DIKETAHUI.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada runtuhan entitas. Laporan ini tidak memuat data pendanaan; co-buy/co-hold saja TIDAK meruntuhkan entitas.
- Tidak ada pemicu screening paper, rekomendasi beli, promosi, atau pemicu trade dari run ini.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked tetap 2026-11-03T03:33:00+07:00; ringkasan run 34 per wallet; field saldo/holding tidak diubah; `last_run` diperbarui ke run 34). Baseline holdings tetap dari run 22 dan sebelumnya, dengan catatan jendela 03:33–19:29 WIB belum terbaca untuk semua dompet.
- Blokir yang tersisa: halaman dompet GMGN login-gated sejak ~17:27 WIB run 22 dan kini untuk semua 54 dompet pada run 34 (run ke-12 berturut-turut yang sepenuhnya login-gated: run 23–34). Penyelesaian butuh sign-in GMGN (di luar kewenangan baca-saja run ini — run ini TIDAK mencoba login) atau menunggu GMGN kembali menampilkan halaman publik tanpa login lalu membaca ulang ke-54 dompet itu. Diskrepansi BNB GMGN vs on-chain untuk 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc tetap TIDAK TERSELESAIKAN, tidak dicek ulang (dompet login-gated pada run ini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
- SENYAP ke chat sesuai aturan run (tidak ada laporan rutin; tidak ada wallet yang memenuhi kriteria promosi terpercaya pada run ini).

## Run 35 — Selasa 2026-11-03, 21:23–21:30 WIB (FULLY LOGIN-GATED, tanpa data publik)

- Daftar dibaca dari `tier-ab-watch.md` + state setiap run: 54 entitas terpantau (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 1 + tambahan JAGENT 4, 2026-11-03 ~08:47 WIB). Ambang sinyal yang berlaku: minimal 14 entitas berbeda membeli token baru yang sama (floor(25% x 54)+1), bukan ambang 4 dari set 14 lama — set 14 lama sudah digantikan oleh promosi 2026-11-01 dan tambahan 2026-11-03. Daftar lama 23 alamat TIDAK dipakai. Catatan: body jadwal run ini masih menyebut set 14/ambang 4; run ini mengikuti set terpantau terkini di file + state (54 entitas), yang mencakup ke-14 dompet inti itu, dan ambang 14 yang lebih konservatif.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow. Pemeriksaan browser live read-only ke-54 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>), harness-measured 21:23–21:30 WIB (laporan per-batch browser 21:23–21:29 WIB, selisih akhir 1 menit dicatat, waktu ukur harness yang dipakai). TIDAK ADA tantangan bot (CAPTCHA) yang dilaporkan.
- Hasil: 0 dari 54 halaman memuat data dompet publik. Setiap URL hanya menampilkan beranda GMGN dengan panel "You are not logged in to GMGN" — tanpa header dompet, saldo BNB, holdings, maupun tab Activity. Ini melanjutkan pola run 22 (parsial, gate menutup ~17:27 WIB 2026-11-02) dan run 23–34 yang sepenuhnya login-gated — run 35 adalah run ke-13 berturut-turut yang sepenuhnya login-gated. Daftar umum Picks/Trending/Callout di panel samping beranda BUKAN holdings maupun Activity dompet yang diperiksa dan tidak dicatat sebagai data dompet mana pun.

Per dompet LOGIN-GATED (54 dompet — Activity TIDAK terbaca, BUKAN "tidak ada buy", BUKAN "No Data", dan TIDAK ada upaya login; saldo/holding tidak diubah di state):
- 21:23–21:25 WIB (batch 1, dompet 1–18): 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6, 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02, 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5, 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7, 0x75642756e4ba4cc8fbe76df2239cada046cfc854, 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a, 0x892200223bdfb11d2506c5ab1cae9222ce253acc, 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c, 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e, 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462, 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf, 0xda91cefe240175e6fab56271110427a4195ab71f, 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc, 0x2325f175975abdbcde555c79cc8e63381d28551b, 0x9856bac497634a62a970233bc4b0f5bb52c844c1, 0x3628764a6576b8dfb31fba0aac6a333b64851423, 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e, 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c
- 21:25–21:28 WIB (batch 2, dompet 19–36): 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74, 0xad94ee77d0e868d299fb3e92b9d67560257f656d, 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a, 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650, 0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b, 0xc621946845d0fd5d1dbc6d6beb3e22aed39d7050, 0xf795c5250f3d4006283a0d0dbb378dc0e69df923, 0x9cdd08f30188c2732cdbcac8eebf4e6e8bf0c1b2, 0xaa49e7fec503664a39598645c7a3fbfa0374380d, 0x82c6085f9ec2722fd6c8fc47577368a156a25b9b, 0x3154f6949285ee7ac1593bd2bdf974adb6731c32, 0xca4e67bb5737c095bd3a80f79ecc6607e5723f1a, 0xe9ed24db105a6b15f880025ed9ad024c06783895, 0x3a39aa05b149141a4bfc7d73611dceb0557b39c4, 0xcb08c02c0a386a10773a2c6589e7089a3dd5aca3, 0xb940e4cd40ea9e887cbc92879062676e2bc4a924, 0x4522e661d9c94ec54b37e71896351a7440ec4f07, 0x5b4beded36c1ea380abe8c6a6a0c4408f38e5024
- 21:28–21:29 WIB (batch 3, dompet 37–54): 0xc6591fde9b44aa081062c9fc6ee48e443d24ef57, 0x362396125a55d932a09f0a5182140cbbcaf30b70, 0xf9689b9d0a675ff9ad876f1d766fb460dbde7d20, 0x2cc8192fc62e3640de91e75582cf3dbbd571b970, 0x97bd895f8123a7837368df410e7d308246c0b3e9, 0x1cce4ec5a7c5e8cfc8dedd771876c61e60b8b645, 0xc0c84518ced6a61d2a4f4a50bc0f438e0cb1031b, 0xc194efe22e874a3fe666b5de5a8fd369f12c32d5, 0xa952331ea48ea9c00c4608d8259c186021331f31, 0x92bc32975b0fbf1a19caf7cc6e3f9ea4092fd314, 0x9b519f5d52cdd03e4b10484829bc137eef1f8c1a, 0xfdec62fde1f1dc56c0ba5e50f4cae5d6c63762bf, 0x64e893a4c5c930b2cc68b054792cbc66344aeb9a, 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36, 0x341bed5b412968755f3dd6e9946636ac6f97457a, 0xd124dd5825ecaad959acdea6336926eb40aa0c9b, 0x5cf3f945620ba1a3cc9065a2086bfc728b172a0f, 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db

Hitungan sinyal run 35 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 35 (setelah 03:33 WIB 2026-11-03): TIDAK ADA yang terverifikasi, karena tidak satu pun Activity terbaca. TIDAK ADA token yang dibeli 2 wallet atau lebih dalam jendela ini, apalagi 14 — tetapi ini adalah ketiadaan bukti, bukan bukti ketiadaan buy.
- Jadi TIDAK ADA SINYAL yang diklaim dari run ini (ambang: minimal 14 entitas berbeda membeli token baru yang SAMA dengan CA yang sama). Pembelian pada jendela ini untuk ke-54 dompet TIDAK DIKETAHUI, bukan nol. Jendela run 22 untuk dompet-dompet yang saat itu login-gated, serta jendela run 23, run 24, run 25, run 26, run 27, run 28, run 29, run 30, run 31, run 32, run 33, dan run 34 untuk semua dompet, juga tetap TIDAK DIKETAHUI.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada runtuhan entitas. Laporan ini tidak memuat data pendanaan; co-buy/co-hold saja TIDAK meruntuhkan entitas.
- Tidak ada pemicu screening paper, rekomendasi beli, promosi, atau pemicu trade dari run ini.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked tetap 2026-11-03T03:33:00+07:00; ringkasan run 35 per wallet; field saldo/holding tidak diubah; `last_run` diperbarui ke run 35). Baseline holdings tetap dari run 22 dan sebelumnya, dengan catatan jendela 03:33–21:30 WIB belum terbaca untuk semua dompet.
- Blokir yang tersisa: halaman dompet GMGN login-gated sejak ~17:27 WIB run 22 dan kini untuk semua 54 dompet pada run 35 (run ke-13 berturut-turut yang sepenuhnya login-gated: run 23–35). Penyelesaian butuh sign-in GMGN (di luar kewenangan baca-saja run ini — run ini TIDAK mencoba login) atau menunggu GMGN kembali menampilkan halaman publik tanpa login lalu membaca ulang ke-54 dompet itu. Diskrepansi BNB GMGN vs on-chain untuk 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc tetap TIDAK TERSELESAIKAN, tidak dicek ulang (dompet login-gated pada run ini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
- SENYAP ke chat sesuai aturan run (tidak ada laporan rutin; tidak ada wallet yang memenuhi kriteria promosi terpercaya pada run ini).

## Run 36 — Kamis 2026-11-05, 00:24–00:31 WIB (FULLY LOGIN-GATED, tanpa data publik)

- Daftar dibaca dari `tier-ab-watch.md` + state setiap run: 54 entitas terpantau (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 1 + tambahan JAGENT 4, 2026-11-03 ~08:47 WIB). Ambang sinyal saat ini: minimal 14 entitas berbeda membeli token baru yang sama (floor(25% x 54)+1), bukan ambang 4 dari set 14 lama.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow. Pemeriksaan browser live read-only ke-54 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>), harness-measured 00:24–00:31 WIB (jadwal run: Rabu 2026-11-04 23:22 WIB).
- Hasil: FULLY LOGIN-GATED — 0 dari 54 halaman memuat publik, 54 login-gated, 0 tantangan bot/CAPTCHA yang dilaporkan. Setiap URL hanya menampilkan beranda GMGN dengan panel "You are not logged in to GMGN", tanpa header dompet, saldo BNB, daftar holdings, maupun tab Activity. Tidak ada klik Log in/Sign up/Connect, tidak ada upaya login.
- Per dompet: ke-54 dompet LOGIN-GATED; saldo/holdings/Activity tidak ditampilkan untuk semuanya, sehingga tidak ada tipe Buy/Sell/Tx In/Tx Out/Add/Burn, simbol token, jumlah, nilai, maupun label waktu yang dapat dicatat. Tidak ada kesimpulan saldo nol yang dibuat dari hasil ini.
- Hitungan sinyal: TIDAK ADA SINYAL yang diklaim dari run ini (ambang: minimal 14 entitas berbeda membeli token baru yang SAMA dengan CA yang sama). Pembelian pada jendela ini untuk ke-54 dompet TIDAK DIKETAHUI, bukan nol. Jendela pembelian setelah 03:33 WIB 2026-11-03 dan semua jendela sejak run 22 partial gate / run 23–35 juga tetap TIDAK DIKETAHUI.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada runtuhan entitas. Laporan ini tidak memuat data pendanaan; co-buy/co-hold saja TIDAK meruntuhkan entitas.
- Tidak ada pemicu screening paper, rekomendasi beli, promosi, atau pemicu trade dari run ini.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked tetap 2026-11-03T03:33:00+07:00; ringkasan run 36 per wallet; field saldo/holding tidak diubah; `last_run` diperbarui ke run 36). Baseline holdings tetap dari run 22 dan sebelumnya, dengan catatan jendela 03:33 WIB 2026-11-03–00:31 WIB 2026-11-05 belum terbaca untuk semua dompet.
- Blokir yang tersisa: halaman dompet GMGN login-gated sejak ~17:27 WIB run 22 dan kini untuk semua 54 dompet pada run 36 (run ke-14 berturut-turut yang sepenuhnya login-gated: run 23–36). Penyelesaian butuh sign-in GMGN (di luar kewenangan baca-saja run ini — run ini TIDAK mencoba login) atau menunggu GMGN kembali menampilkan halaman publik tanpa login lalu membaca ulang ke-54 dompet itu. Diskrepansi BNB GMGN vs on-chain untuk 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc tetap TIDAK TERSELESAIKAN, tidak dicek ulang (dompet login-gated pada run ini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
- SENYAP ke chat sesuai aturan run (tidak ada laporan rutin; tidak ada wallet yang memenuhi kriteria promosi terpercaya pada run ini).

## Run 37 — Kamis 2026-11-05, 01:23–01:41 WIB (FULLY LOGIN-GATED, tanpa data publik)

- Daftar dibaca dari `tier-ab-watch.md` + state setiap run: 54 entitas terpantau (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 1 + tambahan JAGENT 4, 2026-11-03 ~08:47 WIB). Ambang sinyal yang berlaku: minimal 14 entitas berbeda membeli token baru yang sama (floor(25% x 54)+1), bukan ambang 4 dari set 14 lama — set 14 lama sudah digantikan oleh promosi 2026-11-01 dan tambahan 2026-11-03. Daftar lama 23 alamat TIDAK dipakai. Catatan: body jadwal run ini masih menyebut set 14/ambang 4; run ini mengikuti set terpantau terkini di file + state (54 entitas), yang mencakup ke-14 dompet inti itu, dan ambang 14 yang lebih konservatif.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow. Pemeriksaan browser live read-only ke-54 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>), harness-measured 01:23–01:41 WIB (jendela laporan browser 01:24–01:40 WIB; selisih 1 menit di awal/akhir dicatat, waktu ukur harness yang dipakai). TIDAK ADA tantangan bot (CAPTCHA) yang dilaporkan.
- Hasil: 0 dari 54 halaman memuat data dompet publik. Setiap URL hanya menampilkan beranda GMGN dengan panel "You are not logged in to GMGN" — tanpa header dompet, saldo BNB, holdings, maupun tab Activity. Ini melanjutkan pola run 22 (parsial, gate menutup ~17:27 WIB 2026-11-02) dan run 23–36 yang sepenuhnya login-gated — run 37 adalah run ke-15 berturut-turut yang sepenuhnya login-gated. Daftar umum Picks/Trending/Callout di panel samping beranda BUKAN holdings maupun Activity dompet yang diperiksa dan tidak dicatat sebagai data dompet mana pun.

Per dompet LOGIN-GATED (54 dompet — Activity TIDAK terbaca, BUKAN "tidak ada buy", BUKAN "No Data", dan TIDAK ada upaya login; saldo/holding tidak diubah di state):
- Core 14: 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6, 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02, 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5, 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7, 0x75642756e4ba4cc8fbe76df2239cada046cfc854, 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a, 0x892200223bdfb11d2506c5ab1cae9222ce253acc, 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c, 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e, 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462, 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf, 0xda91cefe240175e6fab56271110427a4195ab71f, 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc, 0x2325f175975abdbcde555c79cc8e63381d28551b
- Tier C 35: 0x9856bac497634a62a970233bc4b0f5bb52c844c1, 0x3628764a6576b8dfb31fba0aac6a333b64851423, 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e, 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c, 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74, 0xad94ee77d0e868d299fb3e92b9d67560257f656d, 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a, 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650, 0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b, 0xc621946845d0fd5d1dbc6d6beb3e22aed39d7050, 0xf795c5250f3d4006283a0d0dbb378dc0e69df923, 0x9cdd08f30188c2732cdbcac8eebf4e6e8bf0c1b2, 0xaa49e7fec503664a39598645c7a3fbfa0374380d, 0x82c6085f9ec2722fd6c8fc47577368a156a25b9b, 0x3154f6949285ee7ac1593bd2bdf974adb6731c32, 0xca4e67bb5737c095bd3a80f79ecc6607e5723f1a, 0xe9ed24db105a6b15f880025ed9ad024c06783895, 0x3a39aa05b149141a4bfc7d73611dceb0557b39c4, 0xcb08c02c0a386a10773a2c6589e7089a3dd5aca3, 0xb940e4cd40ea9e887cbc92879062676e2bc4a924, 0x4522e661d9c94ec54b37e71896351a7440ec4f07, 0x5b4beded36c1ea380abe8c6a6a0c4408f38e5024, 0xc6591fde9b44aa081062c9fc6ee48e443d24ef57, 0x362396125a55d932a09f0a5182140cbbcaf30b70, 0xf9689b9d0a675ff9ad876f1d766fb460dbde7d20, 0x2cc8192fc62e3640de91e75582cf3dbbd571b970, 0x97bd895f8123a7837368df410e7d308246c0b3e9, 0x1cce4ec5a7c5e8cfc8dedd771876c61e60b8b645, 0xc0c84518ced6a61d2a4f4a50bc0f438e0cb1031b, 0xc194efe22e874a3fe666b5de5a8fd369f12c32d5, 0xa952331ea48ea9c00c4608d8259c186021331f31, 0x92bc32975b0fbf1a19caf7cc6e3f9ea4092fd314, 0x9b519f5d52cdd03e4b10484829bc137eef1f8c1a, 0xfdec62fde1f1dc56c0ba5e50f4cae5d6c63762bf, 0x64e893a4c5c930b2cc68b054792cbc66344aeb9a
- Promosi individual 1: 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36
- Tambahan JAGENT 4: 0x341bed5b412968755f3dd6e9946636ac6f97457a, 0xd124dd5825ecaad959acdea6336926eb40aa0c9b, 0x5cf3f945620ba1a3cc9065a2086bfc728b172a0f, 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db

Hitungan sinyal run 37 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 37 (setelah 03:33 WIB 2026-11-03): TIDAK ADA yang terverifikasi, karena tidak satu pun Activity terbaca. TIDAK ADA token yang dibeli 2 wallet atau lebih dalam jendela ini, apalagi 14 — tetapi ini adalah ketiadaan bukti, bukan bukti ketiadaan buy.
- Jadi TIDAK ADA SINYAL yang diklaim dari run ini (ambang: minimal 14 entitas berbeda membeli token baru yang SAMA dengan CA yang sama). Pembelian pada jendela ini untuk ke-54 dompet TIDAK DIKETAHUI, bukan nol. Jendela run 22 untuk dompet-dompet yang saat itu login-gated, serta jendela run 23, run 24, run 25, run 26, run 27, run 28, run 29, run 30, run 31, run 32, run 33, run 34, run 35, dan run 36 untuk semua dompet, juga tetap TIDAK DIKETAHUI.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada runtuhan entitas. Laporan ini tidak memuat data pendanaan; co-buy/co-hold saja TIDAK meruntuhkan entitas.
- Tidak ada pemicu screening paper, rekomendasi beli, promosi, atau pemicu trade dari run ini.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked tetap 2026-11-03T03:33:00+07:00; ringkasan run 37 per wallet; field saldo/holding tidak diubah; `last_run` diperbarui ke run 37). Baseline holdings tetap dari run 22 dan sebelumnya, dengan catatan jendela 03:33 WIB 2026-11-03–01:41 WIB 2026-11-05 belum terbaca untuk semua dompet.
- Blokir yang tersisa: halaman dompet GMGN login-gated sejak ~17:27 WIB run 22 dan kini untuk semua 54 dompet pada run 37 (run ke-15 berturut-turut yang sepenuhnya login-gated: run 23–37). Penyelesaian butuh sign-in GMGN (di luar kewenangan baca-saja run ini — run ini TIDAK mencoba login) atau menunggu GMGN kembali menampilkan halaman publik tanpa login lalu membaca ulang ke-54 dompet itu. Diskrepansi BNB GMGN vs on-chain untuk 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc tetap TIDAK TERSELESAIKAN, tidak dicek ulang (dompet login-gated pada run ini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
- SENYAP ke chat sesuai aturan run (tidak ada laporan rutin; tidak ada wallet yang memenuhi kriteria promosi terpercaya pada run ini).

## Run 38 — Kamis 2026-11-05, 03:24–03:32 WIB (FULLY LOGIN-GATED, tanpa data publik)

- Daftar dibaca dari `tier-ab-watch.md` + state setiap run: 54 entitas terpantau (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 1 + tambahan JAGENT 4, 2026-11-03 ~08:47 WIB). Ambang sinyal yang berlaku: minimal 14 entitas berbeda membeli token baru yang sama (floor(25% x 54)+1), bukan ambang 4 dari set 14 lama — set 14 lama sudah digantikan oleh promosi 2026-11-01 dan tambahan 2026-11-03. Daftar lama 23 alamat TIDAK dipakai. Catatan: body jadwal run ini masih menyebut set 14/ambang 4; run ini mengikuti set terpantau terkini di file + state (54 entitas), yang mencakup ke-14 dompet inti itu, dan ambang 14 yang lebih konservatif.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow. Pemeriksaan browser live read-only ke-54 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>), harness-measured 03:24–03:32 WIB (jendela laporan browser 03:24–03:31 WIB; selisih 1 menit di akhir dicatat, waktu ukur harness yang dipakai). TIDAK ADA tantangan bot (CAPTCHA) yang dilaporkan.
- Hasil: 0 dari 54 halaman memuat data dompet publik. Setiap URL hanya menampilkan beranda GMGN dengan panel "You are not logged in to GMGN" — tanpa header dompet, saldo BNB, holdings, maupun tab Activity. Ini melanjutkan pola run 22 (parsial, gate menutup ~17:27 WIB 2026-11-02) dan run 23–37 yang sepenuhnya login-gated — run 38 adalah run ke-16 berturut-turut yang sepenuhnya login-gated. Daftar umum Picks/Trending/Callout di panel samping beranda BUKAN holdings maupun Activity dompet yang diperiksa dan tidak dicatat sebagai data dompet mana pun.

Per dompet LOGIN-GATED (54 dompet — Activity TIDAK terbaca, BUKAN "tidak ada buy", BUKAN "No Data", dan TIDAK ada upaya login; saldo/holding tidak diubah di state):
- Core 14: 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6, 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02, 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5, 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7, 0x75642756e4ba4cc8fbe76df2239cada046cfc854, 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a, 0x892200223bdfb11d2506c5ab1cae9222ce253acc, 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c, 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e, 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462, 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf, 0xda91cefe240175e6fab56271110427a4195ab71f, 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc, 0x2325f175975abdbcde555c79cc8e63381d28551b
- Tier C 35: 0x9856bac497634a62a970233bc4b0f5bb52c844c1, 0x3628764a6576b8dfb31fba0aac6a333b64851423, 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e, 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c, 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74, 0xad94ee77d0e868d299fb3e92b9d67560257f656d, 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a, 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650, 0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b, 0xc621946845d0fd5d1dbc6d6beb3e22aed39d7050, 0xf795c5250f3d4006283a0d0dbb378dc0e69df923, 0x9cdd08f30188c2732cdbcac8eebf4e6e8bf0c1b2, 0xaa49e7fec503664a39598645c7a3fbfa0374380d, 0x82c6085f9ec2722fd6c8fc47577368a156a25b9b, 0x3154f6949285ee7ac1593bd2bdf974adb6731c32, 0xca4e67bb5737c095bd3a80f79ecc6607e5723f1a, 0xe9ed24db105a6b15f880025ed9ad024c06783895, 0x3a39aa05b149141a4bfc7d73611dceb0557b39c4, 0xcb08c02c0a386a10773a2c6589e7089a3dd5aca3, 0xb940e4cd40ea9e887cbc92879062676e2bc4a924, 0x4522e661d9c94ec54b37e71896351a7440ec4f07, 0x5b4beded36c1ea380abe8c6a6a0c4408f38e5024, 0xc6591fde9b44aa081062c9fc6ee48e443d24ef57, 0x362396125a55d932a09f0a5182140cbbcaf30b70, 0xf9689b9d0a675ff9ad876f1d766fb460dbde7d20, 0x2cc8192fc62e3640de91e75582cf3dbbd571b970, 0x97bd895f8123a7837368df410e7d308246c0b3e9, 0x1cce4ec5a7c5e8cfc8dedd771876c61e60b8b645, 0xc0c84518ced6a61d2a4f4a50bc0f438e0cb1031b, 0xc194efe22e874a3fe666b5de5a8fd369f12c32d5, 0xa952331ea48ea9c00c4608d8259c186021331f31, 0x92bc32975b0fbf1a19caf7cc6e3f9ea4092fd314, 0x9b519f5d52cdd03e4b10484829bc137eef1f8c1a, 0xfdec62fde1f1dc56c0ba5e50f4cae5d6c63762bf, 0x64e893a4c5c930b2cc68b054792cbc66344aeb9a
- Promosi individual 1: 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36
- Tambahan JAGENT 4: 0x341bed5b412968755f3dd6e9946636ac6f97457a, 0xd124dd5825ecaad959acdea6336926eb40aa0c9b, 0x5cf3f945620ba1a3cc9065a2086bfc728b172a0f, 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db

Hitungan sinyal run 38 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 38 (setelah 03:33 WIB 2026-11-03): TIDAK ADA yang terverifikasi, karena tidak satu pun Activity terbaca. TIDAK ADA token yang dibeli 2 wallet atau lebih dalam jendela ini, apalagi 14 — tetapi ini adalah ketiadaan bukti, bukan bukti ketiadaan buy.
- Jadi TIDAK ADA SINYAL yang diklaim dari run ini (ambang: minimal 14 entitas berbeda membeli token baru yang SAMA dengan CA yang sama). Pembelian pada jendela ini untuk ke-54 dompet TIDAK DIKETAHUI, bukan nol. Jendela run 22 untuk dompet-dompet yang saat itu login-gated, serta jendela run 23, run 24, run 25, run 26, run 27, run 28, run 29, run 30, run 31, run 32, run 33, run 34, run 35, run 36, dan run 37 untuk semua dompet, juga tetap TIDAK DIKETAHUI.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada runtuhan entitas. Laporan ini tidak memuat data pendanaan; co-buy/co-hold saja TIDAK meruntuhkan entitas.
- Tidak ada pemicu screening paper, rekomendasi beli, promosi, atau pemicu trade dari run ini.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked tetap 2026-11-03T03:33:00+07:00; ringkasan run 38 per wallet; field saldo/holding tidak diubah; `last_run` diperbarui ke run 38). Baseline holdings tetap dari run 22 dan sebelumnya, dengan catatan jendela 03:33 WIB 2026-11-03–03:32 WIB 2026-11-05 belum terbaca untuk semua dompet.
- Blokir yang tersisa: halaman dompet GMGN login-gated sejak ~17:27 WIB run 22 dan kini untuk semua 54 dompet pada run 38 (run ke-16 berturut-turut yang sepenuhnya login-gated: run 23–38). Penyelesaian butuh sign-in GMGN (di luar kewenangan baca-saja run ini — run ini TIDAK mencoba login) atau menunggu GMGN kembali menampilkan halaman publik tanpa login lalu membaca ulang ke-54 dompet itu. Diskrepansi BNB GMGN vs on-chain untuk 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc tetap TIDAK TERSELESAIKAN, tidak dicek ulang (dompet login-gated pada run ini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
- SENYAP ke chat sesuai aturan run (tidak ada laporan rutin; tidak ada wallet yang memenuhi kriteria promosi terpercaya pada run ini).

## Run 39 — Kamis 2026-11-05, 05:23–05:32 WIB (FULLY LOGIN-GATED, tanpa data publik)

- Daftar dibaca dari `tier-ab-watch.md` + state setiap run: 54 entitas terpantau (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 1 + tambahan JAGENT 4, 2026-11-03 ~08:47 WIB). Ambang sinyal yang berlaku: minimal 14 entitas berbeda membeli token baru yang sama (floor(25% x 54)+1), bukan ambang 4 dari set 14 lama — set 14 lama sudah digantikan oleh promosi 2026-11-01 dan tambahan 2026-11-03. Daftar lama 23 alamat TIDAK dipakai. Catatan: body jadwal run ini masih menyebut set 14/ambang 4; run ini mengikuti set terpantau terkini di file + state (54 entitas), yang mencakup ke-14 dompet inti itu, dan ambang 14 yang lebih konservatif.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow. Pemeriksaan browser live read-only ke-54 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>), harness-measured 05:23–05:32 WIB (jendela laporan browser 05:24–05:31 WIB; selisih 1 menit di awal/akhir dicatat, waktu ukur harness yang dipakai). TIDAK ADA tantangan bot (CAPTCHA) yang dilaporkan.
- Hasil: 0 dari 54 halaman memuat data dompet publik. Setiap URL hanya menampilkan beranda GMGN dengan panel "You are not logged in to GMGN" — tanpa header dompet, saldo BNB, holdings, maupun tab Activity. Ini melanjutkan pola run 22 (parsial, gate menutup ~17:27 WIB 2026-11-02) dan run 23–38 yang sepenuhnya login-gated — run 39 adalah run ke-17 berturut-turut yang sepenuhnya login-gated. Daftar umum Picks/Trending/Callout di panel samping beranda BUKAN holdings maupun Activity dompet yang diperiksa dan tidak dicatat sebagai data dompet mana pun.

Per dompet LOGIN-GATED (54 dompet — Activity TIDAK terbaca, BUKAN "tidak ada buy", BUKAN "No Data", dan TIDAK ada upaya login; saldo/holding tidak diubah di state):
- Core 14: 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6, 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02, 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5, 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7, 0x75642756e4ba4cc8fbe76df2239cada046cfc854, 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a, 0x892200223bdfb11d2506c5ab1cae9222ce253acc, 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c, 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e, 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462, 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf, 0xda91cefe240175e6fab56271110427a4195ab71f, 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc, 0x2325f175975abdbcde555c79cc8e63381d28551b
- Tier C 35: 0x9856bac497634a62a970233bc4b0f5bb52c844c1, 0x3628764a6576b8dfb31fba0aac6a333b64851423, 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e, 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c, 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74, 0xad94ee77d0e868d299fb3e92b9d67560257f656d, 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a, 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650, 0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b, 0xc621946845d0fd5d1dbc6d6beb3e22aed39d7050, 0xf795c5250f3d4006283a0d0dbb378dc0e69df923, 0x9cdd08f30188c2732cdbcac8eebf4e6e8bf0c1b2, 0xaa49e7fec503664a39598645c7a3fbfa0374380d, 0x82c6085f9ec2722fd6c8fc47577368a156a25b9b, 0x3154f6949285ee7ac1593bd2bdf974adb6731c32, 0xca4e67bb5737c095bd3a80f79ecc6607e5723f1a, 0xe9ed24db105a6b15f880025ed9ad024c06783895, 0x3a39aa05b149141a4bfc7d73611dceb0557b39c4, 0xcb08c02c0a386a10773a2c6589e7089a3dd5aca3, 0xb940e4cd40ea9e887cbc92879062676e2bc4a924, 0x4522e661d9c94ec54b37e71896351a7440ec4f07, 0x5b4beded36c1ea380abe8c6a6a0c4408f38e5024, 0xc6591fde9b44aa081062c9fc6ee48e443d24ef57, 0x362396125a55d932a09f0a5182140cbbcaf30b70, 0xf9689b9d0a675ff9ad876f1d766fb460dbde7d20, 0x2cc8192fc62e3640de91e75582cf3dbbd571b970, 0x97bd895f8123a7837368df410e7d308246c0b3e9, 0x1cce4ec5a7c5e8cfc8dedd771876c61e60b8b645, 0xc0c84518ced6a61d2a4f4a50bc0f438e0cb1031b, 0xc194efe22e874a3fe666b5de5a8fd369f12c32d5, 0xa952331ea48ea9c00c4608d8259c186021331f31, 0x92bc32975b0fbf1a19caf7cc6e3f9ea4092fd314, 0x9b519f5d52cdd03e4b10484829bc137eef1f8c1a, 0xfdec62fde1f1dc56c0ba5e50f4cae5d6c63762bf, 0x64e893a4c5c930b2cc68b054792cbc66344aeb9a
- Promosi individual 1: 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36
- Tambahan JAGENT 4: 0x341bed5b412968755f3dd6e9946636ac6f97457a, 0xd124dd5825ecaad959acdea6336926eb40aa0c9b, 0x5cf3f945620ba1a3cc9065a2086bfc728b172a0f, 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db

Hitungan sinyal run 39 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 39 (setelah 03:33 WIB 2026-11-03): TIDAK ADA yang terverifikasi, karena tidak satu pun Activity terbaca. TIDAK ADA token yang dibeli 2 wallet atau lebih dalam jendela ini, apalagi 14 — tetapi ini adalah ketiadaan bukti, bukan bukti ketiadaan buy.
- Jadi TIDAK ADA SINYAL yang diklaim dari run ini (ambang: minimal 14 entitas berbeda membeli token baru yang SAMA dengan CA yang sama). Pembelian pada jendela ini untuk ke-54 dompet TIDAK DIKETAHUI, bukan nol. Jendela run 22 untuk dompet-dompet yang saat itu login-gated, serta jendela run 23, run 24, run 25, run 26, run 27, run 28, run 29, run 30, run 31, run 32, run 33, run 34, run 35, run 36, run 37, dan run 38 untuk semua dompet, juga tetap TIDAK DIKETAHUI.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada runtuhan entitas. Laporan ini tidak memuat data pendanaan; co-buy/co-hold saja TIDAK meruntuhkan entitas.
- Tidak ada pemicu screening paper, rekomendasi beli, promosi, atau pemicu trade dari run ini.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked tetap 2026-11-03T03:33:00+07:00; ringkasan run 39 per wallet; field saldo/holding tidak diubah; `last_run` diperbarui ke run 39). Baseline holdings tetap dari run 22 dan sebelumnya, dengan catatan jendela 03:33 WIB 2026-11-03–05:32 WIB 2026-11-05 belum terbaca untuk semua dompet.
- Blokir yang tersisa: halaman dompet GMGN login-gated sejak ~17:27 WIB run 22 dan kini untuk semua 54 dompet pada run 39 (run ke-17 berturut-turut yang sepenuhnya login-gated: run 23–39). Penyelesaian butuh sign-in GMGN (di luar kewenangan baca-saja run ini — run ini TIDAK mencoba login) atau menunggu GMGN kembali menampilkan halaman publik tanpa login lalu membaca ulang ke-54 dompet itu. Diskrepansi BNB GMGN vs on-chain untuk 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc tetap TIDAK TERSELESAIKAN, tidak dicek ulang (dompet login-gated pada run ini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
- SENYAP ke chat sesuai aturan run (tidak ada laporan rutin; tidak ada wallet yang memenuhi kriteria promosi terpercaya pada run ini).

## Run 40 — Kamis 2026-11-05, 07:23–07:31 WIB (FULLY LOGIN-GATED, tanpa data publik)

- Daftar dibaca dari `tier-ab-watch.md` + state setiap run: 54 entitas terpantau (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 1 + tambahan JAGENT 4, 2026-11-03 ~08:47 WIB). Ambang sinyal yang berlaku: minimal 14 entitas berbeda membeli token baru yang sama (floor(25% x 54)+1), bukan ambang 4 dari set 14 lama — set 14 lama sudah digantikan oleh promosi 2026-11-01 dan tambahan 2026-11-03. Daftar lama 23 alamat TIDAK dipakai. Catatan: body jadwal run ini masih menyebut set 14/ambang 4; run ini mengikuti set terpantau terkini di file + state (54 entitas), yang mencakup ke-14 dompet inti itu, dan ambang 14 yang lebih konservatif.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow. Pemeriksaan browser live read-only ke-54 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>), harness-measured 07:23–07:31 WIB (jendela laporan browser 07:23–07:30 WIB; selisih 1 menit di akhir dicatat, waktu ukur harness yang dipakai). TIDAK ADA tantangan bot (CAPTCHA) yang dilaporkan.
- Hasil: 0 dari 54 halaman memuat data dompet publik. Setiap URL hanya menampilkan beranda GMGN dengan panel "You are not logged in to GMGN" — tanpa header dompet, saldo BNB, holdings, maupun tab Activity. Ini melanjutkan pola run 22 (parsial, gate menutup ~17:27 WIB 2026-11-02) dan run 23–39 yang sepenuhnya login-gated — run 40 adalah run ke-18 berturut-turut yang sepenuhnya login-gated. Daftar umum Picks/Trending/Callout di panel samping beranda BUKAN holdings maupun Activity dompet yang diperiksa dan tidak dicatat sebagai data dompet mana pun.

Per dompet LOGIN-GATED (54 dompet — Activity TIDAK terbaca, BUKAN "tidak ada buy", BUKAN "No Data", dan TIDAK ada upaya login; saldo/holding tidak diubah di state):
- Core 14: 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6, 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02, 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5, 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7, 0x75642756e4ba4cc8fbe76df2239cada046cfc854, 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a, 0x892200223bdfb11d2506c5ab1cae9222ce253acc, 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c, 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e, 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462, 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf, 0xda91cefe240175e6fab56271110427a4195ab71f, 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc, 0x2325f175975abdbcde555c79cc8e63381d28551b
- Tier C 35: 0x9856bac497634a62a970233bc4b0f5bb52c844c1, 0x3628764a6576b8dfb31fba0aac6a333b64851423, 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e, 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c, 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74, 0xad94ee77d0e868d299fb3e92b9d67560257f656d, 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a, 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650, 0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b, 0xc621946845d0fd5d1dbc6d6beb3e22aed39d7050, 0xf795c5250f3d4006283a0d0dbb378dc0e69df923, 0x9cdd08f30188c2732cdbcac8eebf4e6e8bf0c1b2, 0xaa49e7fec503664a39598645c7a3fbfa0374380d, 0x82c6085f9ec2722fd6c8fc47577368a156a25b9b, 0x3154f6949285ee7ac1593bd2bdf974adb6731c32, 0xca4e67bb5737c095bd3a80f79ecc6607e5723f1a, 0xe9ed24db105a6b15f880025ed9ad024c06783895, 0x3a39aa05b149141a4bfc7d73611dceb0557b39c4, 0xcb08c02c0a386a10773a2c6589e7089a3dd5aca3, 0xb940e4cd40ea9e887cbc92879062676e2bc4a924, 0x4522e661d9c94ec54b37e71896351a7440ec4f07, 0x5b4beded36c1ea380abe8c6a6a0c4408f38e5024, 0xc6591fde9b44aa081062c9fc6ee48e443d24ef57, 0x362396125a55d932a09f0a5182140cbbcaf30b70, 0xf9689b9d0a675ff9ad876f1d766fb460dbde7d20, 0x2cc8192fc62e3640de91e75582cf3dbbd571b970, 0x97bd895f8123a7837368df410e7d308246c0b3e9, 0x1cce4ec5a7c5e8cfc8dedd771876c61e60b8b645, 0xc0c84518ced6a61d2a4f4a50bc0f438e0cb1031b, 0xc194efe22e874a3fe666b5de5a8fd369f12c32d5, 0xa952331ea48ea9c00c4608d8259c186021331f31, 0x92bc32975b0fbf1a19caf7cc6e3f9ea4092fd314, 0x9b519f5d52cdd03e4b10484829bc137eef1f8c1a, 0xfdec62fde1f1dc56c0ba5e50f4cae5d6c63762bf, 0x64e893a4c5c930b2cc68b054792cbc66344aeb9a
- Promosi individual 1: 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36
- Tambahan JAGENT 4: 0x341bed5b412968755f3dd6e9946636ac6f97457a, 0xd124dd5825ecaad959acdea6336926eb40aa0c9b, 0x5cf3f945620ba1a3cc9065a2086bfc728b172a0f, 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db

Hitungan sinyal run 40 (entitas, bukan alamat mentah):
- Token baru yang terverifikasi dalam jendela run 40 (setelah 03:33 WIB 2026-11-03): TIDAK ADA yang terverifikasi, karena tidak satu pun Activity terbaca. TIDAK ADA token yang dibeli 2 wallet atau lebih dalam jendela ini, apalagi 14 — tetapi ini adalah ketiadaan bukti, bukan bukti ketiadaan buy.
- Jadi TIDAK ADA SINYAL yang diklaim dari run ini (ambang: minimal 14 entitas berbeda membeli token baru yang SAMA dengan CA yang sama). Pembelian pada jendela ini untuk ke-54 dompet TIDAK DIKETAHUI, bukan nol. Jendela run 22 untuk dompet-dompet yang saat itu login-gated, serta jendela run 23, run 24, run 25, run 26, run 27, run 28, run 29, run 30, run 31, run 32, run 33, run 34, run 35, run 36, run 37, run 38, dan run 39 untuk semua dompet, juga tetap TIDAK DIKETAHUI.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada runtuhan entitas. Laporan ini tidak memuat data pendanaan; co-buy/co-hold saja TIDAK meruntuhkan entitas.
- Tidak ada pemicu screening paper, rekomendasi beli, promosi, atau pemicu trade dari run ini.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked tetap 2026-11-03T03:33:00+07:00; ringkasan run 40 per wallet; field saldo/holding tidak diubah; `last_run` diperbarui ke run 40). Baseline holdings tetap dari run 22 dan sebelumnya, dengan catatan jendela 03:33 WIB 2026-11-03–07:31 WIB 2026-11-05 belum terbaca untuk semua dompet.
- Blokir yang tersisa: halaman dompet GMGN login-gated sejak ~17:27 WIB run 22 dan kini untuk semua 54 dompet pada run 40 (run ke-18 berturut-turut yang sepenuhnya login-gated: run 23–40). Penyelesaian butuh sign-in GMGN (di luar kewenangan baca-saja run ini — run ini TIDAK mencoba login) atau menunggu GMGN kembali menampilkan halaman publik tanpa login lalu membaca ulang ke-54 dompet itu. Diskrepansi BNB GMGN vs on-chain untuk 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc tetap TIDAK TERSELESAIKAN, tidak dicek ulang (dompet login-gated pada run ini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
- SENYAP ke chat sesuai aturan run (tidak ada laporan rutin; tidak ada wallet yang memenuhi kriteria promosi terpercaya pada run ini).

## Run 41 — Kamis 2026-11-05, 09:23–09:49 WIB (PUBLIC KEMBALI, 54/54 — akhir 18 run login-gated)

- Daftar dibaca dari `tier-ab-watch.md` + state setiap run: 54 entitas terpantau (Tier A privat 13 + Tier B privat 1 + Tier C ekspansi 35 + promosi individual 1 + tambahan JAGENT 4, 2026-11-03 ~08:47 WIB). Ambang sinyal yang berlaku: minimal 14 entitas berbeda membeli token baru yang SAMA dengan CA yang sama (floor(25% x 54)+1), bukan ambang 4 dari set 14 lama — set 14 lama sudah digantikan oleh promosi 2026-11-01 dan tambahan 2026-11-03. Daftar lama 23 alamat TIDAK dipakai. Catatan: body jadwal run ini masih menyebut set 14/ambang 4; run ini mengikuti set terpantau terkini di file + state (54 entitas), yang mencakup ke-14 dompet inti itu, dan ambang 14 yang lebih konservatif.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow. Pemeriksaan browser live read-only ke-54 halaman GMGN BSC (https://gmgn.ai/bsc/address/<alamat>), harness-measured 09:23–09:49 WIB (jendela laporan browser 09:23–09:48 WIB; selisih 1 menit di akhir dicatat, waktu ukur harness yang dipakai). TIDAK ADA halaman login-gated dan TIDAK ADA tantangan bot (CAPTCHA) yang dilaporkan — ini mengakhiri rentetan run 23–40 yang sepenuhnya login-gated (18 run berturut-turut).
- Batasan yang wajib dicatat:
  - Laporan ini hanya memuat 5 baris Activity terbaru per dompet. Jendela sejak last_checked terakhir yang berhasil dibaca publik (2026-11-03 03:33 WIB) adalah 2+ hari; pembelian dalam jeda itu yang sudah keluar dari 5 baris teratas TETAP TIDAK DIKETAHUI, bukan nol. Yang teramati di run ini hanyalah aktivitas terbaru (sebagian besar ~menit–4 jam sebelum baca, sebagian lagi berhari-hari lalu).
  - Contract address TIDAK tercatat untuk token mana pun pada run ini: tidak ada alamat kontrak lengkap dalam laporan; CA tidak ditebak dari simbol. Karena itu hitungan di bawah memakai simbol + konteks state, dan observasi berbasis simbol saja TIDAK dapat diklaim sebagai token dengan CA yang sama.
  - Tab Holdings memakai filter yang bertahan antar halaman: Hide Closed + Hide Didn't Buy. "No assets held" = sesuai tampilan tab itu, BUKAN klaim saldo on-chain nol; token yang hanya diterima lewat Tx In tersaring dari Holdings.
  - Waktu aktivitas bersifat relatif terhadap waktu baca ("menit/jam/hari lalu") seperti dilaporkan GMGN, bukan stempel waktu absolut yang diverifikasi on-chain.
  - Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

Per dompet (ringkas; detail per dompet ada di `run41_summary` state):
- Core 14: 0x8e96… BNB 0,036 — Buy ASI (simbol-baru, 5–9 menit lalu, lalu Sell sebagian) 1 entitas; 0x2325… BNB 0,45 — Buy 女娲/OSK/DONBUY (simbol-baru, 25 menit–1 jam lalu) masing-masing 1 entitas; dompet core lain TIDAK ADA buy baru (hanya Tx In lama, atau Buy XPIN 19–20 hari lalu yang baseline). Holdings core diperbarui; 视界之眼 di 0x8e96… naik ke $72,87 (sebelumnya ~$6,74).
- Tier C 1–8: Buy simbol-baru BABYSTAR (0x3628… + 0xa0c1… + 0x3803… = 3 entitas), GIFTY/GIFIFY, 招财猫/招财喵, ZERO (0xc7c5… + 0xad94… = 2 entitas), RELU/GRAD/ZKP (0x7488… = 1 entitas) — semuanya CA UNVERIFIED, di bawah ambang. GIFTY vs GIFIFY dan 招财猫 vs 招财喵 adalah simbol berbeda dan TIDAK digabung. Buy 0x9856… (鼻涕/ZAGS) dan 0x40a8… (NITRO) berlabel 3 hari lalu adalah re-trade/pre-window (~2026-11-02, sebelum 2026-11-03 03:33), bukan token baru dalam jendela.
- Tier C 9–35 (klaster $lAped): 24 entitas dengan Buy $lAped yang teramati di 5 baris teratas, ~4 jam sebelum baca (~05:xx WIB 2026-11-05): 0xdb2d…, 0xc621…, 0xf795…, 0x9cdd…, 0xaa49…, 0x82c6…, 0x3154…, 0xe9ed…, 0x3a39…, 0xcb08…, 0xb940…, 0x5b4b…, 0xc659…, 0x3623…, 0xf968…, 0x2cc8…, 0x97bd…, 0x1cce…, 0xc0c8…, 0xc194…, 0xa952…, 0x92bc…, 0x9b51…, 0x64e8…. Tiga dompet klaster yang sama HANYA menampilkan Sell $lAped di 5 baris teratas dan TIDAK dihitung sebagai pembeli: 0xca4e…, 0x4522…, 0xfdec…. Seluruh 27 dompet klaster ini berbagi saldo BNB 0,26 yang identik. Buy PYRO di baris teratas klaster ini adalah re-trade (PYRO sudah dikenal sejak run 16), bukan token baru, dan tanpa CA tidak dapat dipastikan apakah PYRO yang dibeli adalah kontrak yang sama atau berbeda.
- Promosi individual 0x81c3…: Buy 驴来 2,9M $197,4 dan Buy UMplan 927,3K $1,43K (11 jam lalu, ~22:xx WIB 2026-11-04), simbol-baru, 1 entitas.
- JAGENT 4: TIDAK ADA buy baru — hanya Tx In, plus satu Sell AGC 2,2M $5,763 (1 hari lalu, 0x355e…) yang adalah sell, bukan buy.

Hitungan sinyal run 41 (entitas, bukan alamat mentah):
- Observasi simbol terbesar: $lAped, 24 entitas dengan Buy simbol-baru yang teramati — ANGKA INI MELEBIHI ambang 14, TETAPI BUKAN SINYAL, karena: (1) tidak ada CA yang terverifikasi untuk $lAped pada run ini, dan aturan sinyal mensyaratkan token baru yang SAMA dengan CA yang sama; simbol bukan CA (token berbeda dapat memakai simbol sama, dan satu token dapat tampil dengan simbol yang sama di banyak kontrak). Preseden yang sama sudah dipakai di run 12: observasi simbol TART 26 entitas dinyatakan BUKAN sinyal karena CA tidak terverifikasi. (2) observasi ini hanya dari 5 baris Activity teratas; cakupan jendela 2+ hari tidak lengkap.
- Token terverifikasi-CA yang dibeli ≥14 entitas: TIDAK ADA yang terverifikasi pada run ini.
- Jadi TIDAK ADA SINYAL yang diklaim dari run ini. Observasi $lAped 24 entitas dicatat di sini dan di state sebagai observasi simbol yang perlu verifikasi CA sebelum dapat dihitung sebagai sinyal apa pun — bukan rekomendasi beli, bukan promosi, bukan bukti insider, bukan pemicu trade, dan bukan pemicu screening paper sampai CA-nya terverifikasi dan seluruh gerbang screening + konfirmasi money-flow + konfirmasi entry lolos.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada runtuhan entitas. Saldo BNB 0,26 yang identik + co-buy $lAped/PYRO yang sinkron di klaster Tier C 9–35 adalah co-buy/co-balance saja (keterkaitan LEMAH) dan TIDAK meruntuhkan entitas; tidak ada data pendanaan bersama non-exchange, transfer langsung, atau pendanaan berantai yang dilaporkan pada run ini. Pendanaan dari exchange pun tidak menghitung sebagai keterkaitan.
- Pembelian simbol-baru 1–3 entitas (ASI, 女娲/OSK/DONBUY, BABYSTAR 3 entitas, ZERO 2 entitas, dan lain-lain di atas) = bukan sinyal, hanya dicatat di atas.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked 2026-11-05T09:48:00+07:00; ringkasan run 41 + saldo BNB per wallet; field holdings diperbarui untuk dompet dengan holdings terbuka yang dilaporkan). Baseline baru = state ini, dengan catatan: jendela 2026-11-03 03:33 – 2026-11-05 ~05:xx WIB di luar 5 baris Activity teratas tetap TIDAK DIKETAHUI.
- Blokir yang tersisa: diskrepansi BNB GMGN vs on-chain untuk 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc tetap TIDAK TERSELESAIKAN — GMGN pada run ini masih menampilkan BNB 0 ($0), sementara cek batch on-chain run ini menunjukkan 0,02479 BNB (block 0x7da301f), tidak berubah sejak run 3. Diskrepansi ini TIDAK diklaim sebagai pembelian; penyebabnya belum terverifikasi.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
- SENYAP ke chat sesuai aturan run (tidak ada laporan rutin; tidak ada wallet yang memenuhi kriteria promosi terpercaya pada run ini).

## Run 42 — Kamis 2026-11-05, 11:23 WIB (gap: laporan browser belum diterima saat penulisan)

- Daftar dibaca dari `tier-ab-watch.md` + kunci state: 54 entitas terpantau (14 inti + 35 Tier C + 1 whale SENSEI + 4 tambahan yang tercatat di state). Ambang sinyal skala: floor(25% × 54) + 1 = 14 entitas berbeda membeli token baru yang SAMA dengan CA terverifikasi.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only ke-54 halaman GMGN BSC DIDISPATCH (task browser-task:ec6adb7d-6809-512c-9371-fa18b628270f) pada ~11:23 WIB, dengan instruksi eksplisit: bila login-gated, catat saja dan lanjut, JANGAN klik login.
- GAP YANG DICATAT JUJUR, mengikuti preseden run-run sebelumnya:
  - Laporan per-wallet terperinci (holdings + trade terbaru per wallet) dari browser BELUM terkirim ke konteks run ini pada saat penulisan log.
  - TIDAK ADA pembelian baru yang terverifikasi dari run ini.
  - TIDAK ADA SINYAL yang diklaim (ambang: minimal 14 entitas berbeda membeli token baru yang sama dengan CA terverifikasi) — bukan karena wallet terbukti tidak membeli, melainkan karena bukti per-wallet belum diterima. Wallet yang tidak terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
  - TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang terverifikasi).
  - Baseline / state run 41 TIDAK diubah: last_checked tetap 2026-11-05T09:48:00+07:00 dan holdings per wallet tetap dari run 41, sampai laporan browser run ini benar-benar diterima. Hanya field `last_attempt` di state yang diperbarui sebagai penanda run ini.
- Tindak lanjut: bila laporan browser run ini tiba belakangan, tambahkan sebagai adendum run ini dengan stempel waktu penerimaan, dan baru dari laporan itu hitung pembelian baru vs baseline run 41. Bila tidak tiba, run berikutnya harus mengulang pembacaan ke-54 wallet dan mencatat holdings + aktivitas terbaru per wallet secara eksplisit sebelum menghitung sinyal apa pun.
- Catatan umum: data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Adendum Run 42 — laporan browser diterima 2026-11-05 ~11:44 WIB

Pemeriksaan browser terukur 11:23–11:44 WIB (waktu ukur runtime; laporan per-wallet 11:23–11:42 WIB).
Semua 54 halaman memuat data publik TANPA login-gated, tanpa klik Log in/Sign up/Connect, tanpa
sign/transaksi. Koreksi atas bagian "GAP" run 42: bukti per-wallet AKHIRNYA diterima, sehingga
hitungan sinyal run 42 dapat ditetapkan dari laporan ini dan state diperbarui dari laporan ini
(last_checked 2026-11-05T11:42:00+07:00). Batasan laporan yang wajib dicatat:
- Tab Holdings memakai filter default GMGN: "No assets held." = sesuai tampilan tab itu, BUKAN
  klaim saldo on-chain nol; token yang hanya diterima lewat Tx In tersaring dari Holdings.
- Contract address TIDAK tercatat pada run ini untuk token mana pun: tidak ada alamat kontrak
  lengkap yang terlihat dalam teks halaman; CA tidak ditebak dari simbol. Semua hitungan di bawah
  memakai simbol saja, dan karena itu TIDAK ADA token yang lolos sebagai CA sama antar wallet.
- Waktu aktivitas bersifat relatif terhadap waktu baca ("menit/jam lalu") seperti dilaporkan
  GMGN, bukan stempel waktu absolut yang diverifikasi on-chain; label relatif dicocokkan dengan
  jumlah/nilai transaksi sebelum dinyatakan baru, mengikuti preseden run 3–6 dan run 41.
- Jendela run 42 = setelah last_checked run 41 (2026-11-05 09:48 WIB) sampai baca run 42
  (11:23–11:42 WIB). Buy berlabel 6h (~05:30–05:40 WIB) adalah PRE-WINDOW, bukan buy jendela ini.
- Varian penulisan simbol: laporan run 42 menulis $IAped (huruf I kapital) sedangkan run 41
  menulis $lAped (huruf l kecil); jumlah/nilai trade-nya identik dengan trade run 41, sehingga
  diperlakukan sebagai simbol yang sama, bukan token baru.

Per-wallet (ringkas; urutan sesuai penugasan browser):
1. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — BNB 0,037 ($26,19). Buy BARU dalam jendela:
   吕布 196,6K $1,414 (1h, ~10:30 WIB) — simbol-baru bagi wallet ini, CA UNVERIFIED, 1 entitas.
   BUKAN baru: Buy ASI 174,4K $1,423 (2h, pre-window) dan ASI 191,9K (8h) — ASI dikenal run 41;
   Buy 金羊开泰 180,5K $1,398 (4h) dan Buy 屎币人生 199,5K $1,403 (10h) pertama teramati di run
   ini tapi PRE-WINDOW, tidak dihitung sebagai buy jendela; keduanya kini dikenal.
2.–6., 8.–13. (0x13d1…, 0x5b2f…, 0x6ba7…, 0x7564…, 0x8272…, 0x93e7…, 0xaab8…, 0xb787…,
   0xbe59…, 0xda91…, 0xf6a8…): TIDAK ADA buy baru. Aktivitas terbaru hanya Tx In/Tx Out lama
   (termasuk SKYAI dan mubarak sebagai holding/transfer lama, bukan buy baru). Holdings:
   "No assets held." untuk semuanya. Khusus wallet 13 (0xf6a8…): GMGN MASIH menunjukkan BNB 0
   ($0); pengecekan on-chain ulang TIDAK dilakukan pada run ini, jadi diskrepansi vs on-chain
   0,02479 BNB (run 41) tetap belum terverifikasi dan TIDAK diklaim sebagai pembelian.
7. 0x892200223bdfb11d2506c5ab1cae9222ce253acc — BNB 0 ($0,042). Holdings tampil: XPIN, WKC,
   XRP, SLX, BANK (nilai bergeser tipis). Buy terbaru 20d–22d lalu (XPIN/XRP) — baseline,
   bukan buy baru. TIDAK ADA buy baru.
14. 0x2325f175975abdbcde555c79cc8e63381d28551b — BNB 0,45 ($321,92). TIDAK ADA buy baru dalam
   jendela: Buy 女娲 0,128 $20,7 / 0,391 $69,02, OSK 21,74 $41,91, DONBUY 0,128 $41,3 berlabel
   2h–3h adalah DUPLIKAT trade run 41 (jumlah/nilai identik, pre-window) dan token sudah dikenal
   run 41. Buy BNCB 9h dan Buy OSK 12h adalah re-trade token dikenal, pre-window.
15. 0x9856bac497634a62a970233bc4b0f5bb52c844c1 — TIDAK ADA buy baru; Buy 鼻涕/ZAGS 3d lalu
   adalah re-trade token dikenal, pre-window. Tx Out BNB 2d bukan buy.
16. 0x3628764a6576b8dfb31fba0aac6a333b64851423 — Buy BARU dalam jendela (simbol, CA UNVERIFIED):
   驴来 1,13K $0,071 (40 detik lalu), ONE 1,13K $0,071 (13m), TAMA 1,13K $0,071 (24m). Buy
   BABYSTAR 48m adalah re-trade token dikenal run 41. 驴来/ONE/TAMA kini dikenal wallet ini.
17. 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e — Buy BARU dalam jendela (simbol, CA UNVERIFIED):
   驴来 1,13K $0,071 (57 detik lalu), ONE 1,13K $0,071 (13m), TAMA 1,13K $0,071 (24m). Buy
   BABYSTAR 48m adalah re-trade token dikenal run 41. 驴来/ONE/TAMA kini dikenal wallet ini.
18. 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c — TIDAK ADA buy baru; Buy NITRO/鼻涕/FORX/ZAGS
   3d lalu pre-window. Activity terbaru Tx In BTW/SKYAI 2d, bukan buy baru. Holding terbuka
   币安马到成功 $209,64 dicatat, tanpa Buy dalam top 10.
19. 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74 — Buy BARU dalam jendela (simbol, CA UNVERIFIED):
   驴来 1,13K $0,024 (4m), BABYSTAR 1,13K $0,024 (15m), Look 1,13K $0,024 (33m), LEEROY 1,13K
   $0,024 (35m). Keempatnya kini dikenal wallet ini.
20. 0xad94ee77d0e868d299fb3e92b9d67560257f656d — Buy BARU dalam jendela (simbol, CA UNVERIFIED):
   驴来 1,13K $0,024 (4m), BABYSTAR 1,13K $0,024 (16m), Look 1,13K $0,024 (33m), LEEROY 1,13K
   $0,024 (35m). Keempatnya kini dikenal wallet ini.
21. 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a — Buy BARU dalam jendela (simbol, CA UNVERIFIED):
   驴来 832,25 $0,018 (5m), Look 832,25 $0,018 (34m), LEEROY 832,25 $0,018 (36m). Buy BABYSTAR
   16m adalah re-trade token dikenal run 41. 驴来/Look/LEEROY kini dikenal wallet ini.
22. 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650 — Buy BARU dalam jendela (simbol, CA UNVERIFIED):
   ZKIN 110K $0,064 (9m) + 11K $0,058 (1h), PGPT 110K $0,062 (42m), MAL2 1,1K $0,064 (58m),
   masing-masing 1 entitas. Buy ZKP 25m adalah re-trade token dikenal run 41. ZKIN/PGPT/MAL2
   kini dikenal wallet ini.
23.–49. (klaster $lAped/PYRO: 0xdb2d…, 0xc621…, 0xf795…, 0x9cdd…, 0xaa49…, 0x82c6…, 0x3154…,
   0xca4e…, 0xe9ed…, 0x3a39…, 0xcb08…, 0xb940…, 0x4522…, 0x5b4b…, 0xc659…, 0x3623…,
   0xf968…, 0x2cc8…, 0x97bd…, 0x1cce…, 0xc0c8…, 0xc194…, 0xa952…, 0x92bc…, 0x9b51…,
   0xfdec…, 0x64e8…): TIDAK ADA buy baru dalam jendela. Buy $lAped/PYRO berlabel 6h–7h
   (~05:30–05:40 WIB) adalah DUPLIKAT trade run 41 (jumlah/nilai identik) dan PRE-WINDOW, bukan
   buy jendela run 42; token sudah dikenal sejak run 41 (atau sejak run 16 untuk PYRO).
   Pengecualian pencatatan: untuk 0xca4e…, 0x4522…, dan 0xfdec… (run 41 hanya Sell $lAped yang
   teramati), Buy $lAped 6h di run ini adalah pertama teramati sebagai Buy bagi wallet tersebut
   — tetapi tetap PRE-WINDOW, jadi bukan buy jendela run 42; $lAped kini dikenal ketiganya.
   Saldo BNB 0,26 identik di seluruh klaster — co-balance/co-buy saja, BUKAN keterkaitan KUAT.
   Wallet 0x3623… dibaca susulan ~11:42 WIB setelah wallet ke-54, tetap tercakup.
50. 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36 — TIDAK ADA buy baru dalam jendela; Buy 驴来 12h
   dan Buy UMplan 13h adalah trade run 41 (pre-window), token sudah dikenal.
51. 0x341bed5b412968755f3dd6e9946636ac6f97457a — TIDAK ADA buy baru dalam jendela; Buy 0agent
   19,33K $0,695 berlabel 2d adalah pre-window dan pertama teramati di top 10 run ini (run 41
   hanya Tx In 2d) — kini dikenal, bukan buy jendela. Sisanya Tx In 2d.
52. 0xd124dd5825ecaad959acdea6336926eb40aa0c9b — TIDAK ADA buy baru; hanya Tx In 14h–22h dan
   Sell PTAH 19h (sell, bukan buy).
53. 0x5cf3f945620ba1a3cc9065a2086bfc728b172a0f — TIDAK ADA buy baru; hanya Tx In 3d–6d.
54. 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db — TIDAK ADA buy baru; Sell AGC 1d adalah sell,
   bukan buy; sisanya Tx In 1d.

Hitungan sinyal run 42 (entitas, bukan alamat mentah; ambang: minimal 14 entitas berbeda
membeli token baru yang SAMA dengan CA terverifikasi):
- Token dengan CA terverifikasi yang dibeli dalam jendela: TIDAK ADA — tidak ada CA yang
  terverifikasi pada run ini (simbol saja). Jadi TIDAK ADA SINYAL yang dapat diklaim atas dasar CA.
- Observasi simbol saja dalam jendela (CA UNVERIFIED, BUKAN sinyal, dan semuanya di bawah
  ambang 14): 驴来 5 entitas (0x3628…, 0xa0c1…, 0xc7c5…, 0xad94…, 0x3803…); Look 3 entitas;
  LEEROY 3 entitas; ONE 2 entitas; TAMA 2 entitas; BABYSTAR-baru 2 entitas (0xc7c5…, 0xad94…;
  0x3628…/0xa0c1…/0x3803… adalah re-trade); 吕布 1 entitas; ZKIN 1 entitas; PGPT 1 entitas;
  MAL2 1 entitas. Ukuran buy klaster 驴来 sangat kecil ($0,018–$0,071 per Buy) — dicatat apa
  adanya, bukan dinilai sebagai sinyal kuat.
- TIDAK ADA token yang dibeli oleh 14 entitas atau lebih dalam jendela ini, apalagi dengan CA
  yang sama. Jadi TIDAK ADA SINYAL.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada
  runtuhan entitas. Co-buy/co-hold saja — termasuk rotasi mikro 驴来/ONE/TAMA/BABYSTAR/Look/
  LEEROY oleh 5 wallet Tier C dan saldo BNB 0,26 yang identik di klaster $lAped — TIDAK
  meruntuhkan entitas, dan pendanaan dari exchange (bila ada) juga tidak menghitung.
- Pembelian 1–5 wallet saja = bukan sinyal, hanya dicatat di atas.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-05T11:42:00+07:00; seluruh 54 wallet mendapat run42_summary; token simbol-baru di atas
  kini dikenal untuk wallet masing-masing). Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 43 — Kamis 2026-11-05, 13:23–13:36 WIB (PUBLIC, 54/54 — tanpa login-gated)

Pemeriksaan browser terukur 13:23–13:36 WIB (waktu ukur runtime; laporan per-wallet
13:23–13:35 WIB, selisih akhir 1 menit dicatat). Semua 54 halaman memuat data publik
TANPA login-gated, tanpa klik Log in/Sign up/Connect, tanpa sign/transaksi. Jendela run 43
= setelah last_checked run 42 (2026-11-05T11:42:00+07:00) sampai baca run 43. Label GMGN
relatif: "1h" ≈ 12:2x–12:3x WIB = dalam jendela; "2h" ≈ 11:2x–11:3x WIB = pra-jendela.
Batasan yang wajib dicatat:
- Tab Holdings memakai filter default GMGN: "No assets held." = sesuai tampilan tab itu,
  BUKAN klaim saldo on-chain nol; token yang hanya diterima lewat Tx In tersaring dari
  Holdings.
- Contract address TIDAK tercatat pada run ini untuk token mana pun: tidak ada alamat
  kontrak lengkap yang terlihat dalam teks halaman; CA tidak ditebak dari simbol. Semua
  hitungan di bawah memakai simbol saja, dan karena itu TIDAK ADA token yang lolos sebagai
  CA sama antar wallet.
- Waktu aktivitas bersifat relatif terhadap waktu baca ("menit/jam lalu") seperti dilaporkan
  GMGN, bukan stempel waktu absolut yang diverifikasi on-chain; label relatif dicocokkan
  dengan jumlah/nilai transaksi sebelum dinyatakan baru, mengikuti preseden run 3–6 dan
  run 41–42.
- Tab Holdings tidak dibuka rinci per token untuk wallet micro-scalper (1.000–2.000 token,
  mayoritas debu) dan klaster $lAped (Unrealized ≈ $0); posisi terbuka disimpulkan dari
  Activity (Buy terbaru yang belum terjual) dan angka Unrealized Profits.

Per-wallet (ringkas; urutan sesuai penugasan browser):
1. 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02 — BNB 0 ($0,008), Token 0. TIDAK ADA buy
   baru. Aktivitas terbaru hanya Tx In 50d (京东生态）. Holdings: tidak ada.
2. 0x2325f175975abdbcde555c79cc8e63381d28551b — BNB 0,2 ($142,56). BUY BARU dalam jendela
   (simbol, CA UNVERIFIED, masing-masing 1 entitas): 雪球 1,75K $68,5 (2m, first buy
   13:21:46); babymsn 2,4 $20,47 (20m) dan 2,31 $20,51 (1h, first buy 11:48:56);
   英伟达SI 3,4M $40,64 (1h) dan 1,4M $20,36 (1h, first buy 12:02:42). 雪球/babymsn/
   英伟达SI kini dikenal wallet ini. Pra-jendela (duplikat run 41): 女娲/OSK/DONBUY 4–5j
   lalu. Holdings teratas: 英伟达SI $74,12; 女娲 $69,26; 雪球 $57,97; babymsn $39,87;
   DONBUY $33,64; OSK $23,43; BNCB $2,35. BNB turun dari run-42 0,45 — perubahan dicatat,
   bukan diklaim sebagai buy tertentu.
3. 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5 — BNB 0 ($0,014), Token 0. TIDAK ADA buy
   baru; Tx In 50d. Holdings: tidak ada.
4. 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7 — BNB 0,001 ($1,06), Token 0. TIDAK ADA buy
   baru; Tx In 6d (神秘小线）. Holdings: tidak ada.
5. 0x75642756e4ba4cc8fbe76df2239cada046cfc854 — BNB 0 ($0,031), Token 0. TIDAK ADA buy
   baru; Tx In 37d. Holdings: tidak ada.
6. 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a — BNB 0 ($0,011), Token 0. TIDAK ADA buy
   baru; Tx In 71d. Holdings: tidak ada.
7. 0x892200223bdfb11d2506c5ab1cae9222ce253acc — BNB 0 ($0,042), Token 0. TIDAK ADA buy
   baru; Tx In 6d; Buy lama XPIN 20d. Holdings: tidak ada.
8. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — BNB 0,034 ($24,07), Token 403. BUY BARU
   kecil dalam jendela (simbol, CA UNVERIFIED, 1 entitas): 吉祥 200K $1,409 (36m);
   Flap 151,5K $1,409 (59m) lalu Sell Flap 44m ($0,904, −$0,543). Pra-jendela: 吕布
   buy/sell 3j; 驴来 buy 14j (era run 42). 吉祥/Flap kini dikenal wallet ini. Holdings
   teratas (saldo): 吉祥 $2,18; 噜噜 $1,1; 皮坨 $0,852; 莽小六 $0,79; 厉娜 $0,789;
   1113 $0,697 — mayoritas posisi debu, Unrealized $92,57.
9. 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c — BNB 0 ($0,01), Token 0. TIDAK ADA buy
   baru; Tx In 71d. Holdings: tidak ada.
10. 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e — BNB 0 ($0), Token 0. TIDAK ADA buy baru;
    Tx In SKYAI 10d. Holdings: tidak ada.
11. 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462 — BNB 0,007 ($4,89), Token 0. TIDAK ADA
    buy baru; 1 Tx In SKYAI 17d. Holdings: tidak ada.
12. 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf — BNB 0 ($0), Token 0. TIDAK ADA buy baru;
    Tx In 50d. Holdings: tidak ada.
13. 0xda91cefe240175e6fab56271110427a4195ab71f — BNB 0,05 ($35,68), Token 1. TIDAK ADA buy
    baru; Tx In 15d (NEX, mubarak). Holdings: "No assets held" (Token 1 hanya riwayat PnL).
14. 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc — BNB 0 ($0), Token 0. TIDAK ADA buy baru;
    Tx In 15d (NEX, ASTER, Broccoli). Holdings: tidak ada. Diskrepansi GMGN-vs-on-chain BNB
    (run 41: on-chain 0,02479 BNB) TIDAK dicek ulang on-chain run ini; carried forward
    unresolved.
15. 0x9856bac497634a62a970233bc4b0f5bb52c844c1 — BNB 0 ($0), Token 16. TIDAK ADA buy baru;
    terbaru Tx Out BNB −0,065 (2d), Sell/Buy 鼻涕 3d. Holdings: Unrealized $0 (tanpa posisi
    bernilai).
16. 0x3628764a6576b8dfb31fba0aac6a333b64851423 — BNB 0,011 ($7,69), Token 1082. BUY BARU
    dalam jendela (simbol, CA UNVERIFIED): CORLA 3m; BNBS 6m; 雪球 16m; bibi 28m; 苍蝇
    40m, 52m, 1h, 1h; 英伟达S 1h ×3; 撒泼打 1h ×2 — 12× @ $0,071, 1,13K. Sell di jendela:
    雪球 8m (+$0,049), bibi 19m, 苍蝇 32m/44m/55m/1h, 英伟达S 1h ×2, 撒泼打 1h ×2,
    驴来 Sell 1h (+$0,071). Buy 驴来 2j = pra-jendela. CORLA/BNBS/雪球/bibi/苍蝇/
    英伟达S/撒泼打 kini dikenal wallet ini. Holdings: posisi terbuka CORLA + BNBS (buy
    terbaru belum terjual), sisanya debu; Unrealized −$4,39.
17. 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e — BNB 0,033 ($23,48), Token 1063. BUY BARU
    dalam jendela (simbol, CA UNVERIFIED): CORLA 4m; BNBS 6m; 雪球 17m; bibi 28m; 苍蝇
    41m, 53m, 1h, 1h; 英伟达S 1h ×2; 撒泼打 1h ×2 — 12× @ $0,071, 1,13K. Sell di jendela:
    BNBS 1m (−$0,075, rug), 雪球 12m, bibi 23m, 苍蝇 36m/48m/59m/1h, 英伟达S 1h ×3
    (satu rug), 撒泼打 1h ×2 (satu rug), 驴来 Sell 1h. Buy 驴来 2j = pra-jendela.
    CORLA/BNBS/雪球/bibi/苍蝇/英伟达S/撒泼打 kini dikenal wallet ini. Holdings: posisi
    terbuka CORLA (4m), sisanya debu; Unrealized −$0,026.
18. 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c — BNB 0,056 ($40,2), Token 24. TIDAK ADA
    buy baru; terbaru Tx In BTW/SKYAI 2d, Sell/Buy NITRO 3d. Holdings: 24 token riwayat,
    Unrealized −$9,07.
19. 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74 — BNB 0,01 ($7,24), Token 2000. BUY BARU
    dalam jendela (simbol, CA UNVERIFIED): CORLA 7m, 18m, 29m, 41m; 苍蝇 52m, 1h;
    一朵山 1h; 英伟达S 1h; 驴来 1h ×2 (BUY 驴来 BARU di jendela, terpisah dari Buy 2j
    pra-jendela); BABYSTAR 1h ×2 — 12× @ $0,024, 1,13K. Sell di jendela: CORLA 10m/21m/
    33m, 苍蝇 44m/1h, 一朵山 55m, 英伟达S 1h, 驴来 1h ×3, BABYSTAR 1h ×2. Buy 驴来 2j ×3
    = pra-jendela. CORLA/苍蝇/一朵山/英伟达S/驴来/BABYSTAR kini dikenal wallet ini.
    Holdings: posisi terbuka CORLA (7m), sisanya debu; Unrealized −$1,86.
20. 0xad94ee77d0e868d299fb3e92b9d67560257f656d — BNB 0,084 ($60,26), Token 2000. BUY BARU
    dalam jendela (simbol, CA UNVERIFIED): CORLA 7m, 18m, 29m, 41m; 苍蝇 53m, 1h;
    一朵山 1h; 英伟达S 1h; 驴来 1h ×3 (BUY 驴来 BARU di jendela); BABYSTAR 1h ×2 — 13× @
    $0,024, 1,13K. Sell di jendela: CORLA 50d/11m/22m/34m, 苍蝇 46m/1h, 一朵山 57m,
    英伟达S 1h, 驴来 1h ×4, BABYSTAR 1h ×2 — satu Sell BABYSTAR $0,936 (+$0,908; token
    naik ~37× dari harga beli). Buy 驴来 2j ×3 = pra-jendela. CORLA/苍蝇/一朵山/
    英伟达S/驴来/BABYSTAR kini dikenal wallet ini. Holdings: semua terjual, hanya debu;
    Unrealized −$0,029.
21. 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a — BNB 0,023 ($16,76), Token 2000. BUY BARU
    dalam jendela (simbol, CA UNVERIFIED): CORLA 8m, 19m, 29m, 42m; 苍蝇 53m, 1h;
    一朵山 1h; 英伟达S 1h; 驴来 1h ×3 (BUY 驴来 BARU di jendela); BABYSTAR 1h ×2 — 13× @
    $0,018, 832,25. Sell di jendela: CORLA 10m/21m/33m, 苍蝇 45m/1h, 一朵山 56m,
    英伟达S 1h, 驴来 1h ×4, BABYSTAR 1h ×2. Buy 驴来 2j ×3 = pra-jendela. CORLA/苍蝇/
    一朵山/英伟达S/驴来/BABYSTAR kini dikenal wallet ini. Holdings: posisi terbuka CORLA
    (8m), sisanya debu; Unrealized −$1,49.
22. 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650 — BNB 0,011 ($8,12), Token 680. BUY BARU
    dalam jendela (simbol, CA UNVERIFIED, 1 entitas): ZKP 11 $0,064 (11m); NFL 1,1K
    $0,064 (27m); NFI 11K $0,063 (43m); Wu Xin 11 $0,061 (1h); RBLD 110K $0,062 (1h);
    BIAS 11K $0,062 (1h); PUPPY 11K $0,058 (1h); MPRO 110K $0,064 (1h). Sell di jendela:
    NFL 13m, NFI 29m, Wu Xin 45m, RBLD/BIAS/PUPPY/MPRO/ZKIN 1h (MPRO rug −$0,043). Buy
    ZKIN/ZKP 2j = pra-jendela. ZKP/NFL/NFI/Wu Xin/RBLD/BIAS/PUPPY/MPRO kini dikenal wallet
    ini. Holdings: posisi terbuka ZKP (11m), sisanya debu; Unrealized $0,017.
23.–48. Klaster $lAped (27 wallet: 0xdb2d…, 0xc621…, 0xf795…, 0x9cdd…, 0xaa49…, 0x82c6…,
    0x3154…, 0xca4e…, 0xe9ed…, 0x3a39…, 0xcb08…, 0xb940…, 0x4522…, 0x5b4b…, 0xc659…,
    0x3623…, 0xf968…, 0x2cc8…, 0x1cce…, 0xc0c8…, 0xc194…, 0xa952…, 0x92bc…, 0x9b51…,
    0xfdec…, 0x64e8…, 0x97bd…) — semuanya BNB 0,26 (~$185,5), Token 237–251. TIDAK ADA buy
    baru; terbaru $lAped/$Aped/PYRO 8j adalah duplikat pra-jendela (~05:30 WIB, sesuai
    catatan run 42), bukan buy baru. Holdings: Unrealized ≈ $0, kecuali 0xcb08… −$26,49
    dan 0xa952… −$7,21 (pencilan di klaster, dicatat apa adanya).
49. 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36 — BNB 0,008 ($5,37), Token 55. BUY BARU
    dalam jendela (simbol, CA UNVERIFIED, 1 entitas): CORLA 3,62K $493,5 (44m); CORLA
    2,96K $493,5 (45m); CORLA 140,87 $19,74 (39m, top-up). Sell di jendela: CORLA 2,52K
    $1,2K (+$827,54, 22m) dan 1,68K $673,8 (+$421,4, 26m). CORLA kini dikenal wallet ini.
    Pra-jendela: 驴来 Buy $197,4 14j (era run 42), UMplan 13–15j. Holdings teratas: UMplan
    $2,02K; CORLA $1,88K (2.520,87; Unrealized +$1,5K); sisanya bersaldo $0.
50. 0x341bed5b412968755f3dd6e9946636ac6f97457a — BNB 1,24 ($885,1), Token 70. TIDAK ADA buy
    baru; hanya Tx In, terbaru 2d (SPACEDOG, CHICK, ACF, SAIL). Holdings: 70 token dari
    Tx In, Unrealized $0.
51. 0xd124dd5825ecaad959acdea6336926eb40aa0c9b — BNB 0,458 ($326,52), Token 91. TIDAK ADA
    buy baru; hanya Tx In, terbaru 16j (BAYC, PANBA, 币安加油， 合一）. Holdings: 91 token
    dari Tx In, Unrealized −$4,79.
52. 0x5cf3f945620ba1a3cc9065a2086bfc728b172a0f — BNB 0,97 ($692,17), Token 28. TIDAK ADA buy
    baru; hanya Tx In, terbaru 3d (GOATT, AGENTOK, WANGCAI, SAGENT). Holdings: 28 token
    dari Tx In, Unrealized −$2,84.
53. 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db — BNB 0,884 ($630,31), Token 89. TIDAK ADA
    buy baru; hanya Tx In, terbaru 18j (PANBA, 珍珠币）, Sell AGC 1d adalah sell, bukan buy.
    Holdings: 89 token dari Tx In, Unrealized −$7,89.

Hitungan sinyal run 43 (entitas, bukan alamat mentah; ambang: minimal 14 entitas berbeda
membeli token baru yang SAMA dengan CA terverifikasi):
- Token dengan CA terverifikasi yang dibeli dalam jendela: TIDAK ADA — tidak ada CA yang
  terverifikasi pada run ini (simbol saja). Jadi TIDAK ADA SINYAL yang dapat diklaim atas dasar CA.
- Observasi simbol saja dalam jendela (CA UNVERIFIED, BUKAN sinyal, dan semuanya di bawah
  ambang 14): CORLA 6 entitas (0x3628…, 0xa0c1…, 0xc7c5…, 0xad94…, 0x3803…, 0x81c3…);
  苍蝇 5 entitas; 英伟达S 5 entitas; 雪球 3 entitas (0x2325…, 0x3628…, 0xa0c1…); 驴来 3
  entitas (0xc7c5…, 0xad94…, 0x3803… — buy BARU di jendela, terpisah dari buy 2j
  pra-jendela); 一朵山 3 entitas; BABYSTAR 3 entitas; BNBS 2 entitas; bibi 2 entitas;
  撒泼打 2 entitas. Catatan: 英伟达SI (0x2325…) dan 英伟达S (klaster micro-scalper) adalah
  simbol berbeda dan TIDAK digabung; 雪球 berbeda dari 雪球重生 (beli 22j lalu). Ukuran buy
  klaster micro-scalper sangat kecil ($0,018–$0,071 per Buy) — dicatat apa adanya, bukan
  dinilai sebagai sinyal kuat; sebaliknya buy CORLA 0x81c3… besar ($493,5 ×2) tetapi tetap
  1 entitas dan simbol saja.
- TIDAK ADA token yang dibeli oleh 14 entitas atau lebih dalam jendela ini, apalagi dengan CA
  yang sama. Jadi TIDAK ADA SINYAL.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada
  runtuhan entitas. Perdagangan serentak klaster micro-scalper (0x3628/0xa0c1/0xc7c5/0xad94/
  0x3803 — ukuran tetap per wallet, pola buy-sell berulang dalam hitungan menit) dan saldo BNB
  0,26 yang identik di seluruh klaster $lAped adalah co-buy/co-hold/co-balance saja
  (keterkaitan LEMAH) — TIDAK meruntuhkan entitas; pendanaan dari exchange (bila ada) juga
  tidak menghitung. Pola serentak ini dicatat sebagai observasi, bukan sebagai bukti klaster
  terverifikasi.
- Pembelian 1–6 wallet saja (simbol) = bukan sinyal, hanya dicatat di atas.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-05T13:35:00+07:00; seluruh 54 wallet mendapat run43_summary; token simbol-baru di
  atas kini dikenal untuk wallet masing-masing). Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 44 — Kamis 2026-11-05, 15:23–15:34 WIB (PUBLIC, 54/54 — tanpa login-gated)

Jendela run: pembelian pertama teramati setelah ~13:36 WIB (akhir run 43). Tugas browser
runtime-measured 15:23–15:34 WIB. TIDAK ADA login, connect wallet, sign, beli/jual/follow,
atau trade. Semua 54 halaman profil GMGN BSC tampil publik — TIDAK ADA yang login-gated.
Tab Holdings TIDAK dibuka pada run ini (keterbatasan waktu browser untuk 54 dompet; prioritas
pada Activity + semua Buy) — field holdings di state TIDAK diubah, bukan karena tab tidak
bisa dibaca. Label waktu GMGN bersifat relatif; buy berlabel "2h" pada ~15:30 WIB (≈13:30)
tumpang tindih dengan jendela baca run 43 (13:23–13:35) dan diperiksa sebagai duplikat
berdasarkan jumlah/nilai yang identik dengan trade run 43.

Per dompet:
1. 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02 — BNB 0 ($0,009), Token 0. TIDAK ADA buy
   baru; Activity hanya Tx In lama (terbaru 50d).
2. 0x2325f175975abdbcde555c79cc8e63381d28551b — BNB 0,317 ($226,5), Token 144. BUY BARU
   dalam jendela (simbol, CA UNVERIFIED, masing-masing 1 entitas): BURN 867,18 $20,79 (1m)
   + 769,65 $20,73 (19m) + 924,04 $20,72 (24m) + 1,42K $41,48 (30m); 杀零狗 1,4T $17,41
   (21m); 考拉 6,57K $42,3 (24m) + 3,62K $21,14 (25m). BURN/杀零狗/考拉 kini dikenal
   wallet ini. Sell sweep 2–18m (FIST, oANTHROPIC, NVDAB, GOOGLB, JAGENT, 蝴蝶人生, EWYB,
   ZEC, SAFU, 币安人, 币安股票, BABAB, 牛来) bukan buy. BNB naik dari run-43 0,2 ($142,56).
3. 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5 — BNB 0 ($0,014), Token 0. TIDAK ADA buy
   baru; Activity hanya Tx In lama (terbaru 50d).
4. 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7 — BNB 0,001 ($1,06), Token 0. TIDAK ADA buy
   baru; Activity Tx In 7d dan Tx Out USDT 12–15d.
5. 0x75642756e4ba4cc8fbe76df2239cada046cfc854 — BNB 0 ($0,031), Token 0. TIDAK ADA buy
   baru; Activity hanya Tx In lama (terbaru 37d).
6. 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a — BNB 0 ($0,011), Token 0. TIDAK ADA buy
   baru; Activity hanya Tx In lama (terbaru 71d).
7. 0x892200223bdfb11d2506c5ab1cae9222ce253acc — BNB 0 ($0,042), Token 0. TIDAK ADA buy
   baru; Buy XPIN/XRP 20–22d.
8. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — BNB 0,034 ($24,12), Token 404. TIDAK ADA
   buy baru dalam jendela; Buy 吉祥 200K $1,409 (2h) adalah DUPLIKAT trade run 43
   (jumlah/nilai identik, ~13:30, pra-jendela); Flap 3h, 吕布 5h, ASI 6h adalah token
   dikenal run 41–43, pra-jendela.
9. 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c — BNB 0 ($0,01), Token 0. TIDAK ADA buy
   baru; Activity hanya Tx In lama (terbaru 71d).
10. 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e — BNB 0 ($0), Token 0. TIDAK ADA buy baru;
    Activity hanya Tx In SKYAI 10d.
11. 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462 — BNB 0,007 ($4,9), Token 0. TIDAK ADA buy
    baru; Activity hanya Tx In SKYAI 17d.
12. 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf — BNB 0 ($0), Token 0. TIDAK ADA buy baru;
    Activity hanya Tx In lama (terbaru 50d).
13. 0xda91cefe240175e6fab56271110427a4195ab71f — BNB 0,05 ($35,76), Token 2. TIDAK ADA
    buy baru; Activity hanya Tx In/Tx Out mubarak 15–40d.
14. 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc — BNB 0 ($0), Token 0. TIDAK ADA buy baru;
    Activity hanya Tx In lama (terbaru 15d).
15. 0x9856bac497634a62a970233bc4b0f5bb52c844c1 — BNB 0 ($0), Token 16. TIDAK ADA buy
    baru; Buy 鼻涕/ZAGS $0,498 3d; Tx Out BNB 2d bukan buy.
16. 0x3628764a6576b8dfb31fba0aac6a333b64851423 — BNB 0 ($0), Token 0. BUY BARU dalam
    jendela (simbol, CA UNVERIFIED): M4GA 1,13K $0,071 (6m/18m/40m), memes 1,13K $0,071
    (37m/52m/1h), K0 1,13K $0,071 (1h), CStock 1,13K $0,071 (1h). M4GA/memes/K0/CStock
    kini dikenal wallet ini. CORLA 1h/2h dan 雪球/Bbibi/苍蝇/英伟达S/撒泼打/驴来 2–4h
    adalah re-trade token dikenal run 41–43 / pra-jendela.
17. 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e — BNB 0,033 ($23,94), Token 1079. BUY BARU
    dalam jendela (simbol, CA UNVERIFIED): M4GA 1,13K $0,071 (9m/21m/44m), memes 1,13K
    $0,071 (41m/55m/1h), K0 1,13K $0,071 (1h), CStock 1,13K $0,071 (1h). M4GA/memes/
    K0/CStock kini dikenal wallet ini. CORLA 1h/2h dan BNBS/雪球/Bbibi/苍蝇/英伟达S/
    撒泼打/驴来 2–4h adalah re-trade token dikenal run 41–43 / pra-jendela.
18. 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c — BNB 0,056 ($40,27), Token 24. TIDAK ADA
    buy baru; Buy NITRO/鼻涕/FORX/ZAGS 3d.
19. 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74 — BNB 0,011 ($8,02), Token 2000. BUY BARU
    dalam jendela (simbol, CA UNVERIFIED): M4GA 1,13K $0,024 (18s/22m), Dawn 1,13K
    $0,024 (11m), memes 1,13K $0,024 (33m/54m/1h), BURN 1,13K $0,024 (43m), K0 1,13K
    $0,024 (1h). M4GA/Dawn/memes/BURN/K0 kini dikenal wallet ini. CORLA 1h/2h dan 苍蝇/
    一朵山/英伟达S/驴来/BABYSTAR 2–3h adalah re-trade token dikenal run 41–43.
20. 0xad94ee77d0e868d299fb3e92b9d67560257f656d — BNB 0,085 ($60,95), Token 2000. BUY BARU
    dalam jendela (simbol, CA UNVERIFIED): Dawn 1,13K $0,024 (9m), M4GA 1,13K $0,024
    (21m), memes 1,13K $0,024 (31m/53m/1h), BURN 1,13K $0,024 (42m), K0 1,13K $0,024
    (1h). Dawn/M4GA/memes/BURN/K0 kini dikenal wallet ini. CORLA 1h/2h dan 苍蝇/一朵山/
    英伟达S/驴来/BABYSTAR 2–4h adalah re-trade token dikenal run 41–43.
21. 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a — BNB 0,024 ($17,07), Token 2000. BUY BARU
    dalam jendela (simbol, CA UNVERIFIED): Dawn 832,25 $0,018 (5m), M4GA 832,25 $0,018
    (16m), memes 832,25 $0,018 (27m/49m/1h), BURN 832,25 $0,018 (38m), K0 832,25 $0,018
    (1h). Dawn/M4GA/memes/BURN/K0 kini dikenal wallet ini. CORLA 1h/2h dan 苍蝇/一朵山/
    英伟达S/驴来/BABYSTAR 1–3h adalah re-trade token dikenal run 41–43.
22. 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650 — BNB 0,012 ($8,26), Token 683. BUY BARU
    dalam jendela (simbol, CA UNVERIFIED, masing-masing 1 entitas): SOTR 11 $0,057 (10m),
    ZEIN 11K $0,059 (28m), 抢饭 1,1K $0,057 (44m), ZEST 110 $0,063 (1h), DRLU 11 $0,063
    (1h), METECH 11K $0,056 (1h), 离谱币 110 $0,064 (1h). SOTR/ZEIN/抢饭/ZEST/DRLU/
    METECH/离谱币 kini dikenal wallet ini. Buy ZKP/NFL/NFI/Wu Xin 2h adalah DUPLIKAT trade
    run 43 (jumlah/nilai identik, ~13:30, pra-jendela); RBLD/BIAS/PUPPY/MPRO 3h dan
    ZKIN/PGPT/MAL2 4–6h adalah re-trade token dikenal run 41–43, pra-jendela.
23.–48. Klaster $lAped (27 wallet: 0xdb2d…, 0xc621…, 0xf795…, 0x9cdd…, 0xaa49…, 0x82c6…,
    0x3154…, 0xca4e…, 0xe9ed…, 0x3a39…, 0xcb08…, 0xb940…, 0x4522…, 0x5b4b…, 0xc659…,
    0x3623…, 0xf968…, 0x2cc8…, 0x1cce…, 0xc0c8…, 0xc194…, 0xa952…, 0x92bc…, 0x9b51…,
    0xfdec…, 0x64e8…, 0x97bd…) — semuanya BNB 0,26 (~$185,7–$186,4), Token 237–251.
    TIDAK ADA buy baru; Buy $IAped/PYRO/FATCAT 10–13h adalah trade ~02:30–05:30 WIB,
    pra-jendela (duplikat pola run 43). $IAped adalah varian penulisan $lAped (sudah dicatat
    run 42), bukan token baru. FATCAT pertama teramati di run ini (12h, pra-jendela) —
    bukan buy jendela, kini dikenal untuk wallet-wallet klaster ini.
49. 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36 — BNB 0,007 ($4,71), Token 58. BUY BARU
    dalam jendela (simbol, CA UNVERIFIED, 1 entitas): burn 415M $483,6 (52m). Simbol
    'burn' huruf kecil TIDAK digabung dengan 'BURN' (simbol berbeda, ukuran berbeda);
    burn kini dikenal wallet ini. Buy UMplan 343K $959,8 (1h) adalah re-trade token
    dikenal run 41. Buy CORLA 2h ($493,5 x2 + $19,74) adalah DUPLIKAT trade run 43
    (jumlah/nilai identik, pra-jendela). Buy 驴来 16h dan UMplan 17h adalah trade run 41,
    pra-jendela.
50. 0x341bed5b412968755f3dd6e9946636ac6f97457a — BNB 1,24 ($886,77), Token 70. TIDAK ADA
    buy baru; hanya Tx In, terbaru 2d; Buy 0agent 3d bukan baru.
51. 0xd124dd5825ecaad959acdea6336926eb40aa0c9b — BNB 0,458 ($327,42), Token 91. TIDAK ADA
    buy baru; hanya Tx In, terbaru 18h; Sell PTAH 23h bukan buy.
52. 0x5cf3f945620ba1a3cc9065a2086bfc728b172a0f — BNB 0,97 ($693,55), Token 28. TIDAK ADA
    buy baru; hanya Tx In, terbaru 3d; Buy BOT/BS/BUZZ 8–11d bukan baru.
53. 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db — BNB 0,884 ($631,77), Token 89. TIDAK ADA
    buy baru; hanya Tx In, terbaru 19h; Sell AGC 1d bukan buy; Buy HOWL 3d bukan baru.

Hitungan sinyal run 44 (entitas, bukan alamat mentah; ambang: minimal 14 entitas berbeda
membeli token baru yang SAMA dengan CA terverifikasi):
- Token dengan CA terverifikasi yang dibeli dalam jendela: TIDAK ADA — tidak ada CA yang
  terverifikasi pada run ini (simbol saja). Jadi TIDAK ADA SINYAL yang dapat diklaim atas dasar CA.
- Observasi simbol saja dalam jendela (CA UNVERIFIED, BUKAN sinyal, dan semuanya di bawah
  ambang 14): M4GA 5 entitas (0x3628…, 0xa0c1…, 0x3803…, 0xad94…, 0xc7c5…); memes 5
  entitas (lima yang sama); K0 5 entitas (lima yang sama); BURN 4 entitas (0x2325…,
  0x3803…, 0xad94…, 0xc7c5…); Dawn 3 entitas (0x3803…, 0xad94…, 0xc7c5…); CStock 2
  entitas (0x3628…, 0xa0c1…); SOTR/ZEIN/抢饭/ZEST/DRLU/METECH/离谱币 masing-masing 1
  entitas (0x7488…); 杀零狗/考拉 masing-masing 1 entitas (0x2325…); burn 1 entitas
  (0x81c3…). Catatan: 'burn' (0x81c3…) dan 'BURN' adalah simbol berbeda dan TIDAK
  digabung; 'memes' baru untuk kelima wallet klaster micro-scalper (sebelumnya hanya
  dikenal oleh 0x8e96… sejak run 22, yang tidak membeli memes di jendela ini);
  'Bbibi' 2h tidak digabung dengan 'bibi' run 43 dan berlabel pra-jendela/borderline.
  Ukuran buy klaster micro-scalper sangat kecil ($0,018–$0,071 per Buy) — dicatat apa
  adanya, bukan dinilai sebagai sinyal kuat; sebaliknya buy 'burn' 0x81c3… besar ($483,6)
  tetapi tetap 1 entitas dan simbol saja.
- TIDAK ADA token yang dibeli oleh 14 entitas atau lebih dalam jendela ini, apalagi dengan CA
  yang sama. Jadi TIDAK ADA SINYAL.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak ada
  runtuhan entitas. Perdagangan serentak klaster micro-scalper (0x3628/0xa0c1/0x3803/0xad94/
  0xc7c5 — ukuran tetap per wallet, pola buy-sell berulang dalam hitungan menit, kini pada
  simbol rotasi baru M4GA/memes/K0/CStock/Dawn/BURN) dan saldo BNB 0,26 yang identik di
  seluruh klaster $lAped adalah co-buy/co-hold/co-balance saja (keterkaitan LEMAH) — TIDAK
  meruntuhkan entitas; pendanaan dari exchange (bila ada) juga tidak menghitung. Pola serentak
  ini dicatat sebagai observasi, bukan sebagai bukti klaster terverifikasi.
- Pembelian 1–5 wallet saja (simbol) = bukan sinyal, hanya dicatat di atas.
- Catatan celah: tab Holdings tidak dibuka pada run ini, jadi field holdings di state tidak
  diperbarui; aktivitas buy tetap tercatat dari tab Activity. Diskrepansi BNB GMGN-vs-on-chain
  untuk 0xf6a8… dari run sebelumnya belum dicek ulang on-chain pada run ini; dibawa maju
  belum terselesaikan.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-05T15:34:00+07:00; seluruh 54 wallet mendapat run44_summary; token simbol-baru di
  atas kini dikenal untuk wallet masing-masing). Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 45 — Kamis 2026-11-05, 17:23–17:34 WIB (PUBLIC, 54/54 — tanpa login-gated)

Jendela run: pembelian pertama teramati setelah ~15:34 WIB (akhir run 44). Tugas browser
runtime-measured 17:23–17:34 WIB (laporan browser menyebut selesai 17:33 WIB; dipakai
waktu harness 17:23–17:34 WIB). TIDAK ADA login, connect wallet, sign, beli/jual/follow,
atau trade. Semua 54 halaman profil GMGN BSC tampil publik — TIDAK ADA yang login-gated.
Tab Holdings TIDAK dibuka pada run ini (keterbatasan waktu browser untuk 54 dompet;
prioritas pada Activity + semua Buy) — field holdings di state TIDAK diubah, bukan karena
tab tidak bisa dibaca. Label waktu GMGN bersifat relatif dan dibulatkan ("1h" = 60–119
menit), sehingga buy berlabel "1h" bisa berada di sekitar batas 15:34 WIB (tumpang tindih
beberapa menit); buy "1h" tetap dihitung dalam jendela mengikuti konvensi run sebelumnya,
dengan celah ini dicatat. Buy berlabel "2h–3h" diperiksa sebagai duplikat berdasarkan
jumlah/nilai yang identik dengan trade run 44.

Per dompet:
1. 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02 — BNB 0 ($0,009), Token 0. TIDAK ADA buy
   baru; Activity hanya Tx In lama (terbaru 50d).
2. 0x2325f175975abdbcde555c79cc8e63381d28551b — BNB 0,654 ($468,16). BUY BARU dalam
   jendela (simbol, CA UNVERIFIED, masing-masing 1 entitas): bibi 1,81K $21,23 (47m) +
   5,42K $70,71 (1h). bibi kini dikenal wallet ini. Buy BURN 1,34K $20,79 + 1,12K $20,79
   (1h) adalah re-trade token dikenal (run 44), bukan token baru. BURN/杀零狗/考拉 2h
   adalah duplikat run 44 (jumlah/nilai identik, pra-jendela). Sell bibi 35 dtk lalu bukan
   buy. BNB naik dari run-44 0,317 ($226,5).
3. 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5 — BNB 0 ($0,014), Token 0. TIDAK ADA buy
   baru; Activity hanya Tx In lama (terbaru 50d).
4. 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7 — BNB 0,001 ($1,06), Token 0. TIDAK ADA buy
   baru; Activity Tx In 7d.
5. 0x75642756e4ba4cc8fbe76df2239cada046cfc854 — BNB 0 ($0,031), Token 0. TIDAK ADA buy
   baru; Activity hanya Tx In lama (terbaru 38d).
6. 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a — BNB 0 ($0,011), Token 0. TIDAK ADA buy
   baru; Activity hanya Tx In lama (terbaru 71d).
7. 0x892200223bdfb11d2506c5ab1cae9222ce253acc — BNB 0 ($0,042), Token 0. TIDAK ADA buy
   baru; Activity hanya Tx In lama (terbaru 6d).
8. 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 — BNB 0,034 ($24,16), Token 404. TIDAK ADA
   buy baru dalam jendela; Buy 吉祥 200K $1,409 (4h) pra-jendela, duplikat trade run 43/44.
9. 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c — BNB 0 ($0,01), Token 0. TIDAK ADA buy
   baru; Activity hanya Tx In lama (terbaru 71d).
10. 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e — BNB 0 ($0), Token 0. TIDAK ADA buy baru;
    Activity hanya Tx In SKYAI 10d.
11. 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462 — BNB 0,007 ($4,91), Token 0. TIDAK ADA
    buy baru; Activity hanya Tx In SKYAI 17d.
12. 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf — BNB 0 ($0), Token 0. TIDAK ADA buy baru;
    Activity hanya Tx In lama (terbaru 50d).
13. 0xda91cefe240175e6fab56271110427a4195ab71f — BNB 0,05 ($35,82), Token 2. TIDAK ADA
    buy baru; Activity hanya Tx In lama (terbaru 15d).
14. 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc — BNB 0 ($0), Token 0. TIDAK ADA buy baru;
    Activity hanya Tx In lama (terbaru 15d).
15. 0x9856bac497634a62a970233bc4b0f5bb52c844c1 — BNB 0 ($0), Token 16. TIDAK ADA buy
    baru; Tx Out BNB −0,065 (3d) bukan buy.
16. 0x3628764a6576b8dfb31fba0aac6a333b64851423 — BNB 0,01 ($7,51), Token 0. BUY BARU
    dalam jendela (simbol, CA UNVERIFIED): 雪球 1,13K $0,071 (5m); CORLA 1,13K $0,071
    x5 (9m/21m/32m/44m/55m); 突突车 1,13K $0,071 (1h); M4GA 1,13K $0,071 x2 (1h); 4
    1,13K $0,071 (1h). 雪球/突突车/4 kini dikenal wallet ini; CORLA/M4GA re-trade simbol
    dikenal run 44. Duplikat run 44 (2h–3h): M4GA, CORLA, memes (2x), K0, CORLA, CStock.
17. 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e — BNB 0,034 ($24,28), Token 1079. BUY
    BARU dalam jendela (simbol, CA UNVERIFIED): 雪球 1,13K $0,071 (6m); CORLA 1,13K
    $0,071 x5 (9m/21m/32m/44m/56m); 突突车 1,13K $0,071 x2 (1h); M4GA 1,13K $0,071 x2
    (1h); 4 1,13K $0,071 (1h). 雪球/突突车/4 kini dikenal wallet ini; CORLA/M4GA
    re-trade simbol dikenal run 44. Duplikat run 44 (2h–3h): M4GA, CORLA, memes, K0,
    CORLA, CStock.
18. 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c — BNB 0,056 ($40,37), Token 24. TIDAK ADA
    buy baru; Activity hanya Tx In lama (terbaru 2d).
19. 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74 — BNB 0,012 ($8,30), Token 2000. BUY BARU
    dalam jendela (simbol, CA UNVERIFIED): 雪球 1,13K $0,025 (4m) + $0,024 (5m/25m);
    CORLA 1,13K $0,025 (6m/7m/8m) + $0,024 (18m/36m/46m); 米 1,13K $0,024 (58m); 突突车
    1,13K $0,024 x2 (1h); M4GA 1,13K $0,024 x4 (1h). 雪球/米/突突车 kini dikenal wallet
    ini; CORLA/M4GA re-trade simbol dikenal run 44. Duplikat run 44 (2h–3h): Dawn, M4GA,
    memes (2x), BURN, memes, K0, CORLA (3x).
20. 0xad94ee77d0e868d299fb3e92b9d67560257f656d — BNB 0,086 ($61,39), Token 2000. BUY BARU
    dalam jendela (simbol, CA UNVERIFIED): 雪球 1,13K $0,025 (4m) + $0,024 (5m/25m);
    CORLA 1,13K $0,025 (6m/7m/8m) + $0,024 (18m/36m/46m); 米 1,13K $0,024 (58m); 突突车
    1,13K $0,024 x2 (1h); M4GA 1,13K $0,024 x4 (1h). 雪球/米/突突车 kini dikenal wallet
    ini; CORLA/M4GA re-trade simbol dikenal run 44. Duplikat run 44 (2h–3h): Dawn, M4GA,
    memes (2x), BURN, memes, K0, CORLA (3x, satu 1,01K).
21. 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a — BNB 0,024 ($17,14), Token 2000. BUY BARU
    dalam jendela (simbol, CA UNVERIFIED): 雪球 832,25 $0,018 x3 (5m/6m/25m); CORLA
    832,25 $0,018 x6 (7m/8m/8m/18m/36m/46m); 米 832,25 $0,018 (58m); 突突车 832,25
    $0,018 x2 (1h); M4GA 832,25 $0,018 x4 (1h). 雪球/米/突突车 kini dikenal wallet ini;
    CORLA/M4GA re-trade simbol dikenal run 44. Duplikat run 44 (2h–3h): Dawn, M4GA,
    memes (2x), BURN, memes, K0, CORLA (4x).
22. 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650 — BNB 0,012 ($8,41), Token 683. BUY BARU
    dalam jendela (simbol, CA UNVERIFIED, masing-masing 1 entitas): DFI 11 $0,058 (3m);
    ZSUM 1,1K $0,058 (19m); BSCL 110 $0,064 (37m); GRCO 1,1K $0,061 (54m); DBANANA 11
    $0,061 (1h); BSC 11 $0,06 (1h); BSLA 110K $0,058 (1h); NIKE 110K $0,063 (1h).
    DFI/ZSUM/BSCL/GRCO/DBANANA/BSC/BSLA/NIKE kini dikenal wallet ini. SOTR/ZEIN/抢饭/
    ZEST 2h–3h pra-jendela, bukan duplikat run 44.
23.–48. + 50. Klaster GrokBot/CORLA (27 wallet: 0xdb2d…, 0xc621…, 0xf795…, 0x9cdd…,
    0xaa49…, 0x82c6…, 0x3154…, 0xca4e…, 0xe9ed…, 0x3a39…, 0xcb08…, 0xb940…, 0x4522…,
    0x5b4b…, 0xc659…, 0x3623…, 0xf968…, 0x2cc8…, 0x1cce…, 0xc0c8…, 0xc194…, 0xa952…,
    0x92bc…, 0x9b51…, 0xfdec…, 0x64e8…, 0x97bd…) — semuanya BUY BARU dalam jendela
    (simbol, CA UNVERIFIED, 1 entitas per wallet): GrokBot + CORLA, simbol-baru untuk
    ke-27 wallet ini. Per wallet (GrokBot xN + CORLA xM; BNB): 0xdb2d… GrokBot x3 +
    CORLA x1 (0,208); 0xc621… GrokBot x9 + CORLA x1 (0,5); 0xf795… GrokBot x6 + CORLA
    x3 (0,161); 0x9cdd… GrokBot x6 + CORLA x1 (0,249); 0xaa49… GrokBot x6 + CORLA x2
    (0,252); 0x82c6… GrokBot x7 + CORLA x6 (0,248); 0x3154… GrokBot x3 + CORLA x1
    (0,196); 0xca4e… GrokBot x7 + CORLA x6 (0,207); 0xe9ed… GrokBot x6 + CORLA x1
    (0,255); 0x3a39… GrokBot x3 + CORLA x1 (0,28); 0xcb08… GrokBot x3 + CORLA x2
    (0,207); 0xb940… GrokBot x5 + CORLA x1 (0,225); 0x4522… GrokBot x3 + CORLA x5
    (0,275); 0x5b4b… GrokBot x4 + CORLA x4 (0,264); 0xc659… GrokBot x6 + CORLA x2
    (0,292); 0x3623… GrokBot x5 + CORLA x2 (0,327); 0xf968… GrokBot x9 + CORLA x1
    (0,251); 0x2cc8… GrokBot x4 + CORLA x2 (0,31); 0x1cce… GrokBot x2 + CORLA x1
    (0,308); 0xc0c8… GrokBot x5 + CORLA x5 (0,15); 0xc194… GrokBot x5 + CORLA x3
    (0,485); 0xa952… GrokBot x3 + CORLA x2 (0,152); 0x92bc… GrokBot x3 + CORLA x3
    (0,244); 0x9b51… GrokBot x4 + CORLA x3 (0,222); 0xfdec… GrokBot x8 + CORLA x2
    (0,252); 0x64e8… GrokBot x2 + CORLA x1 (0,26); 0x97bd… GrokBot x3 + CORLA x2 (0,26).
    Ukuran buy besar berulang ~$167 per Buy (beberapa buy kecil $0,017–$33,88 di
    antaranya). Setiap wallet juga mencatat Sell GrokBot ~39–46m lalu (bukan buy). Tidak
    ada Buy 2h–3h pada wallet-wallet ini. GrokBot/CORLA kini dikenal untuk ke-27 wallet.
    Saldo BNB klaster ini TIDAK LAGI identik 0,26 seperti run 44 — kini 0,15–0,5.
49. 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36 — BNB 0,006 ($4,63), Token 58. TIDAK ADA
    buy baru dalam jendela. Sell burn 207,5M $547 (1h) bukan buy. Buy burn 415M $483,60
    (2h) adalah DUPLIKAT buy run 44 (jumlah/nilai identik, pra-jendela) — KOREKSI atas
    catatan browser yang menyebutnya bukan duplikat karena tidak ada di konteks tugasnya;
    burn sudah dikenal wallet ini sejak run 44.
50. 0x341bed5b412968755f3dd6e9946636ac6f97457a — BNB 1,24 ($888,19), Token 70. TIDAK ADA
    buy baru; hanya Tx In, terbaru 2d (SPACEDOG).
51. 0xd124dd5825ecaad959acdea6336926eb40aa0c9b — BNB 0,458 ($327,72), Token 91. TIDAK ADA
    buy baru; hanya Tx In, terbaru 20h (BAYC +950).
52. 0x5cf3f945620ba1a3cc9065a2086bfc728b172a0f — BNB 0,97 ($694,71), Token 28. TIDAK ADA
    buy baru; hanya Tx In, terbaru 3d (GOATT).
53. 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db — BNB 0,884 ($632,66), Token 89. TIDAK ADA
    buy baru; hanya Tx In, terbaru 21h (PANBA).

Hitungan sinyal run 45 (entitas, bukan alamat mentah; ambang: minimal 14 entitas berbeda
membeli token baru yang SAMA dengan CA terverifikasi):
- Token dengan CA terverifikasi yang dibeli dalam jendela: TIDAK ADA — tidak ada CA yang
  terverifikasi pada run ini (simbol saja, tab Activity GMGN tidak menampilkan CA). Jadi
  TIDAK ADA SINYAL yang dapat diklaim atas dasar CA.
- Observasi simbol saja dalam jendela (CA UNVERIFIED, BUKAN sinyal): GrokBot 27 entitas
  (0xdb2d… s.d. 0x64e8… + 0x97bd…, semuanya simbol-baru); CORLA 32 entitas (27 simbol-baru
  yang sama + 5 re-trade klaster micro-scalper 0x3628…/0xa0c1…/0x3803…/0xad94…/0xc7c5…);
  雪球 5 entitas; M4GA 5 entitas; 突突车 5 entitas; 米 3 entitas (0x3803…/0xad94…/
  0xc7c5…); 4 2 entitas (0x3628…/0xa0c1…); bibi 1 entitas (0x2325…); DFI/ZSUM/BSCL/GRCO/
  DBANANA/BSC/BSLA/NIKE masing-masing 1 entitas (0x7488…); BURN 1 entitas (0x2325…,
  re-trade, sudah dikenal run 44). Catatan penting: hitungan simbol GrokBot (27) dan CORLA
  (32) SECARA ANGKA melewati ambang 14 entitas, TETAPI simbol bukan CA — token berbeda
  bisa berbagi simbol yang sama — sehingga TIDAK BOLEH diklaim sebagai sinyal. Sinyal
  membutuhkan CA yang sama dan terverifikasi, yang tidak ada pada run ini.
- TIDAK ADA SINYAL.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak
  ada runtuhan entitas. Pola serentak 27 wallet membeli GrokBot + CORLA berukuran ~$167
  dalam jam yang sama, masing-masing juga menjual GrokBot ~39–46m lalu, adalah co-buy/
  co-sell saja (keterkaitan LEMAH) — TIDAK meruntuhkan entitas; pendanaan dari exchange
  (bila ada) juga tidak menghitung. Pola yang sama berlaku untuk klaster micro-scalper
  (0x3628/0xa0c1/0x3803/0xad94/0xc7c5 — ukuran tetap per wallet $0,071/$0,024/$0,018,
  kini rotasi ke simbol baru 雪球/突突车/4/米) dan saldo BNB klaster $lAped yang kini
  tidak lagi identik (0,15–0,5, dari sebelumnya 0,26 seragam). Pola serentak ini dicatat
  sebagai observasi, bukan sebagai bukti klaster terverifikasi.
- Pembelian 1–5 wallet saja (simbol) = bukan sinyal, hanya dicatat di atas.
- Catatan celah: tab Holdings tidak dibuka pada run ini, jadi field holdings di state
  tidak diperbarui; aktivitas buy tetap tercatat dari tab Activity. Diskrepansi BNB
  GMGN-vs-on-chain untuk 0xf6a8… dari run sebelumnya belum dicek ulang on-chain pada run
  ini; dibawa maju belum terselesaikan. Buy berlabel "1h" bisa menumpang batas 15:34 WIB
  beberapa menit (pembulatan label GMGN); dicatat sebagai celah jendela, bukan sebagai
  sinyal.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-05T17:34:00+07:00; seluruh 54 wallet mendapat run45_summary; token simbol-baru di
  atas kini dikenal untuk wallet masing-masing). Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 46 — Kamis 2026-11-05, 19:23–19:36 WIB (PUBLIC, 54/54 — tanpa login-gated)

Jendela: sejak run 45 berakhir 17:34 WIB s.d. 19:36 WIB. Pembacaan browser 19:23–19:34 WIB
(laporan browser) vs harness-measured 19:23–19:36 WIB — dipakai waktu harness, selisih
2 menit dicatat. Aturan waktu: Buy berlabel ≤1 jam dihitung baru dalam jendela; label
"2 jam" ke atas di luar jendela. Semua simbol dilaporkan apa adanya (CA UNVERIFIED —
halaman GMGN tidak menampilkan tautan kontrak terverifikasi).

Ringkasan: 54/54 dompet termuat PUBLIK, 0 LOGIN-GATED. 35 dompet dengan Buy baru; 19 tanpa
Buy baru. Total Buy baru dalam jendela: 304 baris (192 GrokBot + 100 mikro-bot + 1 BURN
re-trade + 8 dompet 21 + 3 dompet 48). Per dompet (indeks — alamat singkat — saldo BNB —
Buy baru; "—" = tidak ada):
0. 0x13d1…6d02 — 0 BNB ($0,008) — — (Tx In 50d)
1. 0x2325…551b — 1,06 BNB ($757,72) — 1 Buy: BURN 1,04K $20,76 (15m, re-trade token
   dikenal run 44, bukan token baru). Duplikat: bibi 1,81K $21,23 (2h) + 5,42K $70,71
   (3h) — sama persis dengan Buy run 45, pre-window.
2. 0x5b2f…48a5 — 0 BNB ($0,014) — — (Tx In 50d)
3. 0x6ba7…49e7 — 0,001 BNB ($1,06) — — (Tx In 7d)
4. 0x7564…c854 — 0 BNB ($0,031) — — (Tx In 38d)
5. 0x8272…8db6a — 0 BNB ($0,011) — — (Tx In 71d)
6. 0x8922…3acc — 0 BNB ($0,042) — — (Tx In 6d; Buy terakhir XPIN 20d)
7. 0x8e96…b8d6 — 0,033 BNB ($23,74) — — (Buy terakhir 吉祥 200K $1,409, 6h)
8. 0x93e7…2e1c — 0 BNB ($0,01) — — (Tx In 71d)
9. 0xaab8…026e — 0 BNB ($0) — — (Tx In SKYAI 10d)
10. 0xb787…1462 — 0,007 BNB ($4,88) — — (Tx In SKYAI 17d)
11. 0xbe59…3cdf — 0 BNB ($0) — — (Tx In 50d)
12. 0xda91…ab71f — 0,05 BNB ($35,64) — — (Tx In 15d)
13. 0xf6a8…e2cc — 0 BNB ($0) — — (Tx In NEX 15d)
14. 0x9856…44c1 — 0 BNB ($0) — — (Tx Out BNB −0,065, 3d; Buy terakhir 鼻涕 4d)
15. 0x3628…1423 — 0,011 BNB ($8,12) — 38 Buy mikro 1,13K $0,071: CORLA ×20, 女娲 ×5,
    雪球 12,86 ×5, BABY 0,04 $0,00000002 ×1, 蝴蝶金 ×1, 7 ×3, 皇冠 ×1, 屎壳郎 ×1,
    GOUT ×1. Urutan trade menit demi menit identik dengan dompet 16.
16. 0xa0c1…9b9e — 0,034 BNB ($24,05) — 14 Buy mikro 1,13K $0,071: CORLA ×5, 女娲 ×1,
    蝴蝶金 ×1, 7 ×3, 皇冠 ×1, 屎壳郎 ×1, GOUT ×1, 雪球 12,86 ×1. Urutan identik dengan
    dompet 15 menit demi menit.
17. 0x40a8…784c — 0,056 BNB ($40,14) — — (Tx In 2d; Buy terakhir NITRO 4d)
18. 0xc7c5…eb74 — 0,01 BNB ($7,42) — 16 Buy mikro 1,13K ~$0,024–0,025: 女娲 ×2,
    CORLA ×4, 蝴蝶金 ×1, 7 ×3, 皇冠 ×2, GOUT ×4. Rincian per simbol identik dengan
    dompet 19 dan 20.
19. 0xad94…656d — 0,086 BNB ($61,54) — 16 Buy mikro 1,13K ~$0,024–0,025, rincian sama
    seperti dompet 18 (女娲 ×2, CORLA ×4, 蝴蝶金 ×1, 7 ×3, 皇冠 ×2, GOUT ×4).
20. 0x3803…036a — 0,024 BNB ($17,34) — 16 Buy mikro 832,25 $0,018, rincian sama seperti
    dompet 18/19 (女娲 ×2, CORLA ×4, 蝴蝶金 ×1, 7 ×3, 皇冠 ×2, GOUT ×4).
21. 0x7488…6650 — 0,01 BNB ($7,06) — 8 Buy (simbol-baru kecuali BSCL): 有味来了币 11
    $0,057 (2m), SELO 110 $0,057 (20m), FAAP 110 $0,057 (37m), Douyin 11 $0,058 (53m),
    BSCL 1,1K $0,063 (1h, re-trade run 45), ALDE 11 $0,062 (1h), SHDW 11 $0,058 (1h),
    TLIM 1,1K $0,058 (1h). Duplikat: DFI 1,1K $0,057 (2h, run 45).
22. 0xdb2d…a52b — 0,194 BNB ($138,53) — 10 Buy GrokBot (6m–1h; 6M $187,6; 5,8M $166,9;
    4,3M $127; 2,72K $0,066; 4,3M $137,8; 2,91K $0,072; 5,6M $170,3; 2,71K $0,089;
    12,8M $167,4; 9,85K $0,088).
23. 0xc621…7050 — 0,306 BNB ($218,31) — 8 Buy GrokBot (8,4M $167,2 10m; 16,3M $285,9;
    16,6M $186,6; 9,6M $236,7; 191,3K $4,901; 2,3M $50,33; 6,9M $178,6; 11,5M $167,7).
24. 0xf795…f923 — 0,473 BNB ($336,9) — 13 Buy GrokBot (35,38K $1,085 7m; 42,71K $1,363
    7m; 41,27K $1,15 8m; 8,4M $156,2 9m; 6,6M $132,5 10m; 13,3M $167,1 11m; 157,5K
    $2,462; 14,6M $265,3; 9,8M $261,8; 8,5M $228,8; 589,6K $19,64; 7,8M $201,4;
    17,1M $167,5 — semua 1h).
25. 0x9cdd…c1b2 — 0,157 BNB ($111,81) — 2 Buy GrokBot (7,2M $191,5 8m; 9,5M $158,9 10m).
26. 0xaa49…380d — 0,411 BNB ($293,15) — 4 Buy GrokBot (9,1M $185,9 10m; 13,7M $159
    12m; 4,8M $127,9 1h; 5,5M $159,4 1h).
27. 0x82c6…5b9b — 0,232 BNB ($165,13) — 11 Buy GrokBot (164,7K $5,234 7m; 5,9M $166,6
    9m; 3,6M $56,05 11m; 8,1M $136,1 11m; 9,7M $112,4 12m; 23,3M $330,4; 9,3M $261,3;
    107,2K $2,813; 803K $20; 9,7M $215,4; 9,8M $159,4 — semua 1h).
28. 0x3154…1c32 — 0,246 BNB ($175,59) — 7 Buy GrokBot (4,5M $139,7 7m; 9,3M $180,5 10m;
    7,9M $111,2 12m; 6,4M $158,9; 544,8K $13,81; 6,2M $141,7; 9,2M $167,5 — semua 1h).
29. 0xca4e…3f1a — 0,224 BNB ($159,97) — 1 Buy GrokBot (5,4M $158,9 9m).
30. 0xe9ed…3895 — 0,195 BNB ($139,16) — 1 Buy GrokBot (4,1M $166,9 5m).
31. 0x3a39…39c4 — 0,152 BNB ($108,13) — 20 Buy GrokBot (63,45K $1,558 10m; 8,5M $168,1
    11m; 14,4M $167 13m; sisanya 1h: 389,6K $8,484; 492,6K $10,65; 751,9K $8,989;
    4,9M $116,4; 3,2M $123; 539,1K $14,42; 42,5K $1,17; 5,5M $158,9; 5,2M $159,7;
    7,6M $235,3; 459,9K $12,97; 39,95K $1,176; 48,55K $1,477; 45,08K $1,247;
    8,8M $169,2; 7,5M $148,5; 13,5M $167,7).
32. 0xcb08…aca3 — 0,16 BNB ($114,37) — 16 Buy GrokBot (547,1K $23,37 5m; 9,7M $280,4
    10m; 8,6M $158,1 11m; 12M $167,1 12m; sisanya 1h: 1,3M $19,5; 3M $32,12; 435,2K
    $13,75; 4,7M $143; 1,2M $32,38; 547,4K $17,48; 6M $181,9; 60,29K $1,664;
    6,8M $177,6; 1,2M $34,25; 97,51K $1,569; 11,2M $167,5).
33. 0xb940…a924 — 0,3 BNB ($213,46) — 5 Buy GrokBot (2M $66,13 7m; 3,7M $111,8 9m;
    528K $15,63 1h; 5,1M $160,4 1h; 7,1M $167,5 1h).
34. 0x4522…4f07 — 0,331 BNB ($235,54) — 5 Buy GrokBot (7,8M $143 12m; 343,7K $9,433 1h;
    6,5M $170,8 1h; 335,6K $9,257 1h; 6,7M $167,6 1h).
35. 0x5b4b…5024 — 0,265 BNB ($188,47) — 12 Buy GrokBot (5M $167 10m; 9,86K $0,088 14m;
    sisanya 1h: 545,2K $15,3; 3,4M $94,65; 6,1M $168,9; 314,2K $9,049; 6,2M $162,7;
    4M $98,26; 629,6K $13,67; 4,2M $84,58; 8,6M $158,5; 7,4M $95,71).
36. 0xc659…ef57 — 0,209 BNB ($148,79) — 2 Buy GrokBot (4,5M $158,8 8m; 3,9M $112,2 1h).
37. 0x3623…0b70 — 0,265 BNB ($188,52) — 12 Buy GrokBot (12,7M $166,9 14m; 9,85K $0,087
    14m; sisanya 1h: 2M $21,22; 6,2M $217,8; 8,6M $247,1; 818,2K $21,99; 8,2M $225,6;
    7,7M $233,4; 10,8M $269,2; 561,4K $15,21; 8,8M $156; 10,8M $167,7).
38. 0xf968…7d20 — 0,284 BNB ($201,99) — 1 Buy GrokBot (4,4M $144,4 8m).
39. 0x2cc8…b970 — 0,275 BNB ($195,56) — 2 Buy GrokBot (7,5M $167 13m; 6,4M $167,7 1h).
40. 0x1cce…b645 — 0,322 BNB ($228,86) — 9 Buy GrokBot (336K $9,226 11m; 7,4M $167,2
    12m; sisanya 1h: 666,9K $17,61; 10,5M $264,3; 6,1M $163,3; 2,1M $46,36;
    4,5M $132,7; 9,8M $184,9; 8,1M $111,6).
41. 0xc0c8…031b — 0,171 BNB ($121,53) — 7 Buy GrokBot (49,55K $1,87 8m; 6,7M $201,7
    11m; 17,1M $167 15m; 5,5M $152,4 1h; 4,9M $151,3 1h; 5,9M $167,8 1h;
    10,9M $167,5 1h).
42. 0xc194…32d5 — 0,191 BNB ($135,59) — 13 Buy GrokBot (356,3K $11,72 8m; 5,7M $167,1
    11m; sisanya 1h: 2,4M $63,05; 5,4M $153,1; 3,6M $105; 2,3M $55,96; 5,4M $135,8;
    964,2K $32,42; 165,5K $5,012; 5,6M $159,4; 3,2M $55,53; 8,3M $134,8;
    8,5M $112,8).
43. 0xa952…1f31 — 0,263 BNB ($186,88) — 3 Buy GrokBot (10,5M $167 14m; 7M $181,7 1h;
    7,5M $167,4 1h).
44. 0x92bc…d314 — 0,329 BNB ($234,28) — 4 Buy GrokBot (6,9M $202,1 12m; 7,3M $112,4
    14m; 7M $180,4 1h; 7,4M $167,5 1h).
45. 0x9b51…8c1a — 0,444 BNB ($315,74) — 8 Buy GrokBot (6,8M $238,9 9m; 5,9M $142,2 12m;
    10,4M $157,6 14m; 12,6M $167,1 15m; 481,6K $16,21 1h; 67,29K $1,687 1h;
    9,2M $181,8 1h; 14,4M $167,5 1h).
46. 0xfdec…62bf — 0,158 BNB ($112,25) — 4 Buy GrokBot (6,3M $229,5 8m; 6,9M $199,8 12m;
    12,9M $167,1 15m; 6,1M $167,5 1h).
47. 0x64e8…eb9a — 0,261 BNB ($185,79) — 11 Buy GrokBot (488,9K $16,5 9m; 966,3K $30,73
    13m; 94,88K $1,566 15m; 10,9M $167,1 15m; sisanya 1h: 16,8M $182,3; 3,9M $117,3;
    7,8M $203,2; 1,6M $47,4; 4,6M $120,6; 8M $206,3; 7,5M $112,7).
48. 0x81c3…de36 — 0,006 BNB ($4,1) — 3 Buy (simbol-baru): 蝶金库 914,3K $191,4 (30m) +
    862,6K $191,4 (30m); 皇冠 25,42 $483,6 (1h). Duplikat: burn 415M $483,6 (4h,
    run 44). Ukuran tetap $483,60 / $191,40 berulang.
49. 0x97bd…b3e9 — 0,194 BNB ($137,86) — 1 Buy GrokBot (3,8M $166,8 8m).
50. 0x341b…457a — 1,24 BNB ($883,09) — — (Tx In SPACEDOG 2d)
51. 0xd124…a0c9b — 0,458 BNB ($325,98) — — (Tx In BAYC 22h)
52. 0x5cf3…2a0f — 0,97 BNB ($690,92) — — (Tx In GOATT 3d)
53. 0x355e…f3db — 0,884 BNB ($629,17) — — (Tx In PANBA 1d)

Hitungan sinyal run 46 (entitas, bukan alamat mentah; ambang: minimal 14 entitas berbeda
membeli token baru yang SAMA dengan CA terverifikasi):
- Token dengan CA terverifikasi yang dibeli dalam jendela: TIDAK ADA — tidak ada CA yang
  terverifikasi pada run ini (simbol saja, tab Activity GMGN tidak menampilkan CA). Jadi
  TIDAK ADA SINYAL yang dapat diklaim atas dasar CA.
- Observasi simbol saja dalam jendela (CA UNVERIFIED, BUKAN sinyal): GrokBot 27 entitas
  (0xdb2d… s.d. 0x64e8… + 0x97bd…, semuanya re-trade simbol dikenal run 45, bukan token
  baru bagi wallet-wallet itu); CORLA 5 entitas (klaster mikro-bot 0x3628…/0xa0c1…/
  0x3803…/0xad94…/0xc7c5…, re-trade); 女娲 5 entitas, 蝴蝶金 5, 7 5, GOUT 5 (klaster
  mikro-bot, simbol-baru untuk wallet-wallet itu); 皇冠 6 entitas (klaster mikro-bot +
  0x81c3…); 雪球 2 entitas, 屎壳郎 2 entitas (klaster mikro-bot); 有味来了币/SELO/FAAP/
  Douyin/ALDE/SHDW/TLIM masing-masing 1 entitas (0x7488…); 蝶金库 1 entitas (0x81c3…);
  BURN 1 entitas (0x2325…, re-trade run 44). Catatan penting: hitungan simbol GrokBot (27)
  SECARA ANGKA melewati ambang 14 entitas, TETAPI simbol bukan CA — token berbeda bisa
  berbagi simbol yang sama — sehingga TIDAK BOLEH diklaim sebagai sinyal. Sinyal
  membutuhkan CA yang sama dan terverifikasi, yang tidak ada pada run ini.
- TIDAK ADA SINYAL.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak
  ada runtuhan entitas. Namun pola klaster mikro-bot MENGUAT pada run ini: dompet 15 vs 16
  menampilkan urutan perdagangan yang sama menit demi menit, dan dompet 18/19/20
  masing-masing mencatat 16 Buy dengan rincian per simbol yang identik — lebih dari
  sekadar co-buy, mengindikasikan skrip/operator yang sama. Ini BELUM memenuhi definisi
  keterkaitan KUAT dalam aturan (pendanaan bersama non-exchange, transfer langsung,
  pendanaan berantai) karena tidak ada bukti pendanaan/transfer yang teramati di halaman
  GMGN (sumber Tx In yang terlihat — mis. 0xfa…3fcd, 0x1f…db01 di dompet 15; 0x21…59c3
  di dompet 1; 0x00…0000 di dompet 48 — bukan alamat yang dipantau), jadi TIDAK ada
  runtuhan entitas pada run ini; dicatat sebagai kandidat cek pendanaan mendalam di run
  berikutnya. Pola serentak 27 wallet membeli GrokBot berukuran ~$167 dalam jendela yang
  sama adalah co-buy saja (keterkaitan LEMAH) — TIDAK meruntuhkan entitas; pendanaan dari
  exchange (bila ada) juga tidak menghitung.
- Pembelian 1–6 wallet saja (simbol) = bukan sinyal, hanya dicatat di atas.
- Catatan celah: tab Holdings tidak dibuka pada run ini, jadi field holdings di state
  tidak diperbarui; aktivitas buy tetap tercatat dari tab Activity. Diskrepansi BNB
  GMGN-vs-on-chain untuk 0xf6a8… dari run sebelumnya belum dicek ulang on-chain pada run
  ini; dibawa maju belum terselesaikan. Buy berlabel "1h" bisa menumpang batas 17:34 WIB
  beberapa menit (pembulatan label GMGN 60–119 menit); dicatat sebagai celah jendela,
  bukan sebagai sinyal. Hitungan dompet 15 (38 Buy) adalah minimum terverifikasi — dompet
  berdagang tiap ~1 menit dan kepadatan baris halaman berubah antar cuplikan; total
  sebenarnya bisa sedikit lebih tinggi.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-05T19:36:00+07:00; seluruh 54 wallet mendapat run46_summary + saldo BNB;
  token simbol-baru di atas kini dikenal untuk wallet masing-masing). Baseline baru =
  state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
---
## Run 47 — Kam 2026-11-05, 21:23–21:36 WIB (jendela sejak ~19:36 WIB; browser task harness-measured 21:23–21:36 WIB)

PUBLIC: 54/54 halaman GMGN BSC termuat publik, 0 login-gated. Tidak ada login, tidak ada
connect wallet, tidak ada sign, tidak ada beli/jual/follow. Tab Holdings tidak dibuka;
field holdings di state tidak diperbarui.

74 peristiwa Buy dalam jendela dari 8 dompet (31 pasti dalam jendela, label <60 mnt;
43 berlabel "1h", batas tidak pasti karena label "1h" = 60–119 mnt sehingga bisa
menumpang batas 19:36 WIB). 46 dompet lain tidak ada Buy baru dalam jendela.

PERNYATAAN CA: Tidak ada contract address (CA) yang diverifikasi. Tab Activity GMGN
hanya menampilkan simbol token, bukan CA — semua pembelian dicatat berdasarkan simbol saja.

CATATAN DUPLIKAT: penugasan browser tidak menyertakan daftar perdagangan run 46,
sehingga browser tidak mencocokkan duplikat jumlah+$ terhadap run 46. Pengecekan
duplikat/token-baru dilakukan parent terhadap state (per-wallet run47_summary).

Rincian per dompet (nomor 1–54, saldo BNB seperti ditampilkan halaman):
1. 0x13d1…6d02 — 0 BNB ($0,008) — — (Tx In 51d)
2. 0x2325…551b — 1,12 BNB ($791,94) — Buy 屎壳郎 73,74 $68,36 (33m, simbol-baru
   untuk dompet ini) + 15,27 $20,44 (1h) + 48,61 $68,44 (1h); Buy 雪球 144,17 $20,45
   (1h) + 444,2 $68,15 (1h) re-trade (dikenal run 43); Buy BURN 1,04K $20,76 (2h)
   re-trade run 44/46, di luar jendela.
3. 0x5b2f…48a5 — 0 BNB ($0,014) — — (Tx In 51d)
4. 0x6ba7…49e7 — 0,001 BNB ($1,05) — — (Tx In 7d)
5. 0x7564…c854 — 0 BNB ($0,03) — — (Tx In 38d)
6. 0x8272…db6a — 0 BNB ($0,011) — — (Tx In 71d)
7. 0x8922…2acc — 0 BNB ($0,041) — — (Tx In 7d; Buy XPIN terakhir 20d lalu)
8. 0x8e96…b8d6 — 0,03 BNB ($21,57) — Buy 狗 126,7K $1.408 (16m, simbol-baru,
   Buy terbesar run ini) + Buy 羊王 192,3K $1,38 (1h, simbol-baru bila dalam
   jendela); Buy 吉祥 200K $1.409 (8h) di luar jendela.
9. 0x93e7…82e1c — 0 BNB ($0,01) — — (Tx In 71d)
10. 0xaab8…026e — 0 BNB ($0) — — (Tx In 10d)
11. 0xb787…1462 — 0,007 BNB ($4,86) — — (Tx In 17d)
12. 0xbe59…3cdf — 0 BNB ($0) — — (Tx In 51d)
13. 0xda91…b71f — 0,05 BNB ($35,48) — — (Tx In 15d)
14. 0xf6a8…ae2cc — 0 BNB ($0) — — (Tx In 15d)
15. 0x9856…44c1 — 0 BNB ($0) — — (Tx Out 3d)
16. 0x3628…1423 — 0,01 BNB ($7,32) — 10 Buy (semua 1,13K $0,07): 打狗 9m;
    KARMA 21m + 33m; NEON 46m; CORLA 57m (re-trade, dikenal run 43–46); DAK 1h x2;
    来财 1h x3. 打狗/KARMA/NEON/DAK/来财 simbol-baru untuk dompet ini.
17. 0xa0c1…b9e — 0,034 BNB ($24,43) — IDENTIK dengan dompet 16 (simbol, jumlah,
    nilai, label waktu sama persis, 10 Buy).
18. 0x40a8…784c — 0,056 BNB ($39,99) — — (Tx In 2d)
19. 0xc7c5…eb74 — 0,012 BNB ($8,2) — 13 Buy (semua 1,13K $0,024): 打狗 7m;
    KARMA 19m + 30m; WUKONG 42m; NEON 52m; DAK 1h x2; CORLA 1h (re-trade);
    来财 1h x4; 钱来 1h. 打狗/KARMA/WUKONG/NEON/DAK/来财/钱来 simbol-baru.
20. 0xad94…656d — 0,087 BNB ($61,78) — IDENTIK dengan dompet 19 kecuali selisih
    waktu ~1 mnt (打狗 8m, KARMA 20m, sisanya sama), 13 Buy.
21. 0x3803…036a — 0,025 BNB ($17,68) — Rotasi sama dengan dompet 19/20, jumlah
    832,25 $0,018, 13 Buy (打狗 8m; KARMA 20m + 31m; WUKONG 42m; NEON 52m;
    DAK 1h x2; CORLA 1h re-trade; 来财 1h x4; 钱来 1h).
22. 0x7488…6650 — 0,01 BNB ($7,16) — 8 Buy: 白小飛 1,1K $0,056 (2m); ZVL 110
    $0,062 (19m); VCHAIN 11 $0,058 (36m); Douyin 110 $0,058 (52m, re-trade run 46);
    孙悟空 1,1K $0,056 (1h); MEMEBET 110K $0,058 (1h); GRCO 110 $0,06 (1h,
    re-trade run 45); NEE 11 $0,06 (1h). 白小飛/ZVL/VCHAIN/孙悟空/MEMEBET/NEE
    simbol-baru untuk dompet ini.
23. 0xdb2d…ea52b — 0,194 BNB ($138,15) — — (Buy GrokBot 6M $187,6 2h, re-trade,
    di luar jendela)
24. 0xc621…d7050 — 0,306 BNB ($217,8) — — (Buy GrokBot 8,4M $167,2 2h, re-trade)
25. 0xf795…f923 — 0,473 BNB ($336,12) — — (Buy GrokBot 2h $1.085 dan $1.363,
    re-trade; ukuran jauh di atas pola ~$167–190 dompet GrokBot lain — dicatat)
26. 0x9cdd…0c1b2 — 0,157 BNB ($111,53) — — (Buy GrokBot 7,2M $191,5 2h, re-trade)
27. 0xaa49…4380d — 0,411 BNB ($292,02) — — (GrokBot 2h, re-trade)
28. 0x82c6…25b9b — 0,232 BNB ($164,4) — — (GrokBot 2h, re-trade)
29. 0x3154…1c32 — 0,246 BNB ($174,81) — — (GrokBot 2h, re-trade)
30. 0xca4e…72f1a — 0,224 BNB ($159,2) — — (Sell GrokBot 2h, bukan buy)
31. 0xe9ed…3895 — 0,195 BNB ($138,56) — — (GrokBot 2h, re-trade)
32. 0x3a39…39c4 — 0,152 BNB ($107,67) — — (GrokBot 2h, re-trade)
33. 0xcb08…5aca3 — 0,16 BNB ($113,88) — — (GrokBot 2h, re-trade)
34. 0xb940…a924 — 0,3 BNB ($212,78) — — (GrokBot 2h, re-trade)
35. 0x4522…4f07 — 0,331 BNB ($234,88) — — (GrokBot 2h, re-trade)
36. 0x5b4b…5024 — 0,265 BNB ($187,91) — — (GrokBot 2h, re-trade)
37. 0xc659…4ef57 — 0,209 BNB ($148,39) — — (GrokBot 2h, re-trade)
38. 0x3623…f30b70 — 0,265 BNB ($187,92) — — (GrokBot 2h, re-trade)
39. 0xf968…de7d20 — 0,284 BNB ($201,42) — — (GrokBot 2h, re-trade)
40. 0x2cc8…1b970 — 0,275 BNB ($194,93) — — (GrokBot 2h, re-trade)
41. 0x1cce…8b645 — 0,322 BNB ($228,22) — — (GrokBot 2h, re-trade)
42. 0xc0c8…031b — 0,171 BNB ($121,27) — — (GrokBot 2h, re-trade)
43. 0xc194…32d5 — 0,191 BNB ($135,2) — — (GrokBot 2h, re-trade)
44. 0xa952…31f31 — 0,263 BNB ($186,29) — — (Sell GrokBot 2h, bukan buy)
45. 0x92bc…2fd314 — 0,329 BNB ($233,56) — — (GrokBot 2h, re-trade)
46. 0x9b51…f8c1a — 0,444 BNB ($315,01) — — (GrokBot 2h, re-trade)
47. 0xfdec…62bf — 0,158 BNB ($112) — — (GrokBot 2h, re-trade)
48. 0x64e8…eb9a — 0,261 BNB ($185,33) — — (GrokBot 2h, re-trade)
49. 0x81c3…de36 — 0,006 BNB ($4,01) — — (Sell 蝴蝶金库 1,8M $557,3 52m bukan buy;
    Buy 蝴蝶金库 914,3K $191,4 2h re-trade run 44/46, di luar jendela)
50. 0x97bd…b3e9 — 0,194 BNB ($137,41) — — (GrokBot 2h, re-trade)
51. 0x341b…457a — 1,24 BNB ($880,07) — — (Tx In 3d)
52. 0xd124…a0c9b — 0,458 BNB ($324,78) — — (Tx In 1d)
53. 0x5cf3…2a0f — 0,97 BNB ($688,59) — — (Tx In 3d)
54. 0x355e…f3db — 0,884 BNB ($627,04) — — (Tx In 1d)

Hitungan sinyal run 47 (entitas, bukan alamat mentah; ambang: minimal 14 entitas berbeda
membeli token baru yang SAMA dengan CA terverifikasi):
- Token dengan CA terverifikasi yang dibeli dalam jendela: TIDAK ADA — tidak ada CA yang
  terverifikasi pada run ini (simbol saja, tab Activity GMGN tidak menampilkan CA). Jadi
  TIDAK ADA SINYAL yang dapat diklaim atas dasar CA.
- Observasi simbol saja dalam jendela (CA UNVERIFIED, BUKAN sinyal): 打狗/KARMA/NEON/
  DAK/来财 5 entitas (klaster mikro-bot 16/17/19/20/21; CORLA tidak dihitung sebagai
  token baru karena re-trade sejak run 43); WUKONG 3 entitas (19/20/21); 钱来 3 entitas
  (19/20/21, semua berlabel "1h"); 屎壳郎 1 entitas (dompet 2, simbol-baru untuk
  dompet itu); 狗 1 entitas (dompet 8, $1.408); 羊王 1 entitas (dompet 8, "1h");
  白小飛/ZVL/VCHAIN/孙悟空/MEMEBET/NEE masing-masing 1 entitas (dompet 22); 雪球
  re-trade (dompet 2, dikenal run 43); Douyin/GRCO re-trade (dompet 22).
- TIDAK ADA SINYAL.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau, jadi tidak
  ada runtuhan entitas. Namun pola klaster mikro-bot MENGUAT pada run ini: dompet 16 vs 17
  identik menit demi menit (simbol, jumlah 1,13K, nilai $0,07, label waktu sama persis
  untuk 10 Buy); dompet 19 vs 20 identik kecuali selisih ~1 menit; dompet 21 mengikuti
  rotasi token yang sama dengan jumlah 832,25/$0,018 — lebih dari sekadar co-buy,
  mengindikasikan skrip/operator yang sama. Ini BELUM memenuhi definisi keterkaitan KUAT
  dalam aturan (pendanaan bersama non-exchange, transfer langsung, pendanaan berantai)
  karena tidak ada bukti pendanaan/transfer yang teramati di halaman GMGN (sumber Tx In
  yang terlihat hanya terpotong / 0x00...0000, tidak dapat dicocokkan dengan alamat yang
  dipantau), jadi TIDAK ada runtuhan entitas pada run ini; dicatat sebagai kandidat cek
  pendanaan mendalam di run berikutnya. Klaster GrokBot (dompet 23–50) kini hanya
  menunjukkan Buy berlabel "2h" — di luar jendela, re-trade run 45–46.
- Pembelian 1–5 wallet saja (simbol) = bukan sinyal, hanya dicatat di atas.
- Catatan celah: tab Holdings tidak dibuka pada run ini, jadi field holdings di state
  tidak diperbarui; aktivitas buy tetap tercatat dari tab Activity. Diskrepansi BNB
  GMGN-vs-on-chain untuk 0xf6a8… dari run sebelumnya belum dicek ulang on-chain pada run
  ini; dibawa maju belum terselesaikan. Buy berlabel "1h" bisa menumpang batas 19:36 WIB
  beberapa menit (pembulatan label GMGN 60–119 menit); dicatat sebagai celah jendela,
  bukan sebagai sinyal. Pengecekan duplikat run 46 oleh browser tidak dilakukan (daftar
  run 46 tidak disertakan dalam penugasan); pengecekan duplikat/token-baru dilakukan
  parent terhadap state dan dicatat di per-wallet run47_summary.
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-05T21:36:00+07:00; seluruh 54 wallet mendapat run47_summary + saldo BNB;
  token simbol-baru di atas kini dikenal untuk wallet masing-masing). Baseline baru =
  state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
---
---

## Run 48 — 2026-11-06 01:27-01:55 WIB (jendela sejak run 47 berakhir 2026-11-05 21:36 WIB)

PUBLIC: 54/54 halaman GMGN BSC termuat publik, 0 login-gated. 895 Buy ≤3h dari 33
dompet (21 dompet tanpa Buy). Tidak ada login, tidak ada connect wallet, tidak ada
sign. Tab Holdings tidak dibuka. CA token TIDAK ditampilkan di halaman Activity
dompet mana pun — hanya simbol. Data GMGN adalah agregat sekunder, bukan bukti
on-chain mentah.

Per dompet (nomor = urutan penugasan; saldo BNB = yang tampil di GMGN):
1. 0x13d1…6d02 — 0 BNB ($0,008) — — (Tx In saja, terbaru 51d)
2. 0x2325…551b — 1,15 BNB ($794,54) — Buy 盘古 0,569 $66,41 (3h, simbol-baru,
   batas tidak pasti) + Buy OSK 423,9K $67,63 (3h, re-trade dikenal run 41,
   batas tidak pasti); Sell OSK + Sell 盘古 2h lalu bukan buy
3. 0x5b2f…48a5 — 0 BNB ($0,013) — — (Tx In saja, terbaru 51d)
4. 0x6ba7…49e7 — 0,001 BNB ($1,03) — — (Tx In saja, terbaru 7d)
5. 0x7564…5854 — 0 BNB ($0,03) — — (Tx In saja, terbaru 38d)
6. 0x8272…8db6a — 0 BNB ($0,011) — — (Tx In saja, terbaru 71d)
7. 0x8922…2acc — 0 BNB ($0,04) — — (Tx In saja, terbaru 7d; Buy terakhir XPIN 20d)
8. 0x8e96…b8d6 — 0,033 BNB ($22,58) — Buy 小黄书 174,4K $1,359 (detik lalu,
   simbol-baru) + Buy 币安一直在 146,6K $1,363 (2h, simbol-baru)
9. 0x93e7…82e1c — 0 BNB ($0,01) — — (Tx In saja, terbaru 71d)
10. 0xaab8…026e — 0 BNB ($0) — — (Tx In saja, terbaru 10d, SKYAI)
11. 0xb787…1462 — 0,007 BNB ($4,75) — — (Tx In saja, terbaru 17d, SKYAI +24,8M)
12. 0xbe59…3cdf — 0 BNB ($0) — — (Tx In saja, terbaru 51d)
13. 0xda91…ab71f — 0,05 BNB ($34,65) — — (Tx In saja, terbaru 15d)
14. 0xf6a8…2cc — 0 BNB ($0) — — (Tx In saja, terbaru 15d, NEX +1)
15. 0x9856…844c1 — 0 BNB ($0) — — (Tx Out BNB −0,065 3d; Buy terakhir 鼻涕 $0,498 4d)
16. 0x3628…1423 — 0,012 BNB ($8,11) — 28 Buy mikro 1,13K $0,068–$0,070:
    simbol-baru HODL x2, BenBen x3, 白头老 x1, DEF x1, XAP x1; re-trade CORLA x14,
    雪球 x1, CStock x1, 打狗 x4
17. 0xa0c1…9b9e — 0,034 BNB ($23,63) — 25 Buy mikro 1,13K $0,068–$0,070:
    simbol-baru HODL x2, BenBen x1, 白头老 x1, DEF x1, XAP x1; re-trade CORLA x13,
    雪球 x1, CStock x1, 打狗 x4
18. 0x40a8…784c — 0,056 BNB ($39,01) — — (Tx In saja, terbaru 2d, BTW +5M,
    SKYAI +5M; Buy terakhir NITRO $5,002 4d)
19. 0xc7c5…2eb74 — 0,011 BNB ($7,33) — 41 Buy mikro 1,13K $0,024: simbol-baru
    BenBen x5, TSLA x2, Shillion, JOB, TIRED, MCRIB, SPY, HARRIET, WIF, FXH,
    equitittie, 白头老, DEF, XAP + 2 token tanpa nama (hanya logo, tidak
    teridentifikasi, tidak dihitung); re-trade CORLA x15, HODL x1, 雪球 x1, 打狗 x6
20. 0xad94…656d — 0,089 BNB ($61,72) — 36 Buy mikro 1,13K $0,024: simbol-baru
    BenBen x3, TSLA x1, Shillion, JOB, TIRED, MCRIB, SPY, HARRIET, WIF,
    equitittie, 白头老, DEF, XAP + 1 token tanpa nama; re-trade CORLA x15,
    HODL x1, 雪球 x1, 打狗 x6
21. 0x3803…036a — 0,026 BNB ($18,25) — 41 Buy mikro 832,25 $0,017–$0,018:
    simbol-baru BenBen x5, TSLA x2, Shillion, JOB, TIRED, MCRIB, SPY, HARRIET,
    WIF, FXH, equitittie, 白头老, DEF, XAP + 1 token tanpa nama (2h); re-trade
    CORLA x17, HODL x1, 雪球 x1, 打狗 x5
22. 0x7488…6650 — 0,01 BNB ($7,15) — 17 Buy mikro (~$0,99): simbol-baru KRX,
    GAI, AUPRO, 抱抱币, GOAI, 狗狗笑死了, AUBANK, HDAI, ADIDAS, ZKST, BSGE,
    DRLE; TSLA/PIVT/ZEST/ZKIN simbol rotasi dikenal (run 16/42/44), bukan baru;
    Douyin re-trade run 45–47
23. 0xdb2d…ea52b — 0,023 BNB ($16,19) — 26 Buy: ASI x18 (simbol-baru), PYRO x6
    (re-trade run 16), CORLA x2 (re-trade run 45)
24. 0xc621…d7050 — 0,306 BNB ($212,34) — 25 Buy: ASI x20 (simbol-baru), PYRO x1,
    CORLA x4
25. 0xf795…f923 — 0,038 BNB ($26,37) — 28 Buy: ASI x21 (simbol-baru), PYRO x2,
    CORLA x5
26. 0x9cdd…0c1b2 — 0,25 BNB ($173,5) — 26 Buy: ASI x20 (simbol-baru), PYRO x3,
    CORLA x3
27. 0xaa49…4380d — 0,097 BNB ($67,42) — 24 Buy: ASI x19 (simbol-baru), PYRO x1,
    CORLA x4
28. 0x82c6…25b9b — 0,033 BNB ($22,83) — 34 Buy: ASI x31 (simbol-baru), PYRO x2,
    CORLA x1
29. 0x3154…1c32 — 0,032 BNB ($22,38) — 16 Buy: ASI x13 (simbol-baru), PYRO x1,
    CORLA x2
30. 0xca4e…72f1a — 0,261 BNB ($180,86) — 23 Buy: ASI x18 (simbol-baru), PYRO x4,
    CORLA x1
31. 0xe9ed…3895 — 0,349 BNB ($242) — 22 Buy: ASI x20 (simbol-baru), PYRO x1,
    CORLA x1
32. 0x3a39…39c4 — 0,336 BNB ($233,14) — 32 Buy: ASI x28 (simbol-baru), PYRO x3,
    CORLA x1
33. 0xcb08…5aca3 — 0,306 BNB ($212,28) — 31 Buy: ASI x26 (simbol-baru), PYRO x4,
    CORLA x1
34. 0xb940…a924 — 0,352 BNB ($243,73) — 32 Buy: ASI x24 (simbol-baru), PYRO x2,
    CORLA x6
35. 0x4522…4f07 — 0,214 BNB ($148,65) — 20 Buy: ASI x16 (simbol-baru), PYRO x1,
    CORLA x3
36. 0x5b4b…5024 — 0,301 BNB ($208,39) — 31 Buy: ASI x26 (simbol-baru), PYRO x2,
    CORLA x3
37. 0xc659…4ef57 — 0,292 BNB ($202,29) — 27 Buy: ASI x21 (simbol-baru), PYRO x5,
    CORLA x1
38. 0x3623…f30b70 — 0,3 BNB ($208,26) — 31 Buy: ASI x26 (simbol-baru), PYRO x3,
    CORLA x2
39. 0xf968…de7d20 — 0,301 BNB ($208,47) — 16 Buy: ASI x11 (simbol-baru), PYRO x2,
    CORLA x3
40. 0x2cc8…1b970 — 0,301 BNB ($208,49) — 31 Buy: ASI x25 (simbol-baru), PYRO x2,
    CORLA x4
41. 0x1cce…8b645 — 0,301 BNB ($208,33) — 27 Buy: ASI x22 (simbol-baru), PYRO x2,
    CORLA x3
42. 0xc0c8…031b — 0,301 BNB ($208,38) — 25 Buy: ASI x18 (simbol-baru), PYRO x4,
    CORLA x3
43. 0xc194…32d5 — 0,301 BNB ($208,22) — 20 Buy: ASI x18 (simbol-baru), PYRO x1,
    CORLA x1
44. 0xa952…31f31 — 0,3 BNB ($207,91) — 24 Buy: ASI x20 (simbol-baru), PYRO x2,
    CORLA x2
45. 0x92bc…2fd314 — 0,3 BNB ($207,93) — 29 Buy: ASI x26 (simbol-baru), PYRO x2,
    CORLA x1
46. 0x9b51…f8c1a — 0,3 BNB ($208) — 27 Buy: ASI x23 (simbol-baru), PYRO x2,
    CORLA x2
47. 0xfdec…62bf — 0,3 BNB ($207,99) — 25 Buy: ASI x22 (simbol-baru), PYRO x1,
    CORLA x2
48. 0x64e8…eb9a — 0,3 BNB ($208,04) — 33 Buy: ASI x30 (simbol-baru), PYRO x1,
    CORLA x2
49. 0x81c3…de36 — 0,006 BNB ($3,91) — — (Tx Out USDT −100 4h; Buy terakhir
    蝴蝶金库 914,3K $191,4 6h, re-trade run 44/46, di luar jendela)
50. 0x97bd…b3e9 — 0,301 BNB ($208,1) — 18 Buy: ASI x14 (simbol-baru), PYRO x2,
    CORLA x2
51. 0x341b…457a — 1,24 BNB ($858,89) — — (Tx In 3d: SPACEDOG +10M, CHICK +10K,
    ACF +16K, SAIL +100K)
52. 0xd124…a0c9b — 0,458 BNB ($316,91) — — (Tx In 1d: BAYC +950, PANBA +2K,
    市安加油 +50M, 合一 +66,58)
53. 0x5cf3…2a0f — 0,97 BNB ($671,75) — — (Tx In 3d: GOATT +1K, AGENTOK +100K;
    Buy terakhir BOT 9,6M $37,15 9d)
54. 0x355e…f3db — 0,884 BNB ($611,92) — — (Tx In 1d: PANBA +2K, 珍珠币 +88,59;
    Sell terakhir AGC 2,2M $5,763 2d)

Hitungan sinyal run 48 (entitas, bukan alamat mentah; ambang: minimal 14 entitas
berbeda membeli token baru yang SAMA dengan CA terverifikasi):
- Token dengan CA terverifikasi yang dibeli dalam jendela: TIDAK ADA — tidak ada CA
  yang terverifikasi pada run ini (tab Activity GMGN hanya menampilkan simbol).
  Jadi TIDAK ADA SINYAL yang dapat diklaim atas dasar CA.
- Observasi simbol saja dalam jendela (CA UNVERIFIED, BUKAN sinyal): ASI
  simbol-baru untuk 27 entitas (dompet 23–48 + 50, klaster GrokBot; label 12m–2h,
  ukuran mayoritas ~$162) — secara angka di atas ambang 14, tetapi CA tidak
  terverifikasi sehingga BUKAN sinyal; CORLA dibeli 32 dompet tetapi re-trade
  (dikenal sejak run 43/45); PYRO dibeli 27 dompet tetapi re-trade (dikenal sejak
  run 16); BenBen/白头老/DEF/XAP simbol-baru 5 entitas (klaster mikro-bot
  16/17/19/20/21); TSLA/Shillion/JOB/TIRED/MCRIB/SPY/HARRIET/WIF/FXH/equitittie
  simbol-baru 3 entitas (19/20/21); HODL simbol-baru 2 entitas (16/17);
  盘古 simbol-baru 1 entitas (dompet 2, label 3h batas tidak pasti; 盘古重生 di
  baseline adalah nama token berbeda); 小黄书/币安一直在 simbol-baru 1 entitas
  (dompet 8); 12 simbol dompet 22 masing-masing 1 entitas.
- TIDAK ADA SINYAL.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau,
  jadi tidak ada runtuhan entitas. Namun pola klaster MENGUAT lagi pada run ini:
  (a) klaster mikro-bot 16/17/19/20/21 — 16 vs 17 ukuran tetap 1,13K
  ($0,068–$0,070) dengan simbol/label menit sama di sebagian besar baris awal,
  19 vs 20 ukuran 1,13K ($0,024) dengan ~12 Buy pertama identik simbol/waktu,
  21 mengikuti rotasi yang sama dengan ukuran 832,25 ($0,017–$0,018) — pola
  skrip/operator yang sama; (b) klaster GrokBot (dompet 23–48, 50) kini
  serentak membeli ASI+PYRO+CORLA dengan ukuran ~$162 setelah GrokBot ~6h lalu;
  (c) saldo BNB klaster 36–48 dan 50 kini konvergen ~0,30–0,35 BNB (banyak yang
  persis 0,301) vs 0,15–0,47 di run 47. Semua ini masih co-buy / co-balance
  saja: tidak ada bukti pendanaan bersama non-exchange / transfer langsung /
  pendanaan berantai yang teramati (sumber Tx In yang terlihat hanya terpotong,
  tidak dapat dicocokkan), jadi TIDAK ada runtuhan entitas pada run ini;
  dicatat sebagai kandidat cek pendanaan mendalam di run berikutnya.
- Pembelian 1–5 wallet saja (simbol) = bukan sinyal, hanya dicatat di atas.
- Catatan celah: tab Holdings tidak dibuka pada run ini, jadi field holdings di
  state tidak diperbarui; aktivitas buy tetap tercatat dari tab Activity.
  Diskrepansi BNB GMGN-vs-on-chain untuk 0xf6a8… dari run sebelumnya belum
  dicek ulang on-chain pada run ini; dibawa maju belum terselesaikan. Buy
  berlabel "3h" bisa menumpang batas 21:36 WIB beberapa menit (label GMGN
  180–239 menit sebelum pembacaan); dicatat sebagai celah jendela, bukan
  sebagai sinyal. Waktu run: harness-measured 01:27–01:55 WIB; laporan browser
  01:27–01:52 WIB (selisih akhir 3 menit dicatat).
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-06T01:55:00+07:00; seluruh 54 wallet mendapat run48_summary + saldo
  BNB; token simbol-baru di atas kini dikenal untuk wallet masing-masing).
  Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 49 — 2026-11-06 03:23-03:47 WIB (jendela sejak run 48 berakhir 01:55 WIB)

PUBLIC: 54/54 halaman GMGN BSC termuat publik, 0 login-gated. Tidak ada login, tidak ada connect wallet, tidak ada
sign. Tab Holdings tidak dibuka. CA token TIDAK ditampilkan di halaman Activity dompet mana pun — hanya simbol
(kolom Type, Token, MC, Amount, Total USD, Profit, Age, Gas, Share; ikon salin di samping nama token tidak diklik,
fungsinya tidak terverifikasi). Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

Per dompet (nomor = urutan penugasan; saldo BNB = yang tampil di GMGN):
1. 0x13d1…6d02 — 0 BNB ($0,008) — — (Tx In saja, terbaru 51d)
2. 0x2325…551b — 1,15 BNB ($793,38) — — (Sell OSK 423,9K $85,53 4h + Buy OSK 423,9K $67,63 5h, pra-jendela)
3. 0x5b2f…48a5 — 0 BNB ($0,013) — — (Tx In saja, terbaru 51d)
4. 0x6ba7…49e7 — 0,001 BNB ($1,02; halaman sempat memuat lambat) — — (Tx In saja, terbaru 7d)
5. 0x7564…c854 — 0 BNB ($0,03) — — (Tx In saja, terbaru 38d)
6. 0x8272…db6a — 0 BNB ($0,011) — — (Tx In saja, terbaru 71d)
7. 0x8922…3acc — 0 BNB ($0,04) — — (Tx In saja, terbaru 7d; Buy terakhir XPIN $4,2K 20d)
8. 0x8e96…b8d6 — 0,036 BNB ($25,06) — Buy 小黄书 174,4K $1,359 (1h) adalah DUPLIKAT trade run 48
   (jumlah/nilai identik, bukan buy baru); Sell 小黄书 174,4K $2,579 (+$1,18) 50m dalam jendela
9. 0x93e7…82e1c — 0 BNB ($0,01) — — (Tx In saja, terbaru 71d)
10. 0xaab8…026e — 0 BNB ($0) — — (Tx In saja, terbaru 10–11d, SKYAI)
11. 0xb787…1462 — 0,007 BNB ($4,74) — — (Tx In saja, terbaru 17d, SKYAI +24,8 jt $705,4K dari 0xed…8771)
12. 0xbe59…3cdf — 0 BNB ($0) — — (Tx In saja, terbaru 51d)
13. 0xda91…b71f — 0,05 BNB ($34,63) — — (Tx In saja, terbaru 15–17d)
14. 0xf6a8…e2cc — 0 BNB ($0) — — (Tx In saja, terbaru 15–29d)
15. 0x9856…44c1 — 0 BNB ($0) — — (Tx Out BNB −0,065 ke 0xd9…e5fb 3d; Buy/Sell terakhir 4d)
16. 0x3628…1423 — 0,01 BNB ($7,15) — 12 Buy: CORLA 1,13K $0,068–$0,069 x10 (re-trade),
    白头老 1,13K $0,068 15m (re-trade, dikenal run 48), 蝴蝶金 1,13K $0,069 27m (re-trade,
    dikenal run 46); batas tak pasti 2h: CORLA x4, HODL x1 (tidak dihitung); Sell CORLA
    $0,102–$0,151 (+$0,025–$0,077 per Sell), 白头老 $0,116 +$0,044, 蝴蝶金 $0,144 +$0,071
17. 0xa0c1…9b9e — 0,034 BNB ($23,59) — 14 Buy: GANG 3,88K $0,069 2m (simbol-baru, 1 entitas);
    CORLA x11 (re-trade; 1,13K $0,068–$0,069 x10 + 38,79K $0,069 26m), 白头老 1,13K $0,068 16m
    (re-trade), 蝴蝶金 1,13K $0,069 27m (re-trade); batas tak pasti 2h: CORLA x4, HODL x1;
    Burn CORLA 38,79K 26m; Sell CORLA $0,0₆5243 −$0,073 1h
18. 0x40a8…784c — 0,056 BNB ($38,98) — — (Tx In saja, terbaru 2d; Buy terakhir NITRO 4d)
19. 0xc7c5…eb74 — 0,011 BNB ($7,75) — 26 Buy mikro 1,13K $0,024: simbol-baru Punjimogui x1,
    WIRELYSS x1, Hedgecat x2, 11/5 x1, OPOS x1, DNUT x2, Edmond x1, HAROLD x1, Envelope x1,
    COGE x3; re-trade CORLA x9, 白头老 x2, 蝴蝶金 x1; Sell kecil untung +$0,06–$0,14 per Sell
    (mis. Punjimogui +$0,063, WIRELYSS +$0,134)
20. 0xad94…656d — 0,091 BNB ($62,66) — 26 Buy mikro 1,13K $0,024, pola identik dompet 19
    (~1 mnt lebih lambat): simbol-baru Punjimogui x2, WIRELYSS x1, Hedgecat x2, 11/5 x1,
    OPOS x1, DNUT x2, Edmond x1, HAROLD x1, Envelope x1, COGE x3; re-trade CORLA x9,
    白头老 x2, 蝴蝶金 x1; Sell pola sama, untung kecil per Sell
21. 0x3803…036a — 0,027 BNB ($18,92) — 26 Buy mikro 832,25 $0,017, pola identik dompet 19/20:
    simbol-baru Punjimogui x2, WIRELYSS x1, Hedgecat x2, 11/5 x1, OPOS x1, DNUT x2,
    Edmond x1, HAROLD x1, Envelope x1, COGE x3; re-trade CORLA x9, 白头老 x2; TANPA Buy
    蝴蝶金 dalam jendela; Sell pola sama, untung kecil per Sell
22. 0x7488…6650 — 0,01 BNB ($7,22) — 9 Buy: simbol-baru GBRN 11 $0,058 1m, DGPT 110 $0,06 17m,
    VDAO 110 $0,058 19m, GILO 110K $0,058 37m, MEIN 1,1K $0,055 53m, SEG 110K $0,06 1h,
    LORE 11K $0,054 1h, LOGS 110 $0,057 1h; re-trade MEMEBET 110 $0,06 1h (BUKAN duplikat
    run 47 — jumlah berbeda dari 110K $0,058); batas tak pasti 2h: KRX, GAI, PIVT, AUPRO x4;
    Sell dalam jendela: DGPT +$0,026, VDAO −$0,019, GILO +$0,026, MEIN +$0,025, SEG +$0,021,
    LORE +$0,024, MEMEBET +$0,026, LOGS −$0,011
23. 0xdb2d…a52b — 0,397 BNB ($274,54; naik dari 0,023 run 48) — 9 Buy: 天蝎 x3 (5,3 jt $83,07;
    7,9 jt $134,9; 8,6 jt $108,8 — semua ~11–12m, simbol-baru); PYRO x6 (re-trade, 1h);
    batas tak pasti 2h: ASI x11 (duplikat run 48); Sell 天蝎 11 jt $211,5 +$30,81,
    PYRO $247,5 +$85,18
24. 0xc621…7050 — 0,546 BNB ($377,86; naik dari 0,306 run 48) — 5 Buy: 天蝎 x4 ($274,7; $140,5;
    $181,6; $187,1 — simbol-baru); PYRO x1 $187,1 (re-trade); batas tak pasti 2h: ASI x7;
    Sell 天蝎 7 jt $333,7 +$71,37
25. 0xf795…f923 — 0,176 BNB ($122,06) — 5 Buy: 天蝎 x3 ($1,778; $198,6; $171,7 — simbol-baru);
    PYRO x2 (re-trade); batas tak pasti 2h: PYRO x1, ASI x8; Sell 天蝎 8,7 jt $100,2 −$101,25,
    PYRO 8,1 jt $100,1 −$123,23
26. 0x9cdd…c1b2 — 0,33 BNB ($228,17) — 6 Buy: 天蝎 x3 ($202; $12,01; $187,1 — simbol-baru);
    PYRO x3 (re-trade); batas tak pasti 2h: ASI x12; Sell 天蝎 6,5 jt $197,4 +$17,71
27. 0xaa49…380d — 0,299 BNB ($207,25) — 3 Buy: 天蝎 x2 ($187,1; $0,078 — simbol-baru);
    PYRO x1 $140,2 (re-trade); batas tak pasti 2h: ASI x5; Sell 天蝎 −$0,141, PYRO +$4,9
28. 0x82c6…5b9b — 0,19 BNB ($131,78) — 5 Buy: 天蝎 x3 ($2,167; $244,3; $169,4 — simbol-baru);
    PYRO x2 (re-trade); batas tak pasti 2h: ASI x11; Sell 天蝎 8,3 jt $105 −$142,39,
    PYRO 8,7 jt $97,92 −$111,02
29. 0x3154…1c32 — 0,318 BNB ($220,29) — 2 Buy: 天蝎 7,6 jt $171,2 (simbol-baru); PYRO 4,7 jt
    $185,4 (re-trade); batas tak pasti 2h: ASI x6; Sell 天蝎 +$3,17, PYRO −$60,24
30. 0xca4e…3f1a — 0,322 BNB ($222,85) — 4 Buy: 天蝎 x2 ($186,9; $0,078 — simbol-baru);
    PYRO x2 (re-trade); batas tak pasti 2h: PYRO x2, ASI x12; Sell 天蝎 +$20,57
31. 0xe9ed…3895 — 0,542 BNB ($375,7; naik dari 0,349 run 48) — 6 Buy, semua 天蝎 (simbol-baru):
    $1,119; $1,388; $1,161; $181,9; $130,1; $187; batas tak pasti 2h: PYRO x1, ASI x8;
    Sell 天蝎 7,6 jt $268,2 +$107,1
32. 0x3a39…39c4 — 0,407 BNB ($282,45) — 3 Buy: 天蝎 x2 ($240,8; $108,9 — simbol-baru);
    PYRO x1 $117,5 (re-trade); batas tak pasti 2h: PYRO x2, ASI x14; Sell 天蝎 −$0,838
33. 0xcb08…aca3 — 0,193 BNB ($133,74) — 5 Buy: 天蝎 x3 ($320,6; $235,6; $187,1 — simbol-baru);
    PYRO x2 (re-trade); batas tak pasti 2h: PYRO x2, ASI x10; Sell 天蝎 14,5 jt $189,3 +$51,79
34. 0xb940…a924 — 0,336 BNB ($233,08) — 4 Buy: 天蝎 x2 ($8,948; $187,1 — simbol-baru);
    PYRO x2 (re-trade); batas tak pasti 2h: ASI x14; Sell PYRO 8,3 jt $125,3 −$69,5
35. 0x4522…4f07 — 0,375 BNB ($260,13) — 2 Buy: 天蝎 7,4 jt $138,7 (simbol-baru); PYRO 5,8 jt
    $187,4 (re-trade); batas tak pasti 2h: ASI x7; Sell 天蝎 +$28,04, PYRO −$59,28
36. 0x5b4b…5024 — 0,195 BNB ($135,34) — 2 Buy, semua 天蝎 (simbol-baru): 5,9 jt $211,5;
    6,6 jt $186,9; batas tak pasti 2h: PYRO x2, ASI x13; Sell 天蝎 6 jt $112,6 −$102,16
37. 0xc659…ef57 — 0,344 BNB ($238,05) — 4 Buy: 天蝎 4,4 jt $140,1 (simbol-baru); PYRO x3 kecil
    ($0,124; $0,14; $0,14 — re-trade); batas tak pasti 2h: PYRO x2, ASI x10; Tx In BAN +137
    dari 0x75…0d21 $0,029 2h lalu (batas tak pasti, BUKAN dalam jendela); Sell PYRO 500,8K
    $20,56 +$7
38. 0x3623…0b70 — 0,217 BNB ($150,07) — 2 Buy: 天蝎 4,1 jt $187 (simbol-baru); PYRO 7,7 jt
    $274,6 (re-trade); batas tak pasti 2h: PYRO x2, ASI x10; Sell 天蝎 −$57,46, PYRO −$218,49
39. 0xf968…7d20 — 0,224 BNB ($154,92) — 1 Buy: 天蝎 5,4 jt $187,3 (simbol-baru); batas tak pasti
    2h: PYRO x2, ASI x4; Sell 天蝎 −$52,88, PYRO +$3,23
40. 0x2cc8…b970 — 0,28 BNB ($194,21) — 4 Buy, semua 天蝎 (simbol-baru): 450,8K $14,74;
    940,7K $26,93; 91,04K $1,516; 11 jt $187,1; batas tak pasti 2h: PYRO x2, ASI x7;
    Sell 天蝎 13,3 jt $185,1 −$23,16
41. 0x1cce…b645 — 0,311 BNB ($215,32) — 5 Buy, semua 天蝎 (simbol-baru): $0,145; $0,164;
    $0,164; $187,1; $0,019; batas tak pasti 2h: PYRO x2, ASI x9; Sell 天蝎 +$9,61
42. 0xc0c8…031b — 0,174 BNB ($120,42) — 3 Buy: 天蝎 x2 ($11,37; $187,1 — simbol-baru);
    PYRO x1 $318,8 (re-trade); batas tak pasti 2h: PYRO x3, ASI x4; Sell 天蝎 −$87,14,
    PYRO +$3,29
43. 0xc194…32d5 — 0,314 BNB ($217,62) — 3 Buy, semua 天蝎 (simbol-baru): 3,5 jt $108,2;
    8,5 jt $205,9; 7,7 jt $107,8; batas tak pasti 2h: PYRO x1, ASI x6; Sell 天蝎 +$21,27
44. 0xa952…1f31 — 0,304 BNB ($210,12) — 1 Buy: 天蝎 11,8 jt $186,8 (simbol-baru); batas tak
    pasti 2h: PYRO x2, ASI x9; Sell 天蝎 kecil +$0,09
45. 0x92bc…d314 — 0,232 BNB ($160,5) — 2 Buy, semua 天蝎 (simbol-baru): 5,5 jt $180,3;
    7,5 jt $169,5; batas tak pasti 2h: PYRO x2, ASI x7; Sell 天蝎 7,2 jt $122,7 −$95,38;
    Sell PYRO dalam jendela tercatat (nilai tidak pasti di laporan — dicatat sebagai
    tidak pasti, bukan angka pasti)
46. 0x9b51…8c1a — 0,217 BNB ($150,03) — 1 Buy: 天蝎 3,8 jt $185,1 (simbol-baru); batas tak
    pasti 2h: PYRO x2, ASI x10; Sell 天蝎 −$57,61, PYRO −$91,77
47. 0xfdec…62bf — 0,198 BNB ($136,93) — 2 Buy, semua 天蝎 (simbol-baru): 8,1 jt $209,9;
    9,1 jt $154,1; batas tak pasti 2h: PYRO x1, ASI x5; Sell 天蝎 −$96,33, PYRO −$82,4
48. 0x64e8…eb9a — 0,249 BNB ($172,92) — 1 Buy: 天蝎 4,4 jt $154,2 (simbol-baru); batas tak
    pasti 2h: PYRO x1, ASI x6; Sell 天蝎 −$34,86, PYRO −$19,35
49. 0x81c3…de36 — 0,006 BNB ($3,92) — — (Tx Out USDT −100 6h; Sell 蝴蝶金库 1,8 jt $557,3
    +$161,13 6h, pra-jendela)
50. 0x97bd…b3e9 — 0,224 BNB ($155,11) — 6 Buy, semua 天蝎 (simbol-baru): $0,949; $199,3;
    $15,78; $85,48; $193,3; $92,47; batas tak pasti 2h: PYRO x2, ASI x5; Sell 天蝎 −$71,06
51. 0x341b…757a — 1,24 BNB ($860,63) — — (Tx In saja, terbaru 3d)
52. 0xd124…a0c9b — 0,458 BNB ($317,51) — — (Tx In saja, terbaru 1d)
53. 0x5cf3…720a0f — 0,97 BNB ($672,97) — — (Tx In saja, terbaru 3–4d)
54. 0x355e…f3db — 0,884 BNB ($612,85) — — (Tx In saja, terbaru 1d; Sell AGC 2,2 jt $5,763 2d)

Hitungan sinyal run 49 (entitas, bukan alamat mentah; ambang: minimal 14 entitas
berbeda membeli token baru yang SAMA dengan CA terverifikasi):
- Token dengan CA terverifikasi yang dibeli dalam jendela: TIDAK ADA — tidak ada CA
  yang terverifikasi pada run ini (tab Activity GMGN hanya menampilkan simbol).
  Jadi TIDAK ADA SINYAL yang dapat diklaim atas dasar CA.
- Observasi simbol saja dalam jendela (CA UNVERIFIED, BUKAN sinyal): 天蝎
  simbol-baru untuk 27 entitas (dompet 23–48 + 50; ukuran Buy mayoritas ~$100–$320,
  label 5–21m) — secara angka di atas ambang 14, tetapi CA tidak terverifikasi
  sehingga BUKAN sinyal; ini pola yang sama seperti ASI di run 48 (27 entitas,
  simbol-baru, CA tidak terverifikasi, BUKAN sinyal). Punjimogui/WIRELYSS/Hedgecat/
  11/5/OPOS/DNUT/Edmond/HAROLD/Envelope/COGE simbol-baru masing-masing 3 entitas
  (19/20/21); GANG simbol-baru 1 entitas (17); GBRN/DGPT/VDAO/GILO/MEIN/SEG/LORE/
  LOGS simbol-baru masing-masing 1 entitas (22).
- TIDAK ADA SINYAL.
- Tidak ada keterkaitan KUAT baru yang terverifikasi antar wallet yang dipantau,
  jadi tidak ada runtuhan entitas. Namun pola klaster MENGUAT lagi pada run ini:
  (a) klaster mikro-bot 16/17/19/20/21 — 19 vs 20 vs 21 urutan trade menit demi menit
  identik (rotasi simbol yang sama, ukuran tetap 1,13K $0,024 / 832,25 $0,017,
  Sell untung kecil per trade), 16/17 ukuran tetap 1,13K $0,068–$0,069 — pola
  skrip/operator yang sama; (b) klaster GrokBot (dompet 23–48, 50) kini berotasi
  ASI (2–3h lalu) → PYRO (~1h lalu) → 天蝎 (~10–20m lalu) dengan ukuran Buy
  ~$100–$320 dan waktu tumpang tindih antar dompet — rotasi token yang sama
  secara serentak; (c) saldo BNB klaster GrokBot naik serentak: dompet 23
  0,023→0,397, 24 0,306→0,546, 31 0,349→0,542 (kenaikan dicatat, penyebabnya
  tidak terverifikasi dari GMGN — bukan klaim pendanaan bersama). Semua ini masih
  co-buy / co-balance saja: tidak ada bukti pendanaan bersama non-exchange /
  transfer langsung / pendanaan berantai yang teramati, jadi TIDAK ada runtuhan
  entitas pada run ini; dicatat sebagai kandidat cek pendanaan mendalam di run
  berikutnya.
- Duplikat run 48: 1 kejadian — Buy 小黄书 dompet 8 (174,4K $1,359, jumlah/nilai
  identik dengan trade run 48). MEMEBET dompet 22 BUKAN duplikat (110 $0,06 vs
  110K $0,058 run 47).
- Catatan celah: tab Holdings tidak dibuka pada run ini, jadi field holdings di
  state tidak diperbarui; aktivitas buy tetap tercatat dari tab Activity. Buy
  berlabel "2h" tidak dihitung (batas tak pasti vs 01:55 WIB); untuk dompet 19/20/21
  50 baris terbaru hanya sampai ~1h ke belakang sehingga Buy 2h mereka tidak
  terhitung dalam angka 278. Buy berlabel "1h" di ujung daftar juga membawa
  ketidakpastian kecil yang sama. Nilai Sell PYRO dompet 45 tidak pasti di laporan
  browser — dicatat sebagai tidak pasti, bukan angka pasti. Waktu run:
  harness-measured 03:23–03:47 WIB; laporan browser 03:23–03:44 WIB (selisih akhir
  3 menit dicatat).
- State diperbarui di `tier-ab-watch-state.json` dari laporan ini (last_checked
  2026-11-06T03:47:00+07:00; seluruh 54 wallet mendapat run49_summary + saldo
  BNB; token simbol-baru di atas kini dikenal untuk wallet masing-masing).
  Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 50 — 2026-11-06 05:23-05:34 WIB (INCOMPLETE — gating)
Jendela: pembelian sejak run 49 (~03:47-05:22 WIB). Browser harness-measured 05:23-05:34 WIB; laporan browser 05:24-05:30 WIB, pengecekan ulang 05:31-05:33 WIB. Tab Holdings tidak dibuka; GMGN hanya menampilkan simbol, CA tidak terverifikasi untuk semua token.
- PUBLIK hanya 2/54: dompet 1 (0x13d1…6d02, BNB 0 ($0,008), Tx In terakhir 51d, 7D Tx 0/0, tidak ada Buy dalam jendela) dan dompet 2 (0x2325…8551b, tidak ada Buy dalam jendela; aktivitas teratas 6-7d lalu: Sell OSK 6d $1,15K, Sell 盘古 6d $2,09K, Buy 盘古 6d 1,46B $3,06K, Buy OSK 7d 1,06B $2,01K — 盘古/OSK sudah dikenal, pre-window re-trade).
- LOGIN-GATED 52/54: dompet 3-54. Aktivitas TIDAK teramati, TIDAK dihitung sebagai "tidak ada pembelian". Tidak ada login yang dicoba.
- TEMUAN PENTING: gating bersifat session-level, bukan per-dompet — dompet 1 PUBLIK pada 05:24 WIB lalu LOGIN-GATED pada pengecekan ulang 05:31 WIB; setelah jeda 120 detik tetap gated, dan dompet 3 di tab baru (05:33 WIB) tetap gated. GMGN tampaknya membatasi tampilan profil anonim hingga ~2 profil. Jadi label LOGIN-GATED dompet 3-54 pada run ini TIDAK terkonfirmasi sebagai setelan privat masing-masing dompet — hanya bahwa halamannya tidak terbaca tanpa login saat dikunjungi.
- Total Buy dalam jendela yang terverifikasi: 0. Token BARU dalam jendela: tidak ada yang terverifikasi.
- DISKREPANSI BNB dompet 2: pembacaan browser 0 ($0) vs state run 49 1,15 ($793,38) — TIDAK TERVERIFIKASI, kemungkinan salah baca tampilan GMGN; TIDAK diklaim sebagai perubahan saldo; field BNB di state dipertahankan 1,15 dan diskrepansi dibawa ke run berikutnya (masalah GMGN-vs-on-chain yang sama sudah tercatat belum terselesaikan sejak run 11).
- Hitungan sinyal run 50: TIDAK ADA SINYAL yang dapat diklaim — tidak ada token dengan CA terverifikasi yang dibeli ≥14 entitas, dan 52 dompet tidak terbaca sehingga run ini tidak lengkap.
- Tidak ada keterkaitan KUAT baru yang terverifikasi, jadi tidak ada runtuhan entitas. Flag klaster run 49 (mikro-bot 16/17/19/20/21; GrokBot 23-48+50) TIDAK dapat diverifikasi ulang pada run ini karena dompet-dompet itu tidak terbaca — dibawa ke run berikutnya.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-06T05:34:00+07:00; seluruh 54 wallet mendapat run50_summary; field BNB/holdings tidak berubah). Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
- Langkah lanjut: run berikutnya harus membaca ulang ke-54 dompet; bila gating berlanjut, jeda lebih lama / sesi anonim lain mungkin diperlukan, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).

## Run 51 — 2026-11-06 07:24-07:26 WIB (INCOMPLETE — gating, 0/54 readable)
Jendela: pembelian sejak run 50 (~05:34-07:23 WIB). Browser harness-measured 07:24-07:26 WIB. Tab Holdings tidak dibuka; GMGN hanya menampilkan simbol, CA tidak terverifikasi untuk semua token.
- PUBLIK 0/54 — lebih buruk dari run 50 (2/54): dompet 1 (0x13d1…6d02) LOGIN-GATED pada 07:24 WIB, percobaan ulang di tab baru setelah jeda 30 detik tetap LOGIN-GATED pada 07:25 WIB; dompet 2 (0x2325…8551b) LOGIN-GATED pada 07:25 WIB. Dompet 3-54 TIDAK dibuka, sesuai instruksi berhenti bila gating bertahan; status masing-masing tidak terverifikasi secara individual dan TIDAK dihitung sebagai "tidak ada pembelian". Tidak ada login yang dicoba.
- TEMUAN: gating bersifat session-level, bukan per-dompet — berbeda dengan run 50 (dompet 1-2 masih publik), pada run 51 gating sudah aktif sejak dompet pertama. Kuota tampilan profil anonim GMGN tampaknya belum pulih sejak run 50 (~2 jam sebelumnya). Jadi label LOGIN-GATED pada run ini TIDAK terkonfirmasi sebagai setelan privat masing-masing dompet — hanya bahwa halamannya tidak terbaca tanpa login saat dikunjungi.
- Total Buy dalam jendela yang terverifikasi: 0. Token BARU dalam jendela: tidak ada yang terverifikasi.
- Hitungan sinyal run 51: TIDAK ADA SINYAL yang dapat diklaim — tidak ada token dengan CA terverifikasi yang dibeli ≥14 entitas, dan 54 dompet tidak terbaca sehingga run ini tidak lengkap.
- Tidak ada keterkaitan KUAT baru yang terverifikasi, jadi tidak ada runtuhan entitas. Flag klaster run 49 (mikro-bot 16/17/19/20/21; GrokBot 23-48+50) TIDAK dapat diverifikasi ulang pada run ini karena dompet-dompet itu tidak terbaca — dibawa ke run berikutnya.
- DISKREPANSI BNB dompet 2 (pembacaan run 50: 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings di state tidak berubah.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-06T07:26:00+07:00; seluruh 54 wallet mendapat run51_summary; field BNB/holdings tidak berubah). Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
- Langkah lanjut: run berikutnya harus membaca ulang ke-54 dompet; bila gating berlanjut, jeda lebih lama / sesi anonim lain mungkin diperlukan, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).

## Run 52 — 2026-11-06 11:54-11:56 WIB (INCOMPLETE — gating, 0/54 readable)
Jendela: pembelian sejak run 51 (~07:26-11:53 WIB). Browser harness-measured 11:54-11:56 WIB; laporan browser 11:54-11:55 WIB (selisih akhir 1 menit dicatat). Tab Holdings tidak dibuka; GMGN hanya menampilkan simbol, CA tidak terverifikasi untuk semua token.
- PUBLIK 0/54 — sama dengan run 51 (0/54): dompet 1 (0x13d1…6d02) LOGIN-GATED pada 11:54 WIB, percobaan ulang di tab baru setelah jeda 30 detik tetap LOGIN-GATED; dompet 2 (0x2325…8551b) LOGIN-GATED pada 11:55 WIB; dompet 3 (0x5b2f…648a5) LOGIN-GATED pada 11:55 WIB. Dompet 4-54 TIDAK dibuka, sesuai instruksi berhenti bila gating bertahan; status masing-masing tidak terverifikasi secara individual dan TIDAK dihitung sebagai "tidak ada pembelian". Tidak ada login yang dicoba.
- TEMUAN: gating bersifat session-level, bukan per-dompet — gating sudah aktif sejak dompet pertama, sama seperti run 51. Kuota tampilan profil anonim GMGN tampaknya belum pulih sejak run 50 (~6,5 jam sebelumnya), meski jeda sejak run 51 sudah ~4,5 jam. Jadi label LOGIN-GATED pada run ini TIDAK terkonfirmasi sebagai setelan privat masing-masing dompet — hanya bahwa halamannya tidak terbaca tanpa login saat dikunjungi.
- Total Buy dalam jendela yang terverifikasi: 0. Token BARU dalam jendela: tidak ada yang terverifikasi.
- Hitungan sinyal run 52: TIDAK ADA SINYAL yang dapat diklaim — tidak ada token dengan CA terverifikasi yang dibeli ≥14 entitas, dan 54 dompet tidak terbaca sehingga run ini tidak lengkap.
- Tidak ada keterkaitan KUAT baru yang terverifikasi, jadi tidak ada runtuhan entitas. Flag klaster run 49 (mikro-bot 16/17/19/20/21; GrokBot 23-48+50) TIDAK dapat diverifikasi ulang pada run ini karena dompet-dompet itu tidak terbaca — dibawa ke run berikutnya.
- DISKREPANSI BNB dompet 2 (pembacaan run 50: 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings di state tidak berubah.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-06T11:56:00+07:00; seluruh 54 wallet mendapat run52_summary; field BNB/holdings tidak berubah). Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
- Langkah lanjut: run berikutnya harus membaca ulang ke-54 dompet; bila gating berlanjut, jeda lebih lama / sesi anonim lain mungkin diperlukan, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
## Run 53 — 2026-11-06 15:53-15:54 WIB (INCOMPLETE — gating, 0/54 readable)
Jendela: pembelian sejak run 52 (~11:56-15:52 WIB). Browser harness-measured 15:53-15:54 WIB; laporan browser 15:53-15:54 WIB. Tab Holdings tidak dibuka; GMGN hanya menampilkan simbol, CA tidak terverifikasi untuk semua token.
- PUBLIK 0/54 — sama dengan run 51-52 (0/54): dompet 1 (0x13d1…6d02) LOGIN-GATED pada 15:53 WIB, percobaan ulang di tab baru setelah jeda 30 detik tetap LOGIN-GATED pada 15:54 WIB; dompet 2 (0x2325…8551b) LOGIN-GATED pada 15:54 WIB. Dompet 3-54 TIDAK dibuka, sesuai instruksi berhenti bila gating bertahan; status masing-masing tidak terverifikasi secara individual dan TIDAK dihitung sebagai "tidak ada pembelian". Tidak ada login yang dicoba.
- TEMUAN: gating bersifat session-level, bukan per-dompet — gating sudah aktif sejak dompet pertama, sama seperti run 51-52. Kuota tampilan profil anonim GMGN tampaknya belum pulih sejak run 50 (~10,5 jam sebelumnya), meski jeda sejak run 52 sudah ~4 jam (frekuensi cron kini 4 jam per amandemen 2026-11-06 ~07:49 WIB). Jadi label LOGIN-GATED pada run ini TIDAK terkonfirmasi sebagai setelan privat masing-masing dompet — hanya bahwa halamannya tidak terbaca tanpa login saat dikunjungi.
- Total Buy dalam jendela yang terverifikasi: 0. Token BARU dalam jendela: tidak ada yang terverifikasi.
- Hitungan sinyal run 53: TIDAK ADA SINYAL yang dapat diklaim — tidak ada token dengan CA terverifikasi yang dibeli ≥14 entitas, dan 54 dompet tidak terbaca sehingga run ini tidak lengkap.
- Tidak ada keterkaitan KUAT baru yang terverifikasi, jadi tidak ada runtuhan entitas. Flag klaster run 49 (mikro-bot 16/17/19/20/21; GrokBot 23-48+50) TIDAK dapat diverifikasi ulang pada run ini karena dompet-dompet itu tidak terbaca — dibawa ke run berikutnya.
- DISKREPANSI BNB dompet 2 (pembacaan run 50: 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings di state tidak berubah.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-06T15:54:00+07:00; seluruh 54 wallet mendapat run53_summary; field BNB/holdings tidak berubah). Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
- Langkah lanjut: run berikutnya harus membaca ulang ke-54 dompet; bila gating berlanjut, jeda lebih lama / sesi anonim lain mungkin diperlukan, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).

## Run 54 — 2026-11-06 18:32-18:33 WIB (INCOMPLETE — gating, 0/54 readable)
Jendela: pembelian sejak run 53 (~15:54-18:31 WIB). Browser harness-measured 18:32-18:33 WIB; laporan browser 18:32-18:33 WIB. Tab Holdings tidak dibuka; GMGN hanya menampilkan simbol, CA tidak terverifikasi untuk semua token.
- PUBLIK 0/54 — sama dengan run 51-53 (0/54): dompet 1 (0x13d1…6d02) LOGIN-GATED pada 18:32 WIB, percobaan ulang di tab baru setelah jeda 30 detik tetap LOGIN-GATED pada 18:33 WIB. Dompet 2-54 TIDAK dibuka, sesuai instruksi berhenti bila gating bertahan; status masing-masing tidak terverifikasi secara individual dan TIDAK dihitung sebagai "tidak ada pembelian". Tidak ada login yang dicoba.
- TEMUAN: klaim konteks run bahwa verifikasi login GMGN pukul 18:30 WIB sudah membuka kembali pembacaan tier-ab TIDAK terkonfirmasi dari sisi read-only ini — halaman tetap menampilkan panel "You are not logged in to GMGN" dengan tombol "Log in" / "Sign Up" dan status "Disconnected"; verifikasi 18:30 itu tampaknya tidak terbawa ke sesi/profil browser ini. Gating bersifat session-level, bukan per-dompet — gating sudah aktif sejak dompet pertama, sama seperti run 51-53. Kuota tampilan profil anonim GMGN tampaknya belum pulih sejak run 50 (~13 jam sebelumnya), meski jeda sejak run 53 sudah ~2,5 jam (frekuensi cron kini 4 jam per amandemen 2026-11-06 ~07:49 WIB; run ini dijadwalkan 18:32 WIB). Jadi label LOGIN-GATED pada run ini TIDAK terkonfirmasi sebagai setelan privat masing-masing dompet — hanya bahwa halamannya tidak terbaca tanpa login saat dikunjungi.
- Total Buy dalam jendela yang terverifikasi: 0. Token BARU dalam jendela: tidak ada yang terverifikasi.
- Hitungan sinyal run 54: TIDAK ADA SINYAL yang dapat diklaim — tidak ada token dengan CA terverifikasi yang dibeli ≥14 entitas, dan 54 dompet tidak terbaca sehingga run ini tidak lengkap.
- Tidak ada keterkaitan KUAT baru yang terverifikasi, jadi tidak ada runtuhan entitas. Flag klaster run 49 (mikro-bot 16/17/19/20/21; GrokBot 23-48+50) TIDAK dapat diverifikasi ulang pada run ini karena dompet-dompet itu tidak terbaca — dibawa ke run berikutnya.
- DISKREPANSI BNB dompet 2 (pembacaan run 50: 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings di state tidak berubah.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-06T18:33:00+07:00; seluruh 54 wallet mendapat run54_summary; field BNB/holdings tidak berubah). Baseline baru = state ini.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
- Langkah lanjut: run berikutnya harus membaca ulang ke-54 dompet; bila gating berlanjut, jeda lebih lama / sesi anonim lain mungkin diperlukan, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).

## Run 55 — Jumat 2026-11-06, 19:53–19:54 WIB (INCOMPLETE, login-gated)

- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat inti (Tier A privat 13 + Tier B privat 1),
  dalam set terpantau 54 entitas (35 Tier C + 1 promosi). Daftar lama 23 alamat TIDAK dipakai.
  Frekuensi kini 4 jam (amendemen 2026-11-06 ~07:49 WIB); JANGAN login GMGN.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only halaman GMGN BSC wallet 1
  (https://gmgn.ai/bsc/address/0x13d1e9a96eba7906e1ede348c9bb604a03e46d02).
- Hasil: LOGIN-GATED pada 19:53 WIB — GMGN hanya menampilkan homepage dengan panel
  "You are not logged in to GMGN" dan tombol "Log in"; tanpa saldo BNB, tanpa tab Holdings,
  tanpa tab Activity, tanpa baris Buy/Sell/Tx In. Tombol Log in/Sign Up tidak diklik.
  Retry setelah ~30 detik + percobaan ulang di tab baru pada 19:54 WIB tetap LOGIN-GATED.
  Sesuai instruksi, pemeriksaan dihentikan di titik ini; wallet 2–54 TIDAK dibuka.
- TIDAK ADA pembelian baru yang terverifikasi dari run ini. TIDAK ADA SINYAL yang diklaim
  (ambang: minimal 14 entitas berbeda membeli token baru yang sama) — bukan karena wallet
  terbukti tidak membeli, melainkan karena tidak satu pun halaman terbaca. Wallet yang tidak
  terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
- TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang
  terverifikasi — tidak ada data Activity yang terlihat). Cluster flags run 49
  (micro-bot 16/17/19/20/21, GrokBot 23–48+50) tidak dapat diverifikasi ulang run ini,
  dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap BELUM
  terverifikasi dan belum terselesaikan; field BNB/holdings tidak diubah.
- Gating bersifat session-level, bukan per-wallet: sudah gated sejak wallet pertama, sama
  seperti run 51–54; kuota tampilan anonim belum reset sejak run 50 (~14,5 jam sebelumnya),
  walau jeda sejak run 54 sudah ~4 jam. Tidak ada login yang dicoba, sesuai aturan read-only.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-06T19:54:00+07:00;
  run55_summary ditambahkan ke ke-54 wallet; baseline/holdings tidak diubah).
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap
  persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal
  login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 56 — 2026-11-06 23:53–23:57 WIB (INCOMPLETE, login-gated; sama seperti run 51–55)

- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat inti (Tier A privat 13 + Tier B privat 1),
  dalam set terpantau 54 entitas (35 Tier C + 1 promosi). Daftar lama 23 alamat TIDAK dipakai.
  Frekuensi kini 4 jam (amendemen 2026-11-06 ~07:49 WIB); JANGAN login GMGN.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only halaman GMGN BSC wallet 1
  (https://gmgn.ai/bsc/address/0x13d1e9a96eba7906e1ede348c9bb604a03e46d02).
- Hasil: LOGIN-GATED pada 23:56 WIB — GMGN hanya menampilkan homepage dengan panel
  "You are not logged in to GMGN" dan tombol "Log in"; tanpa saldo BNB, tanpa tab Holdings,
  tanpa tab Activity, tanpa baris Buy/Sell/Tx In. Tombol Log in/Sign Up tidak diklik.
  Retry setelah ~30 detik + percobaan ulang di tab baru pada 23:57 WIB tetap LOGIN-GATED.
  Sesuai instruksi, pemeriksaan dihentikan di titik ini; wallet 2–54 TIDAK dibuka.
- TIDAK ADA pembelian baru yang terverifikasi dari run ini. TIDAK ADA SINYAL yang diklaim
  (ambang: minimal 14 entitas berbeda membeli token baru yang sama) — bukan karena wallet
  terbukti tidak membeli, melainkan karena tidak satu pun halaman terbaca. Wallet yang tidak
  terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
- TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang
  terverifikasi — tidak ada data Activity yang terlihat). Cluster flags run 49
  (micro-bot 16/17/19/20/21, GrokBot 23–48+50) tidak dapat diverifikasi ulang run ini,
  dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap BELUM
  terverifikasi dan belum terselesaikan; field BNB/holdings tidak diubah.
- Gating bersifat session-level, bukan per-wallet: sudah gated sejak wallet pertama, sama
  seperti run 51–55; kuota tampilan anonim belum reset sejak run 50 (~18,5 jam sebelumnya),
  walau jeda sejak run 55 sudah ~4 jam. Tidak ada login yang dicoba, sesuai aturan read-only.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-06T23:57:00+07:00;
  run56_summary ditambahkan ke ke-54 wallet; baseline/holdings tidak diubah).
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap
  persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal
  login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 57 — 2026-11-07 03:53–03:54 WIB (INCOMPLETE, login-gated; sama seperti run 51–56)

- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat inti (Tier A privat 13 + Tier B privat 1),
  dalam set terpantau 54 entitas (35 Tier C + 1 promosi). Daftar lama 23 alamat TIDAK dipakai.
  Frekuensi kini 4 jam (amendemen 2026-11-06 ~07:49 WIB); JANGAN login GMGN.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only halaman GMGN BSC wallet 1
  (https://gmgn.ai/bsc/address/0x13d1e9a96eba7906e1ede348c9bb604a03e46d02).
- Hasil: LOGIN-GATED pada 03:53 WIB — GMGN hanya menampilkan homepage dengan panel
  "You are not logged in to GMGN" dan tombol "Log in"; tanpa saldo BNB, tanpa tab Holdings,
  tanpa tab Activity, tanpa baris Buy/Sell/Tx In. Tombol Log in/Sign Up tidak diklik.
  Retry setelah ~30 detik + percobaan ulang di tab baru pada 03:54 WIB tetap LOGIN-GATED.
  Sesuai instruksi, pemeriksaan dihentikan di titik ini; wallet 2–54 TIDAK dibuka.
- TIDAK ADA pembelian baru yang terverifikasi dari run ini. TIDAK ADA SINYAL yang diklaim
  (ambang: minimal 14 entitas berbeda membeli token baru yang sama) — bukan karena wallet
  terbukti tidak membeli, melainkan karena tidak satu pun halaman terbaca. Wallet yang tidak
  terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
- TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang
  terverifikasi — tidak ada data Activity yang terlihat). Cluster flags run 49
  (micro-bot 16/17/19/20/21, GrokBot 23–48+50) tidak dapat diverifikasi ulang run ini,
  dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap BELUM
  terverifikasi dan belum terselesaikan; field BNB/holdings tidak diubah.
- Gating bersifat session-level, bukan per-wallet: sudah gated sejak wallet pertama, sama
  seperti run 51–56; kuota tampilan anonim belum reset sejak run 50 (~22,5 jam sebelumnya),
  walau jeda sejak run 56 sudah ~4 jam. Tidak ada login yang dicoba, sesuai aturan read-only.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-07T03:54:00+07:00;
  run57_summary ditambahkan ke ke-54 wallet; baseline/holdings tidak diubah).
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap
  persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal
  login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 58 — 2026-11-07 07:54–07:55 WIB (INCOMPLETE, login-gated; sama seperti run 51–57)

- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat inti (Tier A privat 13 + Tier B privat 1),
  dalam set terpantau 54 entitas (35 Tier C + 1 promosi). Daftar lama 23 alamat TIDAK dipakai.
  Frekuensi kini 4 jam (amendemen 2026-11-06 ~07:49 WIB); JANGAN login GMGN.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only halaman GMGN BSC wallet 1
  (https://gmgn.ai/bsc/address/0x13d1e9a96eba7906e1ede348c9bb604a03e46d02).
- Hasil: LOGIN-GATED pada 07:54 WIB — GMGN hanya menampilkan homepage dengan panel
  "You are not logged in to GMGN" dan tombol "Log in"; tanpa saldo BNB, tanpa tab Holdings,
  tanpa tab Activity, tanpa baris Buy/Sell/Tx In. Tombol Log in/Sign Up tidak diklik.
  Retry setelah ~30 detik + percobaan ulang di tab baru pada 07:55 WIB tetap LOGIN-GATED.
  Sesuai instruksi, pemeriksaan dihentikan di titik ini; wallet 2–54 TIDAK dibuka.
- TIDAK ADA pembelian baru yang terverifikasi dari run ini. TIDAK ADA SINYAL yang diklaim
  (ambang: minimal 14 entitas berbeda membeli token baru yang sama) — bukan karena wallet
  terbukti tidak membeli, melainkan karena tidak satu pun halaman terbaca. Wallet yang tidak
  terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
- TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang
  terverifikasi — tidak ada data Activity yang terlihat). Cluster flags run 49
  (micro-bot 16/17/19/20/21, GrokBot 23–48+50) tidak dapat diverifikasi ulang run ini,
  dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap BELUM
  terverifikasi dan belum terselesaikan; field BNB/holdings tidak diubah.
- Gating bersifat session-level, bukan per-wallet: sudah gated sejak wallet pertama, sama
  seperti run 51–57; kuota tampilan anonim belum reset sejak run 50 (~26,5 jam sebelumnya),
  walau jeda sejak run 57 sudah ~4 jam. Tidak ada login yang dicoba, sesuai aturan read-only.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-07T07:55:00+07:00;
  run58_summary ditambahkan ke ke-54 wallet; baseline/holdings tidak diubah).
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap
  persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal
  login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 59 — 2026-11-07 11:53–11:54 WIB (INCOMPLETE, login-gated; sama seperti run 51–58)

- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat inti (Tier A privat 13 + Tier B privat 1),
  dalam set terpantau 54 entitas (35 Tier C + 1 promosi). Daftar lama 23 alamat TIDAK dipakai.
  Frekuensi kini 4 jam (amendemen 2026-11-06 ~07:49 WIB); JANGAN login GMGN.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only halaman GMGN BSC wallet 1
  (https://gmgn.ai/bsc/address/0x13d1e9a96eba7906e1ede348c9bb604a03e46d02).
- Hasil: LOGIN-GATED pada 11:53 WIB — GMGN hanya menampilkan homepage dengan panel
  "You are not logged in to GMGN" dan tombol "Log in"; tanpa saldo BNB, tanpa tab Holdings,
  tanpa tab Activity, tanpa baris Buy/Sell/Tx In. Tombol Log in/Sign Up tidak diklik.
  Retry setelah ~30 detik + percobaan ulang di tab baru pada 11:54 WIB tetap LOGIN-GATED.
  Sesuai instruksi, pemeriksaan dihentikan di titik ini; wallet 2–54 TIDAK dibuka.
- TIDAK ADA pembelian baru yang terverifikasi dari run ini. TIDAK ADA SINYAL yang diklaim
  (ambang: minimal 14 entitas berbeda membeli token baru yang sama) — bukan karena wallet
  terbukti tidak membeli, melainkan karena tidak satu pun halaman terbaca. Wallet yang tidak
  terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
- TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang
  terverifikasi — tidak ada data Activity yang terlihat). Cluster flags run 49
  (micro-bot 16/17/19/20/21, GrokBot 23–48+50) tidak dapat diverifikasi ulang run ini,
  dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap BELUM
  terverifikasi dan belum terselesaikan; field BNB/holdings tidak diubah.
- Gating bersifat session-level, bukan per-wallet: sudah gated sejak wallet pertama, sama
  seperti run 51–58; kuota tampilan anonim belum reset sejak run 50 (~30,5 jam sebelumnya),
  walau jeda sejak run 58 sudah ~4 jam. Tidak ada login yang dicoba, sesuai aturan read-only.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-07T11:54:00+07:00;
  run59_summary ditambahkan ke ke-54 wallet; baseline/holdings tidak diubah).
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap
  persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal
  login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 60 — 2026-11-07 15:53-15:54 WIB (browser task harness-measured 15:53-15:54 WIB)
- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat inti (Tier A privat 13 + Tier B privat 1),
  dalam set terpantau 54 entitas (35 Tier C + 1 promosi). Daftar lama 23 alamat TIDAK dipakai.
  Frekuensi kini 4 jam (amendemen 2026-11-06 ~07:49 WIB); JANGAN login GMGN.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only halaman GMGN BSC wallet 1
  (https://gmgn.ai/bsc/address/0x13d1e9a96eba7906e1ede348c9bb604a03e46d02).
- Hasil: LOGIN-GATED pada 15:53 WIB — GMGN hanya menampilkan homepage dengan panel
  "You are not logged in to GMGN" dan tombol "Log in"; tanpa saldo BNB, tanpa tab Holdings,
  tanpa tab Activity, tanpa baris Buy/Sell/Tx In. Tombol Log in/Sign Up tidak diklik.
  Retry setelah ~30 detik + percobaan ulang di tab baru pada 15:54 WIB tetap LOGIN-GATED.
  Sesuai instruksi, pemeriksaan dihentikan di titik ini; wallet 2–54 TIDAK dibuka.
- TIDAK ADA pembelian baru yang terverifikasi dari run ini. TIDAK ADA SINYAL yang diklaim
  (ambang: minimal 14 entitas berbeda membeli token baru yang sama) — bukan karena wallet
  terbukti tidak membeli, melainkan karena tidak satu pun halaman terbaca. Wallet yang tidak
  terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
- TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang
  terverifikasi — tidak ada data Activity yang terlihat). Cluster flags run 49
  (micro-bot 16/17/19/20/21, GrokBot 23–48+50) tidak dapat diverifikasi ulang run ini,
  dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap BELUM
  terverifikasi dan belum terselesaikan; field BNB/holdings tidak diubah.
- Gating bersifat session-level, bukan per-wallet: sudah gated sejak wallet pertama, sama
  seperti run 51–59; kuota tampilan anonim belum reset sejak run 50 (~34,5 jam sebelumnya),
  walau jeda sejak run 59 sudah ~4 jam. Tidak ada login yang dicoba, sesuai aturan read-only.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-07T15:54:00+07:00;
  run60_summary ditambahkan ke ke-54 wallet; baseline/holdings tidak diubah).
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap
  persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal
  login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 61 — 2026-11-07 19:53-19:54 WIB (browser task harness-measured 19:53-19:54 WIB)
- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat inti (Tier A privat 13 + Tier B privat 1),
  dalam set terpantau 54 entitas (35 Tier C + 1 promosi). Daftar lama 23 alamat TIDAK dipakai.
  Frekuensi kini 4 jam (amendemen 2026-11-06 ~07:49 WIB); JANGAN login GMGN.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only halaman GMGN BSC wallet 1
  (https://gmgn.ai/bsc/address/0x13d1e9a96eba7906e1ede348c9bb604a03e46d02).
- Hasil: LOGIN-GATED pada 19:53 WIB — GMGN hanya menampilkan homepage dengan panel
  "You are not logged in to GMGN" dan tombol "Log in"; tanpa saldo BNB, tanpa tab Holdings,
  tanpa tab Activity, tanpa baris Buy/Sell/Tx In. Tombol Log in/Sign Up tidak diklik.
  Retry setelah ~30 detik + percobaan ulang di tab baru pada 19:54 WIB tetap LOGIN-GATED.
  Sesuai instruksi, pemeriksaan dihentikan di titik ini; wallet 2–54 TIDAK dibuka.
- TIDAK ADA pembelian baru yang terverifikasi dari run ini. TIDAK ADA SINYAL yang diklaim
  (ambang: minimal 14 entitas berbeda membeli token baru yang sama) — bukan karena wallet
  terbukti tidak membeli, melainkan karena tidak satu pun halaman terbaca. Wallet yang tidak
  terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
- TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang
  terverifikasi — tidak ada data Activity yang terlihat). Cluster flags run 49
  (micro-bot 16/17/19/20/21, GrokBot 23–48+50) tidak dapat diverifikasi ulang run ini,
  dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap BELUM
  terverifikasi dan belum terselesaikan; field BNB/holdings tidak diubah.
- Gating bersifat session-level, bukan per-wallet: sudah gated sejak wallet pertama, sama
  seperti run 51–60; kuota tampilan anonim belum reset sejak run 50 (~38,5 jam sebelumnya),
  walau jeda sejak run 60 sudah ~4 jam. Tidak ada login yang dicoba, sesuai aturan read-only.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-07T19:54:00+07:00;
  run61_summary ditambahkan ke entri wallet 1 dan wallet 2; baseline/holdings tidak diubah).
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap
  persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal
  login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 62 — 2026-11-07 23:53-23:54 WIB (browser task harness-measured 23:53-23:54 WIB)
- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat inti (Tier A privat 13 + Tier B privat 1),
  dalam set terpantau 54 entitas (35 Tier C + 1 promosi). Daftar lama 23 alamat TIDAK dipakai.
  Frekuensi kini 4 jam (amendemen 2026-11-06 ~07:49 WIB); JANGAN login GMGN.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only halaman GMGN BSC wallet 1
  (https://gmgn.ai/bsc/address/0x13d1e9a96eba7906e1ede348c9bb604a03e46d02).
- Hasil: LOGIN-GATED pada 23:53 WIB — GMGN hanya menampilkan homepage dengan panel
  "You are not logged in to GMGN" dan tombol "Log in"; tanpa saldo BNB, tanpa tab Holdings,
  tanpa tab Activity, tanpa baris Buy/Sell/Tx In. Tombol Log in/Sign Up tidak diklik.
  Retry setelah ~30 detik + percobaan ulang di tab baru pada 23:54 WIB tetap LOGIN-GATED.
  Sesuai instruksi, pemeriksaan dihentikan di titik ini; wallet 2–54 TIDAK dibuka.
- TIDAK ADA pembelian baru yang terverifikasi dari run ini. TIDAK ADA SINYAL yang diklaim
  (ambang: minimal 14 entitas berbeda membeli token baru yang sama) — bukan karena wallet
  terbukti tidak membeli, melainkan karena tidak satu pun halaman terbaca. Wallet yang tidak
  terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
- TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang
  terverifikasi — tidak ada data Activity yang terlihat). Cluster flags run 49
  (micro-bot 16/17/19/20/21, GrokBot 23–48+50) tidak dapat diverifikasi ulang run ini,
  dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap BELUM
  terverifikasi dan belum terselesaikan; field BNB/holdings tidak diubah.
- Gating bersifat session-level, bukan per-wallet: sudah gated sejak wallet pertama, sama
  seperti run 51–61; kuota tampilan anonim belum reset sejak run 50 (~42,5 jam sebelumnya),
  walau jeda sejak run 61 sudah ~4 jam. Tidak ada login yang dicoba, sesuai aturan read-only.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-07T23:54:00+07:00;
  run62_summary ditambahkan ke entri wallet 1 dan wallet 2; baseline/holdings tidak diubah).
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap
  persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal
  login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 63 — 2026-11-08 03:53-03:54 WIB (browser task harness-measured 03:53-03:54 WIB)
- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat inti (Tier A privat 13 + Tier B privat 1),
  dalam set terpantau 54 entitas (35 Tier C + 1 promosi). Daftar lama 23 alamat TIDAK dipakai.
  Frekuensi kini 4 jam (amendemen 2026-11-06 ~07:49 WIB); JANGAN login GMGN.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only halaman GMGN BSC wallet 1
  (https://gmgn.ai/bsc/address/0x13d1e9a96eba7906e1ede348c9bb604a03e46d02).
- Hasil: LOGIN-GATED pada 03:53 WIB — GMGN hanya menampilkan homepage dengan panel
  "You are not logged in to GMGN" dan tombol "Log in"; tanpa saldo BNB, tanpa tab Holdings,
  tanpa tab Activity, tanpa baris Buy/Sell/Tx In. Tombol Log in/Sign Up tidak diklik.
  Retry setelah ~30 detik + percobaan ulang di tab baru pada 03:54 WIB tetap LOGIN-GATED.
  Sesuai instruksi, pemeriksaan dihentikan di titik ini; wallet 2–54 TIDAK dibuka.
- TIDAK ADA pembelian baru yang terverifikasi dari run ini. TIDAK ADA SINYAL yang diklaim
  (ambang: minimal 14 entitas berbeda membeli token baru yang sama) — bukan karena wallet
  terbukti tidak membeli, melainkan karena tidak satu pun halaman terbaca. Wallet yang tidak
  terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
- TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang
  terverifikasi — tidak ada data Activity yang terlihat). Cluster flags run 49
  (micro-bot 16/17/19/20/21, GrokBot 23–48+50) tidak dapat diverifikasi ulang run ini,
  dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap BELUM
  terverifikasi dan belum terselesaikan; field BNB/holdings tidak diubah.
- Gating bersifat session-level, bukan per-wallet: sudah gated sejak wallet pertama, sama
  seperti run 51–62; kuota tampilan anonim belum reset sejak run 50 (~46,5 jam sebelumnya),
  walau jeda sejak run 62 sudah ~4 jam. Tidak ada login yang dicoba, sesuai aturan read-only.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-08T03:54:00+07:00;
  run63_summary ditambahkan ke entri wallet 1 dan wallet 2; baseline/holdings tidak diubah).
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap
  persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal
  login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 64 — 2026-11-08 07:53-07:54 WIB (browser task harness-measured 07:53-07:54 WIB)
- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat inti (Tier A privat 13 + Tier B privat 1),
  dalam set terpantau 54 entitas (35 Tier C + 1 promosi). Daftar lama 23 alamat TIDAK dipakai.
  Frekuensi kini 4 jam (amendemen 2026-11-06 ~07:49 WIB); JANGAN login GMGN.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only halaman GMGN BSC wallet 1
  (https://gmgn.ai/bsc/address/0x13d1e9a96eba7906e1ede348c9bb604a03e46d02).
- Hasil: LOGIN-GATED pada 07:53 WIB — GMGN hanya menampilkan homepage dengan panel
  "You are not logged in to GMGN" dan tombol "Log in"; tanpa saldo BNB, tanpa tab Holdings,
  tanpa tab Activity, tanpa baris Buy/Sell/Tx In. Tombol Log in/Sign Up tidak diklik.
  Retry setelah ~30 detik + percobaan ulang di tab baru pada 07:54 WIB tetap LOGIN-GATED.
  Sesuai instruksi, pemeriksaan dihentikan di titik ini; wallet 2–54 TIDAK dibuka.
- TIDAK ADA pembelian baru yang terverifikasi dari run ini. TIDAK ADA SINYAL yang diklaim
  (ambang: minimal 14 entitas berbeda membeli token baru yang sama) — bukan karena wallet
  terbukti tidak membeli, melainkan karena tidak satu pun halaman terbaca. Wallet yang tidak
  terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
- TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang
  terverifikasi — tidak ada data Activity yang terlihat). Cluster flags run 49
  (micro-bot 16/17/19/20/21, GrokBot 23–48+50) tidak dapat diverifikasi ulang run ini,
  dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap BELUM
  terverifikasi dan belum terselesaikan; field BNB/holdings tidak diubah.
- Gating bersifat session-level, bukan per-wallet: sudah gated sejak wallet pertama, sama
  seperti run 51–63; kuota tampilan anonim belum reset sejak run 50 (~50,5 jam sebelumnya),
  walau jeda sejak run 63 sudah ~4 jam. Tidak ada login yang dicoba, sesuai aturan read-only.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-08T07:54:00+07:00;
  run64_summary ditambahkan ke entri wallet 1 dan wallet 2; baseline/holdings tidak diubah).
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap
  persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal
  login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 65 — 2026-11-08 11:53-11:54 WIB (browser task harness-measured 11:53-11:54 WIB)
- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat inti (Tier A privat 13 + Tier B privat 1),
  dalam set terpantau 54 entitas (35 Tier C + 1 promosi). Daftar lama 23 alamat TIDAK dipakai.
  Frekuensi kini 4 jam (amendemen 2026-11-06 ~07:49 WIB); JANGAN login GMGN.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only halaman GMGN BSC wallet 1
  (https://gmgn.ai/bsc/address/0x13d1e9a96eba7906e1ede348c9bb604a03e46d02).
- Hasil: LOGIN-GATED pada 11:53 WIB — GMGN hanya menampilkan homepage dengan panel
  "You are not logged in to GMGN" dan tombol "Log in"; tanpa saldo BNB, tanpa tab Holdings,
  tanpa tab Activity, tanpa baris Buy/Sell/Tx In. Tombol Log in/Sign Up tidak diklik.
  Retry setelah ~30 detik + percobaan ulang di tab baru pada 11:54 WIB tetap LOGIN-GATED.
  Sesuai instruksi, pemeriksaan dihentikan di titik ini; wallet 2–54 TIDAK dibuka.
- TIDAK ADA pembelian baru yang terverifikasi dari run ini. TIDAK ADA SINYAL yang diklaim
  (ambang: minimal 14 entitas berbeda membeli token baru yang sama) — bukan karena wallet
  terbukti tidak membeli, melainkan karena tidak satu pun halaman terbaca. Wallet yang tidak
  terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
- TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang
  terverifikasi — tidak ada data Activity yang terlihat). Cluster flags run 49
  (micro-bot 16/17/19/20/21, GrokBot 23–48+50) tidak dapat diverifikasi ulang run ini,
  dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap BELUM
  terverifikasi dan belum terselesaikan; field BNB/holdings tidak diubah.
- Gating bersifat session-level, bukan per-wallet: sudah gated sejak wallet pertama, sama
  seperti run 51–64; kuota tampilan anonim belum reset sejak run 50 (~54,5 jam sebelumnya),
  walau jeda sejak run 64 sudah ~4 jam. Tidak ada login yang dicoba, sesuai aturan read-only.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-08T11:54:00+07:00;
  run65_summary ditambahkan ke entri wallet 1 dan wallet 2; baseline/holdings tidak diubah).
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap
  persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal
  login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 66 — 2026-11-08 15:53-15:54 WIB (browser task harness-measured 15:53-15:54 WIB)
- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat inti (Tier A privat 13 + Tier B privat 1),
  dalam set terpantau 54 entitas (35 Tier C + 1 promosi). Daftar lama 23 alamat TIDAK dipakai.
  Frekuensi kini 4 jam (amendemen 2026-11-06 ~07:49 WIB); JANGAN login GMGN.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only halaman GMGN BSC wallet 1
  (https://gmgn.ai/bsc/address/0x13d1e9a96eba7906e1ede348c9bb604a03e46d02).
- Hasil: LOGIN-GATED pada 15:53 WIB — GMGN hanya menampilkan homepage dengan panel
  "You are not logged in to GMGN" dan tombol "Log in"; tanpa saldo BNB, tanpa tab Holdings,
  tanpa tab Activity, tanpa baris Buy/Sell/Tx In. Tombol Log in/Sign Up tidak diklik.
  Retry setelah ~30 detik + percobaan ulang di tab baru pada 15:54 WIB tetap LOGIN-GATED.
  Sesuai instruksi, pemeriksaan dihentikan di titik ini; wallet 2–54 TIDAK dibuka.
- TIDAK ADA pembelian baru yang terverifikasi dari run ini. TIDAK ADA SINYAL yang diklaim
  (ambang: minimal 14 entitas berbeda membeli token baru yang sama) — bukan karena wallet
  terbukti tidak membeli, melainkan karena tidak satu pun halaman terbaca. Wallet yang tidak
  terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
- TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang
  terverifikasi — tidak ada data Activity yang terlihat). Cluster flags run 49
  (micro-bot 16/17/19/20/21, GrokBot 23–48+50) tidak dapat diverifikasi ulang run ini,
  dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap BELUM
  terverifikasi dan belum terselesaikan; field BNB/holdings tidak diubah.
- Gating bersifat session-level, bukan per-wallet: sudah gated sejak wallet pertama, sama
  seperti run 51–65; kuota tampilan anonim belum reset sejak run 50 (~58,5 jam sebelumnya),
  walau jeda sejak run 65 sudah ~4 jam. Tidak ada login yang dicoba, sesuai aturan read-only.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-08T15:54:00+07:00;
  run66_summary ditambahkan ke entri wallet 1 dan wallet 2; baseline/holdings tidak diubah).
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap
  persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal
  login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 67 — 2026-11-08 19:53-19:54 WIB (browser task harness-measured 19:53-19:54 WIB)
- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat inti (Tier A privat 13 + Tier B privat 1),
  dalam set terpantau 54 entitas (35 Tier C + 1 promosi). Daftar lama 23 alamat TIDAK dipakai.
  Frekuensi kini 4 jam (amendemen 2026-11-06 ~07:49 WIB); JANGAN login GMGN.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only halaman GMGN BSC wallet 1
  (https://gmgn.ai/bsc/address/0x13d1e9a96eba7906e1ede348c9bb604a03e46d02).
- Hasil: LOGIN-GATED pada 19:53 WIB — GMGN hanya menampilkan homepage dengan panel
  "You are not logged in to GMGN" dan tombol "Log in"; tanpa saldo BNB, tanpa tab Holdings,
  tanpa tab Activity, tanpa baris Buy/Sell/Tx In. Tombol Log in/Sign Up tidak diklik.
  Retry setelah ~30 detik + percobaan ulang di tab baru pada 19:54 WIB tetap LOGIN-GATED.
  Sesuai instruksi, pemeriksaan dihentikan di titik ini; wallet 2–54 TIDAK dibuka.
- TIDAK ADA pembelian baru yang terverifikasi dari run ini. TIDAK ADA SINYAL yang diklaim
  (ambang: minimal 14 entitas berbeda membeli token baru yang sama) — bukan karena wallet
  terbukti tidak membeli, melainkan karena tidak satu pun halaman terbaca. Wallet yang tidak
  terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
- TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang
  terverifikasi — tidak ada data Activity yang terlihat). Cluster flags run 49
  (micro-bot 16/17/19/20/21, GrokBot 23–48+50) tidak dapat diverifikasi ulang run ini,
  dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap BELUM
  terverifikasi dan belum terselesaikan; field BNB/holdings tidak diubah.
- Gating bersifat session-level, bukan per-wallet: sudah gated sejak wallet pertama, sama
  seperti run 51–66; kuota tampilan anonim belum reset sejak run 50 (~62,5 jam sebelumnya),
  walau jeda sejak run 66 sudah ~4 jam. Tidak ada login yang dicoba, sesuai aturan read-only.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-08T19:54:00+07:00;
  run67_summary ditambahkan ke ke-54 entri wallet; baseline/holdings tidak diubah).
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap
  persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal
  login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 68 — 2026-11-08 23:53-23:54 WIB (browser task harness-measured 23:53-23:54 WIB)
- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat inti (Tier A privat 13 + Tier B privat 1),
  dalam set terpantau 54 entitas (35 Tier C + 1 promosi). Daftar lama 23 alamat TIDAK dipakai.
  Frekuensi kini 4 jam (amendemen 2026-11-06 ~07:49 WIB); JANGAN login GMGN.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only halaman GMGN BSC wallet 1
  (https://gmgn.ai/bsc/address/0x13d1e9a96eba7906e1ede348c9bb604a03e46d02).
- Hasil: LOGIN-GATED pada 23:53 WIB — GMGN hanya menampilkan homepage dengan panel
  "You are not logged in to GMGN" dan tombol "Log in"; tanpa saldo BNB, tanpa tab Holdings,
  tanpa tab Activity, tanpa baris Buy/Sell/Tx In. Tombol Log in/Sign Up tidak diklik.
  Retry setelah ~30 detik + percobaan ulang di tab baru pada 23:54 WIB tetap LOGIN-GATED.
  Sesuai instruksi, pemeriksaan dihentikan di titik ini; wallet 2–54 TIDAK dibuka.
- TIDAK ADA pembelian baru yang terverifikasi dari run ini. TIDAK ADA SINYAL yang diklaim
  (ambang: minimal 14 entitas berbeda membeli token baru yang sama) — bukan karena wallet
  terbukti tidak membeli, melainkan karena tidak satu pun halaman terbaca. Wallet yang tidak
  terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
- TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang
  terverifikasi — tidak ada data Activity yang terlihat). Cluster flags run 49
  (micro-bot 16/17/19/20/21, GrokBot 23–48+50) tidak dapat diverifikasi ulang run ini,
  dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap BELUM
  terverifikasi dan belum terselesaikan; field BNB/holdings tidak diubah.
- Gating bersifat session-level, bukan per-wallet: sudah gated sejak wallet pertama, sama
  seperti run 51–67; kuota tampilan anonim belum reset sejak run 50 (~66,5 jam sebelumnya),
  walau jeda sejak run 67 sudah ~4 jam. Tidak ada login yang dicoba, sesuai aturan read-only.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-08T23:54:00+07:00;
  run68_summary ditambahkan ke ke-54 entri wallet; baseline/holdings tidak diubah).
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap
  persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal
  login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
## Run 69 — 2026-11-09 03:53-03:54 WIB (browser task harness-measured 03:53-03:54 WIB)
- Daftar dibaca dari `tier-ab-watch.md`: 14 EOA privat inti (Tier A privat 13 + Tier B privat 1),
  dalam set terpantau 54 entitas (35 Tier C + 1 promosi). Daftar lama 23 alamat TIDAK dipakai.
  Frekuensi kini 4 jam (amendemen 2026-11-06 ~07:49 WIB); JANGAN login GMGN.
- Metode: baca-saja, tanpa login, tanpa connect wallet, tanpa sign, tanpa beli/jual/follow.
  Pemeriksaan browser live read-only halaman GMGN BSC wallet 1
  (https://gmgn.ai/bsc/address/0x13d1e9a96eba7906e1ede348c9bb604a03e46d02).
- Hasil: LOGIN-GATED pada 03:53 WIB — GMGN hanya menampilkan homepage dengan panel
  "You are not logged in to GMGN" dan tombol "Log in"; tanpa saldo BNB, tanpa tab Holdings,
  tanpa tab Activity, tanpa baris Buy/Sell/Tx In. Tombol Log in/Sign Up tidak diklik.
  Retry setelah ~30 detik + percobaan ulang di tab baru pada 03:54 WIB tetap LOGIN-GATED.
  Sesuai instruksi, pemeriksaan dihentikan di titik ini; wallet 2–54 TIDAK dibuka.
- TIDAK ADA pembelian baru yang terverifikasi dari run ini. TIDAK ADA SINYAL yang diklaim
  (ambang: minimal 14 entitas berbeda membeli token baru yang sama) — bukan karena wallet
  terbukti tidak membeli, melainkan karena tidak satu pun halaman terbaca. Wallet yang tidak
  terbaca datanya TIDAK dianggap tidak membeli, sesuai aturan run.
- TIDAK ADA runtuhan entitas baru yang dicatat (tidak ada keterkaitan KUAT baru yang
  terverifikasi — tidak ada data Activity yang terlihat). Cluster flags run 49
  (micro-bot 16/17/19/20/21, GrokBot 23–48+50) tidak dapat diverifikasi ulang run ini,
  dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap BELUM
  terverifikasi dan belum terselesaikan; field BNB/holdings tidak diubah.
- Gating bersifat session-level, bukan per-wallet: sudah gated sejak wallet pertama, sama
  seperti run 51–68; kuota tampilan anonim belum reset sejak run 50 (~70,5 jam sebelumnya),
  walau jeda sejak run 68 sudah ~4 jam. Tidak ada login yang dicoba, sesuai aturan read-only.
- State diperbarui di `tier-ab-watch-state.json` (last_checked 2026-11-09T03:54:00+07:00;
  run69_summary ditambahkan ke ke-54 entri wallet; baseline/holdings tidak diubah).
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap
  persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal
  login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 70 — 2026-11-09 07:53-07:55 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 07:54 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 07:55 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-69; kuota tampilan anonim belum reset sejak run 50 (~74,5 jam lalu), meski jarak ~4 jam sejak run 69 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 71 — 2026-11-09 11:53-11:54 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 11:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 11:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-70; kuota tampilan anonim belum reset sejak run 50 (~78,5 jam lalu), meski jarak ~4 jam sejak run 70 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 72 — 2026-11-09 15:54-15:55 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 15:54 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 15:55 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-71; kuota tampilan anonim belum reset sejak run 50 (~82,5 jam lalu), meski jarak ~4 jam sejak run 71 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 73 — 2026-11-09 19:53-19:54 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 19:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 19:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-72; kuota tampilan anonim belum reset sejak run 50 (~86,5 jam lalu), meski jarak ~4 jam sejak run 72 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 74 — 2026-11-09 23:53-23:54 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 23:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 23:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-73; kuota tampilan anonim belum reset sejak run 50 (~90,5 jam lalu), meski jarak ~4 jam sejak run 73 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 75 — 2026-11-10 03:54-03:55 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 03:54 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 03:55 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-74; kuota tampilan anonim belum reset sejak run 50 (~94,5 jam lalu), meski jarak ~4 jam sejak run 74 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
## Run 76 — 2026-11-10 07:53-07:54 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 07:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 07:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-75; kuota tampilan anonim belum reset sejak run 50 (~98,5 jam lalu), meski jarak ~4 jam sejak run 75 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 77 — 2026-11-10 11:53-11:54 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 11:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 11:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-76; kuota tampilan anonim belum reset sejak run 50 (~102,5 jam lalu), meski jarak ~4 jam sejak run 76 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 78 — 2026-11-10 15:53-15:54 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 15:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 15:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-77; kuota tampilan anonim belum reset sejak run 50 (~106,5 jam lalu), meski jarak ~4 jam sejak run 77 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 79 — 2026-11-10 19:53-19:55 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 19:54 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 19:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-78; kuota tampilan anonim belum reset sejak run 50 (~110,5 jam lalu), meski jarak ~4 jam sejak run 78 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 80 — 2026-11-10 23:53-23:54 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 23:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 23:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-79; kuota tampilan anonim belum reset sejak run 50 (~114,5 jam lalu), meski jarak ~4 jam sejak run 79 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 81 — 2026-11-11 03:53-03:54 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 03:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 03:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-80; kuota tampilan anonim belum reset sejak run 50 (~118,5 jam lalu), meski jarak ~4 jam sejak run 80 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 82 — 2026-11-11 07:53-07:54 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 07:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 07:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-81; kuota tampilan anonim belum reset sejak run 50 (~122,5 jam lalu), meski jarak ~4 jam sejak run 81 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 83 — 2026-11-11 11:53-11:54 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 11:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 11:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-82; kuota tampilan anonim belum reset sejak run 50 (~126,5 jam lalu), meski jarak ~4 jam sejak run 82 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 84 — 2026-11-11 15:53-15:54 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 15:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 15:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-83; kuota tampilan anonim belum reset sejak run 50 (~130,5 jam lalu), meski jarak ~4 jam sejak run 83 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 85 — 2026-11-11 19:53-19:54 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 19:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 19:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-84; kuota tampilan anonim belum reset sejak run 50 (~134,5 jam lalu), meski jarak ~4 jam sejak run 84 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 86 — 2026-11-11 23:53-23:55 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 23:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 23:55 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-85; kuota tampilan anonim belum reset sejak run 50 (~138,5 jam lalu), meski jarak ~4 jam sejak run 85 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 87 — 2026-11-12 03:53-03:54 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 03:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 03:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-86; kuota tampilan anonim belum reset sejak run 50 (~142,5 jam lalu), meski jarak ~4 jam sejak run 86 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 88 — 2026-11-12 07:53-07:54 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 07:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 07:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-87; kuota tampilan anonim belum reset sejak run 50 (~146,5 jam lalu), meski jarak ~4 jam sejak run 87 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 89 — 2026-11-12 11:53-11:54 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 11:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 11:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-88; kuota tampilan anonim belum reset sejak run 50 (~150,5 jam lalu), meski jarak ~4 jam sejak run 88 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 90 — 2026-11-12 15:53-15:54 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 15:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 15:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-89; kuota tampilan anonim belum reset sejak run 50 (~154,5 jam lalu), meski jarak ~4 jam sejak run 89 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 91 — 2026-11-12 19:53-19:54 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 19:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 19:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-90; kuota tampilan anonim belum reset sejak run 50 (~158,5 jam lalu), meski jarak ~4 jam sejak run 90 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 92 — 2026-11-12 23:53-23:55 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 23:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 23:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-91; kuota tampilan anonim belum reset sejak run 50 (~162,5 jam lalu), meski jarak ~4 jam sejak run 91 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 93 — 2026-11-13 03:53-03:55 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 03:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 03:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-92; kuota tampilan anonim belum reset sejak run 50 (~166,5 jam lalu), meski jarak ~4 jam sejak run 92 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 94 — 2026-11-13 07:53-07:55 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 07:54 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 07:55 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-93; kuota tampilan anonim belum reset sejak run 50 (~170,5 jam lalu), meski jarak ~4 jam sejak run 93 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 95 — 2026-11-13 11:53-11:54 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 11:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 11:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-94; kuota tampilan anonim belum reset sejak run 50 (~174,5 jam lalu), meski jarak ~4 jam sejak run 94 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 96 — 2026-11-13 15:53-15:54 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 15:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 15:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-95; kuota tampilan anonim belum reset sejak run 50 (~178,5 jam lalu), meski jarak ~4 jam sejak run 95 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 97 — 2026-11-13 19:53-19:54 WIB — INCOMPLETE (login-gated)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 19:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN", tanpa header dompet/saldo/Activity); retry tab baru sesudah 30 detik tetap LOGIN-GATED 19:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-96; kuota tampilan anonim belum reset sejak run 50 (~182,5 jam lalu), meski jarak ~4 jam sejak run 96 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 98 — 2026-11-13 23:53-23:56 WIB (browser task harness-measured 23:53-23:56 WIB) — INCOMPLETE (LOGIN-GATED)
- Wallet 1 (0x13d1e9a96eba7906e1ede348c9bb604a03e46d02) LOGIN-GATED pukul 23:54 WIB: halaman GMGN BSC hanya menampilkan beranda dengan panel "You are not logged in to GMGN" + tombol "Log In", tanpa header dompet, saldo BNB, maupun tab Activity/Holdings. Retry tab yang sama setelah ~30 dtk tetap LOGIN-GATED pukul 23:55 WIB; retry tab baru tetap LOGIN-GATED pukul 23:56 WIB.
- Wallet 2-54 TIDAK dibuka, sesuai instruksi berhenti saat gating persisten — statusnya tidak terverifikasi, BUKAN dihitung tidak membeli. 0/54 halaman GMGN BSC terbaca publik.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-97; kuota tampilan anonim belum reset sejak run 50 (~186,5 jam lalu), meski jarak ~4 jam sejak run 97 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 99 — 2026-11-14 03:53-03:54 WIB (browser task harness-measured 03:53-03:54 WIB) — INCOMPLETE (LOGIN-GATED)
- Wallet 1 (0x13d1e9a96eba7906e1ede348c9bb604a03e46d02) LOGIN-GATED pukul 03:53 WIB: halaman GMGN BSC hanya menampilkan beranda dengan panel "You are not logged in to GMGN" + tombol "Log In", tanpa header dompet, saldo BNB, maupun tab Activity/Holdings. Retry tab baru setelah ~30 dtk tetap LOGIN-GATED pukul 03:54 WIB.
- Wallet 2-54 TIDAK dibuka, sesuai instruksi berhenti saat gating persisten — statusnya tidak terverifikasi, BUKAN dihitung tidak membeli. 0/54 halaman GMGN BSC terbaca publik.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-98; kuota tampilan anonim belum reset sejak run 50 (~190,5 jam lalu), meski jarak ~4 jam sejak run 98 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 100 — 2026-11-14 07:53-07:54 WIB (browser task harness-measured 07:53-07:55 WIB) — INCOMPLETE (LOGIN-GATED)
- Wallet 1 (0x13d1e9a96eba7906e1ede348c9bb604a03e46d02) LOGIN-GATED pukul 07:53 WIB: halaman GMGN BSC hanya menampilkan beranda dengan panel "You are not logged in to GMGN" + tombol "Log In", tanpa header dompet, saldo BNB, maupun tab Activity/Holdings. Retry tab baru setelah ~30 dtk tetap LOGIN-GATED pukul 07:54 WIB.
- Wallet 2-54 TIDAK dibuka, sesuai instruksi berhenti saat gating persisten — statusnya tidak terverifikasi, BUKAN dihitung tidak membeli. 0/54 halaman GMGN BSC terbaca publik.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-99; kuota tampilan anonim belum reset sejak run 50 (~194,5 jam lalu), meski jarak ~4 jam sejak run 99 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 101 — 2026-11-14 11:53-11:54 WIB (browser task harness-measured 11:53-11:54 WIB) — INCOMPLETE (LOGIN-GATED)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 11:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN" + tombol "Log In", tanpa header dompet/saldo/Activity); retry tab baru sesudah ~30 detik tetap LOGIN-GATED 11:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-100; kuota tampilan anonim belum reset sejak run 50 (~198,5 jam lalu), meski jarak ~4 jam sejak run 100 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.

## Run 102 — 2026-11-14 15:53-15:54 WIB (browser task harness-measured 15:53-15:54 WIB) — INCOMPLETE (LOGIN-GATED)
- 0/54 halaman GMGN BSC termuat publik. Wallet 1 (0x13d1...6d02) LOGIN-GATED 15:53 WIB (hanya beranda GMGN + panel "You are not logged in to GMGN" + tombol "Log In", tanpa header dompet/saldo/Activity); retry tab baru sesudah ~30 detik tetap LOGIN-GATED 15:54 WIB; berhenti sesuai instruksi — wallet 2-54 TIDAK dibuka, statusnya tidak terverifikasi, BUKAN dihitung tidak membeli.
- 0 pembelian baru terverifikasi di jendela run. Tidak ada sinyal yang bisa diklaim dari run ini (tidak ada CA terverifikasi sama sekali; ambang >=14 entitas).
- Tidak ada keterkaitan kuat baru teramati (tidak ada data Activity yang terlihat). Tidak ada upaya login (aturan read-only).
- CATATAN: gating level sesi, bukan per-wallet — gated sejak wallet pertama, sama seperti run 51-101; kuota tampilan anonim belum reset sejak run 50 (~202,5 jam lalu), meski jarak ~4 jam sejak run 101 (frekuensi 4 jam per amandemen 2026-11-06 ~07:49 WIB). Flag klaster run 49 (micro-bot 16/17/19/20/21, GrokBot 23-48+50) TIDAK bisa diverifikasi ulang run ini — wallet tidak terbaca, dibawa ke depan. Diskrepansi BNB wallet 2 (run-50 baca 0 vs state 1,15) tetap TIDAK TERVERIFIKASI dan belum terselesaikan; field BNB/holdings tidak diubah.
- Tindak lanjut: run berikutnya harus mengulang pembacaan ke-54 wallet; bila gating tetap persisten, perlu jeda lebih panjang / sesi anonim berbeda, atau keputusan terpisah soal login GMGN (tidak diotorisasi di sini).
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah.
