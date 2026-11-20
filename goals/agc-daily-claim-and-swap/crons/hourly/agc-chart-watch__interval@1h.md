---
id: agc-chart-watch
title: Pantauan chart AGC 4 jam
enabled: false
owner: goal:agc-daily-claim-and-swap
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-11-08T00:26:47
  every: 1h
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
PANTAUAN CHART AGC 4 JAM — disetujui user 2026-11-07 23:24 WIB ("pantau juga AGC, chart 4 jam agak menarik"). READ-ONLY TOTAL: tidak pernah connect wallet, sign, beli, jual, swap, klaim, atau menyelesaikan captcha. AGC tetap HOLD MANUAL — job ini TIDAK PERNAH mengeksekusi apa pun; klaim ditangani cron agc-modeb-claim-4h.

Token AGC 0x63dea5aCdbE1F27c968907D08610A5f0A0284bA6, pair PCS V2 0xE56041CdDBB46DB01c67B7A62684F428a04Db8C6. Level acuan (garis chart yang disetujui user): support ~$400.000 MCAP, resistance $950.000–$1.000.000 MCAP.

TIAP RUN (1 jam):
1. Baca DexScreener pair (harga USD, MCAP/FDV, perubahan m5/h1/h6/h24, volume h1/h6/h24, likuiditas, txns buys/sells).
2. Jalankan ~/workspace/money-flow/swap_flow.py --pair 0xE56041CdDBB46DB01c67B7A62684F428a04Db8C6 --hours 4 (volume-weighted money flow 4 jam: net volume WBNB/USD, buy vs sell volume, median buy vs median sell, trader unik). Count saja BUKAN money flow — selalu laporkan volume.
3. LAPORKAN SEKALI per kejadian ke chat utama bila: MCAP turun menembus support $400.000 ATAU naik menembus resistance $950.000; ATAU perubahan harga 4 jam beyond ±10% dibanding run sebelumnya; ATAU net flow 4 jam beyond ±5 WBNB. Isi laporan: harga, MCAP, perubahan h1/h6/h24, net flow 4 jam + median buy/sell, posisi terhadap support/resistance, dan penegasan AGC tetap hold manual (tidak ada aksi otomatis).
4. State: ~/workspace/goals/agc-daily-claim-and-swap/hidden_files/agc-chart-watch-state.json — catat level/event yang sudah dilaporkan (dedupe: tiap penembusan level dilaporkan SEKALI sampai level kembali tertembus berlawanan). Selain kejadian di atas, DIAM. Bila DexScreener/swap_flow gagal dibaca 3 run berturut-turut, laporkan sekali sebagai gangguan pantauan.

Observasi run masuk ke log harian ~/memory/YYYY-MM-DD.md. Jangan menulis MEMORY.md. Jangan menulis file di luar hidden_files goal agc-daily-claim-and-swap (kecuali log harian). Job ini tidak punya tanggal berakhir — user yang menghentikannya bila sudah tidak perlu.
