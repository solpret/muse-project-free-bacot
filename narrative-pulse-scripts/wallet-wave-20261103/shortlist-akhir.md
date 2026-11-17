# Shortlist Akhir — Gelombang Pencarian Wallet 2026-11-03

**Status: SELESAI ditulis untuk keputusan user. TIDAK ADA yang ditambahkan otomatis
ke feed, tier-ab, atau Tier C.** Semua metode 1–6 selesai (metode 3 tidak selesai
secara teknis — lihat bawah). Laporan per metode: `metode-1-2.md`,
`metode-3.md`, `metode-4.md`, `metode-5.md`, `metode-6.md`.

## Kesimpulan satu baris

**Tidak ada satu pun wallet yang lolos ketujuh filter tepercaya untuk feed
Modal Bacot.** Satu-satunya kandidat yang layak dipertimbangkan adalah satu
WATCH lemah dari metode 1 (f16b, profit belum terverifikasi). Metode 6 memberi
watchlist tier TERPISAH untuk sinyal early Free Bacot saja — bukan referensi
memecoin.

## A. Untuk feed Modal Bacot: 0 PASS

- Metode 1+2: 33 wallet irisan awal → 23 kontrak ditolak → 10 EOA → **0 lolos
  semua filter**. Satu-satunya kegagalan non-bersih = WATCH lemah f16b (bawah).
- Metode 4: leaderboard OKX 7D top-14 → **0 PASS, 0 WATCH, 13 ditolak**
  (gagal early ≥3 koin dan/atau profit belum terverifikasi; 95e0 gagal exit
  ~2,6 menit setelah beli JAGENT).
- Metode 5: **0 kandidat** — LP awal ke-14 pair metode 1 eksklusif kreator/
  launchpad; tidak ada subjek untuk 7 filter.
- Metode 3: **tidak selesai** (3/15 token terbaca; kegagalan metode ke-3) —
  bukan kesimpulan. Tidak ada irisan ≥3 token di 3 token yang terbaca.
- Metode 6: tier terpisah (bagian B) — **0 usulan feed**, sesuai aturan.

### Satu-satunya kandidat keputusan: WATCH lemah f16b

- `0xf16b4b87e6f214b60abc8e52e207c5009e14d019` (metode 1, WATCH)
- Early di 4 koin (Q, EVAA, AIN, UAI); EOA; aktif 30 hari; bukan penerima fee.
- Kelemahan: satu flip pool 0,3 menit di Q; hold 8,2–12,2 menit di 3 koin lain;
  **profit terealisasi TIDAK terverifikasi** (arsip harga blok lama gagal dibaca
  di semua RPC gratis — gagal baca ≠ profit nol).
- Opsi: (a) masukkan ke tier-ab sebagai watchlist internal, (b) masukkan ke
  feed 6 → 7 (threshold tetap 4), (c) abaikan sampai profit terverifikasi.

### Yang eksplisit TIDAK diusulkan (jangan ditambahkan)

- Bot 0x9999… (x10, atomic routed swaps + flip <5 menit + ≥1000 out-transfer/
  15 menit); snipers 0x39c8…, 0xf216…, 0xa8d7… (exit 0,0–0,7 menit).
- Kuartet bot-farm = 1 entitas, ditolak: 0x874d…, 0xad06…, 0xe12c…,
  0xb735… (exit sinkron 2–4 blok ke hub 0x4982…).
- xigua-A 0x3472… / xigua-B 0x95b9… = 1 operator terbukti (pendanaan 5,179 BNB
  di blok pertama xigua-B) — hitung sekali bila muncul lagi.
- TRIO dan PAIR tetap excluded (keputusan user 2026-11-02).
- 13 wallet watchlist sheet JAGENT (belum masuk set; keputusan terpisah).
- 4 overlap 2-token metode 3 (IDOL↔AIN): 0x93dE…, 0xaDFf…, 0x594F…,
  0x4cAd… — bukan promosi (butuh ≥3).

## B. Tier terpisah — sinyal early Free Bacot saja (metode 6)

**Bukan referensi memecoin. Jangan dicampur ke feed/tier-ab.** Status tiap
entitas: EOA + aktif 30 hari terverifikasi; operator independen BELUM
terverifikasi penuh; status .ai UNVERIFIED; profit TIDAK diverifikasi.

