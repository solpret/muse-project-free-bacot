# SENSEI whale scan — 2026-11-01 (read-only, internal)
- Project: senseiagent.xyz, $SENSEI, BSC. Token 0xa6839b3bc2483f8312466efa25ac8ccc8feb52da,
  Mint 0x50523377351a3c3a0afc550d7a6d14ff8e7ba777, Pool 0xab757b19c35cede781097d4ebf7a764f47a9a05a,
  Revenue Safe 0x71098401d1d3f870b7fc44175d10f2251c4191cc, Management 0x3010d4e5f4d5049065dda37d2dcf0a99e9a33b2a.
- Site API /api/activity: totalMinted 11.559 units (> 10.000 pool-open threshold; pool created 2026-11-01T06:03:13Z).
- Supply on-chain ~990,06 miliar SENSEI (18 dec). Ankr holders list: 927 holders, sum matches supply.
- Distribution (share of total supply): burn 0x000...dEaD 19,92%, pool 17,52%, top independent 2,01%,
  2nd 1,26%; independent >=1%: 2 wallets; >=0,5%: 15; >=0,1%: 169; top10 independent 9,11%; top20 13,89%.
  Median independent holding 0,031%. At pool price ~$1,4714e-7: >=$1.000: 7 wallets; >=$100: 223 wallets.
- Site hold-top20 = independent wallets only (excludes pool+burn); 4/5 spot-checked match on-chain
  exactly (1 had sold between site snapshot block 131032372 and re-read — normal).
- Overlap site hold-top20 vs mint-top20 = 0: biggest holders bought on market, not via mint.
- Flow h1 (GeckoTerminal): 1.175 buys vs 2.013 sells, buyers 722 vs sellers 1.407 — distribution-heavy
  window; price m30 +187,8%, h1 +23,0% (volatile). Pool reserve ~$21.836, volume h24 ~$202.692.
- Verdict: TIDAK banyak whale besar (only 2 above 1%); mid-tier broad (169 above 0,1%).

## Deep check 2 whale teratas — 2026-11-01 (OKLink + GMGN, tanpa login; + cek on-chain sendiri)
- W1 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36: EOA, umur ~5 hari (tx pertama 27/10/2026, +0,02 BNB dari
  Binance Withdraw_61), 32 aset ~$7,74K (ALOY ~$2,70K, SENSEI ~$2,26K, BNCB ~$1,51K). 7 hari: 30 beli/23 jual,
  81,82% beli di MC $0–100K, $97–957 per beli, repeat early buy banyak token (BNBCAT, COOL, TOSH, BIBIAI +118,9%,
  ALOY +489%), SENSEI 4x beli sejam terakhir tanpa jual. Win rate 46,67%, realized 7D +$2,46K (+21,29%),
  total PnL +$7,75K (+54,53%). On-chain sendiri: 100 tx terakhir semua keluar, 50x ke kontrak eksekutor pribadi
  0x296b... (proxy, implementasi tak terverifikasi) + approval token-token ke kontrak itu = pola bot/eksekutor.
  VERDIK: kandidat smart wallet, LAYAK dipantau (promosi menunggu ketukan user).
- W2 0x91a1305a5607c879ba3356abda6b5d390e302f3c: EOA, umur 383 hari (GMGN; OKLink hanya mengindeks dari
  05/05/2026; incoming pertama terlihat 29/05/2026 +0,10499 BNB dari Binance Withdraw_57; GMGN menyebut funder
  0xf5...b115 3,1 BNB — gambaran pendanaan belum lengkap), 263 aset ~$14,21K tapi 67% di satu token
  (rugi berjalan -$3,03K). Pola terkonsentrasi: BIBIAI 10x beli (jual -$1,01K/-44,4%), JAGENT 5x jual (+$879/+377%),
  SENSEI 2x beli $699,67 + 1x jual $532,82 (unrealized +$814/+153%). Win rate 40%, realized 7D -$2,84K (-26,31%),
  total PnL -$1,23K (-3,68%). On-chain sendiri: 78 keluar + 22 masuk, 48x ke eksekutor pribadi 0xb300...,
  approval SENSEI tak terbatas ke kontrak itu, transfer BNB bolak-balik dengan 0x47e80e... (petunjuk klaster
  belum terbukti). VERDIK: TIDAK direkomendasikan sebagai smart wallet (whale satu token, PnL negatif).
- Antar keduanya: TIDAK ditemukan transfer langsung / funder bersama (funder pertama berbeda) = bukan cabal
  berdasar bukti yang ada. Keterbatasan: counterparty GMGN ter-mask (transfer kecil tak bisa dikesampingkan
  penuh); OKLink sempat soft-block data kedua alamat lalu terbuka setelah reload.
