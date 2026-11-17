# Daftar Tracking Wallet — LAPISAN DISCOVERY SEJAJAR NARASI

Status (keputusan user 2026-10-31): tracking wallet adalah lapisan
PENTING yang sejajar dengan narasi, bukan sekadar referensi. Sinyal
wallet menemukan kandidat; gerbang keras yang memutuskan trade.
Sinyal wallet tidak pernah mengesampingkan gerbang, tidak pernah
menjadi pemicu trade sendiri, dan tidak pernah menggantikan
verifikasi kontrak, tax, LP, atau konsentrasi.

## Apa yang dihitung sebagai "smart money"

Label vendor (mis. leaderboard smart-money GMGN) hanya titik awal,
bukan verifikasi. Sebuah wallet baru masuk daftar pantau bila:
- profit terealisasi terukur selama minimal 30 hari dari riwayat
  on-chain (bukan satu trade beruntung)
- minimal 10 trade terealisasi dalam sampel
- perilaku holding tercatat (bukan hanya flip menit-jam)

Verifikasi ulang tiap bulan: wallet yang PnL 30-harinya berubah
negatif atau aktivitasnya berhenti dicopot dari daftar aktif
(tetap tercatat di riwayat).

## Prinsip dasar (user 2026-10-31)

Narasi ramai tidak akan bergerak tanpa adanya pergerakan uang yang
besar yang mendorong pergerakan harga — itu dasar dari memecoin.
Karena itu lapisan ini bukan pelengkap narasi: ia adalah konfirmasi
yang menaikkan sinyal narasi dari alert menjadi kandidat prioritas.
Volume mentah saja tidak cukup sebagai konfirmasi (mudah dipalsukan
lewat wash trading); yang dihitung adalah akumulasi wallet terpantau,
pertumbuhan holder nyata, dan inflow likuiditas.

## Sinyal yang dicari

- Akumulasi mendahului sosial: wallet terpantau membeli SEBELUM
  mention sosial naik (leading indicator untuk lapisan narasi)
- Pembelian klaster: beberapa wallet terpantau membeli token baru
  yang sama dalam jendela singkat
- Wallet segar vs wallet dikenal: pembelian oleh wallet segar adalah
  sinyal yang LEBIH LEMAH (kemungkinan bundle) — dicatat terpisah,
  tidak disamakan dengan wallet terpantau

## Klaster wallet: satu smart wallet = banyak alamat (prinsip user 2026-10-31)

"Onchain never lies" — semua keterkaitan terlihat di rantai, jadi
analisis TIDAK BOLEH berhenti di satu alamat. Smart wallet hampir
selalu mengendalikan lebih dari satu wallet: alamat utama, alamat
fresh/satelit, alamat akumulasi, alamat distribusi. Untuk SETIAP
wallet yang dianalisis, petakan klasternya:
- Wallet pendana: siapa yang mengisi gas/dana pertama wallet ini.
- Wallet turunan: wallet lain yang didanai oleh wallet ini.
- Rekan transfer: wallet yang menerima/mengirim token langsung
  dari/ke wallet ini.
- Co-buyer: wallet lain yang membeli token yang sama dalam
  jendela waktu yang sama.
- Interaksi deployer: pernahkah wallet ini berinteraksi dengan
  wallet deployer token yang sama.

Penilaian dilakukan di level KLASTER, bukan alamat tunggal:
PnL yang dihitung adalah PnL gabungan klaster. Satu alamat yang
tampak untung tetapi klasternya merugi atau sedang distribusi
adalah BUKAN smart — itu lengan distribusi, dan dicatat sebagai
distribution flag, bukan sebagai sinyal beli. Alamat satelit
(fresh, didanai klaster) tidak dihitung sebagai wallet independen;
ia dicatat sebagai anggota klaster dengan peran (akumulasi /
distribusi / umpan).

Standar keterkaitan: KUAT = sumber pendanaan bersama, transfer
langsung antar wallet, atau pendanaan berantai. LEMAH = hanya
co-buy token yang sama tanpa koroborasi lain — dicatat sebagai
"kemungkinan klaster", bukan fakta.

Kejujuran soal "onchain never lies": on-chain menunjukkan APA
yang terjadi dan KAPAN — bukan NIAT. Apakah sebuah klaster itu
insider, kebetulan, atau sekadar trader cepat tetap inferensi;
jangan pernah menulis "terbukti insider" hanya dari data
on-chain. Yang dicatat adalah fakta (alamat, waktu, jumlah,
keterkaitan) dan inferensi dipisah dengan label yang jelas.

## Batasan yang diakui jujur

- Wallet bukan orang: satu orang bisa mengendalikan banyak wallet.
  Klaster hanya dihitung sebagai satu entitas bila keterkaitannya
  terkoroborasi (mis. sumber pendanaan bersama di Bubblemaps);
  bila tidak terkoroborasi, tiap wallet dihitung terpisah.
- Riwayat trade diambil dari agregat GMGN/DexScreener — di VM ini
  eth_getLogs praktis tidak tersedia, jadi log mentah bukan sumbernya.
  Data agregat adalah data sekunder: cukup untuk alert discovery,
  tidak pernah menjadi bukti tunggal untuk trade.
- Sinyal satu wallet saja = alert saja, sama seperti sinyal satu
  sumber di lapisan narasi (G5).

## Daftar

Daftar ini dimulai KOSONG pada 2026-10-31. Wallet pertama masuk
hanya setelah pengukurannya tercatat di sini — tidak ada alamat
yang diisi dari daftar vendor atau dari ingatan.

| Wallet | Label sumber | PnL 30 hari terukur | Trade terealisasi | Perilaku holding | Terakhir diverifikasi | Status |
|--------|--------------|---------------------|-------------------|------------------|----------------------|--------|
| — | — | — | — | — | — | — |
