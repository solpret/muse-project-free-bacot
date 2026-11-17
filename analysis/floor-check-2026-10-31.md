# Floor check 2026-10-31 ~07:55 WIB

## Fresh on-chain, 2026-10-31 (block ~130763862)
- SAFU #3073: listings(3073) seller = wallet utama, price 0.00125 BNB — MASIH TER-LISTING
- CIOW #480: listings(480) seller = wallet, price 0.00125 BNB, isValid=1, feeBps 500 — MASIH TER-LISTING
- AlienID #3333: listings seller = wallet, price 0.001 BNB, active=1 — MASIH TER-LISTING
- AlienID #3684: listings seller = wallet, price 0.001 BNB, active=1 — MASIH TER-LISTING
- Brutes #3967: listings seller = wallet, price 0.000076 BNB — MASIH TER-LISTING
- Hirelings #3927 / #4342: listing() = 0.000133 BNB (0 sebelum listing 2026-10-30) — MASIH TER-LISTING
- WOBBLOKZ in-contract market: marketOpen=1, marketSales=0, marketVolume=0 — belum ada penjualan terverifikasi di market itu
- DIGG Market listings 1..30 (USDT, 18 desimal, active=1 kecuali #21 dan #29 yang inactive):
  - Floor semua tier: 0.8 USDT (listing 24, 28, 30 — tier 1 Stone)
  - Floor Copper (tier 2): 0.89 USDT (listing 18; listing 16 Copper 5 USDT)
  - Turun dari pagi 2026-10-31 (floor Copper 2 USDT saat mint)
  - Ore user TIDAK ter-listing; fee market 2.5%

## Fresh API, 2026-10-31
- Boltbook Runestone solo (wallet 2, #5634 TIDAK ter-listing, dan memang dikecualikan dari listing):
  floor 0.001 BNB, fee 2.5%, daySales 229, volume hari 0.285116 BNB, volume total 0.739386441025641025 BNB, topSale 0.02 BNB, topOffer null.
  Blanket bids tier 7 @ 0.001 BNB (id 54-68) masih ada — itu bid untuk tier VIII apa pun, bukan bid spesifik #5634.

## Baseline 2026-10-30 (BUKAN fresh hari ini — rescan penuh 1.000+ listing tidak diulang di turn ini)
Own-market floor scan 2026-10-30 ~14:53 WIB:
- SAFU own floor 0.00014 BNB (61 listing live)
- CIOW own floor 0.000069 BNB (401 listing isValid=1)
- AlienID own floor 0.001 BNB (= MIN_PRICE market, 740 listing)
- Brutes own floor 0.00008 BNB (98 listing)
- Hirelings own floor 0.00014 BNB (190 listing)
Element snapshot 2026-10-30 13:10-13:17 WIB (venue kedua, bukan market sendiri):
Pulse 0.000128, Synklings 0.00023, SAFU 0.000059, CIOW 0.00007, Mintra 0.001, BinanceMiner 0.00013, AlienID 0.0004, Brutes 0.00045, Hexhive 0.000882, Jellume 0.000035, Hirelings 0.0005, Robotic 0.00019, DigiWarriors 0.000038, HALCYX 0.00025, Fragment 0.000054, HALLU 0.00045, Crystals 0.00045, AgentPunks 0.000247, Bolt Runes 0.00095.
Own-market lain 2026-10-29: Mintra floor 0.0004 (462 listing), BinanceMiner floor 0.0005 (93 listing).

## Penjualan / volume — batas verifikasi
- Hanya Boltbook solo yang memberi angka volume + penjualan harian/total yang bisa dibaca (di atas).
- WOBBLOKZ: 0 penjualan, volume 0 (counter on-chain).
- Market sendiri SAFU/CIOW/AlienID/Brutes/Hirelings/DIGG: tidak ada counter volume/penjualan total yang terverifikasi di kontrak — floor = harga listing terendah, BUKAN harga jual terbukti.
- Tidak ada market live terverifikasi untuk: SIGILS, MORI, SEVY, GLYPH, BOTMOLT, CORA, dan koleksi lain tanpa market sendiri; SPACE ID Agent ID (soulbound) dan CharMasks Pass (non-transferable) tidak bisa diperdagangkan.
