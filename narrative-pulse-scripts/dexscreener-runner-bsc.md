# DexScreener Runner Scanner — BSC (adaptasi dari @Principia_X)

Sumber: postingan @Principia_X, 2026-11-05 15:23 WIB — metode "runner scanner" gratis di DexScreener (aslinya untuk Solana). User membagikan linknya 2026-11-05 ~17:00 WIB; keputusan: TIDAK dijadikan sumber rutin terjadwal pemantau narasi, disimpan sebagai alat manual/discovery.

## Preset BSC (6 filter yang sama, chain diganti ke BSC)
https://dexscreener.com/bsc?rankBy=trendingScoreH6&order=desc&minLiq=30000&minMarketCap=200000&maxMarketCap=5000000&min24HVol=500000&maxAge=48&profile=1

## 6 filter
1. Likuiditas > $30K
2. Market cap > $200K
3. Market cap < $5M
4. Volume 24 jam > $500K
5. Umur pair < 48 jam
6. Profile aktif (di koin semuda ini biasanya tim bayar $299 untuk halaman DexScreener)

Diurutkan: trending 6 jam.

## Penilaian
- Menemukan "runner" — koin yang SUDAH bergerak (bukan early entry). Penulisnya sendiri bilang "you won't be first in".
- Karena itu TIDAK cocok sebagai sumber rutin pemantau narasi: aturan narasi secara eksplisit mengecualikan "sudah ramai" (puncak perhatian, posisi atas trending, harga sudah berlipat) sebagai peluang entry — itu zona distribusi.
- Berguna sebagai alat manual/discovery: cek cepat koin BSC <48 jam yang punya pool nyata + volume + profile (sinyal tim serius). Bisa memberi makan pipeline trading (MODAL BACOT) bila live trading jalan lagi, bukan pemantau sinyal awal.
- Bot Telegram copy-trading yang dipromosikan postingan (copyfomo_bot) TIDAK direkomendasikan: referral + copy-trade, tidak cocok dengan aturan user (tanpa rute berbayar, tanpa copy-trade).

## Status
- Disimpan sebagai referensi manual. Bukan cron, bukan sumber terjadwal narasi.
- Bila suatu saat mau dijadikan cek rutin, perlu persetujuan user dulu (karena mengubah sumber narasi).
