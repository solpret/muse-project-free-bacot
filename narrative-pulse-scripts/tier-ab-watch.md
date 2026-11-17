# Pemantau Tier A+B — aturan sinyal internal (INTERNAL, bukan laporan rutin)

Dibuat 2026-10-31, atas perintah user: pantau Tier A dan B sebelum ada wallet terpercaya;
jika lebih dari 25% wallet tersebut membeli koin yang sama, jadikan itu sinyal untuk Muse.
Koreksi audit linkage 2026-10-31 diterapkan di sini.

## Wallet yang dipantau: 14 EOA privat saja (BUKAN 23 alamat Tier A+B lama)

Tier A lama berisi 22 alamat, Tier B 1 alamat, total 23. Audit linkage (OKLink, 2026-10-31)
menemukan 6 di antaranya adalah wallet exchange sendiri dan 3 adalah kontrak — semuanya
SUDAH dipindah ke Tier E di wallet-priority-full.md dan TIDAK dipantau sebagai monitor.
Sisa monitor privat:

Tier A privat (13):
- 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6
- 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02
- 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5
- 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7
- 0x75642756e4ba4cc8fbe76df2239cada046cfc854
- 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a
- 0x892200223bdfb11d2506c5ab1cae9222ce253acc
- 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c
- 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e
- 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462
- 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf
- 0xda91cefe240175e6fab56271110427a4195ab71f
- 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc

Tier B privat (1):
- 0x2325f175975abdbcde555c79cc8e63381d28551b

Total monitor: 14 entitas (berdasarkan data yang dicek; bukan bukti independen mutlak).

Tier C ekspansi (35, promosi 2026-11-01 ~17:16 WIB atas ketukan user):
kandidat scan idle 2026-11-01 (wallet-expansion-scan-2026-11-01.md), masing-masing EOA beli awal di >=2 pool, bukan kontrak/exchange/terpantau lama. Verifikasi deployer + pendanaan MASIH tertunda untuk 35 ini (diungkap sebelum ketukan).
- 0x9856bac497634a62a970233bc4b0f5bb52c844c1
- 0x3628764a6576b8dfb31fba0aac6a333b64851423
- 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e
- 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c
- 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74
- 0xad94ee77d0e868d299fb3e92b9d67560257f656d
- 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a
- 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650
- 0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b
- 0xc621946845d0fd5d1dbc6d6beb3e22aed39d7050
- 0xf795c5250f3d4006283a0d0dbb378dc0e69df923
- 0x9cdd08f30188c2732cdbcac8eebf4e6e8bf0c1b2
- 0xaa49e7fec503664a39598645c7a3fbfa0374380d
- 0x82c6085f9ec2722fd6c8fc47577368a156a25b9b
- 0x3154f6949285ee7ac1593bd2bdf974adb6731c32
- 0xca4e67bb5737c095bd3a80f79ecc6607e5723f1a
- 0xe9ed24db105a6b15f880025ed9ad024c06783895
- 0x3a39aa05b149141a4bfc7d73611dceb0557b39c4
- 0xcb08c02c0a386a10773a2c6589e7089a3dd5aca3
- 0xb940e4cd40ea9e887cbc92879062676e2bc4a924
- 0x4522e661d9c94ec54b37e71896351a7440ec4f07
- 0x5b4beded36c1ea380abe8c6a6a0c4408f38e5024
- 0xc6591fde9b44aa081062c9fc6ee48e443d24ef57
- 0x362396125a55d932a09f0a5182140cbbcaf30b70
- 0xf9689b9d0a675ff9ad876f1d766fb460dbde7d20
- 0x2cc8192fc62e3640de91e75582cf3dbbd571b970
- 0x97bd895f8123a7837368df410e7d308246c0b3e9
- 0x1cce4ec5a7c5e8cfc8dedd771876c61e60b8b645
- 0xc0c84518ced6a61d2a4f4a50bc0f438e0cb1031b
- 0xc194efe22e874a3fe666b5de5a8fd369f12c32d5
- 0xa952331ea48ea9c00c4608d8259c186021331f31
- 0x92bc32975b0fbf1a19caf7cc6e3f9ea4092fd314
- 0x9b519f5d52cdd03e4b10484829bc137eef1f8c1a
- 0xfdec62fde1f1dc56c0ba5e50f4cae5d6c63762bf
- 0x64e893a4c5c930b2cc68b054792cbc66344aeb9a

Total monitor SETELAH promosi: 49 entitas (13 Tier A privat + 1 Tier B privat + 35 Tier C ekspansi). Ambang sinyal SETELAH promosi: >25% dari 49 = minimal 13 entitas berbeda membeli token baru yang sama.

Promosi individual 2026-11-01 (ketukan user):
- 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36 — whale SENSEI #1 (2,01%), kandidat smart wallet dari deep check 2026-11-01 (wallet baru 5 hari, didanai Binance 0,02 BNB, repeat early buyer banyak token, realized 7D +$2,46K, total PnL +$7,75K; trading via kontrak eksekutor pribadi 0x296b...; bukan klaster dengan whale SENSEI #2).

