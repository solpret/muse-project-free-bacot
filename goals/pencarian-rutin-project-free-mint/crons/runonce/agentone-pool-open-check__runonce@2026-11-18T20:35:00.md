---
id: agentone-pool-open-check
title: AGENTONE pool-open check (sekali, 20:35 WIB)
enabled: true
owner: goal:pencarian-rutin-project-free-mint
mode: task
schedule:
  kind: runonce
  timezone: Asia/Jakarta
  at: 2026-11-18T20:35:00
timeout_secs: 1800
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  tags: [cron:exact-time]
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
Cek sekali (read-only) apakah pool AGENTONE sudah buka, lalu laporkan sekali ke chat utama. JANGAN klaim, JANGAN swap, JANGAN eksekusi apa pun — hanya baca.

Konteks: 2 kartu AGENTONE Hero #3330 + #3331 di-mint gratis 18:17 WIB 18 Nov 2026 di agent wallet 0xeb237F6f9FB4e826739F0954e9768914F28b2c2E. Tiap kartu mengunci 3.000 AONE di kontrak Arena, total 6.000 AONE terkunci. Saldo AONE wallet = 0. Harga buka 3.000 AONE = $1 → nominal ~$2. Kontrak (BSC): sale 0x84D82E933D7781fe11245e7bbd3Eb23dbb963666, token AONE 0x84a0e2831665f2a9aa3824efbe0f5d32f9331f87, hero 0x9B0c237A123277fCf8768550Bbdd7767C73Cf5D3, arena 0x4A003Cc2C60945D31f464F7D664f8AD48fa49F6B, pair 0x062af274ad1ee9c4e2520968e4d3865784bc7975.

Langkah:
1. Baca freeMinted() di kontrak sale (terakhir dibaca 18:54 WIB: 5.315/10.000, laju ~54/menit → perkiraan buka ~20:20 WIB) dan getReserves() di kontrak pair. Pakai cast (~/.foundry/bin/cast) atau JSON-RPC via https://1rpc.io/bnb; egress VM sering flaky — coba ulang beberapa kali dengan endpoint berbeda (1rpc, publicnode) dalam batas wajar. Bila bacaan gagal, laporkan gagal apa adanya, jangan tebak.
2. Pool dianggap BUKA bila reserves pair > 0 (likuiditas sudah masuk).
3. Bila pool BUKA: cek dari state kontrak Arena apakah 6.000 AONE yang terkunci di 2 kartu itu sudah bisa diklaim/dijual (baca state Arena untuk kedua kartu; apakah AONE terkunci itu benar-benar bisa dicairkan masih UNVERIFIED — verifikasi dari state kontrak, jangan asumsikan). Bila bisa dijual, hitung kuotasi dari reserves pair (AONE→BNB, sebutkan angka + cara hitungnya). Laporkan sekali ke chat utama: pool buka + bisa dicairkan atau tidak + kuotasi bila ada.
4. Bila pool BELUM buka: laporkan sekali jumlah kursi gratis saat ini + perkiraan waktu buka yang direvisi (dari laju terakhir), lalu BERHENTI. Jangan loop, jangan buat cron baru — hot-leg 5 menit sudah memantau kursi.
5. Penjualan apa pun (bila bisa dicairkan) butuh persetujuan eksplisit user + audit + preview bersih — JANGAN pernah eksekusi di run ini.
