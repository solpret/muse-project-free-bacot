---
id: agent-registry-watch
title: Pantauan registry Agent ID
enabled: false
owner: goal:pencarian-rutin-project-free-mint
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-11-07T11:22:53
  every: 15m
timeout_secs: 900
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
PANTAUAN REGISTRY AGENT ID (disetujui user 2026-11-07 ~10:58 WIB — pengganti fungsi discovery Boltbook yang mati 2026-11-07). READ-ONLY + lapor saja: TIDAK PERNAH preview/mint/klaim/approve/sign/swap/tx.

AMENDMENT 2026-11-07 ~13:03 WIB (perintah user: "Ini tidak perlu dilaporkan ke saya kecuali ada yang lolos saja"): laporan ke chat utama HANYA bila ada mint yang LOLOS — yaitu namanya terbaca (resolved) sehingga proyeknya bisa diidentifikasi, atau mint yang lolos screening jadi early lead. Mint baru yang namanya belum terbaca TIDAK dilaporkan (hanya dicatat di state/log); daftar panjang tokenId/minter/blok yang belum terbaca bukan laporan.

Registry Agent ID BSC: 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (ERC721). Mint baru = event Transfer dari alamat nol, ~7 mint per ~50 menit (dry-run 132125341–132126341: 7 mint — koreksi atas hitungan awal 3 dari dump parsial).

TIAP RUN (15 menit):
1. cd ~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files && python3 -u registry-watch.py
2. Baca run JSON registry-watch-<from>-<to>.json hasil run itu.
3. Mint baru yang namanya BELUM terbaca (name null): JANGAN laporkan ke chat utama — catat saja di state/log seperti biasa. TokenURI gagal di-retry run berikut; bila kelak terbaca, laporkan saat itu sebagai reresolved (langkah 4).
4. LAPORKAN SEKALI ke chat utama HANYA bila ada yang LOLOS: (a) mint baru yang namanya TERBACA (resolved) — sebutkan nama + tokenId + minter + blok + link metadata (uri bila ada) + candidate NFT contract bila ada; (b) reresolved — mint lama yang namanya kini pertama kali terbaca — sebutkan sekali (tokenId + nama baru + minter + blok).
5. Bila tidak ada mint yang lolos (semua baru belum terbaca dan tidak ada reresolved): DIAM.
6. Mint yang sudah dilaporkan sekali jangan dilaporkan ulang di run berikut (state seen mencatatnya).
7. Bila run gagal (exit 1, getLogs gagal) atau terkunci (exit 3): DIAM — watermark tidak maju, run berikut retry otomatis. Jangan jalankan ulang chunk manual.
8. Observasi singkat ke log harian ~/memory/2026-11-07.md. Jangan menulis snapshot/seen/state job lain. Jangan edit MEMORY.md.
