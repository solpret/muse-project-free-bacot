---
id: stampooor-reveal-check-20261114
title: 'Cek reveal Stampooor Pass #751'
enabled: true
owner: goal:pencarian-rutin-project-free-mint
mode: task
schedule:
  kind: runonce
  timezone: Asia/Jakarta
  at: 2026-11-14T09:30:00
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false}'
  presentation_locale: id-ID
---
CEK REVEAL SATU KALI — Stampooor Pass #751 (mint gratis 2026-11-09 09:43 WIB, tx 0x3b195924a58ba72c4a94bbf76be3a4b068fc3863c4b6fa1f35827c6f5bf6ed78). READ-ONLY: TIDAK PERNAH preview/mint/claim/approve/swap/sign/tx. Klaim apa pun (claim([751])) dilakukan parent di chat utama sesudah laporan, bukan di job ini.

Koin: Stampooor Pass 0xCFB72b0E311796C478c6b74C1cd4592BbAa17aab, token #751 di wallet agent 0xeb237F6f9FB4e826739F0954e9768914F28b2c2E. Mint window berakhir 2026-11-14 09:00:50 WIB (mintEnd on-chain). Tier saat mint: UNREVEALED (revealed()=false; tierOf reverts pre-reveal). Skala tier proyek (verbatim tierName() on-chain): Inverted (0) / Airmail (1) / Registered (2) / Express (3) / First Class (4) / Postcard (5). REVEAL_DELAY 5, REVEAL_WINDOW 8000 blok (~1 jam).

TIAP RUN (satu kali, ~09:30 WIB 14 Nov): baca segar on-chain (eth_call via dataseed/fast_rpc): revealed(), tierOf(751), tokenURI(751), dan balanceOf POSTAGE wallet agent (token 0x6C310EABEdFD4eEd6148bf2C07241FB45a52FB42 — saat mint 10.000; klaim reward tier pasca-reveal via claim([751]) bisa menambah saldo).
- Bila revealed=true: LAPORKAN SEKALI ke chat utama: tier #751 (nama tier proyek verbatim + nomor), traits dari tokenURI, saldo POSTAGE (apakah klaim reward sudah tersedia / sudah bertambah). Perbarui entri Stampooor Pass #751 di ~/workspace/nft-rarity-inventory.md dengan tier terverifikasi. Jangan claim apa pun.
- Bila revealed=false: LAPORKAN SEKALI ke chat utama secara singkat bahwa reveal belum terjadi (mintEnd sudah lewat) supaya parent bisa memutuskan cek berikutnya. Jangan tebak kapan reveal.
- Bila bacaan on-chain gagal (RPC error/timeout): DIAM, catat singkat ke log harian ~/memory/2026-11-14.md. Jangan menulis MEMORY.md.