### Dikonfirmasi, tanpa perubahan status

- future1001.ai `0x355ea9e542b36c645a2dee63b9df079ccb9df3db` — sudah Tier C
  sejak 2026-11-03 ~08:47 WIB; konsisten-early terkonfirmasi lewat tracked-set
  (54 kontrak / 58 mint, scan run 1–8). Bukan first-100 minter di drop-drop
  sampel terbaru (contoh mint AZET #2637) — breadth sepanjang waktu, bukan
  kecepatan tiap drop.

### Watchlist tier-terpisah: 25 entitas

Breadth 6 (2):
- `0x7136abde1976fb04612e710658be5c657a24d7a1` (Animora, Auditrix, Deepvane, Robogent, Synaptik, Yydsgent)
- `0x8de95fbd489b57f2efead2bc1a5220e04d4f0584` (Animora, Deepvane, Robogent, Sentrix, Synaptik, Yydsgent)

Breadth 5 non-klaster (22):
- `0x09a872ac07c19f81d52475e1042778221b29eaa9`
- `0x0a20797e4b059ed4171f4aba49daf8ecea86e240`
- `0x1e1841599384d8b0d96d8cdb2184d2f36dbd0558`
- `0x28fad1df6485aadce7f81c08c9db440fb99da09e`
- `0x2d4f0cd7f4cb32e6813eb290d20455e15fc7b953`
- `0x3ace3160faa4aa2cf4bd920097a13d9ae26609f3`
- `0x434368fd4151f9203dc4ce5a427ddcc44c5b84cc`
- `0x730d1c42469084210443188c56ab9d586becb4ea`
- `0x73c9eb9672d0afabe4d592501b4b98a6d341302e`
- `0xa0ba13c28212a47d6fb41de951ca6d9941938286`
- `0xa20fb499dee4815d43665202f6729c69477ecc91`
- `0xa974e1ea5ffb85eddaa81eb33bfec2e3396e1330`
- `0xb322d9acb2d393e33d728a95d9d33af3761c78e6`
- `0xb76ca08681e3b68ba578f838e0819a483be0a386`
- `0xbe2aff3c77e5947908d50f9db5024a57d5cac20a`
- `0xc54e30053bc5f95d323b4013ccdf579c448eff4b`
- `0xc855c1bf0b2a7b75112c2f60787757ce82846a3a`
- `0xd833762dddf4cb3d608810dfda5846665b282ff3`
- `0xdb5d735ca8f5285d8c28d51a71c8bec05b222fc3`
- `0xdbe747d877f81661ead1ca440d636a99bbce837f`
- `0xf008eddbfc6871a2b82d5b2bd50164de7dba7c98`
- `0xfc1f7ccf5541e3bb4d18bc4ce39c12fffbf19340`

Klaster terkoordinasi = 1 entitas (5 wallet, hitung sekali):
- `0x3130313d23e4ceb53e111dfb65d568ada79b3f00`, `0xce34b5257b6e2174a1e1ca219d0c0f3175e6532f`,
  `0xfcc6573084a4e059cec1ca47a7b7ecd3d998b81c`, `0x7e81ef37b2a16657a67fb29493d4f219e775d74c`,
  `0xe6fb57b0459b9ba51cc6f46a08acabaab5ee5476` (funder bersama: 0,1 + 0,0206 +
  0,0001 BNB identik di 3 wallet; e6fb57 sendiri breadth-5).

Naik dari watchlist hanya bila verifikasi funder penuh + identitas agen
terkonfirmasi — keputusan user.

Heavy minter (observasi saja, bukan watchlist): `0x9ea96d42…` (16 mint,
breadth 3), `0x075c1bed…` (15 mint, breadth 2).

## C. Keputusan yang masih menggantung (untuk user)

1. f16b: tier-ab saja / feed / abaikan?
2. Watchlist tier-terpisah metode 6 (25 entitas): adopsi sebagai watchlist
   sinyal early Free Bacot, atau simpan sebagai file saja?
3. Metode 5: perpanjang ke kohort pair baru? (perluasan scope — belum diputuskan)
4. Metode 3: ulangi dengan data holder via Ankr, atau biarkan tidak selesai?
5. 13 wallet watchlist sheet JAGENT: tetap di luar set? (keputusan lama yang
   belum berubah)