Total monitor SETELAH promosi wallet 1: 50 entitas. Ambang sinyal: >25% dari 50 = minimal 13 entitas (floor(0,25×50)+1 = 13, tidak berubah).


## Ambang sinyal

Lebih dari 25% dari 14 = minimal 4 wallet privat BERBEDA membeli token baru yang sama.
Hitungan memakai ENTITAS, bukan alamat mentah:
- Jika di run berikutnya ditemukan keterkaitan KUAT baru (pendanaan bersama non-exchange,
  transfer langsung, pendanaan berantai) antara dua wallet yang dipantau, runtuhkan
  keduanya menjadi 1 entitas untuk hitungan run itu dan seterusnya.
- Ambang absolut tetap 4, tidak diturunkan bila entitas menyusut — ini konservatif.
- SKALA (aturan user 2026-11-01): persentase TETAP >25% berapa pun jumlah wallet terpantau. Bila set terpantau tumbuh karena tambahan smart wallet, ambang naik mengikutinya: ambang = floor(25% × jumlah entitas terpantau) + 1, dengan lantai 4. Contoh: 14 entitas → 4; 20 entitas → 6; 40 entitas → 11. Ambang tidak pernah turun di bawah 4.

## Klasifikasi simpanan + cek mendalam (aturan user 2026-11-01)

Wallet yang disimpan ke koleksi adalah tiga jenis: smart wallet (pola beli awal berulang), whale (ukuran beli awal besar), dan cabal (klaster wallet yang bergerak bersama).
Untuk tiap wallet yang disimpan, cek mendalam WAJIB mencatat:
- sumber pendanaan: pengirim BNB masuk tertua yang teramati (bukan exchange bila teridentifikasi sebagai exchange);
- wallet-wallet terhubung: wallet lain yang berbagi sumber pendanaan yang sama (keterkaitan KUAT) atau transfer langsung;
- wallet utama klaster sebagai data tambahan: dompet sumber dana bila teridentifikasi, bila tidak maka wallet dengan pembelian awal terbanyak/terawal di klaster itu.
Keterkaitan KUAT meruntuhkan beberapa alamat menjadi 1 entitas untuk hitungan sinyal. Pendanaan dari exchange TIDAK membentuk cabal. Wallet hasil scan idle adalah KANDIDAT dulu — promosi ke set terpantau butuh verifikasi lanjutan (bukan deployer, bukan kontrak/exchange) dan persetujuan user bila mengubah ambang sinyal.
- Keterkaitan LEMAH (co-buy / co-hold saja) TIDAK meruntuhkan entitas.
- Pendanaan dari exchange TIDAK menghitung sebagai keterkaitan antar wallet.

## Definisi "membeli koin yang sama" untuk sinyal ini

- Token BARU bagi wallet tersebut: CA terverifikasi (on-chain / GMGN), belum pernah
  tercatat dipegang wallet itu di state pemantau ini sebelumnya.
- Bukan mubarak / SKYAI yang sudah dipegang — itu holdings lama, bukan pembelian baru.
- Pembelian BARU yang teramati di jendela run (aktivitas terbaru sejak run sebelumnya),
  dicatat per wallet: CA, waktu beli pertama yang teramati, ukuran.
- Satu wallet membeli token yang sama berkali-kali tetap dihitung 1 entitas.
- Token yang hanya dibeli 1-3 wallet = BUKAN sinyal, hanya dicatat di log.

## Apa arti sinyal ini — dan apa yang BUKAN

- Sinyal = pemicu INTERNAL untuk screening paper saja.
- Sinyal BUKAN rekomendasi beli, BUKAN promosi ke daftar pantau terpercaya,
  BUKAN bukti insider, dan BUKAN pemicu trade.
- Setelah sinyal, kandidat tetap harus lolos SELURUH gerbang screening + konfirmasi
  money-flow + konfirmasi entry sebelum masuk paper, dan otomasi live tetap TIDAK
  dipersenjatai.
- Data GMGN adalah agregat sekunder, bukan bukti on-chain mentah — nyatakan itu di log.

## Aturan run (baca-saja)

- Jangan login sendiri, jangan connect wallet, jangan sign, jangan beli/jual/follow.
- Bila halaman wallet login-gated, catat login-gated saja dan lanjut — jangan klaim
  sinyal dari run itu.
- Bila wallet tidak terbaca, catat tidak terbaca, jangan anggap tidak membeli.
- Catat setiap run di tier-ab-watch-log.md + tier-ab-watch-state.json (internal).
- SENYAP ke chat: sinyal dicatat internal saja. Pengecualian satu-satunya yang sudah
  berlaku umum: bila sebuah wallet kemudian memenuhi SELURUH kriteria promosi
  terpercaya (pola ≥3 token + PnL terealisasi 30 hari + keputusan user), itu dilaporkan
  sekali karena promosi butuh keputusan user — itu bukan laporan rutin sinyal ini.
- Jangan ubah MEMORY.md dari run ini; observasi cukup di log + state + log harian bila ada.
