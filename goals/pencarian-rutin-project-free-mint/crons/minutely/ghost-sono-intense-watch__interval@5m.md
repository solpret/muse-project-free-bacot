---
id: ghost-sono-intense-watch
title: Pantau intensif GHOST + SONO (5 menit)
enabled: false
owner: goal:pencarian-rutin-project-free-mint
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-11-05T22:13:51
  every: 5m
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
Pantau intensif 2 early lead FREE BACOT (perintah user 2026-11-05 ~22:01 WIB "Pantau secara intens"). Read-only TOTAL: hanya eth_call, TIDAK PERNAH preview/mint/approve/swap/tx.

Item:
- GHOST (GHOST) 0x474949EBCee9E3A425B6d8033f1E2c8DD3Ae755e — first mint 2026-11-05 20:38:08 WIB; FREE_SUPPLY() tidak merespons (free% UNVERIFIED — JANGAN substitusi totalSupply%).
- SONO (Sonofluidic) 0x1eF7588Dff561b7390D3AF23d06E684D64217419 — first mint 2026-11-05 20:41:43 WIB; FREE_SUPPLY 2.260; MAX_SUPPLY 6.666; PRICE 0,00085 BNB.

Tiap run: jalankan `~/workspace/.abi-venv/bin/python ~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/ghost-sono-watch.py`. Script membaca state segar (totalSupply, freeMinted, MAX_SUPPLY, FREE_SUPPLY, mintOpen, freeClaimed(user), balanceOf(user)), menghitung free% + velocity/menit, memperbarui state file `ghost-sono-watch-state.json` di folder yang sama, dan mencetak blok EVENTS.

Laporkan ke chat utama HANYA bila ada EVENTS (sekali per perubahan):
- PROMOSI STRONG LEAD: free% >= 25% + slot user terbuka + umur <= 48 jam (SONO; GHOST hanya bila FREE_SUPPLY() mulai merespons dan free% terverifikasi >= 25%). Laporan promosi = pemberitahuan saja — eksekusi strong-lead direct mint tetap wewenang job pencarian rutin 30-menit / parent di bawah gate website + audit + preview bersih; job ini TIDAK mengeksekusi.
- FREE POOL HABIS / SLOT USER HILANG / MINT DITUTUP / AGE-EXCLUDED (> 48 jam dari first mint: GHOST 2026-11-07 20:38 WIB, SONO 2026-11-07 20:41 WIB).
Bila tidak ada EVENTS, diam (jangan kirim laporan rutin).

Bila BOTH_RESOLVED: true (kedua item berstatus soldout/slot_lost/closed/age_excluded), nonaktifkan cron ini sendiri (cron.update id ghost-sono-intense-watch, enabled false) dan laporkan sekali bahwa pantauan intensif selesai + status akhir kedua item.

JANGAN menulis snapshot onchain-snapshot.json (milik job pencarian rutin) — hanya state file job ini. Bila script gagal baca (RPC error semua), catat di run log dan diam; jangan laporkan sebagai perubahan.
